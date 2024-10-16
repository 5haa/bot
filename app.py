from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import hashlib
import hmac
import json
import requests
import logging
import sys
import traceback
import os

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Database connection information
db_user = 'root'
db_password = 'mQGaM5XO6KB50GFRfkLkRSnbeFpQ06Cm'
db_host = 'um8w47.stackhero-network.com'
db_port = '4803'
db_name = 'ah-mysql-stackhero-closed-63170'

# Construct the SQLAlchemy database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?ssl_ca=/path/to/isrgrootx1.pem&ssl_verify_cert=true"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

BOT_TOKEN = '8062581965:AAHCldmVb7amxDyfQuj-njP4_jdSKzKL9RA'
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
    app.logger.debug("Received request to /start")
    app.logger.debug(f"Request data: {request.data}")
    
    try:
        data = request.json
        app.logger.debug(f"Parsed JSON data: {data}")
        
        if 'message' in data and 'text' in data['message']:
            chat_id = data['message']['chat']['id']
            user_id = data['message']['from']['id']
            username = data['message']['from'].get('username', 'No username')
            first_name = data['message']['from'].get('first_name', '')
            last_name = data['message']['from'].get('last_name', '')

            app.logger.info(f"Received /start command from user {username} (ID: {user_id})")

            try:
                user = User.query.filter_by(telegram_id=str(user_id)).first()
                if not user:
                    user = User(telegram_id=str(user_id), username=username, 
                                first_name=first_name, last_name=last_name)
                    db.session.add(user)
                    db.session.commit()
                    app.logger.info(f"New user {username} added to database")
            except Exception as db_error:
                app.logger.error(f"Database error: {str(db_error)}")
                # Continue even if database operation fails

            response_text = f"Hello, @{username}! Your bot is running. Welcome to the Mini App!"
            send_result = send_telegram_message(chat_id, response_text)
            app.logger.debug(f"Send message result: {send_result}")
            
            return jsonify({'message': 'Start command processed'}), 200
        else:
            app.logger.warning("Received data is not a Telegram message")
            return jsonify({'error': 'Invalid data format'}), 400

    except Exception as e:
        app.logger.error(f"Error processing /start command: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/')
def home():
    app.logger.debug(f"Received request to home route")
    app.logger.debug(f"Request args: {request.args}")
    app.logger.debug(f"Request headers: {request.headers}")

    init_data = request.args.get('initData')
    
    if not init_data:
        app.logger.warning("No init data provided")
        return render_template('error.html', message="No init data provided. Please launch this app from Telegram.")

    try:
        data_dict = dict(x.split('=') for x in init_data.split('&'))
        app.logger.debug(f"Parsed init data: {data_dict}")

        if not verify_telegram_data(data_dict):
            app.logger.warning("Invalid Telegram data")
            return render_template('error.html', message="Invalid data. Please try launching the app again.")

        user_data = json.loads(data_dict['user'])
        app.logger.debug(f"User data: {user_data}")

        user = User.query.filter_by(telegram_id=user_data['id']).first()
        if not user:
            app.logger.warning(f"User not found: {user_data['id']}")
            return render_template('error.html', message="User not found. Please start the bot first.")

        return render_template('home.html', user=user)

    except Exception as e:
        app.logger.error(f"Error processing home route: {str(e)}")
        app.logger.error(traceback.format_exc())
        return render_template('error.html', message="An error occurred. Please try again later.")

@app.route('/check_db')
def check_db():
    try:
        # Check if the table exists
        exists = db.engine.dialect.has_table(db.engine.connect(), "user")
        if exists:
            users = User.query.all()
            return jsonify({
                "status": "success",
                "message": "Database connected and User table exists",
                "user_count": len(users)
            })
        else:
            return jsonify({
                "status": "warning",
                "message": "Database connected but User table does not exist"
            })
    except Exception as e:
        app.logger.error(f"Database check error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error checking database: {str(e)}"
        }), 500

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"500 error: {str(error)}")
    app.logger.error(traceback.format_exc())
    return jsonify({'error': 'Internal server error'}), 500

def initialize_database():
    app.logger.debug("Attempting to create database tables...")
    try:
        with app.app_context():
            db.create_all()
        app.logger.debug("Database tables created successfully.")
    except Exception as e:
        app.logger.error(f"Error creating database tables: {str(e)}")
        app.logger.error(traceback.format_exc())

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)
