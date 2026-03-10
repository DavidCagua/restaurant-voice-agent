# Agent Server

A Python-based voice AI assistant for restaurant ordering using LiveKit Agents. This agent provides natural language voice interactions in Spanish, allowing customers to place orders through conversational AI.

## 🎯 Overview

The agent server implements a voice assistant named **Daniela** that helps customers:
- Browse the restaurant menu
- Create customer accounts
- Place orders
- Manage delivery addresses
- Complete the ordering process through natural conversation

## ✨ Features

- **Voice-Based Interactions**: Natural Spanish conversation for restaurant ordering
- **Multi-Language Speech Recognition**: Powered by Deepgram Nova-3 model
- **Advanced AI**: OpenAI GPT-4 integration for intelligent conversations
- **High-Quality TTS**: ElevenLabs multilingual text-to-speech with natural voices
- **Real-Time Communication**: LiveKit for low-latency voice interactions
- **Noise Cancellation**: BVC (Best Voice Cancellation) for clear audio
- **Turn Detection**: Multilingual model for natural conversation flow
- **API Integration**: Seamless connection with the restaurant API
- **Thinking Sounds**: Audio feedback during processing

## 🏗️ Architecture

The agent is built on the LiveKit Agents framework and consists of:

- **`agent.py`**: Main agent implementation with `RestaurantAssistant` class
- **`restaurant_tools.py`**: API integration functions for menu, accounts, and addresses
- **`src/observability.py`**: Structured JSON logging and performance tracking
- **`src/retry.py`**: Retry logic with exponential backoff for external API calls
- **`src/health.py`**: Health check HTTP endpoint
- **`debug_menu.py`**: Debug utilities for testing
- **`test_thinking_sounds.py`**: Testing utilities for audio feedback

## 📋 Prerequisites

- **Python** >= 3.10, < 3.14 (required for LiveKit Agents 1.3+)
- **pip** (Python package manager)
- **LiveKit Server** (cloud or self-hosted)
- **API Keys** for:
  - LiveKit
  - OpenAI
  - ElevenLabs
  - Deepgram

## 🚀 Installation

1. **Create and activate a virtual environment** (Python 3.10+):
   ```bash
   python3.10 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download model files** (required for turn detector and VAD):
   ```bash
   python3 agent.py download-files
   ```
   This downloads the turn detector model weights (~396MB) and other required files.

4. **Set up environment variables**:
   ```bash
   cp env.example .env
   ```

5. **Configure your `.env` file**:
   ```env
   # LiveKit Configuration
   LIVEKIT_URL=wss://your-livekit-server.com
   LIVEKIT_API_KEY=your_livekit_api_key
   LIVEKIT_API_SECRET=your_livekit_api_secret

   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key

   # ElevenLabs Configuration
   ELEVEN_API_KEY=your_elevenlabs_api_key

   # Deepgram Configuration
   DEEPGRAM_API_KEY=your_deepgram_api_key

   # Observability (optional)
   DEBUG=false  # Set to true to enable transcript logging
   HEALTH_CHECK_PORT=8080  # Port for health check endpoint
   ```

## 🎮 Usage

### Running the Agent

The agent supports multiple modes:

**Console Mode** (local testing in terminal):
```bash
python3 agent.py console
```
This runs the agent locally in your terminal for testing. You can speak to it directly.

**Development Mode** (connects to LiveKit Cloud):
```bash
python3 agent.py dev
```
This connects your agent to LiveKit Cloud and makes it available via the Agents playground. Useful for testing with real connections.

**Production Mode**:
```bash
python3 agent.py start
```
This runs the agent in production mode with optimized logging.

**Before running, ensure:**
1. **Restaurant API is running** at `http://localhost:3000` — the agent does **not** connect to the database directly; it calls the restaurant API over HTTP. So in `restaurant-api`: start Postgres (`npm run docker:up`), run migrations (`npm run migrate:dev`), then start the API (`npm run dev`).
2. Your LiveKit server is accessible (or use LiveKit Cloud)
3. All API keys are correctly configured in `.env`
4. Model files have been downloaded (`python3 agent.py download-files`)

To point the agent at a different API URL, set `RESTAURANT_API_URL` in `agent-server/.env` (e.g. `RESTAURANT_API_URL=http://localhost:3000/v1`).

### Agent Behavior

The agent follows this workflow:

1. **Greeting**: Welcomes customers in Spanish as "Daniela"
2. **Menu Display**: Shows available products when requested
3. **Order Taking**: Helps customers select items
4. **Account Creation**: Collects customer information (name, phone, email)
5. **Address Collection**: Gathers delivery address and district (barrio)
6. **Order Confirmation**: Confirms order details
7. **Payment Method**: Asks for payment preference (card or cash)
8. **Completion**: Confirms delivery time (30 minutes) and thanks the customer

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `LIVEKIT_URL` | LiveKit server WebSocket URL | Yes | - |
| `LIVEKIT_API_KEY` | LiveKit API key | Yes | - |
| `LIVEKIT_API_SECRET` | LiveKit API secret | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o-mini | Yes | - |
| `ELEVEN_API_KEY` | ElevenLabs API key for TTS (plugin uses this name) | Yes | - |
| `DEEPGRAM_API_KEY` | Deepgram API key for STT | Yes | - |
| `DEBUG` | Enable debug logging including transcripts | No | `false` |
| `HEALTH_CHECK_PORT` | Port for health check HTTP server | No | `8080` |
| `RESTAURANT_API_URL` | Restaurant API base URL (agent calls this; API talks to DB) | No | `http://localhost:3000/v1` |

### API Configuration

The agent calls the restaurant API over HTTP (it does not connect to the database). Default URL is `http://localhost:3000/v1`. Override with `RESTAURANT_API_URL` in `.env`.

To change the API URL, modify this constant in `restaurant_tools.py`.

### Voice Configuration

The agent uses:
- **STT**: Deepgram Nova-3 (multilingual)
- **LLM**: OpenAI GPT-4o-mini
- **TTS**: ElevenLabs multilingual v2 (voice: "rola")
- **VAD**: Silero Voice Activity Detection
- **Turn Detection**: MultilingualModel (from `livekit-plugins-turn-detector`)
- **Noise Cancellation**: BVC (optional, LiveKit Cloud only)

You can modify these in the `entrypoint` function in `agent.py`.

**Note**: Noise cancellation is automatically enabled if available (LiveKit Cloud deployments). For self-hosted deployments, it will be omitted automatically.

## 🔌 API Integration

The agent integrates with the restaurant API through `restaurant_tools.py`, which provides:

### Available Functions

- **`get_menu()`**: Retrieves the current menu from the API
- **`create_customer_account()`**: Creates a new customer account
- **`save_delivery_address()`**: Saves a delivery address for the customer
- **`get_delivery_addresses()`**: Retrieves saved addresses
- **`format_menu_for_voice()`**: Formats menu for voice presentation

### Authentication

The agent uses a default admin account (`john@example.com`) to authenticate with the API. For customer operations, it creates accounts dynamically and uses those credentials.

## 🎨 Customization

### Changing the Assistant Name

Edit the `instructions` in the `RestaurantAssistant.__init__()` method in `agent.py`.

### Modifying the Workflow

Update the instructions string in the `RestaurantAssistant` class to change the agent's behavior and conversation flow.

### Changing the Voice

Modify the `voice_id` in the `elevenlabs.TTS()` call in the `entrypoint` function. Available voices:
- `"86V9x9hrQds83qf7zaGn"` - Rola (current)
- `"J4vZAFDEcpenkMp3f3R9"` - Paisa (commented out)

### Adjusting Thinking Sounds

Modify the `thinking_sounds` dictionary in the `RestaurantAssistant` class to change or add audio feedback during processing.

## 🧪 Testing

### Debug Menu

Use `debug_menu.py` to test API integration:
```bash
python debug_menu.py
```

### Testing Thinking Sounds

Use `test_thinking_sounds.py` to test audio feedback:
```bash
python test_thinking_sounds.py
```

### Console Mode Testing

Test the agent locally in your terminal:
```bash
python3 agent.py console
```
This allows you to speak directly to the agent and test the full conversation flow.

### Health Check

The agent automatically starts a health check server on port 8080 (configurable via `HEALTH_CHECK_PORT`). Check agent health:

```bash
curl http://localhost:8080/health
```

This returns JSON with environment variable checks and API connectivity status.

## 📊 Observability

The agent includes structured JSON logging for performance monitoring and debugging:

- **Structured Logs**: All logs output as JSON with fields: `session_id`, `user_id`, `turn_id`, `tool_name`, `latency_ms`, `model`, `stt_provider`, `tts_provider`
- **Timing Measurements**: Tracks latency for STT, reasoning, tool calls, and TTS stages
- **Debug Mode**: Set `DEBUG=true` in `.env` to enable transcript logging (disabled by default for privacy)

See the main [README.md](../README.md) for detailed observability documentation.

## 🔒 Reliability

The agent includes several reliability improvements:

- **Health Check Endpoint**: HTTP endpoint at `/health` (port 8080) for monitoring
- **Automatic Retries**: All external API calls use exponential backoff retry logic (3 retries max)
- **Error Handling**: Graceful fallbacks with user-friendly error messages in Spanish
- **Timeout Protection**: All API calls have 5-second timeouts to prevent hanging

## 📁 Project Structure

```
agent-server/
├── agent.py                 # Main agent implementation
├── restaurant_tools.py      # API integration functions
├── src/
│   ├── observability.py     # Structured logging and timing
│   ├── retry.py             # Retry logic with exponential backoff
│   └── health.py            # Health check HTTP endpoint
├── debug_menu.py           # Debug utilities
├── test_thinking_sounds.py # Audio testing
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables template
├── .env                   # Your environment variables (not in git)
└── README.md              # This file
```

## 🐛 Troubleshooting

### Agent Won't Start

- **Python version**: Ensure you're using Python 3.10+ (check with `python3 --version`)
- **Dependencies**: Verify all packages are installed: `pip install -r requirements.txt`
- **Model files**: Run `python3 agent.py download-files` to download required model weights
- **Environment variables**: Verify all required API keys are set in `.env`
- **LiveKit server**: Check that LiveKit server is accessible and credentials are correct

### Import Errors

- **`ModuleNotFoundError: No module named 'livekit.plugins.turn_detector'`**: Install the turn detector plugin: `pip install livekit-plugins-turn-detector`
- **`ImportError: cannot import name 'TypeAlias'`**: You're using Python < 3.10. Upgrade to Python 3.10+
- **`ModuleNotFoundError: No module named 'livekit.plugins'`**: Install all plugin packages from `requirements.txt`

### API Connection Issues

- Verify the restaurant API is running at `http://localhost:3000`
- Check API authentication tokens in `restaurant_tools.py`
- Review API logs for errors
- The agent includes automatic retry logic with exponential backoff for transient failures

### Voice Recognition Issues

- Verify Deepgram API key is correct
- Check network connectivity to Deepgram
- Review LiveKit connection status

### TTS Not Working

- Verify ElevenLabs API key is valid
- Check account quota/limits
- Review voice ID configuration

## 📚 Additional Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Deepgram Documentation](https://developers.deepgram.com/)
- [ElevenLabs Documentation](https://elevenlabs.io/docs)

## 🤝 Contributing

When contributing to the agent server:

1. Follow Python PEP 8 style guidelines
2. Add docstrings to new functions
3. Test API integration changes
4. Update this README if adding new features

## 📄 License

ISC
