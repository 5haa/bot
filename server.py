from email.mime import application
from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/callback/<int:user_id>', methods=['POST'])
def callback(user_id):
    data = request.json
    if data['payment_status'] == 'confirmed':
        amount = float(data['pay_amount'])
        # Update user balance in your bot
        update_balance(user_id, amount)
        # Send confirmation message to the user
        send_confirmation(user_id, amount)
    return '', 200

def update_balance(user_id: int, amount: float) -> None:
    """Update user's balance when a deposit is received."""
    global user_balances
    user_balances[user_id] = user_balances.get(user_id, 0) + amount

def send_confirmation(user_id: int, amount: float) -> None:
    """Send a confirmation message to the user via Telegram bot."""
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    bot_token = '7338701081:AAFAkZI1Jo0K3j8woT_fhunwGnpo90XnaUg'
    chat_id = application.bot_data.get(user_id, None)
    if chat_id:
        message = f'Your deposit of {amount} USDT has been confirmed. Your new balance is {user_balances[user_id]}.'
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}'
        requests.get(url)

if __name__ == '__main__':
    app.run()
