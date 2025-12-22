import asyncio
from collections import defaultdict
from dataclasses import dataclass
import uuid
import json


@dataclass
class SSEMessage:
    event: str
    data: dict


class SSEHub:
    def __init__(self) -> None:
        self._queues: dict[uuid.UUID, list[asyncio.Queue[SSEMessage]]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def subscribe(self, game_id: uuid.UUID) -> asyncio.Queue[SSEMessage]:
        q: asyncio.Queue[SSEMessage] = asyncio.Queue(maxsize=200)
        async with self._lock:
            self._queues[game_id].append(q)
        return q

    async def unsubscribe(self, game_id: uuid.UUID, q: asyncio.Queue[SSEMessage]) -> None:
        async with self._lock:
            if game_id in self._queues and q in self._queues[game_id]:
                self._queues[game_id].remove(q)

    async def publish(self, game_id: uuid.UUID, msg: SSEMessage) -> None:
        async with self._lock:
            qs = list(self._queues.get(game_id, []))
        for q in qs:
            if not q.full():
                q.put_nowait(msg)


hub = SSEHub()


def sse_format(msg: SSEMessage) -> str:
    payload = json.dumps(msg.data, separators=(",", ":"))
    return f"event: {msg.event}\ndata: {payload}\n\n"
