#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Миграция дюны: пологий наветренный склон, крутой подветренный; тело сползает по ветру.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // ветер
  line((0.3, 2.7), (2.8, 2.7), mark: (end: ">", fill: INK))
  content((1.5, 2.95), text(size: 9pt, fill: OLIVE)[ветер])

  // профиль дюны: пологий подъём слева → гребень → крутой обрыв справа
  line((0.4, 0), (4.0, 2.0), (4.7, 0), fill: SAND.lighten(30%), stroke: INK)

  // песчинки летят с наветренного склона через гребень
  for (px, py) in ((2.6, 1.5), (3.2, 1.95), (3.7, 2.25), (4.15, 1.7)) { circle((px, py), radius: 0.07, fill: SUN, stroke: none) }

  // подписи склонов
  content((1.7, 0.55), text(size: 8.5pt)[пологий])
  content((4.35, 1.0), anchor: "west", text(size: 8.5pt)[крутой])
  content((1.7, -0.35), text(size: 8pt, fill: OLIVE)[наветренный])
  content((4.45, -0.35), anchor: "west", text(size: 8pt, fill: OLIVE)[подветренный])
  // движение тела
  line((2.0, -0.9), (3.2, -0.9), mark: (end: ">", fill: OLIVE), stroke: OLIVE)
  content((2.6, -1.15), text(size: 8.5pt, fill: OLIVE)[движение дюны])
})
