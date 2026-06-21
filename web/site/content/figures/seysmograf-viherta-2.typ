#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Разрез Земли: жидкое внешнее ядро гасит S-волны → теневая зона дальше ~103°. P-волны преломляются.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let O = (0, 0)
  let R = 2.6      // радиус Земли
  let Rc = 1.45    // радиус ядра

  // мантия, ядро
  circle(O, radius: R, fill: SAND.lighten(45%), stroke: INK)
  circle(O, radius: Rc, fill: OLIVE.lighten(15%), stroke: INK)
  circle(O, radius: 0.55, fill: OLIVE.darken(15%), stroke: INK)
  content((0, -1.0), text(size: 8pt, fill: white)[ядро (жидкое)])
  content((0, 1.95), text(size: 8pt)[мантия])

  // очаг наверху
  let Q = (0, R)
  circle(Q, radius: 0.10, fill: INK, stroke: none)
  content((0, R + 0.32), text(size: 8.5pt, fill: OLIVE)[очаг])

  // P-волны: лучи в мантии, доходят до дальней стороны (огибают/преломляются)
  for ang in (200, 235, 305, 340) {
    let r = ang * 3.14159 / 180
    line(Q, (R * calc.cos(r), R * calc.sin(r)), stroke: (paint: INK, thickness: 0.7pt))
  }
  content((-R - 0.2, -1.4), anchor: "east", text(size: 8pt)[P-волны проходят])

  // S-волны: гаснут на ядре (рисуем до границы ядра, штрих)
  for ang in (250, 290) {
    let r = ang * 3.14159 / 180
    line(Q, (Rc * calc.cos(r) * 1.05, Rc * calc.sin(r) * 1.05), stroke: (paint: INK, thickness: 0.9pt, dash: "dashed"))
  }

  // теневая зона S-волн снизу (дуга, оливой)
  arc(O, start: 245deg, stop: 295deg, radius: R + 0.18, stroke: (paint: OLIVE, thickness: 1.6pt))
  content((0, -R - 0.55), text(size: 8pt, fill: OLIVE)[теневая зона S-волн])
})
