import pandas as pd
import numpy as np
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    TrainingArguments, 
    Trainer,
    DataCollatorWithPadding
)
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score
import os
import re
from pathlib import Path
# root directory of the project
BASE_DIR = Path.cwd()

# config
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
OUTPUT_DIR = f"{BASE_DIR}/models/raw_model"
BATCH_SIZE = 32
EPOCHS = 5
LEARNING_RATE = 2e-5
MAX_LEN = 64

id2label = {
    0: "CARD_ISSUE",
    1: "APP_LOGIN",
    2: "TRANSACTION",
    3: "LOAN_SAVING",
    4: "FRAUD_REPORT",
    5: "OTHERS"
}
label2id = {v: k for k, v in id2label.items()}

# Load data
train_df = pd.read_csv("train.csv")
val_df = pd.read_csv("val.csv")

# convert to datasets
train_dataset = Dataset.from_pandas(train_df[['text_clean', 'label_id']].rename(columns={'label_id': 'labels'}))
val_dataset = Dataset.from_pandas(val_df[['text_clean', 'label_id']].rename(columns={'label_id': 'labels'}))

# Tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize_function(examples):
    return tokenizer(
        examples["text_clean"], 
        padding="max_length", 
        truncation=True, 
        max_length=MAX_LEN
    )

# Tokenize data
tokenized_train = train_dataset.map(tokenize_function, batched=True)
tokenized_val = val_dataset.map(tokenize_function, batched=True)

# Remove text columns
tokenized_train = tokenized_train.remove_columns(["text_clean"])
tokenized_val = tokenized_val.remove_columns(["text_clean"])

# Set format for PyTorch
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, 
    num_labels=len(id2label),
    id2label=id2label,
    label2id=label2id
)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    acc = accuracy_score(labels, predictions)
    
    f1 = f1_score(labels, predictions, average='weighted')
    return {"accuracy": acc, "f1": f1}

# Training arguments
training_args = TrainingArguments(
    output_dir="./results",
    learning_rate=LEARNING_RATE,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    num_train_epochs=EPOCHS,
    weight_decay=0.01,
    evaluation_strategy="epoch",
    save_strategy="epoch",       
    load_best_model_at_end=True, 
    metric_for_best_model="f1",  
    save_total_limit=2,          
    logging_steps=50,
    report_to="none",  
    fp16=True,
    dataloader_num_workers=2              
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
    tokenizer=tokenizer,
    data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
    compute_metrics=compute_metrics,
)

print("start fine turning.")
trainer.train()
print(f"save model to: {OUTPUT_DIR}")
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("Done!")