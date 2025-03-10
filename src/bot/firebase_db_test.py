import pandas as pd 
import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
from suppress_logging import SuppressLogging
from google.api_core.retry import Retry

# Load configuration
with open('config.json', 'r') as json_file:
    config = json.load(json_file)

# Function to initialize Firebase client
def create_firebase_client():
    cred = credentials.Certificate(config["firebase_cred"])
    app = firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db, app  # Return both the Firestore client and app instance

# Initialize Firestore
db, app = create_firebase_client()


# Data to insert
post_data = {
    "post_id": "pankcakeswap--2145cf60ef0265f02dffe5bb09ed3648d905174988c52152861c31d4f4c706934kris1",
    "id": "pankcakeswap--2145cf60ef0265f02dffe5bb09ed3648d905174988c52152861c31d4f4c706934kris1",
    "forum": "discourse_67",
    "created_at": "2025-03-10T14:48:24+05:30",
    "author": "Gandalf",
    "title": "Enable brBTC/BTCB (0.05% fee tier) V3 gauge on BNB Chain",
    "description": """
    <h2><a name="p-2164-overview-1" class="anchor" href="#p-2164-overview-1"></a>Overview</h2> <ul> <li>Proposal to enable brBTC/BTCB 0.05% V3 gauge on BNB Chain.</li> </ul> <h2><a name="p-2164-background-2" class="anchor" href="#p-2164-background-2"></a>Background</h2> <ul> <li> <p>Bedrock is a pioneering multi-asset restaking protocol supporting BTC, ETH, and IOTX, enabling users to unlock impressive yields—some exceeding three digits—while maintaining asset exposure. Backed by top investors, including OKX Ventures, Longhash, Comma3 Ventures, and Waterdrip Capital, Bedrock ensures robust security through audits by PeckShield and Blocksec.</p> </li> <li> <p>As Babylon’s first liquid restaking partner, Bedrock introduced uniBTC, the first Bitcoin LRT, setting a historic precedent in DeFi.</p> </li> <li> <p>Bedrock has a TVL of $600m with over 200,000 users, and is partnered with most of the major DeFi players including OKX, Curve, Balancer, Pendle, Amber, Chainlink, Penpie, Equilibria, Corn, Arbitrum, Optimism, Mode, Mantle, SatLayer, Binance Chain, Babylon, BOB, Avalon, Camelot, Velodrome, and many others.</p> </li> </ul> <h2><a name="p-2164-details-3" class="anchor" href="#p-2164-details-3"></a>Details</h2> <ol> <li> <p>**[Boost Multiplier and Emission Cap % ]<br> 1.00x boost multiplier and 0.5% emission cap</p> </li> <li> <p><strong>Audits</strong>:<br> <a href="https://docs.bedrock.technology/security/audit-reports" rel="noopener nofollow ugc">Audit reports of brBTC &amp; uniBTC</a></p> </li> <li> <p><strong>Token Utility</strong>:<br> uniBTC is minted from BTCB &amp; fBTC on BNB Chain, pegged 1:1 to BTC<br> brBTC is minted from fBTC, m-BTC, BTCB, and uniBTC. and is also pegged 1:1 to BTC.</p> </li> <li> <p><strong>Volatility</strong>:<br> uniBTC unstake is already live and brBTC unstaking will be live in the near future as well, so users may redeem either token back to BTCB, fBTC, or in brBTC’s case, m-BTC 1:1.</p> </li> <li> <p><strong>Oracles</strong>:<br> We’re working with Chainlink for <a href="https://data.chain.link/feeds/ethereum/mainnet/unibtc-por" rel="noopener nofollow ugc">Proof of Reserve</a>, and the uniBTC vault can also be checked here: <a href="https://bscscan.com/address/0x84E5C854A7fF9F49c888d69DECa578D406C26800" rel="noopener nofollow ugc">0x84E5C854A7fF9F49c888d69DECa578D406C26800</a></p> </li> <li> <p><strong>Control</strong>:<br> 0xf940230a3357971fe0F22E8C144BC70d9fA91d43</p> </li> <li> <p><strong>Merit</strong>: How will this proposal benefit PancakeSwap (fees, marketing, users, etc.)?<br> Bedrock offers a robust Diamond points system for all uniBTC &amp; brBTC holders and LPs. In addition, Bedrock has plans to bribe the pool to boost engagement and growth.</p> </li> <li> <p><strong>Vault Strategy (for Position Managers only)</strong>: What strategy does the vault use? Broadly, how does it work? Please share documentation if possible</p> </li> </ol> <h2><a name="p-2164-links-4" class="anchor" href="#p-2164-links-4">
    """,
    "post_type" : "snapshot_proposal",
    "house_id" : "aave",
    "coin" : "aave"
}

# Insert data into Firestore
collection_name = "ai_posts"
try:
    doc_ref = db.collection(collection_name).document(post_data["post_id"])
    doc_ref.set(post_data)
    print(f"Post {post_data['post_id']} successfully added to Firestore in collection '{collection_name}'.")
except Exception as e:
    print(f"Error inserting data: {e}")
    
    
    
# Function to fetch and display document fields from Firestore
def get_collection_fields(collection_name, limit=1):
    try:
        # Fetch one document from the collection
        docs = db.collection(collection_name).limit(limit).stream()
        
        for doc in docs:
            data = doc.to_dict()
            print("Fields in the document:")
            for key in data.keys():
                print(f"- {key}")
            
            return data.keys()  # Return list of field names
        
        print(f"No documents found in the '{collection_name}' collection.")
        return None
    except Exception as e:
        print(f"Error fetching collection fields: {e}")
        return None
    
collection_name = "ai_posts"
fields = get_collection_fields(collection_name)
