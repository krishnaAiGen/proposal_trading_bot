import requests
from datetime import datetime, timedelta
import time
import hmac
import hashlib
from urllib.parse import urlencode
import json

class BinanceClient:
    def __init__(self, api_key, api_secret):
        self.API_KEY = api_key
        self.API_SECRET = api_secret
        self.BASE_URL = 'https://api.binance.com'

    def _generate_signature(self, params):
        query_string = urlencode(params)
        return hmac.new(
            self.API_SECRET.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def get_klines(self, symbol, interval, limit, start_time=None):
        endpoint = '/api/v3/klines'
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        if start_time:
            params['startTime'] = start_time

        headers = {'X-MBX-APIKEY': self.API_KEY}
        response = requests.get(
            self.BASE_URL + endpoint,
            params=params,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

def check_btc_price_drop(api_key, api_secret):
    """
    Check if BTC price has dropped by 2.5% or more in the last 12 or 24 hours
    using Binance API
    """
    client = BinanceClient(api_key, api_secret)
    
    try:
        # Get current time
        now = int(time.time() * 1000)
        
        # Get klines (candlestick data)
        # Fetch last 25 hours of hourly data to ensure we have enough data
        klines = client.get_klines(
            symbol='BTCUSDT',
            interval='1h',
            limit=25
        )
        
        # Extract prices
        current_price = float(klines[-1][4])  # Current closing price
        
        # Find 12h and 24h prices
        twelve_hours_ago_price = float(klines[-12][4])  # 12 hours ago closing price
        twenty_four_hours_ago_price = float(klines[-24][4])  # 24 hours ago closing price
        
        # Calculate drops
        twelve_hr_drop = ((twelve_hours_ago_price - current_price) / twelve_hours_ago_price) * 100
        twenty_four_hr_drop = ((twenty_four_hours_ago_price - current_price) / twenty_four_hours_ago_price) * 100
        
        
        return {
            'current_price': current_price,
            '12h_ago_price': twelve_hours_ago_price,
            '24h_ago_price': twenty_four_hours_ago_price,
            '12h_drop': twelve_hr_drop,
            '24h_drop': twenty_four_hr_drop,
            'has_significant_drop': (twelve_hr_drop >= 2.5 or twenty_four_hr_drop >= 2.5),
            'timestamp': datetime.now().isoformat()
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Binance: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def btc_price_check():
    with open('config.json', 'r') as json_file:
        config = json.load(json_file)
    
    result = check_btc_price_drop(config['API_KEY'], config['API_SECRET'])
    
    if result:  
        if result['has_significant_drop']:
            print("\n⚠️ Significant price drop detected! (>= 2.5%)")
        else:
            print("\nNo significant price drop detected.")
            
    if result['has_significant_drop']:
        return True
    else:
        return False
    
    return False


# if __name__ == "__main__":
#     with open('config.json', 'r') as json_file:
#         config = json.load(json_file)
        
#     client = BinanceClient(config['API_KEY'], config['API_SECRET'])
#     btc_price_check()



