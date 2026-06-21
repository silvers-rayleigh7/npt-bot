#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Облако → сжатие и раскрутка → плоский диск со звездой в центре.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // 1. рыхлое облако
  circle((1.2, 1.4), radius: 1.0, stroke: (paint: OLIVE, dash: "dashed"))
  for (dx, dy) in ((-0.4, 0.3), (0.3, 0.5), (0.5, -0.3), (-0.3, -0.4), (0.0, 0.1), (-0.6, 0.0), (0.2, -0.6)) {
    circle((1.2 + dx, 1.4 + dy), radius: 0.05, fill: SAND.darken(10%), stroke: none)
  }
  arc((1.2, 2.5), start: 60deg, stop: 140deg, radius: 0.5, mark: (end: ">", fill: OLIVE), stroke: OLIVE)
  content((1.2, -0.05), text(size: 8.5pt)[облако])

  line((2.5, 1.4), (3.4, 1.4), mark: (end: ">", fill: INK))

  // 2. сжимается, раскручивается
  circle((4.4, 1.4), radius: 0.55, stroke: (paint: OLIVE, dash: "dashed"))
  for a in (20, 110, 200, 290) { let r = a * 3.14159 / 180
    line((4.4 + 0.85 * calc.cos(r), 1.4 + 0.85 * calc.sin(r)), (4.4 + 0.6 * calc.cos(r), 1.4 + 0.6 * calc.sin(r)), mark: (end: ">", fill: INK), stroke: (thickness: 0.7pt)) }
  arc((4.4, 2.15), start: 60deg, stop: 160deg, radius: 0.42, mark: (end: ">", fill: OLIVE), stroke: (paint: OLIVE, thickness: 1pt))
  content((4.4, -0.05), text(size: 8.5pt)[сжимается])

  line((5.5, 1.4), (6.4, 1.4), mark: (end: ">", fill: INK))

  // 3. диск со звездой
  // диск (эллипс) — рисуем как сплюснутую окружность через scale
  group({
    translate((8.0, 1.4)); scale(x: 100%, y: 32%)
    circle((0, 0), radius: 1.3, stroke: (paint: OLIVE, thickness: 1pt))
    circle((0, 0), radius: 0.85, stroke: (paint: OLIVE.lighten(30%), thickness: 0.6pt))
  })
  circle((8.0, 1.4), radius: 0.22, fill: SUN, stroke: none)        // звезда
  circle((8.0 + 1.3, 1.4), radius: 0.07, fill: INK, stroke: none)  // планета
  content((8.0, -0.05), text(size: 8.5pt)[диск + звезда])
})
