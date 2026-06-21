#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Известняковый массив, разрезанный сетью вертикальных трещин на отдельные столбы.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // массив
  rect((0, 0), (7.0, 3.2), fill: SAND.lighten(35%), stroke: INK)
  // вертикальные трещины разной высоты/частоты → столбы
  let cracks = (0.8, 1.7, 2.3, 3.2, 3.9, 4.9, 5.5, 6.3)
  for x in cracks {
    line((x, 3.2), (x, 0.3 + 0.15 * calc.rem(x * 7, 5)), stroke: (paint: OLIVE.darken(10%), thickness: 1pt))
  }
  // подпись
  content((3.5, -0.35), text(size: 8.5pt)[вертикальные трещины → столбы])
  // вода у подножия (Лена)
  line((0, 0), (7.0, 0), stroke: (paint: OLIVE, thickness: 1.2pt))
  content((6.4, 0.25), text(size: 7.5pt, fill: OLIVE)[Лена])
})
