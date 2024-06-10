import requests
import time
import datetime
import telebot
from requests.exceptions import ConnectionError, Timeout

BSCSCAN_API_KEY = 'TVIUM91NNKRRK4797SR65NCUSPS3Q23I8U'
TELEGRAM_BOT_TOKEN = '7414729656:AAFs_O5nM-TqUyQm3L-pYGiK2OuBIp7eIck'
TELEGRAM_CHAT_ID = '-1001994825490'
BNB_RECEIVING_ADDRESS = '0x12E202C2A4DBe522F4388A550070339D27Ed3A38'
USDT_RECEIVING_ADDRESS = '0x32e150a3047F8D4aCD5Ca541F1DA01d158Ccc225'
TOKEN_CONTRACT_ADDRESS = '0xD10c40eae9B675EEAAF20C84E5D274aBC109281F'
USDT_CONTRACT_ADDRESS = '0x55d398326f99059fF775485246999027B3197955'
MATIC_CONTRACT_ADDRESS = '0xCC42724C6683B7E57334c4E856f4c9965ED682bD'
USDC_CONTRACT_ADDRESS = '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d'
TOTAL_RAISED_ADDRESS = '0x32e150a3047F8D4aCD5Ca541F1DA01d158Ccc225'
CHECK_INTERVAL = 5  # Check every 5 seconds
DOTS_PER_BNB = 0.05  # One dot per 0.1 BNB


IMAGE_URL = 'https://i.imgur.com/hDF9XpV.jpeg'

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def send_telegram_message(message, image_url):
    try:
        bot.send_photo(TELEGRAM_CHAT_ID, photo=image_url, caption=message, parse_mode='HTML')
        print(f"Message sent to Telegram: {message}")
    except Exception as e:
        print(f"Failed to send message: {e}")
        
def get_bnb_price():
    url = "https://min-api.cryptocompare.com/data/price?fsym=BNB&tsyms=USD"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return float(data['USD'])
        else:
            print(f"Failed to fetch BNB price, non-200 response: {response.status_code}")
            return None
    except (ConnectionError, Timeout) as e:
        print(f"Failed to fetch BNB price ({e})")
        return None
    

def make_request_with_retries(url, retries=5, backoff_factor=1):
    for i in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                time.sleep(backoff_factor * (2 ** i))  # Exponential backoff
        except (ConnectionError, Timeout):
            time.sleep(backoff_factor * (2 ** i))  # Exponential backoff
    return None


def get_token_transactions(address, token_contract_address, api_key, start_time):
    url = f"https://api.bscscan.com/api?module=account&action=tokentx&contractaddress={token_contract_address}&address={address}&page=1&offset=100&sort=asc&apikey={api_key}"
    transactions = make_request_with_retries(url)
    
    # Debug: Print the entire API response for token transactions
   #print(f"Token transactions API response for address {address}:\n{transactions}")

    if not transactions or transactions['status'] != '1':
        return []

    new_transactions = []
    for tx in transactions['result']:
        tx_time = int(tx['timeStamp'])
        if tx_time >= start_time and tx['to'].lower() == address.lower():
            print(f"New token transaction found: {tx}")  # Debug: Print each found transaction
            new_transactions.append(tx)
    
    return new_transactions

def get_total_bnb_held(address, api_key):
    url = f"https://api.bscscan.com/api?module=account&action=balance&address={address}&apikey={api_key}"
    balance = make_request_with_retries(url)
    if not balance or balance['status'] != '1':
        return 0
    return int(balance['result']) / 10**18

def get_bnb_transactions(address, api_key, start_time):
    url = f"https://api.bscscan.com/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={api_key}"
    transactions = make_request_with_retries(url)
    
    if not transactions or transactions['status'] != '1':
        return []

    new_transactions = []
    for tx in transactions['result']:
        tx_time = int(tx['timeStamp'])
        if tx_time >= start_time and tx['to'].lower() == address.lower() and int(tx['value']) > 0:
            new_transactions.append(tx)
    
    return new_transactions

def get_usdt_transactions(receiving_address, token_contract_address, api_key, start_time):
    url = f"https://api.bscscan.com/api?module=account&action=tokentx&contractaddress={token_contract_address}&address={receiving_address}&page=1&offset=100&sort=asc&apikey={api_key}"
    transactions = make_request_with_retries(url)
    
    if not transactions or transactions['status'] != '1':
        print(f"Failed to fetch USDT transactions or no valid transactions found for {receiving_address}")
        return []

    new_transactions = []
    for tx in transactions['result']:
        tx_time = int(tx['timeStamp'])
        if tx_time >= start_time and tx['to'].lower() == receiving_address.lower():
            new_transactions.append(tx)
    
    return new_transactions

def get_matic_transactions(receiving_address, token_contract_address, api_key, start_time):
    url = f"https://api.bscscan.com/api?module=account&action=tokentx&contractaddress={token_contract_address}&address={receiving_address}&page=1&offset=100&sort=asc&apikey={api_key}"
    transactions = make_request_with_retries(url)
    
    if not transactions or transactions['status'] != '1':
        print(f"Failed to fetch Matic transactions or no valid transactions found for {receiving_address}")
        return []

    new_transactions = []
    for tx in transactions['result']:
        tx_time = int(tx['timeStamp'])
        if tx_time >= start_time and tx['to'].lower() == receiving_address.lower():
            new_transactions.append(tx)
    
    return new_transactions

def get_usdc_transactions(receiving_address, token_contract_address, api_key, start_time):
    url = f"https://api.bscscan.com/api?module=account&action=tokentx&contractaddress={token_contract_address}&address={receiving_address}&page=1&offset=100&sort=asc&apikey={api_key}"
    transactions = make_request_with_retries(url)
    
    if not transactions or transactions['status'] != '1':
        print(f"Failed to fetch USDC transactions or no valid transactions found for {receiving_address}")
        return []

    new_transactions = []
    for tx in transactions['result']:
        tx_time = int(tx['timeStamp'])
        if tx_time >= start_time and tx['to'].lower() == receiving_address.lower():
            new_transactions.append(tx)
    
    return new_transactions

def generate_green_dots(bnb_amount, dots_per_bnb):
    num_dots = int(bnb_amount / dots_per_bnb)
    return '🟢' * num_dots

def monitor_transactions():
    start_time = int(time.time())
    print(f"Monitoring transactions")
    processed_tx_hashes = set()

    while True:
        
        new_bnb_transactions = get_bnb_transactions(BNB_RECEIVING_ADDRESS, BSCSCAN_API_KEY, start_time)
        
        for tx in new_bnb_transactions:
            if tx['hash'] in processed_tx_hashes:
                continue
            
            sender_address = tx['from']
            bnb_amount = int(tx['value']) / 10**18
            get_token_transactions(sender_address, TOKEN_CONTRACT_ADDRESS, BSCSCAN_API_KEY, start_time)

            token_transactions = get_token_transactions(sender_address, TOKEN_CONTRACT_ADDRESS, BSCSCAN_API_KEY, start_time)
            total_tokens_received = 0
            for token_tx in token_transactions:
                tokens_received = int(token_tx['value']) / 10**18
                total_tokens_received += tokens_received
                print(f"Accumulating tokens: {tokens_received} from transaction {token_tx['hash']}")  # Debug: Print each accumulated token amount

           
            total_raised = get_total_bnb_held(TOTAL_RAISED_ADDRESS, BSCSCAN_API_KEY)
            tx_link = f"https://bscscan.com/tx/{tx['hash']}"
            green_dots = generate_green_dots(bnb_amount, DOTS_PER_BNB)
            usd_amount = float(bnb_amount) * get_bnb_price()
            message = (
                "<b>JBC BUY!</b>\n\n"
                f"🟢🟢🟢{green_dots}\n\n"
                f"<b>💰Spent:</b> {bnb_amount:.5f} BNB | (${usd_amount:.3f})\n\n"
                f"<b>🤑Got:</b> {total_tokens_received:,.2f} JBC\n\n"
                f"<b>💳Price per token:</b> $ 0.0000000087\n\n"
                #f"<b>💸Total Raised:</b> {total_raised:.4f} BNB 💵\n\n"
                "🏷️Presale Live At <a href='http://www.junglebookcrypto.com'>www.junglebookcrypto.com</a>\n\n"
                f"<a href='{tx_link}'>TX</a> | <a href='www.junglebookcrypto.com'>Website</a> | <a href='https://x.com/JBC_Hub'>Twitter</a> | <a href='https://t.me/JBChubJBCsmart'>Telegram</a> | <a href='https://acrobat.adobe.com/id/urn:aaid:sc:AP:d7c5c7fb-2a6c-4395-ab18-ed679a717723'>WhitePaper</a>"
            )
            
            #print(message)
            send_telegram_message(message, IMAGE_URL)
            #response = bot.send_photo(TELEGRAM_CHAT_ID, photo=IMAGE_URL, caption=message, parse_mode='HTML')
            print(message)
            #bot.send_message(TELEGRAM_CHAT_ID, message)
            print("sent message")
            start_time = int(time.time())
            #print(response)
            processed_tx_hashes.add(tx['hash'])
            
            # USDT Transactions
        
        new_usdt_transactions = get_usdt_transactions(USDT_RECEIVING_ADDRESS, USDT_CONTRACT_ADDRESS, BSCSCAN_API_KEY, start_time)
        
        for tx in new_usdt_transactions:
            if tx['hash'] in processed_tx_hashes:
                continue
            
            sender_address = tx['from']
            usdt_amount = int(tx['value']) / 10**18
            get_token_transactions(sender_address, TOKEN_CONTRACT_ADDRESS, BSCSCAN_API_KEY, start_time)

            token_transactions = get_token_transactions(sender_address, TOKEN_CONTRACT_ADDRESS, BSCSCAN_API_KEY, start_time)
            total_tokens_received = 0
            for token_tx in token_transactions:
                tokens_received = int(token_tx['value']) / 10**18
                total_tokens_received += tokens_received
                print(f"Accumulating tokens: {tokens_received} from transaction {token_tx['hash']}")  # Debug: Print each accumulated token amount

        
            #total_raised = get_total_bnb_held(TOTAL_RAISED_ADDRESS, BSCSCAN_API_KEY)
            tx_link = f"https://bscscan.com/tx/{tx['hash']}"
            green_dots = generate_green_dots(usdt_amount, DOTS_PER_BNB)
            usd_amount = usdt_amount
            message = (
                "<b>JBC BUY!</b>\n\n"
                f"🟢🟢🟢{green_dots}\n\n"
                f"<b>💰Spent:</b> {usdt_amount:.5f} USDT \n\n"
                f"<b>🤑Got:</b> {total_tokens_received:,.2f} JBC\n\n"
                f"<b>💳Price per token:</b> $ 0.0000000087\n\n"
                #f"<b>💸Total Raised:</b> {total_raised:.4f} BNB 💵\n\n"
                "🏷️Presale Live At <a href='http://www.junglebookcrypto.com'>www.junglebookcrypto.com</a>\n\n"
                f"<a href='{tx_link}'>TX</a> | <a href='www.junglebookcrypto.com'>Website</a> | <a href='https://x.com/JBC_Hub'>Twitter</a> | <a href='https://t.me/JBChubJBCsmart'>Telegram</a> | <a href='https://acrobat.adobe.com/id/urn:aaid:sc:AP:d7c5c7fb-2a6c-4395-ab18-ed679a717723'>WhitePaper</a>"
            )
            
     
            send_telegram_message(message, IMAGE_URL)
            #bot.send_message(TELEGRAM_CHAT_ID, message)
            print("sent message")
            start_time = int(time.time())
            processed_tx_hashes.add(tx['hash'])
        #MATIC Part
        
        new_matic_transactions = get_matic_transactions(USDT_RECEIVING_ADDRESS, MATIC_CONTRACT_ADDRESS, BSCSCAN_API_KEY, start_time)
        
        for tx in new_matic_transactions:
            if tx['hash'] in processed_tx_hashes:
                continue
            
            sender_address = tx['from']
            matic_amount = int(tx['value']) / 10**18
            get_token_transactions(sender_address, TOKEN_CONTRACT_ADDRESS, BSCSCAN_API_KEY, start_time)

            token_transactions = get_token_transactions(sender_address, TOKEN_CONTRACT_ADDRESS, BSCSCAN_API_KEY, start_time)
            total_tokens_received = 0
            for token_tx in token_transactions:
                tokens_received = int(token_tx['value']) / 10**18
                total_tokens_received += tokens_received
                print(f"Accumulating tokens: {tokens_received} from transaction {token_tx['hash']}")  # Debug: Print each accumulated token amount

        
            #total_raised = get_total_bnb_held(TOTAL_RAISED_ADDRESS, BSCSCAN_API_KEY)
            tx_link = f"https://bscscan.com/tx/{tx['hash']}"
            green_dots = generate_green_dots(matic_amount, DOTS_PER_BNB)
            message = (
                "<b>JBC BUY!</b>\n\n"
                f"🟢🟢🟢{green_dots}\n\n"
                f"<b>💰Spent:</b> {matic_amount:.5f} MATIC]\n\n"
                f"<b>🤑Got:</b> {total_tokens_received:,.2f} JBC\n\n"
                f"<b>💳Price per token:</b> $ 0.0000000087\n\n"
                #f"<b>💸Total Raised:</b> {total_raised:.4f} BNB 💵\n\n"
                "🏷️Presale Live At <a href='http://www.junglebookcrypto.com'>www.junglebookcrypto.com</a>\n\n"
                f"<a href='{tx_link}'>TX</a> | <a href='www.junglebookcrypto.com'>Website</a> | <a href='https://x.com/JBC_Hub'>Twitter</a> | <a href='https://t.me/JBChubJBCsmart'>Telegram</a> | <a href='https://acrobat.adobe.com/id/urn:aaid:sc:AP:d7c5c7fb-2a6c-4395-ab18-ed679a717723'>WhitePaper</a>"
            )
            
     
            send_telegram_message(message, IMAGE_URL)
            #bot.send_message(TELEGRAM_CHAT_ID, message)
            print("sent message")
            start_time = int(time.time())
            processed_tx_hashes.add(tx['hash'])
            
        #USDC Part
        new_usdc_transactions = get_usdc_transactions(USDT_RECEIVING_ADDRESS, USDC_CONTRACT_ADDRESS, BSCSCAN_API_KEY, start_time)
        
        for tx in new_usdc_transactions:
            if tx['hash'] in processed_tx_hashes:
                continue
            
            sender_address = tx['from']
            usdc_amount = int(tx['value']) / 10**18
            get_token_transactions(sender_address, TOKEN_CONTRACT_ADDRESS, BSCSCAN_API_KEY, start_time)

            token_transactions = get_token_transactions(sender_address, TOKEN_CONTRACT_ADDRESS, BSCSCAN_API_KEY, start_time)
            total_tokens_received = 0
            for token_tx in token_transactions:
                tokens_received = int(token_tx['value']) / 10**18
                total_tokens_received += tokens_received
                print(f"Accumulating tokens: {tokens_received} from transaction {token_tx['hash']}")  # Debug: Print each accumulated token amount

        
            #total_raised = get_total_bnb_held(TOTAL_RAISED_ADDRESS, BSCSCAN_API_KEY)
            tx_link = f"https://bscscan.com/tx/{tx['hash']}"
            print(tx_link)
            green_dots = generate_green_dots(usdc_amount, DOTS_PER_BNB)
            message = (
                "<b>JBC BUY!</b>\n\n"
                f"🟢🟢🟢{green_dots}\n\n"
                f"<b>💰Spent:</b> {usdc_amount:.5f} USDC]\n\n"
                f"<b>🤑Got:</b> {total_tokens_received:,.2f} JBC\n\n"
                f"<b>💳Price per token:</b> $ 0.0000000087\n\n"
                #f"<b>💸Total Raised:</b> {total_raised:.4f} BNB 💵\n\n"
                "🏷️Presale Live At <a href='http://www.junglebookcrypto.com'>www.junglebookcrypto.com</a>\n\n"
                f"<a href='{tx_link}'>TX</a> | <a href='www.junglebookcrypto.com'>Website</a> | <a href='https://x.com/JBC_Hub'>Twitter</a> | <a href='https://t.me/JBChubJBCsmart'>Telegram</a> | <a href='https://acrobat.adobe.com/id/urn:aaid:sc:AP:d7c5c7fb-2a6c-4395-ab18-ed679a717723'>WhitePaper</a>"
            )
            
     
            send_telegram_message(message, IMAGE_URL)
            #bot.send_message(TELEGRAM_CHAT_ID, message)
            print("sent message")
            start_time = int(time.time())
            processed_tx_hashes.add(tx['hash'])

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    while True:
        try:
            monitor_transactions()
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(5)  # Wait a bit before restarting
