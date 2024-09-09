from model_prediction import * 
import pandas as pd
import numpy as np

# model_path_proposal = '/Users/krishnayadav/Downloads/trained_model_proposal/'
model_path_proposal = '/Users/krishnayadav/Downloads/trained_model_avg/'
high_price_model_path = '/Users/krishnayadav/Downloads/trained_model_price/'
average_price_model_path = '/Users/krishnayadav/Downloads/trained_model_price_avg/'
label_mapping = {0: 'bearish', 1: 'bullish', 2: 'neutral'}  # Use your predefined label mapping

def clean_text_for_bert(df, text_column):
    # Step 1: Remove empty strings or strings that are just whitespace
    df[text_column] = df[text_column].astype(str)  # Ensure the column is of string type
    df[text_column] = df[text_column].str.strip()  # Remove leading and trailing whitespace
    df = df[df[text_column] != '']  # Remove rows where the text column is empty
    
    df['normalized_text'] = df[text_column].str.lower()  # Normalize text for duplicate checking
    df = df.drop_duplicates(subset=['normalized_text'], keep='first')  # Keep the first occurrence
    df = df.drop(columns=['normalized_text'])  # Remove the helper column used for checking duplicates
    

    df[text_column] = df[text_column].str.replace('[^\w\s]', '', regex=True)  # Remove special characters    
    df = df.reset_index(drop=True)
        
    return df

def load_post_price():
    post_df = pd.read_csv('/Users/krishnayadav/Documents/aiTradingBot/data/post_proposal/sushi_df.csv')
    post_clean = clean_text_for_bert(post_df, "description")
    post_clean = post_clean[["timestamp", "description"]]
    
    price_df = pd.read_csv("/Users/krishnayadav/Downloads/spot/all_day/sushi.csv")
    
    return post_clean, price_df


def get_price_list(timestamp, price_df):
    price_df['timestamp'] = pd.to_datetime(price_df['timestamp'])

    if price_df['timestamp'].dt.tz is None:
        price_df['timestamp'] = price_df['timestamp'].dt.tz_localize('UTC')
    else:
        price_df['timestamp'] = price_df['timestamp'].dt.tz_convert('UTC')    

    T_datetime = pd.to_datetime(timestamp).tz_convert('UTC')
    T_datetime = T_datetime.replace(second=0, microsecond=0)
    
    price = price_df[price_df['timestamp'] == T_datetime]['Close'].to_list()[0]
    start_index = price_df[price_df['timestamp'] == T_datetime].index[0]
    end_index = start_index + (5*24*60)
    
    price_list = price_df.loc[start_index:end_index]['Close']
    timestamp_list = price_df.loc[start_index:end_index]['timestamp']
    
    return price_list, timestamp_list
    

def backtest(post_df, price_df):
    intial_capital = 1000
    
    columns = ['buying_timestmap', 'buying_price', 'selling_timestamp', 'selling_price', 'profit', 'loss']
    
    backtest_df = pd.DataFrame(columns = columns)
    
    for index, row in post_df.iterrows():
        print(index)
        print("intitial capital", intial_capital)
        description = row['description']
        
        description = "proposal to deperecate vega chain"
        
        timestamp = row['timestamp']
        proposal_type = classify_bullish_bearish(model_path_proposal, description, label_mapping)[0]
        print(proposal_type)
        
        if proposal_type!= 'neutral':
            average_price = predict_average_price(average_price_model_path, description)
            high_price = predict_high_price(high_price_model_path, description)
        
        try:
            price_list, timestamp_list = get_price_list(timestamp, price_df)
        except Exception as e:
            print(e)
            continue
        
        if proposal_type == 'neutral':
            continue
        
        elif proposal_type == 'bullish':
            buying_price = price_list[0]
            buying_timestmap = timestamp_list[0]
            number_of_stocks = intial_capital / buying_price
            stop_loss = buying_price - 0.05 * buying_price
            
            for index in range(len(price_list)):
                price = price_list[index]
                if price >= high_price:
                    diff_price = high_price - buying_price
                    profit = number_of_stocks * diff_price
                    capital = capital + profit
                    profit_timestamp = timestamp_list[index]
                    
                    new_row = {
                        'buying_timestmap' : buying_timestmap,
                        'buying_price' : buying_price,
                        'selling_timestamp': profit_timestamp,
                        'selling_price': price,
                        'profit': profit,
                        'loss': 0
                        
                        }
                    backtest_df = pd.concat([backtest_df, pd.DataFrame(new_row)], ignore_index=True)
                    
                    break
                
                if price <= stop_loss:
                    diff = 0.05 * buying_price 
                    loss = number_of_stocks * diff
                    loss_timestamp = timestamp_list[index]
                    capital = capital - loss
                    
                    new_row = {
                        'buying_timestmap' : buying_timestmap,
                        'buying_price' : buying_price,
                        'selling_timestamp': loss_timestamp,
                        'selling_price': price,
                        'profit': loss,
                        'loss': 0
                        
                        }
                    backtest_df = pd.concat([backtest_df, pd.DataFrame(new_row)], ignore_index=True)
                    break
        
        
        elif proposal_type == 'bearish':
            buying_price = price_list[0]
            number_of_stocks = intial_capital / buying_price
            stop_loss = buying_price + 0.05 * buying_price
            
            for index in range(len(price_list)):
                price = price_list[index]
                if price <= high_price:
                    diff_price = buying_price - high_price
                    profit = number_of_stocks * diff_price
                    capital = capital + profit
                    profit_timestamp = timestamp_list[index]
                    
                    new_row = {
                        'buying_timestmap' : buying_timestmap,
                        'buying_price' : buying_price,
                        'selling_timestamp': profit_timestamp,
                        'selling_price': price,
                        'profit': profit,
                        'loss': 0
                        
                        }
                    backtest_df = pd.concat([backtest_df, pd.DataFrame(new_row)], ignore_index=True)
                    
                    break
                
                if price <= stop_loss:
                    diff = 0.05 * buying_price 
                    loss = number_of_stocks * diff
                    loss_timestamp = timestamp_list[index]
                    capital = capital - loss
                    new_row = {
                        'buying_timestmap' : buying_timestmap,
                        'buying_price' : buying_price,
                        'selling_timestamp': loss_timestamp,
                        'selling_price': price,
                        'profit': loss,
                        'loss': 0
                        
                        }
                    backtest_df = pd.concat([backtest_df, pd.DataFrame(new_row)], ignore_index=True)
                    break

    return backtest_df

if __name__ == "__main__":
    post_clean, price_df = load_post_price()
    backtest_df = backtest(post_clean, price_df)

    
    


        

    


