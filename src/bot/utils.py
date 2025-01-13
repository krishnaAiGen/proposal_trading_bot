#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 20:15:44 2024

@author: krishnayadav
"""

import json
from datetime import datetime
import pytz
import os

with open('config.json', 'r') as json_file:
    config = json.load(json_file)

def save_dictionary(dictionary, filename):        
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(dictionary, json_file, indent=4)  # Use indent for pretty

def load_dictionary(filename):
    with open(filename, 'r', encoding='utf-8') as json_file:
        return json.load(json_file)

def get_ist_time():
    ist_timezone = pytz.timezone('Asia/Kolkata')    
    current_utc_time = datetime.now(pytz.utc)
    
    current_ist_time = current_utc_time.astimezone(ist_timezone)    
    ist_time_string = current_ist_time.strftime('%Y-%m-%d %H:%M:%S')
    
    return ist_time_string

def save_error(error):
    error_filename = config['data_dir'] + '/error.json'
    current_time = get_ist_time()
    
    if not os.path.exists(error_filename):
        error_dict = {}
        error_dict[current_time] = error
        save_dictionary(error_dict, error_filename)
    
    else:
        error_dict = load_dictionary(error_filename)
        error_dict[current_time] = error
        save_dictionary(error_dict, error_filename)
        
    print(f"error {error} saved")
    
    



