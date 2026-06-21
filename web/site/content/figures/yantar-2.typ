#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Экспонента распада N(t)=N0·e^(−kt). Обычная ткань — большой k, исчезает быстро;
// в янтаре k почти ноль — кривая держится у единицы.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let H = 3.0   // высота для N/N0 = 1
  let X = 6.2   // длина оси времени

  // оси
  line((0, 0), (X + 0.3, 0), mark: (end: ">", fill: INK))
  line((0, 0), (0, H + 0.4), mark: (end: ">", fill: INK))
  content((X + 0.3, -0.32), anchor: "east", text(size: 9pt, fill: OLIVE)[время $t$])
  content((-0.15, H + 0.4), anchor: "east", text(size: 9pt, fill: OLIVE)[$N\/N_0$])
  // отметка единицы
  line((-0.1, H), (0.1, H)); content((-0.25, H), anchor: "east", text(size: 8.5pt)[$1$])

  // кривая распада: N/N0 = e^(−k x)
  let curve(k, paint, dash) = {
    let pts = ()
    for i in range(0, 26) {
      let x = i / 4
      pts.push((x, H * calc.exp(-k * x)))
    }
    line(..pts, stroke: (paint: paint, thickness: 1.4pt, dash: dash))
  }
  curve(0.95, INK, none)        // обычная ткань — быстро вниз
  curve(0.05, OLIVE, none)      // в янтаре — почти горизонталь

  content((2.2, 0.45), anchor: "west", text(size: 9pt)[обычная ткань])
  content((3.4, 2.55), anchor: "west", text(size: 9pt, fill: OLIVE)[в янтаре])
})
