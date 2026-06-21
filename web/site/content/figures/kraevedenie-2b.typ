#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// L1, ОДНА мысль — собственный хук уровня: «первое имя СТЁРТО».
// НЕ повтор всей хронологии (это несёт фигура L2). Здесь — одно место как
// стопка слоёв-имён, легших на него сверху вниз во времени: самый ранний,
// нижний слой — выцветший, перечёркнутый, без названия («?»): имя стёрто,
// письменности не было. Над ним — два чётких сохранившихся имени.
// Тест «закрой подписи»: одна площадка-место, на ней слои-таблички, нижняя —
// стёртая → «первое имя потеряно».
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let cx = 0.0             // центр стопки по X
  let plate(yc, body, col, th, dash) = {
    content((cx, yc), body, frame: "rect", padding: 5pt,
      fill: white, stroke: (paint: col, thickness: th, dash: dash))
  }

  // ── ОДНА площадка-«место» снизу: неизменна, на неё ложатся имена.
  let baseY = -0.55
  line((-2.5, baseY), (2.5, baseY), stroke: (paint: INK, thickness: 1.6pt))
  line((-2.5, baseY - 0.12), (-2.5, baseY + 0.12), stroke: (paint: INK, thickness: 1.6pt))
  line((2.5, baseY - 0.12), (2.5, baseY + 0.12), stroke: (paint: INK, thickness: 1.6pt))
  content((2.7, baseY), anchor: "west", text(size: 9pt, fill: OLIVE)[одно место])

  // ── СЛОИ-ИМЕНА снизу вверх (раньше → позже). Нижний — стёртый.
  // нижний слой: первое имя, СТЁРТО — выцветшая пунктирная рамка, имя нечитаемо («?»).
  //    Само НАЗВАНИЕ заменено на «?» — стёрто; пояснение, какого рода имя, — мелким.
  let y0 = 0.55
  plate(y0,
    box(width: 3.0cm)[#align(center)[
      #text(size: 8pt, fill: SAND.darken(12%))[(имя городища марийцев)] \
      #text(size: 15pt, fill: SAND.darken(12%))[?]]],
    SAND.darken(10%), 0.9pt, "dashed")

  // средний слой: Басурманская 1556 — чёткое
  let y1 = 2.0
  plate(y1,
    box(width: 3.0cm)[#align(center)[
      #text(size: 9.5pt)[Басурманская] \ #text(size: 8.5pt, fill: OLIVE)[1556]]],
    INK, 1.0pt, none)

  // верхний слой: Введенская 1648 — чёткое
  let y2 = 3.25
  plate(y2,
    box(width: 3.0cm)[#align(center)[
      #text(size: 9.5pt)[Введенская] \ #text(size: 8.5pt, fill: OLIVE)[1648]]],
    INK, 1.0pt, none)

  // ── связь слоёв с местом: тонкий «поводок» от площадки вверх сквозь слои.
  line((cx, baseY + 0.05), (cx, y0 - 0.40), stroke: (paint: INK, thickness: 0.6pt))

  // ── подпись-итог сверху, с воздухом
  content((cx, y2 + 1.1),
    text(size: 9.5pt)[первое имя стёрто — \ письменности не было])
})
