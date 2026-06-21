#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Сукцессия: пустошь → травы → кустарник → молодой лес → старый лес (десятилетия → века).
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let g = 0
  line((-0.3, g), (10.3, g), stroke: (paint: INK, thickness: 1pt))
  // ось времени
  line((-0.3, -0.5), (10.3, -0.5), mark: (end: ">", fill: INK), stroke: (thickness: 0.8pt))
  content((10.3, -0.85), anchor: "east", text(size: 8pt, fill: OLIVE)[время])

  // деревце высотой h в точке x
  let tree(x, h) = {
    line((x, g), (x, g + h), stroke: (thickness: 1.4pt))
    let w = h * 0.45
    line((x - w, g + h * 0.5), (x, g + h * 0.95), (x + w, g + h * 0.5))
  }
  let grass(x) = { for dx in (-0.12, 0, 0.12) { line((x + dx, g), (x + dx, g + 0.3)) } }
  let bush(x) = { circle((x, g + 0.25), radius: 0.28, stroke: INK); line((x, g), (x, g + 0.1)) }

  grass(0.7);              content((0.7, -1.1), text(size: 7.5pt)[травы])
  bush(2.7);               content((2.7, -1.1), text(size: 7.5pt)[кустарник])
  tree(5.0, 1.3);          content((5.0, -1.1), text(size: 7.5pt)[молодой лес])
  tree(7.6, 2.0); tree(8.3, 2.4); tree(8.9, 1.9)
  content((8.3, -1.1), text(size: 7.5pt)[старый лес])

  for (x, lab) in ((0.7, "годы"), (5.0, "десятилетия"), (8.3, "века")) {
    content((x, 2.95), text(size: 7.5pt, fill: OLIVE)[#lab])
  }
})
