#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// L1: аналогия террас. Уровень водохранилища сбрасывали рывками; на бетонной
// стенке каждая долгая задержка воды оставила горизонтальную полосу-отметку.
// Чем выше полоса — тем старее уровень. Та же логика, что у речных террас.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let wx = 0.0            // бетонная стенка (вертикаль слева)
  let top = 4.2
  let waterR = 6.0       // правый край воды
  let wlev = 0.9         // текущий уровень воды

  // ── бетонная стенка
  rect((wx - 0.45, 0), (wx, top), fill: SAND.lighten(55%), stroke: (paint: INK, thickness: LINE))
  // штриховка грунта за стенкой
  for k in range(0, 9) {
    let yy = 0.45 * k
    if yy <= top { line((wx - 0.45, yy), (wx - 0.72, yy + 0.25), stroke: (paint: SAND, thickness: 0.5pt)) }
  }

  // ── текущая вода (светлая заливка у стенки)
  rect((wx, 0), (waterR, wlev), fill: rgb("#E8EBE6"), stroke: none)
  line((wx, wlev), (waterR, wlev), stroke: (paint: OLIVE, thickness: 1.0pt))
  content((waterR - 0.1, wlev - 0.32), anchor: "east", text(size: 8.5pt, fill: OLIVE)[вода сейчас])

  // ── полосы прежних уровней: горизонтальные отметки на стенке (выше = старее)
  let marks = (3.6, 2.7, 1.8)
  for (i, y) in marks.enumerate() {
    line((wx, y), (wx + 2.3, y), stroke: (paint: OLIVE, thickness: 1.1pt))
    line((wx + 2.3, y), (wx + 2.3, y - 0.0), stroke: none)
  }
  // подпись отметок — выноска к верхней полосе, одна строка
  content((wx + 2.55, 3.62), anchor: "west", text(size: 8.5pt, fill: OLIVE)[прежние уровни воды])

  // ── стрелка «сброс рывками» вниз — в чистом поле правее подписи отметок
  line((wx + 5.0, 3.9), (wx + 5.0, wlev + 0.2),
       stroke: (paint: INK, thickness: 1.0pt), mark: (end: ">", fill: INK, scale: 0.5))
  content((wx + 5.2, 2.6), anchor: "west", text(size: 8.5pt)[сброс\
рывками])

  // ── «выше = старше» вертикальная пометка слева у стенки
  line((wx - 1.0, wlev), (wx - 1.0, top), stroke: (paint: INK, thickness: 0.8pt),
       mark: (end: ">", fill: INK, scale: 0.45))
  content((wx - 1.15, (wlev + top) / 2), anchor: "south", angle: 90deg,
    text(size: 8.5pt, fill: OLIVE)[выше — старше])
})
