#!/usr/bin/env python3
"""Сборка retrieval-индексов для урока.

storylines_index.json — эмбеддинги наших сюжетов (для StorylineRetriever).
Запуск офлайн (здесь, с ключом GigaChat), результат коммитится и едет на сервер,
чтобы бэкенд не считал эмбеддинги 42 сюжетов на старте.

Использование:  python3 build_indexes.py
"""
import json
import os
import re
import sys

import yaml
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")
SERVER = os.path.join(ROOT, "site-bar", "server")
load_dotenv(os.path.join(SERVER, ".env"))

sys.path.insert(0, SERVER)
from retrieval.embeddings import EmbeddingsClient  # noqa: E402

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)


def load_storylines():
    d = os.path.join(CONTENT, "storylines")
    items = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md"):
            continue
        raw = open(os.path.join(d, fn), encoding="utf-8").read()
        m = FM_RE.match(raw)
        if not m:
            continue
        fm = yaml.safe_load(m.group(1)) or {}
        body = m.group(2)
        # первый значимый абзац после первого ## — как краткое описание
        parts = re.split(r"(?m)^##\s+.+?\s*$", body)
        summary = ""
        for p in parts[1:]:
            for para in p.strip().split("\n\n"):
                para = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", para)     # картинки ![...](...)
                para = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", para)  # ссылки [text](url) → text
                para = re.sub(r"\[\^[^\]]+\]", "", para)             # сноски
                para = re.sub(r"[*_`>#]", "", para).strip()          # markdown-разметка
                para = re.sub(r"\s+", " ", para)
                if len(para) > 40:
                    summary = para[:400]
                    break
            if summary:
                break
        items.append({
            "slug": fn[:-3],
            "title": fm.get("title", fn[:-3]),
            "topic": fm.get("topic", ""),
            "tags": fm.get("tags", []) or [],
            "region": fm.get("region") or "",
            "summary": summary,
        })
    return items


def main():
    auth = os.environ.get("GIGACHAT_AUTH_KEY")
    if not auth:
        print("Нет GIGACHAT_AUTH_KEY в site-bar/server/.env"); sys.exit(1)
    client = EmbeddingsClient(auth_key=auth, scope=os.environ.get("GIGACHAT_SCOPE", "GIGACHAT_API_CORP"))

    items = load_storylines()
    texts = [f"{it['title']}. {it['topic']}. {', '.join(it['tags'])}. {it['summary']}" for it in items]
    print(f"Сюжетов: {len(items)}; считаю эмбеддинги…")
    vectors = client.embed(texts)
    if len(vectors) != len(items):
        print(f"⚠️ эмбеддингов {len(vectors)} != сюжетов {len(items)}"); sys.exit(1)

    out = []
    for it, vec in zip(items, vectors):
        out.append({
            "slug": it["slug"], "title": it["title"], "topic": it["topic"],
            "tags": it["tags"], "region": it["region"], "summary": it["summary"],
            "url": f"/storylines/{it['slug']}/", "embedding": vec,
        })
    dst = os.path.join(SERVER, "data", "storylines_index.json")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    dim = len(out[0]["embedding"]) if out else 0
    print(f"✓ {dst}: {len(out)} записей, dim={dim}")


if __name__ == "__main__":
    main()
