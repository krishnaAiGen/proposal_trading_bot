import time
import threading
from main import *
from sell import *

# First loop function with a 5-second sleep interval
def scan_proposals():
    counter = 0
    db, app = create_firebase_client()
    store_data(db)
    summary_obj = Summarization("mistral")
    sentiment_analyzer = FinBERTSentiment()
    
    while True:
        try:
            proposal_dict = download_and_save_proposal(db)
            new_row_df = check_new_post(proposal_dict)
            
            
    #         new_row_df =   {
    #             'post_id': 'uniswap-1',
    #             'coin' : 'uniswap',
    #             'timestamp': '2024-11-12',
    #             'description': "The DLT Science Foundation (DSF) has announced its support for the launch of the MiCA Crypto Alliance, with Hedera, Ripple, and Aptos Foundation as founding members. This industry association aims to streamline and enhance compliance with the European Union’s Markets in Crypto-Assets (MiCA) regulation, fostering a sustainable and compliant crypto ecosystem. The MiCA regulation, set to be fully applicable by the end of this year, provides a comprehensive framework for the crypto market, ensuring transparency, consumer protection, and market integrity. The MiCA Crypto Alliance will coordinate compliance efforts among leading blockchain projects and Crypto-Asset Service Providers (CASPs), promoting uniformity and standardization in sustainability disclosures and regulatory compliance."
    # }
    #         new_row_df = pd.DataFrame([new_row_df])   
            
            trigger_trade(new_row_df, summary_obj, sentiment_analyzer)
            
            counter = counter + 1
        
        except Exception as e:
            print("error running scan proposal", e)
            
        # time.sleep(5*60)
     
    close_firebase_client(app)

# Second loop function with a 10-second sleep interval
def scan_open_trades():
    while True:
        try:
            update_or_sell()
        except Exception as e:
            print("error while updating stop loss", e)
            
        # time.sleep(5*60)

# # Creating two threads for the loops
# thread1 = threading.Thread(target=scan_proposals)
# thread2 = threading.Thread(target=loop_10_seconds)

# # Starting both threads
# thread1.start()
# thread2.start()

# scan_proposals()
scan_open_trades()