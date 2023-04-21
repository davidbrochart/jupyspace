import asyncio
import atexit
import os
from pathlib import Path
from typing import Dict

from jupyspace_api.app import App
from jupyspace_api.space import Space

from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine, select

from jupyspace_api.space.models import Environment, EnvironmentCreate, Server
from .micromamba import micromamba
from .subprocess import run_exec
from .utils import get_open_port


engine = create_engine("sqlite:///jupyspace.db", connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

PROCESSES: Dict[int, asyncio.subprocess.Process] = {}

def kill_servers():
    for p in PROCESSES.values():
        p.kill()

atexit.register(kill_servers)


class _Space(Space):
    def __init__(
        self,
        app: App,
    ) -> None:
        super().__init__(app)

    async def get_environments(self):
        with Session(engine) as session:
            environments = session.exec(select(Environment)).all()
            return environments

    async def get_environment(self, name: str):
        with Session(engine) as session:
            statement = select(Environment).where(Environment.name == name)
            results = session.exec(statement)
            environment = results.first()
            if not environment:
                raise HTTPException(status_code=404, detail="Environment not found")

            return environment

    async def create_environment(self, environment: EnvironmentCreate):
        with Session(engine) as session:
            environments = session.exec(select(Environment)).all()
            if environment.name in [e.name for e in environments]:
                raise HTTPException(status_code=409, detail="Environment already exists")

            packages = f"jupyverse fps-noauth fps-jupyterlab {environment.requirements}"
            await micromamba.create(channel="conda-forge", name=environment.name, packages=packages)
            path = (await micromamba.env_list())[environment.name]
            packages = await micromamba.list(environment.name)
            package_list = [f"{pkg_name}={pkg_version}" for pkg_name, pkg_version in packages.items()]
            installed = " ".join(package_list)
            environment.path = path
            environment.installed = installed
            db_environment = Environment.from_orm(environment)
            session.add(db_environment)
            session.commit()
            session.refresh(db_environment)
            return db_environment

    async def delete_environment(self, env_id: int):
        with Session(engine) as session:
            environment = session.get(Environment, env_id)
            if not environment:
                raise HTTPException(status_code=404, detail="Environment not found")

            statement = select(Server).where(Server.env_name == environment.name)
            results = session.exec(statement)
            server = results.first()
            if server:
                raise HTTPException(status_code=409, detail="A server is using the environment")

            await micromamba.remove(environment.name)
            session.delete(environment)
            session.commit()

    async def get_servers(self):
        with Session(engine) as session:
            servers = session.exec(select(Server)).all()
            return servers

    async def create_server(self, env_name: str, cwd: str):
        with Session(engine) as session:
            statement = select(Environment).where(Environment.name == env_name)
            results = session.exec(statement)
            environment = results.one()
            if not environment:
                raise HTTPException(status_code=404, detail="Environment not found")

            statement = select(Server).where(Server.env_name == env_name)
            results = session.exec(statement)
            if not Path(cwd).is_dir():
                raise HTTPException(status_code=404, detail="Directory doesn't exist")

            if cwd in [server.cwd for server in results]:
                raise HTTPException(status_code=409, detail="A server already runs in this environment in the same working directory")

            packages = await micromamba.list(environment.name)
            if "jupyverse" not in packages:
                raise HTTPException(status_code=404, detail="Jupyverse not found in environment")

            port = get_open_port()
            url = f"http://127.0.0.1:{port}"
            if os.name == "nt":
                jupyverse = Path(environment.path) / "Scripts" / "jupyverse.exe"
            else:
                jupyverse = Path(environment.path) / "bin" / "jupyverse"
            cwd_keep = os.getcwd()
            os.chdir(cwd)
            process = await run_exec(
                jupyverse,
                f"--port={port}",
                wait=False,
            )
            os.chdir(cwd_keep)
            while True:
                data = await process.stderr.readline()
                line = data.decode('ascii')
                if "Started server process" in line:
                    break
                
            server = Server(env_name=env_name, cwd=cwd, url=url)
            db_server = Server.from_orm(server)
            session.add(db_server)
            session.commit()
            session.refresh(db_server)
            PROCESSES[db_server.id] = process

        return db_server

    async def get_server(self, server_id: int):
        with Session(engine) as session:
            server = session.get(Server, server_id)
            if not server:
                raise HTTPException(status_code=404, detail="Server not found")

            return server

    async def stop_server(self, server_id: int):
        with Session(engine) as session:
            server = session.get(Server, server_id)
            if not server:
                raise HTTPException(status_code=404, detail="Server not found")

            await self._stop_server(server.id)
            session.delete(server)
            session.commit()


    async def _stop_server(self, server_id: int):
        if server_id not in PROCESSES:
            return

        process = PROCESSES[server_id]
        process.kill()
        if os.name != "nt":  # FIXME
            await process.wait()

        del PROCESSES[server_id]
