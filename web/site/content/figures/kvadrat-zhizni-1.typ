#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Вертикальный разрез «снег держит тепло» (идиом geo-srez — колонка-слои).
// Три горизонтальных слоя снизу вверх: тёплая почва ≈0° → пористый снег
// (~90% воздуха) → холодный воздух −20°. Поток тепла идёт ИЗ почвы ВВЕРХ:
// толстая стрелка в почве, в снегу истончается и гаснет (прерывистая, без
// остриёв) — снег ловит тепло. Абстрактная диаграмма, без реализма.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE), mark: (fill: INK, scale: 0.55))
  let X0 = 0
  let X1 = 4.4

  // ── слой: полоса + двухстрочная подпись справа (название — пояснение)
  let band(y0, y1, fillc, name, note) = {
    rect((X0, y0), (X1, y1), fill: fillc, stroke: INK)
    content((X1 + 0.45, (y0 + y1) / 2 + 0.20), anchor: "west", text(size: 10.5pt)[#name])
    content((X1 + 0.45, (y0 + y1) / 2 - 0.22), anchor: "west", text(size: 9pt, fill: OLIVE)[#note])
  }

  // снизу вверх (y растёт вверх): почва · снег · воздух
  band(0.0, 1.5, OLIVE.lighten(8%),  "тёплая почва", [держит $approx 0°$])
  band(1.5, 4.0, rgb("#EAEEF2"),     "снег",          [пористый, $tilde 90%$ воздуха])
  band(4.0, 5.3, SAND.lighten(70%),  "холодный воздух", [мороз $-20°$])

  // граница почва↔снег и снег↔воздух — чуть жирнее (читаемость слоёв)
  line((X0, 1.5), (X1, 1.5), stroke: (paint: INK, thickness: 0.9pt))
  line((X0, 4.0), (X1, 4.0), stroke: (paint: INK, thickness: 0.9pt))

  // ── снежинка-иконка в слое снега (узнаваемость), сбоку слева внутри полосы
  content((0.62, 3.45), image("icons/snowflake.svg", width: 0.62cm))

  // ── ПОТОК ТЕПЛА: три колонки. Снизу (почва) — толстая сплошная стрелка вверх,
  //    в снегу — истончается и гаснет: короткие прерывистые штрихи, без остриёв.
  //    Тепло НЕ доходит до воздуха → снег ловит тепло почвы.
  let xs = (1.7, 2.55, 3.4)
  for x in xs {
    // в почве: толстая сплошная стрелка — поток сильный, идёт от глубины вверх
    line((x, 0.28), (x, 1.5), stroke: (paint: SUN, thickness: 2.6pt), mark: (end: ">", fill: SUN, scale: 0.7))
    // в снегу: поток истончается и затухает — единый путь без разрывов,
    // продолжается прямо от конца сплошного сегмента, всё тоньше и бледнее
    line((x, 1.5), (x, 2.05), stroke: (paint: SUN, thickness: 1.5pt))
    line((x, 2.05), (x, 2.6), stroke: (paint: SUN.lighten(25%), thickness: 1.0pt, dash: "dotted"))
    line((x, 2.6), (x, 3.05), stroke: (paint: SUN.lighten(45%), thickness: 0.7pt, dash: "dotted"))
    // выше — поток погас (до воздуха тепло не доходит)
  }

  // ── сравнение теплопроводности λ слева от колонки (в чистой зоне):
  //    снег вчетверо хуже проводит тепло, чем воздух → потому и держит.
  content((-1.95, 3.05), anchor: "west", text(size: 9pt, fill: OLIVE)[$lambda$ снега 0,1])
  content((-1.95, 2.62), anchor: "west", text(size: 9pt, fill: OLIVE)[$lambda$ воздуха 0,025])
  content((-1.95, 2.16), anchor: "west", text(size: 8pt, fill: SAND)[Вт/(м·К)])

  // ── подпись-вывод снизу по центру колонки
  content((X1 / 2, -0.62), text(size: 11pt)[снег ловит тепло почвы])
})
