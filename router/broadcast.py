from pywebtransport import WebTransportStream
from service.broadcast.broadcast import BroadcastService


async def broadcast_handler(stream: WebTransportStream):
    print("有人连接")
    broadcast_service = BroadcastService()

    async def client_callback(audio_frame):
        try:
            print("正在发送...")
            await stream.write(data=audio_frame)
        except Exception:
            pass

    broadcast_service.subscribe(client=client_callback)
