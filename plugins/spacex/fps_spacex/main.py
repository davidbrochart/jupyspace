from asphalt.core import Component, Context
from jupyspace_api.app import App
from jupyspace_api.space import Space

from .routes import Spacex


class SpacexComponent(Component):

    async def start(
        self,
        ctx: Context,
    ) -> None:
        app = await ctx.request_resource(App)
        space = await ctx.request_resource(Space)

        spacex = Spacex(app, space)
        ctx.add_resource(spacex)
