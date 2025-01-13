import time
import threading
from main import *
from sell import *
import sys
from slack_bot import post_error_to_slack
from delete_live_trade import delete_live_trade
from sentiment import SentimentPredictor
import traceback
import json
import os 
from utils import *

def check_past_data():
    global config
    with open('config.json', 'r') as json_file:
        config = json.load(json_file)
    
    files_data_len = len(os.listdir(config['data_dir']))
    if files_data_len >=3:
        return True
    else:
        return False

def scan_proposals():
    while True:  # Outer loop to handle setup and teardown errors
        try:
            counter = 0
            db, app = create_firebase_client()
            db_status = check_past_data()

            if db_status == False:
                print("-------------No DB Found, creating new DB----------")
                store_data(db)

            summary_obj = Summarization("mistral")
            sentiment_analyzer = SentimentPredictor(config['sentiment_dir'])
            client = Client(config['API_KEY'], config['API_SECRET'], tld='com')

            while True:  # Main operational loop
                try:
                    delete_live_trade(client)
                    proposal_dict = download_and_save_proposal(db, True)
                    new_row_df = check_new_post(proposal_dict)      
                    trigger_trade(new_row_df, summary_obj, sentiment_analyzer)
                    counter += 1

                    # Countdown timer for 2 minutes (120 seconds)
                    countdown_time = 1 * 60
                    for remaining in range(countdown_time, 0, -1):
                        sys.stdout.write("\rNext scan in: {:02d}:{:02d}".format(remaining // 60, remaining % 60))
                        sys.stdout.flush()
                        time.sleep(1)

                    print("\n")

                except Exception as e:
                    print("Error in current scan round:", e)
                    post_error_to_slack(str(traceback.format_exc()))
                    save_error(str(e))
                    time.sleep(60)
                    continue

        except Exception as e:
            print("Error setting up scan proposals:", e)
            post_error_to_slack(str(traceback.format_exc()))
            save_error(str(e))
            print("Attempting to restart the setup after a delay...")
            time.sleep(60)  # Wait for 60 seconds before retrying
            continue  # Retries the outer loop

        finally:
            close_firebase_client(app)


if __name__ == "__main__":
    post_error_to_slack("Governance Trading Bot Started")
    scan_proposals()
    

    



