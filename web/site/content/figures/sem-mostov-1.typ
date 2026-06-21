#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Абстракция Эйлера: реальная карта (4 участка суши + 7 мостов) → граф (4 вершины + 7 рёбер).
// Слева — схематичная карта: верхний берег, остров Кнайпхоф, нижний берег, правый островок;
// вода — оливковые полосы, мосты — короткие перемычки. Справа — тот же расклад как граф.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // ───────────── КАРТА (слева) ─────────────
  // вода (две протоки) — фон
  rect((0, 2.35), (3, 2.95), stroke: none, fill: OLIVE.lighten(55%))
  rect((0, 1.05), (3, 1.65), stroke: none, fill: OLIVE.lighten(55%))
  rect((2.6, 0), (3.0, 4), stroke: none, fill: OLIVE.lighten(55%))
  // участки суши
  rect((0, 2.95), (3, 4.0), fill: SAND.lighten(40%));   content((1.3, 3.45), text(size: 9pt)[Альтштадт])
  rect((0.7, 1.65), (2.0, 2.35), fill: SAND);           content((1.35, 2.0), text(size: 9pt)[Кнайпхоф])
  rect((0, 0), (3, 1.05), fill: SAND.lighten(40%));     content((1.0, 0.5), text(size: 9pt)[Форштадт])
  rect((3.0, 1.4), (3.9, 2.6), fill: SAND.lighten(40%)); content((3.45, 2.9), text(size: 8.5pt)[Ломзе])
  // 7 мостов — короткие перемычки через воду
  let br(x0, y0, x1, y1) = line((x0, y0), (x1, y1), stroke: (paint: INK, thickness: 1.6pt))
  br(1.0, 2.35, 1.0, 2.95); br(1.7, 2.35, 1.7, 2.95)   // остров — Альтштадт (×2)
  br(1.0, 1.05, 1.0, 1.65); br(1.7, 1.05, 1.7, 1.65)   // остров — Форштадт (×2)
  br(2.0, 2.0, 3.0, 2.0)                                 // остров — Ломзе
  br(2.6, 3.4, 3.2, 2.6); br(2.6, 0.7, 3.2, 1.4)        // Ломзе — Альтштадт; Ломзе — Форштадт

  // ───────────── стрелка абстракции ─────────────
  line((4.2, 2.0), (5.2, 2.0), mark: (end: ">", fill: INK))
  content((4.7, 2.35), text(size: 8.5pt, fill: OLIVE)[абстракция])

  // ───────────── ГРАФ (справа) ─────────────
  let A = (7.0, 3.4)   // Альтштадт
  let B = (7.0, 2.0)   // остров (центр)
  let C = (7.0, 0.6)   // Форштадт
  let D = (8.6, 2.0)   // Ломзе
  // двойные рёбра — две дуги; одиночные — прямые
  bezier(A, B, (6.5, 2.7)); bezier(A, B, (7.5, 2.7))    // остров — Альтштадт ×2
  bezier(B, C, (6.5, 1.3)); bezier(B, C, (7.5, 1.3))    // остров — Форштадт ×2
  line(B, D); line(A, D); line(C, D)                    // остров—Ломзе, Альтштадт—Ломзе, Форштадт—Ломзе
  // вершины
  for (p, lab) in ((A, "А"), (B, "Б"), (C, "В"), (D, "Г")) {
    circle(p, radius: 0.28, fill: white, stroke: (paint: INK, thickness: 1pt))
    content(p, text(size: 10pt, weight: "bold")[#lab])
  }
})
