#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Закон Клайбера в log-log: точки от мыши до слона ложатся на прямую с наклоном 3/4.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // оси
  line((0, 0), (5.6, 0), mark: (end: ">", fill: INK))
  line((0, 0), (0, 3.8), mark: (end: ">", fill: INK))
  content((5.6, -0.32), anchor: "east", text(size: 9pt, fill: OLIVE)[$log M$ (масса)])
  content((0.15, 3.8), anchor: "west", text(size: 9pt, fill: OLIVE)[$log B$ (обмен)])

  // линия наклона 3/4
  line((0.4, 0.5), (5.2, 4.1 * 0.75 + 0.5 - 0.4 * 0.75), stroke: (paint: OLIVE, thickness: 1.4pt))
  // точки-животные на линии
  let pts = ((0.7, "мышь"), (2.0, "кошка"), (3.3, "человек"), (4.7, "слон"))
  for (x, lab) in pts {
    let y = 0.5 + 0.75 * (x - 0.4)
    circle((x, y), radius: 0.09, fill: INK, stroke: none)
    content((x, y + 0.35), text(size: 7.5pt)[#lab])
  }
  content((3.7, 1.4), text(size: 10pt, fill: OLIVE)[$B prop M^(3\/4)$])
  content((2.7, -1.1), text(size: 8.5pt)[наклон 3/4 вместо ожидаемых 2/3])
})
