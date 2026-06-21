#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Теневая цена: +1 единица дефицитного ресурса раздвигает границу, оптимум растёт на λ.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  line((0, 0), (4.4, 0), mark: (end: ">", fill: INK))
  line((0, 0), (0, 3.6), mark: (end: ">", fill: INK))
  content((4.4, -0.3), anchor: "east", text(size: 9pt, fill: OLIVE)[$x_1$])
  content((0.2, 3.6), anchor: "west", text(size: 9pt, fill: OLIVE)[$x_2$])

  // исходная область
  let V = ((0, 0), (3.0, 0), (2.4, 1.6), (0, 2.2))
  line(..V, close: true, fill: SAND.lighten(52%), stroke: (paint: OLIVE.lighten(10%), thickness: 1pt))
  circle((2.4, 1.6), radius: 0.09, fill: OLIVE, stroke: none)

  // расширение: ограничение сдвинуто наружу (пунктир) → новая вершина
  line((0, 2.7), (3.5, 0), stroke: (paint: INK, thickness: 0.9pt, dash: "dashed"))
  circle((2.85, 1.95), radius: 0.10, fill: INK, stroke: (paint: OLIVE, thickness: 0.6pt))
  line((2.4, 1.6), (2.85, 1.95), mark: (end: ">", fill: INK), stroke: (thickness: 0.8pt))
  content((2.95, 1.95), anchor: "west", text(size: 8pt)[новый оптимум])

  content((0.2, 2.95), anchor: "west", text(size: 8pt, fill: OLIVE)[+1 ресурса])
  content((1.4, -0.95), text(size: 9.5pt)[прибыль выросла на $lambda$ — это и есть цена ресурса])
})
