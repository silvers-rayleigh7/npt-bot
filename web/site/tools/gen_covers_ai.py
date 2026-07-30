#!/usr/bin/env python3
"""Заставки сюжетов через генерацию (Nano Banana 2 на OpenRouter).

Стиль выбран сравнением пяти проб на одном сюжете: ризография без рамки.
Решающим оказалось то, что она показывает САМО ЯВЛЕНИЕ — у маятника рисуется
дуга качания, а не просто качели на дереве. Для научно-популярного проекта
это суть: заставка должна намекать, что здесь есть что понять.

Плюс ограниченная палитра держит 42 кадра одной серией, а печать «прямо на
бумаге» убирает белый прямоугольник, из-за которого всё и переделывалось.

Запуск: python3 tools/gen_covers_ai.py [--only slug] [--dry]
"""
import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site", "assets", "icons")
MODEL = "google/gemini-3.1-flash-image"

# Общая часть стиля — одинаковая у всех, именно она даёт единство серии.
STYLE = (
    "Risograph-style illustration printed directly on warm cream paper (#FBF8F1). "
    "NO frame, NO border, NO rectangular panel: the artwork bleeds softly into the paper "
    "with irregular edges and plenty of empty paper around the subject. "
    "Limited ink palette only: deep slate (#22333C), sky blue (#2E9BD6), moss green (#4EA75D), "
    "terracotta (#E9863B), warm yellow (#F6BB2E). Visible paper grain, slight ink "
    "misregistration, flat confident shapes, no photorealism. "
    "Wide horizontal composition, generous negative space, calm and clear. "
    "No text, no letters, no words, no numbers, no labels, no watermark, no signature."
)

# Сюжет → сцена и, главное, ЯВЛЕНИЕ, которое должно быть видно в кадре.
SCENES = {
    "almazy": "a single large cut diamond and a graphite pencil tip side by side, the same carbon "
              "atoms drawn as two contrasting lattices — flat sliding sheets versus a rigid 3D cage",
    "batagay": "a huge thawing crater in tundra with exposed permafrost walls, its edges visibly "
               "retreating outward, arrows of collapse widening the pit year by year",
    "belaya-bereza": "a white birch trunk close up beside a dark oak trunk, sunlight bouncing off "
                     "the birch's bright bark while the oak absorbs it",
    "belyaev": "a wild fox and a tame fox facing each other, the tame one with floppy ears, curled "
               "tail and patchy coat, a row of generations between them",
    "bessel": "the Earth at two opposite points of its orbit, two sight lines to one star forming "
              "a narrow triangle, the tiny parallax angle marked at the apex",
    "dendrohronologiya": "a cross-section of a tree trunk with tree rings of clearly different "
                         "widths, wide wet years and thin dry ones forming a readable record",
    "dvizhushaya-dyuna": "a crescent sand dune with a gentle windward slope and steep slip face, "
                         "wind arrows carrying sand grains over the crest, the whole dune shifted "
                         "forward as a ghost outline",
    "fraktalnaya-ramka": "a branching gully system where a small ravine and a huge valley have the "
                         "same shape, nested outlines showing scale-independence",
    "geo-srez": "a steep road cut exposing thick horizontal rock layers, oldest at the bottom, "
                "each band a different ink, time reading upward",
    "kant-sistema": "a flat rotating disc of dust and gas around a forming star, clumps gathering "
                    "along the ring into young planets",
    "kantorovich": "several factory-like nodes and limited supply lines between them, the optimal "
                   "route highlighted among possible ones",
    "kazhetsya-ponimaet": "a person talking to a simple machine terminal, a speech bubble from the "
                          "human mirrored back by the machine as an empty echo of the same shape",
    "klimat-yakutii": "two places at the same latitude — one warmed by a wide ocean current, the "
                      "other deep inland and frozen, a giant thermometer split between the two",
    "kraevedenie": "an old village seen in three overlapping layers of its past, the earliest layer "
                   "faded almost to nothing",
    "kvadrat-zhizni": "a square frame laid on meadow ground, inside it grass, insects, soil and "
                      "stones — the boundary between living and non-living inside one plot",
    "lavrentyev": "a metal plate deforming under an explosive impulse, the solid metal shown "
                  "flowing like a thick liquid in ordered streamlines",
    "lenskie-stolby": "a wall of tall narrow limestone pillars above a wide river, vertical frost "
                      "cracks splitting the rock into a stone palisade",
    "mamonty": "a mammoth preserved whole inside permafrost ice, the frozen ground drawn as a "
               "protective transparent block around it",
    "mayatniki": "an old wide oak with a wooden swing on long ropes, a dotted arc showing the "
                 "pendulum path, and a second shorter swing swinging faster nearby",
    "mikrobiom": "a bowl of traditional food connected by fine lines to a community of gut "
                 "microbes, different diets producing different microbe populations",
    "minkovsky": "a light cone in spacetime: two axes, a widening cone of possible futures and a "
                 "mirrored cone of the past",
    "most-leonardo": "a self-supporting arched footbridge of straight interlocking logs with no "
                     "nails, the interlocking pattern clearly visible",
    "mys-taran": "a coastal cliff being undercut by waves, the overhang about to collapse, the "
                 "retreating shoreline marked behind it",
    "obratnye-zadachi": "waves sent into the ground from the surface, returning echoes drawing the "
                        "hidden buried shape that was never seen directly",
    "observatoriya": "a small hillside observatory dome open to a night sky, a sight line from the "
                     "dome to the pole star with the latitude angle marked",
    "russkie-isklyucheniya": "a family tree of words where the most used words keep their old "
                             "irregular form while rare ones drift into a regular pattern",
    "sem-mostov": "a river city with two islands and seven bridges, reduced beside it to a graph "
                  "of four nodes and seven edges",
    "seysmograf-viherta": "a heavy suspended mass staying still while the ground shakes beneath, "
                          "a pen tracing the tremor onto a rotating drum",
    "skrytaya-matematika": "three animals of very different size drawn to the same height, their "
                           "limb thickness scaling non-linearly with body mass",
    "sobolev": "a smooth curve meeting a sharp corner, the corner point circled where classical "
               "derivatives fail and a generalised solution takes over",
    "solnechnaya-sistema": "the Sun and a light cone spreading outward, the same beam covering four "
                           "times the area at twice the distance",
    "solnechnye-chasy": "a sundial gnomon casting a long shadow across an hour scale, the shadow "
                        "sweeping through the day",
    "sputnik": "a receiver on the ground with distance spheres from four satellites intersecting "
               "at a single point",
    "staryj-les": "an old-growth forest with fallen decaying trunks, layered undergrowth and hollow "
                  "veteran trees beside a young even-aged plantation of identical thin trees",
    "tancuyushiy-les": "pine trunks bent into loops and spirals in a coastal forest, each trunk "
                       "curving before straightening upward again",
    "terrasy-vremeni": "a river valley with several stepped terraces at different heights, each "
                       "step an older level of the same river",
    "uslysh-rasstoyanie": "a person clapping near a distant cliff, the sound travelling out and "
                          "echoing back, the delay drawn as a measured path",
    "valun-termometr": "a large boulder in a meadow, one side sunlit and warm, the other in cool "
                       "shade, heat slowly seeping through the stone",
    "vhod": "a trail head in a meadow with a simple signpost and a dotted path leading past several "
            "numbered stops into the distance",
    "vishtynec": "a deep clear glacial lake in forest, its layered water column shown in a cutaway "
                 "with a cold dense bottom layer",
    "vodorazdel": "a ridge where rain splits into two streams flowing to opposite sides, the divide "
                  "line running along the crest",
    "yantar": "amber lumps on a beach with an insect trapped inside one, resin flowing down an "
              "ancient pine and hardening over millions of years",
}


def key():
    for line in open(os.path.expanduser("~/.kwork.env"), encoding="utf-8"):
        m = re.match(r'\s*(?:export\s+)?OPENROUTER_API_KEY\s*=\s*"?([^"\s]+)"?', line)
        if m and m.group(1):
            return m.group(1)
    sys.exit("нет OPENROUTER_API_KEY в ~/.kwork.env")


def generate(slug, scene, api):
    prompt = f"{STYLE} Subject: {scene}."
    body = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": prompt}],
                       "modalities": ["image", "text"]}).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {api}", "Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=240))
    img = d["choices"][0]["message"]["images"][0]["image_url"]["url"]
    head, b64 = img.split(",", 1)
    ext = "jpg" if "jpeg" in head else "png"       # MIME у моделей разный
    path = os.path.join(OUT, f"{slug}.{ext}")
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64))
    return path, (d.get("usage") or {}).get("cost", 0) or 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--dry", action="store_true", help="показать промпты, ничего не генерировать")
    args = ap.parse_args()

    items = [(s, v) for s, v in SCENES.items() if not args.only or s == args.only]
    if args.dry:
        for s, v in items:
            print(f"— {s}: {v[:110]}")
        print(f"\nвсего: {len(items)}, ориентировочно {len(items) * 0.069:.2f} USD")
        return

    api, total, ok, fail = key(), 0.0, 0, []
    os.makedirs(OUT, exist_ok=True)
    for i, (slug, scene) in enumerate(items, 1):
        try:
            path, cost = generate(slug, scene, api)
            total += cost
            ok += 1
            print(f"[{i}/{len(items)}] {slug} → {os.path.basename(path)} ({cost:.4f})", flush=True)
        except Exception as e:
            fail.append(slug)
            print(f"[{i}/{len(items)}] {slug}: ОШИБКА {str(e)[:110]}", flush=True)
        time.sleep(1)          # не долбим API вплотную
    print(f"\nготово: {ok}, ошибок: {len(fail)}, потрачено {total:.2f} USD")
    if fail:
        print("не собрались:", ", ".join(fail))


if __name__ == "__main__":
    main()
