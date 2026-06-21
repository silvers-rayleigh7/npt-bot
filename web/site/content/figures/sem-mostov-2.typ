#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Восьмой мост: дополнительное ребро между нечётными вершинами Б(5) и А(3) делает их чётными
// (6 и 4). Остаются две нечётные — В и Г — старт и финиш открытого эйлерова пути.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let A = (1.5, 3.4)
  let B = (1.5, 2.0)
  let C = (1.5, 0.6)
  let D = (3.1, 2.0)

  // исходные 7 рёбер
  bezier(A, B, (1.0, 2.7)); bezier(A, B, (2.0, 2.7))
  bezier(B, C, (1.0, 1.3)); bezier(B, C, (2.0, 1.3))
  line(B, D); line(A, D); line(C, D)

  // 8-й мост — дополнительная дуга Б—А, пунктир оливой
  bezier(A, B, (0.55, 2.7), stroke: (paint: OLIVE, thickness: 1.4pt, dash: "dashed"))
  content((0.05, 2.7), anchor: "east", text(size: 8.5pt, fill: OLIVE)[8-й мост])

  // вершины: степень числом внутри, буква рядом; чётные — обведены оливой
  let node(p, deg, lab, even) = {
    circle(p, radius: 0.30, fill: white,
      stroke: (paint: if even { OLIVE } else { INK }, thickness: if even { 1.6pt } else { 1pt }))
    content(p, text(size: 11pt, weight: "bold", fill: if even { OLIVE } else { INK })[#deg])
    content((p.at(0) + 0.34, p.at(1) + 0.30), anchor: "west", text(size: 8pt, fill: SAND)[#lab])
  }
  node(A, "4", "А", true)
  node(B, "6", "Б", true)
  node(C, "3", "В", false)
  node(D, "3", "Г", false)

  // подпись-итог справа
  content((4.0, 2.6), anchor: "west", text(size: 9.5pt)[было: $5,3,3,3$])
  content((4.0, 2.0), anchor: "west", text(size: 9.5pt)[стало: $6,4,3,3$])
  content((4.0, 1.4), anchor: "west", text(size: 9pt, fill: OLIVE)[2 нечётные → путь есть])
})
