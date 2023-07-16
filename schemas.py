from typing import Union
from datetime import datetime
from pydantic import BaseModel


class user(BaseModel):
    name: str
    hashed_password: str
    is_active: bool
    class Config:
        orm_mode = True

class agents(BaseModel):
    id: int
    name: str
    token: str
    zalo_name: str
    zalo_number_target: str
    webhook_id: int

    class Config:
        orm_mode = True

class webhooks(BaseModel):
    url_webhooks: str
    webhooks_name: str
    created_at: datetime
    ended_at: datetime

class loggers(BaseModel):
    IP: str
    user_agents: str
    device: str
    IP_info: str
    filename: str
    token: str
    timestamp: datetime
    created_at: datetime
    class Config:
        orm_mode = True

class logger_error(BaseModel):
    IP: str
    user_agents: str
    device: str
    IP_info: str
    filename: Union[str, None] = None
    token: Union[str, None] = None
    timestamp: datetime
    created_at: datetime
    class Config:
        orm_mode = True




