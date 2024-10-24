#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 20:48:25 2024

@author: krishnayadav
"""

import json
import os
from binance.client import Client


with open('config.json', 'r') as json_file:
    config = json.load(json_file)

    
# Initialize the Binance client
client = Client(config['API_KEY'], config['API_SECRET'], tld='com')

# response = client.futures_cancel_order(
#             symbol='AAVEUSDT',
#             orderId = live_trade[first_key]['stop_loss_id']
#         )

# response = client.futures_cancel_order(
#             symbol='AAVEUSDT',
#             orderId= live_trade[first_key]['target_order_id']
#         )

# close_position_order = client.futures_create_order(
#     symbol='AAVEUSDT',
#     side='SELL',
#     type='MARKET',
#     quantity=0.3,  # Close entire long position
#     reduceOnly=True  # Ensure this only reduces the position and doesn't open a new one
# )

# response = client.futures_cancel_order(
#             symbol='AAVEUSDT',
#             orderId = 15039231629
#         )

# response = client.futures_cancel_order(
#             symbol='AAVEUSDT',
#             orderId= 15039231609
#         )

# close_position_order = client.futures_create_order(
#     symbol='AAVEUSDT',
#     side='SELL',
#     type='MARKET',
#     quantity=0.2,  # Close entire long position
#     reduceOnly=True  # Ensure this only reduces the position and doesn't open a new one
# )

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
    

print(open_positions)