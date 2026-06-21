#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// L1: сам валун. Полуденное солнце стоит на юге → южная грань встречает лучи
// круто и нагревается, северная — лишь вскользь, остаётся холодной. Абстрактно:
// круг-валун, солнце справа-сверху (юг), тёплая дуга справа, холодная слева.
// (L2 отдельно объясняет ПОЧЕМУ — через угол и площадь; здесь — сама сцена.)
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let O = (0, 0)
  let r = 1.4

  // ── тёплая (южная, правая) дуга — толстая, цвет солнца
  arc(O, start: -70deg, stop: 70deg, radius: r,
      anchor: "origin", stroke: (paint: SUN.darken(5%), thickness: 2.6pt))
  // ── холодная (северная, левая) дуга — тонкая, олива
  arc(O, start: 110deg, stop: 250deg, radius: r,
      anchor: "origin", stroke: (paint: OLIVE, thickness: 1.4pt))
  // замкнуть верх/низ нейтральным штрихом
  arc(O, start: 70deg, stop: 110deg, radius: r, anchor: "origin", stroke: (paint: INK, thickness: LINE))
  arc(O, start: 250deg, stop: 290deg, radius: r, anchor: "origin", stroke: (paint: INK, thickness: LINE))
  content((0, 0), text(size: 9pt, fill: SAND.darken(25%))[валун])

  // ── солнце справа-сверху (юг, полдень) + параллельные лучи на южную грань
  let sun = (3.6, 2.5)
  content(sun, image("icons/sun.svg", width: 0.62cm))
  let dir = (-0.74, -0.67)            // направление лучей (к валуну, вниз-влево)
  for t in (-0.7, 0.0, 0.7) {
    // стартовые точки лучей, разнесённые поперёк
    let sx = 2.5 + t * 0.6
    let sy = 2.3 - t * 0.66
    let ex = sx + dir.at(0) * 1.15
    let ey = sy + dir.at(1) * 1.15
    line((sx, sy), (ex, ey), stroke: (paint: SUN.darken(10%), thickness: 0.9pt),
         mark: (end: ">", fill: SUN.darken(10%), scale: 0.45))
  }

  // ── подписи граней
  content((r + 0.35, 0.15), anchor: "west", text(size: 9pt, fill: SUN.darken(20%))[южная грань\
теплее])
  content((-r - 0.35, 0.15), anchor: "east", text(size: 9pt, fill: OLIVE)[северная\
холоднее])

  // ── итог
  content((0, -2.05), text(size: 9.5pt)[полуденное солнце стоит на юге: южная грань ловит его круто, северная — вскользь])
})
