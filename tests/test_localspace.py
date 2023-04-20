import tempfile

import pytest
from asphalt.core import Context
from jupyspace_api.main import JupyspaceComponent
from httpx import AsyncClient


ENV_NAME = "__test_env__"
temp_dir = tempfile.TemporaryDirectory()
ENV_CWD = temp_dir.name

COMPONENTS = {
    "app": {"type": "app"},
    "space": {"type": "space"},
}


@pytest.mark.asyncio
async def test_environment(unused_tcp_port):
    async with Context() as ctx, AsyncClient() as http:
        await JupyspaceComponent(
            components=COMPONENTS,
            port=unused_tcp_port,
        ).start(ctx)

        environment = dict(
            name=ENV_NAME,
            requirements="attrs",
        )
        response = await http.post(f"http://127.0.0.1:{unused_tcp_port}/api/environments", json=environment, timeout=300)
        assert response.status_code == 201

        response = await http.get(f"http://127.0.0.1:{unused_tcp_port}/api/environments/{ENV_NAME}")
        assert response.status_code == 200
        env = response.json()

        response = await http.delete(f"http://127.0.0.1:{unused_tcp_port}/api/environments/{env['id']}", timeout=60)
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_server(unused_tcp_port):
    async with Context() as ctx, AsyncClient() as http:
        await JupyspaceComponent(
            components=COMPONENTS,
            port=unused_tcp_port,
        ).start(ctx)

        environment = dict(
            name=ENV_NAME,
            requirements="attrs",
        )
        response = await http.post(f"http://127.0.0.1:{unused_tcp_port}/api/environments", json=environment, timeout=300)
        assert response.status_code == 201
        env = response.json()

        response = await http.post(f"http://127.0.0.1:{unused_tcp_port}/api/servers/{ENV_NAME}/{ENV_CWD}", timeout=60)
        assert response.status_code == 201
        server = response.json()

        response = await http.get(f"http://127.0.0.1:{unused_tcp_port}/api/servers/{server['id']}")
        assert response.status_code == 200
        server = response.json()
        assert server["env_name"] == ENV_NAME

        response = await http.get(f"{server['url']}/lab")
        assert response.status_code == 200
        assert "JupyterLab" in response.text

        response = await http.delete(f"http://127.0.0.1:{unused_tcp_port}/api/servers/{server['id']}")
        assert response.status_code == 200

        response = await http.get(f"http://127.0.0.1:{unused_tcp_port}/api/servers")
        assert response.status_code == 200
        servers = response.json()
        assert ENV_NAME not in [server["env_name"] for server in servers]

        response = await http.delete(f"http://127.0.0.1:{unused_tcp_port}/api/environments/{env['id']}", timeout=60)
        assert response.status_code == 200

        response = await http.get(f"http://127.0.0.1:{unused_tcp_port}/api/environments")
        assert response.status_code == 200
        environments = response.json()
        assert ENV_NAME not in [env["name"] for env in environments]
