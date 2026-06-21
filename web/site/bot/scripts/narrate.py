"""Генерация научного нарратива по сюжету POI через OpenRouter."""
from __future__ import annotations

import json
from pathlib import Path

from openai import OpenAI


REQUIRED_NARRATIVE_KEYS = {
    "title_intriguing",
    "title_scientific",
    "L1",
    "L2",
    "L3",
    "narration_short",
}


def build_user_prompt(poi: dict, route_context: dict | None = None) -> str:
    """Формирует юзерское сообщение модели по сюжету POI."""
    route_hint = ""
    if route_context and route_context.get("next_poi"):
        route_hint = (
            f"\n\nКонтекст маршрута: следующая точка по треку — "
            f"'{route_context['next_poi']}' "
            f"(~{route_context.get('next_distance_m', '?')} м). "
            f"В конце narration_short мостик к ней — одно предложение."
        )
    return (
        f"# Точка маршрута\n"
        f"**ID:** {poi['id']}\n"
        f"**Название:** {poi['name']}\n"
        f"**Координаты:** {poi['lat']:.6f}, {poi['lon']:.6f}\n"
        f"**Теги:** {', '.join(poi.get('tags', []))}\n\n"
        f"# Тема\n{poi['topic']}\n\n"
        f"# Заготовка сюжета (вход от куратора)\n{poi['scenario_brief']}\n\n"
        f"# Затравки уровней\n"
        f"- L1: {poi.get('level1_seed', '—')}\n"
        f"- L2: {poi.get('level2_seed', '—')}\n"
        f"- Физический интерактив: {poi.get('physical_interactive', '—')}\n"
        f"- Источники: {', '.join(poi.get('sources', [])) or '—'}\n"
        f"{route_hint}\n\n"
        f"Сгенерируй полный сценарий в формате JSON согласно system prompt. "
        f"Только JSON, без markdown-ограждения."
    )


class Narrator:
    def __init__(
        self,
        api_key: str,
        model: str = "openrouter/free",
        style_file: str | Path = "config/style.md",
        max_tokens: int = 2000,
        temperature: float = 0.4,
        base_url: str = "https://openrouter.ai/api/v1",
        fallback_models: list[str] | None = None,
        app_title: str = "Innopolis Science Trail",
        site_url: str | None = None,
        timeout_seconds: float = 25,
    ):
        headers = {"X-OpenRouter-Title": app_title}
        if site_url:
            headers["HTTP-Referer"] = site_url
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers=headers,
            timeout=timeout_seconds,
        )
        self.model = model
        self.fallback_models = fallback_models or ["openrouter/free"]
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.system = Path(style_file).read_text(encoding="utf-8")

    def _models(self) -> list[str]:
        return [self.model, *[m for m in self.fallback_models if m != self.model]]

    def _complete(
        self,
        model: str,
        user_prompt: str,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> str:
        kwargs = {}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": self.system},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens or self.max_tokens,
            temperature=self.temperature,
            **kwargs,
        )
        content = response.choices[0].message.content or ""
        return content.strip()

    def _chat(self, user_prompt: str, max_tokens: int | None = None) -> str:
        last_error = None
        for model in self._models():
            try:
                return self._complete(model, user_prompt, max_tokens=max_tokens)
            except Exception as exc:
                last_error = exc
        raise RuntimeError(f"OpenRouter generation failed: {last_error}") from last_error

    @staticmethod
    def _parse_json(text: str) -> dict:
        text = text.strip()
        if text.startswith("```"):
            text = text.strip("`")
            text = text.split("\n", 1)[1] if "\n" in text else text
            text = text.rsplit("```", 1)[0]
        if not text.startswith("{"):
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end > start:
                text = text[start : end + 1]
        return json.loads(text)

    def narrate(self, poi: dict, route_context: dict | None = None) -> dict:
        prompt = build_user_prompt(poi, route_context)
        errors = []
        for model in self._models():
            for json_mode in (True, False):
                try:
                    text = self._complete(model, prompt, json_mode=json_mode)
                    narrative = self._parse_json(text)
                    missing = REQUIRED_NARRATIVE_KEYS - set(narrative)
                    if missing:
                        raise ValueError(f"missing keys: {sorted(missing)}")
                    return narrative
                except Exception as exc:
                    errors.append(f"{model}: {exc}")
        raise RuntimeError("; ".join(errors[-4:]))

    def answer_question(
        self,
        poi: dict,
        question: str,
        route_context: dict | None = None,
    ) -> str:
        """Отвечает на голосовой вопрос посетителя вокруг ближайшей POI."""
        prompt = (
            f"# Точка маршрута\n"
            f"**ID:** {poi['id']}\n"
            f"**Название:** {poi['name']}\n"
            f"**Тема:** {poi['topic']}\n\n"
            f"# Заготовка сюжета\n{poi['scenario_brief']}\n\n"
            f"# Вопрос посетителя\n{question}\n\n"
            f"Ответь на русском как научный гид у этой точки. 4-7 коротких предложений, "
            f"без markdown, без LaTeX в голосовой части. Если вопрос выходит за рамки "
            f"сюжета, аккуратно верни его к наблюдаемому объекту."
        )
        if route_context and route_context.get("next_poi"):
            prompt += (
                f"\nСледующая точка маршрута: {route_context['next_poi']} "
                f"(примерно {route_context.get('next_distance_m', '?')} м)."
            )
        return self._chat(prompt, max_tokens=900)
