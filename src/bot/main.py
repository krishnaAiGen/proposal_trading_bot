import numpy as np
import pandas as pd
from scan_proposal import *
import time
import json
from datetime import datetime
from summarize import Summarization
from sell import format_time_utc
from binance_api import * 
from slack_bot import *
from bullish_price import RobertaForRegressionBullish
from bearish_price import RobertaForRegressionBearish
from text_verification import classify_text
from clean_html import remove_html_tags
from btc_check import btc_price_check
from save_trades import Save


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
    proposal_dict = download_and_save_proposal(db, False)
    start_time = store_into_db(proposal_dict)
    print("Key DB created successfully")
    
    proposal_post_all = pd.DataFrame(columns = ["timestamp", "post_id", "coin", "description", "summary", "sentiment", "sentiment_score", "text_verify"])    
    proposal_post_all.to_csv(config['data_dir'] + '/proposal_post_all.csv')
    print("Proposal_post_all DB created successfully")
    
    empty_data = {}
    with open(config['data_dir'] + '/proposal_post_live.json', 'w') as json_file:
        json.dump(empty_data, json_file, indent=4)
        
    print("Proposal_post_live DB created successfully")
    
    price_check_file_path = config['data_dir'] + '/price_check.json'
    if not os.path.exists(price_check_file_path):
        data = []
        # Create new file with empty list
        with open(price_check_file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    print("price_check_json created into DB")
    
    

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

def send_new_post_slack(coin, post_id, discussion_link, sentiment, sentimnet_score, target_price, summary):
    if discussion_link == '' or discussion_link is None:
        discussion_link = summary
        
    message = {
        "discussion_link" : discussion_link,
        "coin" : coin,
        "post_id" : post_id,
        "sentiment" : sentiment,
        "sentiment_score" : sentimnet_score,
        "target_percent" : target_price
        }
    
    # post_to_slack(str(message))
    post_to_slack(message)
    print("Posted to slack", message)

def send_trade_info_slack(coin, trade_type, buying_price, stop_loss_price, targetPrice, trade_id, stop_loss_orderID, target_orderId, quantity):
    message = {
        "coin" : coin,
        "trade_type": trade_type,
        "buying_price" : buying_price,
        "stop_loss_price" : stop_loss_price,
        "target_price" : targetPrice,
        "trade_id": trade_id,
        "stop_loss_orderID": stop_loss_orderID,
        "target_orderId" : target_orderId,
        "quantity" : quantity
        }
    
    # post_to_slack(str(message))
    post_to_slack(message)
    print("Posted to slack", message)

def predict_final_sentiment(sentiment, sentimnet_score, sentiment_crypto, crypto_score):
    if sentiment != sentiment_crypto:
        return sentiment, sentimnet_score
    
    else:
        sentimnet_score = (sentimnet_score + crypto_score) / 2
        return sentiment, sentimnet_score
    

def trigger_trade(new_row_df, summary_obj, sentiment_analyzer, reasoning, dynamo):    
    if len(new_row_df) != 0 and not btc_price_check():
    # if len(new_row_df) != 0:
        proposal_post_all = pd.read_csv(config['data_dir'] + '/proposal_post_all.csv', index_col=0)
        proposal_post_id = pd.read_csv(config['data_dir'] + '/proposal_post_id.csv', index_col=0)
        
        with open(config['data_dir'] + '/proposal_post_live.json', 'r') as json_file:
            proposal_post_live = json.load(json_file)
        
        live_post_ids = []
        for key, live_trade in proposal_post_live.items():
            live_post_ids.append(proposal_post_live[key]['post_id'])


        for index, row in new_row_df.iterrows():
            coin = row['coin']
            post_id = row['post_id']
            post_error_to_slack(str(post_id))
            description = row['description']
            description = clean_content(description)
            timestamp = row['timestamp']
            discussion_link = row['discussion_link']
            
            text_verify = classify_text(description)
            summary = summary_obj.summarize_text(description)
            sentiment, sentimnet_score = sentiment_analyzer.predict(summary)
            
            #calculating deepseek and openAI sentiment
            sentiment, sentimnet_score = reasoning.predict_sentiment(summary, sentimnet_score)
                        
            """
            Saving into DB
            """
            new_row = {
                "post_id" :  post_id,
                "coin" : coin,
                "description": description,
                "summary" :  summary,
                "sentiment" :  sentiment,
                "sentiment_score" : sentimnet_score,
                "text_verify" : text_verify
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
                        
            """
            taking trade from here
            """
            if sentiment == 'positive' and sentimnet_score >= 0.80 and text_verify == 'genuine': 
                #making an object for bullish and bearish price prediction
                bullish_predictor = RobertaForRegressionBullish(config['bullish_dir'])
                target_price = bullish_predictor.predict(summary)[0]
                
                if post_id not in live_post_ids:
                    send_new_post_slack(coin, post_id, discussion_link, sentiment, sentimnet_score, target_price, summary)
                
                check_status = check_trade_limit(coin)
                if check_status == True:
                    buying_price, trade_id, stop_loss_price, stop_loss_orderID, target_orderId, targetPrice, quantity = create_buy_order_long(coin, target_price/100)   #divide by 100 because target profit is in number ex 5 bringing it to 0.05
                    buying_time = format_time_utc()
                    print("---------------TRADE BOUGHT---------------------")
                    
                    store_into_live(coin, post_id, trade_id, description, buying_price, buying_time, stop_loss_price, "long", stop_loss_orderID, proposal_post_live, target_orderId, targetPrice)        
                    send_trade_info_slack(coin, "Long", buying_price, stop_loss_price, targetPrice, trade_id, stop_loss_orderID, target_orderId, quantity)
                    
                    #saving info to dynamoDB
                    try:
                        save_object = Save(dynamo, 'trade_table')
                        save_object.save_to_dynamo(coin, description, sentimnet_score, post_id)
                        print("--saved to dynamoDB--")
                    except Exception as e:
                        print(f"Error saving to DynamoDB: {e}")
                        post_error_to_slack(f"Error saving to DynamoDB: {e}")
                        print("Continuing with remaining operations...")
                    
            if sentiment == 'negative' and sentimnet_score >= 0.80 and text_verify == 'genuine':
                #making an object for bullish and bearish price prediction
                bearish_predictor = RobertaForRegressionBearish(model_path = config['bearish_dir'])
                target_price = bearish_predictor.predict(summary)[0]
                
                if post_id not in live_post_ids:
                    send_new_post_slack(coin, post_id, description, sentiment, sentimnet_score, target_price, summary)

                
                check_status = check_trade_limit(coin)
                if check_status == True:
                    buying_price, trade_id, stop_loss_price, stop_loss_orderID, target_orderId, targetPrice, quantity = create_buy_order_short(coin, target_price/100) #divide by 100 because target profit is in number ex 5 bringing it to 0.05
                    buying_time = format_time_utc()
                    print("---------------TRADE BOUGHT---------------------")
                    
                    store_into_live(coin, post_id, trade_id, description, buying_price, buying_time, stop_loss_price, "short", stop_loss_orderID, proposal_post_live, target_orderId, targetPrice)        
                    send_trade_info_slack(coin, "Short", buying_price, stop_loss_price, targetPrice, trade_id, stop_loss_orderID, target_orderId, quantity)
                    
                    #saving info to dynamoDB
                    try:
                        save_object = Save(dynamo, 'trade_table')
                        save_object.save_to_dynamo(coin, description, sentimnet_score, post_id)
                        print("--saved to dynamoDB--")
                    except Exception as e:
                        print(f"Error saving to DynamoDB: {e}")
                        post_error_to_slack(f"Error saving to DynamoDB: {e}")
                        print("Continuing with remaining operations...")

def close_firebase_client(app):
    firebase_admin.delete_app(app)
    print("Firebase client closed successfully.")




        
