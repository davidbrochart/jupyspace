import asyncio
import os
import time
from typing import Dict

from fastapi import APIRouter, HTTPException, Request
from fps.hooks import register_router

from .models import Environment, Server, Projects
from .subprocess import run_exec
from .utils import get_open_port

PROJECTS = Projects()
PROCESSES: Dict[str, asyncio.subprocess.Process] = {}

router = APIRouter()


@router.get("/api/environments")
async def get_environments():
    print(f"{PROJECTS=}")
    return PROJECTS.environments


@router.post(
    "/api/environments/{name}",
    status_code=201,
)
async def create_environment(
    name,
    environment: Environment,
):
    if name in PROJECTS.environments:
        raise HTTPException(
            status_code=409, detail=f"Environment already exists: {name}"
        )

    await run_exec("mamba", "create", "-n", name)
    packages = (
        "jupyverse",
        "httpcore>0.13.3",
        "httpx-oauth<0.8",
        "fps-auth",
        "fps-jupyterlab",
        *environment.packages,
    )
    await run_exec("mamba", "install", "-y", *packages, "-n", name)
    PROJECTS.environments[name] = environment


@router.delete(
    "/api/environments/{name}",
    status_code=200,
)
async def delete_environment(name):
    await run_exec("mamba", "env", "remove", "-n", name)

    if name not in PROJECTS.environments:
        raise HTTPException(status_code=404, detail=f"Environment not found: {name}")

    del PROJECTS.environments[name]


@router.get("/api/servers")
async def get_servers():
    return PROJECTS.servers


@router.post(
    "/api/servers/{name}",
    status_code=201,
)
async def create_server(name):
    if name not in PROJECTS.environments:
        raise HTTPException(status_code=404, detail=f"Environment not found: {name}")
    if name in PROJECTS.servers:
        raise HTTPException(
            status_code=409, detail=f"Server already exists for environment: {name}"
        )

    port = get_open_port()
    home = os.path.expanduser("~")
    process = await run_exec(
        f"{home}/mambaforge/envs/{name}/bin/jupyverse",
        "--no-open-browser",
        "--auth.mode=noauth",
        f"--port={port}",
        wait=False,
    )
    pid = str(process.pid)
    PROCESSES[pid] = process
    PROJECTS.servers[name] = Server(
        id=pid,
        url=f"http://localhost:{port}",
    )
    time.sleep(2)


@router.get("/api/servers/{name}")
async def get_server(name):
    if name not in PROJECTS.servers:
        raise HTTPException(status_code=404, detail=f"Server not found: {name}")

    return PROJECTS.servers[name]


@router.delete(
    "/api/servers/{name}",
    status_code=200,
)
async def stop_server(name):
    if name not in PROJECTS.servers:
        raise HTTPException(
            status_code=404, detail=f"Server not found for environment: {name}"
        )

    process = PROCESSES[PROJECTS.servers[name].id]
    process.kill()
    await process.wait()
    del PROJECTS.servers[name]


r = register_router(router)
