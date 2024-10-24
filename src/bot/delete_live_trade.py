#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 13:16:26 2024

@author: krishnayadav
"""
import json
from binance.client import Client
from slack_bot import post_error_to_slack

def delete_live_trade(client):  
    with open('config.json', 'r') as json_file:
        config = json.load(json_file)

    with open(config['data_dir'] + '/proposal_post_live.json', 'r') as json_file:
        proposal_post_live = json.load(json_file)
        
    with open('coin.json', 'r') as json_file:
        coin_symbol = json.load(json_file)
    
    live_coin_symbol = {}
    for key, value in proposal_post_live.items():
        live_coin_symbol[key] = coin_symbol[proposal_post_live[key]['coin']]
    
    positions = client.futures_position_information()
    
    # Filter for only open positions
    open_coin = []
    open_positions = [pos for pos in positions if float(pos['positionAmt']) != 0]
    for position_dict in open_positions:
        open_coin.append(position_dict['symbol'])
        
    for trade_id, symbol in live_coin_symbol.items():
        if symbol not in open_coin:
            del proposal_post_live[trade_id]
            print(f"{symbol} was deleted from proposal post live")
            sell_string = f"{symbol} WAS SOLD"
            post_error_to_slack(sell_string)
            
            with open(config['data_dir'] + '/proposal_post_live.json', 'w') as json_file:
                json.dump(proposal_post_live, json_file, indent=4)
        
        else:
            print("No trade was deleted from proposal post live")
    





   