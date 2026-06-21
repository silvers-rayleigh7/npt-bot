#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Лес связывает углерод не только в стволах: до половины — в корнях, подстилке и почве.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // линия земли
  let g = 0.0
  rect((-0.5, -1.6), (5.5, g), fill: SAND.darken(8%), stroke: none)   // почва
  line((-0.5, g), (5.5, g), stroke: (paint: INK, thickness: 1pt))

  // дерево
  line((2.5, g), (2.5, 2.4), stroke: (thickness: 2pt))                 // ствол
  for (cy, w) in ((1.4, 1.0), (1.9, 0.75), (2.3, 0.5)) {
    line((2.5 - w, cy), (2.5, cy + 0.5), (2.5 + w, cy))
  }
  // корни
  line((2.5, g), (1.7, -1.2)); line((2.5, g), (3.3, -1.2)); line((2.5, g), (2.5, -1.3))

  // CO2 in
  line((0.6, 2.6), (1.6, 2.0), mark: (end: ">", fill: OLIVE), stroke: (paint: OLIVE, thickness: 0.9pt))
  content((0.4, 2.75), anchor: "east", text(size: 8.5pt, fill: OLIVE)[CO₂])

  // подписи запасов углерода
  content((3.6, 1.7), anchor: "west", text(size: 8pt)[углерод в древесине])
  content((3.6, -0.7), anchor: "west", text(size: 8pt, fill: white)[корни])
  content((-0.4, -0.8), anchor: "west", text(size: 8.5pt, fill: white)[почва и подстилка])
  content((2.5, -1.95), text(size: 9pt, fill: OLIVE)[до половины углерода — в почве, а не в стволах])
})
