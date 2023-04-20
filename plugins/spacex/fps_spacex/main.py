import logging

from asphalt.core import Component, Context
from jupyspace_api.app import App
from jupyspace_api.space import Space
from jupyspace_api.spacex import Spacex

from .routes import _Spacex


logger = logging.getLogger("spacex")


class SpacexComponent(Component):

    async def start(
        self,
        ctx: Context,
    ) -> None:
        app = await ctx.request_resource(App)
        space = await ctx.request_resource(Space)

        spacex = _Spacex(app, space)
        ctx.add_resource(spacex, types=Spacex)
