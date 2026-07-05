#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Снаружи похоже, внутри несравнимо: ELIZA (правило-переворот) vs языковая модель (предсказание слова).
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // ── левая панель: ELIZA
  rect((0, 0), (4.2, 3.2), stroke: (paint: INK, thickness: LINE))
  content((2.1, 2.85), text(size: 9pt, weight: "bold")[ELIZA (1966)])
  content((2.1, 2.25), text(size: 8pt)[ключевое слово])
  line((2.1, 2.0), (2.1, 1.65), mark: (end: ">", fill: INK))
  content((2.1, 1.4), text(size: 8pt)[правило-заготовка])
  line((2.1, 1.15), (2.1, 0.8), mark: (end: ">", fill: INK))
  content((2.1, 0.55), text(size: 8pt, fill: OLIVE)[переворот фразы])

  // ── правая панель: языковая модель
  rect((5.0, 0), (9.2, 3.2), stroke: (paint: INK, thickness: LINE))
  content((7.1, 2.85), text(size: 9pt, weight: "bold")[языковая модель])
  content((7.1, 2.25), text(size: 8pt)[громадный текст])
  line((7.1, 2.0), (7.1, 1.65), mark: (end: ">", fill: INK))
  content((7.1, 1.4), text(size: 8pt)[обученная сеть])
  line((7.1, 1.15), (7.1, 0.8), mark: (end: ">", fill: INK))
  content((7.1, 0.55), text(size: 8pt, fill: OLIVE)[предсказание слова])

  // общий вывод
  content((4.6, 3.7), text(size: 8.5pt)[снаружи похоже])
  content((4.6, -0.5), text(size: 8.5pt, fill: SAND.darken(20%))[внутри несравнимо])
})
