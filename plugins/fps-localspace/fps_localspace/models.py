from typing import Dict, List

from pydantic import BaseModel


class Environment(BaseModel):
    packages: List[str]


class Environments(BaseModel):
    environments: Dict[str, Environment] = {}


class Server(BaseModel):
    id: str
    url: str


class Servers(BaseModel):
    servers: Dict[str, Server] = {}


class Projects(Environments, Servers):
    pass
