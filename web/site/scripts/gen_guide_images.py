#!/usr/bin/env python3
"""Генерация ИИ-иллюстраций точек гида через Gemini 3.1 Flash Image (Nano Banana).

Читает content/guides/<slug>.yaml, для каждой точки шлёт промпт (объект + единый
стиль-префикс палитры Тропы) в Gemini generateContent (синхронно), декодирует
inlineData и сохраняет в site/assets/guides/<slug>/points/NN.jpg. Идемпотентно.
Резолвер в build.py подхватит .jpg вместо .png/.svg-плейсхолдера.

Опц. --map — образец художественной карты в site/assets/guides/<slug>/map-nano.jpg.
Ключ — GEMINI_API_KEY из ~/.kwork.env.
Использование:  python3 scripts/gen_guide_images.py zernova [--map] [--only N,M]
"""
import base64, json, os, re, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = "gemini-3.1-flash-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

STYLE = ("Hand-drawn watercolor and ink illustration, muted earthy palette "
         "(sand beige, sage green, olive, charcoal) on warm white background, "
         "soft delicate linework, literary storybook mood, no text, no labels, "
         "no people, not photorealistic. Subject: ")

SUBJECTS = {
    1:  "small vintage German-style railway station building with a clock tower",
    2:  "bronze sculpture of a frog princess with a crown on a stone in a park",
    3:  "old half-timbered 'Dune House', former seaside hotel among pines",
    4:  "elegant old villa, former treasurer's house, German resort architecture",
    5:  "miniature scale model of a medieval town with towers in a small square",
    6:  "quiet old resort street with linden trees and vintage lamp posts",
    7:  "ornate wooden burgomaster villa, hunting-house style with a turret",
    8:  "grand Kurhaus resort spa building with columns by the sea",
    9:  "winding stone serpentine staircase descending a wooded slope to the sea",
    10: "white sanatorium villa among tall trees",
    11: "tall brick water tower with a large sundial on its facade",
    12: "stylized snail sculpture in a park, slow-city symbol",
    13: "larch tree park with soft autumn light and a path",
    14: "graceful bronze sculpture of a woman carrying water",
    15: "central town square with an amber heart monument and flower beds",
    16: "small gothic chapel turned organ concert hall",
    17: "tiny whimsical fairytale gnome house among bushes",
    18: "modern seaside concert hall by the dunes",
    19: "landscaped resort park with sculptures and lawns",
    20: "wooden lift tower on high sea cliffs overlooking the Baltic Sea",
}


def gkey():
    for line in open(os.path.expanduser("~/.kwork.env"), encoding="utf-8"):
        m = re.match(r"\s*GEMINI_API_KEY\s*=\s*(\S+)", line)
        if m:
            return m.group(1)
    raise SystemExit("GEMINI_API_KEY не найден")


def gen(key, prompt, path):
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]})
    r = subprocess.run(["curl", "-s", "-m", "120", f"{URL}?key={key}",
        "-H", "Content-Type: application/json", "-d", body],
        capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except Exception:
        print("   bad json:", r.stdout[:140]); return False
    if "error" in d:
        print("   error:", str(d["error"])[:140]); return False
    for p in d.get("candidates", [{}])[0].get("content", {}).get("parts", []):
        if "inlineData" in p:
            open(path, "wb").write(base64.b64decode(p["inlineData"]["data"]))
            return os.path.getsize(path)
    return False


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    slug = sys.argv[1]
    key = gkey()
    only = None
    if "--only" in sys.argv:
        only = {int(x) for x in sys.argv[sys.argv.index("--only") + 1].split(",")}
    import yaml
    g = yaml.safe_load(open(os.path.join(ROOT, "content", "guides", f"{slug}.yaml"), encoding="utf-8"))
    pts = g["route"]["points"]
    out = os.path.join(ROOT, "site", "assets", "guides", slug, "points")
    os.makedirs(out, exist_ok=True)

    ok = 0
    for p in pts:
        n = p["n"]
        if only and n not in only:
            continue
        jpg = os.path.join(out, f"{n:02d}.jpg")
        if os.path.exists(jpg) and os.path.getsize(jpg) > 8000:
            print(f"  skip {n:02d} (есть)"); ok += 1; continue
        subj = SUBJECTS.get(n, p["title"])
        for attempt in (1, 2):
            sz = gen(key, STYLE + subj, jpg)
            if sz:
                print(f"  [OK] {n:02d}: {sz:,} b — {subj[:40]}")
                svg = os.path.join(out, f"{n:02d}.svg")
                if os.path.exists(svg):
                    os.remove(svg)  # убрать плейсхолдер
                ok += 1; break
            print(f"  retry {n:02d} ({attempt})"); time.sleep(2)
        time.sleep(1)

    if "--map" in sys.argv:
        mp = os.path.join(ROOT, "site", "assets", "guides", slug, "map-nano.jpg")
        sz = gen(key, STYLE + "illustrated top-down tourist map of a small Baltic seaside "
                 "resort town, one winding footpath from a railway station rising through "
                 "parks and old villas up to high sea cliffs, the Baltic sea along the top "
                 "edge, scattered tiny landmarks, soft aged-paper map look", mp)
        print(f"  [map] {'OK '+format(sz,',')+' b' if sz else 'FAIL'} -> map-nano.jpg")

    print(f"Готово: {ok} точек.")


if __name__ == "__main__":
    main()
