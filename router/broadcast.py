from pywebtransport import WebTransportStream

async def broadcast_handler(stream: WebTransportStream):
    """
    请求广播音频信号的方式
    """
    while True:
        await stream.write(data=b".", end_stream=False)