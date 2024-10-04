import numpy as np
import pandas as pd
from scan_proposal import *
import time
import json
from datetime import datetime
from summarize import Summarization
from sentiment import FinBERTSentiment
from sentiment_crypto import CryptoSentimentAnalyzer
from sell import format_time_utc
from binance_api import * 
from slack_bot import post_to_slack
from bullish_price import BullishSentimentPredictor
from bearish_price import BearishSentimentPredictor


price_dict = {
  "verySmall": 0.20,  # (0.15 + 0.25) / 2
  "small": 0.325,     # (0.25 + 0.40) / 2
  "medium": 0.50,     # (0.40 + 0.60) / 2
  "high": 0.80,       # (0.60 + 1) / 2
  "nn": 0             # Default to 0 for 'nn'
}
    
    

with open('config.json', 'r') as json_file:
    config = json.load(json_file)

def store_data(db):
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

def store_into_live(coin, post_id, trade_id, description, buying_price, buying_time, stop_loss_price, trade_type, stop_loss_orderID, proposal_post_live, target_orderId, targetPrice):
    new_data = {
        "coin" : coin,
        "post_id": post_id,
        "description": description,
        "buying_price": buying_price,
        "buying_time": buying_time,
        "stop_loss_price": stop_loss_price,
        "type" : trade_type,
        "stop_loss_id" : stop_loss_orderID,
        "target_order_id" : target_orderId,
        "target_price" : targetPrice,
        "status" : "unsold"
        }
    
    proposal_post_live[trade_id] = new_data
    
    with open(config['data_dir'] + '/proposal_post_live.json', 'w') as json_file:
        json.dump(proposal_post_live, json_file, indent=4)
    
def check_trade_limit(coin):
    """
    This function first checks whether there is already existing trade of incoming coin 
    and the total number of trade is less than 4 or not.
    """
    with open(config['data_dir'] + '/proposal_post_live.json', 'r') as json_file:
        proposal_post_live = json.load(json_file)
    
    if len(proposal_post_live) >=4:
        return False
    
    if len(proposal_post_live) == 0:
        return True
   
    for key, value in proposal_post_live.items():
        if proposal_post_live[key]['coin'] == coin:
            return False
        else:
            return True

def send_new_post_slack(coin, post_id, description, sentiment, sentimnet_score, target_price):
    message = {
        "description" : description,
        "coin" : coin,
        "post_id" : post_id,
        "sentiment" : sentiment,
        "sentiment_score" : sentimnet_score,
        "target_percent" : target_price
        }
    
    post_to_slack(str(message))
    print("Posted to slack", message)

def send_trade_info_slack(coin, trade_type, buying_price, stop_loss_price, targetPrice):
    message = {
        "coin" : coin,
        "trade_type": trade_type,
        "buying_price" : buying_price,
        "stop_loss_price" : stop_loss_price,
        "target_price" : targetPrice
        }
    
    post_to_slack(str(message))
    print("Posted to slack", message)

def predict_final_sentiment(sentiment, sentimnet_score, sentiment_crypto, crypto_score):
    if sentiment != sentiment_crypto:
        return sentiment, sentimnet_score
    
    else:
        sentimnet_score = (sentimnet_score + crypto_score) / 2
        return sentiment, sentimnet_score
    

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
            
            # sentiment_analyzer = FinBERTSentiment()
            # summary = summ_text
            # print(summary)
            
            sentiment, sentimnet_score = sentiment_analyzer.predict(summary)
            analyzer = CryptoSentimentAnalyzer()  
            sentiment_crypto, crypto_score = analyzer.analyze_sentiment(summary)
            sentiment, sentimnet_score = predict_final_sentiment(sentiment, sentimnet_score, sentiment_crypto, crypto_score)
            
            if sentiment == 'positive' and sentimnet_score >= 0.75: 
                #making an object for bullish and bearish price prediction
                bullish_predictor = BullishSentimentPredictor(config['bullish_dir'], {0: 'high', 1: 'medium', 2: 'small', 3: 'verySmall'})
                target_price = price_dict[bullish_predictor.predict(summary)['predicted_label']]
                
                send_new_post_slack(coin, post_id, description, sentiment, sentimnet_score, target_price)
                
                check_status = check_trade_limit(coin)
                if check_status == True:
                    buying_price, trade_id, stop_loss_price, stop_loss_orderID, target_orderId, targetPrice = create_buy_order_long(coin, target_price)
                    buying_time = format_time_utc()
                    print("---------------TRADE BOUGHT---------------------")
                    
                    store_into_live(coin, post_id, trade_id, description, buying_price, buying_time, stop_loss_price, "long", stop_loss_orderID, proposal_post_live, target_orderId, targetPrice)        
                    send_trade_info_slack(coin, "Long", buying_price, stop_loss_price, targetPrice)
                    
            if sentiment == 'negative' and sentimnet_score >= 0.75:
                #making an object for bullish and bearish price prediction
                bearish_predictor = BearishSentimentPredictor(config['bearish_dir'], {0: 'high', 1: 'medium', 2: 'small', 3: 'verySmall'})
                target_price = price_dict[bearish_predictor.predict(summary)['predicted_label']]
                
                send_new_post_slack(coin, post_id, description, sentiment, sentimnet_score, target_price)

                
                check_status = check_trade_limit(coin)
                if check_status == True:
                    buying_price, trade_id, stop_loss_price, stop_loss_orderID, target_orderId, targetPrice = create_buy_order_short(coin, target_price)
                    buying_time = format_time_utc()
                    print("---------------TRADE BOUGHT---------------------")
                    
                    store_into_live(coin, post_id, trade_id, description, buying_price, buying_time, stop_loss_price, "short", stop_loss_orderID, proposal_post_live, target_orderId, targetPrice)        
                    send_trade_info_slack(coin, "Short", buying_price, stop_loss_price, targetPrice)

                
            new_row = {
                "post_id" :  post_id,
                "coin" : coin,
                "description": description,
                "summary" :  summary,
                "sentiment" :  sentiment,
                "sentiment_score" : sentimnet_score,
                }
            if post_id not in list(proposal_post_all['post_id']):
                proposal_post_all = pd.concat([proposal_post_all, pd.DataFrame([new_row])], ignore_index=True) 
        
        proposal_post_all.to_csv(config['data_dir'] + '/proposal_post_all.csv')
        
        #store into proposal_post_id 
        new_row1 = {
            "post_id" : post_id
            }
        if post_id not in list(proposal_post_id['post_id']):
            proposal_post_id = pd.concat([proposal_post_id, pd.DataFrame([new_row1])], ignore_index=True)
        
        proposal_post_id.to_csv(config['data_dir'] + '/proposal_post_id.csv')  
        

def close_firebase_client(app):
    firebase_admin.delete_app(app)
    print("Firebase client closed successfully.")



        
