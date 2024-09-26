import time
from datetime import datetime, time as dt_time
import pytz
import requests
import json
from binance_api import * 

with open('config.json', 'r') as json_file:
    config = json.load(json_file)
    
with open('coin.json', 'r') as json_file:
    coin_dict = json.load(json_file)

def format_time_utc():
    current_time_utc = datetime.now(pytz.utc)
    formatted_time = current_time_utc.strftime('%Y-%m-%d %H:%M:%S%z')
    
    return formatted_time

def fetch_currrent_price(coin_name):
    symbol = coin_dict.get(coin_name)
    if not symbol:
        print(f"Symbol for {coin_name} not found in coin_dict")
        return None
    
    try:
            utc_time = format_time_utc()
            json_dict = {'close': float(get_current_price(symbol)), 'timestamp': utc_time}
            return json_dict
    
    except Exception as e:
        print(f"Error fetching current price data for {symbol}: {e}")
        return None
    
def load_live_trade_db():
    with open(config['data_dir'] + '/proposal_post_live.json', 'r') as json_file:
        proposal_post_live = json.load(json_file)
        
    return proposal_post_live

def remove_from_live_db(proposal_post_live, key):
    if key in proposal_post_live:
        del proposal_post_live[key]
    
    else:
        print("key not found in db while deleting from live db")
    
    return proposal_post_live
    
def dump_live_trade_db(proposal_post_live):
    with open(config['data_dir'] + '/proposal_post_live.json', 'w') as json_file:
        json.dump(proposal_post_live, json_file, indent=4)    
    

def update_or_sell():
    try:
        proposal_post_live = load_live_trade_db()
    except Exception as e:
        print("error in loading live DB", proposal_post_live)
    
    for key, values in proposal_post_live.items():
        coin_name = proposal_post_live[key]["coin"]
        response = fetch_currrent_price(coin_name)
        current_price = response['close']
        current_time = response['timestamp']
        symbol = coin_dict[coin_name]
        
        if proposal_post_live[key]["type"] == "long":
            #checking whether that stop loss order exists or not
            stop_loss_id = proposal_post_live[key]["stop_loss_id"]
            status = check_order_status(symbol, stop_loss_id)
            if status == "notFilled":
                #deleting from live db if that trade has already hit stop loss and no more live
                proposal_post_live = remove_from_live_db(proposal_post_live, key)
                continue
            
            if current_price > float(proposal_post_live[key]["buying_price"]):
                updated_stop_lossId, stopPrice = update_stop_loss("long", symbol, stop_loss_id)
                
                #updating in the DB
                proposal_post_live[key]["stop_loss_price"] = stopPrice
                proposal_post_live[key]["stop_loss_id"] = updated_stop_lossId
                
                dump_live_trade_db(proposal_post_live)
        
        if proposal_post_live[key]["type"] == "short":
            stop_loss_id = proposal_post_live[key]["stop_loss_id"]
            status = check_order_status(symbol, stop_loss_id)
            if status == "notFilled":
                #deleting from live db if that trade has already hit stop loss and no more live
                proposal_post_live = remove_from_live_db(proposal_post_live, key)
                continue
            
            if current_price < float(proposal_post_live[key]["buying_price"]):
                updated_stop_lossId, stopPrice = update_stop_loss("short", symbol, stop_loss_id)
                
                #updating in the DB
                proposal_post_live[key]["stop_loss_price"] = stopPrice
                proposal_post_live[key]["stop_loss_id"] = updated_stop_lossId
                
                dump_live_trade_db(proposal_post_live)
            


# if __name__ == "__main__":
#     while True:
#         update_or_sell()
#         time.sleep(60*60)

                    
            

        

        
        
        
