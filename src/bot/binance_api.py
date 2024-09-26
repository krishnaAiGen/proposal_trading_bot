from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
from binance.enums import *
import json
import os

with open('config.json', 'r') as json_file:
    config = json.load(json_file)
    
with open('coin.json', 'r') as json_file:
    coin_dict = json.load(json_file)

with open('precision.json', 'r') as json_file:
    precion_dict = json.load(json_file)
    
# Initialize the Binance client
client = Client(config['API_KEY'], config['API_SECRET'], tld='com')

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
    balance = get_balance_future() / 4
    # balance = get_balance_future()

        
    current_price = get_current_price(symbol)
    quantity = 0.9 * ((balance * 3) / float(current_price))
    # quantity = 0.9 * ((balance * 20) / float(current_price))

    coin_precision = precion_dict[symbol]

    
    return format(quantity, f".{coin_precision}f")

def update_stop_loss(trade_type, symbol, previous_stop_loss_orderId):
    buying_price = get_current_price(symbol)
    
    #cancel the previous_stop_loss_order
    try:
        result = client.futures_cancel_order(symbol=symbol, orderId=previous_stop_loss_orderId)
        print("Stop loss order canceled successfully.")
    except Exception as e:
        print("Failed cancelling stop loss", e)
        
    
    
    #placing stop loss order
    stop_loss_percent = 2
    if trade_type == 'long':
        stopPrice = float(float(buying_price) - ((stop_loss_percent/100) * float(buying_price)))
        
        if stopPrice < 10:
            stopPrice = "{:.2f}".format(stopPrice)
        
        elif stopPrice < 50:
            stopPrice = "{:.1f}".format(stopPrice)
        
        else:
            stopPrice = int(stopPrice)
        
        
        try:
            # Create a stop-loss order
            stop_loss_order = client.futures_create_order(
                symbol=symbol,
                side='SELL',
                type='STOP_MARKET',
                stopPrice=stopPrice,
                closePosition='true'
            )
            print(f"Stop-loss order updated successfully to {stopPrice}.")
            print("Order Details:", stop_loss_order)
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Retrying to place the stop-loss order...")
    
    if trade_type == 'short':
        stopPrice = int(float(buying_price) + ((stop_loss_percent/100) * float(buying_price)))
        
        try:
            # Create a stop-loss order
            stop_loss_order = client.futures_create_order(
                symbol=symbol,
                side='BUY',
                type='STOP_MARKET',
                stopPrice=stopPrice,
                closePosition='true'
            )
            print(f"Stop-loss order updated successfully to {stopPrice}.")
            print("Order Details:", stop_loss_order)
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Retrying to place the stop-loss order...")

    
    return stop_loss_order['orderId'], stopPrice

def create_buy_order_long(coin):
    symbol = coin_dict[coin]
    quantity = get_quantity(symbol)    

    try:
        # result = client.futures_change_leverage(symbol=symbol, leverage = 5)
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
        print("Retrying to place the Market order...")
    
    buying_price = get_current_price(symbol)
    print(f"Bought {symbol} at price {buying_price}")
    
    #placing stop loss order
    stop_loss_percent = 2
    stopPrice = int(float(buying_price) - ((stop_loss_percent/100) * float(buying_price)))
    
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
            print("Retrying to place the stop-loss order...")
        
        stop_loss_orderID = stop_loss_order['orderId']
    
    return buying_price, market_buy_order['orderId'], stopPrice, stop_loss_orderID



def create_buy_order_short(coin):
    # coin = 'btc'
    symbol = coin_dict[coin]
    quantity = get_quantity(symbol)
    
    try:
        # Create a stop-loss order
        # result = client.futures_change_leverage(symbol=symbol, leverage = 5)
        market_buy_order = client.futures_create_order(
           symbol = symbol,
           side = SIDE_SELL,
           type = ORDER_TYPE_MARKET,
           quantity = quantity
        )
        buying_price = get_current_price(symbol)

        print(f"Market short order placed successfully at price {buying_price}.")
        print("Order Details:", market_buy_order)
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Retrying to place the Market order...")
    
    buying_price = get_current_price(symbol)
    print(f"Bought {symbol} at price {buying_price}")
    
    #placing stop loss order
    stop_loss_percent = 2
    stopPrice = int(float(buying_price) + ((stop_loss_percent/100) * float(buying_price)))
    
    if market_buy_order:
        try:
            # Create a stop-loss order
            stop_loss_order = client.futures_create_order(
                symbol=symbol,
                side='BUY',
                type='STOP_MARKET',
                stopPrice=stopPrice,
                closePosition='true'
            )
            print("Stop-loss order placed successfully.")
            print("Order Details:", stop_loss_order)
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Retrying to place the stop-loss order...")
        
        stop_loss_orderID = stop_loss_order['orderId']
    
    return buying_price, market_buy_order['orderId'], stopPrice, stop_loss_orderID

def check_order_status(symbol, order_id):
    try:
        open_orders_list = client.futures_get_open_orders()
        for open_order in open_orders_list:
            if open_order['symbol'] == symbol and open_order['orderId'] == order_id:
                return 'filled'
        
        return 'notFilled'
    except Exception as e:
        print(f"An error occurred while detetcting status: {e}")
        return None   

# if __name__ == "__main__":
    # buying_price, trade_id, stop_loss_price, stop_loss_orderID = create_buy_order_long('uniswap')
    # updated_stop_lossID = update_stop_loss('long', 'UNIUSDT', stop_loss_orderID)
    
    # buying_price, stop_loss_price, trade_id, stop_loss_orderID = create_buy_order_short('btc')
    # updated_stop_lossID = update_stop_loss('short', 'BTCUSDT', stop_loss_orderID)
    
    # print(check_order_status('UNIUSDT', 22))

   
    


    