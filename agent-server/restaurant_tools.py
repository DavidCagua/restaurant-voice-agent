import requests
import json
from typing import List, Dict, Optional
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_BASE_URL = "http://localhost:3000/v1"
API_TOKEN = ''

@dataclass
class Product:
    id: str
    name: str
    price: float
    description: str
    available: bool
    discount: Optional[float] = None
    images: List[str] = None

@dataclass
class Address:
    id: str
    name: str
    address: str
    city: str
    state: str
    postalCode: str
    address2: Optional[str] = None
    district: Optional[str] = None

@dataclass
class Order:
    customer_name: str
    customer_phone: str
    customer_email: str
    products: List[Dict]
    delivery_address: Address
    total_amount: float

def login_to_api(email: str, password: str) -> bool:
    """Login to the restaurant API and get authentication token."""
    global API_TOKEN

    try:
        response = requests.post(f"{API_BASE_URL}/user", json={
            "email": email,
            "password": password
        })

        if response.status_code == 200:
            # Extract token from cookies
            cookies = response.cookies
            token = cookies.get('token')
            if token:
                API_TOKEN = token
                return True
        return False
    except Exception as e:
        print(f"Login error: {e}")
        return False

def get_menu() -> List[Product]:
    """Get the current menu from the restaurant API."""
    global API_TOKEN
    print(f"API_TOKEN: {API_TOKEN}")

    if not API_TOKEN:
        login_to_api("john@example.com", "@Test123")

    try:
        headers = {"Authorization": f"{API_TOKEN}"}
        response = requests.get(f"{API_BASE_URL}/products", headers=headers)

        if response.status_code == 200:
            products_data = response.json()
            products = []
            for product_data in products_data:
                product = Product(
                    id=product_data.get('id'),
                    name=product_data.get('name'),
                    price=product_data.get('price'),
                    description=product_data.get('description'),
                    available=product_data.get('available', False),
                    discount=product_data.get('discount'),
                    images=product_data.get('images', [])
                )
                products.append(product)
            return products
        return []
    except Exception as e:
        print(f"Error getting menu: {e}")
        return []

def create_customer_account(first_name: str, last_name: str, email: str, password: str, phone: str) -> bool:
    """Create a new customer account."""
    try:
        response = requests.post(f"{API_BASE_URL}/users", json={
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "password": password,
            "phone": phone
        })
        print(f"Response: {response.text}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error creating account: {e}")
        return False

def save_delivery_address(name: str, address: str, city: str, state: str, postal_code: str,
                        district: Optional[str] = None, userId: str = None) -> bool:
    """Save a delivery address for the customer."""
    global API_TOKEN

    # Use the hardcoded token that we know works
    token_to_use = API_TOKEN or 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImZhYmQ5MThiLTEzZTgtNGMyYi1iOTJlLTcwYmM1OWU5MGFhMyIsImVtYWlsIjoiam9obkBleGFtcGxlLmNvbSIsImlhdCI6MTc1MjMzNzIxOSwiZXhwIjoxNzUyMzgwNDE5fQ.cX8Wss5OnPnzk_eaHMHotdXnQW3ttDagW73IM8bPOvw'

    try:
        headers = {"Authorization": f"Bearer {token_to_use}"}
        address_data = {
            "name": name,
            "address": address,
            "city": city,
            "state": state,
            "postalCode": postal_code,
            "userId": userId
        }

        if district:
            address_data["district"] = district

        response = requests.post(f"{API_BASE_URL}/addresses",
                               json=address_data,
                               headers=headers)
        print(f"Response: {response.text}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error saving address: {e}")
        return False

def get_delivery_addresses() -> List[Address]:
    """Get saved delivery addresses."""
    global API_TOKEN

    # Use the hardcoded token that we know works
    token_to_use = API_TOKEN or 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImZhYmQ5MThiLTEzZTgtNGMyYi1iOTJlLTcwYmM1OWU5MGFhMyIsImVtYWlsIjoiam9obkBleGFtcGxlLmNvbSIsImlhdCI6MTc1MjMzNzIxOSwiZXhwIjoxNzUyMzgwNDE5fQ.cX8Wss5OnPnzk_eaHMHotdXnQW3ttDagW73IM8bPOvw'

    try:
        headers = {"Authorization": f"Bearer {token_to_use}"}
        response = requests.get(f"{API_BASE_URL}/addresses", headers=headers)

        if response.status_code == 200:
            addresses_data = response.json()
            addresses = []
            for addr_data in addresses_data:
                address = Address(
                    id=addr_data.get('id'),
                    name=addr_data.get('name'),
                    address=addr_data.get('address'),
                    city=addr_data.get('city'),
                    state=addr_data.get('state'),
                    postalCode=addr_data.get('postalCode'),
                    address2=addr_data.get('address2'),
                    district=addr_data.get('district')
                )
                addresses.append(address)
            return addresses
        return []
    except Exception as e:
        print(f"Error getting addresses: {e}")
        return []

def calculate_order_total(products: List[Dict]) -> float:
    """Calculate the total amount for an order."""
    total = 0.0
    for product in products:
        price = product.get('price', 0)
        quantity = product.get('quantity', 1)
        discount = product.get('discount', 0)

        discounted_price = price * (1 - discount / 100) if discount else price
        total += discounted_price * quantity

    return total

def format_menu_for_voice(products: List[Product]) -> str:
    """Format the menu for voice presentation."""
    if not products:
        return "Lo siento, no hay productos disponibles en este momento."

    menu_text = "Aquí está nuestro menú:\n\n"

    for i, product in enumerate(products, 1):
        if product.available:
            price_text = f"${product.price:.2f}"
            if product.discount:
                price_text += f" (con descuento del {product.discount}%)"

            menu_text += f"{i}. {product.name} - {price_text}\n"
            menu_text += f"   {product.description}\n\n"

    menu_text += "¿Qué te gustaría ordenar?"
    return menu_text

def validate_email(email: str) -> bool:
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    import re
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    return len(digits) >= 10

