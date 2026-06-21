#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Неустойчивость: почти нулевые данные → неограниченно растущее решение.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // левый график: данные — крошечная волна
  line((0, 0), (3.0, 0), stroke: (paint: INK, thickness: 0.8pt))
  let d = ()
  for i in range(0, 31) { let x = i / 10; d.push((x, 0.18 * calc.sin(6 * x))) }
  line(..d, stroke: (paint: INK, thickness: 1pt))
  content((1.5, 0.7), text(size: 8.5pt)[данные $~1\/n → 0$])

  // стрелка
  line((3.4, 0), (4.6, 0), mark: (end: ">", fill: INK))
  content((4.0, 0.35), text(size: 8pt, fill: OLIVE)[обратить])

  // правый график: решение — взрывной рост
  let ox = 5.2
  line((ox, -1.6), (ox, 1.9), stroke: (paint: INK, thickness: 0.8pt))
  line((ox, 0), (ox + 3.2, 0), stroke: (paint: INK, thickness: 0.8pt))
  let s = ()
  for i in range(0, 33) { let x = i / 10; s.push((ox + x, 1.7 * calc.sin(6 * x) * calc.exp(0.5 * x) / calc.exp(1.6))) }
  line(..s, stroke: (paint: OLIVE, thickness: 1.2pt))
  content((ox + 1.7, 1.75), text(size: 8.5pt, fill: OLIVE)[решение $→ ∞$])
})
