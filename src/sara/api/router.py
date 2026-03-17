from fastapi import APIRouter

from sara.api import enroll, health, synthesize, transcribe, users, verify, websocket

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(users.router)
api_router.include_router(enroll.router)
api_router.include_router(verify.router)
api_router.include_router(transcribe.router)
api_router.include_router(synthesize.router)

# WebSocket no lleva prefix /api/v1
ws_router = websocket.router
