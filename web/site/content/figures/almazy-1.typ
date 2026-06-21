#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Один углерод — две решётки: графит (скользящие слои) vs алмаз (жёсткий каркас).
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // ── графит: горизонтальные слои
  let atom(p) = circle(p, radius: 0.10, fill: INK, stroke: none)
  for row in (0.3, 1.0, 1.7) {
    line((0, row), (2.6, row), stroke: (paint: OLIVE, thickness: 0.8pt))
    for x in (0.2, 0.7, 1.2, 1.7, 2.2) { atom((x, row)) }
  }
  content((1.3, -0.3), text(size: 8.5pt)[графит: скользящие слои])

  // ── алмаз: тетраэдрический каркас (узлы + связи)
  let cx = 5.2
  let nodes = ((cx, 1.6), (cx - 0.8, 0.9), (cx + 0.8, 0.9), (cx, 0.4), (cx - 0.8, 1.8), (cx + 0.8, 1.8), (cx, 1.0))
  // связи
  let bonds = ((0,6),(1,6),(2,6),(3,6),(0,4),(0,5),(1,3),(2,3))
  for (a, b) in bonds { line(nodes.at(a), nodes.at(b), stroke: (paint: OLIVE, thickness: 0.8pt)) }
  for n in nodes { atom(n) }
  content((cx, -0.3), text(size: 8.5pt)[алмаз: жёсткий 3D-каркас])
})
