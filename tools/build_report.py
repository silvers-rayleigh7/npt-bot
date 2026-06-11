#!/usr/bin/env python3
"""Сборка PDF-отчёта по проекту tropa-bot → ~/Downloads.

Кириллица + научные символы — через Arial Unicode (TTF с полным покрытием Unicode).
Встроенные шрифты ReportLab кириллицу не рисуют, поэтому регистрируем TTF.
"""
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# --- Шрифты (Arial Unicode — кириллица + ρ λ √ ∝ ≈ ½) -------------------------
UNI = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
pdfmetrics.registerFont(TTFont("Uni", UNI))
pdfmetrics.registerFont(TTFont("UniB", BOLD))
pdfmetrics.registerFontFamily("Uni", normal="Uni", bold="UniB", italic="Uni", boldItalic="UniB")

# --- Палитра ------------------------------------------------------------------
NAVY = colors.HexColor("#1d3557")
BLUE = colors.HexColor("#2a6f97")
ACCENT = colors.HexColor("#e76f51")
GREEN = colors.HexColor("#2a9d8f")
LIGHT = colors.HexColor("#eef3f7")
GREY = colors.HexColor("#6c757d")
LINE = colors.HexColor("#cdd7e0")

# --- Стили --------------------------------------------------------------------
ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Title"], fontName="UniB", fontSize=21,
                    textColor=NAVY, leading=25, spaceAfter=2)
SUB = ParagraphStyle("SUB", fontName="Uni", fontSize=10.5, textColor=GREY,
                     leading=14, alignment=TA_CENTER, spaceAfter=2)
H2 = ParagraphStyle("H2", fontName="UniB", fontSize=13.5, textColor=BLUE,
                    leading=17, spaceBefore=13, spaceAfter=5)
BODY = ParagraphStyle("BODY", fontName="Uni", fontSize=9.7, leading=14.2,
                      textColor=colors.HexColor("#23303a"), spaceAfter=4, alignment=TA_LEFT)
SMALL = ParagraphStyle("SMALL", fontName="Uni", fontSize=8.6, leading=12,
                       textColor=colors.HexColor("#23303a"))
SMALLB = ParagraphStyle("SMALLB", parent=SMALL, fontName="UniB")
SMALLW = ParagraphStyle("SMALLW", parent=SMALL, textColor=colors.white)
CODE = ParagraphStyle("CODE", fontName="Uni", fontSize=8.4, leading=12.6,
                      textColor=NAVY, backColor=LIGHT, borderPadding=(6, 6, 6, 6))
FOOT = ParagraphStyle("FOOT", fontName="Uni", fontSize=8, textColor=GREY, alignment=TA_CENTER)


def chip(text, color):
    return Paragraph(f'<font color="white"><b> {text} </b></font>', SMALL), color


def section(title):
    return [Paragraph(title, H2),
            HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=6)]


def kv_table(rows, col_widths, header=None, header_bg=NAVY, body_font="SMALL"):
    style_body = SMALL if body_font == "SMALL" else SMALLB
    data = []
    if header:
        data.append([Paragraph(f"<b>{h}</b>", SMALLW) for h in header])
    for r in rows:
        data.append([Paragraph(c, style_body) for c in r])
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    cmds = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    if header:
        cmds += [("BACKGROUND", (0, 0), (-1, 0), header_bg),
                 ("TOPPADDING", (0, 0), (-1, 0), 5),
                 ("BOTTOMPADDING", (0, 0), (-1, 0), 5)]
        cmds.append(("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]))
    else:
        cmds.append(("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, LIGHT]))
    t.setStyle(TableStyle(cmds))
    return t


story = []

# ===== ШАПКА ==================================================================
story.append(Paragraph("Путеводитель по научной тропе", H1))
story.append(Paragraph("Голосовой научный ИИ-гид в Telegram &nbsp;·&nbsp; отчёт о проделанной работе", SUB))
story.append(Paragraph(
    "10 июня 2026",
    SUB))
story.append(Spacer(1, 4))
story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=4))

# ===== 1. ЧТО ЭТО =============================================================
story += section("1. Что это и зачем")
story.append(Paragraph(
    "Telegram-бот: человек задаёт научный вопрос <b>голосом или текстом</b> и получает "
    "<b>голосовой ответ</b> в манере русского научпопа (Перельман, Ливанов, «Квант»). Бот не "
    "пересказывает энциклопедию, а показывает привычное явление под неожиданным научным углом и "
    "обязательно называет принцип (рэлеевское рассеяние, параметрический резонанс). Философия — "
    "метод вместо фактов, «поперечное сечение реальности».", BODY))
story.append(Paragraph(
    "Ключевое экономическое решение: ядро работает на <b>OAuth-подписке Claude</b>, а не на "
    "поштучном API-биллинге. Это снимает главную боль заказчика — «бот сожрал кредиты».", BODY))

# ===== 2. ЧТО СОЗДАЛИ =========================================================
story += section("2. Что создали — архитектура")
story.append(Paragraph(
    "Сквозной путь запроса: голос пользователя распознаётся в текст, ядро на Claude Code "
    "формирует ответ с опорой на выверенную базу, ответ озвучивается и уходит в чат голосом + текстом.", BODY))
flow = (
    "Пользователь (Telegram)  →  Groq Whisper STT (ru)  →  claude-tg (Python, systemd, VPS)<br/>"
    "&nbsp;&nbsp;→  claude -p (модель opus, читает CLAUDE.md + RAG по content/)<br/>"
    "&nbsp;&nbsp;→  tts.py → Yandex SpeechKit v1 (голос filipp) → oggopus<br/>"
    "&nbsp;&nbsp;→  MCP send_telegram_file (🔊 голос)  +  send_telegram_message (📝 текст)"
)
story.append(Paragraph(flow, CODE))
story.append(Spacer(1, 7))
story.append(kv_table(
    header=["Слой", "Технология", "Зачем именно так"],
    rows=[
        ["Транспорт", "claude-tg (форк, Python)", "Готовый каркас Telegram ↔ Claude; правки — идемпотентным apply_patches.py"],
        ["Речь → текст", "Groq Whisper v3 (ru)", "Бесплатный тариф, русский язык + научный prompt"],
        ["Ядро", "Claude Code opus, OAuth", "Максимум качества; оплата подпиской, не поштучно"],
        ["Текст → речь", "Yandex SpeechKit v1", "Нативно-русские ударения; oggopus без ffmpeg"],
        ["Личность", "CLAUDE.md", "Системный промпт: уровни, манера, обязательный термин"],
        ["Знания (RAG)", "content/ + скилл scipop-answer", "Выверенная база против галлюцинаций"],
    ],
    col_widths=[2.6 * cm, 4.0 * cm, 9.7 * cm]))

# ===== 3. ЭВОЛЮЦИЯ ============================================================
story += section("3. Что добавляли, меняли и убирали — и почему")
story.append(Paragraph(
    "20 коммитов от ядра до текущего состояния. Главные вехи в хронологическом порядке:", BODY))
story.append(kv_table(
    header=["Этап", "Что сделали", "Почему"],
    rows=[
        ["Ядро", "tts.py (TDD), личность CLAUDE.md, база content/", "Минимальный рабочий каркас бота"],
        ["Вывод", "Только голос, память диалога, мультиаккаунт", "Голосовой формат как продукт; свои аккаунты владельца"],
        ["Качество", "Адаптивность уровня (новичок/знаток), opus", "Один вопрос — разным людям разный ответ"],
        ["RAG", "Обязательная проверка базы content/ перед ответом", "Достоверность важнее скорости; против выдумок"],
        ["Принцип", "Обязательно называть научный термин явления", "Это и есть «научный ракурс», ради которого бот"],
        ["Озвучка", "ElevenLabs → Yandex v3 → отказ → Yandex v1 filipp", "ElevenLabs: кривые ударения; v3: нестабильно + андрогинный тембр"],
        ["Доставка", "Патч send_voice (.ogg как голосовое)", "PyPI-версия слала .ogg документом"],
        ["Текст+формулы", "Голос без формул + текст всегда; новый MCP send_telegram_message", "Формулы Telegram голосом не нужны, а в тексте полезны"],
        ["Манера", "Раздел «в духе Капицы»: темп, паузы, регистр", "Весомость и доверие в подаче ответа"],
        ["Чистота", "stop-slop: убрать AI-маркеры из текста", "Живой язык без штампов GPT"],
        ["Тест-ветка", "Два уровня текста (🔹 любознательным / 🔸 продвинутым)", "Простое и глубокое в одном ответе"],
        ["Тест-ветка", "Чистый текст без markdown + формула в Ур. 2 обязательна", "Telegram рисует * # сырыми; формулы пропадали из-за лазейки промпта"],
    ],
    col_widths=[2.4 * cm, 7.2 * cm, 6.7 * cm]))

# ===== 4. КАК ВЫГЛЯДИТ ОТВЕТ ==================================================
story += section("4. Как выглядит ответ бота сейчас")
story.append(Paragraph(
    "На каждый вопрос уходят <b>ровно два сообщения</b>. Голос — живая устная речь без формул, "
    "подстроенная под уровень собеседника. Текст следом — в два уровня:", BODY))
story.append(kv_table(
    rows=[
        ["🔹 Уровень 1 — для любознательных", "Прямой ответ образно и на пальцах, принцип простыми словами, без формул и тяжёлых терминов."],
        ["🔸 Уровень 2 — для продвинутых", "Точный механизм, термины, числовая оценка и формула. Напр.: F ≈ ½ρv<super>2</super>S, "
                                          "T = 2π√(L/g), I ∝ 1/λ<super>4</super> — Юникодом, отдельной строкой, с расшифровкой переменных."],
    ],
    col_widths=[5.3 * cm, 11.0 * cm]))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "Жёсткие правила оформления: никакого markdown (Telegram показывает * # сырыми), только "
    "короткий дефис, формула обязательна для любого количественного явления.", SMALL))

# ===== 5. ТРУДНО / ЛЕГКО ======================================================
story += section("5. Что далось трудно, а что пошло сразу")
hard = [
    "Озвучка — самый длинный путь: ElevenLabs «тянул» слова и врал ударения → Yandex v3 давал андрогинный голос и нестабильную доставку → откат на стабильный v1 filipp.",
    "Доставка .ogg голосовым, а не документом — потребовала патча send_voice.",
    "Баг: не импортирован json → падал /start → не регистрировался 2-й аккаунт.",
    "Формулы пропадали из текста — лазейка в промпте + консерватизм RAG; чинили формулировкой + чисткой в коде.",
    "Сервер /root/tropa-bot оказался не git-репо → деплой через scp + apply_patches, а не git pull.",
]
easy = [
    "Каркас на готовом claude-tg — форк завёлся быстро.",
    "OAuth-подписка вместо API — сразу сняла проблему стоимости.",
    "tts.py написан по TDD — тесты на моках, без расхода токенов.",
    "RAG по content/ через Grep/Read — заработал без сложностей.",
    "Персонализация по уровню и stop-slop — легли в промпт чисто.",
]
hard_p = [Paragraph(f"• {t}", SMALL) for t in hard]
easy_p = [Paragraph(f"• {t}", SMALL) for t in easy]
hard_cell = [Paragraph("<b>Трудно</b>", SMALLW)] + hard_p
easy_cell = [Paragraph("<b>Сразу пошло</b>", SMALLW)] + easy_p
tbl = Table([[hard_cell, easy_cell]], colWidths=[8.15 * cm, 8.15 * cm])
tbl.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("BACKGROUND", (0, 0), (0, 0), ACCENT),
    ("BACKGROUND", (1, 0), (1, 0), GREEN),
    ("BOX", (0, 0), (-1, -1), 0.5, LINE),
    ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
    ("TOPPADDING", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
]))
story.append(tbl)

# ===== 6. СОСТОЯНИЕ ===========================================================
story += section("6. Текущее состояние и что осталось")
story.append(kv_table(
    header=["Ветка", "Состояние", "Что в ней"],
    rows=[
        ["main", "стабильная, в проде", "Базовый бот: голос + текст, персонализация, манера Капицы, stop-slop"],
        ["text-two-levels-test", "развёрнута, тест", "Текст в два уровня + чистый текст без markdown + формула в Ур. 2 обязательна"],
    ],
    col_widths=[4.0 * cm, 3.0 * cm, 9.3 * cm]))
story.append(Spacer(1, 6))
story.append(Paragraph("Осталось (по решению заказчика):", SMALLB))
for t in [
    "Прослушать 4 образца голоса (filipp / zahar / ermil) и выбрать тембр и темп.",
    "Проверить вживую двухуровневый текст на том же вопросе: нет лишних символов, в Ур. 2 есть формула.",
    "Если тест одобрен — влить text-two-levels-test в main (чистый fast-forward).",
    "На будущее: расширение базы content/, web/PWA-версия, GPS-режим гида.",
]:
    story.append(Paragraph(f"• {t}", SMALL))

story.append(Spacer(1, 12))
story.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=5))
story.append(Paragraph(
    "tropa-bot &nbsp;·&nbsp; голосовой научный ИИ-гид &nbsp;·&nbsp; секреты (ключи, токены, пароли) в репозитории не хранятся",
    FOOT))

# ===== СБОРКА =================================================================
out = os.path.expanduser("~/Downloads/tropa-bot_отчёт_о_работе.pdf")
doc = SimpleDocTemplate(
    out, pagesize=A4,
    leftMargin=1.7 * cm, rightMargin=1.7 * cm,
    topMargin=1.5 * cm, bottomMargin=1.3 * cm,
    title="Путеводитель по научной тропе — отчёт", author="AMAI / tropa-bot")
doc.build(story)
print("OK:", out)
print("size:", os.path.getsize(out), "bytes")
