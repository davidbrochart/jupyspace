from __future__ import annotations

from pathlib import Path
from typing import Optional
from typing_extensions import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jupyspace_api.app import App
from jupyspace_api.router import Router
from jupyspace_api.space import Space
from jupyspace_api.space.models import EnvironmentCreate


here = Path(__file__).parent.resolve()
templates = Jinja2Templates(directory=here / "templates")


class Spacex(Router):
    def __init__(
        self,
        app: App,
        space: Space,
    ) -> None:
        super().__init__(app)

        self.space = space
        self.mount("/static", StaticFiles(directory=here / "static"), name="static")

        router = APIRouter()

        @router.get("/", response_class=HTMLResponse)
        async def get_root(request: Request):
            environments = await self.space.get_environments()
            servers = await self.space.get_servers()
            context = {"request": request, "environments": environments, "servers": servers}
            return templates.TemplateResponse("index.html", context)

        @router.get("/environments/{name}", response_class=HTMLResponse)
        async def get_environment(request: Request, name: str):
            environment = await self.space.get_environment(name)
            context = {"request": request, "env": environment}
            res = templates.TemplateResponse("environment.html", context)
            return res

        @router.get("/environments", response_class=HTMLResponse)
        async def get_environments(request: Request):
            environments = await self.space.get_environments()
            servers = await self.space.get_servers()
            context = {"request": request, "environments": environments, "servers": servers}
            return templates.TemplateResponse("environments.html", context)

        @router.post("/search_environments", response_class=HTMLResponse)
        async def search_environments(request: Request, search: Optional[str] = Form(None)):
            environments = await self.space.get_environments()
            if search:
                environments = [env for env in environments if env.name.startswith(search)]
            else:
                environments = []
            context = {"request": request, "environments": environments}
            return templates.TemplateResponse("searched_environments.html", context)

        @router.get("/environment/edit", response_class=HTMLResponse)
        async def edit_environment(request: Request):
            context = {"request": request}
            return templates.TemplateResponse("edit_environment.html", context)

        @router.put("/environment", response_class=HTMLResponse)
        async def create_environment(request: Request, name: Annotated[str, Form()], packages: Annotated[str, Form()]):
            environment = EnvironmentCreate(
                name=name,
                requirements=packages,
            )
            await self.space.create_environment(environment)
            environments = await self.space.get_environments()
            servers = await self.space.get_servers()
            context = {"request": request, "environments": environments, "servers": servers}
            return templates.TemplateResponse("environments.html", context)

        @router.get("/environment/cancel", response_class=HTMLResponse)
        async def cancel_environment(request: Request):
            context = {"request": request}
            return templates.TemplateResponse("create_environment.html", context)

        @router.delete("/environments/{name}", response_class=HTMLResponse)
        async def delete_environment(request: Request, name: str):
            environment = await self.space.get_environment(name)
            await self.space.delete_environment(environment.id)

        @router.get("/servers/{env_name}/edit", response_class=HTMLResponse)
        async def edit_server(request: Request, env_name: str):
            context = {"request": request, "env_name": env_name}
            res = templates.TemplateResponse("edit_server.html", context)
            return res

        @router.put("/servers/{env_name}", response_class=HTMLResponse)
        async def create_server(request: Request, env_name: str, cwd: Annotated[str, Form()]):
            await self.space.create_server(env_name, cwd)
            environments = await self.space.get_environments()
            servers = await self.space.get_servers()
            context = {"request": request, "environments": environments, "servers": servers}
            return templates.TemplateResponse("environments.html", context)

        @router.delete("/servers/{env_name}/{cwd:path}", response_class=HTMLResponse)
        async def stop_server(request: Request, env_name: str, cwd: str):
            servers = await self.space.get_servers()
            servers = [server for server in servers if server.env_name == env_name and server.cwd == cwd]
            if servers:
                await self.space.stop_server(servers[0].id)
            environments = await self.space.get_environments()
            servers = await self.space.get_servers()
            context = {"request": request, "environments": environments, "servers": servers}
            return templates.TemplateResponse("environments.html", context)

        self.include_router(router)
