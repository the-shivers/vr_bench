#!/usr/bin/env python3
import pandas as pd
import argparse

def analyze_results(show_tags=False, show_domains=False, refusal_mode='both'):
    # Load the cleaned results
    df = pd.read_csv("results_cleaned.tsv", sep="\t")
    
    print(f"Loaded {len(df)} questions")
    print(f"Questions with any refusal: {df['any_refusal'].sum()}")
    print(f"Questions without refusal: {len(df) - df['any_refusal'].sum()}")
    print()
    
    # Get model names by finding columns that end with '-correct' or '_correct'
    model_columns = [col for col in df.columns if col.endswith('-correct') or col.endswith('_correct')]
    models = []
    for col in model_columns:
        if col.endswith('-correct'):
            models.append(col.replace('-correct', ''))
        elif col.endswith('_correct'):
            models.append(col.replace('_correct', ''))
    
    print(f"Found {len(models)} models: {', '.join(models)}")
    print()
    
    if refusal_mode in ['both', 'overall']:
        # Calculate overall accuracy
        print("=== OVERALL ACCURACY ===")
        overall_results = []
        
        for model in models:
            # Try both naming conventions
            correct_col = None
            if f"{model}-correct" in df.columns:
                correct_col = f"{model}-correct"
            elif f"{model}_correct" in df.columns:
                correct_col = f"{model}_correct"
                
            if correct_col:
                total_answered = df[correct_col].notna().sum()
                total_correct = df[correct_col].sum()
                accuracy = (total_correct / total_answered * 100) if total_answered > 0 else 0
                
                overall_results.append({
                    'Model': model,
                    'Total_Answered': total_answered,
                    'Total_Correct': total_correct,
                    'Accuracy_%': accuracy
                })
                
                print(f"{model}: {total_correct}/{total_answered} = {accuracy:.1f}%")
        
        print()
    
    if refusal_mode in ['both', 'no-refusal']:
        # Calculate accuracy excluding refusals
        print("=== ACCURACY (EXCLUDING REFUSALS) ===")
        no_refusal_results = []
        
        # Filter to questions where no model refused
        no_refusal_df = df[df['any_refusal'] == 0]
        
        for model in models:
            # Try both naming conventions
            correct_col = None
            if f"{model}-correct" in no_refusal_df.columns:
                correct_col = f"{model}-correct"
            elif f"{model}_correct" in no_refusal_df.columns:
                correct_col = f"{model}_correct"
                
            if correct_col:
                total_answered = no_refusal_df[correct_col].notna().sum()
                total_correct = no_refusal_df[correct_col].sum()
                accuracy = (total_correct / total_answered * 100) if total_answered > 0 else 0
                
                no_refusal_results.append({
                    'Model': model,
                    'Total_Answered': total_answered,
                    'Total_Correct': total_correct,
                    'Accuracy_%': accuracy
                })
                
                print(f"{model}: {total_correct}/{total_answered} = {accuracy:.1f}%")
        
        print()
    
    
    if show_tags:
        # Tag-based analysis
        print("\n" + "="*80)
        print("=== TAG-BASED ANALYSIS ===")
        
        # Get all tag columns (binary columns starting with tag names)
        tag_columns = ['adversarial', 'enumeration', 'extraction', 'identification', 
                       'quality', 'reasoning', 'sequencing', 'spatial']
        
        for tag in tag_columns:
            if tag in df.columns:
                print(f"\n--- {tag.upper()} QUESTIONS ---")
                
                # Filter to questions with this tag
                tag_questions = df[df[tag] == 1]
                tag_no_refusal = tag_questions[tag_questions['any_refusal'] == 0]
                
                print(f"Total {tag} questions: {len(tag_questions)}")
                print(f"{tag} questions without refusals: {len(tag_no_refusal)}")
                
                if len(tag_questions) > 0 and refusal_mode in ['both', 'overall']:
                    print(f"\nOverall accuracy on {tag} questions:")
                    for model in models:
                        correct_col = None
                        if f"{model}-correct" in df.columns:
                            correct_col = f"{model}-correct"
                        elif f"{model}_correct" in df.columns:
                            correct_col = f"{model}_correct"
                            
                        if correct_col:
                            total_answered = tag_questions[correct_col].notna().sum()
                            total_correct = tag_questions[correct_col].sum()
                            accuracy = (total_correct / total_answered * 100) if total_answered > 0 else 0
                            print(f"  {model}: {total_correct}/{total_answered} = {accuracy:.1f}%")
                
                if len(tag_no_refusal) > 0 and refusal_mode in ['both', 'no-refusal']:
                    print(f"\nAccuracy on {tag} questions (excluding refusals):")
                    for model in models:
                        correct_col = None
                        if f"{model}-correct" in df.columns:
                            correct_col = f"{model}-correct"
                        elif f"{model}_correct" in df.columns:
                            correct_col = f"{model}_correct"
                            
                        if correct_col:
                            total_answered = tag_no_refusal[correct_col].notna().sum()
                            total_correct = tag_no_refusal[correct_col].sum()
                            accuracy = (total_correct / total_answered * 100) if total_answered > 0 else 0
                            print(f"  {model}: {total_correct}/{total_answered} = {accuracy:.1f}%")

    if show_domains:
        # Domain-based analysis
        print("\n" + "="*80)
        print("=== DOMAIN-BASED ANALYSIS ===")
        
        # Get all unique domains
        domains = df['domain'].unique()
        domains = [d for d in domains if pd.notna(d)]
        
        for domain in sorted(domains):
            print(f"\n--- {domain.upper()} QUESTIONS ---")
            
            # Filter to questions with this domain
            domain_questions = df[df['domain'] == domain]
            domain_no_refusal = domain_questions[domain_questions['any_refusal'] == 0]
            
            print(f"Total {domain} questions: {len(domain_questions)}")
            print(f"{domain} questions without refusals: {len(domain_no_refusal)}")
            
            if len(domain_questions) > 0 and refusal_mode in ['both', 'overall']:
                print(f"\nOverall accuracy on {domain} questions:")
                for model in models:
                    correct_col = None
                    if f"{model}-correct" in df.columns:
                        correct_col = f"{model}-correct"
                    elif f"{model}_correct" in df.columns:
                        correct_col = f"{model}_correct"
                        
                    if correct_col:
                        total_answered = domain_questions[correct_col].notna().sum()
                        total_correct = domain_questions[correct_col].sum()
                        accuracy = (total_correct / total_answered * 100) if total_answered > 0 else 0
                        print(f"  {model}: {total_correct}/{total_answered} = {accuracy:.1f}%")
            
            if len(domain_no_refusal) > 0 and refusal_mode in ['both', 'no-refusal']:
                print(f"\nAccuracy on {domain} questions (excluding refusals):")
                for model in models:
                    correct_col = None
                    if f"{model}-correct" in df.columns:
                        correct_col = f"{model}-correct"
                    elif f"{model}_correct" in df.columns:
                        correct_col = f"{model}_correct"
                        
                    if correct_col:
                        total_answered = domain_no_refusal[correct_col].notna().sum()
                        total_correct = domain_no_refusal[correct_col].sum()
                        accuracy = (total_correct / total_answered * 100) if total_answered > 0 else 0
                        print(f"  {model}: {total_correct}/{total_answered} = {accuracy:.1f}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze VR benchmark results')
    parser.add_argument('--tags', action='store_true', help='Show tag-based analysis')
    parser.add_argument('--domains', action='store_true', help='Show domain-based analysis')
    parser.add_argument('--refusal', choices=['both', 'overall', 'no-refusal'], default='both',
                        help='Refusal analysis mode: both (default), overall, or no-refusal')
    
    args = parser.parse_args()
    analyze_results(show_tags=args.tags, show_domains=args.domains, refusal_mode=args.refusal)