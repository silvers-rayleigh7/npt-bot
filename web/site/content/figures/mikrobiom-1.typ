#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Человек не может расщепить порфиран сам — это делают бактерии-симбионты.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let box(p, w, body, fillc) = {
    rect((p.at(0) - w/2, p.at(1) - 0.4), (p.at(0) + w/2, p.at(1) + 0.4), radius: 0.12, fill: fillc, stroke: INK)
    content(p, text(size: 9pt)[#body])
  }
  box((0, 0), 1.8, [пища (нори)], SAND.lighten(45%))
  line((0.95, 0), (2.1, 0), mark: (end: ">", fill: INK))

  // человек — не может
  box((3.2, 0.8), 2.0, [фермент человека], SAND.lighten(55%))
  content((4.3, 0.8), anchor: "west", text(size: 11pt, fill: OLIVE)[✗])
  // бактерия — может
  box((3.2, -0.8), 2.0, [бактерия кишечника], OLIVE.lighten(30%))
  content((4.3, -0.8), anchor: "west", text(size: 11pt)[✓])
  line((0.4, -0.25), (2.2, -0.8), mark: (end: ">", fill: INK), stroke: (thickness: 0.7pt))

  line((4.25, -0.8), (5.3, -0.8), mark: (end: ">", fill: INK))
  box((6.5, -0.8), 1.8, [переварено], SAND.lighten(45%))
})
