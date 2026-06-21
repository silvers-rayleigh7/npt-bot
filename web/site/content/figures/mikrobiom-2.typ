#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Горизонтальный перенос гена: морская бактерия → ген расщепления порфирана → кишечная бактерия.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // морская бактерия (на водоросли)
  circle((1.0, 1.6), radius: 0.55, fill: OLIVE.lighten(25%), stroke: INK)
  content((1.0, 1.6), text(size: 7.5pt, fill: white)[морская\ бактерия])
  content((1.0, 0.7), text(size: 7.5pt, fill: OLIVE)[на нори])
  // ген (маленький овал)
  circle((1.0, 1.6), radius: 0.13, fill: SUN, stroke: INK)

  // перенос гена
  line((1.65, 1.5), (4.0, 1.5), mark: (end: ">", fill: INK), stroke: (thickness: 1pt))
  content((2.8, 1.85), text(size: 8pt, fill: OLIVE)[перенос гена])
  circle((2.8, 1.5), radius: 0.10, fill: SUN, stroke: INK)

  // кишечная бактерия
  circle((5.0, 1.5), radius: 0.6, fill: SAND.darken(8%), stroke: INK)
  content((5.0, 1.5), text(size: 7pt, fill: white)[Bacteroides\ plebeius])
  circle((5.0, 1.5), radius: 0.13, fill: SUN, stroke: INK)
  content((5.0, 0.6), text(size: 7.5pt)[в кишечнике человека])

  // итог
  line((5.7, 1.5), (6.7, 1.5), mark: (end: ">", fill: INK))
  content((6.85, 1.5), anchor: "west", text(size: 8.5pt)[переваривает\ порфиран])
})
