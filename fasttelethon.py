_A = None
import asyncio, hashlib, inspect, logging, math, os
from collections import defaultdict
from typing import (
    Optional,
    List,
    AsyncGenerator,
    Union,
    Awaitable,
    DefaultDict,
    Tuple,
    BinaryIO,
)
from telethon import utils, helpers, TelegramClient
from telethon.crypto import AuthKey
from telethon.network import MTProtoSender
from telethon.tl.alltlobjects import LAYER
from telethon.tl.functions import InvokeWithLayerRequest
from telethon.tl.functions.auth import (
    ExportAuthorizationRequest,
    ImportAuthorizationRequest,
)
from telethon.tl.functions.upload import (
    GetFileRequest,
    SaveFilePartRequest,
    SaveBigFilePartRequest,
)
from telethon.tl.types import (
    Document,
    InputFileLocation,
    InputDocumentFileLocation,
    InputPhotoFileLocation,
    InputPeerPhotoFileLocation,
    TypeInputFile,
    InputFileBig,
    InputFile,
)

try:
    from mautrix.crypto.attachments import async_encrypt_attachment
except ImportError:
    async_encrypt_attachment = _A
log = logging.getLogger("telethon")
TypeLocation = Union[
    Document,
    InputDocumentFileLocation,
    InputPeerPhotoFileLocation,
    InputFileLocation,
    InputPhotoFileLocation,
]


class DownloadSender:
    client: TelegramClient
    sender: MTProtoSender
    request: GetFileRequest
    remaining: int
    stride: int

    def __init__(A, client, sender, file, offset, limit, stride, count):
        A.sender = sender
        A.client = client
        A.request = GetFileRequest(file, offset=offset, limit=limit)
        A.stride = stride
        A.remaining = count

    async def next(A):
        if not A.remaining:
            return
        B = await A.client._call(A.sender, A.request)
        A.remaining -= 1
        A.request.offset += A.stride
        return B.bytes

    def disconnect(A):
        return A.sender.disconnect()


class UploadSender:
    client: TelegramClient
    sender: MTProtoSender
    request: Union[SaveFilePartRequest, SaveBigFilePartRequest]
    part_count: int
    stride: int
    previous: Optional[asyncio.Task]
    loop: asyncio.AbstractEventLoop

    def __init__(A, client, sender, file_id, part_count, big, index, stride, loop):
        D = index
        C = part_count
        B = file_id
        A.client = client
        A.sender = sender
        A.part_count = C
        if big:
            A.request = SaveBigFilePartRequest(B, D, C, b"")
        else:
            A.request = SaveFilePartRequest(B, D, b"")
        A.stride = stride
        A.previous = _A
        A.loop = loop

    async def next(A, data):
        if A.previous:
            await A.previous
        A.previous = A.loop.create_task(A._next(data))

    async def _next(A, data):
        A.request.bytes = data
        log.debug(
            f"Sending file part {A.request.file_part}/{A.part_count} with {len(data)} bytes"
        )
        await A.client._call(A.sender, A.request)
        A.request.file_part += A.stride

    async def disconnect(A):
        if A.previous:
            await A.previous
        return await A.sender.disconnect()


class ParallelTransferrer:
    client: TelegramClient
    loop: asyncio.AbstractEventLoop
    dc_id: int
    senders: Optional[List[Union[DownloadSender, UploadSender]]]
    auth_key: AuthKey
    upload_ticker: int

    def __init__(A, client, dc_id=_A):
        B = dc_id
        A.client = client
        A.loop = A.client.loop
        A.dc_id = B or A.client.session.dc_id
        A.auth_key = (
            _A if B and A.client.session.dc_id != B else A.client.session.auth_key
        )
        A.senders = _A
        A.upload_ticker = 0

    async def _cleanup(A):
        await asyncio.gather(*[A.disconnect() for A in A.senders])
        A.senders = _A

    @staticmethod
    def _get_connection_count(file_size, max_count=20, full_size=104857600):
        C = full_size
        B = max_count
        A = file_size
        if A > C:
            return B
        return math.ceil(A / C * B)

    async def _init_download(C, connections, file, part_count, part_size):
        B = part_size
        A = connections
        E, D = divmod(part_count, A)

        def F():
            nonlocal D
            if D > 0:
                D -= 1
                return E + 1
            return E

        C.senders = [
            await C._create_download_sender(file, 0, B, A * B, F()),
            *await asyncio.gather(
                *[
                    C._create_download_sender(file, D, B, A * B, F())
                    for D in range(1, A)
                ]
            ),
        ]

    async def _create_download_sender(A, file, index, part_size, stride, part_count):
        B = part_size
        return DownloadSender(
            A.client, await A._create_sender(), file, index * B, B, stride, part_count
        )

    async def _init_upload(A, connections, file_id, part_count, big):
        D = part_count
        C = file_id
        B = connections
        A.senders = [
            await A._create_upload_sender(C, D, big, 0, B),
            *await asyncio.gather(
                *[A._create_upload_sender(C, D, big, E, B) for E in range(1, B)]
            ),
        ]

    async def _create_upload_sender(A, file_id, part_count, big, index, stride):
        return UploadSender(
            A.client,
            await A._create_sender(),
            file_id,
            part_count,
            big,
            index,
            stride,
            loop=A.loop,
        )

    async def _create_sender(A):
        C = await A.client._get_dc(A.dc_id)
        B = MTProtoSender(A.auth_key, loggers=A.client._log)
        await B.connect(
            A.client._connection(
                C.ip_address, C.port, C.id, loggers=A.client._log, proxy=A.client._proxy
            )
        )
        if not A.auth_key:
            log.debug(f"Exporting auth to DC {A.dc_id}")
            D = await A.client(ExportAuthorizationRequest(A.dc_id))
            A.client._init_request.query = ImportAuthorizationRequest(
                id=D.id, bytes=D.bytes
            )
            E = InvokeWithLayerRequest(LAYER, A.client._init_request)
            await B.send(E)
            A.auth_key = B.auth_key
        return B

    async def init_upload(D, file_id, file_size, part_size_kb=_A, connection_count=_A):
        B = connection_count
        A = file_size
        B = B or D._get_connection_count(A)
        C = (part_size_kb or utils.get_appropriated_part_size(A)) * 1024
        E = (A + C - 1) // C
        F = A > 10485760
        await D._init_upload(B, file_id, E, F)
        return C, E, F

    async def upload(A, part):
        await A.senders[A.upload_ticker].next(part)
        A.upload_ticker = (A.upload_ticker + 1) % len(A.senders)

    async def finish_upload(A):
        await A._cleanup()

    async def download(A, file, file_size, part_size_kb=_A, connection_count=_A):
        C = file_size
        B = connection_count
        B = B or A._get_connection_count(C)
        D = (part_size_kb or utils.get_appropriated_part_size(C)) * 1024
        E = math.ceil(C / D)
        log.debug(f"Starting parallel download: {B} {D} {E} {file!s}")
        await A._init_download(B, file, E, D)
        F = 0
        while F < E:
            G = []
            for I in A.senders:
                G.append(A.loop.create_task(I.next()))
            for J in G:
                H = await J
                if not H:
                    break
                yield H
                F += 1
                log.debug(f"Part {F} downloaded")
        log.debug("Parallel download finished, cleaning up connections")
        await A._cleanup()


parallel_transfer_locks = defaultdict(lambda: asyncio.Lock())


def stream_file(file_to_stream, chunk_size=1024):
    while True:
        A = file_to_stream.read(chunk_size)
        if not A:
            break
        yield A


async def _internal_transfer_to_telegram(client, response, title, progress_callback):
    I = progress_callback
    H = title
    E = response
    F = helpers.generate_random_long()
    D = os.path.getsize(E.name)
    J = hashlib.md5()
    C = ParallelTransferrer(client)
    G, K, L = await C.init_upload(F, D)
    A = bytearray()
    for B in stream_file(E):
        if I:
            M = I(E.tell(), D)
            if inspect.isawaitable(M):
                await M
        if not L:
            J.update(B)
        if len(A) == 0 and len(B) == G:
            await C.upload(B)
            continue
        O = len(A) + len(B)
        if O >= G:
            N = G - len(A)
            A.extend(B[:N])
            await C.upload(bytes(A))
            A.clear()
            A.extend(B[N:])
        else:
            A.extend(B)
    if len(A) > 0:
        await C.upload(bytes(A))
    await C.finish_upload()
    if L:
        return InputFileBig(F, K, H), D
    else:
        return InputFile(F, K, H, J.hexdigest()), D


async def download_file(client, location, out, progress_callback=_A):
    C = progress_callback
    B = out
    A = location
    D = A.size
    F, A = utils.get_input_location(A)
    G = ParallelTransferrer(client, F)
    H = G.download(A, D)
    async for I in H:
        B.write(I)
        if C:
            E = C(B.tell(), D)
            if inspect.isawaitable(E):
                await E
    return B


async def upload_file(client, file, title, progress_callback=_A):
    A = (await _internal_transfer_to_telegram(client, file, title, progress_callback))[
        0
    ]
    return A
