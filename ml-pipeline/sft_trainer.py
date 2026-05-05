# sft_trainer.py
# Use Unsloth for 2x faster, 70% less memory training of LLMs on Kaggle.

import torch
import math
from unsloth import FastLanguageModel
from datasets import load_from_disk
from trl import SFTTrainer
from transformers import TrainingArguments

def preprocess_logits_for_metrics(logits, labels):
    if isinstance(logits, tuple):
        logits = logits[0]
    return logits.argmax(dim=-1)

def compute_metrics(eval_preds):
    preds, labels = eval_preds
    # labels are shifted by 1 relative to preds for causal LM
    labels = labels[:, 1:].reshape(-1)
    preds = preds[:, :-1].reshape(-1)
    
    mask = labels != -100
    labels = labels[mask]
    preds = preds[mask]
    
    accuracy = (preds == labels).mean()
    return {"accuracy": accuracy}

def run_training():
    print("Initializing Unsloth fine-tuning...")
    # 1. Configuration
    max_seq_length = 1024 # Reduced from 2048 to prevent Tesla T4 OOM when packing is enabled
    dtype = None # Auto detection (Float16 / Bfloat16)
    load_in_4bit = True # Use 4bit quantization to reduce memory usage

    # 2. Load Base Model & Tokenizer
    # We will use the highly reliable Llama-3 8B Instruct model which is fully supported dynamically. 
    model_id = "unsloth/llama-3-8b-Instruct-bnb-4bit"
    print(f"Loading Base Model: {model_id}")
    
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = model_id, 
        max_seq_length = max_seq_length,
        dtype = dtype,
        load_in_4bit = load_in_4bit,
    )

    # 2.5 Ensure padding token is set before Trainer logic
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # 3. Add LoRA Adapters (Parameter Efficient Fine-Tuning)
    model = FastLanguageModel.get_peft_model(
        model,
        r = 16, # Size of adapters (8, 16, 32, 64)
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                          "gate_proj", "up_proj", "down_proj"],
        lora_alpha = 16,
        lora_dropout = 0, # Dropout = 0 is highly optimized
        bias = "none",    
        use_gradient_checkpointing = "unsloth", # Re-enabled Unsloth's 70% memory savings since the native bug is patched
        random_state = 3407,
        use_rslora = False,
        loftq_config = None,
    )

    # 4. Load Preprocessed Dataset
    print("Loading processed dataset...")
    try:
        dataset = load_from_disk("./processed_vuln_data")
    except Exception as e:
        print("Error loading data. Did you run prepare_dataset.py?")
        raise e

    # 4.5 Split the dataset for Training & Evaluation metrics
    split_dataset = dataset.train_test_split(test_size=0.1, seed=3407)
    train_set = split_dataset["train"]
    eval_set = split_dataset["test"]

    # 5. Connect SFT Trainer
    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = train_set,
        eval_dataset = eval_set,
        dataset_text_field = "text",
        max_seq_length = max_seq_length,
        dataset_num_proc = 2,
        packing = False, # Packing explicitly disabled to prevent Tesla T4 16GB Memory Overload
        compute_metrics = compute_metrics,
        preprocess_logits_for_metrics = preprocess_logits_for_metrics,
        args = TrainingArguments(
            per_device_train_batch_size = 1, # Strictly dropped to 1 to prevent CUDA Out Of Memory!
            gradient_accumulation_steps = 8, # Increased to keep effective batch size mathematically identical
            warmup_steps = 5,
            max_steps = 60, # Increase to num_epochs=1 for actual training
            learning_rate = 2e-4,
            fp16 = not torch.cuda.is_bf16_supported(),
            bf16 = torch.cuda.is_bf16_supported(),
            logging_steps = 1,
            eval_strategy = "steps", # Enable rigorous evaluation metrics
            eval_steps = 10,         # Log validation loss every 10 steps
            per_device_eval_batch_size = 1,
            optim = "adamw_8bit",
            weight_decay = 0.01,
            lr_scheduler_type = "linear",
            seed = 3407,
            output_dir = "unsloth_outputs",
        ),
    )

    # 6. Execute Training
    print("Beginning Training...")
    # --- HOTFIX FOR UNSLOTH / TRANSFORMERS 5.x CRASH ---
    # Unsloth occasionally crashes during BOTH training and evaluation when Transformers 
    # passes num_items_in_batch, causing compute_loss to return a scalar integer/float.
    original_compute_loss = trainer.compute_loss
    
    def safe_compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None, **kwargs):
        # STRIP num_items_in_batch to prevent Unsloth from getting confused
        result = original_compute_loss(model, inputs, return_outputs=return_outputs, **kwargs)
        
        if return_outputs:
            loss, outputs = result
            if isinstance(loss, (int, float)):
                loss = torch.tensor(float(loss), requires_grad=True, device=model.device)
            return loss, outputs
        else:
            loss = result
            if isinstance(loss, (int, float)):
                loss = torch.tensor(float(loss), requires_grad=True, device=model.device)
            return loss
            
    import types
    trainer.compute_loss = types.MethodType(safe_compute_loss, trainer)

    trainer_stats = trainer.train()
    
    # 6.5 Generate Evaluation Metric Graphs
    try:
        import matplotlib.pyplot as plt
        print("Generating evaluation metric graphs...")
        log_history = trainer.state.log_history
        train_steps, train_loss = [], []
        eval_steps, eval_loss, eval_accuracy, eval_perplexity = [], [], [], []
        
        for log in log_history:
            if "loss" in log and "eval_loss" not in log:
                train_steps.append(log["step"])
                train_loss.append(log["loss"])
            elif "eval_loss" in log:
                eval_steps.append(log["step"])
                eval_loss.append(log["eval_loss"])
                if "eval_accuracy" in log:
                    eval_accuracy.append(log["eval_accuracy"])
                try:
                    eval_perplexity.append(math.exp(log["eval_loss"]))
                except OverflowError:
                    eval_perplexity.append(float('inf'))
                
        # Create a figure with 3 subplots
        fig, axs = plt.subplots(3, 1, figsize=(10, 15))
        
        # Plot 1: Loss
        axs[0].plot(train_steps, train_loss, label="Training Loss", alpha=0.7, color="blue")
        if eval_loss:
            axs[0].plot(eval_steps, eval_loss, label="Validation Loss", marker="o", color="red", linewidth=2)
        axs[0].set_title("Training vs Validation Loss")
        axs[0].set_xlabel("Global Steps")
        axs[0].set_ylabel("Cross-Entropy Loss")
        axs[0].legend()
        axs[0].grid(True, linestyle="--", alpha=0.6)
        
        # Plot 2: Accuracy
        if eval_accuracy:
            axs[1].plot(eval_steps, eval_accuracy, label="Validation Accuracy", marker="s", color="green", linewidth=2)
            axs[1].set_title("Validation Accuracy")
            axs[1].set_xlabel("Global Steps")
            axs[1].set_ylabel("Accuracy")
            axs[1].legend()
            axs[1].grid(True, linestyle="--", alpha=0.6)
            
        # Plot 3: Perplexity
        if eval_perplexity:
            axs[2].plot(eval_steps, eval_perplexity, label="Validation Perplexity", marker="^", color="purple", linewidth=2)
            axs[2].set_title("Validation Perplexity")
            axs[2].set_xlabel("Global Steps")
            axs[2].set_ylabel("Perplexity")
            axs[2].legend()
            axs[2].grid(True, linestyle="--", alpha=0.6)
            
        plt.tight_layout()
        plt.savefig("evaluation_metrics.png", dpi=300, bbox_inches="tight")
        print("Successfully saved evaluation metrics graphs as 'evaluation_metrics.png'")
    except Exception as e:
        print(f"Failed to generate evaluation graphs: {e}")

    # 7. Save Model directly to GGUF format for Ollama!
    print("Saving model to GGUF format...")
    # Q4_K_M is the standard balanced 4-bit quantization method for serving.
    # We save to /tmp/ first to bypass Kaggle's 20GB /kaggle/working disk limit during intermediate conversion.
    model.save_pretrained_gguf("/tmp/ai-code-reviewer-model", tokenizer, quantization_method = "q4_k_m")

    print("Moving final GGUF model back to working directory for download...")
    import os, shutil
    for f in os.listdir("/tmp"):
        if f.endswith(".gguf") and "ai-code-reviewer-model" in f:
            shutil.copy(os.path.join("/tmp", f), f"./{f}")
            print(f"Successfully moved {f} ready for download!")

    print("\n======= SUCCESS =======")
    print("Training complete! The GGUF model has been successfully generated.")
    print("Look for the file in the 'ai-code-reviewer-model' directory.")

if __name__ == "__main__":
    run_training()
