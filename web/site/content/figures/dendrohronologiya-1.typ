#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Годичные кольца: чередование широких (тёплый год) и узких (засуха).
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: 0.7pt))

  // радиусы колец с разными промежутками (широкие/узкие)
  let radii = (0.25, 0.40, 0.72, 0.86, 1.18, 1.32, 1.46, 1.78, 1.92, 2.24)
  for r in radii { circle((0, 0), radius: r) }
  circle((0, 0), radius: 0.08, fill: INK, stroke: none)   // сердцевина

  // указатель на широкое кольцо
  line((2.4, 1.3), (1.55, 0.85), mark: (end: ">", fill: OLIVE), stroke: (paint: OLIVE, thickness: 0.8pt))
  content((2.45, 1.4), anchor: "west", text(size: 8pt, fill: OLIVE)[широкое — тёплый влажный год])
  // указатель на узкое кольцо
  line((2.4, -1.3), (1.85, -0.9), mark: (end: ">", fill: OLIVE), stroke: (paint: OLIVE, thickness: 0.8pt))
  content((2.45, -1.4), anchor: "west", text(size: 8pt, fill: OLIVE)[узкое — засуха или холод])
})
