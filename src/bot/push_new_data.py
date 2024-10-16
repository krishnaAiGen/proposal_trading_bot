import firebase_admin
from firebase_admin import credentials, firestore
import json
import pandas as pd

# Function to load configuration from a JSON file
def load_config(config_file_path):
    with open(config_file_path, 'r') as json_file:
        config = json.load(json_file)
    return config

# Function to create a Firebase client and Firestore instance
def create_firebase_client(config):
    if not firebase_admin._apps:  # Check if the app is already initialized
        cred = credentials.Certificate(config["firebase_cred"])
        app = firebase_admin.initialize_app(cred)
    else:
        app = firebase_admin.get_app()
    db = firestore.client()
    return db, app

# Function to create the data to be pushed to Firestore
def create_post_data(post_id, post_type, protocol, title, coin, timestamp, description, discussion_link, id1):
    new_row = {
        'id' : id1,
        'post_id': post_id,
        'post_type': post_type,
        'protocol': protocol,
        'title': title,
        'coin': coin,
        'timestamp': timestamp,
        'description': description,
        'discussion_link': discussion_link
    }
    return pd.DataFrame([new_row])  # Return a DataFrame if needed

# Function to push data to Firestore collection
def push_data_to_firestore(db, collection_name, data):
    collection_ref = db.collection(collection_name)
    doc_ref = collection_ref.document(data['post_id'])  # Use post_id as document ID
    doc_ref.set(data)  # Push the data using set method
    print(f"Data with post_id {data['post_id']} pushed to Firestore successfully.")

# Main function that orchestrates the above functions
def main():
    # Load config
    config = load_config('config.json')

    # Initialize Firebase
    db, app = create_firebase_client(config)

    # Prepare the post description
    description = """
    This is a signaling proposal to update Stride’s tokenomics by introducing a buyback and burn mechanism for the STRD token using Stride protocol fees...
    """

    # Create post data
    post_data_df = create_post_data(
        id1 = '77',
        post_id='aave-test1',
        post_type='snapshot_proposal',
        protocol='aave',
        title='simple title',
        coin='aave',
        timestamp='2024-11-12',
        description=description,
        discussion_link='https://commonwealth.im/stride/discussion/25027-stride-tokenomics-update-allocate-protocol-fees-to-buy-back-and-burn-strd'
    )

    # Since we need to push it as a dict, convert the DataFrame to dict
    post_data_dict = post_data_df.iloc[0].to_dict()

    # Push the data to Firestore
    push_data_to_firestore(db, 'ai_posts', post_data_dict)

# Run the main function
if __name__ == "__main__":
    main()
