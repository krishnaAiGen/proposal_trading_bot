from utils import load_dictionary, get_ist_time, get_coin_price, save_dictionary
import json
from binance_api import get_last_5_days_price
from datetime import datetime


with open('config.json', 'r') as json_file:
    config = json.load(json_file)

class Monitor:
    def __init__(self, dynamo, table_name):
        self.dynamo = dynamo  
        self.table_name = table_name
    
    def get_highest_lowest(self, ohlc_dict):
        if not ohlc_dict:
            return None, None, None, None, None, None
    
        highest_price = float('-inf')
        lowest_price = float('inf')
        highest_date = None
        lowest_date = None
        highest_type = None
        lowest_type = None
        
        for date, prices in ohlc_dict.items():
            # Check for highest price (comparing both high and close)
            if prices['high'] > highest_price:
                highest_price = prices['high']
                highest_date = date
                highest_type = 'high'
            
            # Also check close price for potential highest
            if prices['close'] > highest_price:
                highest_price = prices['close']
                highest_date = date
                highest_type = 'close'
            
            # Check for lowest price (comparing both low and open)
            if prices['low'] < lowest_price:
                lowest_price = prices['low']
                lowest_date = date
                lowest_type = 'low'
            
            # Also check open price for potential lowest
            if prices['open'] < lowest_price:
                lowest_price = prices['open']
                lowest_date = date
                lowest_type = 'open'
        
        return highest_price, lowest_price, highest_date, lowest_date
    
    def get_remark(self, highest_date, lowest_date):
        remark = ""
        
        highest_date = datetime.strptime(highest_date, '%Y-%m-%d')
        lowest_date = datetime.strptime(lowest_date, '%Y-%m-%d')
        
        if highest_date > lowest_date:
            remark = "stop_loss"
            
        elif highest_date < lowest_date:
            remark = "target hit"
        else:
            remark = "same date"
            
        return remark

    
    def check_price(self):
        price_check_dict = load_dictionary(config['data_dir'] + '/price_check.json')
        
        if len(price_check_dict) == 0:
            return
            
        current_date = get_ist_time().split(' ')[0]
        
        for price_dict in price_check_dict:
            coin_date = price_dict['time_after_5_days']
            coin_initial_date = price_dict['initial_time'].split(' ')[0]
            coin_name = price_dict['coin_name']
            trade_id = price_dict['trade_id']
            coin_initial_price = price_dict['initial_price']
            
            # coin_initial_date = '2025-02-13'
            # coin_date = '2025-02-19'
            # last_5_day_price = get_last_5_days_price(coin_name, coin_initial_date, coin_date, interval="1d")

            
            if current_date == coin_date:
                price = get_coin_price(coin_name)
                last_5_day_price = get_last_5_days_price(coin_name, coin_initial_date, coin_date, interval="1d")
                highest_price, lowest_price, highest_date, lowest_date = self.get_highest_lowest(last_5_day_price)
                # remark = self.get_remark(highest_date, lowest_date)
                
                # Define the primary key for identifying the item
                primary_key = {
                    "trade_id": {"S": str(trade_id)}
                }
                
                # Define new attributes to add
                new_attributes = {
                    "highest_price": {"S": str(highest_price)},  
                    "highest_date": {"S": str(highest_date)},  
                    "lowest_price": {"S": str(lowest_price)},
                    "lowest_date": {"S": str(lowest_date)},
                }
                
                # Construct the UpdateExpression dynamically
                update_expression = "SET " + ", ".join(f"{key} = :{key}" for key in new_attributes.keys())
                
                # ExpressionAttributeValues mapping
                expression_attribute_values = {f":{key}": value for key, value in new_attributes.items()}
                
                # Update the item in DynamoDB
                try:
                    response = self.dynamo.client.update_item(
                        TableName=self.table_name,
                        Key=primary_key,
                        UpdateExpression=update_expression,
                        ExpressionAttributeValues=expression_attribute_values
                    )
                    print("New columns added successfully:", response)
                    
                    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                        price_check_dict.remove(price_dict)
                        save_dictionary(price_check_dict, config['data_dir'] + '/price_check.json')
                        print(f"trade with trade_id {trade_id} removed from price check json")

                except Exception as e:
                    print("Failed to update item:", str(e))
            
            else:
                print(f"current and future date mismatched. Current date: {current_date}, coin date: {coin_date}")


                
                
            
            
            
# if __name__ == "__main__":
#     from dynamo_utils import DynamoDBClient
#     dynamo = DynamoDBClient()
#     monitor = Monitor(dynamo, 'trade_table')
#     monitor.check_price()
        
        
        
        