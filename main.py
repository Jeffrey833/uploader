_B = "Download failed."
_A = False
from telethon import TelegramClient, events, utils
from telethon.errors import ChatAdminRequiredError, UserNotParticipantError
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from fasttelethon import upload_file, download_file
from telethon.tl import types
from telethon import TelegramClient
from telethon.tl.types import (
    InputFile,
    InputMediaPhotoExternal,
    DocumentAttributeFilename,
    DocumentAttributeVideo,
    InputMediaUploadedDocument,
)
import requests, argparse, re, time, os, json, jwt, subprocess, datetime, asyncio, shutil
from dotenv import load_dotenv

load_dotenv()
session_string = os.getenv("SESSION_STRING")
bot_token = os.getenv("BOT_TOKEN")
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
admin_user = "u_p_l_o_a_d_e_r"
SECRET_KEY = bot_token
# client = TelegramClient("test", api_id, api_hash)


class Timer:
    def __init__(A, time_between=2):
        A.start_time = time.time()
        A.time_between = time_between

    def can_send(A):
        if time.time() > A.start_time + A.time_between:
            A.start_time = time.time()
            return True
        return _A


def download_video(magnet_link):
    # return True
    print("Downloading..")
    A = subprocess.Popen(["torrent", "download", magnet_link])
    A.communicate()
    if A.returncode == 0:
        print("Download completed successfully.")
        return True
    else:
        print(_B)
        return _A


def create_jwt(data):
    B = datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
    A = jwt.encode(data, SECRET_KEY, algorithm="HS256")
    return A


def read_jwt(token):
    try:
        A = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return A
    except jwt.ExpiredSignatureError:
        return "Token has expired"
    except jwt.InvalidTokenError:
        return "Invalid token"


def make_filename_safe(filename, divider):
    A = re.sub("[^a-zA-Z0-9]", divider, filename)
    A = re.sub("-+", "-", A).strip("-")
    return A

async def upload(file_to_upload, caption, title, image_url):
    # Check for existing session files
    current_session_files = [f for f in os.listdir() if f.endswith('.session')]
    using_directory = 'using/'
    print(current_session_files)
    
    # Create the using directory if it doesn't exist
    if not os.path.exists(using_directory):
        os.makedirs(using_directory)

    current_using = [f for f in os.listdir('using') if f.endswith('.session')]
    print(current_using)

    # Check for sessions in use
    for session in current_session_files:
        if os.path.exists(os.path.join(using_directory, session)):
            print(f"Session '{session}' is currently in use. Skipping upload.")
            continue  # Skip the upload if the session is in use
        
        # else:
        session_name = session  # Use the first available session or modify as needed
        # input(session_name)
        client = TelegramClient(session_name, api_id, api_hash)

        async with client:
            await client.start()
            print("Client started. Uploading...")
            timer = Timer()
            message = await client.send_message(admin_user, "Uploading started")
            shutil.copy(session_name, using_directory)

            async def progress_callback(current, total):
                if timer.can_send():
                    percent = current * 100 / total
                    print(f"Uploading with {session_name} {percent:.2f}%")
                    await message.edit(f"Uploading with {session_name} {percent}%")

            with open(file_to_upload, "rb") as C:
                D = await upload_file(client, C, title=title, progress_callback=progress_callback)
                result = D.to_dict()
                G, H = utils.get_attributes(file_to_upload)
                I = InputMediaPhotoExternal(url=image_url)
                J = types.InputMediaUploadedDocument(
                    file=D, mime_type=H, attributes=G, thumb=I, force_file=False
                )
                # C.close()
                await client.delete_messages(admin_user, [message.id])
                await client.send_file(entity=admin_user, caption=caption, file=J)

            # I = InputMediaPhotoExternal(url=image_url)
            # J = types.InputMediaUploadedDocument(
            #     file=D, mime_type='video/mp4', attributes=G, thumb=I, force_file=_A
            # )
            # with open(file_to_upload, "rb") as file:
            #     uploaded_file = await upload_file(client, file, title=title, progress_callback=progress_callback)
            #     result = uploaded_file.to_dict()
            #     await client.delete_messages(admin_user, [message.id])
            #     await client.send_message(entity=admin_user, caption=caption, file=uploaded_file)

            await client.disconnect()

        # Move the session back after upload completion
        shutil.move(os.path.join(using_directory, session), session)

        os.remove(file_to_upload)
        return result




async def send_video_by_id(video_data):
    B = "name"
    A = video_data
    await client.start()
    C = InputFile(
        id=A["id"], parts=A["parts"], name=A[B], md5_checksum=A["md5_checksum"]
    )
    D = [
        DocumentAttributeFilename(file_name=A[B]),
        DocumentAttributeVideo(
            duration=0, w=1, h=1, round_message=_A, supports_streaming=_A
        ),
    ]
    E = InputMediaUploadedDocument(file=C, mime_type="video/mp4", attributes=D)
    await client.send_file(
        entity=admin_user,
        file=E,
        caption="Here is the video sent using InputMediaUploadedDocument!",
    )
    print("Video sent successfully!")


def find_file():
    for B, E, C in os.walk(os.getcwd()):
        for A in C:
            if A.endswith(".mp4") or A.endswith(".mkv") or A.endswith(".avi"):
                D = os.path.join(B, A)
                return {"file": D, "root": B}



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Send a video file to a specified chat."
    )
    parser.add_argument(
        "filename", type=str, help="The name of the video file to upload"
    )

    # Parse the arguments
    args = parser.parse_args()

    filename = args.filename
    title = make_filename_safe(filename, ' ')

    image_url = 'https://raw.githubusercontent.com/aN4ksaL4y/uploader/refs/heads/main/thumbnail.jpg'
    

    asyncio.run(upload(file_to_upload=filename, caption=title, title=title, image_url=image_url))
    # loop = asyncio.get_event_loop()
    # loop.close()


