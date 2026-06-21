#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Прямая задача: причина → следствие. Обратная: по следствию восстановить причину.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let box(p, w, body, fillc) = {
    rect((p.at(0) - w / 2, p.at(1) - 0.4), (p.at(0) + w / 2, p.at(1) + 0.4), radius: 0.12, fill: fillc, stroke: INK)
    content(p, text(size: 10pt)[#body])
  }
  let A = (0, 0); let B = (5.2, 0)
  box(A, 2.0, [причина $x$], SAND.lighten(45%))
  box(B, 2.2, [следствие $y$], SAND.lighten(45%))

  // прямая: x → y через закон A
  line((1.05, 0.25), (4.05, 0.25), mark: (end: ">", fill: INK), stroke: (thickness: 1.1pt))
  content((2.55, 0.6), text(size: 9pt)[закон природы $A$])
  content((2.55, 0.05), text(size: 8pt, fill: OLIVE)[прямая задача])

  // обратная: y → x (пунктир, против стрелки)
  line((4.05, -0.25), (1.05, -0.25), mark: (end: ">", fill: OLIVE), stroke: (paint: OLIVE, thickness: 1.1pt, dash: "dashed"))
  content((2.55, -0.62), text(size: 8.5pt, fill: OLIVE)[обратная задача: по $y$ найти $x$])
})
