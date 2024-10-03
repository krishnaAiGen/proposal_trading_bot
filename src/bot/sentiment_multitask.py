import torch
from transformers import RobertaTokenizer
import torch.nn.functional as F
from sklearn.preprocessing import LabelEncoder

class MultiTaskSentimentPredictor:
    def __init__(self, model_path, proposal_type_mapping, category_mapping, device=None):
        """
        Initialize the multitask sentiment predictor.

        Args:
        - model_path: Path to the saved model and tokenizer.
        - proposal_type_mapping: A dictionary that maps the proposal type label indices to their names.
        - category_mapping: A dictionary that maps the category label indices to their names.
        - device: Device to run the model on ('cpu' or 'cuda'). If None, it will automatically choose.
        """
        self.model_path = model_path
        self.tokenizer = RobertaTokenizer.from_pretrained(model_path)
        
        # Load the saved model
        self.model = torch.load(f'{model_path}/pytorch_model.bin')
        
        # Set device (use GPU if available, otherwise CPU)
        if device is None:
            self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        else:
            self.device = torch.device(device)
        
        self.model.to(self.device)
        self.model.eval()  # Set the model to evaluation mode

        # Label mappings
        self.proposal_type_mapping = proposal_type_mapping
        self.category_mapping = category_mapping

    def predict(self, texts):
        """
        Predicts the proposal type and category for the given texts.

        Args:
        - texts: A list of strings (texts) for prediction.

        Returns:
        - A list of dictionaries containing 'proposal_type', 'proposal_confidence', 'category', 'category_confidence' for each text.
        """
        # Tokenize the input texts
        encodings = self.tokenizer(texts, truncation=True, padding=True, max_length=128, return_tensors="pt")
        input_ids = encodings['input_ids'].to(self.device)
        attention_mask = encodings['attention_mask'].to(self.device)

        # Perform predictions
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            
            # Get logits for proposal_type and category
            proposal_logits = outputs['proposal_logits']
            category_logits = outputs['category_logits']
            
            # Convert logits to probabilities using softmax
            proposal_probs = F.softmax(proposal_logits, dim=-1)
            category_probs = F.softmax(category_logits, dim=-1)
            
            # Get the predicted class and the confidence score for each task
            proposal_preds = torch.argmax(proposal_probs, dim=-1)
            category_preds = torch.argmax(category_probs, dim=-1)

        # Prepare results
        results = []
        for i in range(len(texts)):
            proposal_pred_label = self.proposal_type_mapping[proposal_preds[i].item()]
            category_pred_label = self.category_mapping[category_preds[i].item()]
            
            proposal_confidence = proposal_probs[i][proposal_preds[i]].item() * 100
            category_confidence = category_probs[i][category_preds[i]].item() * 100

            # Store the result for this text
            result = {
                'proposal_type': proposal_pred_label,
                'proposal_confidence': proposal_confidence,
                'category': category_pred_label,
                'category_confidence': category_confidence
            }
            results.append(result)

        return results

# Usage Example

# Define the label mappings (adjust these according to your saved model's label encodings)
proposal_type_mapping = {0: 'bearish', 1: 'bullish', 2: 'neutral'}
category_mapping = {0: 'high', 1: 'medium', 2: 'nn', 3: 'small', 4: 'verySmall'}

# Initialize the predictor
predictor = MultiTaskSentimentPredictor(
    model_path='./trained_multitask_model',  # Path to your saved model
    proposal_type_mapping=proposal_type_mapping,
    category_mapping=category_mapping
)

# Sample texts for prediction
texts = [ 
    
    ]

# Make predictions
predictions = predictor.predict(texts)

# Access the prediction results
for i, result in enumerate(predictions):
    print(f"Text: {texts[i]}")
    print(f"Proposal Type: {result['proposal_type']} with confidence {result['proposal_confidence']:.2f}%")
    print(f"Category: {result['category']} with confidence {result['category_confidence']:.2f}%")
    print("\n")
