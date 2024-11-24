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
_A=None
import asyncio,hashlib,inspect,logging,math,os
from collections import defaultdict
from typing import Optional,List,AsyncGenerator,Union,Awaitable,DefaultDict,Tuple,BinaryIO
from telethon import utils,helpers,TelegramClient
from telethon.crypto import AuthKey
from telethon.network import MTProtoSender
from telethon.tl.alltlobjects import LAYER
from telethon.tl.functions import InvokeWithLayerRequest
from telethon.tl.functions.auth import ExportAuthorizationRequest,ImportAuthorizationRequest
from telethon.tl.functions.upload import GetFileRequest,SaveFilePartRequest,SaveBigFilePartRequest
from telethon.tl.types import Document,InputFileLocation,InputDocumentFileLocation,InputPhotoFileLocation,InputPeerPhotoFileLocation,TypeInputFile,InputFileBig,InputFile
try:from mautrix.crypto.attachments import async_encrypt_attachment
except ImportError:async_encrypt_attachment=_A
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
log=logging.getLogger('telethon')
TypeLocation=Union[Document,InputDocumentFileLocation,InputPeerPhotoFileLocation,InputFileLocation,InputPhotoFileLocation]
class DownloadSender:
	client:TelegramClient;sender:MTProtoSender;request:GetFileRequest;remaining:int;stride:int
	def __init__(A,client,sender,file,offset,limit,stride,count):A.sender=sender;A.client=client;A.request=GetFileRequest(file,offset=offset,limit=limit);A.stride=stride;A.remaining=count
	async def next(A):
		if not A.remaining:return
		B=await A.client._call(A.sender,A.request);A.remaining-=1;A.request.offset+=A.stride;return B.bytes
	def disconnect(A):return A.sender.disconnect()
class UploadSender:
	client:TelegramClient;sender:MTProtoSender;request:Union[SaveFilePartRequest,SaveBigFilePartRequest];part_count:int;stride:int;previous:Optional[asyncio.Task];loop:asyncio.AbstractEventLoop
	def __init__(A,client,sender,file_id,part_count,big,index,stride,loop):
		B=index;C=part_count;D=file_id;A.client=client;A.sender=sender;A.part_count=C
		if big:A.request=SaveBigFilePartRequest(D,B,C,b'')
		else:A.request=SaveFilePartRequest(D,B,b'')
		A.stride=stride;A.previous=_A;A.loop=loop
	async def next(A,data):
		if A.previous:await A.previous
		A.previous=A.loop.create_task(A._next(data))
	async def _next(A,data):A.request.bytes=data;log.debug(f"Sending file part {A.request.file_part}/{A.part_count} with {len(data)} bytes");await A.client._call(A.sender,A.request);A.request.file_part+=A.stride
	async def disconnect(A):
		if A.previous:await A.previous
		return await A.sender.disconnect()
class ParallelTransferrer:
	client:TelegramClient;loop:asyncio.AbstractEventLoop;dc_id:int;senders:Optional[List[Union[DownloadSender,UploadSender]]];auth_key:AuthKey;upload_ticker:int
	def __init__(A,client,dc_id=_A):B=dc_id;A.client=client;A.loop=A.client.loop;A.dc_id=B or A.client.session.dc_id;A.auth_key=_A if B and A.client.session.dc_id!=B else A.client.session.auth_key;A.senders=_A;A.upload_ticker=0
	async def _cleanup(A):await asyncio.gather(*[A.disconnect()for A in A.senders]);A.senders=_A
	@staticmethod
	def _get_connection_count(file_size,max_count=20,full_size=104857600):
		A=full_size;B=max_count;C=file_size
		if C>A:return B
		return math.ceil(C/A*B)
	async def _init_download(C,connections,file,part_count,part_size):
		A=part_size;B=connections;E,D=divmod(part_count,B)
		def F():
			nonlocal D
			if D>0:D-=1;return E+1
			return E
		C.senders=[await C._create_download_sender(file,0,A,B*A,F()),*await asyncio.gather(*[C._create_download_sender(file,D,A,B*A,F())for D in range(1,B)])]
	async def _create_download_sender(A,file,index,part_size,stride,part_count):B=part_size;return DownloadSender(A.client,await A._create_sender(),file,index*B,B,stride,part_count)
	async def _init_upload(A,connections,file_id,part_count,big):C=part_count;D=file_id;B=connections;A.senders=[await A._create_upload_sender(D,C,big,0,B),*await asyncio.gather(*[A._create_upload_sender(D,C,big,E,B)for E in range(1,B)])]
	async def _create_upload_sender(A,file_id,part_count,big,index,stride):return UploadSender(A.client,await A._create_sender(),file_id,part_count,big,index,stride,loop=A.loop)
	async def _create_sender(A):
		C=await A.client._get_dc(A.dc_id);B=MTProtoSender(A.auth_key,loggers=A.client._log);await B.connect(A.client._connection(C.ip_address,C.port,C.id,loggers=A.client._log,proxy=A.client._proxy))
		if not A.auth_key:log.debug(f"Exporting auth to DC {A.dc_id}");D=await A.client(ExportAuthorizationRequest(A.dc_id));A.client._init_request.query=ImportAuthorizationRequest(id=D.id,bytes=D.bytes);E=InvokeWithLayerRequest(LAYER,A.client._init_request);await B.send(E);A.auth_key=B.auth_key
		return B
	async def init_upload(D,file_id,file_size,part_size_kb=_A,connection_count=_A):B=connection_count;A=file_size;B=B or D._get_connection_count(A);C=(part_size_kb or utils.get_appropriated_part_size(A))*1024;E=(A+C-1)//C;F=A>10485760;await D._init_upload(B,file_id,E,F);return C,E,F
	async def upload(A,part):await A.senders[A.upload_ticker].next(part);A.upload_ticker=(A.upload_ticker+1)%len(A.senders)
	async def finish_upload(A):await A._cleanup()
	async def download(A,file,file_size,part_size_kb=_A,connection_count=_A):
		C=file_size;B=connection_count;B=B or A._get_connection_count(C);D=(part_size_kb or utils.get_appropriated_part_size(C))*1024;E=math.ceil(C/D);log.debug(f"Starting parallel download: {B} {D} {E} {file!s}");await A._init_download(B,file,E,D);F=0
		while F<E:
			G=[]
			for I in A.senders:G.append(A.loop.create_task(I.next()))
			for J in G:
				H=await J
				if not H:break
				yield H;F+=1;log.debug(f"Part {F} downloaded")
		log.debug('Parallel download finished, cleaning up connections');await A._cleanup()
parallel_transfer_locks=defaultdict(lambda:asyncio.Lock())
def stream_file(file_to_stream,chunk_size=1024):
	while True:
		A=file_to_stream.read(chunk_size)
		if not A:break
		yield A
async def _internal_transfer_to_telegram(client,response,title,progress_callback):
	H=progress_callback;I=title;E=response;F=helpers.generate_random_long();D=os.path.getsize(E.name);J=hashlib.md5();C=ParallelTransferrer(client);G,K,L=await C.init_upload(F,D);A=bytearray()
	for B in stream_file(E):
		if H:
			M=H(E.tell(),D)
			if inspect.isawaitable(M):await M
		if not L:J.update(B)
		if len(A)==0 and len(B)==G:await C.upload(B);continue
		O=len(A)+len(B)
		if O>=G:N=G-len(A);A.extend(B[:N]);await C.upload(bytes(A));A.clear();A.extend(B[N:])
		else:A.extend(B)
	if len(A)>0:await C.upload(bytes(A))
	await C.finish_upload()
	if L:return InputFileBig(F,K,I),D
	else:return InputFile(F,K,I,J.hexdigest()),D
async def download_file(client,location,out,progress_callback=_A):
	C=progress_callback;B=out;A=location;D=A.size;F,A=utils.get_input_location(A);G=ParallelTransferrer(client,F);H=G.download(A,D)
	async for I in H:
		B.write(I)
		if C:
			E=C(B.tell(),D)
			if inspect.isawaitable(E):await E
	return B
async def upload_file(client,file,title,progress_callback=_A):A=(await _internal_transfer_to_telegram(client,file,title,progress_callback))[0];return A
if __name__=='__main__':parser=argparse.ArgumentParser(description='Send a video file to a specified chat.');parser.add_argument('filename',type=str,help='The name of the video file to upload');args=parser.parse_args();filename=args.filename;title=make_filename_safe(filename,' ');image_url='https://raw.githubusercontent.com/aN4ksaL4y/uploader/refs/heads/main/thumbnail.jpg';asyncio.run(upload(file_to_upload=filename,caption=title,title=title,image_url=image_url))