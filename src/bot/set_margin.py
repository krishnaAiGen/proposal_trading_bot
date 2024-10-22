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


# #Change margin type to ISOLATED before placing the order
# for key, symbol in coin_dict.items():
#     try:
#         client.futures_change_margin_type(symbol=symbol, marginType="ISOLATED")
#         print(f"Margin type set to ISOLATED for {symbol}.")
#     except Exception as e:
#         print(f"Error setting margin type: {e}, {symbol}")
        # post_error_to_slack(f"Error setting margin type for {symbol}: {e}")
        
def get_account_info():
    account_info = client.get_account()
    
    return account_info

def get_balance_future():
    balance = client.futures_account_balance()[4]['balance']
    
    return float(balance)

def get_current_price(symbol):
    ticker = client.get_symbol_ticker(symbol=symbol)
    
    return ticker['price']

def get_quantity(symbol):
    # balance = get_balance_future()
    balance = 13
    print("Balance is ", balance)
    print("Taking trade balance of :", balance)
        
    current_price = get_current_price(symbol)
    quantity = 0.95 * ((balance * 3) / float(current_price))
    print("quantity is ", quantity)
    # quantity = 0.9 * ((balance * 20) / float(current_price))

    coin_precision = precion_dict[symbol]    
    rounded_quantity = format(quantity, f".{coin_precision}f")   
    
    if float(rounded_quantity) > quantity:
        rounded_quantity = math.floor(quantity * 10) / 10

    return rounded_quantity

def create_buy_order_long(coin, target_price):
    #####-----------
    # coin = 'uniswap'
    # target_price = 0.02
    ####-------------
    
    
    symbol = coin_dict[coin]
    quantity = get_quantity(symbol)   
    print("Bought Quantity", quantity)

    # Optionally set the leverage, if needed
    result = client.futures_change_leverage(symbol=symbol, leverage=3)

    try:
        # result = client.futures_change_leverage(symbol=symbol, leverage = 5)1
        market_buy_order = client.futures_create_order(
           symbol = symbol,
           side = SIDE_BUY,
           type = ORDER_TYPE_MARKET,
           quantity = quantity
        )
        buying_price = get_current_price(symbol)

        print(f"Market long order placed successfully at price {buying_price}.")
        print("Order Details:", market_buy_order)
    except Exception as e:
        print(f"An error occurred: {e}")
        post_error_to_slack(f"An error occurred: {e}")
        print("Retrying to place the Market order...")
    
    buying_price = get_current_price(symbol)
    print(f"Bought {symbol} at price {buying_price}")
    
    #placing stop loss order
    stop_loss_percent = 2
    stopPrice = float(float(buying_price) - ((stop_loss_percent/100) * float(buying_price)))
    precision1 = get_precision1(buying_price)
    stopPrice = round(stopPrice, precision1)
    
    if market_buy_order:
        try:
            # Create a stop-loss order
            stop_loss_order = client.futures_create_order(
                symbol=symbol,
                side='SELL',
                type='STOP_MARKET',
                stopPrice=stopPrice,
                closePosition='true'
            )
            print("Stop-loss order placed successfully.")
            print("Order Details:", stop_loss_order)
        except Exception as e:
            print(f"An error occurred: {e}")
            post_error_to_slack(f"An error occurred: {e}")
            print("Retrying to place the stop-loss order...")
        
        stop_loss_orderID = stop_loss_order['orderId']
    
    if market_buy_order:
        target_profit_price = float(buying_price) + (abs(target_price) * float(buying_price))
        target_profit_price = round(target_profit_price, precision1)        
            

        # Create a limit order for target profit
        target_profit_order = client.futures_create_order(
            symbol=symbol,
            side='SELL',
            type='LIMIT',
            price=target_profit_price,
            quantity=quantity,  # Specify the quantity to sell
            timeInForce='GTC'  # Good Till Canceled
        )
        print("Target profit order placed successfully.")
        print("Order Details:", target_profit_order)
    
    target_order_id = target_profit_order['orderId']
    target_price = target_profit_order['price']
    
    return buying_price, market_buy_order['orderId'], stopPrice, stop_loss_orderID, target_order_id, target_price, quantity

if __name__ == "__main__":
    coin = 'aave'
    target_price = 160
    create_buy_order_long(coin, target_price)