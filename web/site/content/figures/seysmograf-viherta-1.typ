#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Инерционный сейсмограф: рама на грунте, тяжёлый груз на пружине отстаёт, перо пишет на барабане.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // грунт + штриховка
  line((0, 0), (7.0, 0), stroke: (thickness: 1.2pt))
  for x in range(0, 14) { line((x / 2, 0), (x / 2 - 0.25, -0.28), stroke: (thickness: 0.5pt)) }
  // толчок почвы
  line((0.6, -0.6), (2.0, -0.6), mark: (start: ">", end: ">", fill: INK), stroke: (thickness: 0.8pt))
  content((1.3, -0.9), text(size: 8pt, fill: OLIVE)[толчок почвы])

  // рама (стойка), привинчена к грунту
  line((1.0, 0), (1.0, 3.2), stroke: (thickness: 1.4pt))
  line((1.0, 3.2), (3.0, 3.2), stroke: (thickness: 1.4pt))   // верхняя балка

  // пружина (зигзаг) от балки вниз к грузу
  let sx = 2.6
  let zz = ()
  for i in range(0, 7) { zz.push((sx + (calc.rem(i, 2) * 2 - 1) * 0.18, 3.2 - 0.13 * i)) }
  line(..zz, stroke: (thickness: 0.9pt))
  content((sx + 0.45, 2.7), anchor: "west", text(size: 8pt, fill: OLIVE)[пружина $k$])

  // груз
  circle((sx, 1.9), radius: 0.42, fill: SAND.darken(10%), stroke: INK)
  content((sx, 1.9), text(size: 11pt, weight: "bold")[$M$])

  // тормоз (поршень в масле) рядом
  rect((sx + 0.7, 1.5), (sx + 1.0, 2.3), stroke: INK)
  line((sx + 0.85, 2.3), (sx + 0.85, 3.2), stroke: (thickness: 0.8pt))
  content((sx + 1.1, 1.9), anchor: "west", text(size: 8pt, fill: OLIVE)[тормоз $c$])

  // перо от груза к барабану
  line((sx - 0.42, 1.9), (5.3, 1.9), stroke: (thickness: 0.8pt))
  circle((5.7, 1.9), radius: 0.45, stroke: INK)
  line((5.7, 1.9), (5.7, 2.35), stroke: (thickness: 0.6pt))
  content((5.7, 1.1), text(size: 8pt)[барабан])
})
