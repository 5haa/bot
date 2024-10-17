from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# Define the menu options
MENU_OPTIONS = [
    ["Pizza", "Burger", "Pasta"],
    ["Salad", "Sushi", "Dessert"],
]

# Define a start command handler
def start(update: Update, context):
    user_first_name = update.message.from_user.first_name
    # Send greeting message
    update.message.reply_text(f"Hello {user_first_name}! Welcome to Food Order Bot.")
    
    # Create the food menu
    keyboard = [
        [InlineKeyboardButton(option, callback_data=option) for option in row]
        for row in MENU_OPTIONS
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send message with menu
    update.message.reply_text("Please choose an item from the menu:", reply_markup=reply_markup)

# Handle button clicks
def button(update: Update, context):
    query = update.callback_query
    query.answer()
    
    # Get user's choice from button press
    choice = query.data
    
    # Send confirmation message
    query.edit_message_text(f"You have selected {choice}!")

# Main function to set up the bot
def main():
    # Initialize the bot with your token
    updater = Updater("8062581965:AAHCldmVb7amxDyfQuj-njP4_jdSKzKL9RA", use_context=True)
    
    # Get dispatcher to register handlers
    dp = updater.dispatcher
    
    # Register start command handler
    dp.add_handler(CommandHandler("start", start))
    
    # Register button callback handler
    dp.add_handler(CallbackQueryHandler(button))
    
    # Start the Bot
    updater.start_polling()
    
    # Run the bot until the user stops it
    updater.idle()

if __name__ == '__main__':
    main()
