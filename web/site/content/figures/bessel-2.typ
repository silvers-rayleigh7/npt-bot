#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Эллипсоид Бесселя: Земля слегка сплюснута, полюс ближе к центру (сжатие преувеличено).
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // идеальный шар (пунктир) для сравнения
  circle((0, 0), radius: 2.0, stroke: (paint: OLIVE.lighten(35%), thickness: 0.7pt, dash: "dashed"))
  // эллипсоид (сжатие преувеличено)
  group({ translate((0, 0)); scale(x: 100%, y: 82%); circle((0, 0), radius: 2.0, fill: SAND.lighten(45%), stroke: INK) })
  circle((0, 0), radius: 0.06, fill: INK, stroke: none)

  // экваториальный радиус a
  line((0, 0), (2.0, 0), mark: (end: ">", fill: INK), stroke: (thickness: 0.9pt))
  content((1.0, 0.22), text(size: 8.5pt)[$a$])
  // полярный радиус b
  line((0, 0), (0, 1.64), mark: (end: ">", fill: INK), stroke: (thickness: 0.9pt))
  content((0.2, 0.9), anchor: "west", text(size: 8.5pt)[$b$])

  // подписи значений
  content((2.2, 0), anchor: "west", text(size: 8pt)[$a = 6\,377\,397$ м])
  content((0, 2.25), text(size: 8pt)[$b = 6\,356\,079$ м])
  content((0, -2.5), text(size: 9.5pt)[сжатие $f = (a-b)\/a ≈ 1\/299$ · полюс ближе на ≈21 км])
})
