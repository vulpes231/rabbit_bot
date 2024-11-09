import os
from dotenv import load_dotenv
import logging
import asyncio
from functools import partial
import firebase_admin
from firebase_admin import credentials, db
from aiogram import Bot, Dispatcher, executor, types
from command import start, display_profile, add_product, display_categories, display_products_by_category, handle_category_selection, process_order, get_user_orders, show_faqs_tips, show_help, fund_wallet, handle_manual_method, handle_auto_method,  routine_message, get_product_status, get_all_posted_messages, handle_delete_message, delete_message, delete_due_messages, manual_delete_all_messages, display_product_ids, delete_product

# Load environment credentials
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = os.getenv("BOT_USERNAME")
ADMIN_OTP = os.getenv("ADMIN_OTP")

admin_keys = ["BISHOP", "TED", "TENDRILS", "BIG", "RABBIT", "VULPES"]
ADMINS = [os.getenv(key) for key in admin_keys]

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize database
cred = credentials.Certificate("rabbitcred.json")
firebase_admin.initialize_app(cred, {"databaseURL": DATABASE_URL})

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# User commands
dp.register_message_handler(
    lambda message: start(message), commands=['start'])
dp.register_message_handler(
    display_profile, lambda message: message.text == "Profile")
dp.register_message_handler(lambda message: add_product(
    message, ADMINS), commands=['addproduct'])
dp.register_message_handler(lambda message: display_product_ids(
    message, ADMINS), commands=['productids'])
dp.register_message_handler(lambda message: routine_message(
    message, ADMINS), commands=['addcontent'])
dp.register_message_handler(lambda message: manual_delete_all_messages(
    message, ADMINS), commands=['deleteallmsg'])
dp.register_message_handler(lambda message: get_product_status(
    message, ADMINS), commands=['status'])
dp.register_message_handler(lambda message: get_all_posted_messages(
    message, ADMINS), commands=['getmessages'])
dp.register_message_handler(lambda message: handle_delete_message(
    message, ADMINS), commands=['deletemsg'])
dp.register_message_handler(
    display_categories, lambda message: message.text == "Products")
dp.register_callback_query_handler(
    handle_category_selection, lambda c: c.data.startswith("category_"))
dp.register_callback_query_handler(
    process_order, lambda c: c.data.startswith("order_"))
dp.register_callback_query_handler(
    partial(delete_product, admins=ADMINS),  # Pass ADMINS here
    lambda c: c.data.startswith("delete_product_")
)
dp.register_message_handler(
    get_user_orders, lambda message: message.text == "Orders")
dp.register_message_handler(
    show_faqs_tips, lambda message: message.text == "FAQs")
dp.register_message_handler(
    fund_wallet, lambda message: message.text == "Fund Wallet")
dp.register_callback_query_handler(
    handle_manual_method, lambda c: c.data == "fund_manual")
dp.register_callback_query_handler(
    handle_auto_method, lambda c: c.data == "fund_auto")
dp.register_message_handler(lambda message: show_help(
    message, ADMINS), lambda message: message.text == "Support")


# Start the periodic deletion task after polling starts
async def on_startup(dispatcher):
    asyncio.create_task(delete_due_messages(dispatcher.bot))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)  # Set up logging
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
