import json
import asyncio
import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.config import settings

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, project_id: str, ws: WebSocket):
        await ws.accept()
        self._connections.setdefault(project_id, []).append(ws)

    def disconnect(self, project_id: str, ws: WebSocket):
        if project_id in self._connections:
            self._connections[project_id].remove(ws)

    async def broadcast(self, project_id: str, data: dict):
        for ws in self._connections.get(project_id, []):
            try:
                await ws.send_json(data)
            except Exception:
                pass

manager = ConnectionManager()

@router.websocket("/ws/projects/{project_id}")
async def project_ws(websocket: WebSocket, project_id: str):
    await manager.connect(project_id, websocket)
    redis = aioredis.from_url(settings.REDIS_URL)
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"project:{project_id}")
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                await manager.broadcast(project_id, json.loads(message["data"]))
    except WebSocketDisconnect:
        manager.disconnect(project_id, websocket)
    finally:
        await pubsub.unsubscribe(f"project:{project_id}")
        await redis.aclose()

async def push_ws_event(project_id: str, payload: dict):
    """Push a real-time event to all listeners of a project."""
    redis = aioredis.from_url(settings.REDIS_URL)
    await redis.publish(f"project:{project_id}", json.dumps(payload))
    await redis.aclose()
