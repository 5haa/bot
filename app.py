import os
import logging
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Dispatcher,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,

from telegram import Bot

app = Flask(__name__)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define states for ConversationHandler
CHOOSING_CATEGORY, CHOOSING_ITEM, ORDER_CONFIRMATION = range(3)

# Sample menu
MENU = {
    'Pizza': ['Margherita', 'Pepperoni', 'Hawaiian'],
    'Burger': ['Beef Burger', 'Chicken Burger', 'Veggie Burger'],
    'Drinks': ['Coke', 'Pepsi', 'Water'],
}

# Get the API token from environment variables
TOKEN = os.environ.get('8062581965:AAHCldmVb7amxDyfQuj-njP4_jdSKzKL9RA')
HEROKU_APP_NAME = os.environ.get('shaagamebot')

# Initialize the bot and dispatcher
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

# Define conversation handler functions
def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Order Food']]
    update.message.reply_text(
        "Welcome to FoodBot! How can I assist you today?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CHOOSING_CATEGORY

def order_food(update: Update, context: CallbackContext) -> int:
    categories = list(MENU.keys())
    reply_keyboard = [categories]
    update.message.reply_text(
        "Please select a category:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CHOOSING_ITEM

def choose_item(update: Update, context: CallbackContext) -> int:
    category = update.message.text
    context.user_data['category'] = category

    if category not in MENU:
        update.message.reply_text("Sorry, I didn't understand that category.")
        return CHOOSING_CATEGORY

    items = MENU[category]
    reply_keyboard = [items]
    update.message.reply_text(
        f"Please choose an item from {category}:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ORDER_CONFIRMATION

def confirm_order(update: Update, context: CallbackContext) -> int:
    item = update.message.text
    category = context.user_data.get('category')

    if item not in MENU.get(category, []):
        update.message.reply_text("Sorry, that item isn't available.")
        return CHOOSING_ITEM

    update.message.reply_text(
        f"Thank you! Your order for {item} has been placed and will be delivered shortly."
    )
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Order canceled. Have a nice day!")
    return ConversationHandler.END

# Register handlers
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        CHOOSING_CATEGORY: [
            MessageHandler(Filters.regex('^(Order Food)$'), order_food),
            MessageHandler(Filters.text & ~Filters.command, order_food)
        ],
        CHOOSING_ITEM: [
            MessageHandler(Filters.text & ~Filters.command, choose_item)
        ],
        ORDER_CONFIRMATION: [
            MessageHandler(Filters.text & ~Filters.command, confirm_order)
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

dispatcher.add_handler(conv_handler)

# Define route for webhook
@app.route('/{}'.format(TOKEN), methods=['POST'])
def webhook():
    """Receives updates from Telegram and processes them."""
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'OK', 200

# Set webhook when the app starts
@app.before_first_request
def set_webhook():
    webhook_url = f'https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}'
    bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook set to {webhook_url}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8443)))
