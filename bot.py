import requests
import time
import datetime
import telebot
from requests.exceptions import ConnectionError, Timeout

BSCSCAN_API_KEY = 'TVIUM91NNKRRK4797SR65NCUSPS3Q23I8U'
TELEGRAM_BOT_TOKEN = '7455382251:AAEFG2OiZIAgorzeKKJ5Lv8a9_OmG05ww7Q'
TELEGRAM_CHAT_ID = '-4271464527'
BNB_RECEIVING_ADDRESS = '0x12E202C2A4DBe522F4388A550070339D27Ed3A38'
TOKEN_CONTRACT_ADDRESS = '0xD10c40eae9B675EEAAF20C84E5D274aBC109281F'
TOTAL_RAISED_ADDRESS = '0x32e150a3047F8D4aCD5Ca541F1DA01d158Ccc225'
CHECK_INTERVAL = 5  # Check every 5 seconds
DOTS_PER_BNB = 0.0005  # One dot per 0.1 BNB

IMAGE_URL = 'https://i.imgur.com/M0WbNyC.jpeg'

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def send_telegram_message(message, image_url):
    bot.send_photo(TELEGRAM_CHAT_ID, photo=image_url, caption=message, parse_mode='HTML')

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

def get_token_transactions(address, token_contract_address, api_key, start_time):
    url = f"https://api.bscscan.com/api?module=account&action=tokentx&contractaddress={token_contract_address}&address={address}&page=1&offset=100&sort=asc&apikey={api_key}"
    transactions = make_request_with_retries(url)
    
    if not transactions or transactions['status'] != '1':
        return []

    new_transactions = []
    for tx in transactions['result']:
        tx_time = int(tx['timeStamp'])
        if tx_time >= start_time and tx['to'].lower() == address.lower():
            new_transactions.append(tx)
    
    return new_transactions

def get_total_bnb_held(address, api_key):
    url = f"https://api.bscscan.com/api?module=account&action=balance&address={address}&apikey={api_key}"
    balance = make_request_with_retries(url)
    if not balance or balance['status'] != '1':
        return 0
    return int(balance['result']) / 10**18

def generate_green_dots(bnb_amount, dots_per_bnb):
    num_dots = int(bnb_amount / dots_per_bnb)
    return '🟢' * num_dots

def monitor_transactions():
    start_time = int(time.time())
    print(f"Monitoring transactions from {datetime.datetime.fromtimestamp(start_time)}...")
    processed_tx_hashes = set()

    while True:
        new_bnb_transactions = get_bnb_transactions(BNB_RECEIVING_ADDRESS, BSCSCAN_API_KEY, start_time)
        
        for tx in new_bnb_transactions:
            if tx['hash'] in processed_tx_hashes:
                continue
            
            sender_address = tx['from']
            bnb_amount = int(tx['value']) / 10**18

            token_transactions = get_token_transactions(sender_address, TOKEN_CONTRACT_ADDRESS, BSCSCAN_API_KEY, start_time)
            total_tokens_received = 0
            for token_tx in token_transactions:
                tokens_received = int(token_tx['value']) / 10**18
                total_tokens_received += tokens_received

            price_per_token = bnb_amount / total_tokens_received if total_tokens_received > 0 else 0
            total_raised = get_total_bnb_held(TOTAL_RAISED_ADDRESS, BSCSCAN_API_KEY)
            tx_link = f"https://bscscan.com/tx/{tx['hash']}"
            green_dots = generate_green_dots(bnb_amount, DOTS_PER_BNB)

            message = (
                "<b>JBC BUY!</b>\n\n"
                f"🟢🟢🟢{green_dots}\n\n"
                f"<b>💰Spent:</b> {bnb_amount:.5f} BNB\n\n"
                f"<b>🤑Got:</b> {total_tokens_received:,.2f} JBC\n\n"
                f"<b>💳Price per token:</b> {price_per_token:.10f} BNB⚡\n\n"
                f"<b>💸Total Raised:</b> {total_raised:.4f} BNB 💵\n\n"
                "🏷️Presale Live At <a href='http://www.junglebookcrypto.com'>www.junglebookcrypto.com</a>\n\n"
                f"<a href='{tx_link}'>TX</a> | <a href='www.junglebookcrypto.com'>Website</a> | <a href='https://x.com/JBC_Hub'>Twitter</a> | <a href='https://t.me/JBChubJBCsmart'>Telegram</a> | <a href='https://acrobat.adobe.com/id/urn:aaid:sc:AP:d7c5c7fb-2a6c-4395-ab18-ed679a717723'>WhitePaper</a>"
            )

            send_telegram_message(message, IMAGE_URL)
            processed_tx_hashes.add(tx['hash'])

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_transactions()
