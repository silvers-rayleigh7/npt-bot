#!/usr/bin/env python3
"""Гравюра-иконки сюжетов через Gemini 3.1 Flash Image, в стиле B&W line-art Даниила.
Сохраняет в site/assets/icons/<slug>.jpg (resolver в build.py подхватит). Идемпотентно.
Использование: python3 scripts/gen_storyline_icons.py [slug1 slug2 ...]  (без аргументов — все)
"""
import base64, io, json, os, re, subprocess, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = "gemini-3.1-flash-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
STYLE = ("Single isolated motif, centered, with generous empty space around it. Fine delicate "
         "black ink line drawing, antique botanical book-plate style, thin clean outlines, only "
         "light minimal shading. Plain solid pure white background, no paper texture, no vignette, "
         "no gradient, no ground, no scenery, no border, no frame, no color, no text. Subject: ")

SUBJECTS = {
    "sem-mostov": "a single elegant old stone arch bridge over a river",
    "yantar": "a single polished drop-shaped piece of amber with one tiny insect inside",
    "mys-taran": "a single large rounded glacial erratic boulder",
    "tancuyushiy-les": "a single pine tree whose trunk curves into a graceful loop or spiral",
    "vishtynec": "a calm lake with two slender reeds and one gentle ripple ring, minimal",
    "dvizhushaya-dyuna": "a single smooth crescent sand dune with a few blades of marram grass on its crest",
    "seysmograf-viherta": "a single antique mechanical seismograph with a pendulum mass on a spring and a recording drum",
    "kant-sistema": "a swirling flat spiral protoplanetary disk of gas and dust around a small central star",
    "bessel": "a single antique brass refractor telescope on a tripod",
    "minkovsky": "a double light cone: two slender cones meeting tip to tip, a few thin straight worldlines through the apex",
    "sobolev": "a single tall narrow spike (Dirac delta impulse) rising from a flat horizontal baseline, with a small arrowhead on top",
    "kantorovich": "a single convex polygon outline (feasibility region) with a few straight constraint lines and one small marked dot at an optimal corner",
    "lavrentyev": "a single hollow cone collapsing into one thin focused jet stream shooting forward",
    "belyaev": "a single small sitting friendly fox with floppy ears and a curled fluffy tail",
    "obratnye-zadachi": "a circular tomographic cross-section reconstructed from a few thin straight scan rays crossing it",
    "dendrohronologiya": "a single round tree-stump cross-section with concentric growth rings",
    "skrytaya-matematika": "a tiny mouse next to a large elephant, size comparison, side by side",
    "staryj-les": "a small stand of three tall old coniferous fir trees",
    "mamonty": "a single woolly mammoth with long curved tusks and shaggy fur, side view",
    "almazy": "a single cut brilliant-round diamond gemstone with facets",
    "klimat-yakutii": "a single tall thermometer with a snowflake on the left and a small sun on the right",
    "lenskie-stolby": "a row of several tall narrow vertical rock pillars rising by a river",
    "batagay": "a wide round crater-like sunken pit in flat tundra ground, bird's-eye view",
    "mikrobiom": "a few simple microbe shapes — small rods and spheres — clustered together, representing gut bacteria",
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
        "-H", "Content-Type: application/json", "-d", body], capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except Exception:
        return False
    if "error" in d:
        print("   error:", str(d["error"])[:120]); return False
    for p in d.get("candidates", [{}])[0].get("content", {}).get("parts", []):
        if "inlineData" in p:
            raw = base64.b64decode(p["inlineData"]["data"])
            im = Image.open(io.BytesIO(raw)).convert("RGB")
            if im.width > 800:
                im = im.resize((800, round(im.height * 800 / im.width)))
            # near-white/бежевый фон → чистый белый (как bgless-иконки Даниила на белом сайте)
            mask = im.convert("L").point(lambda v: 255 if v >= 224 else 0)
            im = Image.composite(Image.new("RGB", im.size, (255, 255, 255)), im, mask)
            im.save(path)  # настоящий PNG (Typst читает корректно)
            return os.path.getsize(path) if os.path.exists(path) else False
    return False


def main():
    key = gkey()
    out = os.path.join(ROOT, "site", "assets", "icons")
    os.makedirs(out, exist_ok=True)
    slugs = sys.argv[1:] or list(SUBJECTS)
    for slug in slugs:
        path = os.path.join(out, f"{slug}.png")
        old = os.path.join(out, f"{slug}.jpg")  # старый jpg-вариант убираем (перешли на bgless PNG)
        if os.path.exists(path) and os.path.getsize(path) > 8000:
            print(f"  skip {slug} (есть)"); continue
        if os.path.exists(old):
            os.remove(old)
        subj = SUBJECTS.get(slug)
        if not subj:
            print(f"  ? нет subject для {slug}"); continue
        for attempt in (1, 2):
            sz = gen(key, STYLE + subj, path)
            if sz:
                print(f"  [OK] {slug}: {sz:,} б"); break
            print(f"  retry {slug} ({attempt})")
    print("Готово (иконки).")


if __name__ == "__main__":
    main()
