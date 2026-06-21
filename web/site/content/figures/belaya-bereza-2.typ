#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Шкала альбедо: честное сравнение берёза ↔ тёмная кора (та же α≈0,1 из L2),
// плюс два нейтральных ориентира — асфальт (0,1) и снег (0,9). Единый идиом
// глифов: ВСЕ позиции — свотчи (как в fig1), без Lucide-иконок.
//   асфальт ≈0,1, тёмная кора ≈0,1, берёза ≈0,5, снег ≈0,9.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))
  let W = 10.5

  // ── полоса альбедо: слева тёмное (поглощает), справа светлое (отражает)
  rect((0, 0), (W, 0.55), stroke: INK, fill: gradient.linear(INK, white))

  // ── ось значений под полосой
  for v in (0.0, 0.5, 1.0) {
    let x = v * W
    line((x, 0), (x, -0.18))
    content((x, -0.46), text(size: 9pt)[#if v == 0.5 { "0,5" } else { str(int(v)) }])
  }
  content((W / 2, -1.05), text(size: 10pt)[альбедо $alpha$ — доля отражённого света])

  // ── маркер: тик от полосы вверх + α + имя (tier H высоко, L низко — без коллизий)
  let by(t) = if t == "H" { 2.25 } else { 0.95 }
  let mark(p, name, lab, t) = {
    let x = p * W
    line((x, 0.55), (x, by(t)))
    content((x, by(t) + 0.30), text(size: 8.5pt, fill: OLIVE)[$alpha approx$ #lab])
    content((x, by(t) + 0.62), text(size: 9.5pt)[#name])
  }
  // ── единый идиом: свотч-прямоугольник (как кора в fig1), глиф НАД именем
  let gy(t) = by(t) + 1.30
  let gswatch(p, t, fillc, strokec) = {
    let x = p * W
    let yy = gy(t)
    rect((x - 0.26, yy), (x + 0.26, yy + 0.46), stroke: strokec, fill: fillc)
  }
  // ── берёза: свотч тоном с полосы в точке 0,5 (средне-серый, α≈0,5) + чечевички.
  //    НЕ белый: иначе берёза «ярче» снега 0,9 и противоречит собственной шкале.
  let gbirch(p, t) = {
    let x = p * W
    let yy = gy(t)
    rect((x - 0.26, yy), (x + 0.26, yy + 0.46), stroke: INK, fill: rgb("#8E8E8B"))
    // чечевички вразнобой (как в fig1) — узнаётся берёзовая кора, не «чекбокс»
    line((x - 0.17, yy + 0.12), (x - 0.02, yy + 0.12), stroke: (paint: INK, thickness: 1.4pt))
    line((x + 0.04, yy + 0.24), (x + 0.18, yy + 0.24), stroke: (paint: INK, thickness: 1.4pt))
    line((x - 0.14, yy + 0.35), (x + 0.01, yy + 0.35), stroke: (paint: INK, thickness: 1.4pt))
  }

  // тёмная кора (та же α≈0,1 из L2) и асфальт совпадают по значению — один свотч,
  // двухстрочная подпись; берёза посередине, снег справа
  let markmulti(p, names, lab, t) = {
    let x = p * W
    line((x, 0.55), (x, by(t)))
    content((x, by(t) + 0.26), text(size: 8.5pt, fill: OLIVE)[$alpha approx$ #lab])
    content((x, by(t) + 0.74), align(center, text(size: 9.5pt)[#names]))
  }
  markmulti(0.10, [тёмная кора, \ асфальт], "0,1", "H"); gswatch(0.10, "H", INK, INK)
  mark(0.50, "берёза", "0,5", "H"); gbirch(0.50, "H")
  mark(0.90, "снег",   "0,9", "H"); gswatch(0.90, "H", rgb("#EDEDEA"), INK)
})
