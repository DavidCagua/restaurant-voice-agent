# Restaurant API Testing Guide

## 🚀 Quick Start

First, start your API server:
```bash
npm run dev
```

The API will be available at: `http://localhost:3000`

## 📋 API Endpoints

### **1. User Registration**
```bash
curl -X POST http://localhost:3000/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "password": "@Test123",
    "phone": "(11) 98888-8888"
  }'
```

**Expected Response:** `201 Created`

### **2. User Login**
```bash
curl -X POST http://localhost:3000/v1/user \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "@Test123"
  }'
```

**Expected Response:** `200 OK` with JWT token in cookie

### **3. Create Product (Protected)**
```bash
curl -X POST http://localhost:3000/v1/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "Margherita Pizza",
    "price": 25.99,
    "description": "Classic tomato and mozzarella pizza",
    "images": ["pizza1.jpg", "pizza2.jpg"],
    "available": true
  }'
```

### **4. Get Products (Protected)**
```bash
curl -X GET http://localhost:3000/v1/products \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### **5. Create Address (Protected)**
```bash
curl -X POST http://localhost:3000/v1/addresses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "Home",
    "address": "123 Main Street",
    "address2": "Apt 4B",
    "district": "Downtown",
    "city": "New York",
    "state": "NY",
    "postalCode": "10001"
  }'
```

### **6. Get Addresses (Protected)**
```bash
curl -X GET http://localhost:3000/v1/addresses \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### **7. Change Password (Protected)**
```bash
curl -X PUT http://localhost:3000/v1/user/security \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "oldPassword": "@Test123",
    "newPassword": "@NewPassword123",
    "confirmNewPassword": "@NewPassword123"
  }'
```

## 🔧 Using Postman/Insomnia

### **Step 1: Register a User**
- **Method:** `POST`
- **URL:** `http://localhost:3000/v1/users`
- **Body (JSON):**
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "password": "@Test123",
  "phone": "(11) 98888-8888"
}
```

### **Step 2: Login to Get Token**
- **Method:** `POST`
- **URL:** `http://localhost:3000/v1/user`
- **Body (JSON):**
```json
{
  "email": "john@example.com",
  "password": "@Test123"
}
```

### **Step 3: Use Token for Protected Endpoints**
- **Header:** `Authorization: Bearer YOUR_JWT_TOKEN`

## 📝 Password Requirements

Your API requires strong passwords:
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 symbol

**Example valid passwords:**
- `@Test123`
- `SecurePass1!`
- `MyPassword123#`

## 🔍 Testing Flow

1. **Register a user** → Get `201` response
2. **Login with user** → Get JWT token
3. **Use token** for all protected endpoints
4. **Test CRUD operations** on products and addresses

## 🚨 Common Issues

### **Authentication Errors (401)**
- Missing `Authorization` header
- Invalid JWT token
- Expired token

### **Validation Errors (400/422)**
- Missing required fields
- Invalid email format
- Weak password
- Invalid phone format

### **Conflict Errors (409)**
- Email already exists
- Product name already exists

## 🧪 Test Data Examples

### **Users**
```json
{
  "firstName": "Maria",
  "lastName": "Silva",
  "email": "maria@restaurant.com",
  "password": "@Secure123",
  "phone": "(11) 99999-9999"
}
```

### **Products**
```json
{
  "name": "Caesar Salad",
  "price": 15.50,
  "description": "Fresh romaine lettuce with caesar dressing",
  "images": ["salad1.jpg"],
  "available": true
}
```

### **Addresses**
```json
{
  "name": "Work",
  "address": "456 Business Ave",
  "city": "São Paulo",
  "state": "SP",
  "postalCode": "01234-567"
}
```