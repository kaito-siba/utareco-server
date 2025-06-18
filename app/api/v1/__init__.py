"""API v1 router module."""

from fastapi import APIRouter

from .hpcp import router as hpcp_router
from .recordings import router as recordings_router

# API v1 ルーター
api_v1_router = APIRouter(prefix="/api/v1")

# 各エンドポイントルーターを追加
api_v1_router.include_router(hpcp_router)
api_v1_router.include_router(recordings_router)
