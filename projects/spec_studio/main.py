from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.libs.app:create_app",
        factory=True,
        host=os.environ.get("BACKEND_HOST", "127.0.0.1"),
        port=int(os.environ.get("BACKEND_PORT", "8000")),
        reload=os.environ.get("BACKEND_RELOAD", "").lower() in ("1", "true", "yes"),
    )
