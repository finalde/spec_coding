from .artifacts import router as artifacts_router
from .edits import router as edits_router
from .events import router as events_router
from .interview import router as interview_router
from .inputs import router as inputs_router
from .phases import router as phases_router
from .tasks import router as tasks_router

__all__ = [
    "tasks_router",
    "phases_router",
    "events_router",
    "artifacts_router",
    "edits_router",
    "inputs_router",
    "interview_router",
]
