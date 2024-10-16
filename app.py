from flask import Flask, request, jsonify
from telebot import TeleBot
import mysql.connector
from mysql.connector import Error
import logging
import os
import threading

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Bot token
BOT_TOKEN = '8062581965:AAHCldmVb7amxDyfQuj-njP4_jdSKzKL9RA'

bot = TeleBot(BOT_TOKEN)

# MySQL Database Configuration
db_config = {
    'host': 'um8w47.stackhero-network.com',
    'user': 'root',
    'password': 'mQGaM5XO6KB50GFRfkLkRSnbeFpQ06Cm',
    'database': 'ah-mysql-stackhero-closed-63170',
    'port': '4803'
}

def create_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        logger.info("Database connection successful")
        return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        return None

def create_table():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT UNIQUE,
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                username VARCHAR(255)
            )
            """
            cursor.execute(create_table_query)
            connection.commit()
            logger.info("Table created successfully")
        except Error as e:
            logger.error(f"Error creating table: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

def register_user(user):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO users (user_id, first_name, last_name, username)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            first_name = VALUES(first_name),
            last_name = VALUES(last_name),
            username = VALUES(username)
            """
            user_data = (user.id, user.first_name, user.last_name, user.username)
            cursor.execute(insert_query, user_data)
            connection.commit()
            logger.info(f"User registered: {user.id}")
        except Error as e:
            logger.error(f"Error registering user: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

def get_user_info(user_id):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            select_query = "SELECT * FROM users WHERE user_id = %s"
            cursor.execute(select_query, (user_id,))
            user_info = cursor.fetchone()
            logger.info(f"Retrieved user info for: {user_id}")
            return user_info
        except Error as e:
            logger.error(f"Error getting user info: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return None

@bot.message_handler(commands=['start'])
def start(message):
    logger.info(f"Received /start command from user: {message.from_user.id}")
    user = message.from_user
    register_user(user)
    user_info = get_user_info(user.id)
    
    if user_info:
        greeting = f"Welcome, {user_info['first_name']}!\n\n"
        greeting += "Your information:\n"
        greeting += f"User ID: {user_info['user_id']}\n"
        greeting += f"First Name: {user_info['first_name']}\n"
        greeting += f"Last Name: {user_info['last_name']}\n"
        greeting += f"Username: {user_info['username']}"
    else:
        greeting = "Welcome! There was an error retrieving your information."
    
    bot.reply_to(message, greeting)
    logger.info(f"Sent greeting to user: {message.from_user.id}")

@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = request.get_json()
        bot.process_new_updates([update])
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid content type'})

@app.route("/")
def webhook_info():
    bot_info = bot.get_me()
    return f"Bot is active. Bot username: @{bot_info.username}", 200

def set_webhook(url):
    bot.remove_webhook()
    bot.set_webhook(url=url + '/' + BOT_TOKEN)
    logger.info(f"Webhook set to: {url}/{BOT_TOKEN}")

if __name__ == "__main__":
    create_table()
    set_webhook(os.environ.get('WEBHOOK_URL', 'https://your-app-url.herokuapp.com'))
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
