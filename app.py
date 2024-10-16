from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import hashlib
import hmac
import json
import os
import requests

app = Flask(__name__)
CORS(app)

BOT_TOKEN = os.environ.get('7451089550:AAGiilwzmCsRG0lv-j_5ZYQoQqFPPRb-Ndo')
WEBAPP_URL = os.environ.get('WEBAPP_URL')  # URL where your mini app is hosted

def send_telegram_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    response = requests.post(url, json=payload)
    return response.json()

def verify_telegram_data(init_data):
    data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(init_data.items()) if k != 'hash'])
    secret_key = hmac.new("WebAppData".encode(), BOT_TOKEN.encode(), hashlib.sha256).digest()
    data_check_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return data_check_hash == init_data['hash']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_user_data', methods=['POST'])
def get_user_data():
    init_data = request.json.get('initData')
    if not init_data:
        return jsonify({"error": "No init data provided"}), 400

    parsed_data = {}
    for param in init_data.split('&'):
        key, value = param.split('=')
        parsed_data[key] = value

    if not verify_telegram_data(parsed_data):
        return jsonify({"error": "Invalid init data"}), 400

    user_data = json.loads(parsed_data['user'])
    return jsonify({
        "name": user_data.get('first_name', '') + ' ' + user_data.get('last_name', ''),
        "balance": 6815.53  # This would typically come from a database
    })

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def telegram_webhook():
    update = request.json
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        if 'text' in update['message']:
            text = update['message']['text']
            if text == '/start':
                welcome_message = "Welcome to the Wallet Bot! Click the button below to open the mini app."
                keyboard = {
                    "inline_keyboard": [[{
                        "text": "Open Wallet",
                        "web_app": {"url": WEBAPP_URL}
                    }]]
                }
                send_telegram_message(chat_id, welcome_message, keyboard)
    return '', 200

def setup_bot():
    # Set webhook
    webhook_url = f"{WEBAPP_URL}/{BOT_TOKEN}"
    set_webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    response = requests.post(set_webhook_url, json={"url": webhook_url})
    print("Webhook set response:", response.json())

    # Set commands
    set_commands_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"
    commands = [
        {"command": "start", "description": "Start the bot and open the wallet"},
    ]
    response = requests.post(set_commands_url, json={"commands": commands})
    print("Set commands response:", response.json())

    # Set menu button
    set_menu_button_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setChatMenuButton"
    button = {
        "type": "web_app",
        "text": "Open Wallet",
        "web_app": {"url": WEBAPP_URL}
    }
    response = requests.post(set_menu_button_url, json={"menu_button": button})
    print("Set menu button response:", response.json())

if __name__ == '__main__':
    setup_bot()  # Configure the bot before starting the Flask app
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
