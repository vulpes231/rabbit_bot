import os
from dotenv import load_dotenv
import logging
import firebase_admin
from firebase_admin import credentials, db
from aiogram import Bot, Dispatcher, executor, types
from command import start, display_profile, add_product, display_categories, display_products_by_category, handle_user_selection

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
dp.register_message_handler(
    handle_user_selection, content_types=['text']
)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
