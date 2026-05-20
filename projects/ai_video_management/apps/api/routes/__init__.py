"""Routes package — per-aggregate route files combined into one APIRouter.

Per follow-up 062: the single 850-line `routes.py` was split into
`{aggregate}__route.py` files, one per aggregate. This `__init__.py`
exposes a combined `router` that `apps/api/app_factory.py` mounts on
the FastAPI app via `app.include_router(router)`. Each per-aggregate
file defines its own `APIRouter()`.
"""
from __future__ import annotations

from fastapi import APIRouter

from apps.api.routes.actor__route import router as _actor_router
from apps.api.routes.casting__route import router as _casting_router
from apps.api.routes.character_video__route import router as _character_video_router
from apps.api.routes.downloads__route import router as _downloads_router
from apps.api.routes.file__route import router as _file_router
from apps.api.routes.frame__route import router as _frame_router
from apps.api.routes.media__route import router as _media_router
from apps.api.routes.novel__route import router as _novel_router
from apps.api.routes.tree__route import router as _tree_router

router = APIRouter()
router.include_router(_tree_router)
router.include_router(_file_router)
router.include_router(_media_router)
router.include_router(_frame_router)
router.include_router(_downloads_router)
router.include_router(_actor_router)
router.include_router(_casting_router)
router.include_router(_character_video_router)
router.include_router(_novel_router)
