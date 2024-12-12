#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 20:48:25 2024

@author: krishnayadav
"""

import json
import os
from binance.client import Client

"""
This code manually stops trade without API endpoint
"""

with open('config.json', 'r') as json_file:
    config = json.load(json_file)

# Initialize the Binance client
client = Client(config['API_KEY'], config['API_SECRET'], tld='com')

response = client.futures_cancel_order(
            symbol='CAKEUSDT',
            orderId = 1593383729
        )

print("Stop loss sucess")

response = client.futures_cancel_order(
            symbol='CAKEUSDT',
            orderId= 1593383740
        )

print("Target sucess")


close_position_order = client.futures_create_order(
    symbol='CAKEUSDT',
    side='SELL',
    type='MARKET',
    quantity=7686,  # Close entire long position
    reduceOnly=True  # Ensure this only reduces the position and doesn't open a new one
)

print("All quantity sucess")


    






