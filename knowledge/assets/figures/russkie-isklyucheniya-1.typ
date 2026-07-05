#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Чем чаще слово, тем устойчивее его старая (неправильная) форма.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // оси
  line((0, 0), (0, 3.4), mark: (end: ">", fill: INK))
  line((0, 0), (7.2, 0), mark: (end: ">", fill: INK))
  content((3.6, -0.55), text(size: 8.5pt)[частота слова в речи →])
  content((-0.15, 3.5), text(size: 8.5pt)[устойчивость старой формы], anchor: "west")

  // рост: редкие слова (слева, низко) → частые (справа, высоко)
  line((0.3, 0.25), (1.5, 0.6), (3.0, 1.3), (4.5, 2.2), (6.2, 3.0),
       stroke: (paint: OLIVE, thickness: 1.4pt))

  // маркеры
  circle((1.1, 0.45), radius: 0.09, fill: SAND, stroke: (paint: INK, thickness: 0.5pt))
  content((1.1, 0.95), text(size: 8pt)[редкие])
  content((1.1, 1.35), text(size: 7.5pt, fill: OLIVE)[выравниваются])
  circle((6.0, 2.9), radius: 0.09, fill: SUN, stroke: (paint: INK, thickness: 0.5pt))
  content((5.5, 2.5), text(size: 8pt)[частые])
  content((5.5, 2.12), text(size: 7.5pt, fill: OLIVE)[держат старое])
})
