import time
import threading
from main import *
from sell import *
import sys
from slack_bot import post_error_to_slack
from delete_live_trade import delete_live_trade
import traceback
import json
import os 

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
    try:
        counter = 0
        db, app = create_firebase_client()
        db_status = check_past_data()
        
        if db_status == False:
            print("-------------No DB Found, creating new DB----------")
            store_data(db)
        
        summary_obj = Summarization("mistral")
        sentiment_analyzer = FinBERTSentiment()
        
        client = Client(config['API_KEY'], config['API_SECRET'], tld='com')

        while True:
            try:
                # Perform the main logic of each iteration inside its own try-except block
                delete_live_trade(client)
                proposal_dict = download_and_save_proposal(db, True)
                new_row_df = check_new_post(proposal_dict)
                # print(new_row_df.iloc[0])

                trigger_trade(new_row_df, summary_obj, sentiment_analyzer)

                counter += 1

                # Countdown timer for 2 minutes (120 seconds)
                countdown_time = 1 * 60  # 120 seconds
                for remaining in range(countdown_time, 0, -1):
                    sys.stdout.write("\rNext scan in: {:02d}:{:02d}".format(remaining // 60, remaining % 60))
                    sys.stdout.flush()
                    time.sleep(1)

                print("\n")  # Move to the next line after the countdown

            except Exception as e:
                # Handle errors specific to one iteration and continue the loop
                print("Error in current scan round:", e)
                post_error_to_slack(str(traceback.format_exc()))
                
    except Exception as e:
        # Handle errors related to initializing or closing Firebase connection
        print("Error setting up scan proposals:", e)
        post_error_to_slack(str(traceback.format_exc()))

    finally:
        close_firebase_client(app)


if __name__ == "__main__":
    scan_proposals()
    



