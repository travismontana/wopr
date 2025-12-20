import uuid
import asyncio
from fastapi import FastAPI, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session

from .db import get_db
from . import models
from .routers import games, captures, jobs
from .sse import hub, sse_format, SSEMessage
from .settings import settings

app = FastAPI(
    title="WOPR API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(games.router)
app.include_router(captures.router)
app.include_router(jobs.router)


@app.get("/api/v1/games/{game_id}/stream", tags=["realtime"])
async def stream_game(game_id: uuid.UUID, db: Session = Depends(get_db)):
    if not db.get(models.Game, game_id):
        raise HTTPException(status_code=404, detail="Game not found")

    q = await hub.subscribe(game_id)

    async def event_generator():
        try:
            yield sse_format(SSEMessage(event="hello", data={"game_id": str(game_id)}))
            while True:
                try:
                    msg = await asyncio.wait_for(q.get(), timeout=settings.sse_keepalive_seconds)
                    yield sse_format(msg)
                except asyncio.TimeoutError:
                    yield "event: keepalive\ndata: {}\n\n"
        finally:
            await hub.unsubscribe(game_id, q)

    return EventSourceResponse(event_generator())
