#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Каскад: отбор по поведению → гормоны стресса ↓ → веер «доместикационных» признаков.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let box(p, w, body, fillc) = {
    rect((p.at(0) - w / 2, p.at(1) - 0.35), (p.at(0) + w / 2, p.at(1) + 0.35),
      radius: 0.12, fill: fillc, stroke: INK)
    content(p, text(size: 9pt)[#body])
  }

  let A = (0, 2.4); let B = (0, 0.9)
  box(A, 3.4, [отбор по дружелюбию], SAND.lighten(45%))
  box(B, 3.4, [гормоны стресса ↓], OLIVE.lighten(30%))
  line((0, 2.05), (0, 1.25), mark: (end: ">", fill: INK))

  // веер признаков
  let traits = (
    (-3.3, "висячие уши"), (-1.1, "белые пятна"), (1.1, "хвост колечком"), (3.3, "короткая морда"),
  )
  for (tx, lab) in traits {
    line((0, 0.55), (tx, -0.55), mark: (end: ">", fill: INK), stroke: (thickness: 0.7pt))
    rect((tx - 1.0, -1.25), (tx + 1.0, -0.55), radius: 0.1, fill: SAND.lighten(55%), stroke: INK)
    content((tx, -0.9), text(size: 8pt)[#lab])
  }
  content((0, -1.9), text(size: 8.5pt, fill: OLIVE)[одна «ручка» → каскад признаков])
})
