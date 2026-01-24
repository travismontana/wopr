from typing import TypeVar, Generic, Type, Callable, Optional
from fastapi import APIRouter, status
from pydantic import BaseModel
from app.directus_client import get_one, get_all, post, update, delete
from app.logging import configure_logging
logger = configure_logging("wopr-api")

T = TypeVar('T', bound=BaseModel)
TCreate = TypeVar('TCreate', bound=BaseModel)
TUpdate = TypeVar('TUpdate', bound=BaseModel)


class CRUDRouter(Generic[T, TCreate, TUpdate]):

    def __init__(
        self,
        table_name: str,
        response_model: any,
        create_model: any,
        update_model: any,
        prefix: str,
        tags: list[str],
    ):
        self.table = table_name
        self.router = APIRouter(prefix=prefix, tags=tags)
        self._register_routes(response_model, create_model, update_model)

    def _register_routes(self, response_model, create_model, update_model):

        @self.router.get("", response_model=None)
        async def get_all_items():
            logger.info(f"Fetching all {self.table}")
            return get_all(self.table)

        @self.router.get("/{item_id}", response_model=any)
        async def get_item(item_id: str):
            logger.info(f"Fetching {self.table}: {item_id}")
            return get_one(self.table, item_id)

        @self.router.post("", response_model=any, status_code=status.HTTP_201_CREATED)
        async def create_item(payload: create_model):
            logger.info(f"Creating {self.table}: {payload.model_dump()}")
            return post(self.table, payload.model_dump())

        @self.router.patch("/{item_id}", response_model=response_model)
        async def update_item(item_id: str, payload: update_model):
            logger.info(f"Updating {self.table} {item_id}")
            return update(self.table, item_id, payload.model_dump(mode='json', exclude_unset=True))

        @self.router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_item(item_id: str):
            logger.info(f"Deleting {self.table}: {item_id}")
            return delete(self.table, item_id)

    def add_custom_route(
        self,
        path: str,
        methods: list[str],
        handler: Callable,
        **kwargs
    ):
        """Add custom routes beyond CRUD"""
        self.router.add_api_route(path, handler, methods=methods, **kwargs)
