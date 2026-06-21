#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Профиль мерзлоты: активный слой (оттаивает) над вечной мерзлотой (хранит находки).
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let X0 = 0; let X1 = 4.0
  // слои
  rect((X0, 2.4), (X1, 3.1), fill: SAND.lighten(35%), stroke: INK)         // активный слой
  rect((X0, 0.0), (X1, 2.4), fill: OLIVE.lighten(25%), stroke: INK)        // вечная мерзлота
  // растительность сверху
  for x in (0.4, 1.0, 1.6, 2.2, 2.8, 3.4) { line((x, 3.1), (x, 3.4)) }
  // мамонт в мерзлоте (силуэт)
  circle((2.7, 1.0), radius: 0.42, fill: SAND.darken(12%), stroke: INK)
  line((2.35, 0.85), (2.05, 0.55)); line((2.5, 0.7), (2.4, 0.35))           // бивни/ноги намёком
  content((2.7, 1.0), text(size: 7pt, fill: white)[мамонт])

  // подписи
  content((X1 + 0.3, 2.75), anchor: "west", text(size: 9pt)[активный слой])
  content((X1 + 0.3, 2.45), anchor: "west", text(size: 7.5pt, fill: OLIVE)[оттаивает летом])
  content((X1 + 0.3, 1.3), anchor: "west", text(size: 9pt, fill: white)[вечная мерзлота])
  content((X1 + 0.3, 1.0), anchor: "west", text(size: 7.5pt, fill: white)[T < 0 °C тысячи лет])

  // лето/зима на активном слое
  line((-0.55, 3.0), (-0.15, 2.7), mark: (end: ">", fill: SUN), stroke: (paint: SUN, thickness: 1pt))
  content((-0.6, 3.05), anchor: "east", text(size: 7.5pt, fill: OLIVE)[лето])
})
