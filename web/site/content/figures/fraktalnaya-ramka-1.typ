#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Box-counting (метод подсчёта клеток). Один и тот же ветвящийся контур —
// абстрактное «дерево» оврага (ломаная из отрезков-ветвей) — накрыт квадратной
// сеткой. Считаем клетки, которые контур ЗАДЕВАЕТ (закрашены SAND). Слева крупный
// шаг ε → мало клеток N₁; справа шаг вдвое мельче ε/2 → клеток N₂ ≈ N₁·2^D.
// Снизу мини-график ln N от ln(1/ε): точки на прямой, наклон = размерность D.
// Чистая геометрия, без реалистичного оврага.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // ── КОНТУР: ветвящаяся ломаная в квадрате [0,4]×[0,4] (локальные координаты).
  //    Ствол снизу вверх + раздваивающиеся ветви. Один набор на обе панели.
  let trunk = (
    ((2.0, 0.15), (2.0, 1.3)),                 // ствол
    ((2.0, 1.3),  (1.05, 2.35)),               // левая большая ветвь
    ((2.0, 1.3),  (2.95, 2.3)),                // правая большая ветвь
    ((1.05, 2.35),(0.5, 3.35)),                // левая→верх-влево
    ((1.05, 2.35),(1.55, 3.05)),               // левая→верх-вправо
    ((2.95, 2.3), (2.55, 3.4)),                // правая→верх-влево
    ((2.95, 2.3), (3.55, 2.95)),               // правая→верх-вправо
    // мелкие отвершки на концах — третий уровень ветвления.
    // Чем гуще сеть, тем сильнее N растёт при измельчении сетки (отношение ближе
    // к ~3 ⇒ D ближе к ~1,6 — как у реальной овражной/речной сети, см. L3).
    // D НЕ хардкодим: график ниже берёт наклон из фактических счётчиков cntL/cntR.
    ((0.5, 3.35), (0.25, 3.75)),               // отвершки левой верхней ветви
    ((0.5, 3.35), (0.8, 3.7)),
    ((1.55, 3.05),(1.35, 3.75)),               // отвершки средней ветви
    ((1.55, 3.05),(1.9, 3.5)),
    ((2.55, 3.4), (2.35, 3.8)),                // отвершки правой верхней ветви
    ((2.55, 3.4), (2.85, 3.75)),
    ((3.55, 2.95),(3.35, 2.6)),                // отвершки правого края
    ((3.55, 2.95),(3.85, 3.25)),
    ((0.5, 3.35), (0.3, 3.05)),                // короткие веточки второго порядка
    ((3.55, 2.95),(3.8, 2.7)),
  )

  // целочисленный пол (для индекса клетки) — чистые функции, не draw
  let ifloor(t) = calc.floor(t + 0.0)

  // множество задетых клеток: для каждого отрезка идём мелким шагом и помечаем
  // клетку (i,j) = индекс по сетке шага eps, в которой лежит точка сэмпла.
  // Возвращаем массив пар (i,j) без повторов. (n = число клеток по стороне.)
  let touched(eps, n) = {
    let seen = ()
    for seg in trunk {
      let (a, b) = seg
      let (ax, ay) = a
      let (bx, by) = b
      let len = calc.sqrt((bx - ax) * (bx - ax) + (by - ay) * (by - ay))
      // густой сэмплинг — мельче четверти клетки, чтобы не пропустить угловые
      let steps = calc.max(2, calc.ceil(len / (eps / 6)))
      for s in range(0, steps + 1) {
        let t = s / steps
        let x = ax + (bx - ax) * t
        let y = ay + (by - ay) * t
        let i = calc.min(n - 1, calc.max(0, ifloor(x / eps)))
        let j = calc.min(n - 1, calc.max(0, ifloor(y / eps)))
        let key = (i, j)
        if not seen.contains(key) { seen.push(key) }
      }
    }
    seen
  }

  // ── одна панель: origin (ox,oy), сторона side=4, шаг eps, число клеток n.
  //    Рисует закрашенные клетки → сетку → контур поверх.
  let panel(ox, oy, eps, n) = {
    let side = eps * n
    // закрашенные клетки (под сеткой и контуром)
    for cell in touched(eps, n) {
      let (i, j) = cell
      rect(
        (ox + i * eps, oy + j * eps),
        (ox + (i + 1) * eps, oy + (j + 1) * eps),
        fill: SAND.lighten(45%), stroke: none,
      )
    }
    // сетка
    for k in range(0, n + 1) {
      line((ox + k * eps, oy), (ox + k * eps, oy + side),
           stroke: (paint: SAND, thickness: 0.4pt))
      line((ox, oy + k * eps), (ox + side, oy + k * eps),
           stroke: (paint: SAND, thickness: 0.4pt))
    }
    // внешняя рамка чуть жирнее — аккуратный квадрат
    rect((ox, oy), (ox + side, oy + side), stroke: (paint: INK, thickness: 0.8pt))
    // контур поверх (один штрих)
    for seg in trunk {
      let (a, b) = seg
      let (ax, ay) = a
      let (bx, by) = b
      line((ox + ax, oy + ay), (ox + bx, oy + by),
           stroke: (paint: INK, thickness: 1.5pt))
    }
  }

  // ── ЛЕВАЯ панель: крупная сетка ε (4 клетки по стороне)
  let LX = 0.0
  let LY = 1.4
  let nL = 4
  let epsL = 4.0 / nL            // = 1.0 → сторона панели 4 см
  panel(LX, LY, epsL, nL)
  let cntL = touched(epsL, nL).len()
  content((LX + 2.0, LY + 4.0 + 0.5), text(size: 10pt)[шаг $epsilon$])
  content((LX + 2.0, LY - 0.55), text(size: 10.5pt, fill: OLIVE)[$N_1 = #cntL$ клеток])

  // ── ПРАВАЯ панель: шаг вдвое мельче ε/2 (8 клеток по стороне)
  let RX = 5.4
  let RY = 1.4
  let nR = 8
  let epsR = 4.0 / nR           // = 0.5 → та же сторона 4 см
  panel(RX, RY, epsR, nR)
  let cntR = touched(epsR, nR).len()
  content((RX + 2.0, RY + 4.0 + 0.5), text(size: 10pt)[шаг $epsilon \/ 2$])
  content((RX + 2.0, RY - 0.55), text(size: 10.5pt, fill: OLIVE)[$N_2 = #cntR$ клеток])

  // ── стрелка «мельчим сетку» между панелями
  line((LX + 4.0 + 0.25, LY + 2.0), (RX - 0.25, RY + 2.0),
       mark: (end: ">", fill: OLIVE), stroke: (paint: OLIVE, thickness: 0.7pt))
  content(((LX + 4.0 + RX) / 2, LY + 2.0 + 0.32),
          text(size: 8.5pt, fill: OLIVE)[мельче сетка])

  // ════════ МИНИ-ГРАФИК снизу: ln N от ln(1/ε); наклон = D ════════
  // Отдельная чистая полоса ПОД панелями (панели y∈[1.4,5.4], метки ~0.85).
  // Две точки = (ε; N₁) и (ε/2; N₂) из панелей выше → лежат на прямой, наклон = D.
  let GY = -3.7                 // origin графика (y) — ниже подписей N
  let gh = 2.7                  // высота осей
  let gw = 3.6                  // длина оси X
  // центрируем график по горизонтали под обеими панелями (центр ≈ 4.7)
  let GX = 4.7 - gw / 2 - 0.2

  // оси
  line((GX, GY), (GX + gw, GY), mark: (end: ">", fill: INK))      // X: ln(1/ε)
  line((GX, GY), (GX, GY + gh), mark: (end: ">", fill: INK))      // Y: ln N
  content((GX + gw + 0.12, GY), anchor: "west", text(size: 9.5pt)[$ln(1 \/ epsilon)$])
  content((GX, GY + gh + 0.28), anchor: "south", text(size: 9.5pt)[$ln N$])

  // ДВЕ точки = (ε; N₁) и (ε/2; N₂) — ровно то, что измерено в панелях.
  // Наклон D берём из ФАКТИЧЕСКИХ счётчиков, чтобы график не противоречил панелям.
  let D = calc.log(cntR / cntL) / calc.log(2)   // = log₂(N₂/N₁)
  let x1 = 0.95
  let x2 = 1.95
  let baseY = 0.3
  let yOf(x) = baseY + D * (x - x1)
  let pts = ((x1, yOf(x1)), (x2, yOf(x2)))
  // прямая через две точки (чуть продлена за крайние — тренд)
  line((GX + x1 - 0.35, GY + yOf(x1 - 0.35)), (GX + x2 + 0.35, GY + yOf(x2 + 0.35)),
       stroke: (paint: OLIVE, thickness: 1.3pt))
  // точки-маркеры
  for p in pts {
    circle((GX + p.at(0), GY + p.at(1)), radius: 0.08, fill: INK, stroke: none)
  }
  // тонкие пунктиры от точек к осям + метки ln N₁, ln N₂
  for (p, lab) in ((pts.at(0), $ln N_1$), (pts.at(1), $ln N_2$)) {
    let px = GX + p.at(0)
    let py = GY + p.at(1)
    line((px, GY), (px, py), stroke: (paint: SAND, thickness: 0.4pt, dash: "dotted"))
    line((GX, py), (px, py), stroke: (paint: SAND, thickness: 0.4pt, dash: "dotted"))
    content((GX - 0.18, py), anchor: "east", text(size: 8pt, fill: OLIVE)[#lab])
  }

  // метка наклона у середины прямой (в чистой зоне справа-снизу от линии)
  let pm = pts.at(1)
  content((GX + pm.at(0) + 0.45, GY + pm.at(1) - 0.42), anchor: "west",
          text(size: 9.5pt, fill: OLIVE)[наклон $= D$])

  // подпись-вывод под графиком, по центру всей фигуры
  content((4.7, GY - 0.62),
          text(size: 10.5pt)[наклон прямой $=$ размерность $D$])
})
