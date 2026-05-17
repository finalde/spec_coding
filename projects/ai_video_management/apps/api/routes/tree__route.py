"""Tree-aggregate routes: GET /api/tree."""
from __future__ import annotations

from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from apps.api.container import Container
from libs.application.queries.tree__query import TreeQuery

router = APIRouter()


@router.get("/api/tree")
@inject
def get_tree(query: TreeQuery = Depends(Provide[Container.tree_query])) -> dict[str, Any]:
    return query.build().to_payload()
