import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator

router = APIRouter(prefix="/events", tags=["events"])

# In-memory queue — one queue per connected frontend client
# TODO: Implement redis usage for possible perfomance bottlenecks.
subscribers: list[asyncio.Queue] = []


async def notify_new_project(data: dict) -> None:
    """Push a new project event to all connected SSE clients."""
    for queue in subscribers:
        await queue.put(data)


async def event_generator(queue: asyncio.Queue) -> AsyncGenerator[str, None]:
    try:
        while True:
            data = await queue.get()
            yield f"data: {json.dumps(data)}\n\n"
    except asyncio.CancelledError:
        pass


@router.get("/stream")
async def event_stream():
    """
    SSE endpoint. The frontend connects here and receives a push
    event whenever a new project is created.
    """
    queue: asyncio.Queue = asyncio.Queue()
    subscribers.append(queue)

    async def cleanup():
        async for chunk in event_generator(queue):
            yield chunk
        subscribers.remove(queue)

    return StreamingResponse(
        cleanup(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        },
    )
