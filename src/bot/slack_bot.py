#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 15:23:33 2024

@author: krishnayadav
"""

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Slack bot token from your app
slack_token = 'xoxb-your-slack-bot-token'

# Initialize the Slack client
client = WebClient(token=slack_token)

# Define the channel ID or name (e.g., '#general')
channel_id = '#your-channel-id'

def post_to_slack(message):
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=message
        )
        print(f"Message posted successfully: {response['ts']}")
    except SlackApiError as e:
        print(f"Error posting message: {e.response['error']}")

# Your condition
condition_met = True  # Replace this with your actual condition logic

if condition_met:
    post_to_slack("The condition has been met!")
