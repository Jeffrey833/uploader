_B='Download failed.'
_A=False
from telethon import TelegramClient,events,utils
from telethon.errors import ChatAdminRequiredError,UserNotParticipantError
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from fasttelethon import upload_file,download_file
from telethon.tl import types
from telethon import TelegramClient
from telethon.tl.types import InputFile,InputMediaPhotoExternal,DocumentAttributeFilename,DocumentAttributeVideo,InputMediaUploadedDocument
import requests,argparse,re,time,os,json,jwt,subprocess,datetime,asyncio,shutil
from dotenv import load_dotenv
load_dotenv()
session_string=os.getenv('SESSION_STRING')
bot_token=os.getenv('BOT_TOKEN')
api_id=os.getenv('API_ID')
api_hash=os.getenv('API_HASH')
admin_user='u_p_l_o_a_d_e_r'
SECRET_KEY=bot_token
GREEN='\x1b[0;32m'
NC='\x1b[0m'
class Timer:
	def __init__(A,time_between=2):A.start_time=time.time();A.time_between=time_between
	def can_send(A):
		if time.time()>A.start_time+A.time_between:A.start_time=time.time();return True
		return _A
def download_video(magnet_link):
	print('Downloading..');A=subprocess.Popen(['torrent','download',magnet_link]);A.communicate()
	if A.returncode==0:print('Download completed successfully.');return True
	else:print(_B);return _A
def create_jwt(data):B=datetime.datetime.utcnow()+datetime.timedelta(seconds=60);A=jwt.encode(data,SECRET_KEY,algorithm='HS256');return A
def read_jwt(token):
	try:A=jwt.decode(token,SECRET_KEY,algorithms=['HS256']);return A
	except jwt.ExpiredSignatureError:return'Token has expired'
	except jwt.InvalidTokenError:return'Invalid token'
def make_filename_safe(filename,divider):A=re.sub('[^a-zA-Z0-9]',divider,filename);A=re.sub('-+','-',A).strip('-');return A
async def upload(file_to_upload,caption,title,image_url):
	H='.session';E=file_to_upload;I=[A for A in os.listdir()if A.endswith(H)];B='using/'
	if not os.path.exists(B):os.makedirs(B)
	R=[A for A in os.listdir('using')if A.endswith(H)]
	for C in I:
		if os.path.exists(os.path.join(B,C)):print(f"Session '{C}' is currently in use. Skipping upload.");continue
		D=C;A=TelegramClient(D,api_id,api_hash)
		async with A:
			await A.start();print('Client started. Uploading...');J=Timer();F=await A.send_message(admin_user,'Uploading started');shutil.copy(D,B)
			async def K(current,total):
				if J.can_send():A=current*100/total;print(f"\tUploading with {GREEN}{D}{NC} {A:.2f}%");await F.edit(f"Uploading with {D} {A}%")
			with open(E,'rb')as L:G=await upload_file(A,L,title=title,progress_callback=K);M=G.to_dict();N,O=utils.get_attributes(E);P=InputMediaPhotoExternal(url=image_url);Q=types.InputMediaUploadedDocument(file=G,mime_type=O,attributes=N,thumb=P,force_file=False);await A.delete_messages(admin_user,[F.id]);await A.send_file(entity=admin_user,caption=caption,file=Q)
			await A.disconnect()
		shutil.move(os.path.join(B,C),C);os.remove(E);return M
async def send_video_by_id(video_data):B='name';A=video_data;await client.start();C=InputFile(id=A['id'],parts=A['parts'],name=A[B],md5_checksum=A['md5_checksum']);D=[DocumentAttributeFilename(file_name=A[B]),DocumentAttributeVideo(duration=0,w=1,h=1,round_message=_A,supports_streaming=_A)];E=InputMediaUploadedDocument(file=C,mime_type='video/mp4',attributes=D);await client.send_file(entity=admin_user,file=E,caption='Here is the video sent using InputMediaUploadedDocument!');print('Video sent successfully!')
def find_file():
	for(B,E,C)in os.walk(os.getcwd()):
		for A in C:
			if A.endswith('.mp4')or A.endswith('.mkv')or A.endswith('.avi'):D=os.path.join(B,A);return{'file':D,'root':B}
if __name__=='__main__':parser=argparse.ArgumentParser(description='Send a video file to a specified chat.');parser.add_argument('filename',type=str,help='The name of the video file to upload');args=parser.parse_args();filename=args.filename;title=make_filename_safe(filename,' ');image_url='https://raw.githubusercontent.com/aN4ksaL4y/uploader/refs/heads/main/thumbnail.jpg';asyncio.run(upload(file_to_upload=filename,caption=title,title=title,image_url=image_url))