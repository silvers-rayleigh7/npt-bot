#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Логистическая S-кривая: разгон → перегиб → плато.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let W = 6.0; let H = 3.0
  line((0, 0), (W + 0.3, 0), mark: (end: ">", fill: INK))
  line((0, 0), (0, H + 0.4), mark: (end: ">", fill: INK))
  content((W + 0.3, -0.32), anchor: "east", text(size: 8.5pt, fill: OLIVE)[время $t$])
  content((0.15, H + 0.4), anchor: "west", text(size: 8.5pt, fill: OLIVE)[размер $X$])

  // предел L
  line((0, H), (W, H), stroke: (paint: OLIVE, thickness: 0.7pt, dash: "dashed"))
  content((W - 0.1, H + 0.0), anchor: "south-east", text(size: 7.5pt, fill: OLIVE)[предел $L$])

  // логистическая X(t) = H / (1 + e^{-k(t-t0)})
  let pts = ()
  for i in range(0, 49) {
    let t = i / 48 * W
    pts.push((t, H / (1 + calc.exp(-2.0 * (t - W / 2)))))
  }
  line(..pts, stroke: (paint: INK, thickness: 1.5pt))

  // подписи фаз
  content((1.2, 0.5), text(size: 8pt)[разгон])
  content((3.0, 1.7), text(size: 8pt, fill: OLIVE)[перегиб])
  content((4.9, 2.65), text(size: 8pt)[плато])
})
