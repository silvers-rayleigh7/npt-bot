#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// P–T диаграмма: алмаз устойчив при высоком давлении (мантия), графит — при низком.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let W = 5.4; let H = 3.4
  line((0, 0), (W + 0.3, 0), mark: (end: ">", fill: INK))
  line((0, 0), (0, H + 0.3), mark: (end: ">", fill: INK))
  content((W + 0.3, -0.32), anchor: "east", text(size: 8.5pt, fill: OLIVE)[температура])
  content((0.15, H + 0.3), anchor: "west", text(size: 8.5pt, fill: OLIVE)[давление])

  // граница графит/алмаз (наклонная прямая)
  line((0.4, 0.6), (W, 2.7), stroke: (paint: INK, thickness: 1.2pt))
  content((4.0, 2.95), text(size: 8.5pt)[граница фаз])

  // области
  content((1.3, 2.5), text(size: 10pt)[алмаз])
  content((1.3, 2.1), text(size: 7.5pt, fill: OLIVE)[высокое P · мантия])
  content((4.2, 0.7), text(size: 10pt)[графит])
  content((4.2, 0.35), text(size: 7.5pt, fill: OLIVE)[низкое P · поверхность])

  // точка мантии + быстрый подъём (стрелка вниз-влево к поверхности, минуя превращение)
  circle((1.7, 2.85), radius: 0.09, fill: OLIVE, stroke: (paint: INK, thickness: 0.5pt))
  content((1.85, 3.05), anchor: "west", text(size: 7.5pt)[> 150 км])
  line((1.8, 2.7), (3.4, 0.55), mark: (end: ">", fill: OLIVE), stroke: (paint: OLIVE, thickness: 1pt, dash: "dashed"))
  content((3.5, 1.6), anchor: "west", text(size: 8pt, fill: OLIVE)[быстрый подъём\ алмаз не успевает\ стать графитом])
})
