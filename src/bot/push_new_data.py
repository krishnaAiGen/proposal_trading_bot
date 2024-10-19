import firebase_admin
from firebase_admin import credentials, firestore
import json
import pandas as pd

# Function to load configuration from a JSON file
def load_config(config_file_path):
    with open(config_file_path, 'r') as json_file:
        config = json.load(json_file)
    return config

# Function to create a Firebase client and Firestore instance
def create_firebase_client(config):
    if not firebase_admin._apps:  # Check if the app is already initialized
        cred = credentials.Certificate(config["firebase_cred"])
        app = firebase_admin.initialize_app(cred)
    else:
        app = firebase_admin.get_app()
    db = firestore.client()
    return db, app

# Function to create the data to be pushed to Firestore
def create_post_data(id1, post_id, post_type, protocol, title, coin, timestamp, description, discussion_link, house_id, created_at):
    new_row = {
        'id' : id1,
        'post_id': post_id,
        'post_type': post_type,
        'protocol': protocol,
        'title': title,
        'coin': coin,
        'timestamp': timestamp,
        'description': description,
        'discussion_link': discussion_link,
        'house_id' : house_id,
        'created_at' : created_at
    }
    return pd.DataFrame([new_row])  # Return a DataFrame if needed

# Function to push data to Firestore collection
def push_data_to_firestore(db, collection_name, data):
    collection_ref = db.collection(collection_name)
    doc_ref = collection_ref.document(data['post_id'])  # Use post_id as document ID
    doc_ref.set(data)  # Push the data using set method
    print(f"Data with post_id {data['post_id']} pushed to Firestore successfully.")

# Main function that orchestrates the above functions
def main():
    # Load config
    config = load_config('config.json')

    # Initialize Firebase
    db, app = create_firebase_client(config)

    # Prepare the post description
    description = """
    This is a signaling proposal to update Stride’s tokenomics by introducing a buyback and burn mechanism for the STRD token using Stride protocol fees. The mechanism will utilize 85% of Stride’s protocol fee to buy back STRD and send it to a burn address: stride1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqsgqrn3 (See Appendix below for burn address details).


With the current state of protocol fees this would result in approximately 923,000 STRD (1% of current max supply) being bought back and burned per year.


Background


Stride collects a 10% fee on staking rewards generated by tokens liquid staked with the protocol. Since launch, Stride’s annualized protocol fee has fluctuated from $450,000 USD to $5,000,000 USD based on the market valuations of the underlying staked tokens.


Stride governance controls how the protocol uses its protocol fee, and has currently elected to divert the majority of protocol fees directly to STRD stakers, under the justification that this would encourage additional tokens to be staked, increasing Stride’s bonded ratio and overall security.


However, since that time some significant changes have been made to the Stride protocol, including the transition to consuming interchain security from the Cosmos Hub. Since staked STRD tokens no longer actively contribute to the protocol’s security, it is likely that Stride is overpaying for delegated stake. While staking continues to be a valuable service provided by tokenholders due to the governance powers it confers, it makes sense to revisit the protocol fee allocation model to ensure that it benefits the Stride protocol and ecosystem. This is especially true because inflationary STRD emissions will continue to flow to staked STRD.


Rationale


This proposal, if passed, will redirect the current protocol fee allocated to stakers and instead utilize it to buy back and burn STRD.


The current landscape of Stride tokenholders is far more varied than it was when proposal 8 was passed in late 2022. At the time, it felt imperative to encourage a large movement of STRD to stake to help bolster protocol security and reduce the low overall bonding rate. Today, staking remains important for governance, but there are other ecosystem participants that protocol fees could benefit. This includes stakers, LPs, ATOM stakers earning STRD emissions from ICS fees, and more.


Allocating protocol fees toward a token buyback and burn program ensures that all of these stakeholders are rewarded equally. 


Current Protocol Fee Allocation


Currently, Stride’s protocol fee is allocated as follows:



15% to the Cosmos Hub as payment for interchain security (Proposal 201)

85% to Stride governors and STRD stakers (Proposal 8)

5% of this accrues to the Stride community pool (Proposal 223)


Additionally, Stride governance has approved two protocol fee carve outs that share / reduce protocol fees under certain circumstances:



Stride rewards share program (Proposal 246)

dYdX POL fee reduction (Proposal 234)


Proposed Protocol Fee Allocation


This proposal seeks to redirect all of the protocol fees currently allocated toward Stride governors and STRD stakers towards the buying back and burning of STRD. Rather than being liquid staked and distributed, the underlying staking reward token commissions will take the following path:



Step 1: Tokens are sent to Osmosis or other liquid market (may be asset-specific)

Step 2: Tokens are swapped for STRD

Step 3: STRD is IBC transferred back to the Stride chain burn address


This will all be handled non-custodially via Stride’s interchain accounts on the respective host zones, and will closely resemble the current staking reward swapping mechanism employed for stDYDX.


At current prices, this protocol fee use case would result in approximately 923,524 STRD (approximately 1% of the max supply) being bought back and burned per year. This number is purely an estimate based on publicly available data, and is subject to change as protocol fees fluctuate.


The protocol fee allocation if this proposal passes is:



15% to the Cosmos Hub as payment for interchain security

85% used to buy back and burn STRD (protocol fees allocated to the Stride reward share program will first be deducted from this amount).
    """
    # Create post data
    post_data_df = create_post_data(
        id1 = 'aave--test10',
        post_id='aave--test10',
        post_type='snapshot_proposal',
        protocol='aave',
        title='simple title',
        coin='aave',
        timestamp='2024-11-12',
        description=description,
        discussion_link='https://commonwealth.im/stride/discussion/25027-stride-tokenomics-update-allocate-protocol-fees-to-buy-back-and-burn-strd',
        house_id = 'aave',
        created_at = '2024-10-12'
    )

    # Since we need to push it as a dict, convert the DataFrame to dict
    post_data_dict = post_data_df.iloc[0].to_dict()

    # Push the data to Firestore
    push_data_to_firestore(db, 'ai_posts', post_data_dict)

# Run the main function
if __name__ == "__main__":
    main()
