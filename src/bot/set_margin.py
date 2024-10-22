#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 18:05:16 2024

@author: krishnayadav
"""

from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
from binance.enums import *
import json
import os
from slack_bot import post_error_to_slack


with open('config.json', 'r') as json_file:
    config = json.load(json_file)
    
with open('coin.json', 'r') as json_file:
    coin_dict = json.load(json_file)

with open('precision.json', 'r') as json_file:
    precion_dict = json.load(json_file)
    
# Initialize the Binance client
client = Client(config['API_KEY'], config['API_SECRET'], tld='com')


#Change margin type to ISOLATED before placing the order
for key, symbol in coin_dict.items():
    try:
        client.futures_change_margin_type(symbol=symbol, marginType="ISOLATED")
        print(f"Margin type set to ISOLATED for {symbol}.")
    except Exception as e:
        print(f"Error setting margin type: {e}, {symbol}")
        # post_error_to_slack(f"Error setting margin type for {symbol}: {e}")