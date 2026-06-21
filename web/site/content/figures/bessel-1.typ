#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Параллакс: с двух концов земной орбиты близкая звезда смещается на фоне далёких на угол p.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // фон далёких звёзд (вверху)
  line((-2.6, 4.2), (2.6, 4.2), stroke: (paint: OLIVE.lighten(20%), thickness: 0.8pt))
  for x in (-2.0, -1.0, 0.6, 1.6, 2.2) { circle((x, 4.2), radius: 0.04, fill: OLIVE, stroke: none) }
  content((2.7, 4.2), anchor: "west", text(size: 8pt, fill: OLIVE)[далёкие звёзды])

  // близкая звезда
  let S = (0.2, 2.7)
  circle(S, radius: 0.10, fill: SUN, stroke: none)
  content((S.at(0) + 0.2, S.at(1)), anchor: "west", text(size: 8pt)[близкая звезда])

  // Солнце и орбита Земли
  circle((0, 0), radius: 0.14, fill: SUN, stroke: none)
  content((0, -0.4), text(size: 8pt)[Солнце])
  group({ translate((0, 0)); scale(x: 100%, y: 34%); circle((0, 0), radius: 1.8, stroke: (paint: OLIVE.lighten(30%), thickness: 0.7pt)) })
  let E1 = (-1.8, 0); let E2 = (1.8, 0)
  circle(E1, radius: 0.10, fill: INK, stroke: none); content((-1.8, -0.4), text(size: 8pt)[Земля (янв.)])
  circle(E2, radius: 0.10, fill: INK, stroke: none); content((1.8, -0.4), text(size: 8pt)[Земля (июль)])

  // лучи на звезду и дальше на фон
  line(E1, S, (S.at(0) + (S.at(0) - E1.at(0)) * 0.62, 4.2), stroke: (thickness: 0.7pt))
  line(E2, S, (S.at(0) + (S.at(0) - E2.at(0)) * 0.62, 4.2), stroke: (thickness: 0.7pt))
  // угол параллакса у звезды
  content((S.at(0) - 0.05, S.at(1) - 0.42), text(size: 9pt, fill: OLIVE)[$p$])
  // база
  line((-1.8, 0.55), (1.8, 0.55), mark: (start: ">", end: ">", fill: INK), stroke: (thickness: 0.6pt))
  content((0, 0.78), text(size: 7.5pt, fill: OLIVE)[база ≈ диаметр орбиты])
})
