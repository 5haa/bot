from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import hashlib
import hmac
import json

app = Flask(__name__)
CORS(app)

# Replace with your actual bot token
BOT_TOKEN = "7451089550:AAGiilwzmCsRG0lv-j_5ZYQoQqFPPRb-Ndo"

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

if __name__ == '__main__':
    app.run(debug=True)
