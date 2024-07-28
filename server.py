from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Replace with your Telegram bot token
TELEGRAM_BOT_TOKEN = 'your-telegram-bot-token'
FLUTTER_APP_URL = 'http://your-flutter-app-endpoint'  # Replace with your Flutter app endpoint

vouchers = []

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    data = request.json
    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        text = data['message']['text']
        vouchers.append(text)
        send_message(chat_id, 'Voucher code received.')

        # Send the voucher code to the Flutter app
        response = requests.post(f'{FLUTTER_APP_URL}/voucher', json={'voucher': text})
        if response.status_code == 200:
            send_message(chat_id, 'Voucher code sent to the app.')
        else:
            send_message(chat_id, 'Failed to send voucher code to the app.')

    return '', 200

def send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(url, json=payload)

@app.route('/voucher', methods=['GET'])
def get_voucher():
    if vouchers:
        return jsonify({'voucher': vouchers.pop(0)})
    else:
        return jsonify({'voucher': ''}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
