#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 12:03:35 2024

@author: krishnayadav
"""

from flask import Flask, request, jsonify
import json
from binance.client import Client

# Initialize Flask app
app = Flask(__name__)

# Load configuration
with open('config.json', 'r') as json_file:
    config = json.load(json_file)

client = Client(config['API_KEY'], config['API_SECRET'], tld='com')

# Load proposal and coin data
with open(config['data_dir'] + '/proposal_post_live.json', 'r') as json_file:
    proposal_post_live = json.load(json_file)

with open('coin.json', 'r') as json_file:
    coin_symbol = json.load(json_file)


@app.route('/stop_trade', methods=['POST'])
def stop_trade():
    """
    Endpoint to cancel orders and close a position.
    """
    try:
        # Parse input data
        data = request.json
        symbol = coin_symbol[data.get('symbol')]
        quantity = data.get('quantity')
        stop_orderid = data.get('stop_orderid')
        target_orderid = data.get("target_orderid")
        
        # Cancel stop loss order
        response_sl = client.futures_cancel_order(symbol=symbol, orderId=stop_orderid)
        print("Stop loss successfully cancelled")

        # Cancel target order
        response_target = client.futures_cancel_order(symbol=symbol, orderId=target_orderid)
        print("Target order successfully cancelled")

        if data.get('type') == 'long':
            print("long position was cancelled")
            # Close the position
            close_position_order = client.futures_create_order(
                symbol=symbol,
                side= "SELL",
                type='MARKET',
                quantity=quantity,  # Close entire position
                reduceOnly=True  # Ensure this only reduces the position
            )
        else:
            print("short position was cancelled")
            close_position_order = client.futures_create_order(
                symbol=symbol,
                side= "BUY",
                type='MARKET',
                quantity=quantity,  # Close entire position
            )

        print("All quantity successfully sold")

        # Return a success response
        return jsonify({
            "message": "Trade successfully stopped.",
            "details": {
                "stop_loss_cancelled": response_sl,
                "target_cancelled": response_target,
                "close_position": close_position_order
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/open_positions', methods=['GET'])
def get_open_positions():
    """
    Endpoint to fetch open positions.
    """
    try:
        # Map live coins to their symbols
        live_coin_symbol = {}
        for key, value in proposal_post_live.items():
            live_coin_symbol[key] = coin_symbol[proposal_post_live[key]['coin']]

        # Fetch positions from Binance
        positions = client.futures_position_information()

        # Filter for open positions
        open_positions = [pos for pos in positions if float(pos['positionAmt']) != 0]
        open_coin = [position['symbol'] for position in open_positions]

        # Return the filtered positions
        return jsonify({
            "message": "Open positions fetched successfully.",
            "open_positions": open_positions,
            "open_coin_symbols": open_coin
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7111)
