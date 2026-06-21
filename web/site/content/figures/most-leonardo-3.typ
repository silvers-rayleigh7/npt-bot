#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// L3: вторая дорога к арке без растяжений — цепная линия (катенария). Гибкая
// цепь под своим весом висит кривой, где каждое звено только РАСТЯГИВается вдоль
// нити. Переверни эту кривую — получится арка, где каждый элемент только СЖИМАЕТ
// (камень/бетон любят сжатие). Слева висячая цепь, справа перевёрнутая = арка.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // точки катенарии y = a*cosh(x/a), x∈[-1.4,1.4], нормируем к высоте ~1.7
  let a = 1.0
  let xs = (-1.4, -1.2, -1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0, 1.2, 1.4)
  let y0 = a * calc.cosh(0 / a)
  let ymax = a * calc.cosh(1.4 / a)
  let scale = 1.7 / (ymax - y0)

  // ── ЛЕВО: висячая цепь (U), подвес в двух верхних точках
  let ox = 0.0
  let oy = 2.4
  let chain = ()
  for x in xs {
    let yy = (oy - 1.7) + (a * calc.cosh(x / a) - y0) * scale  // цепь: центр низ, концы верх (U)
    chain.push((ox + x, yy))
  }
  // опоры подвеса
  for s in (chain.first(), chain.last()) {
    circle(s, radius: 0.08, fill: INK, stroke: none)
  }
  line(..chain, stroke: (paint: INK, thickness: 1.6pt))
  content((ox, oy - 1.95), anchor: "north", text(size: 9pt)[цепь висит])
  content((ox, oy - 2.35), anchor: "north", text(size: 8.5pt, fill: OLIVE)[растяжение вдоль звеньев])
  // стрелки растяжения (наружу вдоль концов)
  content((ox - 1.75, oy - 0.05), anchor: "east", text(size: 9pt, fill: OLIVE)[$←$])
  content((ox + 1.75, oy - 0.05), anchor: "west", text(size: 9pt, fill: OLIVE)[$→$])

  // ── стрелка «перевернули»
  let mx = 3.4
  line((mx - 0.6, oy - 0.6), (mx + 0.6, oy - 0.6),
       stroke: (paint: SAND.darken(10%), thickness: 1.0pt), mark: (end: ">", fill: SAND.darken(10%), scale: 0.5))
  content((mx, oy - 0.35), anchor: "south", text(size: 8.5pt, fill: SAND.darken(20%))[перевернули])

  // ── ПРАВО: перевёрнутая катенария = арка (∩)
  let rx = 6.8
  let ry = 0.55          // базовая линия арки (низ опор)
  let arch = ()
  for x in xs {
    let yy = (ry + 1.7) - (a * calc.cosh(x / a) - y0) * scale  // арка: центр верх, пятки низ (∩)
    arch.push((rx + x, yy))
  }
  for s in (arch.first(), arch.last()) {
    circle(s, radius: 0.08, fill: INK, stroke: none)
  }
  line(..arch, stroke: (paint: INK, thickness: 1.8pt))
  // опоры-пятки
  rect((rx - 1.55, ry - 0.4), (rx - 1.25, ry), fill: SAND.lighten(55%), stroke: (paint: INK, thickness: LINE))
  rect((rx + 1.25, ry - 0.4), (rx + 1.55, ry), fill: SAND.lighten(55%), stroke: (paint: INK, thickness: LINE))
  content((rx, ry - 0.5), anchor: "north", text(size: 9pt)[арка стоит])
  content((rx, ry - 0.9), anchor: "north", text(size: 8.5pt, fill: OLIVE)[сжатие вдоль камней])
  // стрелки сжатия (внутрь к опорам)
  content((rx - 2.0, ry + 0.75), anchor: "east", text(size: 9pt, fill: OLIVE)[$→$])
  content((rx + 2.0, ry + 0.75), anchor: "west", text(size: 9pt, fill: OLIVE)[$←$])

  // ── итог
  content((3.4, -1.1), text(size: 9.5pt)[перевёрнутая цепная линия — арка, где всё работает только на сжатие])
})
