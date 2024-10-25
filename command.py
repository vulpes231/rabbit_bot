from aiogram import types
from firebase_admin import db


async def start(message: types.Message, ref):
    user_id = message.chat.id
    username = message.from_user.username if message.from_user.username else str(
        user_id)

    # Check if user profile exists
    user_ref = ref.child(f"users/{user_id}")
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
    buttons = ["Profile", "FAQs", "Fund Wallet", "Products", "Admins"]
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

    # Create keyboard with category buttons
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in categories:
        keyboard.add(types.KeyboardButton(category))

    await message.reply("Select a category:", reply_markup=keyboard)


async def handle_user_selection(message: types.Message):
    # Check if the message text is a category
    products_ref = db.reference("products")
    products_data = products_ref.get() or {}

    # Extract categories to validate the user's selection
    categories = {product['category']
                  for product in products_data.values() if 'category' in product}

    if message.text in categories:
        await display_products_by_category(message)
    else:
        await message.reply("Please select a valid category or use /categories to see options.")


async def display_products_by_category(message: types.Message):
    category = message.text

    # Retrieve products in the selected category from the database
    products_ref = db.reference("products")
    products_data = products_ref.get() or {}

    # Debugging: print the retrieved products data
    # print("Retrieved products data:", products_data)

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
    for product_name, product_details in products_in_category.items():
        name = product_details.get('name', product_name)
        price = product_details.get('price')
        available = product_details.get('available')
        availability_status = "In Stock ✅" if available else "Sold Out ❌"

        product_message = f"• {name} | ${price} | {category} | {availability_status} | /order\n"

        product_messages.append(product_message)

    await message.reply("Available products:\n" + "\n".join(product_messages))
