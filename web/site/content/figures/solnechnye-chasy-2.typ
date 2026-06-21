#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Солнечные часы (вид сверху): циферблат с часовыми метками, гномон в центре,
// тень падает на метку = час. Полуденная тень самая короткая и смотрит на север.
// Иллюстрирует L1 (час / север), отлично от L2 (геометрия Эратосфена).
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let O = (0, 0)
  let R = 2.7
  let pa(a) = (R * calc.cos(a), R * calc.sin(a))

  // ── дуга циферблата (нижняя часть круга, по которой ходит конец тени)
  arc(O, start: 18deg, stop: 162deg, radius: R, anchor: "origin",
    stroke: (paint: INK, thickness: LINE))

  // ── угол, на который указывает тень (= одна из часовых меток)
  let shadow-angle = 70deg

  // ── тень: олива от центра-гномона РОВНО к часовой метке («сейчас» — час дня).
  //    Остриё тени останавливается у ВНУТРЕННЕГО края засечки (R-0.28); сама
  //    засечка (R-0.28 → R) подсвечена оливой и торчит наружу за остриё, так
  //    что радиальная линия тени её не закрывает, а наглядно в неё упирается.
  let sh-inner = ((R - 0.28) * calc.cos(shadow-angle), (R - 0.28) * calc.sin(shadow-angle))
  line(O, sh-inner, stroke: (paint: OLIVE, thickness: 1.4pt))

  // ── часовые метки: засечки вдоль дуги; полдень (90°) выделен ink,
  //    метка под тенью выделена оливой (рисуем после тени, поверх неё)
  let hours = (30deg, 50deg, 70deg, 90deg, 110deg, 130deg, 150deg)
  for a in hours {
    let p1 = pa(a)
    let p2 = ((R - 0.28) * calc.cos(a), (R - 0.28) * calc.sin(a))
    let noon = (calc.abs(a / 1deg - 90) < 1)
    let hit = (calc.abs(a / 1deg - shadow-angle / 1deg) < 1)
    let col = if noon { INK } else if hit { OLIVE } else { SAND }
    let th = if noon { 1.3pt } else if hit { 1.9pt } else { 0.7pt }
    line(p2, p1, stroke: (paint: col, thickness: th))
  }

  // ── север: стрелка вверх к полуденной метке + подпись
  line((0, R + 0.15), (0, R + 0.95), stroke: (paint: INK, thickness: 1.0pt),
    mark: (start: ">", fill: INK, scale: 0.5))
  content((0, R + 1.12), anchor: "south", text(size: 9.5pt)[север (полдень)])

  // подпись «тень» — СЛЕВА от линии (в чистой зоне, не на ней)
  let sh = pa(shadow-angle)
  content((sh.at(0) * 0.5 - 0.2, sh.at(1) * 0.5 + 0.05), anchor: "east",
    text(size: 9.5pt, fill: OLIVE)[тень])

  // ── гномон: в виде сверху — точка-узел в центре; подпись слева-снизу, у дуги чисто
  circle(O, radius: 0.1, fill: INK, stroke: none)
  content((-0.22, -0.02), anchor: "east", text(size: 9pt, fill: OLIVE)[гномон])

  // ── подпись: что показывает тень
  content((0, -0.65), text(size: 9.5pt)[конец тени на метке = текущий час])
})
