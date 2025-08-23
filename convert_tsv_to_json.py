#!/usr/bin/env python3
import json
import csv

def convert_tsv_to_json():
    # Read the TSV file
    new_questions = []
    
    with open("new_questions_for_bench.tsv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        
        for row in reader:
            # Parse tags (split by comma and strip whitespace)
            tags = [tag.strip() for tag in row["Tags"].split(",") if tag.strip()]
            
            # Parse alternate answers (split by comma and strip whitespace)
            alternate_answers = []
            if row["Alternate Answers"].strip():
                alternate_answers = [ans.strip() for ans in row["Alternate Answers"].split(",") if ans.strip()]
            
            # Create JSON structure matching existing questions.json format
            question_obj = {
                "question": row["Question"],
                "image": row["Image"],
                "tags": tags,
                "type": row["Type"],
                "domain": row["Domain"],
                "answer": row["Answer"],
                "alternate_answers": alternate_answers
            }
            
            new_questions.append(question_obj)
    
    # Load existing questions
    with open("questions.json", "r") as f:
        existing_questions = json.load(f)
    
    # Combine them
    combined_questions = existing_questions + new_questions
    
    # Write combined questions back to questions.json
    with open("questions.json", "w") as f:
        json.dump(combined_questions, f, indent=2)
    
    print(f"Added {len(new_questions)} new questions to questions.json")
    print(f"Total questions now: {len(combined_questions)}")

if __name__ == "__main__":
    convert_tsv_to_json()