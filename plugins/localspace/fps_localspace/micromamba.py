import asyncio
import os
import shutil
from typing import Dict, List, Tuple


if os.name == "nt":
    dash = "-"
else:
    dash = "─"


class Micromamba:

    def __init__(self) -> None:
        self._micromamba = shutil.which("micromamba")
        if self._micromamba is None:
            raise RuntimeError("Cannot find micromamba, please install it.")

    async def env_list(self) -> Dict[str, str]:
        stdout, stderr = await self._run("env", "list")
        get_env = False
        envs = {}
        for line in stdout.splitlines():
            line = line.decode().strip()
            if get_env:
                line_list = line.split()
                # there can be a "*" in the middle, for active environment
                name = line_list[0]
                path = line_list[-1]
                envs[name] = path
            elif line.startswith("base"):
                get_env = True
        return envs

    async def list(self, name: str) -> Dict[str, str]:
        stdout, stderr = await self._run("list", "-n", name)
        get_pkg = False
        pkgs = {}
        for line in stdout.splitlines():
            line = line.decode().strip()
            if get_pkg:
                name, version, build, channel = line.split()
                pkgs[name] = version
            elif line.startswith(dash * 10):
                get_pkg = True
        return pkgs

    async def create(self, channel, name, packages):
        package_list = packages.split()
        stdout, stderr = await self._run("create", "-c", channel, "-n", name, *package_list, "-y")

    async def remove(self, name):
        stdout, stderr = await self._run("env", "remove", "-n", name, "-y")

    async def _run(self, *cmd: Tuple[str]) -> Tuple[bytes, bytes]:
        proc = await asyncio.create_subprocess_exec(
            self._micromamba, *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return stdout, stderr


micromamba = Micromamba()
