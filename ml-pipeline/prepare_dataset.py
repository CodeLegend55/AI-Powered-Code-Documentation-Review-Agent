import pandas as pd
from datasets import load_dataset, Dataset
import json
import os

def format_prompt(instruction, code, response=""):
    """Formats the instruction and code into an Alpaca-style prompt"""
    prompt = f"Below is an instruction that describes a task, paired with input context. Write a response that appropriately completes the request.\n\n### Instruction:\n{instruction}\n\n### Input Context:\n{code}\n\n### Response:\n{response}"
    return prompt

def prepare_diversevul():
    """
    Simulated ingestion for DiverseVul (or arbitrary jsonl dataset).
    To use the real huggingface dataset:
    dataset = load_dataset("secdbg/DiverseVul", split="train")
    """
    print("Loading vulnerability dataset...")
    # Example logic using HuggingFace Datasets (using an example sub-sample for robustness)
    try:
        print("Loading real dataset: VatsaDev/code-review...")
        
        # ==========================================
        # PASTE YOUR HUGGINGFACE SECRET TOKEN BELOW:
        # ==========================================
        HF_TOKEN = "your_secret_token_here" 

        dataset = load_dataset("VatsaDev/code-review", split="train[:1500]", token=HF_TOKEN) # Load 1500 authentic review examples
    except Exception as e:
        print(f"Critical: Could not fetch VatsaDev/code-review. {e}")
        return None
        
    formatted_data = []
    
    # Process dataset into Instruction/Input/Response mapping
    for row in dataset:
        # If the dataset is already pre-formatted for Unsloth (has only a 'text' built column)
        if 'text' in row and 'code' not in row and 'input' not in row:
            text_val = str(row['text']).strip()
            # Safety check: prevent completely empty rows which crash the SFTTrainer with generic 'int' exceptions
            if len(text_val) > 10:
                formatted_data.append({"text": text_val + " <|eot_id|>"})
            continue

        # Instruct the model to operate as an expert code reviewer
        instruction = "You are an expert AI code reviewer. Evaluate the provided code and provide a highly accurate technical review."
        
        # Dynamically extract question/answer depending on CodeReviewQA schema
        input_text = row.get('code', row.get('input', row.get('question', row.get('context', ''))))
        output_text = row.get('review', row.get('output', row.get('answer', row.get('response', ''))))
        
        # Skip malformed/empty rows
        if not input_text or not output_text:
            continue

        formatted_data.append({
            "instruction": instruction,
            "input": input_text,
            "output": output_text,
            "text": format_prompt(instruction, input_text, output_text)
        })
    if len(formatted_data) == 0:
        raise ValueError(f"Dataset parsing failed! No rows matched the expected schema! Columns found: {dataset.column_names}\nPlease report this back so we can fix the row.get() dictionary!")
        
    final_dataset = Dataset.from_pandas(pd.DataFrame(formatted_data))
    return final_dataset

if __name__ == "__main__":
    print("Starting data preparation for AI Code Reviewer...")
    
    os.makedirs("./processed_vuln_data", exist_ok=True)
    
    ds = prepare_diversevul()
    if ds:
        # Save to disk to load later in training script
        ds.save_to_disk("./processed_vuln_data")
        print(f"Data preparation complete! Saved {len(ds)} samples to ./processed_vuln_data")
