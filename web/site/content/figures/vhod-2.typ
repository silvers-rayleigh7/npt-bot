#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// L2 vhod: научный метод как ЦИКЛ. Четыре шага по кругу —
// наблюдение → причина → проверка → применение → и снова наблюдение.
// Узлы — авто-фреймленные круги (frame: "circle"): подпись НИКОГДА не вылезет
// за границу, круг сам подстраивается под текст. Единая ширина бокса = равные узлы.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let R = 3.6            // радиус раскладки (центр → узел)
  let nodes = (
    (90deg,  [наблюдение]),
    (0deg,   [причина]),
    (-90deg, [проверка]),
    (180deg, [применение]),
  )
  let pos(a) = (R * calc.cos(a), R * calc.sin(a))

  // ── дуги-стрелки по часовой между соседними узлами (рисуем ПОД узлами)
  // gap = угловой зазор у плашек, чтобы стрелка не въезжала в круг
  let gap = 26deg
  let pairs = ((90deg, 0deg), (0deg, -90deg), (-90deg, -180deg), (-180deg, -270deg))
  for pr in pairs {
    arc((0, 0), radius: R, start: pr.at(0) - gap, stop: pr.at(1) + gap,
        anchor: "origin", stroke: (paint: OLIVE, thickness: 1.1pt),
        mark: (end: ">", fill: OLIVE, scale: 0.55))
  }

  // ── узлы: авто-фрейм круга под подпись фиксированной ширины (равные узлы)
  for n in nodes {
    let p = pos(n.at(0))
    content(p, box(width: 2.0cm)[#align(center, text(size: 10pt)[#n.at(1)])],
            frame: "circle", padding: 5pt,
            fill: SAND.lighten(62%), stroke: (paint: INK, thickness: LINE))
  }

  // ── центр: тот же круг повторяется на каждом стенде
  content((0, 0.40), text(size: 9pt, fill: SAND.darken(20%))[один круг —])
  content((0, -0.04), text(size: 9pt, fill: SAND.darken(20%))[на каждом])
  content((0, -0.48), text(size: 9pt, fill: SAND.darken(20%))[стенде])
})
