#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Трилатерация: каждое измеренное расстояние d_i до спутника задаёт окружность
// (в 3D — сферу) возможных положений. Три окружности, проходящие через одну
// точку P, пересекаются в ней — это и есть положение приёмника. Абстрактная
// геометрия в идиоме observatoriya/geo-srez: тонкий штрих, палитра, иконки где
// помогают узнаванию (спутник — Lucide-иконка, приёмник — пин «вы здесь»).
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE), mark: (fill: INK, scale: 0.5))

  let dist(a, b) = calc.sqrt(
    calc.pow(b.at(0) - a.at(0), 2) + calc.pow(b.at(1) - a.at(1), 2)
  )

  // приёмник — общая точка пересечения трёх окружностей
  let P = (0, 0)
  // три спутника, разнесённые по дуге сверху
  let S1 = (-2.7, 1.9)
  let S2 = (2.8, 2.2)
  let S3 = (0.1, 3.4)
  let sats = (S1, S2, S3)
  let cols = (OLIVE, SAND, SUN)

  // ── окружности: радиус = измеренное расстояние до спутника (через P)
  for i in range(3) {
    let s = sats.at(i)
    circle(s, radius: dist(s, P), stroke: (paint: cols.at(i), thickness: LINE))
  }

  // ── радиусы d_i: отрезок спутник → приёмник, подписанный измеренным расстоянием
  let dlabels = ($d_1$, $d_2$, $d_3$)
  for i in range(3) {
    let s = sats.at(i)
    line(s, P, stroke: (paint: INK, thickness: LINE))
    // подпись посередине радиуса, со смещением в сторону от линии
    let mx = (s.at(0) + P.at(0)) / 2
    let my = (s.at(1) + P.at(1)) / 2
    content((mx + 0.28, my + 0.10), text(size: 10.5pt)[#dlabels.at(i)])
  }

  // ── спутники: иконка орбитального спутника (не наземная тарелка) + подпись
  for i in range(3) {
    let s = sats.at(i)
    content((s.at(0), s.at(1) + 0.05), image("icons/satellite.svg", width: 0.85cm))
  }
  content((S1.at(0) - 0.1, S1.at(1) + 0.7), text(size: 9pt, fill: OLIVE)[спутник])

  // ── приёмник: пин «вы здесь» над точкой пересечения
  circle(P, radius: 0.07, fill: INK, stroke: none)
  content((P.at(0), P.at(1) + 0.02), anchor: "south", image("icons/map-pin.svg", width: 0.66cm))
  content((P.at(0) + 0.62, P.at(1) - 0.14), anchor: "west", text(size: 9pt, fill: OLIVE)[вы здесь])
})
