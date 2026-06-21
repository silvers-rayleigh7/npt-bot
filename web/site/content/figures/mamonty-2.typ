#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Радиоуглерод: каждые 5730 лет — вдвое; после ~50 000 лет метод не работает.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let H = 3.0; let W = 6.0
  // оси
  line((0, 0), (W + 0.3, 0), mark: (end: ">", fill: INK))
  line((0, 0), (0, H + 0.4), mark: (end: ">", fill: INK))
  content((W + 0.3, -0.32), anchor: "east", text(size: 8.5pt, fill: OLIVE)[годы])
  content((0.15, H + 0.4), anchor: "west", text(size: 8.5pt, fill: OLIVE)[доля ¹⁴C])

  // кривая N/N0 = (1/2)^(t/5730); по x: 1 период = W/6
  let per = W / 6
  let pts = ()
  for i in range(0, 49) {
    let t = i / 8                     // в периодах полураспада
    pts.push((t * per, H * calc.pow(0.5, t)))
  }
  line(..pts, stroke: (paint: INK, thickness: 1.4pt))

  // отметки полураспада на оси Y (1, 1/2, 1/4, 1/8, 1/16, 1/32)
  let labs = ("1", "1\/2", "1\/4", "1\/8", "1\/16", "1\/32")
  for i in range(0, 6) {
    let y = H * calc.pow(0.5, i)
    line((-0.1, y), (0.1, y))
    content((-0.2, y), anchor: "east", text(size: 7pt)[$#labs.at(i)$])
    line((i * per, -0.1), (i * per, 0.1))
    content((i * per, -0.32), text(size: 6.5pt)[#(i * 5730)])
  }

  // практический предел ~50000 лет (≈8.7 периодов, но шкала до 6 → стрелка справа)
  content((W - 0.1, 0.9), anchor: "east", text(size: 8pt, fill: OLIVE)[предел метода ≈ 50 000 лет])
})
