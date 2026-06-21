#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Момент импульса L=mvr=const: радиус падает вдвое → скорость растёт вдвое.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // большая орбита (медленно)
  circle((0, 0), radius: 1.7, stroke: (paint: OLIVE.lighten(20%), thickness: 0.8pt))
  circle((0, 0), radius: 0.12, fill: SUN, stroke: none)
  circle((1.7, 0), radius: 0.16, fill: SAND.darken(10%), stroke: INK)
  line((1.7, 0.25), (1.7, 0.95), mark: (end: ">", fill: INK), stroke: (thickness: 0.9pt))
  content((1.85, 0.7), anchor: "west", text(size: 8.5pt, fill: OLIVE)[$v$])
  line((0, 0), (1.7, 0), stroke: (thickness: 0.6pt)); content((0.85, -0.28), text(size: 8.5pt)[$r$])

  // стрелка коллапса
  line((2.6, 0), (3.6, 0), mark: (end: ">", fill: INK))
  content((3.1, 0.3), text(size: 8pt, fill: OLIVE)[сжатие])

  // малая орбита (быстро)
  let cx = 5.8
  circle((cx, 0), radius: 0.85, stroke: (paint: OLIVE.lighten(20%), thickness: 0.8pt))
  circle((cx, 0), radius: 0.12, fill: SUN, stroke: none)
  circle((cx + 0.85, 0), radius: 0.16, fill: SAND.darken(10%), stroke: INK)
  line((cx + 0.85, 0.25), (cx + 0.85, 1.65), mark: (end: ">", fill: INK), stroke: (thickness: 0.9pt))
  content((cx + 1.0, 1.1), anchor: "west", text(size: 8.5pt, fill: OLIVE)[$2v$])
  line((cx, 0), (cx + 0.85, 0), stroke: (thickness: 0.6pt)); content((cx + 0.42, -0.28), text(size: 8.5pt)[$r\/2$])

  content((2.9, -1.9), text(size: 10pt)[$L = m v r = $ const #h(0.3cm) → #h(0.2cm) $r↓$ → $v↑$])
})
