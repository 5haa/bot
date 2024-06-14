from flask import Flask, request, jsonify
import requests
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global dictionary to store user balances
user_balances = {}

# Telegram bot token
TELEGRAM_BOT_TOKEN = '7338701081:AAFAkZI1Jo0K3j8woT_fhunwGnpo90XnaUg'

def send_confirmation(user_id: int, amount: float) -> None:
    """Send a confirmation message to the user via Telegram bot."""
    chat_id = user_id  # Assuming user_id is the chat_id
    message = f'Your deposit of {amount} USDT has been confirmed. Your new balance is {user_balances[user_id]}.'
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logger.info(f'Sent confirmation message to user {user_id}: {response.json()}')
    except requests.exceptions.RequestException as e:
        logger.error(f'Failed to send confirmation message to user {user_id}: {e}')

@app.route('/callback/<int:user_id>', methods=['POST'])
def callback(user_id):
    data = request.json
    logger.info(f'Received IPN callback for user {user_id}: {data}')
    try:
        if data['payment_status'] == 'confirmed':
            amount = float(data['pay_amount'])
            # Update user balance
            update_balance(user_id, amount)
            # Log the balance after update
            logger.info(f'Balance after update for user {user_id}: {user_balances[user_id]}')
            # Send confirmation message to the user
            send_confirmation(user_id, amount)
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f'Error processing IPN callback for user {user_id}: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500

def update_balance(user_id: int, amount: float) -> None:
    """Update user's balance when a deposit is received."""
    global user_balances  # Referencing the global user_balances variable
    if user_id not in user_balances:
        user_balances[user_id] = 0  # Initialize balance if not exists
    logger.info(f'Current balance for user {user_id}: {user_balances[user_id]}')
    user_balances[user_id] += amount
    logger.info(f'Updated balance for user {user_id}: {user_balances[user_id]}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
