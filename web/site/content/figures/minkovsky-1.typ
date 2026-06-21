#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Диаграмма Минковского: оси ct и x, световой конус 45°, области причинности.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let R = 2.5
  // оси
  line((0, -R - 0.3), (0, R + 0.4), mark: (end: ">", fill: INK))
  line((-R - 0.3, 0), (R + 0.4, 0), mark: (end: ">", fill: INK))
  content((0.25, R + 0.4), anchor: "west", text(size: 9pt, fill: OLIVE)[$c t$])
  content((R + 0.4, -0.3), anchor: "east", text(size: 9pt, fill: OLIVE)[$x$])

  // световой конус (45°), залит слегка
  line((0, 0), (R, R), (-R, R), close: true, fill: SAND.lighten(55%), stroke: (paint: OLIVE, thickness: 1pt))
  line((0, 0), (R, -R), (-R, -R), close: true, fill: SAND.lighten(55%), stroke: (paint: OLIVE, thickness: 1pt))

  content((0, 1.9), text(size: 8.5pt)[будущее])
  content((0, -1.9), text(size: 8.5pt)[прошлое])
  content((1.85, 0.32), text(size: 8pt, fill: OLIVE)[«где-то»])
  content((-1.85, 0.32), text(size: 8pt, fill: OLIVE)[«где-то»])

  // мировая линия (внутри конуса — достижимо)
  line((0, 0), (0.7, 2.2), stroke: (paint: INK, thickness: 1.4pt))
  circle((0.7, 2.2), radius: 0.07, fill: INK, stroke: none)
  content((0.85, 2.2), anchor: "west", text(size: 7.5pt)[достижимо])
  // событие снаружи — недостижимо
  circle((2.2, 0.6), radius: 0.07, fill: OLIVE, stroke: none)
  content((2.35, 0.6), anchor: "west", text(size: 7.5pt, fill: OLIVE)[недостижимо])
})
