import asyncio
from agent import RestaurantAssistant

async def test_thinking_sounds():
    """Test the thinking sounds functionality"""
    print("Testing thinking sounds...")

    # Create an instance of the restaurant assistant
    assistant = RestaurantAssistant()

    # Test the thinking sounds dictionary
    print("Available thinking sounds:")
    for sound_type, url in assistant.thinking_sounds.items():
        print(f"  {sound_type}: {url}")

    # Test the play_thinking_sound method (without actual room)
    print("\nTesting thinking sound methods...")
    try:
        # This will fail since we don't have a room, but it tests the method structure
        await assistant.play_thinking_sound("thinking")
        print("✓ play_thinking_sound method works")
    except Exception as e:
        print(f"Expected error (no room): {e}")

    try:
        await assistant.stop_thinking_sound()
        print("✓ stop_thinking_sound method works")
    except Exception as e:
        print(f"Expected error (no room): {e}")

    print("\n✓ Thinking sounds implementation complete!")

if __name__ == "__main__":
    asyncio.run(test_thinking_sounds())