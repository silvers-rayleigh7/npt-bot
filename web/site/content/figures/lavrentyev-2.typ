#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Течение как линии тока ψ=const; свободная граница струи — одна из линий тока.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let ax = 1.6
  // внутренние линии тока (сходятся к струе)
  bezier((0, ax + 0.3), (6.2, ax + 0.07), (3.0, ax + 0.18), stroke: (paint: OLIVE.lighten(15%), thickness: 0.8pt))
  bezier((0, ax - 0.3), (6.2, ax - 0.07), (3.0, ax - 0.18), stroke: (paint: OLIVE.lighten(15%), thickness: 0.8pt))
  line((0, ax), (6.4, ax), stroke: (paint: OLIVE.lighten(35%), thickness: 0.7pt, dash: "dotted"))   // ось

  // свободная граница струи — выделенная линия тока ψ=const
  bezier((0, ax + 1.1), (6.2, ax + 0.16), (2.6, ax + 0.9), stroke: (paint: INK, thickness: 1.6pt))
  bezier((0, ax - 1.1), (6.2, ax - 0.16), (2.6, ax - 0.9), stroke: (paint: INK, thickness: 1.6pt))
  content((6.5, ax + 0.16), anchor: "west", text(size: 8pt)[граница струи\ $psi = $const])

  // стрелки направления течения
  for y in (ax + 0.55, ax - 0.55) { line((2.8, y), (3.5, y - 0.04 * (y - ax) / 0.55 * 5), mark: (end: ">", fill: INK), stroke: (thickness: 0.7pt)) }
  content((1.2, ax + 1.35), text(size: 8.5pt, fill: OLIVE)[линии тока $psi = $const])
})
