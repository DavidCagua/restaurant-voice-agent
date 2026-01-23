# Restaurant Management System

A comprehensive restaurant management system designed to **attend phone calls and take delivery orders** through an AI-powered voice assistant. This monorepo contains both the backend API and the LiveKit-based voice agent that work together to provide a complete solution for handling customer calls, processing orders, and managing deliveries.

## 🎯 Purpose

The primary purpose of this system is to **automate the process of attending incoming phone calls and taking delivery orders** for restaurants. When customers call the restaurant, the AI voice assistant (Daniela) answers the call and:

- Greets customers in Spanish
- Shows the menu and helps customers select items
- Collects customer information and creates accounts
- Gathers delivery addresses
- Confirms orders and payment methods
- Processes the complete order flow

This eliminates the need for human staff to manually answer every call, allowing restaurants to handle more orders efficiently while providing a consistent, friendly customer experience.

## 🏗️ Architecture

This project consists of two main components:

```
restaurant/
├── restaurant-api/     # Node.js/TypeScript REST API (Express + Prisma + PostgreSQL)
├── agent-server/       # Python voice AI assistant (LiveKit + OpenAI + Deepgram + ElevenLabs)
└── package.json        # Root workspace configuration (npm workspaces)
```

### Component Overview

**restaurant-api**: A production-ready REST API built with Express.js, TypeScript, and Prisma ORM. It handles:
- User authentication and authorization (JWT)
- Product/menu management
- Customer account management
- Delivery address management
- PostgreSQL database integration

**agent-server**: A Python-based voice AI assistant powered by LiveKit Agents that **answers phone calls and takes orders**. It provides:
- Phone call handling via LiveKit telephony integration
- Natural language voice interactions in Spanish
- Real-time speech recognition (Deepgram)
- GPT-4 powered conversation
- Text-to-speech synthesis (ElevenLabs)
- Integration with the restaurant API for order processing

## 🚀 Getting Started

### Prerequisites

- **Node.js** >= 16.0.0
- **npm** >= 8.0.0
- **Python** >= 3.8
- **pip** (Python package manager)
- **PostgreSQL** (or use Docker Compose)
- **Docker** and **Docker Compose** (optional, for database)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd restaurant
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Install Python dependencies**:
   ```bash
   cd agent-server
   pip install -r requirements.txt
   cd ..
   ```

4. **Set up environment variables**:
   
   For the API server:
   ```bash
   cp restaurant-api/.sample.env restaurant-api/.env
   # Edit restaurant-api/.env with your configuration
   ```
   
   For the agent server:
   ```bash
   cp agent-server/env.example agent-server/.env
   # Edit agent-server/.env with your API keys
   ```

5. **Set up the database** (if using Docker):
   ```bash
   npm run docker:up
   ```

6. **Run database migrations**:
   ```bash
   cd restaurant-api
   npm run migrate:dev
   cd ..
   ```

## 🛠️ Development

### Running the Services

**Start the API server** (in development mode):
```bash
npm run dev
# Or from the restaurant-api directory:
cd restaurant-api
npm run dev
```

The API will be available at `http://localhost:3000`

**Start the voice agent server**:
```bash
cd agent-server
python agent.py
```

The agent will connect to LiveKit and be ready to handle voice interactions.

### Running Both Services

For a complete setup, you'll need both services running:

1. **Terminal 1** - API Server:
   ```bash
   npm run dev
   ```

2. **Terminal 2** - Agent Server:
   ```bash
   cd agent-server
   python agent.py
   ```

## 📜 Available Scripts

### Root Level Commands

- `npm run dev` - Start the API server in development mode
- `npm run build` - Build all workspaces
- `npm run test` - Run tests for all workspaces
- `npm run lint` - Lint all workspaces
- `npm run docker:up` - Start Docker services (PostgreSQL)
- `npm run docker:down` - Stop Docker services

### Workspace-specific Commands

To run commands for a specific workspace:

```bash
# Run dev for restaurant-api only
npm run dev --workspace=restaurant-api

# Run tests for restaurant-api
npm run test --workspace=restaurant-api

# Install a package in a specific workspace
npm install express --workspace=restaurant-api
```

## 🔧 Configuration

### Restaurant API Configuration

The API requires the following environment variables (see `restaurant-api/.sample.env`):

- `PORT` - Server port (default: 3000)
- `DATABASE_URL` - PostgreSQL connection string
- `ACCESS_TOKEN_SECRET` - JWT secret for access tokens
- `REFRESH_TOKEN_SECRET` - JWT secret for refresh tokens

### Agent Server Configuration

The agent requires the following environment variables (see `agent-server/env.example`):

- `LIVEKIT_URL` - LiveKit server WebSocket URL
- `LIVEKIT_API_KEY` - LiveKit API key
- `LIVEKIT_API_SECRET` - LiveKit API secret
- `OPENAI_API_KEY` - OpenAI API key (for GPT-4)
- `ELEVENLABS_API_KEY` - ElevenLabs API key (for TTS)
- `DEEPGRAM_API_KEY` - Deepgram API key (for STT)

**Note**: The agent server connects to the API at `http://localhost:3000/v1` by default. Ensure the API is running before starting the agent.

## 🏛️ Workspaces

### restaurant-api

The main REST API server built with Express.js, TypeScript, and Prisma.

**Key Features:**
- RESTful API endpoints
- JWT-based authentication
- User management (registration, login, password change)
- Product/menu management
- Address management (CRUD operations)
- PostgreSQL database with Prisma ORM
- Comprehensive test coverage
- API documentation with VitePress
- Rate limiting and error handling
- CI/CD pipeline with GitHub Actions

**Tech Stack:**
- Node.js + Express.js
- TypeScript
- Prisma ORM
- PostgreSQL
- Jest (testing)
- VitePress (documentation)

See [restaurant-api/README.md](./restaurant-api/README.md) for detailed API documentation.

### agent-server

Python-based voice AI assistant for restaurant ordering using LiveKit Agents.

**Key Features:**
- Voice-based restaurant assistant (Spanish)
- Multi-language speech recognition (Deepgram Nova-3)
- OpenAI GPT-4 integration for natural conversations
- ElevenLabs multilingual text-to-speech
- LiveKit real-time communication
- Noise cancellation (BVC)
- Turn detection (multilingual model)
- Integration with restaurant API for:
  - Menu retrieval
  - Customer account creation
  - Delivery address management
  - Order processing

**Tech Stack:**
- Python 3.8+
- LiveKit Agents
- OpenAI GPT-4
- Deepgram (STT)
- ElevenLabs (TTS)
- Silero VAD

See [agent-server/README.md](./agent-server/README.md) for detailed agent documentation.

## 🔗 Integration

The agent server integrates with the restaurant API to:

1. **Retrieve Menu**: Fetches available products from the API
2. **Create Accounts**: Registers new customers via the API
3. **Manage Addresses**: Saves and retrieves delivery addresses
4. **Process Orders**: Handles the complete order flow

The integration is handled through the `restaurant_tools.py` module, which provides Python functions that call the REST API endpoints.

## 📚 Documentation

- **API Documentation**: Available at `restaurant-api/docs/` (VitePress) or run `npm run docs:dev --workspace=restaurant-api`
- **API Testing Guide**: See `restaurant-api/api-testing.md`
- **Agent Documentation**: See `agent-server/README.md`

## 🧪 Testing

Run tests for the API:
```bash
npm run test --workspace=restaurant-api
```

The API includes comprehensive test coverage for use cases and endpoints.

## 🤝 Contributing

1. Make changes in the appropriate workspace
2. Run tests: `npm run test`
3. Run linting: `npm run lint`
4. Commit your changes (follow conventional commits)
5. Create a pull request

## 📄 License

ISC
