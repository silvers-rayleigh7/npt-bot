#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Допустимый многоугольник ограничений; целевая прямая упирается в вершину = оптимум.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // оси
  line((0, 0), (4.4, 0), mark: (end: ">", fill: INK))
  line((0, 0), (0, 3.4), mark: (end: ">", fill: INK))
  content((4.4, -0.3), anchor: "east", text(size: 9pt, fill: OLIVE)[$x_1$])
  content((0.2, 3.4), anchor: "west", text(size: 9pt, fill: OLIVE)[$x_2$])

  // допустимая область (выпуклый многоугольник)
  let V = ((0, 0), (3.2, 0), (2.6, 1.7), (0, 2.4))
  line(..V, close: true, fill: SAND.lighten(50%), stroke: (paint: OLIVE, thickness: 1pt))
  // продолжения двух ограничений (тонко)
  line((3.2, 0), (3.9, -0.0)); // нижняя на оси
  content((1.4, 0.7), text(size: 8.5pt)[допустимые планы])

  // целевая прямая (пунктир) и направление роста ценности c
  line((3.5, 0.4), (1.2, 2.9), stroke: (paint: INK, thickness: 0.8pt, dash: "dashed"))
  line((1.8, 1.5), (2.6, 2.1), mark: (end: ">", fill: INK), stroke: (thickness: 1pt))
  content((2.7, 2.15), anchor: "west", text(size: 8pt, fill: OLIVE)[рост $c^T x$])

  // оптимум — вершина
  circle((2.6, 1.7), radius: 0.10, fill: OLIVE, stroke: (paint: INK, thickness: 0.6pt))
  content((2.75, 1.6), anchor: "west", text(size: 8.5pt, fill: OLIVE)[оптимум])
})
