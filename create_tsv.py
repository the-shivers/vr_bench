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
    
    # Create TSV headers
    headers = [
        "question", "image", "correct_answer", "tags", "domain", 
        "alternate_answers", "difficulty"
    ]
    
    # Add columns for each model (answer + reasoning)
    for model in model_names:
        headers.extend([f"{model}_answer", f"{model}_reasoning", f"{model}_correct"])
    
    # Create TSV data
    rows = []
    
    for q in questions:
        row = {
            "question": q.get("question", ""),
            "image": q.get("image", ""),
            "correct_answer": q.get("answer", ""),
            "tags": "|".join(q.get("tags", [])),
            "domain": q.get("domain", ""),
            "alternate_answers": "|".join(q.get("alternate_answers", [])),
            "difficulty": q.get("difficulty", "")
        }
        
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
            else:
                row[f"{model}_answer"] = ""
                row[f"{model}_reasoning"] = ""  
                row[f"{model}_correct"] = ""
        
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