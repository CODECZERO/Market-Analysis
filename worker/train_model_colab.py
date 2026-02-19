"""
Fine-Tuning Script for Brand Expert Model
=========================================

Instructions for Google Colab:
1. Upload your 'training_data.jsonl' file to Colab.
2. Install dependencies:
   !pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
   !pip install --no-deps "xformers<0.0.27" "trl<0.9.0" peft accelerate bitsandbytes
3. Run this script.
"""

import torch
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments, TrainerCallback
import random
import matplotlib.pyplot as plt

# 1. Configuration
max_seq_length = 2048 # Choose any! We auto support RoPE Scaling internally!
dtype = None # None for auto detection. Float16 for Tesla T4, V100, Bfloat16 for Ampere+
load_in_4bit = True # Use 4bit quantization to reduce memory usage. Can be False.

# 2. Load Model (Llama 3.2 8B or 1B)
model_name = "unsloth/Llama-3.2-3B-Instruct" # 3B is great for edge devices/workers

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_name,
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# 3. Add LoRA Adapters (Fine-tuning config)
model = FastLanguageModel.get_peft_model(
    model,
    r = 16, # Choose any number > 0 ! Suggested 8, 16, 32, 64, 128
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",],
    lora_alpha = 16,
    lora_dropout = 0, # Supports any, but = 0 is optimized
    bias = "none",    # Supports any, but = "none" is optimized
    use_gradient_checkpointing = "unsloth", # True or "unsloth" for very long context
    random_state = 3407,
    use_rslora = False,  # We support rank stabilized LoRA
    loftq_config = None, # And LoftQ
)

# 4. Load Your Data
dataset = load_dataset("json", data_files="training_data.jsonl", split="train")

# 4.1 Split Data for Evaluation (to measure Bias/Variance)
# 90% Training, 10% Evaluation (Testing)
dataset = dataset.train_test_split(test_size=0.1)
train_dataset = dataset["train"]
eval_dataset = dataset["test"]

print(f"Training Samples: {len(train_dataset)}")
print(f"Evaluation Samples: {len(eval_dataset)}")

# 5. Format Prompts
def formatting_prompts_func(examples):
    inputs = examples["input_text"]
    outputs = examples["output_json"]
    texts = []
    
    # Simple prompt template matching your worker logic
    prompt_template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a brand reputation specialist.<|eot_id|><|start_header_id|>user<|end_header_id|>

{}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
    
    for input_text, output_data in zip(inputs, outputs):
        import json
        if isinstance(output_data, (dict, list)):
            output_str = json.dumps(output_data)
        else:
            output_str = str(output_data)
            
        text = prompt_template.format(input_text) + output_str + "<|eot_id|>"
        texts.append(text)
    return { "text" : texts, }

train_dataset = train_dataset.map(formatting_prompts_func, batched = True)
eval_dataset = eval_dataset.map(formatting_prompts_func, batched = True)

# 5.5 Data Preview (Sanity Check)
print("="*80)
print("DATA PREVIEW: Input Example")
print("="*80)
print(train_dataset[0]["text"])
print("="*80)

# 6. Train the Model

class DetailedLogCallback(TrainerCallback):
    def on_log(self, args, state, control, logs=None, **kwargs):
        _ = logs.pop("total_flos", None)
        if state.is_local_process_zero:
            step = state.global_step
            if "loss" in logs:
                print(f"--> Step {step}: Train Loss = {logs['loss']:.4f}")
            if "eval_loss" in logs:
                print(f"--> Step {step}: VAL LOSS = {logs['eval_loss']:.4f} (Checking Overfitting)")

# 6.1 Inference Testing Callback (The "Exam" during class)
class GenerationCallback(TrainerCallback):
    def __init__(self, model, tokenizer, test_inputs):
        self.model = model
        self.tokenizer = tokenizer
        self.test_inputs = test_inputs
        
    def on_step_end(self, args, state, control, **kwargs):
        # Run test every 10 steps
        if state.global_step % 10 == 0 and state.global_step > 0:
            print(f"\n\n[STEP {state.global_step}] RUNNING LIVE TEST...")
            
            # Pick a random test case
            test_case = random.choice(self.test_inputs)
            # Preview the prompt (skip system header for readability)
            preview = test_case.split("user<|end_header_id|>")[-1][:100].replace("\n", " ")
            print(f"Testing Input: {preview}...")
            
            # 1. Switch to Inference Mode (Fast)
            FastLanguageModel.for_inference(self.model)
            
            # 2. Generate
            inputs = self.tokenizer([test_case], return_tensors = "pt").to("cuda")
            outputs = self.model.generate(**inputs, max_new_tokens = 256, use_cache = True)
            decoded = self.tokenizer.batch_decode(outputs)[0]
            
            # 3. Extract JSON part (Basic parsing)
            try:
                # Assuming prompt ends with "assistant<|end_header_id|>"
                response = decoded.split("assistant<|end_header_id|>")[-1].strip()
                import json
                
                # Cleanup potential extra tokens like <|eot_id|>
                clean_json = response.replace("<|eot_id|>", "").strip()
                
                # Try validation
                json.loads(clean_json) # Will crash if invalid
                print(f"✅ PASSED JSON CHECK:\n{clean_json[:120]}...")
            except Exception as e:
                print(f"❌ FAILED JSON CHECK: {e}\nOutput: {decoded[-200:]}")
            
            # 4. Switch back to Training
            FastLanguageModel.for_training(self.model)

# Define diverse test cases (Multilingual, Competitors, Slang)
test_inputs = [
    # 1. Basic Complaint
    """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a brand reputation specialist.<|eot_id|><|start_header_id|>user<|end_header_id|>

Analyze this tweet: "Brand X service is absolutely terrible, I waited on hold for 2 hours!"<|eot_id|><|start_header_id|>assistant<|end_header_id|>

""",
    # 2. Competitor Mention
    """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a brand reputation specialist.<|eot_id|><|start_header_id|>user<|end_header_id|>

Analyze this tweet: "Honestly, the new Samsung S24 wipes the floor with the iPhone. Switching tomorrow."<|eot_id|><|start_header_id|>assistant<|end_header_id|>

""",
    # 3. Multilingual (Spanish)
    """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a brand reputation specialist.<|eot_id|><|start_header_id|>user<|end_header_id|>

Analyze this tweet: "No puedo creer lo bueno que es este producto, me encanta!"<|eot_id|><|start_header_id|>assistant<|end_header_id|>

""",
    # 4. Slang / Internet Speak
    """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a brand reputation specialist.<|eot_id|><|start_header_id|>user<|end_header_id|>

Analyze this tweet: "yooo this drop is lit af no cap fr fr"<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
]

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = train_dataset,
    eval_dataset = eval_dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    packing = False,
    callbacks = [DetailedLogCallback(), GenerationCallback(model, tokenizer, test_inputs)],
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 60, 
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        
        # Evaluation Settings (For Graphs)
        eval_strategy = "steps",
        eval_steps = 10, # Check validation every 10 steps
        save_strategy = "no",
        
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
        report_to = "none", # Disable wandb for simple local graphs
    ),
)

# Check if we should resume from a checkpoint
import os
last_checkpoint = None
if os.path.exists("outputs"):
    # Simple check for existing checkpoints
    checkpoints = [d for d in os.listdir("outputs") if d.startswith("checkpoint")]
    if checkpoints:
        print(f"🔄 Found existing checkpoints: {checkpoints}. Resuming training...")
        last_checkpoint = True

trainer_stats = trainer.train(resume_from_checkpoint=last_checkpoint)

# 7. Visualization: Bias/Variance Graph
history = trainer.state.log_history
train_loss = []
eval_loss = []
steps = []

for entry in history:
    if "loss" in entry:
        train_loss.append(entry["loss"])
        # If eval_loss is not in this exact step, we might want to interpolate or just plot available points
        # But usually 'loss' and 'eval_loss' are logged at different frequencies.
        # Let's collect them separately.
        
train_steps = [x["step"] for x in history if "loss" in x]
train_values = [x["loss"] for x in history if "loss" in x]

eval_steps = [x["step"] for x in history if "eval_loss" in x]
eval_values = [x["eval_loss"] for x in history if "eval_loss" in x]

plt.figure(figsize=(10, 6))
plt.plot(train_steps, train_values, label="Training Loss", alpha=0.7)
plt.plot(eval_steps, eval_values, label="Validation Loss", linewidth=2, color="red")
plt.title("Model Training Performance (Bias & Variance Test)")
plt.xlabel("Training Steps")
plt.ylabel("Loss (Lower is Better)")
plt.legend()
plt.grid(True)

# Interpretation Text
plt.figtext(0.5, -0.1, 
            "Gap between lines = Variance (Overfitting)\nHigh values = Bias (Underfitting)", 
            ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})

print("Saving training graph to 'training_graph.png'...")
plt.savefig("training_graph.png", bbox_inches="tight")
plt.show()

# 8. Export for Ollama
print("Saving model to GGUF format for Ollama...")
model.save_pretrained_gguf("model_gguf", tokenizer, quantization_method = "q4_k_m")

print("DONE! Graph saved as 'training_graph.png'.")
