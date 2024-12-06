import os
from dotenv import load_dotenv
import logging
from functools import partial
import firebase_admin
from firebase_admin import credentials, db
from aiogram import Bot, Dispatcher, executor, types
from command import (
    start, display_profile, add_product, process_order, get_user_orders, show_faqs_tips, show_help,
    fund_wallet, handle_manual_method, handle_auto_method, routine_message, get_product_status,
    get_all_posted_messages, display_product_ids, delete_product, display_products, show_product_details
)


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = os.getenv("BOT_USERNAME")
ADMIN_OTP = os.getenv("ADMIN_OTP")

admin_keys = ["BISHOP", "TED", "TENDRILS", "BIG", "RABBIT", "VULPES"]
ADMINS = [os.getenv(key) for key in admin_keys]
CHANNELS = [-1002426920807]

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

# Register User Commands
dp.register_message_handler(start, commands=['start'])
dp.register_message_handler(
    display_profile, lambda message: message.text == "Profile")
dp.register_message_handler(lambda message: add_product(
    message, ADMINS), commands=['addproduct'])
dp.register_message_handler(lambda message: display_product_ids(
    message, ADMINS), commands=['productids'])
dp.register_message_handler(lambda message: routine_message(
    message, ADMINS, CHANNELS), commands=['addcontent'])
dp.register_message_handler(lambda message: get_product_status(
    message, ADMINS, CHANNELS), commands=['status'])
dp.register_message_handler(lambda message: get_all_posted_messages(
    message, ADMINS), commands=['getmessages'])
dp.register_message_handler(
    display_products, lambda message: message.text == "Products")
dp.register_message_handler(lambda message: get_user_orders(
    message), lambda message: message.text == "Orders")
dp.register_message_handler(lambda message: show_faqs_tips(
    message), lambda message: message.text == "FAQs")
dp.register_message_handler(lambda message: show_help(
    message, ADMINS), lambda message: message.text == "Support")
dp.register_message_handler(lambda message: fund_wallet(
    message), lambda message: message.text == "Fund Wallet")

# Register Callback Query Handlers
dp.register_callback_query_handler(
    show_product_details, lambda c: c.data.startswith("product_"))
dp.register_callback_query_handler(
    process_order, lambda c: c.data.startswith("order_"))
dp.register_callback_query_handler(partial(
    delete_product, admins=ADMINS), lambda c: c.data.startswith("delete_product_"))
dp.register_callback_query_handler(
    handle_manual_method, lambda c: c.data == "fund_manual")
dp.register_callback_query_handler(
    handle_auto_method, lambda c: c.data == "fund_auto")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
