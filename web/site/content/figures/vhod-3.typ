#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// L3 vhod: идея Фейнмана — из ОДНОГО принципа («всё из атомов в движении»)
// выводится множество явлений. Центральный узел-принцип, лучи к явлениям.
// Центр — авто-фрейм круга под текст фиксированной ширины: подпись «в вечном
// движении» гарантированно внутри круга (раньше вылезала за края).
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let C = (0, 0)
  let rC = 1.45   // радиус центра (бокс 2.2см + padding) — старт лучей за краем

  // ── явления вокруг, лучи от края центра к подписям
  let phen = (
    (135deg,  [вода\
замерзает]),
    (45deg,   [пахнет\
цветок]),
    (-135deg, [дерево\
держит форму]),
    (-45deg,  […и многое\
другое]),
  )
  let Rp = 3.4
  for p in phen {
    let a = p.at(0)
    let pt = (Rp * calc.cos(a), Rp * calc.sin(a))
    let from = (rC * calc.cos(a), rC * calc.sin(a))
    let to = ((Rp - 0.8) * calc.cos(a), (Rp - 0.8) * calc.sin(a))
    line(from, to, stroke: (paint: OLIVE, thickness: 0.9pt), mark: (end: ">", fill: OLIVE, scale: 0.45))
    content(pt, text(size: 8.5pt)[#align(center, p.at(1))])
  }

  // ── центр: один принцип (авто-фрейм круга → текст всегда внутри)
  content(C, box(width: 2.2cm)[#align(center)[
    #text(size: 10pt)[всё из атомов] \
    #text(size: 8pt, fill: OLIVE)[в вечном движении]
  ]], frame: "circle", padding: 6pt,
     fill: SUN.lighten(60%), stroke: (paint: INK, thickness: 1.1pt))

  // ── подпись снизу
  content((0, -4.2), text(size: 9.5pt)[один принцип — и из него выводится множество явлений])
})
