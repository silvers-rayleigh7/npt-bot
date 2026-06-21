#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Ступенька Хевисайда H(x) → её обобщённая производная — дельта Дирака.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // ── левый график: H(x)
  line((-1.4, 0), (1.6, 0), mark: (end: ">", fill: INK))    // ось x
  line((0, -0.3), (0, 1.9), mark: (end: ">", fill: INK))    // ось y
  line((-1.3, 0), (0, 0), stroke: (paint: INK, thickness: 1.6pt))
  line((0, 1.2), (1.4, 1.2), stroke: (paint: INK, thickness: 1.6pt))
  line((0, 0), (0, 1.2), stroke: (paint: INK, thickness: 1.6pt, dash: "dotted"))
  content((-0.18, 1.2), anchor: "east", text(size: 8pt)[1])
  content((0.9, 1.5), text(size: 9pt)[$H(x)$])

  // стрелка «производная»
  line((2.0, 0.8), (3.2, 0.8), mark: (end: ">", fill: INK))
  content((2.6, 1.1), text(size: 8.5pt, fill: OLIVE)[$H' = delta$])

  // ── правый график: дельта-импульс
  let ox = 5.0
  line((ox - 1.4, 0), (ox + 1.6, 0), mark: (end: ">", fill: INK))
  line((ox, -0.3), (ox, 1.9), mark: (end: ">", fill: INK))
  line((ox, 0), (ox, 1.55), stroke: (paint: OLIVE, thickness: 2pt), mark: (end: ">", fill: OLIVE))
  content((ox + 0.2, 1.5), anchor: "west", text(size: 9pt, fill: OLIVE)[$delta(x)$])
  content((ox, -0.32), text(size: 8pt)[0])
})
