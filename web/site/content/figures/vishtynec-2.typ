#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Аномалия плотности воды: максимум при +4 °C (парабола), и теплее, и холоднее — легче.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let W = 6.0; let H = 2.2
  // оси
  line((0, 0), (W + 0.3, 0), mark: (end: ">", fill: INK))
  line((0, 0), (0, H + 0.5), mark: (end: ">", fill: INK))
  content((W + 0.3, -0.32), anchor: "east", text(size: 9pt, fill: OLIVE)[температура $T$, °C])
  content((0.1, H + 0.5), anchor: "west", text(size: 9pt, fill: OLIVE)[плотность $rho$])

  // кривая ρ(T) ∝ 1 − k(T−4)²; T от 0 до 8 → x от 0 до W
  let pts = ()
  for i in range(0, 33) {
    let T = i / 4                      // 0..8
    let x = T / 8 * W
    let y = H * (1 - 0.045 * calc.pow(T - 4, 2))
    pts.push((x, y))
  }
  line(..pts, stroke: (paint: INK, thickness: 1.4pt))

  // вершина при T=4
  let xt = 4 / 8 * W
  line((xt, 0), (xt, H), stroke: (paint: OLIVE, thickness: 0.8pt, dash: "dashed"))
  circle((xt, H), radius: 0.07, fill: OLIVE, stroke: none)
  content((xt, -0.32), text(size: 8.5pt, fill: OLIVE)[+4])
  content((xt + 0.2, H + 0.05), anchor: "west", text(size: 8.5pt, fill: OLIVE)[плотнее всего])
  content((0.15, -0.32), text(size: 8pt)[0])
})
