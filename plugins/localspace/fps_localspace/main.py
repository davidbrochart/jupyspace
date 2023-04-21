import logging

import httpx
from asphalt.core import Component, Context
from jupyspace_api.app import App
from jupyspace_api.space import Space
from jupyspace_api.space.models import Environment, Server
from sqlmodel import Session, select

from .micromamba import micromamba
from .routes import _Space, create_db_and_tables, engine


logger = logging.getLogger("space")


class LocalspaceComponent(Component):

    async def start(
        self,
        ctx: Context,
    ) -> None:
        app = await ctx.request_resource(App)

        space = _Space(app)
        ctx.add_resource(space, types=Space)

        create_db_and_tables()
        with Session(engine) as session:
            existing_envs = await micromamba.env_list()
            env_names = list(existing_envs.keys())
            environments = session.exec(select(Environment)).all()
            for env in environments:
                if env.name not in env_names:
                    logger.info("Environment cannot be found: %s", env.name)
                    session.delete(env)

            # discover existing environments
            for env_name, env_path in existing_envs.items():
                logger.info("Found environment: %s", env_name)
                statement = select(Environment).where(Environment.name == env_name)
                environment = session.exec(statement).first()
                if not environment:
                    # environment not in database, add it
                    packages = await micromamba.list(env_name)
                    package_list = [f"{pkg_name}={pkg_version}" for pkg_name, pkg_version in packages.items()]
                    installed = " ".join(package_list)
                    environment = Environment(name=env_name, path=env_path, installed=installed)
                    session.add(environment)
                    session.commit()
                else:
                    # environment in database, check that installed packages match requirements?
                    # (because of out-of-band changes)
                    pass

            # check running servers
            servers = session.exec(select(Server)).all()
            for server in servers:
                async with httpx.AsyncClient() as http:
                    try:
                        await http.get(server.url)
                        logger.info("Found server: %s", server.url)
                    except httpx.ConnectError:
                        logger.info("Server unresponsive: %s", server.url)
                        session.delete(server)
            session.commit()
