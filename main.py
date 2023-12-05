import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os

# Telegram bot credentials
bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')  # Environment variable for bot token
chat_id = os.environ.get('TELEGRAM_CHAT_ID')  # Environment variable for chat id

telegram_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

# User's wallet address and chain
users = [
    {'address': 'CDQqYJqbQofae4sCFvcw4JK1TEvuknU1cbnq192LQ3qz', 'chain': 'solana'} #example test address
    # Add more user dictionaries here...
]

# Function to check transactions and notify
def check_transactions_and_notify(user, chain, last_notified_time):
    url = f"https://api.solscan.io/v2/account/transaction?address={user}&cluster="
    headers = {'User-Agent': 'Mozilla/5.0 ... Safari/537.3'}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"API error: {response.status_code}")
        return last_notified_time

    data = response.json().get('data', [])
    new_transactions = []
    latest_tx_time = last_notified_time

    for tx in data:
        tx_time = datetime.utcfromtimestamp(tx.get('blockTime', 0))
        if tx_time > last_notified_time and tx_time > datetime.utcnow() - timedelta(minutes=15):
            new_transactions.append(tx.get('txHash'))
            if tx_time > latest_tx_time:
                latest_tx_time = tx_time

    if new_transactions:
        send_notification(user, chain, new_transactions)
    else:
        print(f"No new activity detected for {user} on {chain}")

    return latest_tx_time

# Function to send notification
def send_notification(user, chain, transactions):
    message = f"{user} has made {len(transactions)} new activities on {chain}. Check it out: https://birdeye.so/profile/{user}?chain={chain}"
    payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
    response = requests.post(telegram_api_url, data=payload)
    if response.status_code != 200:
        print("Failed to send message", response.text)

# Main execution loop
def main():
    last_notified = {user['address']: datetime.min for user in users}
    while True:
        for user_info in users:
            last_notified[user_info['address']] = check_transactions_and_notify(
                user_info['address'], user_info['chain'], last_notified[user_info['address']])
        time.sleep(900)  # Wait for 15 minutes before checking again

if __name__ == "__main__":
    main()
