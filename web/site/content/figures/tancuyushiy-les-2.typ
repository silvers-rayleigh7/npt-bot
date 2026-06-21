#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Жёсткость ствола ∝ d⁴: тонкий гнётся сильно, толстый почти не гнётся.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // ветер
  line((0.2, 3.3), (1.5, 3.3), mark: (end: ">", fill: INK))
  content((0.85, 3.55), text(size: 8.5pt, fill: OLIVE)[ветер])

  // тонкий ствол — сильно гнётся
  bezier((1.0, 0), (2.4, 2.8), (1.0, 1.6), stroke: (thickness: 1.2pt))
  line((0.85, 0), (1.15, 0))
  content((1.0, -0.4), text(size: 8.5pt)[тонкий $d$])
  content((2.5, 2.6), anchor: "west", text(size: 8pt, fill: OLIVE)[большой прогиб $delta$])

  // толстый ствол — почти прямой
  line((5.0, 0), (5.2, 2.8), stroke: (thickness: 3pt))
  content((5.1, -0.4), text(size: 8.5pt)[толстый $2d$])
  content((5.4, 2.4), anchor: "west", text(size: 8pt, fill: OLIVE)[прогиб в 16 раз меньше])

  // вывод
  content((3.1, -1.1), text(size: 10pt)[$I = pi d^4 \/ 64$, #h(0.2cm) $d times 2 →$ жёсткость $times 16$])
})
