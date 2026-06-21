#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Шкала-маршрут модели (Солнце 2,5 м → Нептун 165 м). Реальные расстояния в
// масштабе: 4 внутренние планеты скучены в первых 8 м у Солнца, дальше — гиганты
// с огромными провалами пустоты. Иллюстрирует L1: «почти весь путь — пустота».
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let W = 13.0
  let Dmax = 165.0
  let s = W / Dmax              // см на метр модели
  let y = 0.0
  let xof(d) = d * s

  // ── ось-маршрут
  line((0, y), (W + 0.3, y), stroke: (paint: INK, thickness: 1.0pt),
    mark: (end: ">", fill: INK, scale: 0.5))

  // ── Солнце слева (иконка над осью, подпись под осью — не теснит внутреннюю зону)
  content((0, y + 0.18), anchor: "south", image("icons/sun.svg", width: 0.52cm))
  content((0, y - 0.42), text(size: 9pt, fill: SUN.darken(15%))[Солнце])

  // ── внутренние 4 планеты: при линейном масштабе они в первых 8 м (≈0,6 см) —
  //    скучены вплотную к Солнцу. Не рисуем неразборчивые точки, а помечаем зону
  //    коротким оливковым сегментом на оси + выноской в ЧИСТОЕ поле перед Юпитером.
  let z0 = xof(2.0)
  let z1 = xof(8.4)
  line((z0, y), (z1, y), stroke: (paint: OLIVE, thickness: 2.2pt))
  // выноска: от зоны вверх-вправо к компактной двустрочной подписи (Солнце↔Юпитер)
  line(((z0 + z1) / 2, y + 0.08), (1.2, y + 0.55), stroke: (paint: SAND, thickness: 0.6pt))
  content((1.2, y + 0.62), anchor: "south",
    align(center, text(size: 8.5pt, fill: OLIVE)[4 планеты\
первые 8 м]))

  // ── внешние гиганты: подписи снизу, поодиночке (видны провалы пустоты)
  let outer = (
    (28.6, [Юпитер]), (52.0, [Сатурн]), (105.0, [Уран]), (165.0, [Нептун]),
  )
  for p in outer {
    let x = xof(p.at(0))
    circle((x, y), radius: 0.09, fill: INK, stroke: none)
    line((x, y - 0.04), (x, y - 0.30), stroke: (paint: SAND, thickness: 0.6pt))
    content((x, y - 0.42), text(size: 9.5pt)[#p.at(1)])
  }

  // ── ремарки
  content((W / 2, y - 1.15), text(size: 9.5pt, fill: OLIVE)[почти весь путь — пустота])
  content((W, y + 0.5), anchor: "east", text(size: 9pt)[165 м до Нептуна])
})
