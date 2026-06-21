#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Здоровая сосна тянется вверх за лидером; со сбитым лидером ствол достраивается вбок и петляет.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // ── здоровая сосна (слева): прямой ствол, лидер вверх
  line((1.0, 0), (1.0, 3.0), stroke: (thickness: 1.4pt))
  line((1.0, 3.0), (1.0, 3.5), mark: (end: ">", fill: OLIVE), stroke: (paint: OLIVE, thickness: 1.2pt))
  content((1.0, 3.8), text(size: 8pt, fill: OLIVE)[лидер])
  for y in (1.0, 1.7, 2.4) { line((1.0, y), (0.55, y - 0.35)); line((1.0, y), (1.45, y - 0.35)) }
  content((1.0, -0.4), text(size: 8.5pt)[здоровая])

  // ── сбитый лидер (справа): излом за изломом → петля
  line((4.0, 0), (4.0, 1.2), (3.5, 1.9), (4.3, 2.5), (3.8, 3.1), stroke: (thickness: 1.4pt))
  // отметка гибели лидера
  line((3.85, 1.05), (4.15, 1.35), stroke: (paint: OLIVE, thickness: 1pt))
  line((4.15, 1.05), (3.85, 1.35), stroke: (paint: OLIVE, thickness: 1pt))
  content((4.5, 1.2), anchor: "west", text(size: 8pt, fill: OLIVE)[лидер сбит])
  content((4.0, -0.4), text(size: 8.5pt)[лидер сбит → излом])
})
