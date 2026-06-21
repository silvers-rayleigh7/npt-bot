#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Идея L2: зимой тёмный ствол рискует ПЕРЕГРЕТЬСЯ — на него приходят ДВА входа:
// прямое низкое солнце сверху и свет, отражённый от снега снизу, и тёмная кора
// ОБА ПОГЛОЩАЕТ. Субъект — тёмный свотч (идиом fig1/fig2), а не «дерево» (кринж).
// Солнце низко у горизонта → пологий угол лучей («низкое зимнее солнце»).
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE), mark: (fill: INK, scale: 0.5))

  let g = 0.0            // уровень снега
  let bl = 5.4           // тёмный свотч коры
  let br = 6.7
  let bt = 3.0           // высота свотча

  // ── снег: читаемый слой (линия SAND + короткие штрихи)
  line((-0.3, g), (8.2, g), stroke: (paint: SAND, thickness: 1.6pt))
  for x in (0.1, 0.7, 1.3, 1.9, 2.5, 3.1, 3.7, 7.2, 7.8) {
    line((x, g), (x - 0.18, g - 0.24), stroke: (paint: SAND, thickness: 0.6pt))
  }
  content((0.55, g - 0.52), text(size: 10pt, fill: OLIVE)[снег])

  // ── тёмный свотч коры: сплошная заливка INK (как тёмная кора в fig1/fig2)
  rect((bl, g), (br, bt), stroke: none, fill: INK)
  content((bl + 0.65, bt + 0.42), text(size: 10pt)[тёмная кора])

  // ── солнце (иконка Lucide) В ВЕРХНЕМ ЛЕВОМ УГЛУ — диск ВЫШЕ верхней кромки свотча (bt=3.0)
  let sx = 0.95
  let sy = 3.85
  content((sx, sy), image("icons/sun.svg", width: 0.9cm))

  // ── ВХОД 1: прямой НИСХОДЯЩИЙ пологий луч сверху → верхняя часть свотча.
  //    Низкое зимнее солнце = пологий угол, но диск ВЫШЕ сцены, луч падает СВЕРХУ ВНИЗ;
  //    у точки попадания почти горизонтален (≈ под прямым углом к вертикальному стволу).
  line((sx + 0.55, sy - 0.30), (bl - 0.03, 2.62), mark: (end: ">"))

  // ── ВХОД 2: ПРИЧИННЫЙ отскок (солнце → точка P на снегу → нижняя часть свотча)
  let px = 3.5
  line((sx + 0.35, sy - 0.55), (px, g))                                       // падающий от солнца на снег
  line((px, g), (bl - 0.03, 0.85), mark: (end: ">"), stroke: (paint: OLIVE))  // отражённый снегом → низ свотча

  // ── РЕАКЦИЯ: тёмная кора ПОГЛОЩАЕТ → греется (волна тепла + термометр, как в fig1)
  line(
    (br + 0.05, 1.6), (br + 0.30, 1.8), (br + 0.55, 1.4), (br + 0.80, 1.6),
    stroke: (paint: OLIVE), mark: (end: ">"),
  )
  content((br + 1.35, 1.55), image("icons/thermometer-sun.svg", width: 0.85cm))
  content((br + 1.35, 0.6), text(size: 9.5pt, fill: OLIVE)[перегрев])
})
