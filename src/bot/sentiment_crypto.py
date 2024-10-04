#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 15:49:59 2024

@author: krishnayadav
"""

import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification, pipeline

class CryptoSentimentAnalyzer:
    def __init__(self, model_name="kk08/CryptoBERT"):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(model_name)
        self.classifier = pipeline("sentiment-analysis", model=self.model, tokenizer=self.tokenizer)

        # Dictionary to map model labels to sentiment labels
        self.sent_dict = {
            "LABEL_0": "negative",
            "LABEL_1": "positive"
        }

    def analyze_sentiment(self, text):
        
        try:
            result = self.classifier(text)[0]
            label = result['label']
            prob = result['score']
            return self.sent_dict.get(label, "unknown sentiment"), prob
        except Exception as e:
            print(f"Error during sentiment analysis: {e}")
            return None

