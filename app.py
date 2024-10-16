from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import hashlib
import hmac
import json
import requests

app = Flask(__name__)

# Database connection information
db_user = 'admin'
db_password = '$H@@Gy4n'
db_host = 'c3p4ih.stackhero-network.com'
db_port = '5796'
db_name = 'admin'

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?sslmode=require"

db = SQLAlchemy(app)

BOT_TOKEN = '8062581965:AAHCldmVb7amxDyfQuj-njP4_jdSKzKL9RA'  # Replace with your actual bot token
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))

def verify_telegram_data(data):
    data_check_string = '\n'.join([f'{k}={v}' for k, v in sorted(data.items()) if k != 'hash'])
    secret_key = hashlib.sha256(BOT_TOKEN.encode('utf-8')).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode('utf-8'), hashlib.sha256).hexdigest()
    return computed_hash == data['hash']

def send_telegram_message(chat_id, text):
    url = f"{API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, json=payload)
    return response.json()

@app.route('/start', methods=['POST'])
def start():
    data = request.json
    
    # Check if this is a bot command or Mini App data
    if 'message' in data and 'text' in data['message']:
        # This is a bot command
        chat_id = data['message']['chat']['id']
        user_id = data['message']['from']['id']
        username = data['message']['from'].get('username', 'No username')
        first_name = data['message']['from'].get('first_name', '')
        last_name = data['message']['from'].get('last_name', '')

        user = User.query.filter_by(telegram_id=str(user_id)).first()
        if not user:
            user = User(telegram_id=str(user_id), username=username, 
                        first_name=first_name, last_name=last_name)
            db.session.add(user)
            db.session.commit()

        response_text = f"Hello, @{username}! Your bot is running. Welcome to the Mini App!"
        send_telegram_message(chat_id, response_text)
        return jsonify({'message': 'Start command processed'}), 200

    else:
        # This is Mini App data
        if not verify_telegram_data(data):
            return jsonify({'error': 'Invalid data'}), 400

        user = User.query.filter_by(telegram_id=data['id']).first()
        if not user:
            user = User(telegram_id=data['id'], username=data.get('username'), 
                        first_name=data.get('first_name'), last_name=data.get('last_name'))
            db.session.add(user)
            db.session.commit()
        return jsonify({'message': 'User registered successfully'})

@app.route('/')
def home():
    data = request.args.get('initData')
    if not data:
        return jsonify({'error': 'No init data provided'}), 400

    data_dict = dict(x.split('=') for x in data.split('&'))
    if not verify_telegram_data(data_dict):
        return jsonify({'error': 'Invalid data'}), 400

    user_data = json.loads(data_dict['user'])
    user = User.query.filter_by(telegram_id=user_data['id']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return render_template('home.html', user=user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
