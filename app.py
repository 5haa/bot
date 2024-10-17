import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

# Function to handle the /start command
async def start(update: Update, context):
    # Get user's first name
    user_first_name = update.effective_user.first_name
    
    # Send a greeting message
    await update.message.reply_text(f"Hello, {user_first_name}! Welcome to the bot!")

# Main function to run the bot
if __name__ == '__main__':
    # Get bot token from environment variables
    bot_token = os.getenv('BOT_TOKEN')

    # Initialize the bot application
    application = ApplicationBuilder().token(bot_token).build()

    # Add handler for the /start command
    application.add_handler(CommandHandler('start', start))

    # Run the bot until manually stopped
    application.run_polling()
