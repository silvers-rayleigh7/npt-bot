#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Цикл отбора Беляева: популяция → отбор по дружелюбию → новое поколение → повтор.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let box(p, w, h, body) = {
    rect((p.at(0) - w / 2, p.at(1) - h / 2), (p.at(0) + w / 2, p.at(1) + h / 2),
      radius: 0.12, fill: SAND.lighten(45%), stroke: INK)
    content(p, text(size: 9pt)[#body])
  }

  let A = (0, 1.4); let B = (4.2, 1.4); let C = (4.2, -1.0); let D = (0, -1.0)
  box(A, 2.4, 0.7, [популяция лисиц])
  box(B, 2.8, 0.7, [отбор по дружелюбию])
  box(C, 2.6, 0.7, [новое поколение])
  box(D, 2.2, 0.7, [скрещивание])

  set-style(mark: (end: ">", fill: INK))
  line((1.25, 1.4), (2.75, 1.4))                     // A→B
  line((4.2, 1.0), (4.2, -0.65))                     // B→C
  line((2.85, -1.0), (1.15, -1.0))                   // C→D
  line((0, -0.65), (0, 1.0))                         // D→A (замыкание)
  content((2.1, 1.65), text(size: 8pt, fill: OLIVE)[самых спокойных])
  content((-0.15, 0.2), anchor: "east", text(size: 8pt, fill: OLIVE)[повтор])
})
