import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from transformers import BertTokenizer, BertModel
import torch

# Load data
data = pd.read_csv("/Users/krishnayadav/Downloads/mistral.csv")
data['proposal_type'].value_counts()
data['proposal'] = data['proposal'].fillna('').astype(str)


# Drop unnecessary column
data = data.drop("Unnamed: 0", axis=1)

# Initialize BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Function to generate BERT embeddings for a given sentence
def get_bert_embeddings(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    # Use the mean of the last hidden state as the sentence embedding
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

# Generate BERT embeddings for all the text in the dataset
X = np.array([get_bert_embeddings(sentence) for sentence in data['proposal']])
y = data['proposal_type']

# Handle imbalanced classes using SMOTE
# smote = SMOTE()
# X_resampled, y_resampled = smote.fit_resample(X, data['proposal_type'])

# Split data into training and testing sets
# X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# Initialize and train RandomForest model
rf_model = RandomForestClassifier()
rf_model.fit(X_train, y_train)

# Predict on test data
y_pred = rf_model.predict(X_test)

# Evaluate the model
print(classification_report(y_test, y_pred))

# Confusion Matrix
conf_matrix = confusion_matrix(y_test, y_pred)

# Plotting Confusion Matrix
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=rf_model.classes_, yticklabels=rf_model.classes_)
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Confusion Matrix')
plt.show()

# Predict class and probabilities for a new sentence
# new_sentence = "The text discusses changes in the Community Council of an unspecified entity, due to Hasherror's resignation. Two options are proposed: either replacing Hasherror with Tritium or pscoolidge, both maintaining an 8-member council size. The third option suggests a return to a 7-member council if a quorum is not reached. Overall, the text conveys a sense of change and decision-making within the council structure."



new_sentence = summ_text
new_sentence_vectorized = get_bert_embeddings(new_sentence).reshape(1, -1)

# Predict the label
predicted_label = rf_model.predict(new_sentence_vectorized)[0]

# Predict probabilities for each class
predicted_probabilities = rf_model.predict_proba(new_sentence_vectorized)

# Get the classes
classes = rf_model.classes_

# Find the score for the predicted label (probability)
predicted_score = predicted_probabilities[0][np.argmax(predicted_probabilities)]

# Print results
print(f"Predicted Label: {predicted_label}")
print(f"Predicted Probabilities for each class: {dict(zip(classes, predicted_probabilities[0]))}")
print(f"Predicted Score for the predicted label: {predicted_score}")

sum1 = 0
for key, value in proposal_dict.items():
    
    print(key, ":", len(value))
    sum1 = sum1 + len(value)
    
print(sum1)



