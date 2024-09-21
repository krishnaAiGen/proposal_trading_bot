import numpy as np
import pandas as pd
from scan_proposal import *
import time
import json
from datetime import datetime
from summarize import Summarization
from sentiment import FinBERTSentiment
from sell import format_time_utc

with open('config.json', 'r') as json_file:
    config = json.load(json_file)

def store_data():
    print("Initating first DB creation")
    proposal_dict = download_and_save_proposal(db)
    start_time = store_into_db(proposal_dict)
    print("Key DB created successfully")
    
    proposal_post_all = pd.DataFrame(columns = ["timestamp", "post_id", "coin", "description", "summary", "sentiment", "sentiment_score"])    
    proposal_post_all.to_csv(config['data_dir'] + '/proposal_post_all.csv')
    print("Proposal_post_all DB created successfully")
    
    empty_data = {}
    with open(config['data_dir'] + '/proposal_post_live.json', 'w') as json_file:
        json.dump(empty_data, json_file, indent=4)
        
    print("Proposal_post_live DB created successfully")

def store_into_live(coin, post_id, trade_id, description, buying_price, buying_time, stop_loss_price, trade_type, proposal_post_live):
    new_data = {
        "coin" : coin,
        "post_id": post_id,
        "description": description,
        "buying_price": buying_price,
        "buying_time": buying_time,
        "stop_loss_price": stop_loss_price,
        "type" : trade_type,
        "status" : "unsold"
        }
    
    proposal_post_live[trade_id] = new_data
    
    with open(config['data_dir'] + '/proposal_post_live.json', 'w') as json_file:
        json.dump(proposal_post_live, json_file, indent=4)

def trigger_trade(new_row_df, summary_obj, sentiment_analyzer):
    if len(new_row_df) != 0:
        proposal_post_all = pd.read_csv(config['data_dir'] + '/proposal_post_all.csv', index_col=0)
        proposal_post_id = pd.read_csv(config['data_dir'] + '/proposal_post_id.csv', index_col=0)
        
        with open(config['data_dir'] + '/proposal_post_live.json', 'r') as json_file:
            proposal_post_live = json.load(json_file)

        
        for index, row in new_row_df.iterrows():
            coin = row['coin']
            post_id = row['post_id']
            description = row['description']
            timestamp = row['timestamp']
            
            summary = summary_obj.summarize_text(row['description'])            
            sentiment, sentimnet_score = sentiment_analyzer.predict(summary)
            
            if sentiment == 'positive' and sentimnet_score >= 0.7:
                buying_price, stop_loss_price, trade_id = buy_call(coin)
                buying_time = format_time_utc()
                store_into_live(coin, post_id, trade_id, description, buying_price, buying_time, stop_loss_price, "call", proposal_post_live)        
 
            if sentiment == 'negative' and sentimnet_score >= 0.7:
                buying_price, stop_loss_price = buy_put(coin)
                buying_time = format_time_utc()
                store_into_live(coin, post_id, trade_id, description, buying_price, buying_time, stop_loss_price, "put", proposal_post_live)        

                
            new_row = {
                "post_id" :  post_id,
                "coin" : coin,
                "description": description,
                "summary" :  summary,
                "sentiment" :  sentiment,
                "sentiment_score" : sentimnet_score,
                }
            
            proposal_post_all = pd.concat([proposal_post_all, pd.DataFrame([new_row])], ignore_index=True) 
        
        proposal_post_all.to_csv(config['data_dir'] + '/proposal_post_all.csv')
        
        #store into proposal_post_id 
        new_row1 = {
            "post_id" : post_id
            }
        proposal_post_id = pd.concat([proposal_post_id, pd.DataFrame([new_row1])], ignore_index=True)
        proposal_post_id.to_csv(config['data_dir'] + '/proposal_post_id.csv')  

def close_firebase_client(app):
    firebase_admin.delete_app(app)
    print("Firebase client closed successfully.")

if __name__== "__main__":
    counter = 0
    db, app = create_firebase_client()
    store_data()
    summary_obj = Summarization("mistral")
    sentiment_analyzer = FinBERTSentiment()
    
    while True:
        proposal_dict = download_and_save_proposal(db)
        new_row_df = check_new_post(proposal_dict)
        trigger_trade(new_row_df, summary_obj, sentiment_analyzer)
        
        counter = counter + 1
        time.sleep(5*60)
     
    close_firebase_client(app)

        
