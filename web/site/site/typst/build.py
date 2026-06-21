#!/usr/bin/env python3
"""
Build PDF cards for each POI x level from the Tropa route YAML.

Usage:
    python build.py                              # uses default YAML
    python build.py --yaml path/to/poi.yaml      # custom YAML
    python build.py --content-dir path/to/md/     # override content from .md files
    python build.py --output-dir path/to/cards/   # custom output directory

Content override directory structure (--content-dir):
    {poi_id}.l1.md   - L1 content for poi_id
    {poi_id}.l2.md   - L2 content for poi_id
    {poi_id}.l3.md   - L3 content for poi_id

If a .md file exists, its content is used; otherwise the YAML seed is used.
For L2 content, use Typst math syntax: $rho_i = c dot (t_(rx) - t_i) + b$
"""

import argparse
import json
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required. Install: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_YAML = SCRIPT_DIR.parent.parent / "bot" / "config" / "poi.innopolis.yaml"
DEFAULT_OUTPUT = SCRIPT_DIR.parent / "cards"
TEMPLATE_PATH = SCRIPT_DIR / "template.typ"
DIAGRAMS_PATH = SCRIPT_DIR / "diagrams.typ"

# Mapping from poi_id to diagram function name in diagrams.typ
POI_DIAGRAMS = {}

# Full website content for each POI, keyed by poi_id.
# These are the rich texts from the website (index.html), much fuller than YAML seeds.
# L2 content uses Typst math notation.
WEBSITE_CONTENT = {
    "university_entrance": {
        "l1": (
            "Открой бот --- он уже знает, что ты у главного входа. Но ни один спутник "
            "тебя не видел. Ни камеры, ни луча, ни фотографии.\n\n"
            "Спутники не ищут тебя. Каждый передаёт одно: «сейчас такое-то время, "
            "я в такой-то точке». Телефон ловит сигналы и замеряет задержку. "
            "Один спутник --- расстояние. Три спутника --- три сферы. "
            "Точка пересечения --- ты.\n\n"
            "Ошибка в миллионную долю секунды сдвигает на 300 метров. Поэтому "
            "на орбите --- атомные часы. Так же охотится летучая мышь: крик, задержка, расстояние."
        ),
        "l2": (
            "Спутники работают как маяки: передают координаты и точное время отправки. "
            "Телефон знает время приёма. Разница при скорости света --- расстояние.\n\n"
            "Одно расстояние --- сфера. Два --- окружность. Три --- две точки, одна обычно "
            "в космосе. Четвёртый спутник нужен не для геометрии, а для часов: у телефона "
            "нет атомных часов, его время сдвинуто на неизвестную величину $b$.\n\n"
            "Псевдодальность до $i$-го спутника:\n\n"
            "$rho_i = c dot (t_(r x) - t_i) + b$\n\n"
            "где $c = 3 dot 10^8$ м/с. Четыре спутника --- четыре уравнения "
            "для $x, y, z$ и $b$.\n\n"
            "Ошибка $Delta t = 1$ мкс → $Delta d = 300$ м. Атомные часы (рубидий, цезий) "
            "держат $tilde 10$ нс --- это $tilde 3$ м. В городской застройке "
            "Иннополиса сигнал отражается от стен, мультиконстелляция "
            "(GPS+ГЛОНАСС+Galileo+BeiDou) снижает ошибку.\n\n"
            "Тот же принцип --- трилатерация по задержке --- работает "
            "в подводном сонаре, в УЗИ и у каждой летучей мыши."
        ),
        "l3": (
            "*Эйнштейн в кармане.* Без поправок общей теории относительности GPS "
            "сломался бы за сутки. Часы на спутниках (высота 20 200 км) идут быстрее "
            "земных: гравитационный потенциал ниже, время течёт иначе. Разница --- "
            "38 мкс в сутки. Звучит ничтожно, но $38 \"мкс\" times 3 dot 10^8 \"м/с\"$ "
            "= 11.4 км ошибки за день. К концу недели навигатор показывал бы соседний город. "
            "Поправку заложили до первого запуска GPS в 1978 году --- инженеры поверили "
            "Эйнштейну на слово.\n\n"
            "*От микросекунд к метрам.* Скорость света --- не приблизительная величина. "
            "С 1983 года метр определён через неё: ровно 299 792 458 м/с. GPS работает на "
            "двух частотах --- L1 (1575.42 МГц) и L2 (1227.60 МГц). Двухчастотный приём "
            "устраняет ионосферную задержку: заряженные частицы на высоте 80--400 км замедляют "
            "волны по-разному на разных частотах. Гражданская точность: 3--5 м. Военная "
            "(код P(Y)): 0.3 м. Дифференциальный GPS с базовой станцией: сантиметры. "
            "Геодезисты измеряют движение тектонических плит --- миллиметры в год --- "
            "тем же GPS.\n\n"
            "*Четыре обличия одной задачи.* Радар: радиоимпульс → отражение от самолёта → "
            "задержка → расстояние. Летучая мышь: ультразвуковой щелчок (20--200 кГц) → "
            "отражение от мотылька → расстояние с точностью 1 мм. Подводный сонар: звук "
            "в воде (1500 м/с) → отражение от дна → профиль глубин. УЗИ: ультразвук → "
            "отражение от границ органов → изображение ребёнка. Сейсморазведка: взрыв → "
            "упругие волны → отражение от пластов → карта нефти. Одна структура, "
            "пять доменов.\n\n"
            "*От Мерсенна к Хафеле.* Марен Мерсенн в 1636 году первым измерил скорость "
            "звука: выстрел из пушки, помощник на расстоянии, вспышка мгновенна, звук --- нет. "
            "В 1971 году Хафеле и Китинг посадили атомные часы на рейсовые самолёты "
            "и облетели Землю в обе стороны. Часы на востоке отстали, на западе --- ушли "
            "вперёд. Разница совпала с ОТО с точностью 10%. Прямое подтверждение поправки, "
            "которую GPS-инженеры заложили за 7 лет до этого эксперимента.\n\n"
            "*Открытый вопрос.* GPS уязвим: сигнал 20 Вт с высоты 20 000 км легко "
            "заглушить. В тоннеле, под водой, в зоне РЭБ --- навигации нет. Квантовая "
            "инерциальная навигация измеряет ускорение через интерференцию охлаждённых "
            "атомов --- без единого внешнего сигнала. DARPA финансирует с 2010-х. Проблема: "
            "атомы нужно охладить до микрокельвинов. Пока это шкаф. Когда поместится "
            "в телефон --- не знает никто."
        ),
    },
    "atrium_library": {
        "l1": (
            "Хлопни в ладоши прямо здесь, в атриуме. Один раз, громко. Слышишь, как звук "
            "не исчезает сразу? Он ещё «живёт» --- полсекунды, секунду.\n\n"
            "Это не эхо от одной стены. Это сотни отражений --- от стёкол, потолка, бетона --- "
            "которые накладываются друг на друга. Большой зал звучит иначе, чем комната, "
            "именно поэтому: чем больше объём, тем дольше звук путешествует внутри.\n\n"
            "Ковры, люди, книжные полки --- не декор. Это инструменты управления звуком. "
            "Каждый материал поглощает свою долю энергии. Акустические панели в аудиториях "
            "Иннополиса --- укрощение этого облака отражений."
        ),
        "l2": (
            "После хлопка энергия звука мечется между стенами, теряя часть при каждом "
            "отражении. Время реверберации $T_60$ --- время, за которое уровень падает "
            "на 60 дБ (в миллион раз).\n\n"
            "Формула Сабина: $T_60 = 0.161 dot V slash A$, где $V$ --- объём (м³), "
            "$A$ --- эквивалентная площадь поглощения (м² сабин). Для атриума Иннополиса "
            "($V approx 5000$ м³, $A approx 500$ м²): $T_60 approx 1.6$ с --- длинновато "
            "для лекций (оптимум 0.7--1.0 с), но нормально для фойе.\n\n"
            "Коэффициенты поглощения: бетон $tilde 0.02$, ковёр $tilde 0.4$, "
            "человек $tilde 0.5$ сабин, акустическая панель $tilde 0.8$. Удвоение "
            "поглощающей площади сокращает хвост вдвое.\n\n"
            "Тот же принцип --- поглощение волновой энергии средой --- работает для света "
            "в тумане, тепла в стене и радиоволн в лесу."
        ),
        "l3": (
            "*Подушки из Гарварда.* Уоллес Сабин в 1895 году получил задачу: починить "
            "акустику лекционного зала Fogg Museum в Гарварде. Лектора не было слышно --- "
            "звук тонул в реверберации. Сабин поступил как физик: три года таскал подушки "
            "из соседнего зала, раскладывал по-разному и замерял время затухания. Из этих "
            "опытов родилась формула и профессия акустического консультанта --- первая "
            "в истории.\n\n"
            "*Числа в камне.* Бостонский Symphony Hall (1900), построенный по расчётам "
            "Сабина, до сих пор считается одним из лучших залов мира. $T_60 approx 1.8$ с --- "
            "идеально для симфонического оркестра. Большой зал Московской консерватории: "
            "$T_60 approx 1.7$ с. Берлинская филармония Шаруна (1963): $T_60 approx 2.0$ с --- "
            "длиннее, под Караяна. Каждый зал --- компромисс: короткий хвост --- "
            "разборчивость речи, длинный --- объём оркестра.\n\n"
            "*Поперечное сечение.* Экспоненциальное затухание волновой энергии в среде --- "
            "структура, работающая в любом масштабе. Свет в мутной воде: интенсивность падает "
            "по закону Бугера-Ламберта-Бера $I = I_0 e^(-alpha x)$. Радиоволна в лесу: "
            "каждое дерево --- поглотитель, сигнал GPS слабеет. Тепло сквозь стену: "
            "температура экспоненциально приближается к наружной. Звук в зале --- то же "
            "уравнение, только среда --- объём воздуха, а «поглотители» --- стены и люди.\n\n"
            "*Как измеряют.* Современная акустическая съёмка: выстрел стартового пистолета → "
            "массив микрофонов → импульсный отклик помещения (IR). Из IR считают $T_60$, "
            "ранние отражения, clarity ($C_80$), lateral fraction. Симуляция: метод "
            "трассировки лучей (тысячи виртуальных «фотонов звука» отражаются от стен) "
            "или конечных элементов. Точность: $plus.minus 0.1$ с для $T_60$ --- архитектор "
            "проверяет зал до того, как его построят.\n\n"
            "*Открытый вопрос.* Формула Сабина работает для диффузного поля --- когда "
            "звуковая энергия распределена равномерно. В реальных залах это приближение. "
            "Современные алгоритмы (wave-based acoustic simulation) решают полное волновое "
            "уравнение --- но для зала объёмом 10 000 м³ на частотах выше 1 кГц это "
            "вычислительно неподъёмно. Граница между лучевой и волновой акустикой --- открытая "
            "задача. Кто первым научится считать полную волновую акустику концертного зала "
            "в реальном времени --- перевернёт архитектуру."
        ),
    },
}

# POI colors matching the website
POI_COLORS = {
    "university_entrance": "#f04f3a",
    "atrium_library": "#3c7dd9",
    "robot_path": "#e0a72f",
    "tesla_marker": "#7f56d9",
    "boulevard_game": "#2f6f63",
    "sports_scaling": "#c45f28",
    "forest_water_column": "#4a8a3f",
    "data_center_view": "#111827",
}


def html_to_typst(html: str) -> str:
    """Convert HTML content with KaTeX math to plain text with Typst math."""
    text = html
    text = re.sub(r'</?p>', '\n\n', text)
    text = re.sub(r'<strong>(.*?)</strong>', r'*\1*', text)
    text = re.sub(r'</?[^>]+>', '', text)

    def convert_math(match):
        m = match.group(1)
        while '\\\\' in m:
            m = m.replace('\\\\', '\\')
        m = m.replace('\\mathcal{E}', 'cal(E)')
        m = re.sub(r'\\dot\{([^}]+)\}', r'dot(\1)', m)
        m = re.sub(r'\\text\{([^}]+)\}', r'"\1"', m)
        m = re.sub(r'\\operatorname\{([^}]+)\}', r'"\1"', m)
        m = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', m)
        m = re.sub(r'\\sqrt\{([^}]+)\}', r'sqrt(\1)', m)
        m = m.replace('\\cdot', ' dot ')
        m = m.replace('\\times', ' times ')
        m = m.replace('\\Delta', 'Delta ')
        m = m.replace('\\Phi', 'Phi ')
        m = m.replace('\\Omega', 'Omega ')
        m = m.replace('\\sim', 'tilde ')
        m = m.replace('\\approx', 'approx ')
        m = m.replace('\\rho', 'rho ')
        m = m.replace('\\theta', 'theta ')
        m = m.replace('\\alpha', 'alpha ')
        m = m.replace('\\beta', 'beta ')
        m = m.replace('\\gamma', 'gamma ')
        m = m.replace('\\lambda', 'lambda ')
        m = m.replace('\\mu', 'mu ')
        m = m.replace('\\pi', 'pi ')
        m = m.replace('\\sigma', 'sigma ')
        m = m.replace('\\omega', 'omega ')
        m = m.replace('\\epsilon', 'epsilon ')
        m = m.replace('\\ldots', 'dots ')
        m = m.replace('\\dots', 'dots ')
        m = m.replace('\\leq', 'lt.eq ')
        m = m.replace('\\geq', 'gt.eq ')
        m = m.replace('\\pm', 'plus.minus ')
        m = m.replace('\\ln', 'ln ')
        m = m.replace('\\log', 'log ')
        m = m.replace('\\exp', 'exp ')
        m = m.replace('\\sin', 'sin ')
        m = m.replace('\\cos', 'cos ')
        m = m.replace('^\\top', '^(top)')
        m = m.replace('^{\\top}', '^(top)')
        m = m.replace('\\top', 'top')
        m = m.replace('\\nbsp', ' ')
        m = re.sub(r'_\{([^}]+)\}', r'_(\1)', m)
        m = re.sub(r'\^\{([^}]+)\}', r'^(\1)', m)
        # Multi-letter variables: wrap 2+ consecutive letters in quotes
        # But skip known Typst built-ins
        typst_builtins = {'dot', 'tilde', 'approx', 'lt', 'gt', 'eq', 'top',
                          'ln', 'log', 'exp', 'sin', 'cos', 'sqrt', 'cal',
                          'plus', 'minus', 'times', 'dots', 'Delta', 'Phi',
                          'Omega', 'rho', 'theta', 'alpha', 'beta', 'gamma',
                          'lambda', 'mu', 'pi', 'sigma', 'omega', 'epsilon'}
        def fix_multichar(m2):
            word = m2.group(0)
            if word in typst_builtins:
                return word
            return f'"{word}"'
        m = re.sub(r'(?<!["\w])([A-Za-z]{2,})(?!["\w(a-z])', fix_multichar, m)
        m = re.sub(r'\\([A-Za-z]+)', r'\1', m)
        return f'${m}$'

    text = re.sub(r'\$\$([^$]+)\$\$', convert_math, text)
    text = re.sub(r'\$([^$]+)\$', convert_math, text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = text.replace('\\_', '_')
    text = text.replace('\\\\', '\\')
    return text.strip()


def escape_typst(text: str) -> str:
    """Escape special Typst characters in plain text, but preserve $...$ math blocks."""
    # Split on $...$ to preserve math
    parts = re.split(r'(\$[^$]+\$)', text)
    result = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            # This is a math block - keep as is
            result.append(part)
        else:
            # Plain text - escape special chars
            part = part.replace('\\', '\\\\')
            part = part.replace('#', '\\#')
            part = part.replace('*', '\\*')
            part = part.replace('_', '\\_')
            part = part.replace('@', '\\@')
            # Keep --- as em-dash
            part = part.replace('---', '---')
            result.append(part)
    return ''.join(result)


def get_content(poi_id: str, level: str, yaml_poi: dict, content_dir: Path | None) -> str:
    """Get content for a POI at a given level. Priority: content_dir > WEBSITE_CONTENT > YAML seed."""
    level_key = level.lower()

    # 1. Check content-dir override
    if content_dir:
        md_path = content_dir / f"{poi_id}.{level_key}.md"
        if md_path.exists():
            return md_path.read_text(encoding="utf-8").strip()

    # 2. Check built-in website content
    if poi_id in WEBSITE_CONTENT and level_key in WEBSITE_CONTENT[poi_id]:
        return WEBSITE_CONTENT[poi_id][level_key]

    # 3. Fall back to YAML l1/l2/l3 fields (HTML → Typst conversion)
    raw = yaml_poi.get(level_key, "")
    if isinstance(raw, str) and raw.strip():
        result = html_to_typst(raw)
        result = "\x00TYPST_READY\x00" + result
        return result

    # 4. Legacy: YAML seed keys
    seed_key = f"{level_key.replace('l', 'level')}_seed"
    seed = yaml_poi.get(seed_key, "")
    if isinstance(seed, str):
        return seed.strip()
    return str(seed).strip()


def generate_typ_file(poi: dict, poi_number: int, level: str, content: str, output_path: Path):
    """Generate a .typ file for a single POI card."""
    poi_id = poi["id"]
    poi_name = poi["name"]
    poi_color = POI_COLORS.get(poi_id, "#2f6f63")
    topic = poi.get("topic", "")
    expert = poi.get("expert", "")
    tags = poi.get("tags", [])
    diagram_func = POI_DIAGRAMS.get(poi_id)

    if content.startswith("\x00TYPST_READY\x00"):
        safe_content = content[len("\x00TYPST_READY\x00"):]
    else:
        safe_content = escape_typst(content)
    safe_name = poi_name.replace('"', '\\"')
    safe_topic = topic.replace('"', '\\"')
    safe_expert = expert.replace('"', '\\"')
    tags_str = ", ".join(f'"{t}"' for t in tags)

    # Build import line and diagram parameter
    if diagram_func and level in ("L1", "L2"):
        imports = (
            '#import "template.typ": poi-card\n'
            f'#import "diagrams.typ": {diagram_func}'
        )
        diagram_param = f'  diagram: {diagram_func}(rgb("{poi_color}")),'
    else:
        imports = '#import "template.typ": poi-card'
        diagram_param = ''

    diagram_line = f"\n{diagram_param}" if diagram_param else ""

    typ_content = textwrap.dedent(f"""\
        {imports}

        #poi-card(
          poi_name: "{safe_name}",
          poi_number: {poi_number},
          poi_color: "{poi_color}",
          topic: "{safe_topic}",
          level: "{level}",
          content_text: [{safe_content}],
          expert: "{safe_expert}",
          tags: ({tags_str}),{diagram_line}
        )
    """)

    output_path.write_text(typ_content, encoding="utf-8")


def compile_typ(typ_path: Path, pdf_path: Path) -> bool:
    """Compile a .typ file to PDF using typst CLI."""
    try:
        result = subprocess.run(
            ["typst", "compile", str(typ_path), str(pdf_path), "--root", str(typ_path.parent)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(f"  ERROR compiling {typ_path.name}: {result.stderr.strip()}", file=sys.stderr)
            return False
        return True
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT compiling {typ_path.name}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("ERROR: typst not found. Install: https://typst.app", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Build Tropa POI PDF cards")
    parser.add_argument("--yaml", type=Path, default=DEFAULT_YAML, help="Path to poi YAML file")
    parser.add_argument("--content-dir", type=Path, default=None,
                        help="Directory with .md content overrides (poi_id.l1.md, etc.)")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT,
                        help="Output directory for PDF cards")
    parser.add_argument("--levels", nargs="+", default=["L1", "L2", "L3"],
                        help="Levels to generate (default: L1 L2 L3)")
    args = parser.parse_args()

    # Load YAML
    if not args.yaml.exists():
        print(f"ERROR: YAML file not found: {args.yaml}", file=sys.stderr)
        sys.exit(1)

    with open(args.yaml, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    pois = data.get("poi", [])
    if not pois:
        print("ERROR: No POIs found in YAML", file=sys.stderr)
        sys.exit(1)

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # We need the template and diagrams accessible from the generated .typ files
    # Copy them to output dir so imports work with --root
    import shutil
    template_dest = args.output_dir / "template.typ"
    shutil.copy2(TEMPLATE_PATH, template_dest)
    diagrams_dest = args.output_dir / "diagrams.typ"
    shutil.copy2(DIAGRAMS_PATH, diagrams_dest)

    index = {}
    total = 0
    errors = 0

    for i, poi in enumerate(pois):
        poi_id = poi["id"]
        poi_number = i + 1
        index[poi_id] = {}

        for level in args.levels:
            content = get_content(poi_id, level, poi, args.content_dir)
            if not content:
                print(f"  SKIP {poi_id}/{level}: no content")
                continue

            slug = f"{poi_number:02d}_{poi_id}_{level.lower()}"
            typ_path = args.output_dir / f"{slug}.typ"
            pdf_path = args.output_dir / f"{slug}.pdf"

            print(f"  {poi_number}. {poi['name']} [{level}] ...", end=" ")

            generate_typ_file(poi, poi_number, level, content, typ_path)

            if compile_typ(typ_path, pdf_path):
                print("OK")
                index[poi_id][level.lower()] = pdf_path.name
                total += 1
            else:
                errors += 1

    # Write index.json
    index_path = args.output_dir / "index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"\nDone: {total} PDFs generated, {errors} errors")
    print(f"Output: {args.output_dir}")
    print(f"Index:  {index_path}")

    # Clean up .typ files (keep only PDFs and index)
    for typ_file in args.output_dir.glob("*.typ"):
        if typ_file.name not in ("template.typ", "diagrams.typ"):
            typ_file.unlink()
    template_dest.unlink(missing_ok=True)
    diagrams_dest.unlink(missing_ok=True)

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
