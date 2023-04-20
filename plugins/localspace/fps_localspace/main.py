import logging

from asphalt.core import Component, Context
from jupyspace_api.app import App
from jupyspace_api.space import Space
from jupyspace_api.space.models import Environment
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
        # discover existing environments
        with Session(engine) as session:
            for env_name, env_path in (await micromamba.env_list()).items():
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
