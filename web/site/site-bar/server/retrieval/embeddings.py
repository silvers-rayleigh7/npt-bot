"""Клиент эмбеддингов GigaChat (та же авторизация, что и chat) + косинус.

Используется офлайн (build_indexes.py) для индекса сюжетов и онлайн (StorylineRetriever)
для эмбеддинга запроса. При недоступности — бросает EmbeddingsError, ретривер ловит и
падает на keyword-фолбэк.
"""
from __future__ import annotations

import math
import os
import time
import uuid
from typing import List

import requests
import urllib3

_GIGA_CA = os.environ.get("GIGACHAT_CA")
if not _GIGA_CA:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class EmbeddingsError(Exception):
    pass


class EmbeddingsClient:
    def __init__(
        self,
        auth_key: str,
        scope: str = "GIGACHAT_API_CORP",
        model: str = "Embeddings",
        oauth_url: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
        base_url: str = "https://gigachat.devices.sberbank.ru/api/v1",
        timeout: float = 30.0,
    ):
        self.auth_key = auth_key
        self.scope = scope
        self.model = model
        self.oauth_url = oauth_url
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._token = None
        self._exp_ms = 0

    @property
    def _verify(self):
        return _GIGA_CA if _GIGA_CA else False

    def _ensure_token(self) -> str:
        if self._token and time.time() * 1000 < self._exp_ms - 60_000:
            return self._token
        r = requests.post(
            self.oauth_url,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "RqUID": str(uuid.uuid4()),
                "Authorization": f"Basic {self.auth_key}",
            },
            data={"scope": self.scope},
            timeout=self.timeout,
            verify=self._verify,
        )
        r.raise_for_status()
        d = r.json()
        self._token = d["access_token"]
        self._exp_ms = int(d.get("expires_at", time.time() * 1000 + 1_800_000))
        return self._token

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Вектора для списка текстов. Бросает EmbeddingsError при любой проблеме."""
        if not texts:
            return []
        try:
            token = self._ensure_token()
            r = requests.post(
                f"{self.base_url}/embeddings",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"model": self.model, "input": texts},
                timeout=self.timeout,
                verify=self._verify,
            )
            r.raise_for_status()
            data = r.json()["data"]
            # порядок сохраняется по index
            return [item["embedding"] for item in sorted(data, key=lambda x: x.get("index", 0))]
        except Exception as exc:
            raise EmbeddingsError(str(exc)) from exc


def cosine(a: List[float], b: List[float]) -> float:
    """Косинусная близость двух векторов. 0 при нулевой норме."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)
