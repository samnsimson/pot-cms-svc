from datetime import timedelta
from fastapi import Request
from redis import Redis
from typing import Any, Callable, Optional, TypedDict
from sqlmodel import SQLModel
import json


class CacheClient:
    def __init__(self, redis: Redis):
        self.redis = redis

    def set(self, key: str, value: Any, expire: Optional[timedelta] = timedelta(minutes=5)) -> None:
        if isinstance(value, (str, int, float, bool)): data = str(value)
        elif isinstance(value, (dict, list)): data = json.dumps(value)
        elif isinstance(value, SQLModel): data = json.dumps(value.model_dump())
        else: raise TypeError(f"Unsupported type for caching: {type(value)}")
        self.redis.setex(key, expire, data)

    def get(self, key: str) -> Any:
        data = self.redis.get(key)
        if data is None: return None
        try: return json.loads(data)
        except json.JSONDecodeError: return data


def get_redis(request: Request) -> CacheClient:
    redis: Redis = request.app.state.redis
    return CacheClient(redis)
