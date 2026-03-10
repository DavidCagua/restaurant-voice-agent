# Restaurant API

A production-ready REST API for restaurant management built with Node.js, Express.js, TypeScript, and Prisma ORM. This API provides comprehensive functionality for managing a single restaurant, including user authentication, product management, and address handling.

## 🎯 Overview

The Restaurant API is designed to handle all backend operations for a restaurant management system. It provides secure, scalable endpoints for user management, product catalog, and delivery address management, with comprehensive testing and documentation.

## ✨ Features

- **RESTful API**: Clean, well-structured REST endpoints
- **Authentication & Authorization**: JWT-based secure authentication
- **User Management**: Registration, login, password management
- **Product Management**: Full CRUD operations for menu items
- **Address Management**: Complete address CRUD with district support
- **Database Integration**: PostgreSQL with Prisma ORM
- **Type Safety**: Full TypeScript implementation
- **Testing**: Comprehensive Jest test coverage
- **Documentation**: VitePress-based API documentation
- **Code Quality**: ESLint, Prettier, Husky pre-commit hooks
- **CI/CD**: GitHub Actions workflow
- **Rate Limiting**: Built-in request rate limiting
- **Error Handling**: Comprehensive error handling middleware

## 🏗️ Architecture

The API follows a clean architecture pattern:

```
src/
├── modules/          # Feature modules (addresses, products, users)
│   └── addresses/
│       └── use-cases/  # Business logic
├── core/             # Core domain logic
│   ├── controller/   # Base controllers
│   ├── domain/       # Domain errors
│   └── logic/        # Shared utilities
└── infra/            # Infrastructure layer
    ├── http/         # Express app and routes
    └── prisma/       # Database client and schema
```

## 📋 Prerequisites

- **Node.js** >= 16.0.0
- **npm** >= 8.0.0
- **PostgreSQL** >= 12.0 (or use Docker Compose)
- **Docker** and **Docker Compose** (optional, for database)

## 🚀 Getting Started

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Set up environment variables**:
   ```bash
   cp .sample.env .env
   ```

3. **Configure your `.env` file**:
   ```env
   PORT=3000
   DATABASE_URL=postgresql://user:password@localhost:5432/restaurant_db
   ACCESS_TOKEN_SECRET=your_access_token_secret
   REFRESH_TOKEN_SECRET=your_refresh_token_secret
   ```

4. **Set up the database** (using Docker):
   ```bash
   npm run docker:up
   ```

   Or use your own PostgreSQL instance and update `DATABASE_URL` accordingly.

5. **Run database migrations**:
   ```bash
   npm run migrate:dev
   ```

6. **Start the development server**:
   ```bash
   npm run dev
   ```

The API will be available at `http://localhost:3000`

## 📚 API Documentation

### Interactive Documentation

Start the VitePress documentation server:
```bash
npm run docs:dev
```

Then visit `http://localhost:5173` to view the interactive API documentation.

### Build Documentation

Build static documentation:
```bash
npm run docs:build
```

Preview the built documentation:
```bash
npm run docs:preview
```

### Online Documentation

The API documentation is also available at: [https://restaurant-docs.vercel.app/](https://restaurant-docs.vercel.app/)

## 🔌 API Endpoints

### Base URL

All endpoints are prefixed with `/v1`

### Authentication Endpoints

- `POST /v1/user` - User login (returns JWT in Set-Cookie)
- `POST /v1/users` - Create new user account
- `PUT /v1/user/security` - Change password (requires authentication)

### Product Endpoints

- `GET /v1/products` - Get all products (requires authentication)
- `POST /v1/products` - Create a new product (requires authentication)
- `DELETE /v1/product` - Delete a product (requires authentication; id in body)

### Address Endpoints

- `GET /v1/addresses` - Get all addresses for authenticated user
- `POST /v1/addresses` - Create a new address
- `PUT /v1/address` - Update an address (requires authentication; id in body)
- `DELETE /v1/address` - Delete an address (requires authentication; id in body)

### Authentication

Protected endpoints require a JWT in the **Authorization** header:

```
Authorization: Bearer <your_token>
```

Login (`POST /v1/user`) returns the token in a **Set-Cookie** header; for Postman or API clients, use that token value in the `Authorization` header on subsequent requests.

---

## 📮 Testing with Postman

**Base URL:** `http://localhost:3000/v1` (with API running: `npm run dev`)

### 1. Login (get token)

| Field | Value |
|-------|--------|
| **Method** | `POST` |
| **URL** | `http://localhost:3000/v1/user` |
| **Body** | raw → JSON |

```json
{
  "email": "john@example.com",
  "password": "@Test123"
}
```

- Send the request. The response body is JSON: `{ "token": "eyJ..." }`. Copy the `token` value.
- On protected requests, add header: **Authorization** = `Bearer <paste_token>` (or use **Authorization** → Bearer Token and paste the token).

**Optional – auto-save token in Postman:** In the login request **Tests** tab, add:

```js
const json = pm.response.json();
if (json.token) pm.environment.set("auth_token", json.token);
```

Create an environment and set variable `auth_token` (leave value empty). Then on protected requests use **Authorization** → Bearer Token → Token: `{{auth_token}}`.

### 2. Get products (menu)

| Field | Value |
|-------|--------|
| **Method** | `GET` |
| **URL** | `http://localhost:3000/v1/products` |
| **Headers** | `Authorization: Bearer <paste_token_here>` |

Use the token from the login cookie (or `{{auth_token}}` if you set it).

### 3. Create user (register)

| Field | Value |
|-------|--------|
| **Method** | `POST` |
| **URL** | `http://localhost:3000/v1/users` |
| **Body** | raw → JSON |

```json
{
  "firstName": "María",
  "lastName": "García",
  "email": "maria@example.com",
  "password": "@Test123",
  "phone": "+573001112233"
}
```

### 4. Create address (requires auth)

| Field | Value |
|-------|--------|
| **Method** | `POST` |
| **URL** | `http://localhost:3000/v1/addresses` |
| **Headers** | `Authorization: Bearer <token>` |
| **Body** | raw → JSON |

```json
{
  "name": "Casa",
  "address": "Calle 10 # 20-30",
  "city": "Pasto",
  "state": "Nariño",
  "postalCode": "150001",
  "district": "Centro"
}
```

### 5. Get addresses

| Field | Value |
|-------|--------|
| **Method** | `GET` |
| **URL** | `http://localhost:3000/v1/addresses` |
| **Headers** | `Authorization: Bearer <token>` |

### Quick checklist

1. Start DB: `npm run docker:up`
2. Run migrations: `npm run migrate:dev`
3. Seed data: `npm run db:seed`
4. Start API: `npm run dev`
5. In Postman: login → copy token from cookie → use `Authorization: Bearer <token>` on protected requests.

## 🛠️ Available Scripts

### Development

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build TypeScript to JavaScript
- `npm start` - Start production server (requires build first)

### Database

- `npm run migrate:dev` - Create and apply new migration
- `npm run migrate:deploy` - Apply pending migrations (production)

### Testing

- `npm run test` - Run all tests
- `npm run test:watch` - Run tests in watch mode

### Code Quality

- `npm run lint` - Check code style
- `npm run lint:fix` - Fix code style issues automatically

### Docker

- `npm run docker:up` - Start PostgreSQL container
- `npm run docker:down` - Stop PostgreSQL container

### Documentation

- `npm run docs:dev` - Start documentation dev server
- `npm run docs:build` - Build documentation
- `npm run docs:preview` - Preview built documentation

### Commits

- `npm run commit` - Interactive commit with conventional commits

## 🧪 Testing

The API includes comprehensive test coverage using Jest.

### Running Tests

```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch
```

### Test Environment

Tests use a separate database configured via `.env.test`. The test setup:
- Automatically runs migrations before tests
- Uses isolated test database
- Cleans up after test runs

### Test Structure

Tests are co-located with use cases:
```
src/modules/addresses/use-cases/get-addresses/
├── get-addresses-use-case.ts
└── get-addresses-use-case.test.ts
```

## 🗄️ Database

### Prisma Schema

The database schema is defined in `src/infra/prisma/schema.prisma`. Key models:

- **User**: User accounts with authentication
- **Product**: Menu items/products
- **Address**: Delivery addresses linked to users

### Migrations

Create a new migration:
```bash
npm run migrate:dev
```

Apply migrations in production:
```bash
npm run migrate:deploy
```

### Prisma Studio

View and edit database data:
```bash
npx prisma studio
```

## 🔒 Security

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for password storage
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Secure error messages (no sensitive data exposure)
- **Rate Limiting**: Protection against abuse

## 📁 Project Structure

```
restaurant-api/
├── src/
│   ├── modules/          # Feature modules
│   │   └── addresses/
│   │       └── use-cases/
│   ├── core/             # Core domain
│   │   ├── controller/
│   │   ├── domain/
│   │   └── logic/
│   └── infra/            # Infrastructure
│       ├── http/         # Express setup
│       └── prisma/       # Database
├── docs/                 # API documentation
├── .github/              # CI/CD workflows
├── .husky/               # Git hooks
├── docker-compose.yml    # PostgreSQL container
├── jest.config.ts        # Jest configuration
├── prisma/               # Prisma files
└── tsconfig.json         # TypeScript config
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `PORT` | Server port | No (default: 3000) |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `ACCESS_TOKEN_SECRET` | JWT secret for access tokens | Yes |
| `REFRESH_TOKEN_SECRET` | JWT secret for refresh tokens | Yes |

### Database Connection

The `DATABASE_URL` should follow this format:
```
postgresql://username:password@host:port/database
```

Example:
```
postgresql://postgres:password@localhost:5432/restaurant_db
```

## 🚢 Deployment

### Production Build

1. **Build the project**:
   ```bash
   npm run build
   ```

2. **Run migrations**:
   ```bash
   npm run migrate:deploy
   ```

3. **Start the server**:
   ```bash
   npm start
   ```

### Environment Setup

Ensure production environment variables are set:
- `DATABASE_URL` - Production database connection
- `ACCESS_TOKEN_SECRET` - Strong random secret
- `REFRESH_TOKEN_SECRET` - Strong random secret
- `PORT` - Server port (if different from default)

## 🤝 Contributing

1. **Follow the code style**:
   - ESLint and Prettier are configured
   - Run `npm run lint:fix` before committing

2. **Write tests**:
   - Add tests for new features
   - Maintain test coverage

3. **Use conventional commits**:
   ```bash
   npm run commit
   ```

4. **Follow the architecture**:
   - Place business logic in use cases
   - Keep controllers thin
   - Use the domain layer for shared logic

## 📝 Code Quality

The project includes:

- **ESLint**: Code linting
- **Prettier**: Code formatting
- **Husky**: Git hooks for pre-commit checks
- **Commitlint**: Conventional commit validation
- **TypeScript**: Type safety

Pre-commit hooks automatically:
- Run ESLint
- Format with Prettier
- Validate commit messages

## 🐛 Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running
- Check `DATABASE_URL` format
- Ensure database exists
- Check network connectivity

### Migration Issues

- Ensure database is accessible
- Check migration lock file
- Review Prisma schema syntax

### Port Already in Use

Change the port in `.env`:
```env
PORT=3001
```

## 📚 Additional Resources

- [Express.js Documentation](https://expressjs.com/)
- [Prisma Documentation](https://www.prisma.io/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)

## 👤 Author

**Julio Martins**

- LinkedIn: [@jjuliomarttins](https://www.linkedin.com/in/jjuliomarttins/)
- GitHub: [@eujuliu](https://github.com/eujuliu)

## 📄 License

ISC

<p align="right">(<a href="#readme-top">back to top</a>)</p>
