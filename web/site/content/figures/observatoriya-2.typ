#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Широта = высота Полярной. Тот же прямоугольный треугольник, повёрнутый и
// наложенный на небо. Шар Земли (центр C), радиус в точку наблюдателя P (местная
// вертикаль), плоскость экватора (горизонталь через C), ось вращения (вертикаль) и
// параллельные лучи на далёкую Полярную (направление = ось). Угол φ между плоскостью
// экватора и радиусом CP равен широте; угол 90°−φ — между местной вертикалью и
// направлением на Полярную. Абстрактная диаграмма, без реалистичных объектов.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE), mark: (fill: INK, scale: 0.5))

  let R = 3.0
  let C = (0, 0)
  let lat = 55deg
  let P = (R * calc.cos(lat), R * calc.sin(lat))

  // ── шар Земли
  circle(C, radius: R)

  // ── плоскость экватора (горизонтальный диаметр через центр)
  line((-R - 0.7, 0), (R + 0.7, 0), stroke: (paint: SAND, thickness: LINE))

  // ── ось вращения Земли (вертикаль через центр) — направление на Полярную
  line((0, -R - 0.5), (0, R + 1.6), stroke: (paint: OLIVE, thickness: LINE, dash: "dashed"))

  // ── радиус в точку наблюдателя = местная вертикаль; продлеваем наружу
  let Vout = (P.at(0) * 1.62, P.at(1) * 1.62)
  line(C, Vout)

  // ── параллельные лучи на Полярную: из точки наблюдателя вверх (∥ оси)
  line(P, (P.at(0), P.at(1) + 1.9), stroke: (paint: OLIVE, thickness: LINE, dash: "dashed"),
    mark: (end: ">", fill: OLIVE))

  // ── дуга угла φ: между плоскостью экватора (+x) и радиусом CP, при центре C
  arc(C, start: 0deg, stop: lat, radius: 0.9, anchor: "origin")

  // ── дуга угла 90°−φ: при точке наблюдателя, между местной вертикалью (наружу, ∥ CP)
  // и направлением на Полярную (вверх). Откладываем у P.
  arc(P, start: lat, stop: 90deg, radius: 0.8, anchor: "origin")

  // ── узлы
  circle(C, radius: 0.05, fill: INK, stroke: none)
  circle(P, radius: 0.05, fill: INK, stroke: none)

  // ── подписи
  content((C.at(0) - 0.04, C.at(1) - 0.34), text(size: 11pt)[$C$])
  // φ у центра, внутри дуги, по биссектрисе угла φ
  content((1.05 * calc.cos(lat / 2), 1.05 * calc.sin(lat / 2)), text(size: 11pt)[$phi$])
  // 90°−φ у наблюдателя, по биссектрисе между вертикалью наружу и направлением вверх
  let bis = lat + (90deg - lat) / 2
  content((P.at(0) + 1.20 * calc.cos(bis), P.at(1) + 1.20 * calc.sin(bis)),
    text(size: 10pt)[$90 degree - phi$])
  // наблюдатель — у самого узла P на поверхности шара, в чистом клине справа-снизу
  // (между радиусом-вертикалью и окружностью), чтобы подпись тегала точку, а не висела в небе
  content((P.at(0) + 0.34, P.at(1) - 0.22), anchor: "west", text(size: 9pt, fill: OLIVE)[наблюдатель])
  // на Полярную — у верхней стрелки, левее радиуса чтобы не сталкиваться с «наблюдатель»
  content((P.at(0) + 0.16, P.at(1) + 1.78), anchor: "west", text(size: 9pt, fill: OLIVE)[на Полярную])
  // ось мира — вдоль пунктирной оси, вверху слева от оси
  content((-0.18, R + 1.4), anchor: "east", text(size: 9pt, fill: OLIVE)[ось мира])
  // плоскость экватора — у левого конца горизонтали
  content((-R - 0.8, -0.32), anchor: "west", text(size: 9pt, fill: SAND)[плоскость экватора])
})
