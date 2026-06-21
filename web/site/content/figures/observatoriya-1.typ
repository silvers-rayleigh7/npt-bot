#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Прямоугольный треугольник горизонта. Земля — дуга окружности с центром O внизу.
// Наблюдатель на высоте h над поверхностью: вертикаль O→глаз = R+h. Касательный
// луч от глаза до точки касания T на дуге — искомое расстояние d. Радиус R = OT
// перпендикулярен касательной (прямой угол в T). Абстрактная геометрия, без
// реалистичных объектов — в идиоме geo-srez/belaya-bereza.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE), mark: (fill: INK, scale: 0.5))

  let R = 5.0
  let h = 0.9
  let L = R + h            // O → глаз наблюдателя
  let O = (0, 0)
  let P = (0, L)           // глаз наблюдателя (вершина вертикали)
  // точка касания: угол от вертикали OP равен arccos(R/L)
  let aT = 90deg - calc.acos(R / L)           // угол T от оси +x
  let T = (R * calc.cos(aT), R * calc.sin(aT))
  // точка на поверхности прямо под наблюдателем (основание высоты h)
  let S = (0, R)

  // ── дуга Земли: часть окружности с центром O, вокруг T и вершины S
  arc(O, start: 30deg, stop: 100deg, radius: R, anchor: "origin")

  // ── вертикаль O → глаз (R + h): радиус R до поверхности + высота h над ней
  line(O, P)

  // ── радиус R = O T (к точке касания)
  line(O, T)

  // ── касательный луч d: от глаза наблюдателя до точки касания T (горизонт)
  line(P, T)

  // ── прямой угол в T (между радиусом OT и касательной TP)
  let qn(a, b, s) = {       // единичный вектор от a к b, домноженный на s
    let dx = b.at(0) - a.at(0)
    let dy = b.at(1) - a.at(1)
    let n = calc.sqrt(dx * dx + dy * dy)
    (dx / n * s, dy / n * s)
  }
  let q = 0.34
  let uO = qn(T, O, q)      // вдоль TO
  let uP = qn(T, P, q)      // вдоль TP
  let c1 = (T.at(0) + uO.at(0), T.at(1) + uO.at(1))
  let c3 = (T.at(0) + uP.at(0), T.at(1) + uP.at(1))
  let c2 = (T.at(0) + uO.at(0) + uP.at(0), T.at(1) + uO.at(1) + uP.at(1))
  line(c1, c2, c3, stroke: (paint: INK, thickness: LINE))

  // ── узлы
  circle(O, radius: 0.05, fill: INK, stroke: none)
  circle(P, radius: 0.05, fill: INK, stroke: none)
  circle(T, radius: 0.05, fill: INK, stroke: none)

  // ── подписи (воздух у каждой; габариты учтены)
  content((O.at(0) - 0.34, O.at(1) - 0.04), text(size: 11pt)[$O$])
  // R+h — вдоль вертикали, слева, в её нижней половине (вдали от дуги и узлов)
  content((-0.62, R / 2 + 0.15), anchor: "east", text(size: 10.5pt)[$R + h$])
  // h — короткий участок вертикали над поверхностью (S→глаз), справа от линии
  content((0.30, (R + L) / 2), anchor: "west", text(size: 10.5pt, fill: OLIVE)[$h$])
  // R — посередине радиуса OT, чуть в сторону от линии (вправо-вниз)
  content((T.at(0) / 2 + 0.34, T.at(1) / 2 - 0.20), text(size: 10.5pt)[$R$])
  // d — посередине касательного луча PT, со стороны вне треугольника (вправо-вверх)
  content((
    (P.at(0) + T.at(0)) / 2 + 0.40,
    (P.at(1) + T.at(1)) / 2 + 0.18,
  ), text(size: 10.5pt)[$d$])
  // T — у точки касания, со стороны дуги (вправо)
  content((T.at(0) + 0.30, T.at(1) + 0.04), anchor: "west", text(size: 11pt)[$T$])
  // наблюдатель — подпись у глаза (вершина), над узлом
  content((P.at(0), P.at(1) + 0.36), text(size: 9pt, fill: OLIVE)[наблюдатель])
  // горизонт — ниже точки касания, в чистой зоне под дугой (дуга уходит вправо-вниз,
  // подпись смещена левее и опущена так, чтобы её прямоугольник целиком лежал ниже кривой)
  content((T.at(0) - 0.45, T.at(1) - 1.25), anchor: "west", text(size: 9pt, fill: OLIVE)[горизонт])
})
