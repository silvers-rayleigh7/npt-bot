#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Теорема Минковского: симметричная выпуклая область объёмом > 2ⁿ накрывает узел решётки.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // целочисленная решётка
  for i in range(-2, 3) {
    for j in range(-2, 3) {
      circle((i, j), radius: 0.05, fill: SAND.darken(5%), stroke: none)
    }
  }
  // начало координат
  circle((0, 0), radius: 0.08, fill: INK, stroke: none)
  content((0.0, -0.35), text(size: 7.5pt)[0])

  // симметричная выпуклая область (эллипс) вокруг 0, достаточно большая
  group({ translate((0, 0)); scale(x: 130%, y: 78%); circle((0, 0), radius: 1.55, stroke: (paint: OLIVE, thickness: 1.4pt)) })

  // накрытый ненулевой узел
  circle((1, 1), radius: 0.11, fill: OLIVE, stroke: (paint: INK, thickness: 0.6pt))
  content((1.2, 1.15), anchor: "west", text(size: 8pt, fill: OLIVE)[узел решётки])

  content((0, -2.7), text(size: 9.5pt)[объём $V > 2^n$ → внутри есть ненулевой узел])
})
