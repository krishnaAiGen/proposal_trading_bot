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


temp = [{'symbol': 'ENAUSDT', 'positionAmt': '65457', 'entryPrice': '0.4281605481461', 'breakEvenPrice': '0.4283746284202', 'markPrice': '0.37870000', 'unRealizedProfit': '-3237.53856678', 'liquidationPrice': '0.24836096', 'leverage': '3', 'maxNotionalValue': '10000000', 'marginType': 'isolated', 'isolatedMargin': '8725.45720255', 'isAutoAddMargin': 'false', 'positionSide': 'BOTH', 'notional': '24788.56590000', 'isolatedWallet': '11962.99576933', 'updateTime': 1729728003429, 'isolated': True, 'adlQuantile': 1}, {'symbol': 'SCRUSDT', 'positionAmt': '55915', 'entryPrice': '0.9490900116249', 'breakEvenPrice': '0.9495645566308', 'markPrice': '0.94336613', 'unRealizedProfit': '-320.05075020', 'liquidationPrice': '0.53900980', 'leverage': '3', 'maxNotionalValue': '750000', 'marginType': 'isolated', 'isolatedMargin': '23138.05263128', 'isAutoAddMargin': 'false', 'positionSide': 'BOTH', 'notional': '52748.31715895', 'isolatedWallet': '23458.10338148', 'updateTime': 1729728003956, 'isolated': True, 'adlQuantile': 1}, {'symbol': 'ETHUSDT', 'positionAmt': '5.737', 'entryPrice': '2614.8', 'breakEvenPrice': '2616.1074', 'markPrice': '2546.86000000', 'unRealizedProfit': '-389.77178000', 'liquidationPrice': '1623.77551366', 'leverage': '3', 'maxNotionalValue': '530000000', 'marginType': 'isolated', 'isolatedMargin': '5332.99809864', 'isAutoAddMargin': 'false', 'positionSide': 'BOTH', 'notional': '14611.33582000', 'isolatedWallet': '5722.76987864', 'updateTime': 1729728000305, 'isolated': True, 'adlQuantile': 1}, {'symbol': 'SANDUSDT', 'positionAmt': '88176', 'entryPrice': '0.2861057884231', 'breakEvenPrice': '0.2862488413174', 'markPrice': '0.26623989', 'unRealizedProfit': '-1751.69471664', 'liquidationPrice': '0.16367522', 'leverage': '3', 'maxNotionalValue': '5000000', 'marginType': 'isolated', 'isolatedMargin': '9139.76796231', 'isAutoAddMargin': 'false', 'positionSide': 'BOTH', 'notional': '23475.96854064', 'isolatedWallet': '10891.46267895', 'updateTime': 1729728001602, 'isolated': True, 'adlQuantile': 2}, {'symbol': 'NEARUSDT', 'positionAmt': '11309', 'entryPrice': '4.504999381024', 'breakEvenPrice': '4.507251880711', 'markPrice': '4.67700000', 'unRealizedProfit': '1945.15501158', 'liquidationPrice': '3.06019672', 'leverage': '3', 'maxNotionalValue': '12500000', 'marginType': 'isolated', 'isolatedMargin': '18753.54473956', 'isAutoAddMargin': 'false', 'positionSide': 'BOTH', 'notional': '52892.19300000', 'isolatedWallet': '16808.38972798', 'updateTime': 1729728001405, 'isolated': True, 'adlQuantile': 3}]

