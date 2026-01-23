import requests
import json
from restaurant_tools import get_menu, login_to_api, save_delivery_address, create_customer_account


def test_login():
    """Test login functionality"""
    print("\nTesting login...")
    success = login_to_api("john@example.com", "@Test123")
    print(f"Login success: {success}")
    return success

def test_get_menu():
    """Test the get_menu function"""
    print("\nTesting get_menu function...")

    # Add debugging to see what's happening
    print("Calling get_menu()...")
    products = get_menu()
    print(f"Number of products returned: {len(products)}")

    if products:
        print("First product:")
        print(f"  ID: {products[0].id}")
        print(f"  Name: {products[0].name}")
        print(f"  Price: {products[0].price}")
        print(f"  Description: {products[0].description}")
        print(f"  Available: {products[0].available}")
    else:
        print("No products returned from get_menu()")

    return products

def test_direct_api_call():
    """Test direct API call with authentication"""
    print("\nTesting direct API call...")
    try:
        # Try with the hardcoded token first
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImZhYmQ5MThiLTEzZTgtNGMyYi1iOTJlLTcwYmM1OWU5MGFhMyIsImVtYWlsIjoiam9obkBleGFtcGxlLmNvbSIsImlhdCI6MTc1MjMzNzIxOSwiZXhwIjoxNzUyMzgwNDE5fQ.cX8Wss5OnPnzk_eaHMHotdXnQW3ttDagW73IM8bPOvw"}
        response = requests.get("http://localhost:3000/v1/products", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")

        if response.status_code == 200:
            data = response.json()
            print(f"Number of products in response: {len(data)}")
            if data:
                print("First product from API:")
                print(f"  {json.dumps(data[0], indent=2)}")

        return response.status_code == 200
    except Exception as e:
        print(f"Direct API call error: {e}")
        return False

def save_delivery_address_test():
    """Test the save_delivery_address function"""
    print("\nTesting save_delivery_address function...")
    success = save_delivery_address("Casa", "Calle 123", "Pasto", "Nariño", "150001", "Barrio 123", "4d0947d4-f1fd-4242-951d-52c83c341e47")
    print(f"Save delivery address success: {success}")
    return success

def create_customer_account_test():
    """Test the create_customer_account function"""
    print("\nTesting create_customer_account function...")
    success = create_customer_account("John", "Connor", "connor@example.com", "@Test123", "1234567890")
    print(f"Create customer account success: {success}")
    return success

if __name__ == "__main__":
    print("=== Debugging get_menu tool ===\n")

    # # Test 2: Login
    # login_ok = test_login()

    # # Test 3: Direct API call
    # direct_ok = test_direct_api_call()

    # Test 4: get_menu function
    # products = test_get_menu()

    # Test 5: Step by step test
    # delivery_address_test = save_delivery_address_test()
    customer_account_test = create_customer_account_test()

    print("\n=== Summary ===")
    # print(f"Login: {'✓' if login_ok else '✗'}")
    # print(f"Direct API Call: {'✓' if direct_ok else '✗'}")
    # print(f"get_menu function: {'✓' if products else '✗'}")
    # print(f"save_delivery_address function: {'✓' if delivery_address_test else '✗'}")
    print(f"create_customer_account function: {'✓' if customer_account_test else '✗'}")


        # if not login_ok:
        #     print("- Login is failing")
        # if not direct_ok:
        #     print("- Authentication is failing")
        # if not products:
        #     print("- get_menu function has internal issues")
    # if not delivery_address_test:
    #     print("- save_delivery_address function has internal issues")
    if not customer_account_test:
        print("- create_customer_account function has internal issues")