#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// L1: одни и те же координаты точки приходят двумя путями — выбиты на латунном
// репере геодезистами И появляются на смартфоне от спутников. Совпадение цифр —
// и есть мысль уровня. Абстрактно: диск-репер слева, смартфон справа, ≈ между.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // ── РЕПЕР: латунный диск с геодезическим крестом и координатами
  let M = (0, 0)
  circle(M, radius: 1.15, fill: SAND.lighten(45%), stroke: (paint: INK, thickness: 1.1pt))
  circle(M, radius: 1.15, stroke: none)
  // крест-марка в центре
  line((-0.5, 0), (0.5, 0), stroke: (paint: INK, thickness: 0.8pt))
  line((0, -0.5), (0, 0.5), stroke: (paint: INK, thickness: 0.8pt))
  circle(M, radius: 0.12, fill: INK, stroke: none)
  content((0, -1.5), anchor: "north", text(size: 8.5pt)[репер])
  content((0, -1.9), anchor: "north", text(size: 8pt, fill: OLIVE)[(геодезисты)])
  content((0, 1.5), anchor: "south", text(size: 8.5pt)[55,751° N\
48,731° E])

  // ── знак приблизительного равенства между источниками
  content((2.4, 0.1), text(size: 16pt, fill: SAND.darken(15%))[$approx$])
  content((2.4, -0.8), anchor: "north", text(size: 8.5pt, fill: OLIVE)[те же\
цифры])

  // ── СМАРТФОН: скруглённый прямоугольник с экраном и теми же координатами
  let px = 4.8
  rect((px - 0.85, -1.5), (px + 0.85, 1.7), radius: 0.22,
       fill: white, stroke: (paint: INK, thickness: 1.1pt))
  rect((px - 0.62, -1.0), (px + 0.62, 1.3), radius: 0.06,
       fill: rgb("#EEF0EC"), stroke: (paint: SAND, thickness: 0.6pt))
  content((px, 0.45), text(size: 8pt)[55,751° N\
48,731° E])
  // точка-«вы здесь» на экране
  content((px, -0.35), image("icons/map-pin.svg", width: 0.4cm))
  content((px, -1.85), anchor: "north", text(size: 8.5pt)[смартфон])
  content((px, -2.25), anchor: "north", text(size: 8pt, fill: OLIVE)[(спутники)])

  // ── спутники над смартфоном: 3 орбитальных спутника с сигналом вниз
  for dx in (-1.2, 0.0, 1.2) {
    let sx = px + dx
    content((sx, 3.0), image("icons/satellite.svg", width: 0.66cm))
    line((sx, 2.6), (px, 1.78), stroke: (paint: SAND, thickness: 0.5pt, dash: "dotted"))
  }

  // ── итог
  content((2.4, -3.0), text(size: 9.5pt)[одни и те же координаты — из латуни под ногами и из космоса])
})
