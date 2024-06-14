import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# In-memory database to store user balances and invoice URLs
user_balances = {}
user_invoice_urls = {}

# NOWPayments API Key
NOWPAYMENTS_API_KEY = 'WBBJ03E-EMV4P7V-G86V1TY-Q6WQ1FH'

# NOWPayments API Endpoint
NOWPAYMENTS_API_URL = 'https://api.nowpayments.io/v1'

def create_invoice(user_id: int, amount: float) -> str:
    """Create an invoice using NOWPayments API."""
    url = f'{NOWPAYMENTS_API_URL}/invoice'
    headers = {
        'x-api-key': NOWPAYMENTS_API_KEY,
        'Content-Type': 'application/json'
    }
    payload = {
        'price_amount': amount,
        'price_currency': 'USD',
        'pay_currency': 'usdttrc20',
        'ipn_callback_url': f'https://yourserver.com/callback/{user_id}',
        'order_id': str(user_id),
        'order_description': 'Deposit to wallet'
    }
    response = requests.post(url, json=payload, headers=headers)
    response_data = response.json()

    if response.status_code in [200, 201] and 'invoice_url' in response_data:
        return response_data['invoice_url']
    else:
        logger.error('Failed to create deposit address: %s', response_data)
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.message.from_user
    if user.id not in user_balances:
        user_balances[user.id] = 0  # Initialize user balance
    await update.message.reply_text(f'Welcome {user.first_name}! Your wallet has been created with a balance of 0.')

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /balance is issued."""
    user = update.message.from_user
    balance = user_balances.get(user.id, 0)
    await update.message.reply_text(f'{user.first_name}, your current balance is {balance}.')

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create an invoice for the user to deposit 5 USDT."""
    user = update.message.from_user
    amount = 5  # Amount to be deposited
    invoice_url = create_invoice(user.id, amount)
    if invoice_url:
        user_invoice_urls[user.id] = invoice_url
        await update.message.reply_text(f'Please deposit {amount} USDT using the following link: {invoice_url}')
    else:
        await update.message.reply_text('Failed to generate deposit link. Please try again later.')

async def handle_payment_confirmation(user_id: int, amount: float, application: Application) -> None:
    """Handle payment confirmation by updating the user's balance and sending a confirmation message."""
    user_balances[user_id] = user_balances.get(user_id, 0) + amount
    chat_id = application.bot_data.get(user_id, None)
    if chat_id:
        await application.bot.send_message(chat_id, f'Your deposit of {amount} USDT has been confirmed. Your new balance is {user_balances[user_id]}.')

def main() -> None:
    """Start the bot."""
    # Replace 'YOUR_TOKEN' with your actual bot token
    application = Application.builder().token("7338701081:AAFAkZI1Jo0K3j8woT_fhunwGnpo90XnaUg").build()

    # Register handlers for different commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("balance", balance))
    application.add
