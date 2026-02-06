import asyncio
import logging

from service.controller import FetchService

log = logging.getLogger(__name__)


async def wt_broadcast(scope, receive, send):
    fetch = FetchService()

    msg = await receive()
    if msg["type"] != "webtransport.connect":
        return

    await send({"type": "webtransport.accept"})

    await send({"type": "webtransport.stream.open", "is_unidirectional": True})

    stream_id = None
    while stream_id is None:
        msg = await receive()
        if msg["type"] == "webtransport.stream.opened":
            stream_id = msg["stream"]
            break
        if msg["type"] == "webtransport.close":
            return

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
