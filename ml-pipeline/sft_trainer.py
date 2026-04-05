# sft_trainer.py
# Use Unsloth for 2x faster, 70% less memory training of LLMs on Kaggle.

import torch
from unsloth import FastLanguageModel
from datasets import load_from_disk
from trl import SFTTrainer
from transformers import TrainingArguments

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
        use_gradient_checkpointing = "unsloth", # Restored Unsloth memory magic since we have a much better workaround now
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

    # 5. Connect SFT Trainer
    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = dataset,
        dataset_text_field = "text",
        max_seq_length = max_seq_length,
        dataset_num_proc = 2,
        packing = False, # Packing explicitly disabled to prevent Tesla T4 16GB Memory Overload
        args = TrainingArguments(
            per_device_train_batch_size = 1, # Strictly dropped to 1 to prevent CUDA Out Of Memory!
            gradient_accumulation_steps = 8, # Increased to keep effective batch size mathematically identical
            warmup_steps = 5,
            max_steps = 60, # Increase to num_epochs=1 for actual training
            learning_rate = 2e-4,
            fp16 = not torch.cuda.is_bf16_supported(),
            bf16 = torch.cuda.is_bf16_supported(),
            logging_steps = 1,
            optim = "adamw_8bit",
            weight_decay = 0.01,
            lr_scheduler_type = "linear",
            seed = 3407,
            output_dir = "unsloth_outputs",
        ),
    )

    # 6. Execute Training
    print("Beginning Training...")
    
    # --- HOTFIX FOR TRANSFORMERS 5.x VERSION MISMATCH ---
    # Unsloth's training_step override crashes on newer transformers due to a signature change (num_items_in_batch).
    # We safely revert the training_step back to the native HuggingFace Trainer to prevent the integer exception.
    import types
    from transformers import Trainer
    trainer.training_step = types.MethodType(Trainer.training_step, trainer)
    
    trainer_stats = trainer.train()
    
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
