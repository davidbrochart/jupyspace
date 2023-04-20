from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from fastapi import APIRouter

from .models import EnvironmentRead, EnvironmentCreate, ServerRead
from ..app import App
from ..router import Router


class Space(Router, ABC):

    def __init__(
        self,
        app: App,
    ) -> None:
        super().__init__(app)

        router = APIRouter()

        @router.get("/api/environments", response_model=List[EnvironmentRead])
        async def get_environments():
            return await self.get_environments()

        @router.get("/api/environments/{name}", response_model=EnvironmentRead)
        async def get_environment(name: str):
            return await self.get_environment(name)

        @router.post("/api/environments", response_model=EnvironmentRead, status_code=201)
        async def create_environment(environment: EnvironmentCreate):
            return await self.create_environment(environment)

        @router.delete("/api/environments/{env_id}")
        async def delete_environment(env_id: int):
            return await self.delete_environment(env_id)

        @router.get("/api/servers", response_model=List[ServerRead])
        async def get_servers():
            return await self.get_servers()

        @router.post("/api/servers/{env_name}/{cwd:path}", response_model=ServerRead, status_code=201)
        async def create_server(env_name, cwd):
            return await self.create_server(env_name, cwd)

        @router.get("/api/servers/{server_id}", response_model=ServerRead)
        async def get_server(server_id: int):
            return await self.get_server(server_id)

        @router.delete("/api/servers/{server_id}")
        async def stop_server(server_id: int):
            return await self.stop_server(server_id)

        self.include_router(router)

    @abstractmethod
    async def get_environments(self):
        ...

    @abstractmethod
    async def get_environment(self, name: str):
        ...

    @abstractmethod
    async def create_environment(self, environment: EnvironmentCreate):
        ...

    @abstractmethod
    async def delete_environment(self, env_id: int):
        ...

    @abstractmethod
    async def get_servers(self):
        ...

    @abstractmethod
    async def create_server(self, env_name: str):
        ...

    @abstractmethod
    async def get_server(self, server_id: int):
        ...

    @abstractmethod
    async def stop_server(self, server_id: int):
        ...
