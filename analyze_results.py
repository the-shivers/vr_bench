#!/usr/bin/env python3
import json
from collections import defaultdict

def analyze_results():
    # Load data
    with open("questions.json") as f:
        questions = json.load(f)
    
    try:
        with open("results.json") as f:
            results = json.load(f)
    except FileNotFoundError:
        print("No results.json found")
        return
    
    model_names = list(results.keys())
    print(f"Analyzing {len(model_names)} models: {', '.join(model_names)}\n")
    
    # Create question lookup
    q_lookup = {(q["question"], q["image"]): q for q in questions}
    
    # Collect all data per model
    model_data = {}
    
    for model in model_names:
        model_responses = results[model]
        
        scores = []
        costs = []
        tokens = []
        tag_stats = defaultdict(lambda: {"correct": 0, "total": 0})
        domain_stats = defaultdict(lambda: {"correct": 0, "total": 0})
        type_stats = defaultdict(lambda: {"correct": 0, "total": 0})
        prefix_stats = defaultdict(lambda: {"correct": 0, "total": 0})
        
        for response in model_responses:
            q_key = (response["question"], response["image"])
            question = q_lookup.get(q_key)
            if not question:
                continue
                
            # Score the response
            model_answer = response.get("response", "").strip().lower()
            correct_answer = question.get("answer", "")
            alternates = question.get("alternate_answers", [])
            
            score = 0
            if correct_answer and model_answer == str(correct_answer).strip().lower():
                score = 1
            else:
                for alt in alternates:
                    if alt and model_answer == str(alt).strip().lower():
                        score = 1
                        break
            
            scores.append(score)
            
            # Cost and tokens
            if "tokens" in response:
                costs.append(response["tokens"].get("cost", 0) or 0)
                tokens.append(response["tokens"].get("total", 0) or 0)
            
            # Breakdowns
            for tag in question.get("tags", []):
                tag_stats[tag]["correct"] += score
                tag_stats[tag]["total"] += 1
            
            if question.get("domain"):
                domain_stats[question["domain"]]["correct"] += score
                domain_stats[question["domain"]]["total"] += 1
            
            if question.get("type"):
                type_stats[question["type"]]["correct"] += score
                type_stats[question["type"]]["total"] += 1
            
            # Image prefix (before first underscore or dot)
            image_name = question.get("image", "")
            if image_name:
                prefix = image_name.split("_")[0].split(".")[0]
                prefix_stats[prefix]["correct"] += score
                prefix_stats[prefix]["total"] += 1
        
        model_data[model] = {
            "scores": scores,
            "costs": costs, 
            "tokens": tokens,
            "tag_stats": dict(tag_stats),
            "domain_stats": dict(domain_stats),
            "type_stats": dict(type_stats),
            "prefix_stats": dict(prefix_stats)
        }
    
    # Generate analysis
    analysis = []
    
    # Overall accuracy
    analysis.append("=== OVERALL ACCURACY ===")
    for model in model_names:
        data = model_data[model]
        if data["scores"]:
            acc = sum(data["scores"]) / len(data["scores"])
            analysis.append(f"{model}: {sum(data['scores'])}/{len(data['scores'])} = {acc:.3f}")
        else:
            analysis.append(f"{model}: No responses")
    analysis.append("")
    
    # Accuracy per dollar
    analysis.append("=== ACCURACY PER DOLLAR ===")
    for model in model_names:
        data = model_data[model]
        if data["scores"] and data["costs"]:
            total_cost = sum(data["costs"])
            total_correct = sum(data["scores"])
            if total_cost > 0:
                acc_per_dollar = total_correct / total_cost
                analysis.append(f"{model}: {total_correct} correct / ${total_cost:.4f} = {acc_per_dollar:.1f} correct/$")
            else:
                analysis.append(f"{model}: ${total_cost:.4f} cost")
        else:
            analysis.append(f"{model}: No cost data")
    analysis.append("")
    
    # Accuracy per token
    analysis.append("=== ACCURACY PER TOKEN ===")
    for model in model_names:
        data = model_data[model]
        if data["scores"] and data["tokens"]:
            total_tokens = sum(data["tokens"])
            total_correct = sum(data["scores"])
            if total_tokens > 0:
                acc_per_token = total_correct / total_tokens
                analysis.append(f"{model}: {total_correct} correct / {total_tokens} tokens = {acc_per_token:.6f} correct/token")
        else:
            analysis.append(f"{model}: No token data")
    analysis.append("")
    
    # Helper function for breakdown analysis
    def add_breakdown(title, stat_key):
        analysis.append(f"=== {title} ===")
        all_categories = set()
        for data in model_data.values():
            all_categories.update(data[stat_key].keys())
        
        for category in sorted(all_categories):
            analysis.append(f"\n{category}:")
            for model in model_names:
                stats = model_data[model][stat_key].get(category, {"correct": 0, "total": 0})
                if stats["total"] > 0:
                    acc = stats["correct"] / stats["total"]
                    analysis.append(f"  {model}: {stats['correct']}/{stats['total']} = {acc:.3f}")
                else:
                    analysis.append(f"  {model}: 0/0 = N/A")
        analysis.append("")
    
    # Breakdowns
    add_breakdown("ACCURACY BY TAG", "tag_stats")
    add_breakdown("ACCURACY BY DOMAIN", "domain_stats") 
    add_breakdown("ACCURACY BY TYPE", "type_stats")
    add_breakdown("ACCURACY BY IMAGE PREFIX", "prefix_stats")
    
    # Write analysis
    with open("analysis.txt", "w") as f:
        f.write("\n".join(analysis))
    
    print("Analysis complete! Check analysis.txt")
    print(f"Processed {len(questions)} questions")

if __name__ == "__main__":
    analyze_results()