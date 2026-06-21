#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Профиль лесной подстилки: непрерывный переход свежий лист → почва.
// В ОТЛИЧИЕ от слоистой колонки geo-srez здесь НЕТ резких границ — суть сюжета
// в том, что живое и неживое перетекают друг в друга. Поэтому колонка залита
// НАСТОЯЩИМ линейным градиентом (gradient.linear по высоте), а не дискретными
// слоями — на рендере между свежим листом и почвой ни одной видимой ступени.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let x0 = 0.0
  let w = 2.4
  let ytop = 5.0
  let ybot = 0.0
  // верх — светлая листовая зелень, низ — тёмная почва (INK)
  let top = rgb(157, 161, 127)
  let bot = rgb(40, 38, 33)
  // настоящий линейный градиент по высоте: сверху лист, снизу почва.
  // dir: btt → 0% (start) внизу, 100% (end) вверху, поэтому почва-лист.
  rect((x0, ybot), (x0 + w, ytop),
    fill: gradient.linear(bot, top, dir: btt),
    stroke: (paint: INK, thickness: LINE))

  // листик-иконка над колонкой — «вход» свежей листвы
  content((x0 + w / 2, ytop + 0.05), anchor: "south", image("icons/leaf.svg", width: 0.6cm))

  // подписи справа, привязанные к глубинам (выноска-чёрточка к колонке)
  let tick(yfrac, label, col) = {
    let y = ytop - (ytop - ybot) * yfrac
    line((x0 + w, y), (x0 + w + 0.3, y), stroke: (paint: SAND, thickness: 0.6pt))
    content((x0 + w + 0.42, y), anchor: "west", text(size: 10pt, fill: col)[#label])
  }
  tick(0.10, [свежие листья], INK)
  tick(0.37, [прошлогодние, ломкие], OLIVE)
  tick(0.63, [не отличить лист от почвы], OLIVE)
  tick(0.90, [почва], INK)

  // слева — вертикальная ось «глубже» + ремарка «резкой границы нет»
  line((x0 - 0.45, ytop), (x0 - 0.45, ybot),
    stroke: (paint: INK, thickness: 0.8pt), mark: (end: ">", fill: INK, scale: 0.5))
  content((x0 - 0.62, (ytop + ybot) / 2), anchor: "south", angle: 90deg,
    text(size: 9.5pt, fill: OLIVE)[глубже])
})
