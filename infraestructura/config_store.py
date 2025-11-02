import os
import time
import json
from typing import Any, Optional

try:
    import consul
except Exception:
    consul = None

DEFAULT_CONSUL_HOST = os.getenv("CONSUL_HOST", "consul")
DEFAULT_CONSUL_PORT = int(os.getenv("CONSUL_PORT", "8500"))


class ConfigStore:
    """Simple configuration store wrapper.

    Priority: environment variables > Consul KV (if available) > default
    Provides lightweight caching and type casting helpers.
    """

    def __init__(self, ttl: int = 5):
        self.ttl = ttl
        self._cache = {}
        self._last = {}
        self.consul = None
        if consul is not None:
            try:
                # python-consul library expects host/port
                self.consul = consul.Consul(host=DEFAULT_CONSUL_HOST, port=DEFAULT_CONSUL_PORT)
            except Exception:
                self.consul = None

    def _from_env(self, key: str) -> Optional[str]:
        return os.getenv(key)

    def _from_consul(self, key: str) -> Optional[str]:
        if not self.consul:
            return None
        try:
            index, data = self.consul.kv.get(key)
            if data and data.get("Value") is not None:
                return data["Value"].decode("utf-8")
        except Exception:
            return None
        return None

    def _cast(self, value: Any, as_type: type):
        if value is None:
            return None
        if as_type is bool:
            return str(value).lower() in ("1", "true", "yes", "on")
        if as_type is int:
            return int(value)
        if as_type is float:
            return float(value)
        if as_type is dict:
            if isinstance(value, str):
                return json.loads(value)
            return value
        return value

    def get(self, key: str, default: Any = None, as_type: type = str, use_cache: bool = True) -> Any:
        # 1) env override
        v = self._from_env(key)
        if v is not None:
            return self._cast(v, as_type)

        # 2) cache
        now = time.time()
        if use_cache and key in self._cache and now - self._last.get(key, 0) < self.ttl:
            return self._cache[key]

        # 3) consul
        v = None
        if self.consul:
            try:
                v = self._from_consul(key)
            except Exception:
                v = None

        # 4) fallback
        if v is None:
            v = default

        v_cast = self._cast(v, as_type) if as_type is not None else v
        self._cache[key] = v_cast
        self._last[key] = now
        return v_cast


# global instance for convenience
cfg = ConfigStore()
