#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 24 00:43:39 2024

@author: krishnayadav
"""

import numpy as np
import pandas as pd
import os
import yfinance as yf
from datetime import datetime, timedelta


price_dir = '/Users/krishnayadav/Documents/aiTradingBot/data/price_data'
# price_dir = '/Users/krishnayadav/Downloads/spot/all/'

def load_price():
    price_dict = {}
    
    for price_csv in os.listdir(price_dir):
        data = pd.read_csv(price_dir + '/' + price_csv)
        print(price_csv.split('.'))
        price_dict[str(price_csv.split('.')[0])] = data
    
    return price_dict
    

def read_files(post_directory):
    
    post_df_dict = {}
    for post in os.listdir(post_directory):
        if post == '.DS_Store':
            continue
        
        post_df = pd.read_csv(post_directory + '/' + post)
        post_df_dict[post.split('.')[0].split('_')[0]] = post_df
        
    return post_df_dict

def combine_post_comment(post_df_dict, comment_df_dict):    
    
    df_dict = {}
    
    for key in post_df_dict:
        protocol = []
        post_id =[]
        timestamp = []
        description = []
        category = []
        sentiment = []
        sentiment_score = []
        
        for index, row in post_df_dict[key].iterrows():
            protocol.append(row['protocol'])
            post_id.append(row['post_id'])
            timestamp.append(row['timestamp'])
            description.append(row['description'])
            category.append('post')
            sentiment.append(row['description_label'])
            sentiment_score.append(row['description_score'])
        
        for index, row in comment_df_dict[key].iterrows():
            protocol.append(key)
            post_id.append(row['post_id'])
            timestamp.append(row['created_at'])
            description.append(row['content'])
            category.append('comment')
            sentiment.append(row['content_label'])
            sentiment_score.append(row['content_score'])
        
        data = {
            'protocol': protocol,
            'post_id': post_id,
            'timestamp': timestamp,
            'description': description,
            'category': category,
            'sentiment': sentiment,
            'sentiment_score': sentiment_score
        }
        
        # Create the DataFrame
        df = pd.DataFrame(data)
        df = df.sort_values(by='timestamp')
        
        df_dict[key] = df
        
    return df_dict

def get_results(df_dict, price_dict, start, end, sentiment_treshold, neg_boolean):
    for key, post_df in df_dict.items():
        columns = [
                    'timestamp', 'post_id', 'description', 'sentiment', 'sentiment_score', 
                    'buying_price', 'end_day_price', 'day1', 'day2', 
                    'day3', 'day4', 'day5'
                ]
        result_df = pd.DataFrame(columns = columns)
        
        counter0 = 0
        counter1 = 0
        counter2 = 0
        counter3 = 0
        counter4 = 0
        counter5 = 0
        buying_price = 0
        
        for index, row in post_df.iterrows():
            try:
                coin_name = str(row['protocol'])
                post_id = row['post_id']
                description = row['description']
                full_date = row['timestamp']
                hour = full_date.split(' ')[1].split(':')[0]
                timestamp = row['timestamp'].split(' ')
                sentiment = row['sentiment']
                sentiment_score = row['sentiment_score']

                sentiment = sentiment.lower()
                
                if sentiment == 'positive' and sentiment_score > sentiment_treshold:
                    counter0 = counter0 + 1
                    date = timestamp[0]
                    df = price_dict[coin_name]
                    
                    # specific_date = '2018-01-28'
                    date_index = df.index[df['Date'] == date].tolist()[0]
                    probable_date_index = [date_index, date_index + 1, date_index + 2, date_index + 3, date_index + 4, date_index + 5]
                    
                    close_price_list = []
                    for date_index in probable_date_index:
                        close_price_list.append(df.iloc[date_index]['Close'])
                    
                    buying_price = close_price_list[0]
                    
                    if close_price_list[1] > buying_price:
                        counter1 = counter1 + 1
                        day1 = 1
                    
                    else:
                        day1 = 0
                    
                    if close_price_list[1] > buying_price and close_price_list[2] > buying_price:
                        counter2 = counter2 + 1
                        day2 = 1
                    
                    else:
                        day2 = 0
                    
                    if close_price_list[1] > buying_price and close_price_list[2] > buying_price and close_price_list[3] > buying_price:
                        counter3 = counter3 + 1
                        day3 = 1
                    
                    else:
                        day3 = 0
                        
                    if close_price_list[1] > buying_price and close_price_list[2] > buying_price and close_price_list[3] > buying_price and close_price_list[4] > buying_price:
                        counter4 = counter4 + 1
                        day4 = 1
                    
                    else:
                        day4 = 0
                        
                    if close_price_list[1] > buying_price and close_price_list[2] > buying_price and close_price_list[3] > buying_price and close_price_list[4] > buying_price and close_price_list[5] > buying_price:
                        counter5 = counter5 + 1
                        day5 = 1
                    else:
                        day5 = 0
        
                    new_row = [{
                                'timestamp' : timestamp, 
                                'post_id' : post_id, 
                                'description': description, 
                                'sentiment': sentiment, 
                                'sentiment_score': sentiment_score, 
                                'buying_price': buying_price, 
                                'end_day_price': close_price_list[5], 
                                'day1': day1, 
                                'day2': day2, 
                                'day3': day3, 
                                'day4': day4, 
                                'day5': day5
                            }]
                    
                    new_row = pd.DataFrame(new_row)
                    
                    result_df = pd.concat([result_df, new_row], ignore_index = True)        
            except Exception as e:
                continue
        print("\n\n----------")
        result_df.to_csv(f'/Users/krishnayadav/Documents/aiTradingBot/data/analysis5day/{key}.csv')
        print(f"{key}, counter0 = {counter0}, counter1 = {counter1}, counter2 = {counter2}, counter3 = {counter3}, counter4 = {counter4}, counter5 = {counter5}")
        print("\n\n----------")

"""
This backtesting covers all the positive and negative posts and comments
where you donot wait for 5 days and invest in all trades with additional capital 
"""

def backtest_strategy(df_dict, price_dict, start, end, sentiment_threshold, neg_boolean):
    for key, post_df in df_dict.items():
        print("\n\n")
        initial_capital = 1000
        profit_amount = 0
        loss_amount = 0
        
        counter0 = 0
        counter1 = 0
        counter2 = 0
        
        for index, row in post_df.iterrows():
            try:
                coin_name = str(row['protocol'])
                post_id = row['post_id']
                description = row['description']
                full_date = row['timestamp']
                hour = full_date.split(' ')[1].split(':')[0]
                timestamp = row['timestamp'].split(' ')
                sentiment = row['sentiment']
                sentiment_score = row['sentiment_score']
                
                sentiment = sentiment.lower()

                if sentiment == 'positive' and sentiment_score > sentiment_threshold and coin_name == '0xprotocol':
                    date = timestamp[0]
                    df = price_dict[coin_name]
                    counter0 = counter0 + 1
                    
                    date_index = df.index[df['Date'] == date].tolist()[0]
                    probable_date_index = [date_index, date_index + 1, date_index + 2, date_index + 3, date_index + 4, date_index + 5]
                    
                    
                    buying_date = price_dict[coin_name].iloc[probable_date_index[0]]['Date']
                    selling_date = price_dict[coin_name].iloc[probable_date_index[5]]['Date']
                    
                    
                    close_price_list = []
                    for date_index in probable_date_index:
                        close_price_list.append(df.iloc[date_index]['Close'])
                    
                    if close_price_list[5] > close_price_list[0]:
                        profit = close_price_list[5] - close_price_list[0]
                        number_of_shares = int(initial_capital / close_price_list[0])
                        initial_capital = initial_capital + number_of_shares * profit
                        
                        profit_amount += profit
                        print(f"{key}, buying_date = {buying_date}, selling_date = {selling_date} profit is there of {number_of_shares * profit} and initial capital = {initial_capital}")
                        counter1 = counter1 + 1

                                                
                    if close_price_list[5] < close_price_list[0]:
                        loss = close_price_list[0] - close_price_list[5]
                        number_of_shares = int(initial_capital / close_price_list[0])
                        initial_capital = initial_capital - number_of_shares * loss

                        loss_amount += loss
                        print(f"{key}, buying_date {buying_date}, selling_date = {selling_date} loss is there of {number_of_shares * loss} and initial capital = {initial_capital}")
                        counter2 = counter2 + 1

                        
        
        
                
    
            except Exception as e:
                continue
        print(f"counter0 = {counter0}, counter1 = {counter1}, counter2 = {counter2}")



def backtest_strategy_five_day_negative(df_dict, price_dict, start, end, sentiment_threshold, neg_boolean, test_coin, end_day):
    total_initial_capital = 0
    max_initial_capital = 0
    
    bruteforce_df = pd.DataFrame(columns=['coin', 'buying_date', 'selling_date', 'buying_price', 'selling_price', 'no_of_shares', 'profit', 'loss', 'initial_capital'])

    coins = [
    "aragon",
    "makerdao",
    "0xprotocol",
    "starknet",
    "pancakeswap"
                    ]

    for key, post_df in df_dict.items():
        # if key not in coins:
        #     continue
        
        if key == "apecoin" or key == "compound":
            continue
            
        initial_capital = 1000
        profit_amount = 0
        loss_amount = 0
        
        counter0 = 0
        counter1 = 0
        counter2 = 0
        capital_list = []
        previous_buying_date = datetime.strptime('2016-11-09', '%Y-%m-%d')
        
        for index, row in post_df.iterrows():
            try:
                coin_name = str(row['protocol'])
                post_id = row['post_id']
                description = row['description']
                full_date = row['timestamp']
                hour = full_date.split(' ')[1].split(':')[0]
                timestamp = row['timestamp'].split(' ')
                sentiment = row['sentiment']
                sentiment_score = row['sentiment_score']
                
                sentiment = sentiment.lower()
                
                # print(full_date)
                # full_date = '2024-08-14 22:36:24.112000+00:00'
                date_range = int(full_date.split(' ')[0].split('-')[0])
                # date_range = datetime.fromisoformat(full_date)
                # and date_range == 2020

                
                if sentiment == 'negative' and sentiment_score > sentiment_threshold:
                    date = timestamp[0]
                    df = price_dict[coin_name]
                    counter0 = counter0 + 1
                    
                    date_index = df.index[df['Date'] == date].tolist()[0]
                    # probable_date_index = [date_index, date_index + 1, date_index + 2, date_index + 3, date_index + 4, date_index + 5]
                    probable_date_index = [date_index + i for i in range(end_day + 1)]

                    
                    
                    buying_date = price_dict[coin_name].iloc[probable_date_index[0]]['Date']
                    buying_date = datetime.strptime(buying_date, '%Y-%m-%d')

                    # print(buying_date)
                    # print(previous_buying_date + timedelta(days=5))
                    
                    
                    selling_date = price_dict[coin_name].iloc[probable_date_index[end_day]]['Date']
                    selling_date = datetime.strptime(selling_date, '%Y-%m-%d')
                    
                    
                    close_price_list = []
                    for date_index in probable_date_index:
                        close_price_list.append(df.iloc[date_index]['Close'])
                    
                    if buying_date > previous_buying_date + timedelta(days=end_day):
                        if close_price_list[end_day] < close_price_list[0]:
                            profit = close_price_list[0] - close_price_list[end_day]
                            number_of_shares = int(initial_capital / close_price_list[0])
                            initial_capital = initial_capital + number_of_shares * profit
                            
                            profit_amount += profit
                            # print(f"{key}, buying_date = {buying_date}, selling_date = {selling_date}, buying_price = {close_price_list[0]}, selling_price = {close_price_list[end_day]}, no.shares = {number_of_shares} profit {number_of_shares * profit} and initial capital = {initial_capital}")
                            counter1 = counter1 + 1
                            
                            previous_buying_date = buying_date
                            
                            new_row = {'coin' : coin_name, 'buying_date' : buying_date, 'selling_date' : selling_date, 'buying_price' : close_price_list[0], 'selling_price': close_price_list[end_day], 'no_of_shares': number_of_shares, 'profit' : number_of_shares * profit, 'loss' : 0, 'initial_capital': initial_capital}
                            new_row = pd.DataFrame([new_row])
                            bruteforce_df = pd.concat([bruteforce_df, new_row], ignore_index=True)

                                                    
                        if close_price_list[1] > close_price_list[0]:
                            loss = close_price_list[1] - close_price_list[0]
                            
                            
                            number_of_shares = int(initial_capital / close_price_list[0])
                            
                            if number_of_shares * loss > 100:
                                total_loss = 100
                                initial_capital = initial_capital - total_loss
                            else:
                                total_loss = number_of_shares * loss
                                initial_capital = initial_capital - total_loss
                            
                            # total_loss = number_of_shares * loss
                            # initial_capital = initial_capital - total_loss

    
                            loss_amount += loss
                            # print(f"{key}, buying_date {buying_date}, selling_date = {selling_date}, buying_price = {close_price_list[0]}, selling_price = {close_price_list[end_day]}, no.shares = {number_of_shares}, loss = {number_of_shares * loss} and initial capital = {initial_capital}")
                            counter2 = counter2 + 1
                            
                            previous_buying_date = buying_date
                            
                            selling_date = price_dict[coin_name].iloc[probable_date_index[1]]['Date']
                            selling_date = datetime.strptime(selling_date, '%Y-%m-%d')
                            
                            new_row = {'coin' : coin_name, 'buying_date' : buying_date, 'selling_date' : selling_date, 'buying_price' : close_price_list[0], 'selling_price': close_price_list[end_day], 'no_of_shares': number_of_shares, 'profit' : 0 * profit, 'loss' : total_loss, 'initial_capital': initial_capital}
                            new_row = pd.DataFrame([new_row])
                            bruteforce_df = pd.concat([bruteforce_df, new_row], ignore_index=True)
                            
                        # if close_price_list[end_day] < close_price_list[0]:
                        #     loss = close_price_list[0] - close_price_list[end_day]
                        #     number_of_shares = int(initial_capital / close_price_list[0])
                        #     initial_capital = initial_capital - number_of_shares * loss
    
                        #     loss_amount += loss
                        #     # print(f"{key}, buying_date {buying_date}, selling_date = {selling_date}, buying_price = {close_price_list[0]}, selling_price = {close_price_list[end_day]}, no.shares = {number_of_shares}, loss = {number_of_shares * loss} and initial capital = {initial_capital}")
                        #     counter2 = counter2 + 1
                            
                        #     previous_buying_date = buying_date
                            
                        #     selling_date = price_dict[coin_name].iloc[probable_date_index[end_day]]['Date']
                        #     selling_date = datetime.strptime(selling_date, '%Y-%m-%d')
                            
                        #     new_row = {'coin' : coin_name, 'buying_date' : buying_date, 'selling_date' : selling_date, 'buying_price' : close_price_list[0], 'selling_price': close_price_list[end_day], 'no_of_shares': number_of_shares, 'profit' : 0 * profit, 'loss' : number_of_shares * loss, 'initial_capital': initial_capital}
                        #     new_row = pd.DataFrame([new_row])
                        #     bruteforce_df = pd.concat([bruteforce_df, new_row], ignore_index=True)

                            
                capital_list.append(initial_capital)
                

            except Exception as e:
                continue
        # print(f"counter0 = {counter0}, counter1 = {counter1}, counter2 = {counter2}")
        print(f"coin = {coin_name}, end_day = {end_day}, capital_at_end = {initial_capital}, max_capital = {max(capital_list)}, min_capital = {min(capital_list)}")
        
        if key != "compound":
            total_initial_capital = total_initial_capital + initial_capital
            max_initial_capital = max_initial_capital + max(capital_list)
            
        
    # print("----------------------------")
    print(f"total_initial_capital = {total_initial_capital}, max_initial_capital = {max_initial_capital}")
    
    new_row = {'sentiment_treshold': sentiment_threshold, 'hold_period': end_day, 'compounded_capital': total_initial_capital, 'compounded_max_capital': max_initial_capital}

    # return pd.DataFrame([new_row])
    return bruteforce_df


"""
This backtesting is based on Jaski logic.
"""
def backtest_strategy_continue(df_dict, price_dict, start, end, sentiment_threshold, neg_boolean, test_coin, stop_loss, end_day, input_date, input_month):
    total_initial_capital = 0
    max_initial_capital = 0
    
    bruteforce_df = pd.DataFrame(columns=['coin', 'buying_date', 'selling_date', 'trade_type', 'buying_price', 'selling_price', 'no_of_shares', 'profit', 'loss', 'initial_capital'])

    coins = [
    "aragon",
    "makerdao",
    "0xprotocol",
    "starknet",
    "pancakeswap"
                    ]

    not_coin = ["uniswap"]
    for key, post_df in df_dict.items():
        if key in not_coin:
            continue
            
        initial_capital = 1000
        profit_amount = 0
        loss_amount = 0
        
        counter0 = 0
        counter1 = 0
        counter2 = 0
        capital_list = []
        previous_buying_date = datetime.strptime('2016-11-09', '%Y-%m-%d')
        previous_selling_date = datetime.strptime('2016-11-08', '%Y-%m-%d')
        
        for index, row in post_df.iterrows():
            try:
                coin_name = str(row['protocol'])
                post_id = row['post_id']
                description = row['description']
                full_date = row['timestamp']
                hour = full_date.split(' ')[1].split(':')[0]
                timestamp = row['timestamp'].split(' ')
                # timestamp = row['timestamp']

                # sentiment = row['sentiment']
                # sentiment_score = row['sentiment_score']
                sentiment = row['description_label']
                sentiment_score = row['description_score']
                
                sentiment = sentiment.lower()
                
                date_range = int(full_date.split(' ')[0].split('-')[0])
                month = int(full_date.split(' ')[0].split('-')[1])
                percent = 2
                
                # date_range = datetime.fromisoformat(full_date)
                # and date_range == 2020
                # and date_range == input_date
                # and month == input_month

                # and date_range == input_date
                
                if sentiment == 'positive' and sentiment_score > sentiment_threshold:
                    date = timestamp[0]
                    # date = pd.to_datetime(timestamp).floor('T').strftime('%Y-%m-%d %H:%M:%S%z')
                    df = price_dict[coin_name]
                    date_index = df.index[df['Date'] == date].tolist()[0]
                    # date_index = df.index[df['timestamp'] == date].tolist()[0]

                    
                    probable_date_index = [i for i in range(date_index, len(df))]
                    probable_buying_price = df['Close'].iloc[probable_date_index].tolist()
                    buying_date = price_dict[coin_name].iloc[probable_date_index[0]]['Date']
                    buying_date = datetime.strptime(buying_date, '%Y-%m-%d')
                    
                    if buying_date >= previous_selling_date:
                        buying_price = probable_buying_price[0]
                        after_buying_price = buying_price
                        number_of_shares = initial_capital / buying_price
                        
                        for after_price_index in range(1, len(probable_buying_price)):
                            if probable_buying_price[after_price_index] > after_buying_price:
                                after_buying_price = probable_buying_price[after_price_index]
                                cut_off_price = after_buying_price - (percent/100) * after_buying_price

                                continue
                            
                            if  probable_buying_price[after_price_index] < after_buying_price:
                                cut_off_price = after_buying_price - (percent/100) * after_buying_price
                                
                                if probable_buying_price[after_price_index] < cut_off_price:
                                    if probable_buying_price[after_price_index] > buying_price:
                                        profit = (number_of_shares) * (cut_off_price - buying_price) 
                                        # profit = (number_of_shares) * (probable_buying_price[after_price_index] - buying_price) 

                                        previous_selling_date = df['Date'].iloc[probable_date_index[after_price_index]]
                                        previous_selling_date = datetime.strptime(previous_selling_date, '%Y-%m-%d')

                                        
                                        initial_capital = initial_capital + profit
                                        new_row = {'coin' : coin_name, 'buying_date' : buying_date, 'selling_date' : previous_selling_date, 'trade_type': 'call', 'buying_price' : buying_price, 'selling_price': cut_off_price, 'no_of_shares': number_of_shares, 'profit' : profit, 'loss' : 0, 'initial_capital': initial_capital}
                                        new_row = pd.DataFrame([new_row])
                                        bruteforce_df = pd.concat([bruteforce_df, new_row], ignore_index=True)
                                        break
                                    
                                    if probable_buying_price[after_price_index] < buying_price:
                                        loss = (number_of_shares) * (buying_price - cut_off_price)
                                        # loss = (number_of_shares) * (buying_price - probable_buying_price[after_price_index])


                                        previous_selling_date = df['Date'].iloc[probable_date_index[after_price_index]]
                                        previous_selling_date = datetime.strptime(previous_selling_date, '%Y-%m-%d')

                                        
                                        initial_capital = initial_capital - loss
                                        if loss > 0:
                                            new_row = {'coin' : coin_name, 'buying_date' : buying_date, 'selling_date' : previous_selling_date, 'trade_type': 'call', 'buying_price' : buying_price, 'selling_price': cut_off_price, 'no_of_shares': number_of_shares, 'profit' : 0 , 'loss' : loss, 'initial_capital': initial_capital}
                                        
                                        if loss < 0:
                                            new_row = {'coin' : coin_name, 'buying_date' : buying_date, 'selling_date' : previous_selling_date, 'trade_type': 'call', 'buying_price' : buying_price, 'selling_price': cut_off_price, 'no_of_shares': number_of_shares, 'profit' : -(loss), 'loss' : 0, 'initial_capital': initial_capital}
                                        
                                        new_row = pd.DataFrame([new_row])
                                        bruteforce_df = pd.concat([bruteforce_df, new_row], ignore_index=True)
                                        break
                                            
                            
                capital_list.append(initial_capital)
                

            except Exception as e:
                continue
        try:
            print(f"coin = {coin_name}, end_day = {end_day}, capital_at_end = {initial_capital}, max_capital = {max(capital_list)}, min_capital = {min(capital_list)}")
            
            if key != "compound":
                total_initial_capital = total_initial_capital + initial_capital
                max_initial_capital = max_initial_capital + max(capital_list)
        except:
            continue
            
        
    # print("----------------------------")
    print(f"total_initial_capital = {total_initial_capital}, max_initial_capital = {max_initial_capital}")
    
    new_row = {'year': input_date,  'sentiment_treshold': sentiment_threshold, 'hold_period': end_day, 'compounded_capital': total_initial_capital, 'compounded_max_capital': max_initial_capital}

    # return pd.DataFrame([new_row])
    return bruteforce_df


def backtest_strategy_continue1(df_dict, price_dict, start, end, sentiment_threshold, neg_boolean, test_coin, stop_loss, end_day, input_date, input_month):
    total_initial_capital = 0
    max_initial_capital = 0
    
    bruteforce_df = pd.DataFrame(columns=['coin', 'buying_date', 'selling_date', 'trade_type', 'buying_price', 'selling_price', 'no_of_shares', 'profit', 'loss', 'initial_capital'])

    coins = [
    "aragon",
    "makerdao",
    "0xprotocol",
    "starknet",
    "pancakeswap"
                    ]

    not_coin = ["uniswap"]
    for key, post_df in df_dict.items():
        if key in not_coin:
            continue
            
        initial_capital = 1000
        profit_amount = 0
        loss_amount = 0
        
        counter0 = 0
        counter1 = 0
        counter2 = 0
        capital_list = []
        previous_buying_date = datetime.strptime('2016-11-09', '%Y-%m-%d')
        previous_selling_date = datetime.strptime('2016-11-08', '%Y-%m-%d')
        
        for index, row in post_df.iterrows():
            try:
                coin_name = str(row['protocol'])
                post_id = row['post_id']
                description = row['description']
                full_date = row['timestamp']
                hour = full_date.split(' ')[1].split(':')[0]
                timestamp = row['timestamp'].split(' ')
                # timestamp = row['timestamp']

                # sentiment = row['sentiment']
                # sentiment_score = row['sentiment_score']
                sentiment = row['description_label']
                sentiment_score = row['description_score']
                
                sentiment = sentiment.lower()
                
                date_range = int(full_date.split(' ')[0].split('-')[0])
                month = int(full_date.split(' ')[0].split('-')[1])
                percent = 2
                
                # date_range = datetime.fromisoformat(full_date)
                # and date_range == 2020
                # and date_range == input_date
                # and month == input_month

                # and date_range == input_date
                
                if sentiment == 'positive' and sentiment_score > sentiment_threshold:
                    date = timestamp[0]
                    # date = pd.to_datetime(timestamp).floor('T').strftime('%Y-%m-%d %H:%M:%S%z')
                    df = price_dict[coin_name]
                    date_index = df.index[df['Date'] == date].tolist()[0]
                    # date_index = df.index[df['timestamp'] == date].tolist()[0]

                    
                    probable_date_index = [i for i in range(date_index, len(df))]
                    probable_buying_price = df['Close'].iloc[probable_date_index].tolist()
                    probable_low_price = df['Low'].iloc[probable_date_index].tolist()
                    buying_date = price_dict[coin_name].iloc[probable_date_index[0]]['Date']
                    buying_date = datetime.strptime(buying_date, '%Y-%m-%d')
                    
                    if buying_date >= previous_selling_date:
                        buying_price = probable_buying_price[0]
                        after_buying_price = buying_price
                        number_of_shares = initial_capital / buying_price
                        
                        for after_price_index in range(1, len(probable_buying_price)):
                            if probable_buying_price[after_price_index] > after_buying_price:
                                after_buying_price = probable_buying_price[after_price_index]
                                cut_off_price = after_buying_price - (percent/100) * after_buying_price

                                continue
                            
                            if  probable_buying_price[after_price_index] < after_buying_price:
                                cut_off_price = after_buying_price - (percent/100) * after_buying_price
                                
                                if probable_buying_price[after_price_index] < cut_off_price:
                                    if probable_buying_price[after_price_index] > buying_price:
                                        # profit = (number_of_shares) * (cut_off_price - buying_price) 
                                        profit = (number_of_shares) * (probable_buying_price[after_price_index] - buying_price) 

                                        previous_selling_date = df['Date'].iloc[probable_date_index[after_price_index]]
                                        previous_selling_date = datetime.strptime(previous_selling_date, '%Y-%m-%d')

                                        
                                        initial_capital = initial_capital + profit
                                        new_row = {'coin' : coin_name, 'buying_date' : buying_date, 'selling_date' : previous_selling_date, 'trade_type': 'call', 'buying_price' : buying_price, 'selling_price': probable_buying_price[after_price_index], 'no_of_shares': number_of_shares, 'profit' : profit, 'loss' : 0, 'initial_capital': initial_capital}
                                        new_row = pd.DataFrame([new_row])
                                        bruteforce_df = pd.concat([bruteforce_df, new_row], ignore_index=True)
                                        break
                                    
                                    if probable_buying_price[after_price_index] < buying_price:
                                        # loss = (number_of_shares) * (buying_price - cut_off_price)
                                        loss = (number_of_shares) * (buying_price - probable_buying_price[after_price_index])


                                        previous_selling_date = df['Date'].iloc[probable_date_index[after_price_index]]
                                        previous_selling_date = datetime.strptime(previous_selling_date, '%Y-%m-%d')

                                        
                                        initial_capital = initial_capital - loss
                                        if loss > 0:
                                            new_row = {'coin' : coin_name, 'buying_date' : buying_date, 'selling_date' : previous_selling_date, 'trade_type': 'call', 'buying_price' : buying_price, 'selling_price': probable_buying_price[after_price_index], 'no_of_shares': number_of_shares, 'profit' : 0 , 'loss' : loss, 'initial_capital': initial_capital}
                                        
                                        if loss < 0:
                                            new_row = {'coin' : coin_name, 'buying_date' : buying_date, 'selling_date' : previous_selling_date, 'trade_type': 'call', 'buying_price' : buying_price, 'selling_price': probable_buying_price[after_price_index], 'no_of_shares': number_of_shares, 'profit' : -(loss), 'loss' : 0, 'initial_capital': initial_capital}
                                        
                                        new_row = pd.DataFrame([new_row])
                                        bruteforce_df = pd.concat([bruteforce_df, new_row], ignore_index=True)
                                        break
                                            
                            
                capital_list.append(initial_capital)
                

            except Exception as e:
                continue
        try:
            print(f"coin = {coin_name}, end_day = {end_day}, capital_at_end = {initial_capital}, max_capital = {max(capital_list)}, min_capital = {min(capital_list)}")
            
            if key != "compound":
                total_initial_capital = total_initial_capital + initial_capital
                max_initial_capital = max_initial_capital + max(capital_list)
        except:
            continue
            
        
    # print("----------------------------")
    print(f"total_initial_capital = {total_initial_capital}, max_initial_capital = {max_initial_capital}")
    
    new_row = {'year': input_date,  'sentiment_treshold': sentiment_threshold, 'hold_period': end_day, 'compounded_capital': total_initial_capital, 'compounded_max_capital': max_initial_capital}

    # return pd.DataFrame([new_row])
    return bruteforce_df
        


"""
This backtesting donot covers all the positive and negative posts and comments
where you have to wait for 5 days.
"""

def backtest_strategy_five_day(df_dict, price_dict, start, end, sentiment_threshold, neg_boolean, test_coin, stop_loss, end_day, input_date, input_month):
    total_initial_capital = 0
    max_initial_capital = 0
    
    bruteforce_df = pd.DataFrame(columns=['coin', 'buying_date', 'selling_date', 'buying_price', 'selling_price', 'no_of_shares', 'profit', 'loss', 'initial_capital'])

    coins = [
    "aragon",
    "makerdao",
    "0xprotocol",
    "starknet",
    "pancakeswap"
                    ]

    not_coin = ["uniswap", "starknet", "compound"]
    for key, post_df in df_dict.items():
        if key in not_coin:
            continue
        
        # if key in not_coin:
        #     continue
            
        initial_capital = 1000
        profit_amount = 0
        loss_amount = 0
        
        counter0 = 0
        counter1 = 0
        counter2 = 0
        capital_list = []
        previous_buying_date = datetime.strptime('2016-11-09', '%Y-%m-%d')
        
        for index, row in post_df.iterrows():
            try:
                coin_name = str(row['protocol'])
                post_id = row['post_id']
                description = row['description']
                full_date = row['timestamp']
                hour = full_date.split(' ')[1].split(':')[0]
                timestamp = row['timestamp'].split(' ')
                sentiment = row['sentiment']
                sentiment_score = row['sentiment_score']
                
                sentiment = sentiment.lower()
                
                # print(full_date)
                # full_date = '2024-08-14 22:36:24.112000+00:00'
                date_range = int(full_date.split(' ')[0].split('-')[0])
                month = int(full_date.split(' ')[0].split('-')[1])
                
                # date_range = datetime.fromisoformat(full_date)
                # and date_range == 2020
                # and date_range == input_date
                # and month == input_month


                
                if sentiment == 'positive' and sentiment_score > sentiment_threshold and date_range == input_date and month == input_month:
                    date = timestamp[0]
                    df = price_dict[coin_name]
                    counter0 = counter0 + 1
                    
                    date_index = df.index[df['Date'] == date].tolist()[0]
                    # probable_date_index = [date_index, date_index + 1, date_index + 2, date_index + 3, date_index + 4, date_index + 5]
                    probable_date_index = [date_index + i for i in range(end_day + 1)]

                    

                    buying_date = price_dict[coin_name].iloc[probable_date_index[0]]['Date']
                    buying_date = datetime.strptime(buying_date, '%Y-%m-%d')

                    # print(buying_date)
                    # print(previous_buying_date + timedelta(days=5))
                    
                    
                    selling_date = price_dict[coin_name].iloc[probable_date_index[end_day]]['Date']
                    selling_date = datetime.strptime(selling_date, '%Y-%m-%d')
                    
                    
                    close_price_list = []
                    for date_index in probable_date_index:
                        close_price_list.append(df.iloc[date_index]['Close'])
                    
                    if buying_date > previous_buying_date + timedelta(days=end_day):
                        if close_price_list[end_day] > close_price_list[0]:
                            profit = close_price_list[end_day] - close_price_list[0]
                            number_of_shares = int(initial_capital / close_price_list[0])
                            initial_capital = initial_capital + number_of_shares * profit
                            
                            profit_amount += profit
                            # print(f"{key}, buying_date = {buying_date}, selling_date = {selling_date}, buying_price = {close_price_list[0]}, selling_price = {close_price_list[end_day]}, no.shares = {number_of_shares} profit {number_of_shares * profit} and initial capital = {initial_capital}")
                            counter1 = counter1 + 1
                            
                            previous_buying_date = buying_date
                            
                            new_row = {'coin' : coin_name, 'buying_date' : buying_date, 'selling_date' : selling_date, 'buying_price' : close_price_list[0], 'selling_price': close_price_list[end_day], 'no_of_shares': number_of_shares, 'profit' : number_of_shares * profit, 'loss' : 0, 'initial_capital': initial_capital}
                            new_row = pd.DataFrame([new_row])
                            bruteforce_df = pd.concat([bruteforce_df, new_row], ignore_index=True)
                            # end_day = 11

                                                    
                        elif close_price_list[1] < close_price_list[0]:
                            loss = close_price_list[0] - close_price_list[1]
                            
                            
                            number_of_shares = int(initial_capital / close_price_list[0])
                            
                            if number_of_shares * loss > stop_loss:
                                total_loss = stop_loss
                                initial_capital = initial_capital - total_loss
                            else:
                                total_loss = number_of_shares * loss
                                initial_capital = initial_capital - total_loss
                            
                            # total_loss = number_of_shares * loss
                            # initial_capital = initial_capital - total_loss

    
                            loss_amount += loss
                            # print(f"{key}, buying_date {buying_date}, selling_date = {selling_date}, buying_price = {close_price_list[0]}, selling_price = {close_price_list[end_day]}, no.shares = {number_of_shares}, loss = {number_of_shares * loss} and initial capital = {initial_capital}")
                            counter2 = counter2 + 1
                            
                            previous_buying_date = buying_date
                            
                            selling_date = price_dict[coin_name].iloc[probable_date_index[1]]['Date']
                            selling_date = datetime.strptime(selling_date, '%Y-%m-%d')
                            
                            new_row = {'coin' : coin_name, 'buying_date' : buying_date, 'selling_date' : selling_date, 'buying_price' : close_price_list[0], 'selling_price': close_price_list[end_day], 'no_of_shares': number_of_shares, 'profit' : 0 * profit, 'loss' : total_loss, 'initial_capital': initial_capital}
                            new_row = pd.DataFrame([new_row])
                            bruteforce_df = pd.concat([bruteforce_df, new_row], ignore_index=True)
                            
                            # end_day = 1

                            
                capital_list.append(initial_capital)
                

            except Exception as e:
                continue
        # print(f"counter0 = {counter0}, counter1 = {counter1}, counter2 = {counter2}")
        try:
            print(f"coin = {coin_name}, end_day = {end_day}, capital_at_end = {initial_capital}, max_capital = {max(capital_list)}, min_capital = {min(capital_list)}")
            
            if key != "compound":
                total_initial_capital = total_initial_capital + initial_capital
                max_initial_capital = max_initial_capital + max(capital_list)
        except:
            continue
            
        
    # print("----------------------------")
    print(f"total_initial_capital = {total_initial_capital}, max_initial_capital = {max_initial_capital}")
    
    new_row = {'year': input_date,  'sentiment_treshold': sentiment_threshold, 'hold_period': end_day, 'compounded_capital': total_initial_capital, 'compounded_max_capital': max_initial_capital}

    # return pd.DataFrame([new_row])
    return bruteforce_df
        

        

# Example Usage
if __name__ == "__main__":
    
    # post_directory = '/Users/krishnayadav/Documents/aiTradingBot/data/ai_posts_labeled_new/'
    # comment_directory = '/Users/krishnayadav/Documents/aiTradingBot/data/ai_comments_labeled_new/'
    
    post_directory = '/Users/krishnayadav/Documents/aiTradingBot/data/fin_bert_labeled/posts_new/'
    comment_directory = '/Users/krishnayadav/Documents/aiTradingBot/data/fin_bert_labeled/comments_new/'
    proposal_dir = '/Users/krishnayadav/Downloads/post_proposal_summarized_label/'
    
    # post_directory = '/Users/krishnayadav/Documents/aiTradingBot/data/crypto_bert_labeled/posts/'
    # comment_directory = '/Users/krishnayadav/Documents/aiTradingBot/data/crypto_bert_labeled/comments/'
    
    post_df_dict = read_files(proposal_dir)
    comment_df_dict = read_files(comment_directory)
    price_dict = load_price()
    df_dict = combine_post_comment(post_df_dict, comment_df_dict)
    
    # get_results(df_dict, price_dict, 1, 5, 0.5, True)
    
    # backtest_strategy(df_dict, price_dict, 1, 5, 0.5, True)
    # bruteforce_df = backtest_strategy_five_day(df_dict, price_dict, 1, 5, 0.8, True, 'uniswap', 5, 11, 2020, 0)
    bruteforce_df = backtest_strategy_continue(post_df_dict, price_dict, 1, 5, 0.7, True, 'uniswap', 5, 5, 2022, 7)
    bruteforce_df_1 = backtest_strategy_continue1(post_df_dict, price_dict, 1, 5, 0.7, True, 'uniswap', 5, 5, 2022, 7)

    loss_ws = bruteforce_df['loss']
    loss_s = bruteforce_df['loss']
    
    print(sum(loss_s))
    
    print(bruteforce_df['coin'].unique())

    percent_list = [0.6, 0.7, 0.8, 0.9]
    day_list = [2019, 2020, 2021, 2022, 2023]
    bruteforce_df = pd.DataFrame(columns=['year', 'sentiment_treshold', 'hold_period', 'compounded_capital', 'compounded_max_capital'])

    for day_range in day_list:
        for day in range(2, 13):
            for percent in percent_list:
                print(f"\n percent = {percent}, day = {day}, year = {day_range}")
                new_row = backtest_strategy_five_day(df_dict, price_dict, 1, 5, percent, True, 'uniswap', day, day_range)
            # backtest_strategy_five_day(df_dict, price_dict, 1, 5, percent, True, 'uniswap', day)

                bruteforce_df = pd.concat([bruteforce_df, new_row], ignore_index=True)
    
    bruteforce_df.to_csv('/Users/krishnayadav/Documents/aiTradingBot/results/2018-2024(WOSL).csv')
    bruteforce_df.to_csv('/Users/krishnayadav/Documents/aiTradingBot/results/2018-2024(WSL).csv')
    

    
    

    # for key, value in df_dict.items():
    #     print(key, len(value), (value['sentiment'] == 'positive').sum())
    
    for key, value in df_dict.items():
        # Convert 'date' column to datetime if not already
        # value['date'] = pd.to_datetime(value['timestamp'])
        value['date'] = value['timestamp']
        
        # Filter based on the date range from 2018 to 2019
        filtered_df = value.loc[(value['date'] >= '2024-01-01') & (value['date'] <= '2024-12-31')]
        
        # Print the required information
        print(key, len(filtered_df), (filtered_df['sentiment'] == 'positive').sum())
    
    
    import pandas as pd

    # Assuming df_dict is your dictionary containing DataFrames for each coin
    # Replace df_dict with your actual dictionary name
    
    # Initialize a dictionary to store the results
    results = {}
    
    for coin, df in price_dict.items():
        # Ensure the 'Date' column is in datetime format
        df['Date'] = pd.to_datetime(df['Date'])
    
        # Extract the year from the 'Date' column
        df['Year'] = df['Date'].dt.year
    
        # Group by the 'Year' and calculate the min, mean, and max of the 'Close' price
        yearly_stats = df.groupby('Year')['Close'].agg(['min', 'mean', 'max']).reset_index()
    
        # Add missing years with zeroes for all values
        all_years = pd.DataFrame({'Year': range(2018, 2024)})
        yearly_stats = pd.merge(all_years, yearly_stats, on='Year', how='left').fillna(0)
    
        # Store the results in the dictionary
        results[coin] = yearly_stats
    
    # Display the results for each coin
    for coin, stats in results.items():
        print(f"Coin: {coin}")
        print(stats)
        print("\n")




