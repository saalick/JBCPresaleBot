import requests
import time
import datetime
import telebot
from requests.exceptions import ConnectionError, Timeout

# Constants
BSCSCAN_API_KEY = 'TVIUM91NNKRRK4797SR65NCUSPS3Q23I8U'
TELEGRAM_BOT_TOKEN = '7414729656:AAFs_O5nM-TqUyQm3L-pYGiK2OuBIp7eIck'
TELEGRAM_CHAT_ID = '-1001994825490'
BNB_RECEIVING_ADDRESS = '0x12E202C2A4DBe522F4388A550070339D27Ed3A38'
USDT_RECEIVING_ADDRESS = '0x32e150a3047F8D4aCD5Ca541F1DA01d158Ccc225'
TOKEN_SENDING_ADDRESS = '0x12E202C2A4DBe522F4388A550070339D27Ed3A38'
TOKEN_CONTRACT_ADDRESS = '0xD10c40eae9B675EEAAF20C84E5D274aBC109281F'
USDT_CONTRACT_ADDRESS = '0x55d398326f99059fF775485246999027B3197955'
CHECK_INTERVAL = 5  # Check every 5 seconds
DOTS_PER_BNB = 0.5  # One dot per 0.1 BNB


IMAGE_URL = 'https://i.imgur.com/M0WbNyC.jpeg'

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def send_telegram_message(message, image_url):
    print("Sending message to Telegram...")
    bot.send_photo(TELEGRAM_CHAT_ID, photo=image_url, caption=message, parse_mode='HTML')

def make_request_with_retries(url, retries=5, backoff_factor=1):
    for i in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"Request successful: {url}")
                return response.json()
            else:
                print(f"Non-200 response: {response.status_code} for {url}")
                time.sleep(backoff_factor * (2 ** i))  # Exponential backoff
        except (ConnectionError, Timeout) as e:
            print(f"Request failed ({e}): {url}")
            time.sleep(backoff_factor * (2 ** i))  # Exponential backoff
    return None

def get_bnb_transactions(address, api_key, start_time):
    url = f"https://api.bscscan.com/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={api_key}"
    transactions = make_request_with_retries(url)
    
    if not transactions or transactions['status'] != '1':
        print(f"Failed to fetch BNB transactions or no valid transactions found for {address}")
        return []

    new_transactions = []
    for tx in transactions['result']:
        tx_time = int(tx['timeStamp'])
        if tx_time >= start_time and tx['to'].lower() == address.lower() and int(tx['value']) > 0:
            print(f"New BNB transaction found: {tx}")
            new_transactions.append(tx)
    
    return new_transactions

def get_token_transactions(address, token_contract_address, api_key, start_time):
    url = f"https://api.bscscan.com/api?module=account&action=tokentx&contractaddress={token_contract_address}&address={address}&page=1&offset=100&sort=asc&apikey={api_key}"
    transactions = make_request_with_retries(url)
    
    if not transactions or transactions['status'] != '1':
        print(f"Failed to fetch token transactions or no valid transactions found for {address}")
        return []

    new_transactions = []
    for tx in transactions['result']:
        tx_time = int(tx['timeStamp'])
        if tx_time >= start_time and tx['from'].lower() == address.lower():
            print(f"New token transaction found: {tx}")
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
            print(f"New USDT transaction found: {tx}")
            new_transactions.append(tx)
    
    return new_transactions

def get_bnb_price():
    url = "https://min-api.cryptocompare.com/data/price?fsym=BNB&tsyms=USD"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"Fetched BNB price: {data['USD']} USD")
            return float(data['USD'])
        else:
            print(f"Failed to fetch BNB price, non-200 response: {response.status_code}")
            return None
    except (ConnectionError, Timeout) as e:
        print(f"Failed to fetch BNB price ({e})")
        return None

def generate_green_dots(amount, dots_per_unit):
    num_dots = int(amount / dots_per_unit)
    print(f"Generated {num_dots} green dots for amount: {amount}")
    return '🟢' * num_dots

def monitor_transactions():
    start_time = int(time.time())
    print(f"Monitoring transactions from {datetime.datetime.fromtimestamp(start_time)}...")
    processed_tx_hashes = set()

    while True:
        bnb_price = get_bnb_price()
        if bnb_price is None:
            print("Failed to fetch BNB price. Retrying...")
            time.sleep(CHECK_INTERVAL)
            continue

        # BNB Transactions
        new_bnb_transactions = get_bnb_transactions(BNB_RECEIVING_ADDRESS, BSCSCAN_API_KEY, start_time)
        
        for tx in new_bnb_transactions:
            if tx['hash'] in processed_tx_hashes:
                continue

            sender_address = tx['from']
            bnb_amount = float(int(tx['value']) / 10**18)
            print(f"Processing BNB transaction from {sender_address} of {bnb_amount} BNB")

            token_transactions = get_token_transactions(TOKEN_SENDING_ADDRESS, TOKEN_CONTRACT_ADDRESS, BSCSCAN_API_KEY, start_time)
            total_tokens_received = 0
            for token_tx in token_transactions:
                if token_tx['to'].lower() == sender_address.lower():
                    tokens_received = int(token_tx['value']) / 10**18
                    total_tokens_received += tokens_received
                    print(f"Token transaction found: {tokens_received} tokens sent to {sender_address}")

            
            

            tx_link = f"https://bscscan.com/tx/{tx['hash']}"
            green_dots = generate_green_dots(bnb_amount, DOTS_PER_BNB)
            usd_amount = bnb_amount * bnb_price
            message = (
                "<b>JBC BUY!</b>\n\n"
                f"🟢🟢🟢🟢{green_dots}\n\n"
                f"<b>💰Spent:</b> {bnb_amount:.5f} BNB | (${usd_amount:.3f})\n\n"
                f"<b>🤑Got:</b> {total_tokens_received:,.2f} JBC\n\n"
                f"<b>💳Price per token:</b> $0.0000000087 \n\n"
                "🏷️Presale Live At <a href='http://www.junglebookcrypto.com'>www.junglebookcrypto.com</a>\n\n"
                f"<a href='{tx_link}'>TX</a> | <a href='www.junglebookcrypto.com'>Website</a> | <a href='https://x.com/JBC_Hub'>Twitter</a> | <a href='https://t.me/JBChubJBCsmart'>Telegram</a> | <a href='https://acrobat.adobe.com/id/urn:aaid:sc:AP:d7c5c7fb-2a6c-4395-ab18-ed679a717723'>WhitePaper</a>"
            )

            send_telegram_message(message, IMAGE_URL)
            processed_tx_hashes.add(tx['hash'])

        # USDT Transactions
        new_usdt_transactions = get_usdt_transactions(USDT_RECEIVING_ADDRESS, USDT_CONTRACT_ADDRESS, BSCSCAN_API_KEY, start_time)
        
        for tx in new_usdt_transactions:
            print(f"Processing USDT Transaction: {tx['hash']}")
            if tx['hash'] in processed_tx_hashes:
                continue

            sender_address = tx['from']
            usdt_amount = float(int(tx['value']) / 10**18)  # USDT has 18 decimal places
            print(f"Processing USDT transaction from {sender_address} of {usdt_amount} USDT")

            token_transactions = get_token_transactions(TOKEN_SENDING_ADDRESS, TOKEN_CONTRACT_ADDRESS, BSCSCAN_API_KEY, start_time)
            total_tokens_received = 0
            for token_tx in token_transactions:
                if token_tx['to'].lower() == sender_address.lower():
                    tokens_received = int(token_tx['value']) / 10**18
                    total_tokens_received += tokens_received
                    print(f"Token transaction found: {tokens_received} tokens sent to {sender_address}")

            

            tx_link = f"https://bscscan.com/tx/{tx['hash']}"
            green_dots = generate_green_dots(usdt_amount, DOTS_PER_BNB)
            usd_amount = usdt_amount  # 1 USDT = 1 USD
            message = (
                "<b>JBC BUY!</b>\n\n"
                f"🟢🟢🟢🟢{green_dots}\n\n"
                f"<b>💰Spent:</b> {usdt_amount:.2f} USDT | (${usd_amount:.2f})\n\n"
                f"<b>🤑Got:</b> {total_tokens_received:,.2f} JBC\n\n"
                f"<b>💳Price per token:</b> $0.0000000087 \n\n"
                "🏷️Presale Live At <a href='http://www.junglebookcrypto.com'>www.junglebookcrypto.com</a>\n\n"
                f"<a href='{tx_link}'>TX</a> | <a href='www.junglebookcrypto.com'>Website</a> | <a href='https://x.com/JBC_Hub'>Twitter</a> | <a href='https://t.me/JBChubJBCsmart'>Telegram</a> | <a href='https://acrobat.adobe.com/id/urn:aaid:sc:AP:d7c5c7fb-2a6c-4395-ab18-ed679a717723'>WhitePaper</a>"
            )

            send_telegram_message(message, IMAGE_URL)
            processed_tx_hashes.add(tx['hash'])

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_transactions()
