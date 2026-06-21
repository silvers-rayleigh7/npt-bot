#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE), mark: (fill: INK, scale: 0.55))

  // ── солнце (иконка Lucide), вверху по центру
  content((4.2, 5.1), image("icons/sun.svg", width: 1.05cm))

  // ── свотчи коры: светлая (контур) и тёмная (заливка), широко разнесены
  rect((1.0, 1.0), (2.2, 3.0), stroke: INK, fill: white)
  // чечевички на светлой коре — короткие чёрточки, чтобы читалось как берёзовая кора
  for y in (1.5, 2.05, 2.6) { line((1.2, y), (1.46, y), stroke: (paint: INK, thickness: 1.3pt)) }
  content((1.6, 0.5), text(size: 10pt)[светлая кора])
  rect((6.0, 1.0), (7.2, 3.0), stroke: none, fill: INK)
  content((6.6, 0.5), text(size: 10pt)[тёмная кора])

  // ── падающие лучи от солнца, остриё точно на верхней грани свотчей
  // светлая: остриё на верхней грани в общем узле с отражёнными (1.95, 3.0)
  line((3.55, 4.5), (1.95, 3.0), mark: (end: ">"))
  // тёмная: остриё внутри верхней грани (свотч 6.0..7.2), не обрываясь в воздухе
  line((4.85, 4.5), (6.4, 3.0), mark: (end: ">"))

  // ── светлая: аккуратный V — обе отражённые выходят ИЗ той же точки (1.95, 3.0)
  line((1.95, 3.0), (0.95, 4.1), mark: (end: ">"), stroke: (paint: OLIVE))
  line((1.95, 3.0), (0.55, 3.75), mark: (end: ">"), stroke: (paint: OLIVE))
  content((0.45, 4.55), text(size: 10pt, fill: OLIVE)[отражает])

  // ── тёмная: греется — термометр придвинут к свотчу, волна тепла OLIVE связывает их
  // волнистая линия тепла от правой грани тёмного свотча к термометру
  line(
    (7.25, 2.5), (7.5, 2.7), (7.75, 2.3), (8.0, 2.5),
    stroke: (paint: OLIVE), mark: (end: ">"),
  )
  content((8.55, 2.45), image("icons/thermometer-sun.svg", width: 0.9cm))
  content((8.55, 1.45), text(size: 9.5pt, fill: OLIVE)[нагревается])
})
