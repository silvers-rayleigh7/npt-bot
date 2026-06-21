#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Годовой ход T: приморский климат (малая амплитуда) vs резкоконтинентальный (огромный размах).
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let W = 6.0; let mid = 1.5
  // ось времени и нулевая линия
  line((0, mid), (W + 0.3, mid), mark: (end: ">", fill: INK))
  content((W + 0.3, mid - 0.3), anchor: "east", text(size: 8pt, fill: OLIVE)[месяцы])
  line((0, -0.6), (0, 3.3), mark: (end: ">", fill: INK))
  content((-0.15, 3.3), anchor: "west", text(size: 8pt, fill: OLIVE)[T])
  content((-0.15, mid), anchor: "east", text(size: 7.5pt)[0])

  // приморский — малая амплитуда
  let coast = ()
  for i in range(0, 49) { let x = i / 8; coast.push((x, mid + 0.4 * calc.sin(x * 0.52 - 1.4))) }
  line(..coast, stroke: (paint: OLIVE, thickness: 1.2pt))
  content((W - 0.1, mid + 0.6), anchor: "east", text(size: 8pt, fill: OLIVE)[у моря])

  // континентальный — огромный размах
  let cont = ()
  for i in range(0, 49) { let x = i / 8; cont.push((x, mid + 1.55 * calc.sin(x * 0.52 - 1.4))) }
  line(..cont, stroke: (paint: INK, thickness: 1.4pt))
  content((3.0, mid + 1.85), text(size: 8pt)[+35])
  content((3.0, mid - 1.9), text(size: 8pt)[−50])
  content((W - 0.1, mid - 1.0), anchor: "east", text(size: 8pt)[Якутия])
})
