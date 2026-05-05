# Kaggle Fine-Tuning Guide (SFT with Unsloth)

This directory contains the Python Data Pipeline and ML Training scripts needed to fine-tune your base LLM (like DeepSeek-Coder or Llama-3) on Code Vulnerability datasets (like DiverseVul). 

We are utilizing **Unsloth**, a library that makes training large models 2-5x faster and highly memory efficient, allowing you to train on a free Kaggle T4x2 GPU.

## Step-by-Step Kaggle Instructions

### 1. Setup the Notebook
*   Create a new **Kaggle Notebook**.
*   In the settings on the right sidebar, change the **Accelerator** to **GPU T4 x2**.
*   Turn **Internet** ON.

### 2. Install Engine Dependencies
Create a notebook cell and run the following pip installations. (*Note: We removed `xformers` to prevent out-of-memory RAM crashes, as modern PyTorch natively handles the attention mechanisms without needing to compile it from source*):
```bash
# FIXED: Uninstall and freshly install the official PyPI packages to prevent version mismatches
!pip uninstall unsloth unsloth_zoo -y
!pip install --upgrade --no-cache-dir unsloth unsloth-zoo
!pip install --no-deps trl peft accelerate bitsandbytes
!pip install datasets pandas
```

### 3. Move Scripts to Notebook
You have two options:
*   **Option A**: Upload `prepare_dataset.py` and `sft_trainer.py` into the Kaggle environment data section and run them natively (`!python prepare_dataset.py`).
*   **Option B**: Just copy and paste the contents of `prepare_dataset.py` into Cell 2, and `sft_trainer.py` into Cell 3.

### 4. Execute the Pipeline
Run the cell corresponding to data preparation:
```bash
!python prepare_dataset.py
```
This will download `secdbg/DiverseVul`, format it into Alpaca Instruction format, and save it to `./processed_vuln_data`.

Run the cell for the SFT training:
```bash
!python sft_trainer.py
```
*(Note: adjust `max_steps` to something like 200, 500, or use `num_epochs=1` inside the `TrainingArguments` to properly train it beyond a 60-step test).*

### 5. Export for the Backend (Ollama)
The script automatically exports the newly trained weights into the native **GGUF format** using 4-bit standard quantization (`q4_k_m`).
Once the notebook concludes:
1. Locate the GGUF file in the output directory.
2. Download it from Kaggle to your local machine (`C:/Users/91701/Documents/.../code-3`).
3. Set up the local Ollama instance with a custom Modelfile:

```dockerfile
# /ml-pipeline/Modelfile
FROM ./ai-code-reviewer-model-unsloth.Q4_K_M.gguf

TEMPLATE """Below is an instruction that describes a task, paired with input context. Write a response that appropriately completes the request.

### Instruction:
{{ .Prompt }}

### Response:
"""

SYSTEM """You are an expert AI code reviewer. Locate vulnerabilities, suggest best practices, and output structured code documentation."""
```

4. Build your tuned model locally:
```bash
ollama create custom-code-reviewer -f Modelfile
```

5. Confirm it runs locally!
```bash
ollama run custom-code-reviewer
```
