#!/bin/bash

# Run the first command and disown it
nohup python3 -u trading_app.py > trade.log 2>&1 & disown

# Wait for 60 seconds
sleep 60

# Run the second command and disown it
nohup python3 -u open_stop.py > open_stop.log 2>&1 & disown
