# Промпт для иконок-мотивов сюжетов (единый ручной стиль)

Вставляешь **мастер-промпт** + подставляешь объект сюжета в `{{SUBJECT}}`.
Стиль: тонкая ручная монолиния чёрным по чистому белому, как натуралистический
полевой набросок. Один вес линии, без заливки/теней/цвета.

## Мастер-промпт (EN — модели понимают лучше)

```
Minimalist hand-drawn line illustration of {{SUBJECT}}, shown as a small natural
nature vignette — organic forms, set on a faint horizon / ground line with a few
sparse grass blades, twigs or gentle hills, like a naturalist's field-journal sketch.
Single thin ink line, uniform stroke weight, fine-liner pen sketch, monoline, rounded
line ends, hand-drawn and slightly imperfect. No fill, no shading, no hatching, no
color — pure black ink (#1A1A18) on a plain pure-white background. Calm, airy, lots of
negative space, minimal detail, flat 2D, no perspective, no 3D. Wide horizontal banner
format, aspect ratio 2:1, composition spread gently across the width.
```

## Негатив-промпт

```
color, gradient, shading, hatching, crosshatch, fill, texture, photo, photorealistic,
3D, perspective, shadow, frame, border, box, text, letters, label, watermark,
signature, busy, cluttered, dense detail
```
(фон-сцену не запрещаем — нужна лёгкая природная виньетка: горизонт, трава, холмы.)

## Как держать ЕДИНЫЙ стиль на всём наборе

- Используй **style-reference**: одну нашу иконку как эталон стиля
  (Midjourney `--sref <url>`, Recraft → Style, или «match this style» с приложенным
  PNG). Тогда все иконки выйдут одной рукой.
- Фиксируй **один сид** (seed) для всей серии.
- Лучшие сервисы: **Recraft** (вектор/SVG, можно залочить стиль — идеально),
  Ideogram, Midjourney (`--no color`), DALL·E. Для вектора сразу — Recraft.

## Как заполнять {{SUBJECT}}

Описывай КОНКРЕТНЫЙ предмет/мотив сюжета одной фразой (по-английски), без сцены:

| Сюжет | {{SUBJECT}} |
|---|---|
| Водораздел | a hill ridge with one water drop splitting into two streams down opposite slopes |
| Мост Леонардо | a self-supporting arched bridge made of interlocking logs |
| Валун-термометр | a single rounded boulder with a small sun above it |
| Маятниковая роща | a simple pendulum: a bob on a string under a horizontal bar |
| Солнечные часы | a sundial with a triangular gnomon casting a shadow |
| Белая берёза | a single birch leaf with veins |
| Услышь расстояние | concentric sound-wave arcs spreading from a point (echo) |
| Террасы времени | a stepped terraced hillside (staircase of soil layers) |
| Спутниковая навигация | a small satellite on an orbit line around a dot |

## Пример (готовый к вставке)

```
Minimalist hand-drawn line illustration of a self-supporting arched bridge made of
interlocking logs over a small stream, shown as a natural nature vignette on a faint
ground line with a few sparse grass blades. Single thin ink line, uniform stroke weight,
fine-liner pen sketch, monoline, rounded line ends, hand-drawn. No fill, no shading,
no color — pure black ink on a plain pure-white background. Calm, airy, lots of negative
space, flat 2D, no 3D. Wide horizontal banner, aspect ratio 2:1.
```
