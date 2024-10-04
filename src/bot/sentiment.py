import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class FinBERTSentiment:
    def __init__(self):
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")    
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
        sentiment = labels[predicted_class]
        
        return sentiment, max(probabilities)

