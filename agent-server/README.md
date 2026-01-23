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
- **`debug_menu.py`**: Debug utilities for testing
- **`test_thinking_sounds.py`**: Testing utilities for audio feedback

## 📋 Prerequisites

- **Python** >= 3.8
- **pip** (Python package manager)
- **LiveKit Server** (cloud or self-hosted)
- **API Keys** for:
  - LiveKit
  - OpenAI
  - ElevenLabs
  - Deepgram

## 🚀 Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   cp env.example .env
   ```

3. **Configure your `.env` file**:
   ```env
   # LiveKit Configuration
   LIVEKIT_URL=wss://your-livekit-server.com
   LIVEKIT_API_KEY=your_livekit_api_key
   LIVEKIT_API_SECRET=your_livekit_api_secret

   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key

   # ElevenLabs Configuration
   ELEVENLABS_API_KEY=your_elevenlabs_api_key

   # Deepgram Configuration
   DEEPGRAM_API_KEY=your_deepgram_api_key
   ```

## 🎮 Usage

### Running the Agent

Start the agent server:
```bash
python agent.py
```

The agent will connect to LiveKit and be ready to handle voice interactions. Make sure:
1. The restaurant API is running at `http://localhost:3000`
2. Your LiveKit server is accessible
3. All API keys are correctly configured

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

| Variable | Description | Required |
|----------|-------------|----------|
| `LIVEKIT_URL` | LiveKit server WebSocket URL | Yes |
| `LIVEKIT_API_KEY` | LiveKit API key | Yes |
| `LIVEKIT_API_SECRET` | LiveKit API secret | Yes |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 | Yes |
| `ELEVENLABS_API_KEY` | ElevenLabs API key for TTS | Yes |
| `DEEPGRAM_API_KEY` | Deepgram API key for STT | Yes |

### API Configuration

The agent connects to the restaurant API at `http://localhost:3000/v1` by default. This is configured in `restaurant_tools.py`:

```python
API_BASE_URL = "http://localhost:3000/v1"
```

To change the API URL, modify this constant in `restaurant_tools.py`.

### Voice Configuration

The agent uses:
- **STT**: Deepgram Nova-3 (multilingual)
- **LLM**: OpenAI GPT-4o-mini
- **TTS**: ElevenLabs multilingual v2 (voice: "rola")
- **VAD**: Silero Voice Activity Detection
- **Turn Detection**: Multilingual model

You can modify these in the `entrypoint` function in `agent.py`.

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

## 📁 Project Structure

```
agent-server/
├── agent.py                 # Main agent implementation
├── restaurant_tools.py      # API integration functions
├── debug_menu.py           # Debug utilities
├── test_thinking_sounds.py # Audio testing
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables template
├── .env                   # Your environment variables (not in git)
└── README.md              # This file
```

## 🐛 Troubleshooting

### Agent Won't Start

- Verify all environment variables are set correctly
- Check that LiveKit server is accessible
- Ensure Python dependencies are installed: `pip install -r requirements.txt`

### API Connection Issues

- Verify the restaurant API is running at `http://localhost:3000`
- Check API authentication tokens in `restaurant_tools.py`
- Review API logs for errors

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
