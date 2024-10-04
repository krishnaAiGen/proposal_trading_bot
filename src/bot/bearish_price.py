import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification

class BearishSentimentPredictor:
    def __init__(self, model_dir, label_mapping=None):
        self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        self.model = RobertaForSequenceClassification.from_pretrained(model_dir).to(self.device)
        self.tokenizer = RobertaTokenizer.from_pretrained(model_dir)
        
        # If label_mapping is not provided, generate a default one
        if label_mapping is None:
            self.label_mapping = {i: f"label_{i}" for i in range(self.model.config.num_labels)}
        else:
            self.label_mapping = label_mapping

    def predict(self, text):
        # Preprocess and tokenize the input text
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128).to(self.device)

        # Get model outputs
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Get predicted label
        logits = outputs.logits
        predicted_class_id = torch.argmax(logits, dim=-1).item()
        
        # Convert label id to the actual label using label_mapping
        predicted_label = self.label_mapping[predicted_class_id]
        
        # Compute confidence (softmax)
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        confidence = probabilities[0][predicted_class_id].item()
        
        return {
            "predicted_label": predicted_label,
            "confidence": confidence
        }