from aiogram import types
from firebase_admin import db
import asyncio
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_errors.log"),  # Log to a file
        logging.StreamHandler()  # Also log to console
    ]
)


async def start(message: types.Message):
    user_id = message.chat.id
    username = message.from_user.username if message.from_user.username else str(
        user_id)

    # Check if user profile exists
    user_ref = db.reference(f"users/{user_id}")
    user_data = user_ref.get()

    if user_data is None:
        # Create a new user profile with Telegram username and balance of 0
        user_ref.set({
            'username': username,
            'balance': 0
        })
        balance = 0
    else:
        balance = user_data['balance']

    # Send welcome message
    welcome_text = f"Yoo! {username}! Welcome to Rabbithole \n Your Wallet balance is: {balance}."
    await message.reply(welcome_text, reply_markup=await get_keyboard())


async def get_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Profile", "FAQs", "Fund Wallet",
               "Products", "Orders", "Support"]
    keyboard.add(*buttons)
    return keyboard


# display user profile
async def display_profile(message: types.Message):
    user_id = message.chat.id

    # Retrieve user profile from the database
    user_ref = db.reference(f"users/{user_id}")
    user_data = user_ref.get()

    if user_data is None:
        await message.reply("Profile not found. Please start the bot to create a profile.")
        return

    username = user_data['username']
    balance = user_data['balance']

    # Create a message to display the profile information
    profile_text = (
        f"👤 Username: {username}\n"
        f"💰 Wallet Balance: {balance}"
    )

    await message.reply(profile_text)


# admin add product
async def add_product(message: types.Message, admin_usernames):
    # Check if the user is an admin
    username = message.from_user.username
    if username not in admin_usernames:
        await message.reply("Access Forbidden. You are not authorized to add products.")
        return

    # Parse the command message for product details
    command_args = message.get_args().split(',')

    if len(command_args) < 4:
        await message.reply("Please provide at least: name, category, price, and availability (true/false).")
        return

    # Extract product details
    name = command_args[0].strip()
    category = command_args[1].strip()
    price = float(command_args[2].strip())
    available = command_args[3].strip().lower() == 'true'

    # Initialize features and descriptions as empty lists if not provided
    features = []
    descriptions = []

    # Check for additional arguments for features and descriptions
    if len(command_args) > 4:
        features = [feature.strip() for feature in command_args[4].strip().split(
            ',') if feature.strip()]

    if len(command_args) > 5:
        descriptions = [description.strip() for description in command_args[5].strip(
        ).split(',') if description.strip()]

    # Add the product to the Firebase database
    product_ref = db.reference("products").push()
    product_ref.set({
        'name': name,
        'category': category,
        'price': price,
        'available': available,
        'features': features,
        'descriptions': descriptions
    })

    await message.reply(f"Product '{name}' added successfully!")


# display producxt by categories
async def display_categories(message: types.Message):
    # Retrieve all products from the database
    products_ref = db.reference("products")
    products_data = products_ref.get()

    if not products_data:
        await message.reply("No products available.")
        return

    # Extract categories from products
    categories = set()
    for product in products_data.values():
        if 'category' in product:
            categories.add(product['category'])

    if not categories:
        await message.reply("No categories available.")
        return

    # Create inline keyboard with category buttons
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for category in categories:
        keyboard.add(types.InlineKeyboardButton(
            text=category, callback_data=f"category_{category}"))

    await message.reply("Select a category:", reply_markup=keyboard)


# handle category selection
async def handle_category_selection(callback_query: types.CallbackQuery):
    category = callback_query.data.split("_", 1)[1]
    await display_products_by_category(callback_query.message, category)


# display products
async def display_products_by_category(message: types.Message, category: str):
    # Retrieve products in the selected category from the database
    products_ref = db.reference("products")
    products_data = products_ref.get() or {}

    # Filter products by the selected category
    products_in_category = {
        name: details for name, details in products_data.items()
        if details.get('category') == category
    }

    if not products_in_category:
        await message.reply(f"No products available in the '{category}' category.")
        return

    # Create a message with products and purchase buttons
    product_messages = []
    buttons = []
    for product_name, product_details in products_in_category.items():
        name = product_details.get('name', product_name)
        price = product_details.get('price')
        available = product_details.get('available')
        availability_status = "In Stock ✅" if available else "Sold Out ❌"

        product_message = f"• {name} | ${price} | {category} | {availability_status}"
        product_messages.append(product_message)

        # Add inline button for ordering
        buttons.append(types.InlineKeyboardButton(
            text=f"Order {name}", callback_data=f"order_{name}_{price}"))

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    await message.reply("Available products:\n" + "\n".join(product_messages), reply_markup=keyboard)

# place order


async def process_order(callback_query: types.CallbackQuery):
    data = callback_query.data.split("_")
    product_name = data[1]
    product_price = float(data[2])  # Convert price to float

    # Call the order_product function
    await order_product(callback_query.message, product_name, product_price)


# process order
async def order_product(message: types.Message, product_name: str, product_price: float):
    customer_id = message.chat.id
    customer_name = message.from_user.username
    status = "pending"

    user_ref = db.reference("users").child(str(customer_id))
    user_data = user_ref.get()

    if user_data is None:
        await message.reply("Profile not found. Please start the bot to create a profile.")
        return

    if user_data['balance'] < product_price:
        await message.reply("Insufficient funds")
        return

    # Update user's balance
    user_ref.update({"balance": user_data['balance'] - product_price})

    # Create an order
    order_ref = db.reference("orders").push({
        "product_name": product_name,
        "price": product_price,
        "customer_id": customer_id,
        "customer_name": customer_name,
        "status": status,
    })

    await message.reply("Order placed successfully")


# get user orders
async def get_user_orders(message: types.Message):
    user_id = message.chat.id

    order_ref = db.reference("orders")

    # Get all orders
    orders_data = order_ref.get() or {}

    # Filter orders for the specific user
    user_orders = {
        order_id: order_details
        for order_id, order_details in orders_data.items()
        if order_details.get('customer_id') == user_id
    }

    if not user_orders:
        await message.reply("You have no orders.")
        return

    # Create a message to display user orders
    orders_message = "Your Orders:\n"
    for order_id, order_details in user_orders.items():
        product_name = order_details.get('product_name')
        price = order_details.get('price')
        status = order_details.get('status')
        orders_message += f"Order ID: {order_id} | Product: {product_name} | Price: ${price} | Status: {status}\n"

    await message.reply(orders_message)


# show faq
async def show_faqs_tips(message: types.Message):
    # Example FAQs and tips
    faqs = [
        {
            "question": "HOW DOES YOUR MERCHANT LINK WORK?",
            "answer": """Our merchant links are links that you, your client, your box job, or anyone can use to make credit card payments, ACH payments, Apple Pay, Cash App, and international payments.\n\n It takes 2-3 days for payments to drop for old merchants.\n\n For new merchants, it takes 7-10 days.\n\n Our cut can range from 35 - 45\% \depending on the amount and merchant.\n\n"""
        },
        {
            "question": "HOW LONG DOES YOUR RDP LAST?",
            "answer": """Our rdps can stay on for 6month - 1 year. We offer guarrantee on them.\n\n you'd have to renew your subscription every month to keep it on. otherwise at the end of a month it will be turnt off automatically.\n\n Your files are backup so you won't lose them.\n\n"""
        },
        {
            "question": "IS ONE BOX SOLD TO MORE THAN ONE PERSON?",
            "answer": """Of course not! Once a box is bought already we take it off the list before selling a box we confirm if it's been sold already.\n\nThe smart ones here can confirm by trying to buy same accounts from different handles to confirm yourself.\n\n Review any boxes bought within the space of when you bought it, coming back to complain after 24hrs+ will be ignored.\n\n If you have inferior extraction tools and can't get the most out of a box it's not on us to teach you because you bought a box\n\n We will replace a box that can't send out\n"""
        },
        # Add more FAQs as needed
    ]

    # Construct the message
    faq_message = ""
    for faq in faqs:
        # Replace line breaks in answers with formatted bullet points
        # formatted_answer =
        # Escape the dash
        # formatted_answer = formatted_answer.strip()

        faq_message += f"• *{faq['question']}*\n {faq['answer']}\n\n"

    # Send the message
    await message.reply(faq_message, parse_mode=types.ParseMode.HTML)


# show admins
async def show_help(message: types.Message, admins):
    # Create inline buttons for each admin
    buttons = []
    for admin in admins:
        # Create a button that links to the admin's profile (using their username)
        buttons.append(types.InlineKeyboardButton(
            text=admin, url=f"https://t.me/{admin}"))

    # Create an inline keyboard markup
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    # Send the reply with the inline keyboard
    await message.reply("You need human help? Contact any of our admins:", reply_markup=keyboard)


# fund wallet
async def fund_wallet(message: types.Message):
    # Create inline buttons for Automatic and Manual funding
    buttons = [
        types.InlineKeyboardButton(
            text="Automatic deposit", callback_data="fund_auto"),
        types.InlineKeyboardButton(
            text="Manual deposit", callback_data="fund_manual"),
    ]

    # Create an inline keyboard markup
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)

    # Send the initial message with the inline keyboard
    await message.reply("Choose a funding method:", reply_markup=keyboard)


async def handle_manual_method(callback_query: types.CallbackQuery):
    # This function handles the manual deposit option
    usdt_address = "TD12CZLCkX3G8MaTUpyJ4wprupTmuF82JS"
    btc_address = "bc1q7hgjre0lr9twuwf558qhqdlzwp88xrns6u323e"
    naira_address = "We accept <b>NIGERIAN NAIRA\nSOUTH AFRICAN RANDS</b>\nAccount details will be available upon request."

    message = (
        f"Fund account by making payment to any of the addresses below \n\n"
        f"<b>USDT (TRC20): {usdt_address}</b>\n\n"
        f"<b>BTC:</b> {btc_address}\n\n"
        f"<b>Amount will be funded on your account</b>.\n\n"
        f"{naira_address} \n\n"
        f"<b>NOTE! Please send proof of payment to admin!! otherwise funds won't reflect on your account!</b>"
    )

    # Respond to the callback query to avoid "callback query is not answered" error
    await callback_query.answer()

    # Send the message with funding information
    await callback_query.message.reply(message, parse_mode="HTML")


async def handle_auto_method(callback_query: types.CallbackQuery):

    message = (
        f"coming soon... \n\n"
    )

    # Respond to the callback query to avoid "callback query is not answered" error
    await callback_query.answer()

    # Send the message with funding information
    await callback_query.message.reply(message, parse_mode="HTML")


# get product status
async def get_product_status(message: types.Message, admins, channels):
    # Check if the user is an admin
    username = message.from_user.username
    if username not in admins:
        await message.reply("Access Forbidden. You are not authorized to view product statuses.")
        return

    products_ref = db.reference("products")
    products = products_ref.get()

    if not products:
        await message.reply("No products found.")
        return

    response = []

    for product_id, product_details in products.items():
        product_name = product_details.get('name', 'Unknown Product')
        price = product_details.get('price', 'N/A')
        available = product_details.get('available', False)
        availability_status = "In Stock ✅" if available else "Sold Out ❌"

        response.append(f"{product_name} - ${price} - {availability_status}\n")

    # Join all the product status messages into a single string
    product_status_message = "\n".join(response)

    # Reply to the admin
    await message.reply(product_status_message, parse_mode='HTML')

    # Send the message to each channel
    for channel_id in channels:
        try:
            await message.bot.send_message(channel_id, product_status_message, parse_mode='HTML')
        except Exception as e:
            await message.reply(f"Failed to send message to channel ID {channel_id}: {e}")


# Get posted messages
async def get_all_posted_messages(message: types.Message, admins):
    # Check if the user is an admin
    username = message.from_user.username
    if username not in admins:
        await message.reply("Access Forbidden. You are not authorized to view posted messages.")
        return

    messages_ref = db.reference("messages")  # Reference to the 'messages' node
    messages = messages_ref.get()  # Retrieve all messages

    if not messages:
        await message.reply("No posted messages found.")
        return

    response = []

    for message_id, message_details in messages.items():
        message_text = message_details.get('message', 'Unknown message')
        channel_ids = message_details.get('channel_ids', [])
        timestamp = message_details.get('timestamp', 'Unknown timestamp')
        status = message_details.get('status', 'Unknown status')
        sent_message_ids = message_details.get('sent_message_ids', [])

        # Collect sent message IDs and format them for display
        formatted_sent_ids = []
        for sent_key, sent_data in sent_message_ids.items():
            numeric_id = sent_data.get('numeric_id')
            firebase_id = sent_data.get('firebase_message_id')
            formatted_sent_ids.append(
                f"Numeric ID: {numeric_id}, Firebase ID: {firebase_id}")

        # Format each message's properties into a readable string
        formatted_message = (
            f"<b>Firebase Message ID:</b> {message_id}\n"
            f"<b>Message Text:</b> {message_text}\n"
            f"<b>Channel IDs:</b> {', '.join(map(str, channel_ids))}\n"
            f"<b>Timestamp:</b> {timestamp}\n"
            f"<b>Status:</b> {status}\n"
            f"<b>Sent Message IDs:</b> {', '.join(formatted_sent_ids) if formatted_sent_ids else 'None'}\n"
            f"<b>--------------------------</b>"
        )
        response.append(formatted_message)

    # Join all message entries into a single string
    formatted_messages = "\n\n".join(response)

    await message.reply(formatted_messages, parse_mode='HTML')


async def routine_message(message: types.Message, admins, channels):
    logging.info(f"Received message: {message.text}")

    if message.from_user.username in admins:
        # Remove the command part "/addcontent" from the message
        content = message.text[len("/addcontent"):].strip()

        # Check if content is empty
        if not content:
            await message.reply("Please provide a message and optional interval in the correct format: `/addcontent <message>, <interval>`.")
            return

        # Split the content by comma (message, interval)
        content_parts = content.split(',')

        # The first part is the message
        closure_message = content_parts[0].strip()

        # The second part is the interval (optional)
        interval = 0  # Default interval is 0 (no reposting)

        if len(content_parts) == 2:
            interval_str = content_parts[1].strip()
            if interval_str.isdigit():
                interval = int(interval_str)
                if interval < 1:
                    await message.reply("Interval must be at least 1 minute.")
                    return
            else:
                await message.reply("Invalid interval. Please provide a valid number in minutes.")
                return

        # Log interval value
        logging.info(f"Interval set to: {interval} minutes")

        # Store the message data in Firebase
        message_ref = db.reference('messages').push()

        # Get the unique ID for this message from Firebase
        firebase_message_id = message_ref.key

        # Store the message details in Firebase
        message_ref.set({
            'message': closure_message,
            'interval': interval,
            'channels': channels,
            'timestamp': time.time(),
            'status': 'sent',
        })

        # Retrieve the stored message from Firebase by its ID
        stored_message_ref = db.reference(f'messages/{firebase_message_id}')
        stored_message = stored_message_ref.get()

        if not stored_message:
            await message.reply("Failed to retrieve the message data from the database.")
            return

        # Extract data from the retrieved Firebase record
        message_content = stored_message['message']
        message_interval = stored_message['interval']
        message_channels = stored_message['channels']

        # Send the message to each channel and handle reposting if interval is greater than 0
        for channel_id in message_channels:
            try:
                # Send the message to the channel
                sent_message = await message.bot.send_message(channel_id, message_content)
                await message.reply(f"Message sent to channel ID: {channel_id}.")

                # Track the sent message in Firebase under the 'sentmessages' collection
                sent_message_ref = db.reference(
                    f'sentmessages/{channel_id}/{firebase_message_id}')

                sent_message_ref.set({
                    'message_id': sent_message.message_id,
                    'content': message_content,
                })

                # If an interval is provided, schedule reposting
                if message_interval > 0:
                    await schedule_repost(message.bot, firebase_message_id, message_content, channel_id, message_interval)

            except Exception as e:
                await message.reply(f"Failed to send message to channel ID {channel_id}: {str(e)}")
    else:
        await message.reply("You are not authorized to use this command.")


async def schedule_repost(bot, firebase_message_id, message_text, channel_id, interval):
    """
    Reposts the given message to the channel at the specified interval.
    """
    while True:
        # Wait for the specified interval (in minutes)
        await asyncio.sleep(interval * 60)

        try:
            # Fetch the message from Firebase using the firebase_firebase_message_id
            messages_ref = db.reference(f'messages/{firebase_message_id}')
            message_details = messages_ref.get()

            # Check if the message still exists in Firebase (it may have been deleted)
            if message_details is None:
                logging.info(
                    f"Message ID {message_id} does not exist in Firebase anymore. Skipping repost.")
                return

            # Fetch the message content and channel details from the stored message
            message_content = message_details['message']
            message_channels = message_details['channels']

            # Check if the message has already been sent to this channel
            sent_message_ref = db.reference(
                f'sentmessages/{channel_id}/{firebase_message_id}')
            existing_message = sent_message_ref.get()

            if existing_message:
                logging.info(
                    f"Message already sent to channel {channel_id}, deleting before reposting.")
                await delete_message_from_channel(bot, existing_message['message_id'], channel_id)

            # Send the message to the channel
            sent_message = await bot.send_message(channel_id, message_content)
            logging.info(
                f"Message reposted to channel {channel_id}, message ID: {sent_message.message_id}.")

            # Track the sent message in Firebase under the 'sentmessages' collection
            sent_message_ref.set({
                'message_id': sent_message.message_id,
                'content': message_content,
            })

        except Exception as e:
            logging.error(
                f"Error reposting message {message_id} to channel {channel_id}: {e}")


# Delete message helper
class DummyMessage:
    def __init__(self, bot):
        self.bot = bot

    async def reply(self, text):
        logging.info(f"Dummy reply: {text}")


async def delete_message_from_channel(bot, message_id, channel_id):
    """
    Deletes a message from a channel.
    """
    try:
        await bot.delete_message(channel_id, message_id)
        logging.info(
            f"Message {message_id} deleted from channel {channel_id}.")
    except Exception as e:
        logging.error(
            f"Failed to delete message {message_id} from channel {channel_id}: {e}")


async def display_product_ids(message: types.Message, admins):
    # Check if the user is an admin
    username = message.from_user.username
    if username not in admins:
        await message.reply("Access Forbidden. You are not authorized to view posted messages.")
        return

    # Reference to the "products" collection in Firebase
    product_ref = db.reference("products")
    products = product_ref.get()

    if not products:
        await message.reply("No products found in the database.")
        return

    # Start building the message to display
    response_message = "Product List:\n\n"
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    for product_id, product_details in products.items():
        # Ensure product details exist (name and price should be provided)
        product_name = product_details.get("name", "N/A")
        product_price = product_details.get("price", "N/A")

        # Add the product details to the response message
        response_message += f"ID: {product_id}\n"
        response_message += f"Name: {product_name}\n"
        response_message += f"Price: {product_price}\n\n"

        # Create a delete button for this product
        delete_button = types.InlineKeyboardButton(
            text=f"Delete {product_name}",  # Button text with product name
            # Callback data containing product_id
            callback_data=f"delete_product_{product_id}"
        )
        keyboard.add(delete_button)

    # Send the formatted product list along with the delete buttons
    await message.reply(response_message, reply_markup=keyboard)


async def delete_product(callback_query: types.CallbackQuery, admins):
    # Extract the product ID from callback data
    callback_data = callback_query.data
    if callback_data.startswith("delete_product_"):
        product_id = callback_data[len("delete_product_"):]

        # Reference to the "products" collection in Firebase
        product_ref = db.reference("products")

        # Attempt to get the product details first
        product_details = product_ref.child(product_id).get()

        if not product_details:
            await callback_query.answer(f"Product with ID {product_id} not found.", show_alert=True)
            return

        # Check if the user is an admin
        username = callback_query.from_user.username
        if username not in admins:
            await callback_query.answer("You are not authorized to delete this product.", show_alert=True)
            return

        # Delete the product from the database
        product_ref.child(product_id).delete()

        # Inform the admin that the product has been deleted
        await callback_query.answer(f"Product {product_id} has been deleted.")

        # Optionally, delete the product from the message by updating it (or resend the message)
        await callback_query.message.edit_text(
            f"Product {product_id} deleted successfully.\n\n" +
            "The list has been updated.", reply_markup=None
        )

        # Call display_product_ids to refresh the list
        await display_product_ids(callback_query.message, admins)
    else:
        await callback_query.answer("Invalid action.", show_alert=True)
