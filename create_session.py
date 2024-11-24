import os,asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
async def create_session(session_name,api_id,api_hash):
	B=session_name
	if os.path.exists(B+'.session'):print(f"Session file '{B}.session' already exists. No new session created.");return
	A=TelegramClient(B,api_id,api_hash);await A.start()
	if await A.is_user_authorized():print('User is already authorized.')
	else:
		print('User is not authorized. Please complete the authentication process.');C=input('Please enter your phone number: ');await A.send_code_request(C);D=input('Please enter the code you received: ');await A.sign_in(C,D)
		if isinstance(await A.get_me(),str):E=input('Please enter your password: ');await A.sign_in(password=E)
	print(f"Session '{B}.session' created successfully.");await A.disconnect()
if __name__=='__main__':
	api_id=os.getenv('API_ID');api_hash=os.getenv('API_HASH');import sys
	if len(sys.argv)<2:print('Please provide a session name as a command line argument.');sys.exit(1)
	session_name=sys.argv[1];asyncio.run(create_session(session_name,api_id,api_hash))