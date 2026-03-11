import requests
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import os
from dotenv import load_dotenv
from src.retry import retry_with_backoff, is_transient_error

load_dotenv()

# API Configuration (agent calls restaurant API over HTTP; the API connects to the DB)
API_BASE_URL = os.getenv("RESTAURANT_API_URL", "http://localhost:3000/v1")
print(f"API_BASE_URL: {API_BASE_URL}")
API_TOKEN = ""

@dataclass
class Product:
    id: str
    name: str
    price: float
    description: str
    available: bool
    discount: Optional[float] = None
    images: List[str] = None
    category: Optional[str] = None


@retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0)
def _login_to_api_with_retry(email: str, password: str) -> Tuple[bool, Optional[int]]:
    """Internal login function with retry logic. Returns (success, status_code)."""
    global API_TOKEN
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/user",
            json={"email": email, "password": password},
            timeout=5.0
        )
        
        if response.status_code == 200:
            cookies = response.cookies
            token = cookies.get('token')
            if token:
                API_TOKEN = token
                return True, 200
        return False, response.status_code
    except Exception as e:
        # Re-raise if transient, otherwise return False
        if is_transient_error(None, e):
            raise
        return False, None


def login_to_api(email: str, password: str) -> bool:
    """Login to the restaurant API and get authentication token."""
    try:
        success, _ = _login_to_api_with_retry(email, password)
        return success
    except Exception as e:
        print(f"Login error after retries: {e}")
        return False

@retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0)
def _get_menu_with_retry(category: Optional[str] = None) -> Tuple[List[Product], Optional[int]]:
    """Internal menu retrieval with retry logic. Returns (products, status_code)."""
    global API_TOKEN
    
    if not API_TOKEN:
        if not login_to_api("john@example.com", "@Test123"):
            return [], None
    
    try:
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        url = f"{API_BASE_URL}/products"
        if category:
            url += f"?category={requests.utils.quote(category)}"
        response = requests.get(
            url,
            headers=headers,
            timeout=5.0
        )
        
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
                    images=product_data.get('images', []),
                    category=product_data.get('category'),
                )
                products.append(product)
            return products, 200
        
        # If 401, try to re-authenticate once
        if response.status_code == 401:
            if login_to_api("john@example.com", "@Test123"):
                response = requests.get(
                    url,
                    headers={"Authorization": f"Bearer {API_TOKEN}"},
                    timeout=5.0
                )
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
                            images=product_data.get('images', []),
                            category=product_data.get('category'),
                        )
                        products.append(product)
                    return products, 200
        
        return [], response.status_code
    except Exception as e:
        if is_transient_error(None, e):
            raise
        return [], None


def get_menu(category: Optional[str] = None) -> List[Product]:
    """Get the current menu from the restaurant API, optionally filtered by category."""
    try:
        products, _ = _get_menu_with_retry(category=category)
        return products
    except Exception as e:
        print(f"Error getting menu after retries: {e}")
        return []


# Main categories for Biela - offer these first (platos principales)
# Format: (API category key, Spanish display name)
BIELA_MAIN_CATEGORIES = [
    ("Burgers", "Hamburguesas"),
    ("Hot Dogs", "Perros calientes"),
    ("Fries", "Papas fritas"),
    ("Chicken Burgers", "Hamburguesas de pollo"),
    ("Menú Infantil", "Menú infantil"),
    ("Steak & Ribs", "Carne y costillas"),
]
BIELA_DRINKS_CATEGORY = ("Bebidas", "Bebidas")


def get_categories(include_drinks: bool = False) -> str:
    """Return the list of menu categories in Spanish for voice presentation.
    Use include_drinks=False when offering platos principales; use True after main dish is complete."""
    categories = BIELA_MAIN_CATEGORIES
    if include_drinks:
        categories = list(categories) + [BIELA_DRINKS_CATEGORY]
    names = [spanish for _, spanish in categories]
    return "Tenemos: " + ", ".join(names) + "."

@retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0)
def _create_order_with_retry(
    first_name: str,
    last_name: str,
    phone: str,
    address: str,
    district: Optional[str],
    city: str,
    state: Optional[str],
    postal_code: str,
    payment_method: str,
    items_json: str,
) -> Tuple[Optional[str], Optional[int]]:
    """Internal order creation with retry. Returns (order_id, status_code)."""
    global API_TOKEN

    if not API_TOKEN:
        if not login_to_api("john@example.com", "@Test123"):
            return None, None

    try:
        items = json.loads(items_json)
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        payload = {
            "customerName": first_name,
            "customerLastName": last_name,
            "customerPhone": phone,
            "deliveryAddress": address,
            "district": district or None,
            "city": city,
            "state": state or None,
            "postalCode": postal_code,
            "paymentMethod": payment_method,
            "items": [
                {
                    "productId": item.get("product_id"),
                    "productName": item.get("product_name"),
                    "quantity": int(item.get("quantity", 1)),
                    "unitPrice": float(item.get("unit_price", 0)),
                }
                for item in items
            ],
        }
        response = requests.post(
            f"{API_BASE_URL}/orders",
            json=payload,
            headers=headers,
            timeout=5.0,
        )
        if response.status_code == 201:
            data = response.json()
            return data.get("id"), 201
        return None, response.status_code
    except Exception as e:
        if is_transient_error(None, e):
            raise
        return None, None


def create_order(
    first_name: str,
    last_name: str,
    phone: str,
    address: str,
    district: Optional[str],
    city: str,
    state: Optional[str],
    postal_code: str,
    payment_method: str,
    items_json: str,
) -> Optional[str]:
    """Create an order with customer data, address, payment method and items.
    items_json: [{"product_id": "...", "product_name": "Barracuda", "quantity": 1, "unit_price": 28000}]
    Returns order id on success, None otherwise."""
    try:
        order_id, _ = _create_order_with_retry(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
            district=district,
            city=city,
            state=state,
            postal_code=postal_code,
            payment_method=payment_method,
            items_json=items_json,
        )
        return order_id
    except Exception as e:
        print(f"Error creating order after retries: {e}")
        return None


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

    for product in products:
        if product.available:
            price_text = f"${int(product.price)}"
            if product.discount:
                price_text += f" (con descuento del {product.discount}%)"

            menu_text += f"{product.name} - {price_text}\n"
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

