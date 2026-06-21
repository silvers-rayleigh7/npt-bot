#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// L1: самоподобие. Ветвящийся контур балки; малый отвершек, если его увеличить,
// по форме НЕ отличить от всей балки — у формы нет масштаба. Слева целая балка
// с выделенной веткой, справа эта ветка увеличена = тот же ветвящийся узор.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // рекурсивная ветвь: рисует отрезок и две дочерние под углом ±spread, короче в k
  let branch(x, y, ang, len, depth, th) = {
    if depth <= 0 { return }
    let x2 = x + len * calc.cos(ang)
    let y2 = y + len * calc.sin(ang)
    line((x, y), (x2, y2), stroke: (paint: INK, thickness: th))
    branch(x2, y2, ang + 32deg, len * 0.7, depth - 1, calc.max(th * 0.8, 0.4pt))
    branch(x2, y2, ang - 28deg, len * 0.72, depth - 1, calc.max(th * 0.8, 0.4pt))
  }

  // ── ЛЕВО: целая балка (ствол вверх, 4 уровня ветвления)
  branch(0, 0, 90deg, 1.5, 4, 1.4pt)
  content((0, -0.4), anchor: "north", text(size: 9pt)[балка целиком])
  // рамка вокруг одного отвершка (правая верхняя подветвь)
  rect((0.95, 2.2), (2.15, 3.5), stroke: (paint: OLIVE, thickness: 0.8pt, dash: "dashed"))

  // ── стрелка увеличения
  line((2.5, 2.4), (3.7, 2.4), stroke: (paint: SAND.darken(10%), thickness: 0.9pt),
       mark: (end: ">", fill: SAND.darken(10%), scale: 0.5))
  content((3.1, 2.62), anchor: "south", text(size: 8.5pt, fill: SAND.darken(20%))[увеличили])

  // ── ПРАВО: тот же отвершек крупно (3 уровня) — форма не отличается
  branch(4.6, 1.3, 80deg, 1.45, 3, 1.4pt)
  rect((4.0, 1.0), (5.9, 3.7), stroke: (paint: OLIVE, thickness: 0.8pt, dash: "dashed"))
  content((4.95, 0.7), anchor: "north", text(size: 9pt)[тот же узор])

  // ── итог
  content((2.6, -1.15), text(size: 9.5pt)[малый отвершек = уменьшенная балка: по форме не отличить])
})
