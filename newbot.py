import os
from dotenv import load_dotenv
import logging
import firebase_admin
from firebase_admin import credentials


# ********* load environment creds**********
load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = os.getenv("BOT_USERNAME")
ADMIN_OTP = os.getenv("ADMIN_OTP")

admin_keys = ["BISHOP", "TED", "TENDRILS", "BIG", "RABBIT", "VULPES"]


ADMINS = [os.getenv(key) for key in admin_keys]

# ********* set up logging **********
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ********* initialize database **********
cred = credentials.Certificate("./rabbitcred.json")
firebase_admin.initialize_app(cred)


# ********* command: /start **********

async def start():
