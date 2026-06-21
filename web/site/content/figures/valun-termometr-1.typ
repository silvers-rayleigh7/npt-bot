#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Идея L2: один и тот же поток лучей под разным углом к поверхности освещает
// РАЗНУЮ площадь. Отвесно (90°) — узкое пятно (1×), полого (30°) — вдвое шире
// (2×), потому что S ∝ 1/sin α. АБСТРАКТНАЯ диаграмма (в идиоме geo-srez):
// горизонтальная линия = поверхность, пучок параллельных стрелок = поток,
// жирный отрезок = пятно. Никакого реалистичного камня/солнца.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE), mark: (fill: INK, scale: 0.5))

  // Геометрия: 5 параллельных лучей, поперечный шаг между ними = d.
  // Ширина пятна = (поперечная ширина пучка) / sin α. При 90° → как есть,
  // при 30° → вдвое шире (sin30°=0,5). Поперечный шаг d одинаков в обеих
  // панелях → поток (плотность лучей поперёк) РАВЕН.
  let d = 0.42            // поперечный шаг между лучами
  let n = 5               // число лучей (одинаково слева и справа)
  let L = 2.1             // длина луча (визуальная)
  let surf = 0.0          // уровень поверхности (y)

  // (CeTZ-функции рисования НЕ должны возвращать значения — canvas падает.
  //  Поэтому ширину пятна считаем заранее чистой функцией.)
  let spanOf(alpha) = (n - 1) * (d / calc.sin(alpha * 1deg))  // ширина пятна по поверхности

  // ── одна панель: пучок из n параллельных лучей под углом α, центр пятна в cx
  let panel(cx, alpha) = {
    let a = alpha * 1deg
    let dx = calc.cos(a)          // вдоль луча: вниз-вправо (cos a, -sin a)
    let dy = calc.sin(a)
    let stepx = d / dy            // горизонтальный шаг следов лучей по поверхности
    let span = (n - 1) * stepx    // полная ширина пятна
    let x0 = cx - span / 2        // левый край пятна
    // поверхность (горизонтальная линия) с запасом по краям
    line((x0 - 1.0, surf), (x0 + span + 1.0, surf), stroke: (paint: INK, thickness: 1.0pt))
    // короткие штрихи-«грунт» под поверхностью
    for k in range(0, 13) {
      let hx = x0 - 0.9 + k * (span + 1.8) / 12
      line((hx, surf), (hx - 0.16, surf - 0.22), stroke: (paint: SAND, thickness: 0.55pt))
    }
    // пучок параллельных стрелок: остриё точно на поверхности
    for i in range(0, n) {
      let fx = x0 + i * stepx
      line((fx + dx * L, surf + dy * L), (fx, surf), mark: (end: ">"))
    }
    // ПЯТНО: жирный олива-отрезок на поверхности + засечки на краях
    line((x0, surf), (x0 + span, surf), stroke: (paint: OLIVE, thickness: 2.8pt))
    line((x0, surf - 0.13), (x0, surf + 0.13), stroke: (paint: OLIVE, thickness: 1.6pt))
    line((x0 + span, surf - 0.13), (x0 + span, surf + 0.13), stroke: (paint: OLIVE, thickness: 1.6pt))
  }

  // ── ЛЕВАЯ панель: отвесно, 90°
  let LX = 2.6
  let lSpan = spanOf(90)
  panel(LX, 90)
  // угол луч↔поверхность У ОСНОВАНИЯ правого луча. 90° = канонический квадратик.
  let lFoot = LX + lSpan / 2
  let rs = 0.26
  line((lFoot, surf + rs), (lFoot + rs, surf + rs), stroke: (paint: INK, thickness: 0.7pt))
  line((lFoot + rs, surf + rs), (lFoot + rs, surf), stroke: (paint: INK, thickness: 0.7pt))
  content((lFoot + 0.62, surf + 0.42), text(size: 10pt)[$90°$])
  content((LX, surf - 0.92), text(size: 11pt, fill: OLIVE)[$1×$])
  content((LX, surf + 2.7), text(size: 10pt)[отвесно])

  // ── ПРАВАЯ панель: полого, 30°
  let RX = 9.2
  let rSpan = spanOf(30)
  panel(RX, 30)
  // дуга угла МЕЖДУ поверхностью и падающим лучом, у основания правого луча
  let rFoot = RX + rSpan / 2
  arc((rFoot, surf), start: 0deg, stop: 30deg, radius: 0.95, stroke: (paint: INK, thickness: 0.7pt))
  content((rFoot + 1.22, surf + 0.3), text(size: 10pt)[$30°$])
  content((RX, surf - 0.92), text(size: 11pt, fill: OLIVE)[$2×$])
  content((RX, surf + 2.7), text(size: 10pt)[полого])

  // ── ВЫВОД под сценой, по центру всей фигуры
  let midx = (LX + RX) / 2
  content((midx, surf - 1.78),
    text(size: 10.5pt)[тот же поток — вдвое больше площади #h(0.25em) $arrow.r$ #h(0.25em) вдвое меньше тепла])
  content((midx, surf - 2.5), text(size: 11pt, fill: OLIVE)[$S prop 1 / (sin alpha)$])
})
