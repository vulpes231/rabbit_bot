import os
from dotenv import load_dotenv
import logging
import firebase_admin
from firebase_admin import credentials, db
from aiogram import Bot, Dispatcher, executor, types
from command import start, display_profile, add_product, display_categories, display_products_by_category,  handle_category_selection, process_order, get_user_orders, show_faqs_tips

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
firebase_admin.initialize_app(
    cred, {"databaseURL": DATABASE_URL})


ref = db.reference("/")

# Initialize bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# User commands

# /start
dp.register_message_handler(
    lambda message: start(message, ref), commands=['start']
)

# Check profile
dp.register_message_handler(
    display_profile, lambda message: message.text == "Profile"
)

# Add product
dp.register_message_handler(
    lambda message: add_product(message, ADMINS), commands=['addproduct']
)

# Display categories
dp.register_message_handler(
    display_categories, lambda message: message.text == "Products"
)

# Handle user selection (category selection and product display)
dp.register_callback_query_handler(
    handle_category_selection, lambda c: c.data.startswith("category_"))

# Register the order processing callback
dp.register_callback_query_handler(
    process_order, lambda c: c.data.startswith("order_"))


dp.register_message_handler(
    get_user_orders, lambda message: message.text == "Orders"
)

dp.register_message_handler(
    show_faqs_tips, lambda message: message.text == "FAQs"
)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
