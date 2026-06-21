#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Путь янтаря: смола капает в лесу → река сносит в море → оседает в «голубой земле».
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // ── 1. дерево со смолой
  line((1.0, 0.0), (1.0, 1.6))                         // ствол
  for (cy, w) in ((1.4, 0.9), (2.0, 0.7), (2.5, 0.5)) {
    line((1.0 - w, cy), (1.0, cy + 0.55), (1.0 + w, cy)) // ярус хвои
  }
  circle((1.35, 1.1), radius: 0.10, fill: SUN, stroke: none)   // капля смолы
  circle((1.4, 0.55), radius: 0.08, fill: SUN, stroke: none)
  content((1.0, -0.4), text(size: 8.5pt)[смола в лесу])

  line((2.5, 1.2), (3.4, 1.2), mark: (end: ">", fill: INK))

  // ── 2. река/море
  for y in (0.7, 1.1, 1.5) {
    line((3.7, y), (4.1, y + 0.18), (4.5, y), (4.9, y + 0.18), (5.3, y),
         stroke: (paint: OLIVE, thickness: 1pt))
  }
  circle((4.5, 1.3), radius: 0.10, fill: SUN, stroke: none)
  content((4.5, -0.4), text(size: 8.5pt)[река сносит в море])

  line((5.5, 1.2), (6.4, 1.2), mark: (end: ">", fill: INK))

  // ── 3. разрез: песок над «голубой землёй» с янтарём
  rect((6.7, 1.3), (9.2, 2.0), fill: SAND.lighten(40%));  content((7.95, 1.65), text(size: 8pt)[песок])
  rect((6.7, 0.4), (9.2, 1.3), fill: OLIVE.lighten(20%))
  content((7.95, 0.9), text(size: 8pt, fill: white)[голубая земля])
  for px in (7.2, 8.0, 8.7) { circle((px, 0.7), radius: 0.11, fill: SUN, stroke: (paint: INK, thickness: 0.5pt)) }
  content((7.95, -0.4), text(size: 8.5pt)[оседает янтарём])
})
