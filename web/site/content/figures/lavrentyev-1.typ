#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Кумулятивный заряд: коническая облицовка схлопывается к оси → тонкая струя вперёд.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let ax = 1.6   // ось (y)
  // корпус заряда (взрывчатка)
  rect((0, 0.3), (2.6, 2.9), fill: SAND.lighten(40%), stroke: INK)
  content((1.0, 2.6), text(size: 8pt)[заряд])
  // детонация сзади
  for y in (0.8, 1.6, 2.4) { line((-0.6, y), (-0.05, y), mark: (end: ">", fill: INK), stroke: (thickness: 0.8pt)) }
  content((-0.6, 0.1), anchor: "west", text(size: 7.5pt, fill: OLIVE)[детонация])
  // коническая облицовка (V, вершина к оси справа)
  line((2.6, 0.5), (3.5, ax), stroke: (paint: INK, thickness: 1.8pt))
  line((2.6, 2.7), (3.5, ax), stroke: (paint: INK, thickness: 1.8pt))
  content((2.55, ax), anchor: "east", text(size: 7.5pt, fill: OLIVE)[облицовка])
  // схлопывание к оси
  line((3.0, 0.75), (3.3, ax - 0.05), mark: (end: ">", fill: OLIVE), stroke: (paint: OLIVE, thickness: 0.8pt))
  line((3.0, 2.45), (3.3, ax + 0.05), mark: (end: ">", fill: OLIVE), stroke: (paint: OLIVE, thickness: 0.8pt))
  // кумулятивная струя вперёд
  line((3.5, ax - 0.06), (6.3, ax - 0.02), (6.3, ax + 0.02), (3.5, ax + 0.06), close: true, fill: OLIVE, stroke: none)
  line((6.3, ax), (6.7, ax), mark: (end: ">", fill: INK), stroke: (thickness: 1pt))
  content((5.0, ax + 0.35), text(size: 8.5pt, fill: OLIVE)[кумулятивная струя ~10 км/с])
})
