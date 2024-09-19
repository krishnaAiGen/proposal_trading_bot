import numpy as np
import pandas as pd
from scan_proposal import *
import time
import json
from datetime import datetime
from summarize import Summarization
from sentiment import FinBERTSentiment

with open('config.json', 'r') as json_file:
    config = json.load(json_file)

def store_data():
    print("Creating firebase client")
    db = create_firebase_client()
    
    print("Initating first DB creation")
    proposal_dict = download_and_save_proposal(db)
    start_time = store_into_db(proposal_dict)
    print("Key DB created successfully")
    
    proposal_post_all = pd.DataFrame(columns = ["post_id", "coin", "description", "summary", "sentiment", "sentiment_score"])    
    proposal_post_all.to_csv(config['data_dir'] + '/proposal_post_all.csv')
    print("Proposal_post_all DB created successfully")
    
    empty_data = {}
    with open(config['data_dir'] + 'proposal_post_live.json', 'w') as json_file:
        json.dump(empty_data, json_file, indent=4)
        
    print("Proposal_post_live DB created successfully")

def store_into_live(coin, post_id, trade_id, description, buying_price, buying_time, stop_loss_price, proposal_post_live):
    new_data = {
        "coin" : coin,
        "post_id": post_id,
        "description": description,
        "buying_price": buying_price,
        "buying_time": buying_time,
        "stop_loss_price": stop_loss_price,
        "status" : "unsold"
        }
    
    proposal_post_live[trade_id] = new_data
    
    return proposal_post_live

def trigger_trade(new_row_df):
    if len(new_row_df) != 0:
        proposal_post_all = pd.read_csv(config['data_dir'] + '/proposal_post_all.csv')
        summary_obj = Summarization("mistral")
        sentiment_analyzer = FinBERTSentiment()
        
        with open(config['data_dir'] + 'proposal_post_live.json', 'r') as json_file:
            proposal_post_live = json.load(json_file)

        
        for index, row in new_row_df.iterrows():
            coin = row['coin']
            post_id = row['post_id']
            description = row['description']
            
            summary = summary_obj.summarize_text(row['description'])            
            sentiment, sentimnet_score = sentiment_analyzer.predict(summary)
            
            if sentiment == 'positive' and sentimnet_score >= 0.7:
                buying_price, stop_loss_price, trade_id = buy_call(coin)
                proposal_post_live = store_into_live(coin, post_id, trade_id, description, buying_price, buying_time, stop_loss_price, proposal_post_live)        
 
            if sentiment == 'negative' and sentimnet_score >= 0.7:
                buying_price, stop_loss_price = buy_put(coin)
                proposal_post_live = store_into_live(coin, post_id, trade_id, description, buying_price, buying_time, stop_loss_price, proposal_post_live)        

                
            new_row = {
                "post_id" :  post_id,
                "coin" : coin,
                "description": description,
                "summary" :  summary,
                "sentiment" :  sentiment,
                "sentiment_score" : sentimnet_score,
                }
            
            proposal_post_all = pd.concat([proposal_post_all, new_row], ignore_index=True)
        
        with open(config['data_dir'] + 'proposal_post_live.json', 'w') as json_file:
            json.dump(proposal_post_live, json_file, indent=4)    
            

def scan_data():
    while True:
        proposal_dict = download_and_save_proposal()
        new_row_df = check_new_post(proposal_dict)
        trigger_trade(new_row_df)
        
        time.sleep(5*60)
     
        
        
