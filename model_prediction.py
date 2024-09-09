import torch
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import RobertaTokenizer, RobertaModel
import torch.nn as nn
from safetensors.torch import load_file
from transformers import RobertaTokenizer, RobertaForSequenceClassification, AutoConfig



# Initialize the BERT tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Function to load the trained model and make predictions
def classify_bullish_bearish(model_path, texts, label_mapping):
    """
    Load a trained RoBERTa model from a specified path and make predictions on input texts.

    Args:
    model_path (str): Path to the directory containing the saved model.
    texts (list of str): List of input texts for prediction.
    label_mapping (dict): A dictionary mapping label indices to their corresponding names.

    Returns:
    list: Predicted labels for the input texts.
    """
    # Check if a compatible device is available and set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')

    # Load the RoBERTa tokenizer from the pre-trained model directly
    tokenizer = RobertaTokenizer.from_pretrained('roberta-base')

    # Load the configuration for the model
    config = AutoConfig.from_pretrained(model_path)

    # Load the model weights from the safetensors file
    model_weights = load_file(f"{model_path}/model.safetensors")

    # Initialize the model with the loaded configuration and weights
    model = RobertaForSequenceClassification(config).to(device)
    model.load_state_dict(model_weights)

    # Tokenize the input texts
    encodings = tokenizer(texts, truncation=True, padding=True, max_length=128, return_tensors='pt')
    encodings = {key: val.to(device) for key, val in encodings.items()}

    # Set the model to evaluation mode and make predictions
    model.eval()
    with torch.no_grad():
        outputs = model(**encodings)
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=-1).cpu().numpy()

    # Decode the predictions using the provided label mapping
    decoded_predictions = [label_mapping[pred] for pred in predictions]
    return decoded_predictions

# Custom model class for regression using RoBERTa
class RobertaForRegression(nn.Module):
    def __init__(self, model_name='roberta-large'):
        super(RobertaForRegression, self).__init__()
        self.roberta = RobertaModel.from_pretrained(model_name)
        self.regressor = nn.Linear(self.roberta.config.hidden_size, 1)  # Regression head

    def forward(self, input_ids, attention_mask=None):
        outputs = self.roberta(input_ids, attention_mask=attention_mask)
        logits = self.regressor(outputs.pooler_output)  # Use the pooled output for regression
        return logits

# Function to load the trained model and make predictions
def predict_average_price(model_path, texts):
    """
    Load the trained model from the given path and predict the price based on the provided text.

    Args:
    model_path (str): Path to the directory containing the saved model.
    texts (list of str): List of input texts for prediction.

    Returns:
    list: Predicted prices for the input texts.
    """
    # Check if a compatible GPU is available and set device
    # device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    device = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')

    # Load the tokenizer
    tokenizer = RobertaTokenizer.from_pretrained('roberta-large')

    # Load the trained model
    model = RobertaForRegression()
    state_dict = load_file(f"{model_path}/model.safetensors")  # Load the model using safetensors
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()

    # Preprocess the input texts
    encodings = tokenizer(texts, truncation=True, padding=True, max_length=128, return_tensors='pt')
    encodings = {key: val.to(device) for key, val in encodings.items()}

    # Predict prices
    with torch.no_grad():
        logits = model(**encodings)
        predictions = logits.squeeze().cpu().numpy()  # Flatten and convert to numpy array

    return predictions  

# Function to load the trained model and make predictions
def predict_high_price(model_path, texts):
    # Check if a compatible GPU is available and set device
    # device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    device = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')

    # Load the tokenizer
    tokenizer = RobertaTokenizer.from_pretrained('roberta-large')

    # Load the trained model
    model = RobertaForRegression()
    state_dict = load_file(f"{model_path}/model.safetensors")  # Load the model using safetensors
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()

    # Preprocess the input texts
    encodings = tokenizer(texts, truncation=True, padding=True, max_length=128, return_tensors='pt')
    encodings = {key: val.to(device) for key, val in encodings.items()}

    # Predict prices
    with torch.no_grad():
        logits = model(**encodings)
        predictions = logits.squeeze().cpu().numpy()  # Flatten and convert to numpy array

    return predictions


if __name__ == "__main__":
    input_proposal_text = ["The market is looking bearish.", "I'm happy with my investments.", "It's a neutral day."]

    
    #bullish and bearish classification
    model_path = './trained_model'  # Replace with the path where the model is saved
    label_mapping = {0: 'bearish', 1: 'bullish', 2: 'neutral'}  # Use your predefined label mapping
    predictions_proposal = clasify_bullish_bearish(model_path, input_proposal_text, label_mapping)
    print("Predictions:", predictions_proposal)
    
    #get expected high price
    high_price_model_path = ''
    high_price = predict_high_price(high_price_model_path, input_proposal_text)
    
    #get expected high price
    average_price_model_path = ''
    average_price = predict_average_price(average_price_model_path, input_proposal_text)

