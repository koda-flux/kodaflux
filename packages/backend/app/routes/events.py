import asyncio
import json
import os

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import redis.asyncio as aioredis


router = APIRouter(prefix="/events", tags=["events"])

CHANNEL = os.getenv("REDIS_CHANNEL")
if not CHANNEL:
    raise ValueError("REDIS_CHANNEL environment variable not set")


def get_redis() -> aioredis.Redis:
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        raise ValueError("REDIS_URL environment variable not set")

    return aioredis.from_url(
        redis_url,
        decode_responses=True,
    )


async def notify_new_project(data: dict) -> None:
    """
    Publishes a new project event to the Redis channel.
    Any worker with an active SSE subscriber will pick it up.
    """
    r = get_redis()
    try:
        await r.publish(CHANNEL, json.dumps(data))
    finally:
        await r.aclose()


async def event_generator():
    """
    Subscribes to the Redis channel and yields SSE events
    as they arrive.
    """
    r = get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(CHANNEL)

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                yield f"data: {message['data']}\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        await pubsub.unsubscribe(CHANNEL)
        await r.aclose()


@router.get("/stream")
async def event_stream():
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        },
    )
