import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
TOKEN = '8062581965:AAHCldmVb7amxDyfQuj-njP4_jdSKzKL9RA'

# Menu items
MENU = {
    'pizza': 10,
    'burger': 8,
    'salad': 6,
    'pasta': 9,
    'drink': 2
}

# User's current order
user_orders = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! Welcome to the Food Order Bot. Use /menu to see our offerings."
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display the menu with inline buttons."""
    keyboard = [
        [InlineKeyboardButton(f"{item.capitalize()} - ${price}", callback_data=f"add_{item}")]
        for item, price in MENU.items()
    ]
    keyboard.append([InlineKeyboardButton("View Order", callback_data="view_order")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose an item to add to your order:", reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button clicks."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id not in user_orders:
        user_orders[user_id] = {}

    if query.data.startswith("add_"):
        item = query.data.split("_")[1]
        if item in user_orders[user_id]:
            user_orders[user_id][item] += 1
        else:
            user_orders[user_id][item] = 1
        await query.edit_message_text(f"Added 1 {item} to your order. Use /menu to add more items or view your order.")
    elif query.data == "view_order":
        order_text = "Your current order:\n\n"
        total = 0
        for item, quantity in user_orders[user_id].items():
            price = MENU[item] * quantity
            order_text += f"{item.capitalize()}: {quantity} x ${MENU[item]} = ${price}\n"
            total += price
        order_text += f"\nTotal: ${total}"

        keyboard = [
            [InlineKeyboardButton("Place Order", callback_data="place_order")],
            [InlineKeyboardButton("Cancel Order", callback_data="cancel_order")],
            [InlineKeyboardButton("Back to Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(order_text, reply_markup=reply_markup)
    elif query.data == "place_order":
        # Here you would typically integrate with a payment system and delivery service
        await query.edit_message_text("Thank you for your order! It will be delivered soon.")
        del user_orders[user_id]
    elif query.data == "cancel_order":
        del user_orders[user_id]
        await query.edit_message_text("Your order has been cancelled. Use /menu to start a new order.")
    elif query.data == "back_to_menu":
        await menu(update, context)

def main() -> None:
    """Run the bot."""
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(button_click))

    application.run_polling()

if __name__ == '__main__':
    main()
