#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Три способа переноса песка: крип (катится), сальтация (скачет), взвесь (летит).
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // земля
  line((0, 0), (8.2, 0), stroke: (paint: INK, thickness: 1pt))
  // ветер
  line((0.2, 2.6), (1.7, 2.6), mark: (end: ">", fill: INK))
  content((0.95, 2.85), text(size: 9pt, fill: OLIVE)[ветер])

  // крип — зерно катится по земле
  circle((1.2, 0.16), radius: 0.13, fill: SAND, stroke: INK)
  line((1.5, 0.16), (2.1, 0.16), mark: (end: ">", fill: INK), stroke: (thickness: 0.8pt))
  content((1.5, -0.4), text(size: 8.5pt)[крип · ползёт])

  // сальтация — скачки дугами
  let hop(x0, x1, h) = bezier((x0, 0), (x1, 0), ((x0 + x1) / 2, h), stroke: (paint: OLIVE, thickness: 1.1pt))
  hop(3.0, 4.0, 0.8); hop(4.0, 5.1, 0.95); hop(5.1, 6.3, 1.05)
  for px in (4.0, 5.1) { circle((px, 0.06), radius: 0.10, fill: SUN, stroke: none) }
  content((4.6, -0.4), text(size: 8.5pt, fill: OLIVE)[сальтация · скачет])

  // взвесь — мелкая пыль уносится вверх
  for (px, py) in ((6.8, 0.9), (7.2, 1.5), (7.6, 2.1), (7.9, 2.6)) { circle((px, py), radius: 0.05, fill: SAND, stroke: none) }
  content((7.3, -0.4), text(size: 8.5pt)[взвесь · летит])
})
