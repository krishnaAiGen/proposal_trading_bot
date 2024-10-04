#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 13:55:25 2024

@author: krishnayadav
"""

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

def download_and_save_proposal(db):
    print("#########Downloading intial proposals###########")
    collection_name = 'ai_posts'
    collection_ref = db.collection(collection_name)    
    docs = collection_ref.stream()
    
    protocol_list = []
    docs_list = []
    for doc in docs:
        protocol = str(doc.id).split('--')[0]
        if protocol not in protocol_list:
            protocol_list.append(protocol)
        docs_list.append(doc.to_dict())
            
    proposal_dict = {}
    for key in protocol_list:
        discourse_df = pd.DataFrame(columns = ['protocol', 'post_id', 'timestamp', 'title', 'description'])    
        
        for doc in docs_list:   
            if doc['post_type'] == 'snapshot_proposal':
                df_row = []
                if key in doc['house_id']:
                    post_id = doc['id']
                    protocol = key
                    timestamp = doc['created_at']
                    title = doc['title']
                    description = clean_content(doc['description'])
                    
                    df_row = [protocol, post_id, timestamp, title, description]
                    
                    temp_df = pd.DataFrame([df_row], columns=discourse_df.columns)
                    
                    discourse_df = pd.concat([discourse_df, temp_df], ignore_index=True)
                    
        proposal_dict[key] = discourse_df
    
    return proposal_dict

# sum1 = 0
# for key, dataframe1 in proposal_dict.items():
#     dataframe1.to_csv(f'/Users/krishnayadav/Documents/proposal_data/discourse_data/{key}.csv')

# #saving the two dataframe into one
# for dataframe1 in os.listdir()

snapshot_data = download_and_save_proposal(db)
discourse_data = download_and_save_proposal(db)

concatenated_dict = {}
for key, values in snapshot_data.items():
    df1 = snapshot_data[key]
    df2 = discourse_data[key]
    
    concatenated_df = pd.concat([df1, df2], axis=0)
    cleaned_df = concatenated_df.drop_duplicates(subset='post_id')
    print(key, len(concatenated_df), len(cleaned_df))
    
    concatenated_dict[key] = concatenated_df
    
    concatenated_df.to_csv(f'/Users/krishnayadav/Documents/proposal_data/combined_proposal_data/{key}.csv')
    
print(concatenated_dict.keys())
    

