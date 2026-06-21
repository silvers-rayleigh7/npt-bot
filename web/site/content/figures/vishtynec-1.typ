#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Летняя стратификация: тёплый эпилимнион, резкий термоклин, холодный гиполимнион.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let X0 = 0; let X1 = 5.0
  // солнце
  circle((0.5, 3.6), radius: 0.22, fill: SUN, stroke: none)
  for a in (0, 45, 90, 135, 180, 225, 270, 315) {
    let r = a * 3.14159 / 180
    line((0.5 + 0.3 * calc.cos(r), 3.6 + 0.3 * calc.sin(r)), (0.5 + 0.45 * calc.cos(r), 3.6 + 0.45 * calc.sin(r)), stroke: (paint: SUN, thickness: 0.8pt))
  }
  // ветер на поверхности
  line((1.4, 3.5), (2.6, 3.5), mark: (end: ">", fill: INK), stroke: (thickness: 0.8pt))
  content((2.0, 3.72), text(size: 7.5pt, fill: OLIVE)[ветер])

  // слои (сверху вниз)
  rect((X0, 2.2), (X1, 3.3), fill: SAND.lighten(45%));  // эпилимнион
  rect((X0, 1.8), (X1, 2.2), fill: OLIVE.lighten(35%)); // термоклин
  rect((X0, 0.0), (X1, 1.8), fill: OLIVE.lighten(8%));  // гиполимнион
  rect((X0, 0.0), (X1, 3.3), stroke: INK)               // рамка водоёма

  content((X1 + 0.3, 2.75), anchor: "west", text(size: 9pt)[эпилимнион · 18–22 °C])
  content((X1 + 0.3, 2.0), anchor: "west", text(size: 9pt, fill: OLIVE)[термоклин · −1 °C\/м])
  content((X1 + 0.3, 0.9), anchor: "west", text(size: 9pt, fill: INK)[гиполимнион · 4–6 °C])
})
