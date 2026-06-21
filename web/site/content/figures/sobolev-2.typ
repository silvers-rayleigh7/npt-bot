#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Метод конечных элементов: область (с углом) разбита на треугольники.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: OLIVE, thickness: 0.8pt))

  // L-образная область, залитая, с контуром
  let outline = ((0, 0), (4, 0), (4, 1.6), (2, 1.6), (2, 3), (0, 3))
  line(..outline, close: true, fill: SAND.lighten(52%), stroke: (paint: INK, thickness: 1.2pt))

  // узлы сетки
  let nodes = (
    (0,0),(1,0),(2,0),(3,0),(4,0),
    (0,1),(1,1),(2,1),(3,1),(4,1),
    (0,2),(1,2),(2,2),
    (0,3),(1,3),(2,3),
  )
  // рёбра треугольной сетки (горизонтали, вертикали, диагонали) — вручную, чтобы не вылезать за угол
  let seg(a, b) = line(a, b, stroke: (paint: OLIVE, thickness: 0.7pt))
  // нижняя полоса 0..1
  for x in (0,1,2,3) { seg((x,0),(x+1,0)); seg((x,1),(x+1,1)); seg((x,0),(x,1)); seg((x,0),(x+1,1)) }
  seg((4,0),(4,1))
  // верхняя левая часть 1..3 (только x≤2)
  for x in (0,1) { seg((x,1),(x+1,1)); seg((x,2),(x+1,2)); seg((x,3),(x+1,3)) }
  for x in (0,1,2) { seg((x,1),(x,2)) }
  for x in (0,1) { seg((x,2),(x,3)); seg((x,1),(x+1,2)); seg((x,2),(x+1,3)) }

  // узлы поверх
  for n in nodes { circle(n, radius: 0.05, fill: INK, stroke: none) }

  content((5.0, 1.5), anchor: "west", text(size: 9pt, fill: INK)[конечные\ элементы])
})
