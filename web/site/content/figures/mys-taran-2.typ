#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Оползень: вода застаивается над водоупорной глиной, поровое давление растёт,
// эффективное напряжение падает, пласт песка сползает по глиняной подошве.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // слой глины (водоупор) — наклонная подошва
  line((0, 0.3), (6.0, 0.3), (6.0, 0.0), (0, 0.0), close: true, fill: OLIVE.lighten(15%), stroke: INK)
  content((3.0, 0.15), text(size: 8pt, fill: white)[глина · водоупор])

  // слой песка над ней
  line((0, 0.3), (6.0, 0.3), (6.0, 1.6), (0, 2.0), close: true, fill: SAND.lighten(35%), stroke: INK)
  content((1.4, 1.1), text(size: 8.5pt)[песок])

  // уровень застоявшейся воды (перехваченный глиной)
  line((0.3, 0.9), (5.7, 0.7), stroke: (paint: OLIVE, thickness: 1pt, dash: "dashed"))
  content((4.2, 1.05), text(size: 8pt, fill: OLIVE)[вода застаивается])
  // капли просачивания сверху
  for px in (1.0, 2.0, 3.0) { line((px, 2.1), (px, 1.7), mark: (end: ">", fill: OLIVE), stroke: (paint: OLIVE, thickness: 0.7pt)) }
  content((2.0, 2.35), text(size: 8pt, fill: OLIVE)[дождь, талый снег])

  // сползающий блок + стрелка скольжения по подошве
  line((4.6, 1.4), (4.6, 0.34), mark: (end: ">", fill: INK), stroke: (thickness: 1pt))
  line((4.6, 0.4), (5.6, 0.32), mark: (end: ">", fill: INK), stroke: (thickness: 1.4pt))
  content((5.1, 0.62), anchor: "west", text(size: 8pt)[пласт сползает])

  // формула
  content((3.0, -0.7), text(size: 10pt)[$sigma' = sigma - u$ #h(0.4cm) → #h(0.2cm) растёт $u$, падает $sigma'$])
})
