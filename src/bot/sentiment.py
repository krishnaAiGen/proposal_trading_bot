import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import torch.nn.functional as F

class SentimentPredictor:
    def __init__(self, model_path):
        # Load the trained model and tokenizer
        self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        self.model = RobertaForSequenceClassification.from_pretrained(model_path).to(self.device)
        self.tokenizer = RobertaTokenizer.from_pretrained(model_path)
        self.model.eval()
        
        # Define label mapping
        self.label_mapping = {0: "negative", 1: "positive", 2: "neutral"}

    def predict(self, texts):
        # Check if single text or list of texts
        if isinstance(texts, str):
            texts = [texts]

        # Tokenize and prepare inputs
        encodings = self.tokenizer(texts, truncation=True, padding=True, max_length=128, return_tensors='pt')
        encodings = {key: val.to(self.device) for key, val in encodings.items()}
        
        # Get predictions
        with torch.no_grad():
            outputs = self.model(**encodings)
            logits = outputs.logits
            probs = F.softmax(logits, dim=-1)
            predictions = torch.argmax(probs, dim=-1)
        
        # Map predictions to labels and return results
        results = [{"text": text, 
                    "prediction": self.label_mapping[int(pred)], 
                    "probability": prob.tolist()} for text, pred, prob in zip(texts, predictions, probs)]
        
        return results[0]['prediction'], max(results[0]['probability'])
    


# predictor = SentimentPredictor(model_path='/Users/krishnayadav/Documents/trading_model_Dec/trained_model_sentiment/')

# Predict on new text(s)


# predictions = predictor.predict("""
                                
#                                 This proposal’s expectation is to produce a community signal. Full details and discussions thus far can be found at:

# https://forum.sushi.com/discussion/25769-treasury-diversification-proposal

# Synopsis:

# As the Sushi DAO continues to evolve, it is crucial to ensure the sustainability and growth of our treasury. The DAO ultimately holds its treasury in SUSHI tokens, which exposes it to high volatility and potential liquidity challenges. This proposal outlines a strategy for diversifying the treasury assets to mitigate risks and enhance the protocol’s long-term stability.

# Objectives:

# Reduce Volatility: Minimize the impact of native token holdings on the treasury’s value.
# Enhance Liquidity: Increase liquidity for operations and strategic assets.
# Generate Yield: Explore staking, lending, or liquidity provision opportunities.
# TLDR:

# Full strategy of the treasury diversification proposal can be found in the forum post attached.
#                                 """)
                                
# predictions[0]['prediction']



