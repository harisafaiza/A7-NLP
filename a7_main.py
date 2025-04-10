# -*- coding: utf-8 -*-
"""A7_main.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/14kXJISplaxKf_hgEkWpvtX9GriFNUKIc
"""

import pandas as pd
import numpy as np
import re
from sklearn.model_selection import train_test_split

# Load the dataset
train_df = pd.read_csv("/content/train.csv")
test_df = pd.read_csv("/content/test.csv")

# List of columns corresponding to various toxicity labels
label_cols = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']

# Ensure label columns exist in train_df before processing
if all(col in train_df.columns for col in label_cols):
    # Convert all text to lowercase
    train_df['comment_text'] = train_df['comment_text'].str.lower()
    test_df['comment_text'] = test_df['comment_text'].str.lower()

    # Remove special characters and extra spaces
    def clean_text(text):
        return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', '', str(text))).strip()

    train_df['comment_text'] = train_df['comment_text'].apply(clean_text)
    test_df['comment_text'] = test_df['comment_text'].apply(clean_text)

    # Create binary label for toxic comments
    train_df['toxic_binary'] = (train_df[label_cols].sum(axis=1) > 0).astype(int)

    # Split the dataset into training and validation
    train_df, val_df = train_test_split(train_df, test_size=0.2, random_state=42)

    # Save processed datasets
    train_df.to_csv("processed_train.csv", index=False)
    val_df.to_csv("processed_val.csv", index=False)
    test_df.to_csv("processed_test.csv", index=False)

    print(" Data preprocessing completed successfully!")
    print(train_df.head())
else:
    print(" Error: Expected toxicity label columns are missing in train.csv!")

#Model Implementation: Odd-Layer, Even-Layer, and LoRA Models
#Load DistilBERT and Tokenizer
from transformers import DistilBertTokenizer, DistilBertModel

# Load DistilBERT tokenizer and model
tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
model = DistilBertModel.from_pretrained("distilbert-base-uncased")

#Creating Student Models (Odd-Layer & Even-Layer)
import torch
from torch import nn
from transformers import DistilBertModel

class CustomDistilBert(nn.Module):
    def __init__(self, base_model, layers):
        super().__init__()
        self.distilbert = base_model
        self.layers = layers  # Layers to keep (odd or even)

    def forward(self, input_ids, attention_mask):
        outputs = self.distilbert(input_ids, attention_mask=attention_mask)
        hidden_states = outputs.hidden_states
        selected_layers = [hidden_states[i] for i in self.layers]
        return selected_layers[-1]  # Return the last selected layer output

# Odd and Even layers configurations
odd_layers = [1, 3, 5]
even_layers = [0, 2, 4]

# Create models
odd_model = CustomDistilBert(model, odd_layers)
even_model = CustomDistilBert(model, even_layers)

!pip install loralib

import torch
import torch.nn as nn
import loralib as lora
from transformers import DistilBertModel

class LoRAModel(nn.Module):
    def __init__(self, base_model):
        super().__init__()
        self.distilbert = base_model

        # Apply LoRA to attention layers of DistilBERT
        for layer in self.distilbert.transformer.layer:
            layer.attention.q_lin = lora.Linear(layer.attention.q_lin.in_features,
                                                layer.attention.q_lin.out_features)
            layer.attention.v_lin = lora.Linear(layer.attention.v_lin.in_features,
                                                layer.attention.v_lin.out_features)

    def forward(self, input_ids, attention_mask=None):
        return self.distilbert(input_ids, attention_mask=attention_mask)

# Load Pretrained DistilBERT and Apply LoRA
base_model = DistilBertModel.from_pretrained("distilbert-base-uncased")
lora_model = LoRAModel(base_model)

# Move to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
lora_model.to(device)

print("LoRA Model Loaded Successfully on:", device)

import torch
import torch.nn as nn
from transformers import Trainer, TrainingArguments, DistilBertModel
import loralib as lora

# Tokenization function
def tokenize_data(df):
    return tokenizer(list(df['comment_text']), padding=True, truncation=True, return_tensors='pt')

train_encodings = tokenize_data(train_df)
val_encodings = tokenize_data(val_df)

# Dataset class
class ToxicDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: val[idx].clone().detach() for key, val in self.encodings.items()}  # Fix applied here
        item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)  # Ensure correct dtype
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = ToxicDataset(train_encodings, train_df['toxic_binary'].values)
val_dataset = ToxicDataset(val_encodings, val_df['toxic_binary'].values)

# Training arguments
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=16,
    logging_dir='./logs',
    logging_steps=10,
    eval_strategy="epoch",
    save_strategy="epoch"
)

# LoRA Model
class LoRAModel(nn.Module):
    def __init__(self, base_model):
        super().__init__()
        self.distilbert = base_model
        self.distilbert.config.output_hidden_states = True

        for layer in self.distilbert.transformer.layer:
            layer.attention.q_lin = lora.Linear(layer.attention.q_lin.in_features, layer.attention.q_lin.out_features)
            layer.attention.v_lin = lora.Linear(layer.attention.v_lin.in_features, layer.attention.v_lin.out_features)

        self.classifier = nn.Linear(self.distilbert.config.hidden_size, 2)  # Binary classification

    def forward(self, input_ids, attention_mask=None, labels=None):
        outputs = self.distilbert(input_ids, attention_mask=attention_mask)
        hidden_states = outputs.hidden_states[-1]  # Last hidden state
        logits = self.classifier(hidden_states[:, 0, :])  # Use CLS token

        if labels is not None:
            loss_fn = nn.CrossEntropyLoss()
            loss = loss_fn(logits, labels)
            return {"loss": loss, "logits": logits}
        return {"logits": logits}

# Initialize model
base_model = DistilBertModel.from_pretrained("distilbert-base-uncased")
lora_model = LoRAModel(base_model)

trainer = Trainer(
    model=lora_model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

# Train the model
trainer.train()

#Model Evaluation
from sklearn.metrics import classification_report, confusion_matrix

# Get predictions
preds = trainer.predict(val_dataset)
predictions = np.argmax(preds.predictions, axis=-1)

# Classification report and confusion matrix
print(classification_report(val_df['toxic_binary'], predictions))
print(confusion_matrix(val_df['toxic_binary'], predictions))