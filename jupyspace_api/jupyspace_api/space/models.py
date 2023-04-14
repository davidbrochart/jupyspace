from typing import List, Optional

from sqlmodel import Field, SQLModel


class ServerBase(SQLModel):
    env_name: str = Field(index=True)
    url: str = Field(index=True)
    cwd: str
    #environment: Optional[int] = Field(default=None, foreign_key="environment.id")


class Server(ServerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ServerCreate(ServerBase):
    pass


class ServerRead(ServerBase):
    id: int


class EnvironmentBase(SQLModel):
    name: str = Field(index=True)
    path: Optional[str] = None
    requirements: Optional[str] = None
    installed: Optional[str] = None


class Environment(EnvironmentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    path: Optional[str]


class EnvironmentCreate(EnvironmentBase):
    pass


class EnvironmentRead(EnvironmentBase):
    id: int
    path: str
