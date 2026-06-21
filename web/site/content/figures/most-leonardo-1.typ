#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// L2: бревно ЗАЖАТО между соседями. Ключ — угол θ, на который сила прижима P
// от соседа отклонена от нормали N к грани контакта. Пока θ < ≈22° (tan θ = μ),
// трения вдоль грани хватает, бревно не выскальзывает по оси. Чем ПЛОЩЕ мост,
// тем сильнее P завалена от нормали → θ растёт → за порогом плетёнка распускается.
// НЕ наклонная плоскость с гравитацией: соседи и прижим, а не вес на склоне.
// Два случая рядом: крутой мост (θ мал, держит) и пологий (θ→22°, срыв).
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE), mark: (fill: INK, scale: 0.5))

  // ── один случай: два кружка-сечения (сосед снизу, бревно сверху) касаются в C.
  //    N — нормаль (линия центров, вертикаль). P — прижим соседа, отклонён от N
  //    на θ. F — трение вдоль грани (горизонталь). Дуга θ между N и P.
  let panel(ox, ang, fl, title, verdict, vcol) = {
    let r = 0.95
    let C = (ox, 0)
    let Cn = (ox, -r)          // центр соседа
    let Cb = (ox, r)           // центр бревна
    circle(Cn, radius: r, stroke: (paint: SAND, thickness: LINE))
    circle(Cb, radius: r, fill: SAND.lighten(72%), stroke: (paint: INK, thickness: LINE))
    content((ox, r * 2 + 0.06), anchor: "south", text(size: 8.5pt)[бревно])
    content((ox, -r * 2 - 0.08), anchor: "north", text(size: 8.5pt, fill: OLIVE)[сосед])

    // нормаль N — вертикаль вверх от C (пунктир-ось)
    line(C, (ox, 1.45), stroke: (paint: SAND, thickness: 0.7pt, dash: "dashed"))
    content((ox - 0.1, 1.5), anchor: "south-east", text(size: 8.5pt, fill: SAND.darken(25%))[$N$])

    // прижим P — отклонён от вертикали на ang (в бревно), сплошная жирная стрелка
    let pl = 1.5
    let Pe = (ox + pl * calc.sin(ang), pl * calc.cos(ang))
    line(C, Pe, stroke: (paint: INK, thickness: 1.4pt), mark: (end: ">", scale: 0.6))
    content((Pe.at(0) + 0.1, Pe.at(1) + 0.02), anchor: "west", text(size: 9pt)[$P$])

    // дуга угла между N (вертикаль) и P + метка θ в самом клине.
    // Метка лежит на биссектрисе сектора (ang/2 от вертикали) на радиусе lr —
    // так глиф θ остаётся в чистом клине между пунктиром N и стрелкой P
    // при любом ang (для узкого 13° не задевает стрелку).
    arc(C, start: 90deg, stop: 90deg - ang, radius: 0.66,
        anchor: "origin", stroke: (paint: OLIVE, thickness: 0.9pt))
    let lr = 0.92
    let lb = ang / 2
    content((ox + lr * calc.sin(lb), lr * calc.cos(lb)), text(size: 9pt, fill: OLIVE)[$theta$])

    // трение F — вдоль грани (горизонталь у C), тонкая стрелка.
    // длина fl растёт с θ: требуемое трение P·sinθ больше при площе мосте
    line(C, (ox - fl, 0), stroke: (paint: OLIVE, thickness: 0.9pt), mark: (end: ">", scale: 0.45))
    content((ox - fl - 0.04, -0.04), anchor: "east", text(size: 8pt, fill: OLIVE)[$F$])

    // вердикт под панелью
    content((ox, -r * 2 - 0.62), text(size: 8.5pt)[#title])
    content((ox, -r * 2 - 1.04), text(size: 8.5pt, fill: vcol)[#verdict])
  }

  panel(0.0, 13deg, 0.62, [крутой мост], [θ мал — зажато], OLIVE)
  panel(4.4, 22deg, 1.0, [пологий мост], [θ → 22° — срыв], INK)

  // разделитель «площе →» между случаями
  content((2.2, 0.6), text(size: 9pt, fill: SAND.darken(15%))[площе →])
  line((1.55, 0.15), (2.85, 0.15), stroke: (paint: SAND, thickness: 0.7pt, dash: "dotted"))

  // ── общий итог снизу (с воздухом от вердиктов панелей)
  content((2.2, -3.7),
    text(size: 9.5pt)[прижим $P$ отклонён от нормали $N$ на $theta$; пока $tan theta < mu$ ($theta < 22°$) — трения хватает])
})
