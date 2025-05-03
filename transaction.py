import datetime
import plaid
from plaid.api import plaid_api
from plaid.model.transactions_sync_request import TransactionsSyncRequest
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
        "user": {"client_user_id": "user123"},
        "client_name": "Hackathon Bank Tracker",
        "products": ["transactions"],
        "country_codes": ["US"],
        "language": "en",
        "webhook": "https://addtransaction.com/plaid-webhook"
    })
    print("🔗 Link token généré:", response["link_token"])
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
        print(f"webhook error: {e}")
    
    return access_token

def refresh_transactions(access_token):
    try:
        response = client.sandbox_item_fire_webhook({
            "access_token": access_token,
            "webhook_code": "SYNC_UPDATES_AVAILABLE"
        })
        print("   Status:", "Succes" if response.get('webhook_fired') else "failure")
        print("fetching...")
        time.sleep(2)  
    except plaid.exceptions.ApiException as e:
        print(f"❌ Erreur lors du rafraîchissement des transactions : {e}")
        print(f"   Message d'erreur: {e.body}")

def get_account_info(access_token):
    try:
        response = client.accounts_get({
            'access_token': access_token
        })
        accounts = response['accounts']
        print(f"📊 Informations sur les comptes connectés:")
        for account in accounts:
            print(f"  • {account['name']} ({account['official_name'] or 'N/A'})")
            print(f"    Type: {account['type']}, Sous-type: {account['subtype']}")
            print(f"    Solde disponible: {account.get('balances', {}).get('available', 'N/A')}")
            print(f"    Solde actuel: {account.get('balances', {}).get('current', 'N/A')}")
            print()
        return accounts
    except plaid.exceptions.ApiException as e:
        print(f"Erreur lors de la récupération des comptes: {e}")
        return []

def get_transactions(access_token, max_retries=3, wait_time=5):
    retries = 0
    while retries <= max_retries:
        try:
            request = TransactionsSyncRequest(
                access_token=access_token,
            )
            response = client.transactions_sync(request)
            
            print(f"État initial de la réponse sync:")
            print(f"  • Transactions ajoutées: {len(response['added'])}")
            print(f"  • Y a-t-il plus de transactions? {response['has_more']}")
            
            transactions = response['added']

            while response['has_more']:
                print(f"Récupération de transactions supplémentaires avec cursor: {response['next_cursor'][:20]}...")
                request = TransactionsSyncRequest(
                    access_token=access_token,
                    cursor=response['next_cursor']
                )
                response = client.transactions_sync(request)
                print(f"  • Nouvelles transactions ajoutées: {len(response['added'])}")
                transactions += response['added']

            print(f"📄 {len(transactions)} transactions reçues au total")
            
            if len(transactions) == 0:
                print("⚠️ Aucune transaction trouvée. Il est possible que:")
                print("  1. Les transactions ne soient pas encore disponibles dans le compte sandbox")
                print("  2. L'institution bancaire simulée n'a pas de transactions d'exemple")
                print("  3. Vous utilisez un compte de test qui n'a pas été configuré avec des transactions")
            else:
                print("\nTransactions:")
                for t in transactions:
                    try:
                        category = t.category[0] if t.category and len(t.category) > 0 else "Non catégorisé"
                        print(f"{t.date} | {t.name} | {t.amount} USD | {category}")
                    except Exception as e:
                        print(f"{t.date} | {t.name} | {t.amount} USD | Erreur d'affichage: {e}")
            
            return transactions
            
        except plaid.exceptions.ApiException as e:
            try:
                # Utiliser json.loads au lieu de eval pour parser la réponse
                error_data = json.loads(e.body)
                error_code = error_data.get("error_code", "")
                
                if error_code == "PRODUCT_NOT_READY":
                    retries += 1
                    if retries <= max_retries:
                        print(f"Les transactions ne sont pas encore prêtes. Attente de {wait_time} secondes (tentative {retries}/{max_retries})...")
                        time.sleep(wait_time)
                    else:
                        print("Délai d'attente dépassé pour la récupération des transactions.")
                        return []
                elif error_code == "TRANSACTIONS_SYNC_MUTATION_DURING_PAGINATION":
                    print("❗ Les données ont changé pendant la pagination. Redémarrage de la synchronisation...")
                    retries += 1
                    time.sleep(2)  # Court délai avant de réessayer
                else:
                    print(f"Erreur Plaid: {error_code}")
                    print(f"Message: {error_data.get('error_message', '')}")
                    return []
            except Exception as parse_error:
                print(f"Erreur lors de l'analyse de la réponse d'erreur: {parse_error}")
                print(f"Corps de la réponse: {e.body}")
                return []

if __name__ == "__main__":
    link_token = create_link_token()
    access_token = get_access_token()
    
    print("\nRécupération des informations sur les comptes...")
    accounts = get_account_info(access_token)

    print("\n💾 Demande de rafraîchissement des transactions (sandbox)...")
    refresh_transactions(access_token)

    print("\n📥 Récupération des transactions. Cela peut prendre quelques instants...")
    transactions = get_transactions(access_token, max_retries=5, wait_time=10)

    print("\n=== Résumé ===")
    print(f"Comptes connectés: {len(accounts)}")
    print(f"Transactions récupérées: {len(transactions)}")
