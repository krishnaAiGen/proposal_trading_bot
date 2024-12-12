#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 13:25:48 2024

@author: krishnayadav
"""

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd

class FinBERTSentiment:
    def __init__(self, model):
        self.device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")        
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForSequenceClassification.from_pretrained(model)    
        self.model.to(self.device)

    def predict(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)        
        inputs = {key: value.to(self.device) for key, value in inputs.items()}   
        
        with torch.no_grad():
            outputs = self.model(**inputs)        
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1).cpu().numpy()[0]  # Move back to CPU for numpy processing
        
        # Get the predicted class (0=negative, 1=neutral, 2=positive)
        predicted_class = np.argmax(probabilities)
        labels = ['negative', 'neutral', 'positive']
        # sentiment = labels[predicted_class]
        sentiment = predicted_class
        
        return sentiment, max(probabilities)
    

# model_list = ["ckandemir/crypto_sentiment"]
# data = pd.read_csv("/Users/krishnayadav/Downloads/mistral.csv")
# sent_dict = {
#     "negative": "bearish",
#     "positive" : "bullish",
#     "neutral" : "neutral"
#     }


# for model in model_list:
    model = "ProsusAI/finbert"
    bert_obj = FinBERTSentiment(model)
    bert_obj.predict(summ_text)
    
#     counter = 0
#     counter1 = 0
#     for index, row in data.iterrows():
#         try:
#             print(index)
#             text = row['proposal']
#             true_prediction = row['proposal_type']
#             prediction, prob = bert_obj.predict(text)
#             print(f"{true_prediction}:{prediction}:{prob}")
            
#             if prob >= 0.8:
#                 counter1 = counter1 + 1
#                 if true_prediction == sent_dict[prediction]:
#                     counter = counter + 1
        
#         except Exception as e:
#             continue
#     print(counter, counter1)
#     print(counter/counter1)
    

#-------------------------
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline

data = pd.read_csv("/Users/krishnayadav/Downloads/mistral.csv")
tokenizer = BertTokenizer.from_pretrained("kk08/CryptoBERT")
model = BertForSequenceClassification.from_pretrained("kk08/CryptoBERT")

classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

sent_dict = {
    "LABEL_0": "bearish",
    "LABEL_1" : "bullish"
  }

result = classifier(summ_text)[0]

counter = 0
counter1 = 0
for index, row in data.iterrows():
    try:
        print(index)
        text = row['proposal']
        true_prediction = row['proposal_type']
        # if true_prediction == "neutral":
        #     continue
        # prediction, prob = bert_obj.predict(text)
        result = classifier(text)[0]
        prediction = result['label']
        prob = result['score']
        print(f"{true_prediction}:{prediction}:{prob}")
        
        if prob >= 0.9 and prediction in list(sent_dict.keys()):
            counter1 = counter1 + 1
            if true_prediction == sent_dict[prediction]:
                counter = counter + 1
    
    except Exception as e:
        print(e)
        continue
print(counter, counter1)
print(counter/counter1)


data1 = pd.read_csv("/Users/krishnayadav/Downloads/mistral.csv")
df_bullish = data1[data1['proposal_type'] == 'bullish']
# df_bullish['category'].value_counts()
df_bullish.to_csv('/Users/krishnayadav/Downloads/df_bullish.csv')

df_bearish = data1[data1['proposal_type'] == 'bearish']
df_bearish.to_csv('/Users/krishnayadav/Downloads/df_bearish.csv')


