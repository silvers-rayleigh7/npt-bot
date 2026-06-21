#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Закон обратных квадратов. Точечный источник (иконка солнца) слева — апекс
// расходящегося пучка. Одни и те же 4 луча из одной точки касаются углов
// ближнего квадрата (сторона s, площадь A на расстоянии r) и, по подобию
// треугольников, углов дальнего (сторона 2s, площадь 4A на расстоянии 2r).
// Свет тот же — растёкся вчетверо → яркость ÷4. Чистая геометрия, без реализма.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // ── геометрия пучка: апекс в источнике; подобие треугольников даёт ×2 сторону
  let apex = (0, 0)            // точечный источник (центр иконки солнца)
  let x1 = 3.3                 // ближняя грань малого квадрата = расстояние r
  let x2 = 6.6                 // ближняя грань большого = 2r (ровно вдвое)
  let h1 = 0.72               // полусторона малого; на x2 пучок даёт 2*h1
  let h2 = h1 * x2 / x1        // = 1.44, сторона ×2 → площадь ×4

  // ── малый квадрат A (грань на расстоянии r): пучок ровно вписан, лёгкая заливка
  rect((x1, -h1), (x1 + 2 * h1, h1), stroke: INK, fill: SUN.lighten(70%))
  // ── большой квадрат 4A (грань на 2r): сторона вдвое, площадь вчетверо
  rect((x2, -h2), (x2 + 2 * h2, h2), stroke: INK, fill: SUN.lighten(85%))

  // ── 4 луча из источника сквозь углы малого → к внешним углам большого квадрата
  // (касаются углов; острие точно на верхнем/нижнем углу дальней ячейки)
  for sy in (1, -1) {
    line(apex, (x2, sy * h2), mark: (end: ">", fill: INK, scale: 0.62))
  }

  // подпись площади по центру каждой ячейки
  content((x1 + h1, 0), text(size: 11pt)[$A$])
  content((x2 + h2, 0), text(size: 11.5pt)[$4 A$])

  // ── иконка солнца как точечный источник (в апексе)
  content(apex, image("icons/sun.svg", width: 0.6cm))

  // ── ось расстояний снизу: источник · r · 2r (к ближним граням ячеек)
  let yb = -h2 - 0.66
  line((0, yb), (x2, yb), stroke: (paint: OLIVE, thickness: LINE))
  for (x, lab) in ((0, none), (x1, $r$), (x2, $2 r$)) {
    line((x, yb - 0.12), (x, yb + 0.12), stroke: (paint: OLIVE, thickness: LINE))
    if lab != none {
      content((x, yb - 0.42), text(size: 10.5pt)[#lab])
    }
  }
  // тонкие выноски от ближних граней ячеек к их меткам на оси
  line((x1, -h1), (x1, yb + 0.12), stroke: (paint: OLIVE, thickness: 0.4pt, dash: "dotted"))
  line((x2, -h2), (x2, yb + 0.12), stroke: (paint: OLIVE, thickness: 0.4pt, dash: "dotted"))

  // ── итог сверху, в чистой зоне над пучком (одна строка, воздух)
  content((x2 / 2 + 0.3, h2 + 0.78),
    text(size: 10.5pt, fill: OLIVE)[расстояние #sym.times 2 #h(0.15em) #sym.arrow.r #h(0.15em) площадь #sym.times 4 #h(0.15em) #sym.arrow.r #h(0.15em) яркость #sym.div 4])
})
