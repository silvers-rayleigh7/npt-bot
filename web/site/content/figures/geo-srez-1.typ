#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Стратиграфическая колонка: старое внизу → молодое сверху.
// Четыре слоя снизу вверх — известняк (мелкое море) · песчаник (берег) ·
// рыхлые отложения (ледник/реки/ветер) · почва (наши дни). Абстрактные полосы в идиоме
// шкалы fig2, без псевдореализма. Слева — стрелка времени.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))
  let X0 = 0
  let X1 = 3.0

  // ── слой: полоса + подпись справа (порода — среда)
  let band(y0, y1, fillc, rock, env) = {
    rect((X0, y0), (X1, y1), fill: fillc, stroke: INK)
    content((X1 + 0.4, (y0 + y1) / 2 + 0.16), anchor: "west", text(size: 10.5pt)[#rock])
    content((X1 + 0.4, (y0 + y1) / 2 - 0.20), anchor: "west", text(size: 9pt, fill: OLIVE)[#env])
  }

  // снизу вверх (y растёт вверх)
  band(0.0, 1.3, SAND.lighten(58%), "известняк", "мелкое море")
  band(1.3, 2.4, SAND,              "песчаник",  "отступающее море, берег")
  band(2.4, 3.3, OLIVE,            "рыхлые отложения", "ледник, реки, ветер")
  band(3.3, 3.75, INK.lighten(22%), "почва",     "наши дни")

  // ── стрелка времени слева: старое → молодое (вверх)
  line((-0.65, 0.0), (-0.65, 3.75), mark: (end: ">", fill: INK))
  content((-0.65, -0.34), text(size: 8.5pt, fill: OLIVE)[старое])
  content((-0.65, 4.08), text(size: 8.5pt, fill: OLIVE)[молодое])
  content((-1.15, 1.85), angle: 90deg, text(size: 9.5pt)[время])
})
