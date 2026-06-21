#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Обрыв мыса Таран: слоистые отложения с валунами, волны бьют в подножие, берег отступает.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // тело обрыва (слева), вертикальный срез у воды на x=3.4
  // слои снизу вверх: глина · песок · почва
  rect((0, 0), (3.4, 0.8), fill: OLIVE.lighten(20%));   content((1.0, 0.4), text(size: 8pt, fill: white)[глина])
  rect((0, 0.8), (3.4, 2.4), fill: SAND.lighten(35%));  content((1.0, 1.6), text(size: 8pt)[песок])
  rect((0, 2.4), (3.4, 2.8), fill: INK.lighten(30%))
  // валуны в толще и у подножия
  for (px, py) in ((1.6, 1.3), (2.4, 1.1), (3.0, 0.45), (3.9, 0.25), (4.5, 0.2)) {
    circle((px, py), radius: 0.18, fill: SAND.darken(15%), stroke: INK)
  }

  // море справа
  rect((3.4, 0), (6.2, 0.5), stroke: none, fill: OLIVE.lighten(58%))
  for y in (0.18, 0.4) { line((3.5, y), (4.0, y + 0.1), (4.5, y), (5.0, y + 0.1), (5.5, y), stroke: (paint: OLIVE, thickness: 0.8pt)) }
  // волна бьёт в подножие
  line((4.3, 0.55), (3.5, 0.55), mark: (end: ">", fill: INK), stroke: (thickness: 1.2pt))
  content((4.9, 0.75), text(size: 8pt, fill: OLIVE)[волна подмывает])

  // отступание берега
  line((2.9, 3.15), (2.0, 3.15), mark: (end: ">", fill: OLIVE), stroke: (paint: OLIVE, dash: "dashed"))
  content((3.0, 3.15), anchor: "west", text(size: 8.5pt, fill: OLIVE)[обрыв отступает])
})
