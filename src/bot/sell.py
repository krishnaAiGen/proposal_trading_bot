import time
from datetime import datetime, time as dt_time
import pytz
import requests
import json

with open('config.json', 'r') as json_file:
    config = json.load(json_file)

coin_dict = {
        'astar': 'ASTRUSDT',
        '0xprotocol': 'ZRXUSDT',
        'uniswap': 'UNIUSDT',
        'venus': 'XVSUSDT',
        'badger': 'BADGERUSDT',
        'apecoin': 'APEUSDT',
        'aragon': 'ANTUSDT',
        'pankcakeswap': 'CAKEUSDT',
        'curve': 'CRVUSDT',
        'makerdao': 'MKRUSDT',
        'balancer': 'BALUSDT',
        'aave': 'AAVEUSDT',
        'compound': 'COMPUSDT',
        'btc' : 'BTCUSDT'
    }

def format_time_utc():
    current_time_utc = datetime.now(pytz.utc)
    formatted_time = current_time_utc.strftime('%Y-%m-%d %H:%M:%S%z')
    
    return formatted_time

def fetch_currrent_price(coin_name, coin_dict):
    symbol = coin_dict.get(coin_name)
    if not symbol:
        print(f"Symbol for {coin_name} not found in coin_dict")
        return None
    
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url)
        current_price = response.json().get('price')
        
        if current_price:
            utc_time = format_time_utc()
            json_dict = {'close': float(current_price), 'timestamp': utc_time}
            return json_dict
    
    except Exception as e:
        print(f"Error fetching current price data for {symbol}: {e}")
        return None
    

def load_live_trade_db():
    with open(config['data_dir'] + 'proposal_post_live.json', 'r') as json_file:
        proposal_post_live = json.load(json_file)
        
    return proposal_post_live

def remove_from_live_db(proposal_post_live, key):
    if key in proposal_post_live:
        del proposal_post_live[key]
    
    else:
        print("key not found in db while deleting from live db")
    
def dump_live_trade_db(proposal_post_live):
    with open(config['data_dir'] + 'proposal_post_live.json', 'w') as json_file:
        json.dump(proposal_post_live, json_file, indent=4)    
    

def update_or_sell(stop_loss = 2):
    proposal_post_live = load_live_trade_db
    
    #temp 
    # proposal_post_live = {
    #             "1": {
    #                 "coin": "btc",
    #                 "post_id": "12345",
    #                 "description": "Bitcoin purchase based on technical analysis",
    #                 "buying_price": 45000,
    #                 "buying_time": "2024-09-20T12:00:00",
    #                 "stop_loss_price": 44000,
    #                 "trade_type": "call",
    #                 "status": "unsold"
    #             },
    #             "2": {
    #                 "coin": "astar",
    #                 "post_id": "12346",
    #                 "description": "Ethereum purchase based on forum sentiment",
    #                 "buying_price": 1600,
    #                 "buying_time": "2024-09-20T13:00:00",
    #                 "stop_loss_price": 1550,
    #                 "trade_type": "put",
    #                 "status": "unsold"
    #             }
    #         }
    
    for key, values in proposal_post_live.items():
        
        # key = "1"
        
        coin_name = proposal_post_live[key]["coin"]
        response = fetch_currrent_price(coin_name)
        current_price = response['close']
        current_time = response['timestamp']
        
        if proposal_post_live[key]["trade_type"] == "call":
            if current_price > proposal_post_live[key]["buying_price"]:
                new_stop_loss = current_price - (stop_loss/100) * current_price
                # status = update_stop_loss(key, new_stop_loss)           #get this API from mridul
                # if status == 200:
                proposal_post_live[key]["buying_price"] = current_price
                proposal_post_live[key]["buying_time"] = current_time
                proposal_post_live[key]["stop_loss_price"] = new_stop_loss
            
            if current_price < proposal_post_live[key]["stop_loss_price"]:
                status = sell_order(key)                #get this API from mridul
                if status == 200:
                    remove_from_live_db(proposal_post_live, key)
                    dump_live_trade_db(proposal_post_live)
        

                    
            

        

        
        
        
