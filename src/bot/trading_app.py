import time
import threading
from main import *
from sell import *
import sys
from slack_bot import post_error_to_slack
from delete_live_trade import delete_live_trade
import warnings
import traceback
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

def scan_proposals():
    try:
        counter = 0
        db, app = create_firebase_client()
        store_data(db)
        summary_obj = Summarization("mistral")
        sentiment_analyzer = FinBERTSentiment()
        
        while True:
            delete_live_trade()
            proposal_dict = download_and_save_proposal(db)
            new_row_df = check_new_post(proposal_dict)
            
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
        print("Error running scan proposal:", e)
        post_error_to_slack(str(traceback.format_exc()))

    close_firebase_client(app)


if __name__ == "__main__":
    scan_proposals()
    



