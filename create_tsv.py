#!/usr/bin/env python3
import json
import csv

def score_answer(model_answer, correct_answer, alternate_answers):
    """Score model answer against correct + alternate answers"""
    if not model_answer:
        return 0
    
    model_clean = str(model_answer).strip().lower()
    
    # Check against correct answer
    if correct_answer and model_clean == str(correct_answer).strip().lower():
        return 1
    
    # Check against alternate answers
    if alternate_answers:
        for alt in alternate_answers:
            if alt and model_clean == str(alt).strip().lower():
                return 1
    
    return 0

def create_tsv():
    # Load questions
    with open("questions.json") as f:
        questions = json.load(f)
    
    # Load results (if exists)
    results = {}
    try:
        with open("results.json") as f:
            results = json.load(f)
    except FileNotFoundError:
        print("No results.json found, creating empty TSV structure")
    
    # Get all model names from results
    model_names = list(results.keys()) if results else []
    
    # Get all unique tags for binary columns
    all_tags = set()
    for q in questions:
        all_tags.update(q.get("tags", []))
    all_tags = sorted(list(all_tags))
    
    # Create TSV headers
    headers = [
        "question", "image", "correct_answer", "domain", 
        "alternate_answers", "difficulty"
    ]
    
    # Add binary tag columns
    for tag in all_tags:
        headers.append(f"is_{tag.replace(' ', '_').replace('-', '_').lower()}")
    
    # Keep original tags column for reference
    headers.append("tags_original")
    
    # Add columns for each model (answer + reasoning + token data + timing)
    for model in model_names:
        headers.extend([
            f"{model}_answer", 
            f"{model}_reasoning", 
            f"{model}_correct",
            f"{model}_time",
            f"{model}_prompt_tokens",
            f"{model}_completion_tokens", 
            f"{model}_reasoning_tokens",
            f"{model}_total_tokens",
            f"{model}_cost"
        ])
    
    # Create TSV data
    rows = []
    
    for q in questions:
        row = {
            "question": q.get("question", ""),
            "image": q.get("image", ""),
            "correct_answer": q.get("answer", ""),
            "domain": q.get("domain", ""),
            "alternate_answers": "|".join(q.get("alternate_answers", [])),
            "difficulty": q.get("difficulty", "")
        }
        
        # Add binary tag columns
        question_tags = q.get("tags", [])
        for tag in all_tags:
            row[f"is_{tag.replace(' ', '_').replace('-', '_').lower()}"] = 1 if tag in question_tags else 0
        
        # Keep original tags for reference
        row["tags_original"] = "|".join(question_tags)
        
        # Add model responses
        for model in model_names:
            model_responses = results.get(model, [])
            
            # Find response for this question
            response = None
            for r in model_responses:
                if (r.get("question") == q.get("question") and 
                    r.get("image") == q.get("image")):
                    response = r
                    break
            
            if response:
                model_answer = response.get("response", "")
                row[f"{model}_answer"] = model_answer
                row[f"{model}_reasoning"] = response.get("reasoning", "") or ""
                
                # Auto-score the answer
                score = score_answer(
                    model_answer, 
                    q.get("answer"), 
                    q.get("alternate_answers", [])
                )
                row[f"{model}_correct"] = score
                
                # Add timing and token data
                row[f"{model}_time"] = response.get("time", "")
                
                tokens = response.get("tokens", {})
                row[f"{model}_prompt_tokens"] = tokens.get("prompt", "")
                row[f"{model}_completion_tokens"] = tokens.get("completion", "")
                row[f"{model}_reasoning_tokens"] = tokens.get("reasoning", "")
                row[f"{model}_total_tokens"] = tokens.get("total", "")
                row[f"{model}_cost"] = tokens.get("cost", "")
                
            else:
                row[f"{model}_answer"] = ""
                row[f"{model}_reasoning"] = ""  
                row[f"{model}_correct"] = ""
                row[f"{model}_time"] = ""
                row[f"{model}_prompt_tokens"] = ""
                row[f"{model}_completion_tokens"] = ""
                row[f"{model}_reasoning_tokens"] = ""
                row[f"{model}_total_tokens"] = ""
                row[f"{model}_cost"] = ""
        
        rows.append(row)
    
    # Write TSV
    with open("results.tsv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Created results.tsv with {len(rows)} questions and {len(model_names)} models")
    print(f"Models: {', '.join(model_names)}")

if __name__ == "__main__":
    create_tsv()