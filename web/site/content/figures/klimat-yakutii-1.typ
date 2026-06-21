#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Океан — глубокий тепловой аккумулятор (стабильная T); суша — тонкий слой (резкие перепады).
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // ── океан: глубокая толща воды
  rect((0, 0), (2.6, 3.0), fill: OLIVE.lighten(30%), stroke: INK)
  for y in (0.6, 1.4, 2.2) { line((0.3, y), (2.3, y), stroke: (paint: OLIVE, thickness: 0.5pt)) }
  content((1.3, 3.3), text(size: 8.5pt)[океан])
  content((1.3, -0.35), text(size: 7.5pt, fill: OLIVE)[греется/стынет медленно])
  content((1.3, 1.5), text(size: 9pt, fill: white)[$c≈4200$])

  // термометр стабильный
  line((3.0, 0.4), (3.0, 2.6)); circle((3.0, 0.4), radius: 0.18, fill: SAND.darken(10%), stroke: INK)
  content((3.0, 3.0), text(size: 8pt)[ровно])

  // ── суша: тонкий прогретый слой
  rect((4.4, 2.4), (7.0, 3.0), fill: SAND.lighten(25%), stroke: INK)       // прогретый слой
  rect((4.4, 0), (7.0, 2.4), fill: SAND.darken(12%), stroke: INK)          // холодная глубина
  content((5.7, 3.3), text(size: 8.5pt)[суша])
  content((5.7, 2.65), text(size: 7pt)[$c≈800$])
  content((5.7, -0.35), text(size: 7.5pt, fill: OLIVE)[греется/стынет быстро])

  // термометр скачущий
  line((7.4, 0.4), (7.4, 2.6)); circle((7.4, 0.4), radius: 0.18, fill: SAND.darken(10%), stroke: INK)
  line((7.2, 2.4), (7.6, 2.6), mark: (start: ">", end: ">", fill: INK), stroke: (thickness: 0.7pt))
  content((7.4, 3.0), text(size: 8pt, fill: OLIVE)[скачет])
})
