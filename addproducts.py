import firebase_admin
from firebase_admin import credentials, db
import json
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# Path to the JSON file you want to process
json_file_path = './products.json'

# Initialize Firebase Admin SDK
cred = credentials.Certificate("rabbitcred.json")
firebase_admin.initialize_app(cred, {"databaseURL": DATABASE_URL})


def process_json_file(json_file_path):
    try:
        with open(json_file_path, 'r') as f:
            products = json.load(f)

        if not products:
            print("The JSON file is empty or not in the correct format.")
            return

        for product in products:
            name = product.get('name', '').strip()
            category = product.get('category', '').strip()
            price = float(product.get('price', 0))
            available = product.get('available', False)
            descriptions = product.get('descriptions', [])

            # Firebase reference to push product data
            product_ref = db.reference("products").push()
            product_ref.set({
                'name': name,
                'category': category,
                'price': price,
                'available': available,
                'descriptions': descriptions
            })

        print("Products added successfully from JSON!")

    except json.JSONDecodeError as e:
        print(f"Error parsing the JSON file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Run the script
if __name__ == '__main__':
    process_json_file(json_file_path)
