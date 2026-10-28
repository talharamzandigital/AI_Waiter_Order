# Fine-Tuning: AI Waiter (Quick Bites Restaurant)

Documentation for the LoRA fine-tuning, export, and Ollama configuration of the AI Waiter conversational model.

---

## Purpose

The purpose of fine-tuning was to adapt a base instruct model into a specialized AI waiter persona for "Quick Bites Restaurant" in Lahore. The model learns conversational restaurant etiquette, answering menu questions, taking food orders, and confirming table orders in the designated persona.

---

## Base Model and Method

All training configurations and environment parameters are recorded in `fine_tuning/train_lora_colab.ipynb`:

| Parameter | Recorded Value in Notebook | Source Cell / Output |
|---|---|---|
| **Base Model** | `unsloth/mistral-7b-instruct-v0.3-bnb-4bit` | Cell 1, Cell 2 |
| **Fine-Tuning Framework** | Unsloth (version `2026.6.6`) + Hugging Face TRL (`SFTTrainer`) | Cell 0, Cell 2, Cell 8 |
| **Method** | LoRA (PEFT via `FastLanguageModel.get_peft_model`) | Cell 3 |
| **LoRA Rank ($r$)** | `16` | Cell 3 |
| **LoRA Alpha ($\alpha$)** | `16` | Cell 3 |
| **LoRA Dropout** | `0` | Cell 3 |
| **LoRA Target Modules** | `["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]` (all 32 layers patched) | Cell 3 |
| **LoRA Bias** | `"none"` | Cell 3 |
| **Gradient Checkpointing** | `"unsloth"` | Cell 3 |
| **Max Sequence Length** | `2048` | Cell 1, Cell 8 |
| **Per-Device Batch Size** | `2` | Cell 8 |
| **Gradient Accumulation Steps** | `4` | Cell 8 |
| **Total Batch Size** | `8` ($2 \times 4 \times 1$) | Cell 8 output |
| **Warmup Steps** | `5` | Cell 8 |
| **Max Training Steps** | `60` | Cell 8 |
| **Learning Rate** | `2e-4` | Cell 8 |
| **Precision** | `fp16 = True` | Cell 8 |
| **Optimizer** | `adamw_8bit` | Cell 8 |
| **Random Seed** | `3407` | Cell 3, Cell 8 |
| **Dataset Size** | `52` examples | Cell 7, Cell 8 output |
| **Training Epochs** | `9` epochs (progress stopped at epoch `8.62/9` at step 60) | Cell 8 output |
| **Trainable Parameters** | `41,943,040` of `7,289,966,592` total ($0.58\%$ trained) | Cell 8 output |
| **Hardware / GPU** | `Tesla T4` (1 GPU, Max memory: `14.563 GB`, Platform: `Linux`, CUDA `7.5`/`12.8`) | Cell 2 output |

---

## Training Result

Training was executed with `logging_steps = 10` for a total of 60 steps. The recorded training time was **03:17** (3 minutes 17 seconds).

### Logged Training Loss
Recorded directly from the dataframe output of Cell 8 in `train_lora_colab.ipynb`:

| Step | Training Loss |
|:---:|:---:|
| 10 | 1.846143 |
| 20 | 0.665788 |
| 30 | 0.377555 |
| 40 | 0.234267 |
| 50 | 0.170302 |

*Note on final step*: The last logged loss value in the table is at **step 50**. Step 60 completed the training loop, but loss at step 60 was not emitted prior to trainer completion.

### Checkpoint PicklingError and Adapter Saving
Immediately after completing the 60 training steps, `trainer.train()` attempted to save the full trainer state and raised a `PicklingError`:
```text
PicklingError: Can't pickle <class 'trl.trainer.sft_config.SFTConfig'>: it's not the same object as trl.trainer.sft_config.SFTConfig
```
Because the training loop itself had already finished, the LoRA adapter weights and tokenizer were saved separately in Cell 9 using:
```python
model.save_pretrained("ai_waiter_model")
tokenizer.save_pretrained("ai_waiter_model")
```
This completed successfully (`"Model saved successfully!"`).

---

## Export

The trained model and tokenizer were merged to 16-bit and converted to GGUF format using Unsloth's `model.save_pretrained_gguf` in Cell 10 and Cell 13:
* **Quantization Method**: `q4_k_m` (4-bit medium quantization)
* **Exported File Name**: `mistral-7b-instruct-v0.3.Q4_K_M.gguf`
* **File Size**: **4,372,815,648 bytes** (~4.07 GiB / 4.1 GB, logged in Cell 21 and Cell 22 download metadata)
* **Hugging Face Hub Repository**: Uploaded to [`Talha-rajput/ai-waiter-quickbites`](https://huggingface.co/Talha-rajput/ai-waiter-quickbites) via `HfApi().upload_file(...)` in Cell 20.

> **Note**: The GGUF binary file (`4.37 GB`) is hosted on Hugging Face and is **not** committed to this Git repository.

---

## How to Run It Locally

To run the fine-tuned model locally using Ollama:

1. **Download the GGUF file** from Hugging Face into the `fine_tuning/` directory and rename it to `ai-waiter.gguf`:
   ```bash
   # From the fine_tuning/ directory:
   curl -L -o ai-waiter.gguf https://huggingface.co/Talha-rajput/ai-waiter-quickbites/resolve/main/mistral-7b-instruct-v0.3.Q4_K_M.gguf
   ```
2. **Review the Modelfile**:
   The file `fine_tuning/Modelfile` references the downloaded GGUF:
   ```dockerfile
   FROM ./ai-waiter.gguf

   SYSTEM """
   You are a friendly AI waiter for Quick Bites Restaurant in Lahore.
   Help customers browse menu, take orders, and confirm them.
   Always be polite and professional.
   """
   ```
3. **Create the model in Ollama**:
   ```bash
   ollama create ai-waiter -f Modelfile
   ```
4. **Test the model interactively**:
   ```bash
   ollama run ai-waiter
   ```

When Ollama is running at `http://localhost:11434`, the Django application (`django_ai_waiter`) automatically detects the model `ai-waiter:latest` and routes chat requests to it.

---

## Dataset

* **Source File**: `fine_tuning/ai_waiter_dataset.jsonl`
* **Size**: 52 conversation examples (52 lines of valid JSON)
* **Structure**: Each example is a single-turn conversation containing 3 messages:
  1. `system`: Setting the persona as an AI waiter for "Quick Bites Restaurant" in Lahore.
  2. `user`: Customer query or order instruction.
  3. `assistant`: Polite, domain-specific waiter response with menu items, prices, or order status.
* **Origin**: The dataset was generated with LLM assistance and manually reviewed and verified by the author.

---

## Known Limitations

1. **Small Dataset & Lack of Evaluation Split**: The training dataset contains only **52 examples** trained for **~9 epochs** (60 steps). There was **no validation split** and **no held-out test evaluation**. Consequently, the low training loss ($0.1703$ at step 50) is not evidence of generalization (it may partly reflect memorization of the small training set).
2. **Prompt Template Mismatch**: The dataset formatting script (Cell 7) formatted training samples using Llama-2 style tags:
   ```text
   <s>[INST] <<SYS>>
   {system_message}
   <</SYS>>

   {user_message} [/INST] {assistant_message} </s>
   ```
   However, the base model is `Mistral-7B-Instruct-v0.3`, which natively uses `[INST] ... [/INST]` prompt syntax and does not recognize the `<<SYS>>` syntax.
3. **No `TEMPLATE` in Modelfile**: The provided `fine_tuning/Modelfile` defines only `FROM ./ai-waiter.gguf` and `SYSTEM """..."""`, without a custom `TEMPLATE` block specifying exact token delimiters.
4. **Baked-in Prices vs. Live Tools**: Fixed prices and item details are baked directly into the training texts. In production, live menu availability and pricing are strictly retrieved via database tools (MCP / `MCPServer`), not from LLM internal weights.
5. **Conflicting duplicate in the dataset**: The user message "What payment methods do you accept?" appears twice (zero-based records 44 and 47) with different assistant answers (cash only vs. cash, JazzCash, EasyPaisa and card), so the model saw conflicting targets for the same input.
6. **Single-turn only**: All 52 examples are single-turn (one user message and one assistant reply). There are no multi-turn dialogues, so behaviour across a longer order conversation (changing items, confirming) was neither trained nor evaluated.
