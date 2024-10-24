#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 14:16:33 2024

@author: krishnayadav
"""


import json
import os
from binance.client import Client


with open('config.json', 'r') as json_file:
    config = json.load(json_file)
    
# Initialize the Binance client
client = Client(config['API_KEY'], config['API_SECRET'], tld='com')

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