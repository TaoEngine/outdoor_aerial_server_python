import asyncio
import logging

from service.controller import FetchService

log = logging.getLogger(__name__)


async def wt_broadcast(scope, receive, send):
    msg = await receive()
    if msg["type"] != "webtransport.connect":
        return

    await send({"type": "webtransport.accept"})

    stream_id = None
    while stream_id is None:
        msg = await receive()
        if msg["type"] == "webtransport.stream.receive":
            stream_id = msg["stream"]
            break
        if msg["type"] == "webtransport.close":
            return

    fetch = FetchService()

    async def push(data: bytes) -> None:
        await send(
            {
                "type": "webtransport.stream.send",
                "stream": stream_id,
                "data": data,
            }
        )

    fetch.subscribe(stream_id, push)

    try:
        while True:
            msg = await receive()
            if msg["type"] == "webtransport.close":
                break
    except asyncio.CancelledError:
        pass
    finally:
        if stream_id is not None:
            fetch.unsubscribe(stream_id)
