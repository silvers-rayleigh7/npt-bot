#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Опыт Эратосфена. Земля — окружность с центром O. Два радиуса к двум городам:
// Сиена (солнце в зените, радиус смотрит точно на солнце) и Александрия (радиус
// отклонён на угол β от вертикали). Параллельные лучи Солнца сверху падают
// вертикально вниз. У Сиены гномон вдоль радиуса смотрит на солнце → тени нет.
// У Александрии гномон отклонён → отбрасывает короткую тень; угол тени = β.
// Угол тени = угол между радиусами = центральный угол дуги Сиена–Александрия.
// Истинный угол 7,2° для наглядности показан крупнее (как в учебнике) —
// метка несёт точное значение. Абстрактная геометрия, без реализма.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE), mark: (fill: INK, scale: 0.5))

  let R = 3.6
  let O = (0, 0)
  // Истинный угол 7,2°; визуально раскрываем до β для читаемости дуги и тени.
  let beta = 26deg
  let lab = [7,2°]               // точная подпись угла (десятичная запятая)

  // ── направления радиусов от центра: Сиена вертикально вверх (на солнце),
  //    Александрия отклонена на β к западу (влево)
  let aS = 90deg
  let aA = 90deg + beta
  let S = (R * calc.cos(aS), R * calc.sin(aS))   // Сиена на окружности (вершина)
  let A = (R * calc.cos(aA), R * calc.sin(aA))   // Александрия (слева-сверху)

  // единичный вектор от a к b, домноженный на s
  let un(a, b, s) = {
    let dx = b.at(0) - a.at(0)
    let dy = b.at(1) - a.at(1)
    let n = calc.sqrt(dx * dx + dy * dy)
    (dx / n * s, dy / n * s)
  }

  // ── ОКРУЖНОСТЬ ЗЕМЛИ (центр O): верхняя дуга, охватывающая оба города
  arc(O, start: 50deg, stop: 165deg, radius: R, anchor: "origin")

  // ── два радиуса от центра к городам
  line(O, S)
  line(O, A)

  // ── дуга центрального угла β у центра O (между радиусами) + точная метка
  let ra = 1.15
  arc(O, start: aS, stop: aA, radius: ra, anchor: "origin",
      stroke: (paint: OLIVE, thickness: 0.9pt))
  let amid = (aS + aA) / 2
  content((calc.cos(amid) * (ra + 0.5), calc.sin(amid) * (ra + 0.5)),
          text(size: 10pt, fill: OLIVE)[#lab])
  content((calc.cos(amid) * (ra - 1.55), calc.sin(amid) * (ra - 1.55) - 0.05),
          text(size: 10.5pt)[$O$])

  // ── узлы: центр и города
  circle(O, radius: 0.06, fill: INK, stroke: none)
  circle(S, radius: 0.06, fill: INK, stroke: none)
  circle(A, radius: 0.06, fill: INK, stroke: none)

  // ════════ ПАРАЛЛЕЛЬНЫЕ ЛУЧИ СОЛНЦА (сверху, строго вертикально вниз) ════════
  let rayTop = R + 1.9
  let rayBot = R + 0.55
  for rx in (-3.0, -1.5, 0.0, 1.5, 3.0) {
    line((rx, rayTop), (rx, rayBot), mark: (end: ">", scale: 0.6))
  }
  // иконка солнца сверху по центру, в чистой зоне над лучами
  content((0, rayTop + 0.58), image("icons/sun.svg", width: 0.72cm))

  // ════════ СИЕНА: гномон вдоль радиуса (точно на солнце), тени НЕТ ════════
  let gln = 0.95                 // длина гномона
  let Sg = (S.at(0) + un(O, S, gln).at(0), S.at(1) + un(O, S, gln).at(1))
  line(S, Sg, stroke: (paint: INK, thickness: 1.7pt))
  content((Sg.at(0) + 0.34, Sg.at(1)), anchor: "west", text(size: 9.5pt)[Сиена])
  content((Sg.at(0) + 0.34, Sg.at(1) - 0.40), anchor: "west", text(size: 8.5pt, fill: OLIVE)[тени нет])

  // ════════ АЛЕКСАНДРИЯ: гномон вдоль радиуса (отклонён) + короткая тень ════════
  let Ag = (A.at(0) + un(O, A, gln).at(0), A.at(1) + un(O, A, gln).at(1))
  line(A, Ag, stroke: (paint: INK, thickness: 1.7pt))    // гномон вдоль радиуса
  content((A.at(0) - 0.32, A.at(1) + 0.34), anchor: "east", text(size: 9.5pt)[Александрия])

  // тонкий вертикальный «луч на солнце» из основания A (направление падающего света)
  // — относительно него гномон отклонён на тот же угол β, что и радиусы
  line(A, (A.at(0), A.at(1) + gln + 0.25),
       stroke: (paint: SAND, thickness: 0.6pt, dash: "dotted"))

  // дуга «угла тени» в основании A: между вертикальным лучом (90°) и гномоном (aA)
  arc(A, start: 90deg, stop: aA, radius: 0.62, anchor: "origin",
      stroke: (paint: OLIVE, thickness: 0.9pt))
  let aGmid = (90deg + aA) / 2
  content((A.at(0) + calc.cos(aGmid) * 1.06, A.at(1) + calc.sin(aGmid) * 1.06),
          text(size: 9pt, fill: OLIVE)[#lab])

  // тень: лежит ВДОЛЬ поверхности и падает ОТ солнца (влево-вниз, прочь от
  //   вертикального луча). касательная (x,y)->(-y,x), знак выбран в сторону от солнца.
  let urA = un(O, A, 1)
  let tx = -urA.at(1)            // влево-вниз = от солнца, по поверхности
  let ty = urA.at(0)
  let shadowLen = 1.05
  let Ash = (A.at(0) + tx * shadowLen, A.at(1) + ty * shadowLen)
  line(A, Ash, stroke: (paint: OLIVE, thickness: 1.5pt))
  content((Ash.at(0) - 0.12, Ash.at(1) - 0.12), anchor: "north", text(size: 8.5pt, fill: OLIVE)[тень])

  // ── ПОДПИСЬ снизу: ключевое равенство, в чистой зоне под Землёй
  content((0, -0.95),
          text(size: 10pt, fill: OLIVE)[угол тени $=$ угол между радиусами $= 1\/50$ окружности])
})
