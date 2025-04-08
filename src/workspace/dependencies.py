from dataclasses import dataclass

import httpx

http_client = httpx.AsyncClient()


@dataclass
class AgentDeps:
    http_client: httpx.AsyncClient
