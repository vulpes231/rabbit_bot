import os
from dotenv import load_dotenv
import logging
import firebase_admin
from firebase_admin import credentials, db
from aiogram import Bot, Dispatcher, executor, types

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

# User command handler for /start


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.chat.id
    username = str(user_id)

    # Check if user profile exists
    user_ref = ref.child(f"users/{username}")
    user_data = user_ref.get()

    if user_data is None:
        # Create a new user profile
        user_ref.set({
            'username': username,
            'balance': 0
        })
        balance = 0
    else:
        balance = user_data['balance']

    # Send welcome message
    welcome_text = f"Welcome, {username}! Your balance is: {balance}."
    await message.reply(welcome_text, reply_markup=await get_keyboard())


async def get_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Profile", "Admin", "Fund Wallet", "Products"]
    keyboard.add(*buttons)
    return keyboard

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
