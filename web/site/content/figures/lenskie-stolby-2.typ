#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Морозное расклинивание: вода в трещине замерзает, +9% объёма, лёд распирает трещину как клин.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let block(x0, gap, body, water, ice) = {
    rect((x0, 0), (x0 + 1.4, 2.6), fill: SAND.lighten(35%), stroke: INK)        // левая стенка
    rect((x0 + 1.4 + gap, 0), (x0 + 2.8 + gap, 2.6), fill: SAND.lighten(35%), stroke: INK)  // правая
    if water { rect((x0 + 1.4, 0.5), (x0 + 1.4 + gap, 2.1), fill: OLIVE.lighten(30%), stroke: none) }
    if ice { rect((x0 + 1.4, 0.3), (x0 + 1.4 + gap, 2.3), fill: OLIVE.lighten(10%), stroke: (paint: INK, thickness: 0.6pt)) }
    content((x0 + 1.4 + gap / 2, -0.35), text(size: 8pt)[#body])
  }
  block(0.0, 0.18, [вода в трещине], true, false)
  // стрелка замерзания
  line((3.4, 1.3), (4.0, 1.3), mark: (end: ">", fill: INK)); content((3.7, 1.6), text(size: 7pt, fill: OLIVE)[мороз])
  block(4.2, 0.42, [лёд +9% распирает], false, true)
  // клин-стрелки наружу
  line((5.55, 1.3), (5.25, 1.3), mark: (end: ">", fill: OLIVE), stroke: OLIVE)
  line((6.05, 1.3), (6.35, 1.3), mark: (end: ">", fill: OLIVE), stroke: OLIVE)
})
