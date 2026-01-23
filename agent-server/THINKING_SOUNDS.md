# Thinking Sounds Feature

This restaurant agent now includes thinking sounds that play during tool execution to provide audio feedback to users.

## How It Works

The thinking sounds feature works as follows:

1. **Sound Types**: Three different thinking sounds are available:
   - `thinking`: Bell ringing sound for general thinking
   - `processing`: Clock ticking sound for data processing
   - `searching`: Typewriter sound for searching/retrieving data

2. **Automatic Playback**: When any tool function is called, the appropriate thinking sound automatically starts playing in a loop.

3. **Automatic Stop**: When the tool function completes, the thinking sound automatically stops.

## Implementation Details

### Sound URLs
The thinking sounds use free sound effects from SoundJay:
- Thinking: `https://www.soundjay.com/misc/sounds/bell-ringing-05.wav`
- Processing: `https://www.soundjay.com/misc/sounds/clock-ticking-1.wav`
- Searching: `https://www.soundjay.com/misc/sounds/typewriter-1.wav`

### Tool Functions with Thinking Sounds

1. **get_menu()**: Uses "searching" sound while fetching menu data
2. **create_customer_account()**: Uses "processing" sound while creating account
3. **save_delivery_address()**: Uses "processing" sound while saving address
4. **get_delivery_addresses()**: Uses "searching" sound while retrieving addresses

### Methods

- `play_thinking_sound(sound_type)`: Starts playing the specified thinking sound
- `stop_thinking_sound()`: Stops the currently playing thinking sound

## Testing

Run the test script to verify the thinking sounds implementation:

```bash
python test_thinking_sounds.py
```

## Customization

To add more thinking sounds or change the existing ones:

1. Add new sound URLs to the `thinking_sounds` dictionary in the `__init__` method
2. Update the tool functions to use the appropriate sound type
3. Ensure the sound URLs are publicly accessible and in a supported audio format

## Notes

- The thinking sounds are played using LiveKit's room audio player
- Sounds loop until the tool function completes
- Error handling is included to prevent crashes if audio playback fails
- The feature is designed to work seamlessly with the existing agent functionality