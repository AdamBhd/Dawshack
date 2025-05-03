import datetime
import plaid
from plaid.api import plaid_api
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.sandbox_item_fire_webhook_request import SandboxItemFireWebhookRequest
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
import time
import json

client_id = "6816235ac1a0a80023f099d4"
secret = "ae984027995b66267f0b10b378242b"
plaid_env = "sandbox"

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': client_id,
        'secret': secret,
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

def create_link_token():
    response = client.link_token_create({
        "user": {"client_user_id": "user_good"},
        "client_name": "Hackathon Bank Tracker",
        "products": ["transactions"],
        "country_codes": ["US"],
        "language": "en",
        "webhook": "https://addtransaction.com/plaid-webhook"
    })
    return response["link_token"]

def get_access_token():
    response = client.sandbox_public_token_create({
        "institution_id": "ins_109508",  
        "initial_products": ["transactions"],
        "options": {
            "transactions": {
                "start_date": (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
            }
        }
    })
    public_token = response["public_token"]

    exchange = client.item_public_token_exchange({
        "public_token": public_token
    })
    access_token = exchange["access_token"]
    
    try:
        client.item_webhook_update({
            "access_token": access_token,
            "webhook": "https://addtransaction.com/plaid-webhook"
        })
    except plaid.exceptions.ApiException as e:
        pass
    
    return access_token

def refresh_transactions(access_token):
    try:
        response = client.sandbox_item_fire_webhook({
            "access_token": access_token,
            "webhook_code": "SYNC_UPDATES_AVAILABLE"
        })
        time.sleep(2)  
    except plaid.exceptions.ApiException as e:
        pass

def get_account_info(access_token):
    try:
        response = client.accounts_get({
            'access_token': access_token
        })
        accounts = response['accounts']
        return accounts
    except plaid.exceptions.ApiException as e:
        return []

def get_transactions(access_token, max_retries=3, wait_time=10):
    retries = 0
    while retries <= max_retries:
        try:
            request = TransactionsSyncRequest(
                access_token=access_token,
            )
            response = client.transactions_sync(request)
            
            transactions = response['added']

            while response['has_more']:
                request = TransactionsSyncRequest(
                    access_token=access_token,
                    cursor=response['next_cursor']
                )
                response = client.transactions_sync(request)
                transactions += response['added']
            
            return transactions
            
        except plaid.exceptions.ApiException as e:
            try:
                error_data = json.loads(e.body)
                error_code = error_data.get("error_code", "")
                
                if error_code == "PRODUCT_NOT_READY":
                    retries += 1
                    if retries <= max_retries:
                        time.sleep(wait_time)
                    else:
                        return []
                elif error_code == "TRANSACTIONS_SYNC_MUTATION_DURING_PAGINATION":
                    retries += 1
                    time.sleep(2)
                else:
                    return []
            except Exception as parse_error:
                return []

if __name__ == "__main__":
    link_token = create_link_token()
    access_token = get_access_token()
    
    refresh_transactions(access_token)
    transactions = get_transactions(access_token, max_retries=5, wait_time=10)
    
    print("Transactions:")
    for transaction in transactions:
        print(f"Date: {transaction['date']}, ammount: {transaction['amount']}, Description: {transaction['name']}, , Category: {transaction['category']}")
