"""LLM-провайдеры site-бота: GigaChat (основной) и OpenRouter/DeepSeek (fallback).

Оба провайдера говорят в OpenAI-совместимом формате chat/completions.
generate() пробует провайдеров по порядку; первый успешный — ответ.
"""
from __future__ import annotations

import os
import time
import uuid

import requests
import urllib3

# GigaChat использует Русский доверенный корневой CA. Если он не установлен в системе,
# проверку TLS отключаем (verify=False) — это server-to-server вызов к известному эндпоинту Сбера.
# В проде лучше задать GIGACHAT_CA = путь к russian_trusted_root_ca.cer и включить проверку.
_GIGA_CA = os.environ.get("GIGACHAT_CA")  # путь к CA-бандлу или пусто
if not _GIGA_CA:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ProviderError(Exception):
    pass


class GigaChatProvider:
    name = "gigachat"

    def __init__(
        self,
        auth_key: str,
        scope: str = "GIGACHAT_API_CORP",
        model: str = "GigaChat-2-Max",
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
        self._token: str | None = None
        self._exp_ms: int = 0  # время истечения токена (ms epoch)

    @property
    def _verify(self):
        return _GIGA_CA if _GIGA_CA else False

    def _ensure_token(self) -> str:
        # обновляем заранее, за 60 с до истечения
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

    def chat(self, messages: list[dict], max_tokens: int = 700, temperature: float = 0.4) -> str:
        token = self._ensure_token()
        r = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=self.timeout,
            verify=self._verify,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()


class OpenRouterProvider:
    name = "openrouter"

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek/deepseek-chat",
        base_url: str = "https://openrouter.ai/api/v1",
        app_title: str = "Tropa site-bar",
        site_url: str = "https://tropa.fmin.xyz",
        timeout: float = 30.0,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.app_title = app_title
        self.site_url = site_url
        self.timeout = timeout

    def chat(self, messages: list[dict], max_tokens: int = 700, temperature: float = 0.4) -> str:
        r = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-Title": self.app_title,
                "HTTP-Referer": self.site_url,
            },
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()


def build_providers() -> list:
    """Собирает список провайдеров по приоритету из переменных окружения."""
    provs = []
    # Урок длиннее чата — GigaChat может отвечать 30–50с; даём запас (env, дефолт 60с).
    timeout = float(os.environ.get("LLM_TIMEOUT", "60"))
    auth = os.environ.get("GIGACHAT_AUTH_KEY")
    if auth:
        provs.append(GigaChatProvider(
            auth_key=auth,
            scope=os.environ.get("GIGACHAT_SCOPE", "GIGACHAT_API_CORP"),
            model=os.environ.get("GIGACHAT_MODEL", "GigaChat-2-Max"),
            timeout=timeout,
        ))
    ork = os.environ.get("OPENROUTER_API_KEY")
    if ork:
        provs.append(OpenRouterProvider(
            api_key=ork,
            model=os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-chat"),
            timeout=timeout,
        ))
    if not provs:
        raise RuntimeError("Нет ни одного провайдера: задайте GIGACHAT_AUTH_KEY и/или OPENROUTER_API_KEY")
    return provs


def generate(messages: list[dict], providers: list, max_tokens: int = 700, temperature: float = 0.4):
    """Пробует провайдеров по порядку. Возвращает (текст, имя_провайдера)."""
    errors = []
    for p in providers:
        try:
            text = p.chat(messages, max_tokens=max_tokens, temperature=temperature)
            if text:
                return text, p.name
            errors.append(f"{p.name}: пустой ответ")
        except Exception as exc:  # таймаут, сетевая ошибка, 4xx/5xx — идём к следующему
            errors.append(f"{p.name}: {exc}")
    raise ProviderError("; ".join(errors[-3:]))
