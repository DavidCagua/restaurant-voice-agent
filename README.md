# Restaurant Voice Agent

A production-ready voice AI system for restaurant order taking, built with **LiveKit** for real-time communication, **Deepgram** streaming STT, **ElevenLabs** TTS, **OpenAI** reasoning, and a **Node.js/TypeScript** backend with **Prisma** and **PostgreSQL**. The agent handles complete order workflows through natural Spanish conversation, including menu browsing, customer account creation, address management, and order processing.

## Tech Stack

- **Voice Infrastructure**: LiveKit Agents (real-time WebRTC)
- **Speech-to-Text**: Deepgram Nova-3 (streaming, multilingual)
- **Text-to-Speech**: ElevenLabs multilingual v2
- **Reasoning**: OpenAI GPT-4o-mini
- **Backend API**: Node.js + Express + TypeScript
- **Database**: PostgreSQL with Prisma ORM
- **Integration**: Python agent → HTTP tool calls → Node/TS REST API

## Architecture Overview

The system consists of two main components:

```
┌─────────────────────────────────────────────────────────────┐
│                    Voice Agent (Python)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ LiveKit  │→ │ Deepgram │→ │  OpenAI  │→ │ElevenLabs│   │
│  │  (STT)   │  │  (STT)   │  │  (LLM)   │  │  (TTS)   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                          ↓                                   │
│                    Tool Calls (HTTP)                         │
└──────────────────────────┼───────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Restaurant API (Node.js/TypeScript)            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Express  │→ │  Prisma  │→ │PostgreSQL│                  │
│  │   REST   │  │   ORM    │  │          │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

**agent-server/** - Python-based LiveKit agent implementing:
- Real-time voice session management
- Streaming STT via Deepgram Nova-3
- GPT-4o-mini for conversation reasoning
- Function tools for API integration
- ElevenLabs TTS synthesis
- Silero VAD and multilingual turn detection
- BVC noise cancellation

**restaurant-api/** - Node.js/TypeScript REST API providing:
- JWT-based authentication
- User management (CRUD)
- Product/menu management
- Address management
- PostgreSQL persistence via Prisma

## Request/Response Flow

```
1. Voice Input
   ↓
2. LiveKit Room (WebRTC connection)
   ↓
3. Deepgram STT (streaming transcription, multilingual)
   ↓
4. OpenAI GPT-4o-mini (reasoning, intent extraction)
   ↓
5. Tool Call Decision (if needed)
   ↓
6. HTTP Request → Node/TS Backend API
   ├─ GET /v1/products (menu retrieval)
   ├─ POST /v1/users (account creation)
   ├─ POST /v1/addresses (address management)
   └─ GET /v1/addresses (address retrieval)
   ↓
7. Prisma ORM → PostgreSQL (data persistence)
   ↓
8. API Response → Agent
   ↓
9. OpenAI generates natural language response
   ↓
10. ElevenLabs TTS (multilingual voice synthesis)
    ↓
11. LiveKit → Voice Output
```

## Local Setup

### Prerequisites

- **Node.js** >= 16.0.0
- **npm** >= 8.0.0
- **Python** >= 3.8
- **PostgreSQL** (or Docker Compose)
- **Docker** and **Docker Compose** (optional, for database)

### Installation Steps

1. **Clone and install dependencies**:
   ```bash
   git clone <repository-url>
   cd restaurant-voice-agent
   npm install
   cd agent-server
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL** (using Docker):
   ```bash
   npm run docker:up
   ```

3. **Run database migrations**:
   ```bash
   cd restaurant-api
   npm run migrate:dev
   ```

4. **Configure environment variables** (see Environment Variables section below)

5. **Start services**:
   ```bash
   # Terminal 1: Start API server
   npm run dev
   
   # Terminal 2: Start voice agent
   cd agent-server
   python agent.py
   ```

The API will be available at `http://localhost:3000` and the agent will connect to LiveKit.

## Environment Variables

### Agent Server (`agent-server/.env`)

| Variable | Description | Required |
|----------|-------------|----------|
| `LIVEKIT_URL` | LiveKit server WebSocket URL (e.g., `wss://your-livekit-server.com`) | Yes |
| `LIVEKIT_API_KEY` | LiveKit API key | Yes |
| `LIVEKIT_API_SECRET` | LiveKit API secret | Yes |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o-mini | Yes |
| `ELEVEN_API_KEY` | ElevenLabs API key for TTS (agent uses this env name) | Yes |
| `DEEPGRAM_API_KEY` | Deepgram API key for streaming STT | Yes |
| `DEBUG` | Enable debug logging including transcripts (set to `true` to log sensitive content) | No | `false` |
| `BRAINTRUST_API_KEY` | Braintrust API key for tracing LLM calls and voice interactions | No | - |
| `BRAINTRUST_PARENT` | Braintrust project identifier (e.g., `project:restaurant-voice-agent`) | No | `project:restaurant-voice-agent` |

### Restaurant API (`restaurant-api/.env`)

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `PORT` | Server port | No | `3000` |
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `ACCESS_TOKEN_SECRET` | JWT secret for access tokens | Yes | - |
| `REFRESH_TOKEN_SECRET` | JWT secret for refresh tokens | Yes | - |

**Setup**:
```bash
# Agent server
cp agent-server/env.example agent-server/.env
# Edit agent-server/.env with your API keys

# Restaurant API
cp restaurant-api/.sample.env restaurant-api/.env
# Edit restaurant-api/.env with your configuration
```

## Observability

### Braintrust Tracing (Optional)

When `BRAINTRUST_API_KEY` is set, the agent sends traces to [Braintrust](https://braintrust.dev) via OpenTelemetry. This captures:

- Voice interactions (STT, reasoning, TTS)
- LLM calls (OpenAI chat completions)
- Tool executions (get_menu, create_customer_account, etc.)

Add to `agent-server/.env`:

```bash
BRAINTRUST_API_KEY=your-braintrust-api-key
BRAINTRUST_PARENT=project:restaurant-voice-agent  # optional, default shown
```

View traces in the [Braintrust app](https://www.braintrust.dev/app).

### Structured JSON Logging

The agent server includes structured JSON logging for performance monitoring and debugging. All logs are output as JSON with the following fields:

- `session_id`: Unique session identifier
- `user_id`: User identifier (if available)
- `turn_id`: Conversation turn identifier
- `tool_name`: Name of the tool being called (if applicable)
- `latency_ms`: Latency in milliseconds
- `model`: LLM model name (e.g., `gpt-4o-mini`)
- `stt_provider`: STT provider (e.g., `deepgram`)
- `tts_provider`: TTS provider (e.g., `elevenlabs`)
- `stage`: Processing stage (`stt`, `reasoning`, `tool_call`, `tts`)
- `event_type`: Event type (e.g., `stt_start`, `reasoning_end`, `tool_call_start`)

### Timing Measurements

The system tracks latency for each stage:
- **STT**: Speech-to-text processing (receive/start events)
- **Reasoning**: LLM processing (start/end with latency)
- **Tool Calls**: API integration calls (start/end with latency per tool)
- **TTS**: Text-to-speech synthesis (start/end with latency)

### Debug Logging

By default, **transcript text is excluded** from logs to protect sensitive user content. To enable transcript logging for debugging:

```bash
# In agent-server/.env
DEBUG=true
```

**Warning**: Enabling DEBUG mode will log all user transcripts, which may contain sensitive information. Only use in development or with proper data handling policies.

### Example Log Output

```json
{"timestamp":"2024-01-15T10:30:45.123Z","level":"INFO","message":"tool_call_start: tool_call","session_id":"abc123","turn_id":"turn-456","tool_name":"get_menu","stage":"tool_call","model":"gpt-4o-mini","stt_provider":"deepgram","tts_provider":"elevenlabs","event_type":"tool_call_start"}
{"timestamp":"2024-01-15T10:30:45.456Z","level":"INFO","message":"tool_call_end: tool_call","session_id":"abc123","turn_id":"turn-456","tool_name":"get_menu","latency_ms":333.0,"stage":"tool_call","model":"gpt-4o-mini","stt_provider":"deepgram","tts_provider":"elevenlabs","event_type":"tool_call_end"}
```

## Deployment Notes

### Agent Server

- Runs as a LiveKit agent worker, connecting to LiveKit Cloud or self-hosted instance
- Requires persistent connection to LiveKit server
- API base URL is hardcoded to `http://localhost:3000/v1` in `restaurant_tools.py` (needs configuration for production)
- Uses default admin account (`john@example.com`) for API authentication (should be replaced with service account)

### Restaurant API

- Production build: `npm run build` → `npm start`
- Database migrations: `npm run migrate:deploy`
- Requires PostgreSQL connection
- JWT tokens stored in HTTP-only cookies
- CORS and security headers should be configured for production

### Production Considerations

- **API URL**: Update `API_BASE_URL` in `agent-server/restaurant_tools.py` for production
- **Authentication**: Replace hardcoded admin credentials with proper service account
- **Error Handling**: Add retry logic and circuit breakers for API calls
- **Monitoring**: Add logging, metrics, and health checks
- **Scaling**: Agent workers can be horizontally scaled; API requires connection pooling

## Future Improvements

### High Priority

- [ ] Environment-based API URL configuration (remove hardcoded localhost)
- [ ] Service account authentication for agent → API communication
- [ ] Order creation endpoint and persistence (currently only collects order data)
- [ ] Error handling and retry logic for API tool calls
- [ ] Production-ready logging and monitoring

### Medium Priority

- [ ] Order status tracking and updates
- [ ] Payment processing integration
- [ ] Multi-language support beyond Spanish
- [ ] Conversation state persistence
- [ ] Agent performance metrics and analytics

### Low Priority

- [ ] Voice cloning customization
- [ ] Advanced noise cancellation tuning
- [ ] Conversation replay and debugging tools
- [ ] A/B testing for agent prompts

## TODO: Items to Confirm

- [ ] Order persistence: Verify if orders are saved to database or only collected in conversation
- [ ] Payment processing: Confirm payment method collection vs. actual payment processing
- [ ] Production deployment: Verify LiveKit deployment strategy (Cloud vs. self-hosted)
- [ ] API authentication: Confirm service account setup for production
- [ ] Database migrations: Verify migration strategy for production deployments
- [ ] Rate limiting: Confirm if API has rate limiting for agent requests

## Project Structure

```
restaurant-voice-agent/
├── agent-server/              # Python LiveKit agent
│   ├── agent.py              # Main agent implementation
│   ├── restaurant_tools.py   # API integration functions
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Agent environment variables
│
└── restaurant-api/            # Node.js/TypeScript REST API
    ├── src/
    │   ├── modules/          # Domain modules (users, products, addresses)
    │   ├── infra/            # Infrastructure (HTTP, Prisma)
    │   └── core/             # Core utilities
    ├── src/infra/prisma/     # Prisma schema and migrations
    └── .env                  # API environment variables
```

## Development

### Running Tests

```bash
# API tests
npm run test --workspace=restaurant-api

# Agent (manual testing via debug utilities)
cd agent-server
python debug_menu.py
```

### Available Scripts

- `npm run dev` - Start API server in development mode
- `npm run build` - Build all workspaces
- `npm run test` - Run tests for all workspaces
- `npm run docker:up` - Start PostgreSQL via Docker
- `npm run docker:down` - Stop Docker services

## License

ISC
