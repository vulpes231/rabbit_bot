# -*- coding: utf-8 -*-

from typing import List
from telegram import Bot
from telegram.error import BadRequest
from telegram.constants import ParseMode
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import logging
from firebase_admin import credentials, firestore, storage
import firebase_admin
import base64
from flask import Flask, request
import hashlib
import json
import requests
import os
from dotenv import load_dotenv, dotenv_values
# loading variables from .env file
load_dotenv()


######################## end of imports ####################


# Replace 'YOUR_BOT_TOKEN' with your actual bot token


TOKEN = os.getenv(TOKEN)

# os.environ.get("TOKEN")

# Cryptomus apikeys


# Replace with your actual Telegram bot username
bot_username = "Rabbithole4ogs_bot"


# for logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# List of usernames allowed to call this function

# ADMIN USERNAME
ADMIN_USERNAME = "bishopzeit"
ADMIN2_USERNAME = "bishopzeit"
ADMIN3_USERNAME = "rabbitsocial"
ADMIN4_USERNAME = "tendbank2"
ADMIN5_USERNAME = "bigxxxl01"
ADMIN6_USERNAME = "tendrilsofficial"

ADMIN_CHATID = 5518246575

ALLOWED_USERNAMES = [ADMIN_USERNAME, ADMIN2_USERNAME]

OTP_ADMIN = 'shoqhere'

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://tendrils1-default-rtdb.firebaseio.com/'
})

# Function for the '/start' command


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Check if the user has an existing profile
    user_profile = firestore.client().collection(
        'user_profiles').document(str(user_id)).get().to_dict()

    if user_profile is None:
        # If not, create a new profile with default balance
        user_profile = {'chat_id': chat_id, 'balance': 0}
        firestore.client().collection('user_profiles').document(
            str(user_id)).set(user_profile)

    # Send a welcome message along with the user's balance
    await context.bot.send_message(chat_id=chat_id, parse_mode='HTML', text=f"<b>Yoo! {update.effective_user.username}! Welcome to Rabbithole.</b>\nYour balance: ${user_profile['balance']}")

    # Construct the keyboard with a button first set

    keyboard2 = [['Products', 'Admin', 'Fund wallet', 'profile']]

    reply_markup2 = ReplyKeyboardMarkup(keyboard2,
                                        one_time_keyboard=False,
                                        resize_keyboard=True)

    # Send the menu as a message
    await update.message.reply_text('Choose a Service:', reply_markup=reply_markup2)

############################### sort menu commands ####################################


async def menusorter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the selected language
    menusorter = update.message.text

    # Respond based on the selected option
    if menusorter == 'Products':
        # Respond with the /products command
        await update.message.reply_text("Products 🔰")
        await product(update, context)
    elif menusorter == 'Admin':

        await update.message.reply_text("Admin 🔰")

        await adminbutton(update, context)

    elif menusorter == 'profile':
        await update.message.reply_text("My Profile 🔰")

        await profile(update, context)

    elif menusorter == 'Fund wallet':

        await update.message.reply_text("Funding 🔰")

        await initiate_payment(update, context)


##################### initiate payment #########################
async def initiate_payment(update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    # Create an inline keyboard with a "Buy" button that redirects to the support chat
    keyboard200 = [[InlineKeyboardButton(
        "Account details for non-crypto funding", url=f'https://t.me/{ADMIN_USERNAME}')]]
    twofa200_options_reply_markup = InlineKeyboardMarkup(keyboard200)

    # Specify the parameters for wallet creation

    usdt_address = "TD12CZLCkX3G8MaTUpyJ4wprupTmuF82JS"

    btc_address = "bc1q7hgjre0lr9twuwf558qhqdlzwp88xrns6u323e"

    naira_address = "We accept <b>NIGERIAN NAIRA\nSOUTH AFRICAN RANDS</b>\nAccount details will be Available upon request."
    message = f"Fund account by making payment to any of the addresses below \n\n<b>USDT(TRC20):   {usdt_address}</b>\n\n<b>BTC:</b>  {btc_address}\n\n<b>Amount will be funded on your account</b>.\n\n{naira_address} \n\n<b>NOTE! Please send proof of payment to admin!! otherwise funds won't reflect on your account!</b>"

    await context.bot.send_message(chat_id, text=message, reply_markup=twofa200_options_reply_markup, parse_mode='html',)


async def initiate_payment2(update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Specify the parameters for wallet creation
    currency = "USDT"  # Replace with the desired currency
    network = "tron"   # Replace with the desired blockchain network
    order_id = str(user_id)  # Use a unique order ID, you can modify this logic
    # Append /crypto_callback to your ngrok URL
    url_callback = f"{callback_url}/crypto_callback"
    status = 'paid'

    # Create CryptoMus wallet
    wallet_details = create_payment(
        currency, network, order_id, url_callback, status)

    if wallet_details:
        # Wallet creation successful, you can handle the details as needed
        wallet_address = wallet_details.get('address')
        wallet_url = wallet_details.get('url')
        message = f"Fund account via <b>USDT(TRC20)</b> only. Amount will be funded on your account.\n\n Wallet Address:\n\n\n <a href='{wallet_address}'>{wallet_address}</a>\n\n\n You can also click on the link below to make payment.\n\n <a href='{wallet_url}'>{wallet_url}</a>\n\n"

        logging.info(message)
        await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='html')
    else:
        # Wallet creation failed, handle the error
        error_message = "Error creating CryptoMus wallet."
        logging.error(error_message)
        await context.bot.send_message(chat_id=chat_id, text=error_message)


########################################## Product ########################

# Function to call the start function
async def product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Simply call the start function from within the home function

    # await context.bot.send_photo(chat_id=update.effective_chat.id, photo='https://rabbitsms.online/rabbitrabbit.webp')

    keyboard = [
        [InlineKeyboardButton("🧧TUTORIALS + CLASSES",
                              callback_data='option36')],

        [InlineKeyboardButton("2FA Links", callback_data='option1')],
        [InlineKeyboardButton(
            "Redirect tools for  inbox projects", callback_data='option2')],
        [InlineKeyboardButton(
            "ATTACHMENT SPAMMING & LETTERS", callback_data='option25')],

        [InlineKeyboardButton("Rdps", callback_data='option3')],
        [InlineKeyboardButton("Social Media Accounts",
                              callback_data='option18')],
        [InlineKeyboardButton("Drainer (crypto)", callback_data='option37')],
        [InlineKeyboardButton("Malwares (RATs)", callback_data='option38')],


        [InlineKeyboardButton("Resume", callback_data='option11')],
        [InlineKeyboardButton("Senders Email | SMS",
                              callback_data='option21')],
        [InlineKeyboardButton("Office LOGS", callback_data='option4')],
        # [InlineKeyboardButton("Send GIFT items to Clients", callback_data='option19')],
        [InlineKeyboardButton("Merchant links (payments)",
                              callback_data='option30')],



        [InlineKeyboardButton(
            "Bank LOGs and Account Openups", callback_data='option23')],

        [InlineKeyboardButton(
            "PICK UP SERVICES: (WIRE/INVOICE/OPEN BENFICIARY)", callback_data='option39')],

        [InlineKeyboardButton("NON VBV CCs", callback_data='option17')],
        [InlineKeyboardButton("Freebies", callback_data='option20')],
        # [InlineKeyboardButton("Vpn", callback_data='option22')],
        [InlineKeyboardButton("Custom requests", callback_data='option24')],
        [InlineKeyboardButton("Email leads n Sms Leads",
                              callback_data='option26')],
        [InlineKeyboardButton("Website building services",
                              callback_data='option40')],


        [InlineKeyboardButton("SMTP (TOP-SMTPS ONLY)",
                              callback_data='option27')],
        [InlineKeyboardButton("Extractor AND Sorter",
                              callback_data='option28')],

        # [InlineKeyboardButton("DATING Accounts", callback_data='option29')],
        [InlineKeyboardButton("Fullz + info", callback_data='option32')],
        # [InlineKeyboardButton("LINKEDIN ACCOUNTS", callback_data='option33')],
        # [InlineKeyboardButton("GOOGLE VOICE + ICQ ACCOUNTS", callback_data='option34')],
        [InlineKeyboardButton(
            "🀄️🀄️Our channels List and admin list", callback_data='option31')],
        [InlineKeyboardButton("💹SELL YOUR CRYPTOCURRENCIES",
                              callback_data='option35')],
        [InlineKeyboardButton("🧧TUTORIALS + CLASSES",
                              callback_data='option36')],



    ]

    reply_markup_product = InlineKeyboardMarkup(keyboard)

    # Send the additional options as a message
    await update.message.reply_text("🀄️🀄️🀄️\n\n What you want Og?", reply_markup=reply_markup_product)


############################################# PROFILE #####################################################


# Function for the "Profile" button


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Check if the user has an existing profile
    user_profile = firestore.client().collection(
        'user_profiles').document(str(user_id)).get().to_dict()

    # Check if the profile exists
    if user_profile:
        # Send the user's profile information
        await update.message.reply_text(f"Your profile:\nChat ID: {user_profile['chat_id']}\nBalance: ${user_profile['balance']}")
    else:
        # Inform the user that the profile doesn't exist
        await update.message.reply_text("Profile not found.")


########################################### 2FA ##############################################################
# Callback function for '2FA' button

async def option1_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    # Construct the keyboard for the additional options when 'Support' is clicked
    extract_keyboard = [
        [InlineKeyboardButton(
            "Subscribe", url=f'https://t.me/{ADMIN_USERNAME}?start=support')],
    ]

    twofa_options_reply_markup = InlineKeyboardMarkup(extract_keyboard)

    await update.callback_query.message.reply_text('🧧 2FA - 2 Factor authenticator ByPasser + Cookie\n\n\n🀄OFFICE365 AVAILABLE\n🀄OUTLOOK AVAILABLE\n🀄YAHOO MAIL\n🀄Gmail\n🀄Quickbooks\n🀄Aol\n🀄Dropbox\n🀄Sendgrid\n🀄Ionos\n🀄Rackspace\n\nEmail Cookie Capture\nYou get email access cookies to bypass 2fa\n\nFeatures\nANTI-RED 2FA LINKS 🔰\nAUTO CAPTURE 2FA COOKIES (phone and Microsoft Authenticator app) 🔰\nAVAILABLE WITH OFFLINE 2FA ATTACHMENTS \nResults in tg and web dashboard🔰\nLINK TRACKING ( click and paste detection)🔰\nMultiple custom redirect pages🔰\nAuto fetch custom logos and background 🔰\nSuper dynamic codes!\nsee samples here ---> https://t.me/rabbit2fa/63\n\n🧧 NON 2FA LINKS\n\n<b>$170 flat</b>\n\nThis subscription package includes all stated below. You’d have access to all for the duration of 1 month.\n\n🀄OFFICE365 AVAILABLE \n🀄OUTLOOK AVAILABLE\n🀄YAHOO MAIL\n🀄Aol\n🀄Dropbox\n🀄Sendgrid\n🀄Ionos\n🧧 ATTACHMENTS: $150', reply_markup=twofa_options_reply_markup, parse_mode='html')


# Callback function for PICK UPS items


async def option39_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    # Construct the keyboard for the additional options when 'Support' is clicked
    extract_keyboard = [
        [InlineKeyboardButton(
            "Use pick-up service", url=f'https://t.me/{ADMIN_USERNAME}?start=support')],
    ]

    twofa_options_reply_markup = InlineKeyboardMarkup(extract_keyboard)

    await update.callback_query.message.reply_text('🧧 In our bid to be a one stop shop we added pick up services..\n\n\nOur Pickup network is vast and reliable,Connect runs deep.\n\n\nPayment in btc  fast and reliable, afterall the house does it best.\n\n\nAccounts available for COUNTRIES LISTED BELOW\n\n\nHong Kong\n\nCanada\n\nUnited-kingdom\n\nAustralia\n\nUSA\n\nPortugal\n\nSpain\n\nMexico\n\nChina\n\nJapan\n\nSouth korea\n\nVietnam\n\nThailand\n\n\nOpen beneficiary accounts\n\nClient payments (direct deposit and service banks)\n\nCash mailing\n\nCashapp accounts for pickups\n\nWestern Union + money gram route and addresses\n\nCheck pickups (using big business accounts)\n\nThings we do so well.', reply_markup=twofa_options_reply_markup, parse_mode='html')


# Callback function for ATTACHMENT items
async def option25_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    # Send the additional options as a message

    await update.callback_query.message.reply_text('🀄️🀄️<b>ATTACHMENT SPAMMING</b>\n\nSpam without links using downloadable attachment files and receive results in tg.\n\nLetters for spamming\n\nOffice 365 Letters\n\nBank letters and co.Join here to view our letter samples.\n\nWe also take requests for custom  letters\n\nhttps://t.me/+AhDf1Q5WSVI4ZTlk', parse_mode='html')


# Callback function for EXTRACTOR AND SORTER items
async def option28_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.callback_query.answer()

    # Construct the keyboard for the additional options when 'Support' is clicked
    extract_keyboard = [
        [InlineKeyboardButton(
            "Buy EXTRACTOR", url=f'https://t.me/{ADMIN_USERNAME}?start=support')],
    ]

    reply_markup = InlineKeyboardMarkup(extract_keyboard)

    # Send the additional options as a message

    await update.callback_query.message.reply_text('🀄️🀄️EXTRACTOR for office365 boxes. Our extractor comes with a redirect finder.\n\nThis means you get your leads extracted and you get redirect as well for your inbox project.\n\nPRICE $150\n\n\nYou can also rent our extraction tool for $10 per extraction\n\n<b>SORTER.</b> Sorters are used for sorting emails into various email provider like office365, outlook, godaddy and co..\n\nPrice - $60', reply_markup=reply_markup, parse_mode='html')


# Callback function for EXTRACTOR AND SORTER items
async def option40_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.callback_query.answer()

    # Construct the keyboard for the additional options when 'Support' is clicked
    extract_keyboard = [
        [InlineKeyboardButton(
            "Talk to dev", url=f'https://t.me/{ADMIN_USERNAME}?start=support')],
    ]

    reply_markup = InlineKeyboardMarkup(extract_keyboard)

    # Send the additional options as a message

    await update.callback_query.message.reply_text('🀄️🀄️Build websites, flash banks, all web2 and web3 projects. Our devs are at your service.\n\nOptional services include:\n\nBULLET-PROOF HOSTING\n\nDomain\n\nEmail\n\nInvestment website\nEmployment website\n\nBanks\n\nCrypto projects websites\n\nAirdrop websites\n\nAny phishing projects\n\n\nMore --->  https://t.me/rabbitholecustom', reply_markup=reply_markup, parse_mode='html')


# Callback function for fullz
async def option32_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.callback_query.answer()

    # Construct the keyboard for the additional options when 'Support' is clicked
    extract_keyboard = [
        [InlineKeyboardButton(
            "Buy FULLZ", url=f'https://t.me/{ADMIN_USERNAME}?start=support')],
    ]

    reply_markup = InlineKeyboardMarkup(extract_keyboard)

    # Send the additional options as a message

    await update.callback_query.message.reply_text('🀄️🀄️Company Fullz for various use\n\nSAMPLE BELOW\n\nZEROHOLDINGS LLC\n\n11175 CICERO DR SUITE 100,ALPHARETTA, GA 30022\n\nTAX id 46-3220269\n\nOWNER INFO\nPHILLIP MILES\n300 HAYWARD LN,ALPAHRETTA, GA 30022\n\nSSN 255 35 2912\nDOB 07/11/1966\n\n\nPRICE $35\n\n🀄️EXTRACTED TAX INF0 + IDME\n\nPrice - $200-$400', reply_markup=reply_markup, parse_mode='html')


# Callback function for enroll
async def option36_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.callback_query.answer()

    # Construct the keyboard for the additional options when 'Support' is clicked
    extract_keyboard = [
        [InlineKeyboardButton(
            "ENROLL", url=f'https://t.me/{ADMIN_USERNAME}?start=support')],
    ]

    reply_markup = InlineKeyboardMarkup(extract_keyboard)

    # Send the additional options as a message

    await update.callback_query.message.reply_text('🀄Inbox setup - $1200\n\nInfo --> https://t.me/rabbithole420/243\n\nSms spamming classes $1200\n\n info ---> https://t.me/rabbithole420/160\n\nSpamming classes o365 - $1800\n\nMore info --> https://t.me/rabbithole420/154\n\nEmployment job package - $1500\n\nMore info --> https://t.me/rabbithole420/306\n\nMentorship - $3000\n\nMore info --> https://t.me/rabbithole420/156', reply_markup=reply_markup, parse_mode='html')


# Callback function for drainer
async def option37_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.callback_query.answer()

    # Construct the keyboard for the additional options when 'Support' is clicked
    extract_keyboard = [
        [InlineKeyboardButton(
            "Buy Drainer", url=f'https://t.me/{ADMIN_USERNAME}?start=support')],
    ]

    reply_markup = InlineKeyboardMarkup(extract_keyboard)

    # Send the additional options as a message

    await update.callback_query.message.reply_text('🀄️🀄️Crypto Drainers for draining wallets\n\nThese are Dapps + smartcontracts used for draining crypto funds from any decentralized wallet.\n\n🔥All in one drainer with a website + Smart Contracts Included::\n\n📜Claim, Claim Reward, Connect, Execute, Multicall, Security Update, Swap\n\n🀄️ Methods for Asset Withdrawal Native Coins:\n\nSign, Transfer, Smart Contract Tokens: Multiple withdrawal methods including Sign, Approve, Multicall, etc. NFTs: Sign, Transfer, and more. This powerful crypto wallet drainer supports multiple networks:\n\nEthereum\nPolygon\nArbitrum Base Chain\nCelo Network\nCronos\nCanto\nBNB Smart Chain\nAvalanche\nFantom\nOptimism\nHarmony\nKlaytn\n\nPrice: $1200\n\nMore --> https://t.me/rabbitholecustom/22', reply_markup=reply_markup, parse_mode='html')


# Callback function for malware

async def option38_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.callback_query.answer()

    # Construct the keyboard for the additional options when 'Support' is clicked
    extract_keyboard = [
        [InlineKeyboardButton(
            "BUY malware", url=f'https://t.me/{ADMIN_USERNAME}?start=support')],
    ]

    reply_markup = InlineKeyboardMarkup(extract_keyboard)

    # Send the additional options as a message

    await update.callback_query.message.reply_text('🀄Malware RAT for collecting persistent data,CC,Credentials and tokens\n\nPrice - $400\n\nMore info --> https://t.me/rabbitholecustom/22', reply_markup=reply_markup, parse_mode='html')


# Callback function for channels items
async def option31_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.callback_query.answer()

# Construct the keyboard for the additional options when 'channles' is clicked
    extract_keyboard = [
        [InlineKeyboardButton(
            "🧧Main channel ", url=f'https://t.me/rabbithole420')],
        [InlineKeyboardButton("🧧2FA Link related ",
                              url=f'https://t.me/rabbit2fa')],
        [InlineKeyboardButton("🧧Free tools and updates ",
                              url=f'https://t.me/rabbitfreebie')],
        [InlineKeyboardButton("🧧Visuals + happy transactions",
                              url=f'https://rabbithole4ogs.com/channel/visuals/messages.html')],
        [InlineKeyboardButton("🧧WEBSITE", url=f'https://rabbithole4ogs.com')],

        [InlineKeyboardButton("🧧Bank Logs, Checks and Co ",
                              url=f'https://t.me/azalogsandaccs')],

        [InlineKeyboardButton(
            "🧧Custom tools and services,web3+ ", url=f'https://t.me/rabbitholecustom')],
        [InlineKeyboardButton(
            "🧧Gift items for Cl\n\nflowers,pizza,ring+ ", url=f'https://t.me/rabbitholegift')],
        [InlineKeyboardButton("🧧Got a Tool suggestion? Complaint or Feedback ",
                              url=f'https://storyzink.com/m/mx9lw0sc?s=2')],
        [InlineKeyboardButton("🧧Reach out to MP\n\n ",
                              url=f'https://t.me/bishopzeit')],
        [InlineKeyboardButton("🧧Reach out to DEV1ISH \n\n ",
                              url=f'https://t.me/devrabbit1')],
        [InlineKeyboardButton("🧧Reach out to SEUN\n\n ",
                              url=f'https://t.me/tendrilsofficial')],
        [InlineKeyboardButton("🧧SELL YOUR CRYPTO\n\n ",
                              url=f'https://t.me/bigxxxl01')],




    ]

    reply_markup = InlineKeyboardMarkup(extract_keyboard)

    # Send the additional options as a message

    await update.callback_query.message.reply_text('Useful links', reply_markup=reply_markup, parse_mode='html')


# Callback function for "sell your crypto"
async def option35_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.callback_query.answer()

    # Construct the keyboard for the additional options when 'Support' is clicked
    extract_keyboard = [
        [InlineKeyboardButton(
            "Sell Coin", url=f'https://t.me/{ADMIN5_USERNAME}?start=support')],
    ]

    reply_markup = InlineKeyboardMarkup(extract_keyboard)

    # Send the additional options as a message

    await update.callback_query.message.reply_text('<b>We BUY all major cryptocurrencies.</b>\n\n🀄Fast confirmations and naira payments\n\n🀄Online 24/7 for swift responses\n\n🀄We are buying at the best rate\n\n📞 <b>+2348078004473\n@shoqhere</b>\n\nQuick steps to follow:\n\nRequest for rate\n\nAgree on rate\n\nSend cryptocurrency\n\nWait for a short period of time to confirm\n\nDrop naira account for payment\n\nThat’s a deal well done!', reply_markup=reply_markup, parse_mode='html')


# Callback function for Merchant links items
async def option30_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.callback_query.answer()

    # Construct the keyboard for the additional options when 'MERCHANT LINKS' is clicked
    extract_keyboard = [
        [InlineKeyboardButton(
            "Use a link", url=f'https://t.me/{ADMIN_USERNAME}?start=support')],
    ]

    reply_markup = InlineKeyboardMarkup(extract_keyboard)

    # Send the additional options as a message

    await update.callback_query.message.reply_text('🀄️🀄️Merchant links for receiving invoice payments,credit card,Cash app,Apple pay,Payment from canada,usa,europe and co(office365 payments) Or Receiving funds from Cls.These merchant links are widely accepted\n\n\nSee more ---> https://t.me/rabbithole420/40', reply_markup=reply_markup, parse_mode='html')


# Callback function for custom orders

async def option24_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    # Send the additional options as a message

    await update.callback_query.message.reply_text('🀄️🀄️<b>CUSTOM REQUESTS</b>\n\n\n<b>Website building services\n\nWeb3 Dapps for crypto drainners\n\nWallet scanners\n\nTelegram scrapper bot\n\nTwitter watch bot\n\nRUG PULL CONTRACTS FOR CRYPTO\n\nHoney Pots for crypto\n\nMalwares,Rats and Stealers\n\nfAKE BTC SENDER\n\nClipboard stealer for copy paste crypto hijacking and more</b>....Join here to view our CUSTOM JOBS AND TOOLS\n\nhttps://t.me/rabbitholecustom', parse_mode='html')


# Callback function for freebies
async def option20_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    # Send the additional options as a message

    await update.callback_query.message.reply_text('🀄️🀄️Because we are Ogs we give freebies such as <b>credit cards,tips,free tools, softwares and free updates</b> we find on the internet that an OG might need\n\nJoin the freebies channel below\n\nhttps://t.me/+2yMIbanV8EtiMGQ0', parse_mode='html')


# Callback function for senders
async def option21_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()


# Construct the keyboard for the additional options when 'Support' is clicked
    otp_options_keyboard = [
        [InlineKeyboardButton(
            "Buy Sender", url=f'https://t.me/{ADMIN_USERNAME}?start=support')],
    ]

    reply_markup = InlineKeyboardMarkup(otp_options_keyboard)

    # Send the additional options as a message

    await update.callback_query.message.reply_text('🀄️🀄️Senders\n\n\n🀄️<b>BLAST SENDER</b>\n\nFully licensed\n\nSupports Admin connector for sending via admin\n\nSupports attachment\n\n2YEARS access\n\nMulti Smtp,throttle and easy letter manipulation\n\n<b>Price</b> - $100\n\n🀄️<b>Gammadyne Sender</b>\n\nFully licensed\n\nProfessional unlimited\n\nSupports attachment\n\nMulti Smtp,throttle and good for inbox projects\n\nLife time access\n\n<b>Price</b> - $100\n\n\n🀄️<b>Fisher Sender</b>\n\nHot sender with super scripted attachment capabilities\n\nExcellent for inbox setup\n\nSupports attachment\n\nImage-letter,Qr code,Multi function\n\nLife time access\n\n<b>Price</b> - $250\n\n🀄️<b>Super Mailer</b>\n\nFully licensed\n\nSupports Admin connector for sending via admin\n\nSupports attachment\n\nLife time access\n\nMulti Smtp,throttle and good for inbox projects\n\n<b>Price</b> - $100\n\n\n\n🀄️<b>TELYNX SMS SENDER </b>\n\nFully licensed\n\nSends SMS WORLDWIDE\n\nSupports LINKS\n\nBest for sms spamming\n\nStraight to number.\n\n<b>Price</b> - $150\n\n🀄️<b>Node Mailer</b>\n\nFully licensed\n\nSupports Admin connector for sending via admin\n\nSupports attachment\n\nLife time access\n\nMulti Smtp,throttle and good for inbox projects\n\n<b>Price</b> - $120\n\n🀄️<b>TELYNX SMS SENDER </b>\n\nFully licensed\n\nSends SMS WORLDWIDE\n\nSupports LINKS\n\nBest for sms spamming\n\nStraight to number.\n\n<b>Price</b> - $150\n\n🀄️<b>Rabbit SMS SENDER</b>\n\nYEARLY LICENSED\n\nEasiest to use, You get login access,no need setup\n\nSupports Links\n\nLife time access\n\nCan send world wide\n\n Samples and guide --> https://t.me/rabbithole420/265 \n\n<b>Price</b> - $150 yearly plan', reply_markup=reply_markup, parse_mode='html')


# Callback function for SMTP
async def option27_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.callback_query.answer()

    # Construct the keyboard for the additional options when 'Support' is clicked
    otp_options_keyboard = [
        [InlineKeyboardButton(
            "Buy SMTP", url=f'https://t.me/{ADMIN_USERNAME}?start=support')],
    ]

    reply_markup = InlineKeyboardMarkup(otp_options_keyboard)

    # Send the additional options as a message

    await update.callback_query.message.reply_text('🀄️🀄️<b>SMTPs we list are inbox smtps with reputation and good limits we have tested over time. We allow test to two emails. These smtps will inbox for several project so they are pricy</b>\n\n\n🀄️<b>ZIMBRA SMTP - PRICE $80 </b>\n\nHacked SMTP\n\n10K daily Sending Limit\n\nIt Can Work with Attachment  and Link\n\n🀄️<b>T-Mobile SMTP - PRICE $90</b>\n\n\nHacked SMTP\n\n7 - 10 K daily Sending Limit\n\nIt Can Work with Attachment  and Link\n\n\n🀄️<b>GMOBB Japan SMTP - PRICE $150</b>\n\nHacked SMTP\n\n10k - 15K daily Sending Limit\n\nIt Can Work with Attachment  and Link\n\n🀄️<b>Kagoya SMTP - PRICE $350</b>\n\n\nHacked SMTP\n\n50K daily Sending Limit\n\nIt Can Work with Attachment  and Link\n\n\n\n🀄️<b>DREAMHOST SMTP - PRICE $110</b>\n\nHacked SMTP\n\n10K daily Sending Limit\n\nIt Can Work with Attachment  and Link\n\n\n\n🀄️<b>Mailgun SMTP – 50K Limit - PRICE $300</b>\n\nBEST FOR INBOX, GUARRANTEE FOR INBOX PROJECT\n\nIt Can Work with Attachment  and Link\n\n\n\n\n\n🀄️<b>Wadax Japan SMTP – 50K Limit- PRICE $250</b>\n\nSUPER FOR INBOX, GUARRANTEE FOR INBOX PROJECT\n\nIt Can Work with Attachment  and Link\n\n\n\n\n🀄️<b>MAIL-JET Japan SMTP – 50K Limit- PRICE $250</b>\n\nSUPER FOR INBOX with GUARRANTEE FOR INBOX PROJECT\n\nIt Can Work with Attachment  and Link\n\n\n🀄️<b>MANDRILL SMTP – 50K Limit- PRICE $300</b>\n\nSUPER FOR INBOX and GUARRANTEE FOR INBOX PROJECT\n\nIt Can Work with Attachment  and Link\n\nThe best out there\n\n\n🀄️<b>AWS SMTP – 50K Limit- PRICE $300</b>\n\nBEST SINGLE SMTP OUT THERE and GUARRANTEE FOR INBOX PROJECT\n\nIt Can Work with Attachment  and Link\n\n\n\nConsole for aws,mandrill and co available too\n\n\nPRICE $800-$900', reply_markup=reply_markup, parse_mode='html')


# Callback function for leads
async def option26_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()


# Construct the keyboard for the additional options when 'Support' is clicked
    otp_options_keyboard = [
        [InlineKeyboardButton(
            "Buy leads", url=f'https://t.me/{ADMIN_USERNAME}?start=support')],
    ]

    reply_markup = InlineKeyboardMarkup(otp_options_keyboard)

    # Send the additional options as a message

    await update.callback_query.message.reply_text('🀄️🀄️<b>LEADS</b>\n\n\nB2B LEADS (5K - 50K) PRICE $25 - $150 \n\nCEO/CFO LEADS (5K - 20K) - PRICE $300 - $2000 \n\nREAL ESTATE LEADS (5K - 50K) PRICE $50 - $150\n\nLAW FIRMS LEADS  (5K - 50K) PRICE $50 - $150\n\nEMPLOYMENT LEADS  (5K - 50K) PRICE $100 - $700\n\nFIN TECH LEADS (5K - 50K) PRICE $50 - $150\n\n\nCountry specific leads available\n\n\nBANK LEADS (5K - 200K) PRICE $50 - $500\n\nLAW FIRMS LEADS  (5K - 50K) PRICE $50 - $700\n\nVALIDATED NUMBER LEADS LEADS (5K - 500K) PRICE $50 - $500\n\nLAW FIRMS LEADS  (5K - 50K) PRICE $50 - $500', reply_markup=reply_markup, parse_mode='html')


# Callback function for linkedin
async def option33_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    # Construct the keyboard for the additional options when 'Support' is clicked
    otp_options_keyboard = [
        [InlineKeyboardButton(
            "Buy linkedin", url=f'https://t.me/{ADMIN_USERNAME}?start=support')],
    ]

    reply_markup = InlineKeyboardMarkup(otp_options_keyboard)

    # Send the additional options as a message

    await update.callback_query.message.reply_text('🀄️🀄️<b>LinkedIn With sales Navigator + email access </b>\n\n\n🀄️<b>PRICE $60</b>', reply_markup=reply_markup, parse_mode='html')


# callback function for social media accounts


async def option18_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    # Construct the keyboard for the additional options when 'Support' is clicked
    otp_options_keyboard = [
        [InlineKeyboardButton(
            "Buy Account", url=f'https://t.me/{ADMIN3_USERNAME}?start=support')],
    ]

    reply_markup = InlineKeyboardMarkup(otp_options_keyboard)

    await update.callback_query.message.reply_text('<b>🀄️ SOCIAL MEDIA ACCOUNT LIST🀄️</b>\n\n\n🧧Verified twitter account with minimun 5k followers\n\nPrice - $120\n\n🧧Verified instagram (minimum 5k followers)\n\nPrice - $250\n\n\n<b>🀄️INSTAGRAM ACCOUNTS (with followers)</b>\n\n\n20k followers[5years old] - $60 \n\n10k followers[4years old] - $40\n\n5k followers[5years old] - $20\n\n2k followers[3years old] - $10\n\n\n🀄️<b>TWITTER ACCOUNTS</b>\n\n500 followers - $10\n\n1000 followers - $20\n\n2000 followers -$35\n\n\n🀄️REDDIT ACCOUNTS\n\n\n100+ karma - $10\n\n500+ karma - $15\n\n1k+ karma - $25\n\n\n5k+ karma - $50🀄️<b>Facebook ACCOUNTS</b>\n\nRandom facebook\n\n5years - No pictures - No profile\nPrice - $10\n\nRandom facebook\n\n5years - with 100+ Friends\nPrice - $17\n\nRandom facebook\n\n6years - with 1k+ Friends\nPrice - $30\n\nUSA facebook\n\n6years - with Friends\nPrice - $30\n\nDATING facebook\n\n6years - with Friends\n\nActivities for trust on facebook\nPrice - $50\n\n\n<b>🀄️REDDIT ACCOUNTS</b>\n\n100+ karma - $10\n\n500+ karma - $15\n\n1k+ karma - $25\n\n5k+ karma - $50\n\n\n<b>🀄Gmail  ACCOUNTS</b>\n\nGmail verified via sms already - $5\n\nGmail account - $3\n\nAged gmail (5yrs) - $10\n\n\nAged gmail (10yrs) - $15\n\n\n🀄️<b>TIKTOK ACCOUNTS</b>\n\nTiktok AD account USA - $10\n\nTIKTOK NEW ACCOUNT  - $3\n\nTiktok aged account $5', reply_markup=reply_markup, parse_mode='html')


# Callback function for '2FA' button

async def option17_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    # Construct the keyboard for the additional options when 'Support' is clicked
    nonvbv_options_keyboard = [
        [InlineKeyboardButton(
            "Credit cards", url=f'https://t.me/{ADMIN5_USERNAME}?start=support')],
    ]

    reply_markup = InlineKeyboardMarkup(nonvbv_options_keyboard)

    await update.callback_query.message.reply_text('<b>NON VBV cards with known balances</b>\n\nCURRENT NON VBV CARDs Prices list\n\n\nBalance: $1500 - $2500\n\n\n($50~ $70)\n\nBalance: $2000 - $4000\n\n\n($70~ $150)\n\nBalance: $$4000 - $7000\n\n\n($150 - $300)\n\n\nBalance: $$7000 - $16k\n\n\n($300 - $ $600)\n\nNO OTP OR VERIFICATION NEEDED\n\nGuide --> https://t.me/rabbithole420/390', reply_markup=reply_markup, parse_mode='html')


# Callback function for additional options when 'bank logs' is clicked
async def option23_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.callback_query.answer()

    # Send the additional options as a message

    await update.callback_query.message.reply_text('🀄️🀄️ Join the channel to view our bank log list\n\nWe also have Bank accounts open up as a service.\n\n<b>🀄️Company logs</b>\n\n<b>🀄️Direct Deposit log</b>\n\n<b>🀄️ACH logs</b>\n\n\n\n<b>🀄️Bank open ups</b>\n\n\n\n<b>🀄️SOFI,CHASE,PAYPAL,KRAKEN AND CO</b>\n\n🀄️<b>Bill pay logs</b>\n\n<b>Wire checks logs</b>\n\n<b>Mobile deposit logs </b>\n\nJOIN HERE https://t.me/azalogsandaccs', parse_mode='html')


# Callback function for '2FA' button
async def option14_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.callback_query.answer()

    # Assuming there's a function to deduct the amount from the user's account
    user_id = update.effective_user.id
    deducted_amount = 300  # The amount to deduct

    # Deduct the amount from the user's account (You need to implement this function)
    if deduct_amount_from_user(user_id, deducted_amount):
        # If the deduction is successful, proceed

        # Code to send user ID and plan details to admin
        await send_plan_details_to_admin(update.effective_user.id, "1 month plan", context)

        # Create an inline keyboard with a "Buy" button that redirects to the support chat
        keyboard200 = [[InlineKeyboardButton(
            "You are all set for 1Month!", url=f'https://t.me/{ADMIN_USERNAME}')]]
        twofa200_options_reply_markup = InlineKeyboardMarkup(keyboard200)

        # Send the additional options as a message
        await update.callback_query.message.reply_text('Please send your result-handle to admin for set-up. Also follow channel at https://t.me/rabbithole420 for detailed information on usage', reply_markup=twofa200_options_reply_markup)
    else:
        # If the deduction fails, handle the error (You need to implement error handling)
        await update.callback_query.message.reply_text('You have insufficient funds. please fund your account!')


# function to send id + plan to admin

# Function to send user ID and plan details to admin
async def send_plan_details_to_admin(user_id, plan, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Replace 'ADMIN_CHAT_ID' with the actual chat ID of the admin
        admin_chat_id = ADMIN_CHATID

        # plan = 'month'

        # Compose the message
        message = f"User ID: {user_id}\nPlan: {plan}"

        # Send the message to the admin
        await context.bot.send_message(chat_id=admin_chat_id, text=message)

        # You can also log the message or perform additional actions here

    except Exception as e:
        # Handle exceptions (e.g., network errors or bot permissions issues)
        print(f"Error sending plan details to admin: {str(e)}")


# callback for 2fa options
async def option15_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    # Assuming there's a function to deduct the amount from the user's account
    user_id = update.effective_user.id
    deducted_amount = 200  # The amount to deduct

    # Deduct the amount from the user's account (You need to implement this function)
    if deduct_amount_from_user(user_id, deducted_amount):
        # If the deduction is successful, proceed

        # Code to send user ID and plan details to admin
        await send_plan_details_to_admin(update.effective_user.id, "14 DAYS plan", context)

        # Create an inline keyboard with a "Buy" button that redirects to the support chat
        keyboard120 = [[InlineKeyboardButton(
            "You are all set for 14DAYS!", url=f'https://t.me/{ADMIN_USERNAME}')]]
        twofa120_options_reply_markup = InlineKeyboardMarkup(keyboard120)

        # Send the additional options as a message
        await update.callback_query.message.reply_text('Please send your result-handle to admin for set-up. Also follow channel at https://t.me/rabbithole420 for detailed information on usage', reply_markup=twofa120_options_reply_markup)
    else:
        # If the deduction fails, handle the error (You need to implement error handling)
        await update.callback_query.message.reply_text('You have insufficient funds. please fund your account!')


########################################### REDIRECT ##############################################################


# Callback function for 'Redirect' button
async def option2_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Callback function for 'Redirect' button
    await update.callback_query.answer()

    # Construct the keyboard for the additional options when 'Redirect' is clicked
    redirect_options_keyboard = [
        [InlineKeyboardButton("BUY", url=f'https://t.me/{ADMIN_USERNAME}')],
    ]

    redirect_options_reply_markup = InlineKeyboardMarkup(
        redirect_options_keyboard)

    # Send the additional options as a message
    await update.callback_query.message.reply_text('<b>REDIRECTS | LINK ENCRYPTER | ANTIBOT | MAGIC LINK</b>\n\n\nREDIRECTS - Price $20/redirect\n\nLINK ENCRYPTER - Price $20\n\nANTIBOT - Price $20\n\nDOUBLE REDIRECT - Price $30\n\n\nAmazon redirects - Price $150\n\n\nOpen redirect - Price $150\n\n\nGuide on these tools --> https://t.me/rabbithole420/78', reply_markup=redirect_options_reply_markup, parse_mode="html")


# Callback function for 'Redirect' button


####################################### RESUME ################################################

# Callback function for Resume options when 'resume' is clicked
async def option11_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Callback function for 'RESUME' button
    await update.callback_query.answer()

    # Construct the keyboard for the additional options when 'Resume' is clicked
    resume_options_keyboard = [
        [InlineKeyboardButton("$1.5 - Per Usa resume ",
                              url=f'https://t.me/{ADMIN6_USERNAME}')],
        [InlineKeyboardButton(" $2 - Per Aud resume",
                              url=f'https://t.me/{ADMIN6_USERNAME}')]
    ]

    resume_options_reply_markup = InlineKeyboardMarkup(resume_options_keyboard)

    # Send the additional options as a message
    await update.callback_query.message.reply_text('We get our resumes from ziprecruiter,linkedin and indeed.\n\nSelect country :', reply_markup=resume_options_reply_markup)


########################################### OFFICE ##############################################################


# Callback function for additional options when 'Office Boxes' is clicked
async def option4_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Callback function for 'Office Boxes' button
    await update.callback_query.answer()

    # Construct the keyboard for the additional options when 'Office Boxes' is clicked
    office_boxes_options_keyboard = [
        [InlineKeyboardButton(
            "Buy ", url=f'https://t.me/{ADMIN6_USERNAME}?start=buy')],
    ]

    reply_markup = InlineKeyboardMarkup(office_boxes_options_keyboard)

    # Send a message to the user with the inline keyboard

    await update.callback_query.message.reply_text("message admin and ask for office365 boxes.", reply_markup=reply_markup)

########################################### Admin ##############################################################


# Callback function for  'Admin' button
async def adminbutton(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Create an inline keyboard with a "Buy" button that redirects to the support chat
    keyboard = [[InlineKeyboardButton(
        "Contact Admin", url=f'https://t.me/{ADMIN_USERNAME}')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send a message to the user with the inline keyboard

    await update.message.reply_text("<b>Hey Friend!here's a list of TiPs so we have an understanding.</b>\n\nPlease be precise with your messages, we won't respond to 'Hi' or messages that are not to the point.\n\nHere's a list of Frequently Asked Questions:\nHOW DOES YOUR MERCHANT LINK WORK?\n\nOur merchant links are links that you, your cl, your box job or anyone can use in making credit card payments, ACH payments,Applepay,cashapp,international payments.\nIt takes  2-3days for payments to drop for old merchants.\n\nNew merchants 7-10days.\nOur cut can range from 35-45% depending on the amount and merchant.\n\nyou get paid in btc.\n\nHOW LONG DOES YOUR RDP LAST?\n\nOur rdps can stay on for 6month - 1 year. We offer guarrantee on them.\nyou'd have to renew your subscription every month to keep it on. otherwise at the end of a month it will be turnt off automatically.\n\nYour files are backup so you won't lose them.\n\nOFFICE BOXES QUESTIONS.\nQuestions like...\nPICK A BOX FOR ME THAT CONTAINS TRANSACTION OR SEND ME BOX WITH CFO CHAT\n\nWill be ignored because if we handpick boxes for you How is that fair to everyone else?\n\nBoxes are freshly Spammed and are mostly usa boxes.\n\nMost will contain cards,transactions,invoices,ids,accounts,credentials,logs,and more. So it's up to you to utilize based on how well you know the job.\n\ni'll send a list of available domains to you and you pick, Make payment by either Funding your account via the 'Fund wallet' Button or you ask for a crypto,naira or rands account details. after payment we send logs,if you have issue with logging in please reach out. always use a VPN or log in via rdp. You know this og.\n\nBoxes that don't have transaction could have log,or ccs or accounts or be used to create more tools depending on if it has priviledges of an admin and other settings, could be used for b2b or the smtp used for sending out messages via senders,you could payroll it or blackmail the box.\n\nAlot you can do so it's up to you to know your stuff\n\n\nIS ONE BOX SOLD TO MORE THAN ONE PERSON?\n\nOf course not! Once a box is bought already we take it off the list,before selling a box we confirm if it's been sold already.The smart ones here can confirm by trying to buy same accounts from different handles to confirm yourself.\n\nReview any boxes bought within the space of when you bought it, coming back to complain after 24hrs+ will be ingnored.\n\nIf you have inferior extraction tools and can't get the most out of a box it's not on us to teach you because you bought a box\n\nWe will replace a box that can't send out.FOR SENDERS,MAILERS,SOFTWARE-TOOLS THAT ARE NOT LISTED ON THE STORE PLEASE VISIT THE CHANNEL at https://t.me/rabbithole420 or contact admin and ask directly.\n\nThe store is constantly being upgraded to accept more Vendor and products an OG needs.\nIF you are a vendor feel free to reach out.", reply_markup=reply_markup, parse_mode='html')

########################################### SUPPORT ##############################################################


################ RDPS #################################################################


# Callback function for additional options when 'RDPS' is clicked
async def option3_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Callback function for 'RDPS' button
    await update.callback_query.answer()

    keyboard = [[InlineKeyboardButton(
        "Contact Admin", url=f'https://t.me/{ADMIN6_USERNAME}')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.reply_text('🀄️🀄️RDPS\n\n<b>microsoft azure Rdps best ip reputations and very reliable\n\nCpu: 4 Cores Xeon Silver\n\n4GB DDR4,corei7 laptop equivalent, with renewable monthly subscription.</b>\n\n<b>USA,CANADA,EUROPE,GERMANY RDPS - $30\n\nCpu: 8 Cores Xeon Silver\n\n8GB/16GB DDR4,corei9+ laptop equivalent, with renewable monthly subscription.</b>\n\nUSA,CANADA,EUROPE,GERMANY RDPS - $50\n\n\n<b>ADMIN RDP(PORT 25)</b>\n\nSuper for spamming\n\n<b>CPU: Cores XEON Silver\n\n4GB DDR4,corei7 laptop equivalent, with renewable monthly subscription.</b>\n\nUSA,CANADA,EUROPE,GERMANY\n\nRDPSPort 25 open\nClean IP\n\nWorks well with admin connectors\n\nPrice - $50-$80 (depending on ram)\n\nMore on admin rdp ------>https://t.me/rabbithole420/406 ', reply_markup=reply_markup, parse_mode='html')


# Function to get the total number of users in the database
async def get_user_count(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Check if the username is in the allowed list
    username = update.effective_user.username

    if username not in ALLOWED_USERNAMES:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Imposter! You are not Bishop nor Mp\n\nThe Zeitgeist Movement is a global sustainability advocacy organization that promotes a transition to a more sustainable, equitable, and humane global society. It advocates for a socioeconomic system which is based on responsible resource management, socioeconomic equality, and a sustainable ecological footprint. It aims to unify humanity through a new 'train of thought' transcending national, religious, and political divisions."
        )
        return

    try:
        # Reference to the 'user_profiles' collection
        user_profiles_ref = firestore.client().collection('user_profiles')

        # Get all documents in the collection
        users = user_profiles_ref.stream()

        # Count the number of documents
        user_count = sum(1 for _ in users)

        # Send a message with the user count
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Total number of users in the database: {user_count}"
        )
    except Exception as e:
        # Handle exceptions
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Error retrieving user count: {str(e)}"
        )


############################### message section ####


# a user

async def sendit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Extract chat_id and message from the command arguments
    args = context.args
    if len(args) >= 2:
        chat_id = args[0]
        message = ' '.join(args[1:])
        try:
            await context.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            print(f"Error sending message to user {chat_id}: {str(e)}")
    else:
        await update.message.reply_text('Usage: /sendit <chat_id> <message>')


# all users

async def broadcastit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = ' '.join(context.args)
    if message:
        user_profiles_ref = firestore.client().collection('user_profiles')
        try:
            users = user_profiles_ref.stream()
            for user in users:
                user_data = user.to_dict()
                chat_id = user_data.get('chat_id')
                try:
                    await context.bot.send_message(chat_id=chat_id, text=message)
                    print(f"Message sent to {chat_id}")
                except Exception as e:
                    print(f"Error sending message to user {chat_id}: {str(e)}")
        except Exception as e:
            print(f"Error broadcasting message: {str(e)}")
    else:
        await update.message.reply_text('Usage: /broadcastit <message>')


# Create a message and save in DB @vulpescode
async def create_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the message from the command arguments
    message = ' '.join(context.args)
    if message:
        # Save to Firestore
        doc_ref = firestore.client().collection(
            'routine_messages').add({'message': message})

        # Create the message with a delete button
        keyboard = [[InlineKeyboardButton("Delete", callback_data=doc_ref.id)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the message to the channel
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_markup)
        print(f"Message created: {message}")
    else:
        await update.message.reply_text("Please provide a message.")


# Delete message from DB and channel @vulpescode
async def delete_message(doc_id: str, bot, chat_id: int):
    # Delete the document with the specified ID from the 'routine_messages' collection
    firestore.client().collection('routine_messages').document(doc_id).delete()
    print(f"Message with ID {doc_id} deleted.")
    await bot.send_message(chat_id=chat_id, text="The message has been deleted.")


# add product  @vulpescode
async def add_product_to_firestore(name: str, price: float, category: str, status: bool) -> dict:
    # Validate compulsory fields
    if not name or not category:
        raise ValueError("Name and category are compulsory fields.")

    # Create a Firestore client
    db = firestore.client()

    # Create a new product document in the 'products' collection
    product_ref = db.collection('products').add({
        'name': name,
        'price': price,
        'category': category,
        'status': status
    })

    # Return the newly created product data with its ID
    return {
        'id': product_ref.id,
        'name': name,
        'price': price,
        'category': category,
        'status': status
    }

# add product to DB  @vulpescode


async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Extract parameters from the command arguments
    if len(context.args) < 4:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: /add_product <name> <price> <category> <status>")
        return

    name = context.args[0]
    # Make sure to handle potential conversion errors
    price = float(context.args[1])
    category = context.args[2]
    status = context.args[3].lower() == 'true'  # Convert to boolean

    try:
        product = await add_product_to_firestore(name, price, category, status)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Product added successfully: {product}")
    except ValueError as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=str(e))
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred while adding the product.")


# fetch products from DB and channel @vulpescode
async def fetch_products_from_firestore() -> List[dict]:
    products = []
    # Fetch products from the 'products' collection
    docs = firestore.client().collection('products').stream()
    for doc in docs:
        product_data = doc.to_dict()
        # Add each product dictionary to the list
        products.append(product_data)
    return products


# post products from DB and channel @vulpescode
async def post_routine_products(bot, channel_id, products, interval_seconds):
    while True:
        for product in products:
            product_name = product.get('name', 'Unknown Product')
            product_status = product.get('status', 'Status Not Available')
            message = f"Product: {product_name}\nStatus: {product_status}"
            await bot.send_message(chat_id=channel_id, text=message)
        await asyncio.sleep(interval_seconds)


# command handlers to start auto posting product status @vulpescode
async def start_routine_posting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Assuming the command is sent in the channel
    channel_id = update.effective_chat.id

    # Fetch products from Firestore
    products = await fetch_products_from_firestore()

    if not products:
        await context.bot.send_message(chat_id=channel_id, text="No products found in Firestore.")
        return

    interval_seconds = 21600  # Post every 6 hours (21600 seconds)
    task = asyncio.create_task(post_routine_products(
        context.bot, channel_id, products, interval_seconds))
    await context.bot.send_message(chat_id=channel_id, text="Routine product posting started.")


# Callback function to handle button clicks
async def color_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Acknowledge the callback
    # You can update the message or take action based on the button clicked
    if query.data == 'red':
        await query.edit_message_text(text="You clicked Red!")
    elif query.data == 'green':
        await query.edit_message_text(text="You clicked Green!")

    # Update the message with the new color (e.g., by editing the message or sending a new one)


if __name__ == '__main__':
    # Create the bot application using the ApplicationBuilder
    application = ApplicationBuilder().token(TOKEN).build()

    # Define the CommandHandler for the '/start' command
    start_handler = CommandHandler('start', start)

    # Define the CommandHandler for the '/product' command
    product_handler = CommandHandler('product', product)
    payment_handler = CommandHandler('payment', initiate_payment)
    profile_handler = CommandHandler('profile', profile)
    start_routine_handler = CommandHandler(
        'routinestart', start_routine_posting)
    post_routine_handler = CommandHandler('routinepost', post_routine_products)
    create_post_handler = CommandHandler('createpost', create_message)
    fetch_product_handler = CommandHandler(
        'fetchproduct', fetch_products_from_firestore)

    send_user_handler = CommandHandler('sendit', sendit)
    broadcast_handler = CommandHandler('broadcastit', broadcastit)
    delete_message_handler = CommandHandler('deletemsg', delete_message)
    # add_product_handler = CommandHandler('addproduct', add_product_to_firestore)
    add_product_handler = CommandHandler('addproduct', add_product)

    # CommandHandler for the 'get_user_count' command
    get_user_count_handler = CommandHandler('usercount', get_user_count)

    # Add the 'get_user_count' command handler to the application
    application.add_handler(get_user_count_handler)

    # Define the CallbackQueryHandlers for each button
    application.add_handler(CallbackQueryHandler(
        option1_callback, pattern='^option1$'))
    application.add_handler(CallbackQueryHandler(
        option2_callback, pattern='^option2$'))
    application.add_handler(CallbackQueryHandler(
        option3_callback, pattern='^option3$'))
    application.add_handler(CallbackQueryHandler(
        option4_callback, pattern='^option4$'))
    application.add_handler(CallbackQueryHandler(
        option11_callback, pattern='^option11$'))
    application.add_handler(CallbackQueryHandler(
        option17_callback, pattern='^option17$'))
    application.add_handler(CallbackQueryHandler(
        option21_callback, pattern='^option21$'))
    application.add_handler(CallbackQueryHandler(
        option26_callback, pattern='^option26$'))
    # application.add_handler(CallbackQueryHandler(option29_callback, pattern='^option29$'))
    application.add_handler(CallbackQueryHandler(
        option37_callback, pattern='^option37$'))

    application.add_handler(CallbackQueryHandler(
        option27_callback, pattern='^option27$'))
    application.add_handler(CallbackQueryHandler(
        option36_callback, pattern='^option36$'))

    application.add_handler(CallbackQueryHandler(
        option20_callback, pattern='^option20$'))

    application.add_handler(CallbackQueryHandler(handle_button_click))

    application.add_handler(send_user_handler)
    application.add_handler(broadcast_handler)
    application.add_handler(start_routine_handler)
    application.add_handler(post_routine_handler)
    application.add_handler(create_post_handler)
    application.add_handler(fetch_product_handler)
    application.add_handler(delete_message_handler)
    application.add_handler(add_product_handler)

    # Additional Callbacks

    # application.add_handler(CallbackQueryHandler(option9_callback, pattern='^option9$'))
    # application.add_handler(CallbackQueryHandler(option10_callback, pattern='^option10$'))
    application.add_handler(CallbackQueryHandler(
        option14_callback, pattern='^option14$'))
    application.add_handler(CallbackQueryHandler(
        option15_callback, pattern='^option15$'))
    application.add_handler(CallbackQueryHandler(
        option23_callback, pattern='^option23$'))
    application.add_handler(CallbackQueryHandler(
        option18_callback, pattern='^option18$'))
    # application.add_handler(CallbackQueryHandler(option22_callback, pattern='^option22$'))
    # application.add_handler(CallbackQueryHandler(option24_callback, pattern='^option24$'))
    application.add_handler(CallbackQueryHandler(
        option28_callback, pattern='^option28$'))
    application.add_handler(CallbackQueryHandler(
        option31_callback, pattern='^option31$'))
    application.add_handler(CallbackQueryHandler(
        option32_callback, pattern='^option32$'))
    # application.add_handler(CallbackQueryHandler(option33_callback, pattern='^option33$'))
    # application.add_handler(CallbackQueryHandler(option34_callback, pattern='^option34$'))
    application.add_handler(CallbackQueryHandler(
        option35_callback, pattern='^option35$'))
    application.add_handler(CallbackQueryHandler(
        option38_callback, pattern='^option38$'))
    application.add_handler(CallbackQueryHandler(
        option39_callback, pattern='^option39$'))
    application.add_handler(CallbackQueryHandler(
        option40_callback, pattern='^option40$'))

    # Add the callback query handler to the application builder
    application.add_handler(CallbackQueryHandler(color_button_callback))

    application.add_handler(CallbackQueryHandler(
        option30_callback, pattern='^option30$'))

    application.add_handler(CallbackQueryHandler(
        option25_callback, pattern='^option25$'))

    # application.add_handler(CallbackQueryHandler(option19_callback, pattern='^option19$'))

    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, menusorter))

    # Add the 'start' command handler to the application
    application.add_handler(start_handler)
    application.add_handler(product_handler)
    application.add_handler(payment_handler)
    application.add_handler(profile_handler)

    # Start the bot polling
    application.run_polling()
