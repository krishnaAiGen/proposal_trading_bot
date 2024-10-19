import pandas as pd 
import numpy as np

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import os
import pandas as pd
from bs4 import BeautifulSoup
from pymongo import MongoClient
import json
from datetime import datetime
from suppress_logging import SuppressLogging
from google.api_core.retry import Retry


with open('config.json', 'r') as json_file:
    config = json.load(json_file)

def create_firebase_client():
    cred = credentials.Certificate(config["firebase_cred"])
    app = firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    return db, app  # Return both the Firestore client and app instance


def clean_content(html_text):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_text, 'html.parser')
    
    # Get the clean text by extracting only the text part
    clean_text = soup.get_text()
    
    return clean_text

def download_and_save_proposal(db, scan):
    print("#########Downloading intial proposals###########")
    retry_strategy = Retry()
    collection_name = 'ai_posts'
    collection_ref = db.collection(collection_name)    
    
    if scan:
        docs = collection_ref.order_by('created_at', direction='DESCENDING').limit(100).stream(retry=retry_strategy)
    else:
        docs = collection_ref.stream(retry=retry_strategy)

    
    protocol_list = []
    docs_list = []
    for doc in docs:
        protocol = str(doc.id).split('--')[0]
        if protocol not in protocol_list:
            protocol_list.append(protocol)
        docs_list.append(doc.to_dict())
        
    proposal_dict = {}
    for key in protocol_list:
        discourse_df = pd.DataFrame(columns = ['protocol', 'post_id', 'timestamp', 'title', 'description', "discussion_link"])    
        
        for doc in docs_list: 
            try:
                
                # doc = post_data_df.iloc[0]
                # key = 'aave'
                
                if doc['post_type'] == 'snapshot_proposal':
                    df_row = []
                    if key in doc['house_id']:
                        post_id = doc['id']
                        protocol = key
                        timestamp = doc['created_at']
                        title = doc['title']
                        description = clean_content(doc['description'])
                        
                        try:
                            discussion_link = doc['discussion_link']
                        except Exception as e:
                            discussion_link = ''
                        
                        df_row = [protocol, post_id, timestamp, title, description, discussion_link]
                        
                        temp_df = pd.DataFrame([df_row], columns=discourse_df.columns)
                        
                        with SuppressLogging():
                            discourse_df = pd.concat([discourse_df, temp_df], ignore_index=True)
            
            except Exception as e:
                print(doc)
                continue
                    
        proposal_dict[key] = discourse_df
    
    return proposal_dict


def check_new_post(proposal_dict):
    proposal_post_id = list(pd.read_csv(config["data_dir"] + '/proposal_post_id.csv', index_col=0)['post_id'])
    
    columns = ["post_id", "coin", "description", "discussion_link", "timestamp"]
    new_row_df = pd.DataFrame(columns = columns)
    
    for key, coin_df in proposal_dict.items():
        for index, row in coin_df.iterrows():
            
            # row = post_data_df.iloc[0]
            
            post_id = row['post_id']
            if post_id not in proposal_post_id:
                coin = post_id.split("--")[0]
                description = row['description']
                discussion_link = row['discussion_link']
                timestamp = row['timestamp']
                
                new_row = {
                    "post_id" : post_id,
                    "coin" : coin,
                    "description": description,
                    "discussion_link": discussion_link,
                    "timestamp": timestamp
                    }
                with SuppressLogging():
                    new_row_df = pd.concat([new_row_df, pd.DataFrame([new_row])], ignore_index=True)
                    
    return new_row_df


"""
Sharing initial dumped data into db.
"""
def store_into_db(proposal_dict):
    proposal_csv = pd.DataFrame()
    key_list = []
    
    for coin in proposal_dict:
        temp_key = proposal_dict[coin]['post_id']
        for key in temp_key:
            if key not in key_list:
                key_list.append(key)
    
    proposal_csv['post_id'] =  key_list
    
    proposal_csv.to_csv(config["data_dir"] + '/proposal_post_id.csv')
    
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return start_time


    
    
    

    
    
