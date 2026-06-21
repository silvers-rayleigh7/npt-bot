#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Линия времени места + три дорожки-свидетеля. Абстрактная диаграмма (НЕ ландшафт).
// КЛЮЧЕВОЕ: ось РАЗОРВАНА зигзагом. Слева — «дописьменная глубь» (бронзовый век,
// ~II тыс. до н.э.) БЕЗ привязки к конкретным годам CE. Справа от слома —
// письменная эпоха с реальными годами (1556, 1648, 1782–89).
// Три дорожки-свидетеля:
//   предание — широкая размытая полоса, тянется из дописьменной глуби, к нашим дням тает;
//   документы — узкая точная линия, начинается у порога письменности (1556);
//   археология — отдельные точки-«островки» ТОЛЬКО в дописьменной глуби (бронзовый век).
// Городище марийцев — веха без даты («?») в дописьменной зоне, не привязана к году.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE), mark: (fill: INK, scale: 0.55))

  // ── РАЗОРВАННАЯ ось. Холст по X от 0 до 12.5.
  //    Левый сегмент [Xa0..Xa1] = «дописьменная глубь» (бронзовый век, без лет CE).
  //    Зигзаг-слом в Xbreak. Правый сегмент [Xb0..X1] = письменная эпоха (годы CE).
  let Xa0 = 0.0
  let Xa1 = 3.1            // конец дописьменной зоны
  let Xbreak = 3.55        // центр зигзага-слома
  let Xb0 = 4.0            // начало письменной эпохи на холсте
  let X1 = 12.0            // правый край (наши дни условно)

  // письменная эпоха: реальные годы → доля правого сегмента
  let Yb0 = 1540           // чуть раньше 1556, чтобы засечка не на самом краю
  let Yb1 = 1850
  let xt = year => Xb0 + (year - Yb0) / (Yb1 - Yb0) * (X1 - Xb0)

  // ── таймлайн-ось сверху (с разрывом-зигзагом)
  let axisY = 4.55
  // левый сегмент
  line((Xa0, axisY), (Xa1, axisY), stroke: (paint: INK, thickness: 1.3pt))
  // зигзаг-слом
  let zz = 0.13
  line((Xa1, axisY), (Xbreak - 0.18, axisY + zz), (Xbreak + 0.18, axisY - zz), (Xb0, axisY),
       stroke: (paint: INK, thickness: 1.3pt))
  // правый сегмент со стрелкой
  line((Xb0, axisY), (X1 + 0.45, axisY), mark: (end: ">"),
       stroke: (paint: INK, thickness: 1.3pt))
  content((X1 + 0.62, axisY), anchor: "west", text(size: 9pt, fill: OLIVE)[время])

  // подпись дописьменной зоны под левым сегментом
  content(((Xa0 + Xa1) / 2, axisY - 0.42), text(size: 8.5pt, fill: OLIVE)[
    дописьменная глубь])
  content(((Xa0 + Xa1) / 2, axisY - 0.74), text(size: 8pt, fill: OLIVE)[
    (бронзовый век, ~II тыс. до н.э.)])

  // ── веха на оси: тик вверх + подпись (год снизу у оси, событие сверху).
  let milestone(x, ev, yr, hi) = {
    line((x, axisY), (x, axisY + 0.22), stroke: (paint: INK, thickness: 1.3pt))
    circle((x, axisY), radius: 0.075, fill: INK, stroke: none)
    content((x, axisY + (if hi { 0.78 } else { 0.45 })), text(size: 9.5pt)[#ev])
    content((x, axisY - 0.30), text(size: 8.5pt, fill: OLIVE)[#yr])
  }
  // городище — в дописьменной зоне; даты НЕТ («?»), а год-подпись вынесена в само
  //    событие, чтобы не сталкиваться с подписью зоны под осью.
  let gx = Xa0 + 0.75
  line((gx, axisY), (gx, axisY + 0.22), stroke: (paint: INK, thickness: 1.3pt))
  circle((gx, axisY), radius: 0.075, fill: INK, stroke: none)
  content((gx, axisY + 0.78), text(size: 9.5pt)[городище])
  content((gx, axisY + 0.48), text(size: 8.5pt, fill: OLIVE)[(дата ?)])
  // письменные вехи — на реальных годах
  milestone(xt(1556), "слобода", "1556", false)
  milestone(xt(1648), "Введенская", "1648", true)
  milestone(xt(1785), "церковь", "1782–89", false)

  // ════════ ТРИ ДОРОЖКИ-СВИДЕТЕЛЯ (под осью) ════════
  let tr_pred = 3.05       // предание
  let tr_doc  = 2.15       // документы
  let tr_arch = 1.25       // археология
  let labx = -0.35         // правый край подписей дорожек (слева от холста)

  content((labx, tr_pred), anchor: "east", text(size: 9.5pt)[предание])
  content((labx, tr_doc),  anchor: "east", text(size: 9.5pt)[документы])
  content((labx, tr_arch), anchor: "east", text(size: 9.5pt)[археология])

  // ── ПРЕДАНИЕ: широкая размытая полоса штриховкой. Из дописьменной глуби,
  //    к правому краю штрихи редеют — память ТАЕТ, не обрываясь стеной.
  let pb_top = tr_pred + 0.27
  let pb_bot = tr_pred - 0.27
  let pb_x0 = Xa0
  let pb_x1 = xt(1730)    // тает, не дотягивая до наших дней
  line((pb_x0, pb_top), (xt(1640), pb_top), stroke: (paint: SAND, thickness: 0.5pt))
  line((pb_x0, pb_bot), (xt(1640), pb_bot), stroke: (paint: SAND, thickness: 0.5pt))
  let kn = 34
  for i in range(0, kn) {
    let t = i / kn
    let x = pb_x0 + (pb_x1 - pb_x0) * t
    let frac = if t < 0.72 { 1.0 } else { calc.max(0.0, 1.0 - (t - 0.72) / 0.28) }
    let y0 = pb_bot
    let y1 = pb_bot + (pb_top - pb_bot) * frac
    line((x, y0), (x + 0.30 * frac, y1), stroke: (paint: SAND, thickness: 0.45pt))
  }

  // ── ДОКУМЕНТЫ: узкая точная сплошная линия, НАЧИНАЕТСЯ у порога письменности (1556).
  let dx0 = xt(1556)
  line((dx0, tr_doc), (X1, tr_doc), stroke: (paint: INK, thickness: 1.5pt))
  line((dx0, tr_doc - 0.16), (dx0, tr_doc + 0.16), stroke: (paint: INK, thickness: 1.5pt))
  for yr in (1556, 1648, 1785) {
    circle((xt(yr), tr_doc), radius: 0.06, fill: INK, stroke: none)
  }

  // ── АРХЕОЛОГИЯ: отдельные точки-«островки» ТОЛЬКО в дописьменной глуби
  //    (стоянки бронзового века). Дискретна: где копали — там точка, между — пустота.
  //    НИ ОДНОЙ точки в письменной эпохе — археология достаёт туда, куда документы нет.
  let arch_x = (Xa0 + 0.55, Xa0 + 1.35, Xa0 + 2.35)
  for x in arch_x {
    circle((x, tr_arch), radius: 0.11, fill: OLIVE, stroke: none)
  }

  // ── ПОРОГ ПИСЬМЕННОСТИ: вертикаль у слома — слева бумаг нет.
  let bz = (Xa1 + Xb0) / 2
  line((bz, tr_arch - 0.42), (bz, axisY - 0.95),
       stroke: (paint: SAND, thickness: 0.5pt, dash: "dotted"))
  content((bz, tr_arch - 0.70), text(size: 8.5pt, fill: OLIVE)[порог письменности])
})
