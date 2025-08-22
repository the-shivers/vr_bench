#!/usr/bin/env python3
import json, base64, time, os, mimetypes, threading
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from dotenv import load_dotenv



# SETTINGS
SYS_PROMPT = """
This is for a visual reasoning benchmark, where your goal is to get the highest score. 
You'll be asked a single question, and you need to give JUST the direct answer, with no 
explanation, formatting, or extra words. So if the question is "How many balls are there?"
Your answer should be JUST a number: 3, or 135, or 234243, etc. NOT "twelve" or "About 3." If
the question is "what color is the triangle?" your answer should be "red" or "yellow" and 
NOT "periwinkle" or "light orange" (unless there is another orange object you need to distinguish 
it from). If the question is "Who is this singer?" Your answer should be "Adele" or "P!nk" and not
"Adele Laurie Blue Adkins" or "Alecia Beth Moore." So generally, give the obvious answer and 
nothing extra. You are welcome to reason about it for extended periods, but your response should
consist of just the answer.
"""
MAX_QUESTIONS = 7 # Set to 1000000 for all questions
MODELS = [
    {"name": "gemini-2.5-pro", "model": "google/gemini-2.5-pro", "reasoning_effort": "low"},
    {"name": "anthropic/claude-sonnet-4", "model": "anthropic/claude-sonnet-4", "reasoning_max_tokens": "2000"},
]

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)
all_results = {}
results_lock = threading.Lock()

def run_model(model_config, questions):
    model_results = all_results.get(model_config["name"], [])
    completed = skipped = 0
    
    for i, q in enumerate(questions):
        if any(r.get("question") == q["question"] and r.get("image") == q["image"] for r in model_results):
            print(f"[{model_config['name']}] [{i+1}/{len(questions)}] SKIP")
            skipped += 1
            continue
            
        print(f"[{model_config['name']}] [{i+1}/{len(questions)}] {q['question'][:60]}...")
        
        try:
            with open(f"images/{q['image']}", "rb") as f:
                data = base64.b64encode(f.read()).decode('utf-8')
            mime_type, _ = mimetypes.guess_type(q['image'])
            if not mime_type or not mime_type.startswith('image/'):
                mime_type = 'image/jpeg'
            params = {
                "model": model_config["model"],
                "messages": [
                    {"role": "system", "content": SYS_PROMPT},
                    {"role": "user", "content": [
                        {"type": "text", "text": q["question"]},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{data}"}}
                    ]}
                ],
                "temperature": 0.0,
                "extra_body": {"usage": {"include": True}}
            }
            if model_config.get("reasoning_effort"):
                params["reasoning_effort"] = model_config["reasoning_effort"]
            elif model_config.get("reasoning_max_tokens"):
                params['extra_body'].update({'reasoning': {'max_tokens': 2000}})
                
            start = time.time()
            response = client.chat.completions.create(**params)
            duration = time.time() - start
            content = response.choices[0].message.content
            reasoning_trace = getattr(response.choices[0].message, 'reasoning', None)
            usage = response.usage if hasattr(response, 'usage') else None
            
            result = {
                "question": q["question"],
                "image": q["image"],
                "response": content,
                "reasoning": reasoning_trace,
                "correct_answer": q.get("answer", ""),
                "model": model_config["name"],
                "time": duration
            }
            
            if usage:
                result["tokens"] = {
                    "prompt": usage.prompt_tokens,
                    "completion": usage.completion_tokens,
                    "total": usage.total_tokens,
                    "cost": usage.cost if hasattr(usage, 'cost') else None
                }
                if hasattr(usage, 'completion_tokens_details') and usage.completion_tokens_details:
                    result["tokens"]["reasoning"] = getattr(usage.completion_tokens_details, 'reasoning_tokens', 0)
            
            with results_lock:
                model_results.append(result)
                all_results[model_config["name"]] = model_results
                with open("results.json", "w") as f:
                    json.dump(all_results, f, indent=2)
            
            print(f"[{model_config['name']}] → {content[:60]}... ({duration:.1f}s)")
            completed += 1
            
        except Exception as e:
            print(f"[{model_config['name']}] ERROR: {e}")
            continue
    
    print(f"[{model_config['name']}] DONE! {completed} completed, {skipped} skipped")

def main():
    with open("questions.json") as f:
        questions = json.load(f)
    questions = questions[:MAX_QUESTIONS]
    
    if os.path.exists("results.json"):
        with open("results.json") as f:
            all_results.update(json.load(f))
    
    with ThreadPoolExecutor(max_workers=len(MODELS)) as executor:
        futures = [executor.submit(run_model, model_config, questions) for model_config in MODELS]
        for future in futures:
            future.result()
    
    print("\nAll models complete! Results in results.json")
if __name__ == "__main__":
    main()