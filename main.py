import asyncio
from pywebtransport import (
    Event,
    ServerApp,
    ServerConfig,
    WebTransportSession,
    WebTransportStream,
)
from pywebtransport.types import EventType
from pywebtransport.utils import generate_self_signed_cert
from router.broadcast import broadcast_handler

app = ServerApp(
    config=ServerConfig(certfile="cert/localhost.crt", keyfile="cert/localhost.key")
)


@app.route(path="/station")
async def route_station(session: WebTransportSession) -> None:
    pass


@app.route(path="/program")
async def route_program(session: WebTransportSession) -> None:
    pass


@app.route(path="/episode")
async def route_episode(session: WebTransportSession) -> None:
    pass


@app.route(path="/broadcast")
async def route_broadcast(session: WebTransportSession) -> None:
    async def on_stream(event: Event):
        if isinstance(event.data, dict) and (stream := event.data.get("stream")):
            if isinstance(stream, WebTransportStream):
                asyncio.create_task(broadcast_handler(stream))

    session.on(event_type=EventType.STREAM_OPENED, handler=on_stream)
    await session.wait_for(event_type=EventType.SESSION_CLOSED)
    session.off(event_type=EventType.STREAM_OPENED, handler=on_stream)


if __name__ == "__main__":
    generate_self_signed_cert(hostname="localhost", output_dir="cert")
    app.run(host="127.0.0.1", port=8908)
