import os
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

async def create_session(session_name, api_id, api_hash):
    # Check if the session file already exists
    if os.path.exists(session_name + '.session'):
        print(f"Session file '{session_name}.session' already exists. No new session created.")
        return

    # Create a new Telegram client
    client = TelegramClient(session_name, api_id, api_hash)

    # Start the client and perform authentication
    await client.start()

    # Check if the user needs to enter a password
    if await client.is_user_authorized():
        print("User is already authorized.")
    else:
        print("User is not authorized. Please complete the authentication process.")
        phone_number = input("Please enter your phone number: ")
        await client.send_code_request(phone_number)
        code = input("Please enter the code you received: ")
        await client.sign_in(phone_number, code)

        # If the account has 2FA enabled, handle password
        if isinstance(await client.get_me(), str):
            password = input("Please enter your password: ")
            await client.sign_in(password=password)

    print(f"Session '{session_name}.session' created successfully.")
    await client.disconnect()

if __name__ == "__main__":
    # Set your API ID and HASH here
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")

    # Get the session name from command line arguments
    import sys
    if len(sys.argv) < 2:
        print("Please provide a session name as a command line argument.")
        sys.exit(1)

    session_name = sys.argv[1]
    asyncio.run(create_session(session_name, api_id, api_hash))