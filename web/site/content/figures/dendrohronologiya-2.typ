#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Перекрёстная датировка: узоры колец живого и старого дерева совпадают на стыке → летопись сшивают вглубь.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: 0.8pt))

  // рисунок ширины колец как столбики разной высоты (общий «штрихкод»)
  let pat = (0.5, 0.8, 0.3, 0.7, 0.9, 0.35, 0.6, 0.85, 0.4, 0.75, 0.55, 0.9)
  let bars(x0, y0, seq, paint) = {
    let x = x0
    for h in seq { rect((x, y0), (x + 0.16, y0 + h), fill: paint, stroke: none); x += 0.22 }
  }

  // живое дерево (справа, недавние годы)
  bars(3.0, 1.4, pat.slice(0, 8), OLIVE.lighten(10%))
  content((3.0, 2.5), anchor: "west", text(size: 8.5pt)[живое дерево])
  // старое бревно (левее, перекрытие на стыке тем же узором)
  bars(1.24, 0.0, pat.slice(4, 12), SAND.darken(8%))
  content((1.24, -0.45), anchor: "west", text(size: 8.5pt)[старое бревно])

  // область совпадения узора
  rect((3.0, -0.55), (3.0 + 0.22 * 4 - 0.06, 1.4 + 0.95), stroke: (paint: OLIVE, thickness: 1pt, dash: "dashed"), fill: none)
  content((3.4, 2.95), text(size: 8pt, fill: OLIVE)[совпадение узора → сшивка])
  // стрелка «вглубь времени»
  line((3.6, -1.0), (1.0, -1.0), mark: (end: ">", fill: INK), stroke: (thickness: 0.8pt))
  content((2.3, -1.3), text(size: 8pt)[вглубь времени])
})
