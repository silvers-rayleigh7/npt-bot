#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Кривая затухания устной памяти. Абстрактная диаграмма-график:
// X — поколения 0…16 (≈400 лет, шаг 25), Y — доля уцелевших деталей S=(1-p)^n
// от 1 до 0. Две кривые: p=0,05 (спадает медленно, к ~0,44) и p=0,2 (резко к ~0,03).
// Тонкая сетка, оси с засечками, подписи кривых у их правых концов.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE), mark: (fill: INK, scale: 0.55))

  // ── габариты поля графика
  let W = 8.4              // ширина (ось X)
  let H = 5.2              // высота (ось Y)
  let NMAX = 16            // поколений по оси X
  // координаты: поколение n → x ; доля S∈[0,1] → y
  let px = n => n / NMAX * W
  let py = s => s * H

  // ── ТОНКАЯ СЕТКА (приглушённая), под осями и кривыми
  // вертикали по поколениям, через 4
  for n in (4, 8, 12, 16) {
    line((px(n), 0), (px(n), H), stroke: (paint: SAND.lighten(35%), thickness: 0.4pt))
  }
  // горизонтали по доле, через 0,25
  for s in (0.25, 0.5, 0.75, 1.0) {
    line((0, py(s)), (W, py(s)), stroke: (paint: SAND.lighten(35%), thickness: 0.4pt))
  }

  // ── ОСИ
  line((0, 0), (W + 0.5, 0), mark: (end: ">"), stroke: (paint: INK, thickness: 1.2pt))
  line((0, 0), (0, H + 0.5), mark: (end: ">"), stroke: (paint: INK, thickness: 1.2pt))

  // подписи делений X (поколения)
  for n in (0, 4, 8, 12, 16) {
    line((px(n), 0), (px(n), -0.14), stroke: (paint: INK, thickness: 1.0pt))
    content((px(n), -0.40), text(size: 9pt)[#str(n)])
  }
  // подписи делений Y (доля), с десятичной запятой
  let ylabel = s => if s == 0 { "0" } else if s == 1 { "1" } else {
    "0," + str(int(s * 100))
  }
  for s in (0.0, 0.25, 0.5, 0.75, 1.0) {
    line((0, py(s)), (-0.14, py(s)), stroke: (paint: INK, thickness: 1.0pt))
    content((-0.30, py(s)), anchor: "east", text(size: 9pt)[#ylabel(s)])
  }

  // ── названия осей
  content((W / 2, -1.05), text(size: 10pt)[поколения $n$ (за 400 лет, по 25 лет)])
  content((-1.55, H / 2), angle: 90deg,
          text(size: 10pt)[доля деталей $S = (1-p)^n$])

  // ── КРИВАЯ S=(1-p)^n: ломаная по n=0..16 (плавно за счёт частого шага).
  //    Чистая функция — строит массив точек.
  let curvepts = p => {
    let pts = ()
    for k in range(0, NMAX + 1) {
      pts.push((px(k), py(calc.pow(1 - p, k))))
    }
    pts
  }

  // p=0,05 — медленный спад (к ~0,44). Сплошная INK.
  line(..curvepts(0.05), stroke: (paint: INK, thickness: 1.5pt))
  // p=0,2 — резкий спад к нулю. OLIVE, чуть тоньше, чтобы различать.
  line(..curvepts(0.2), stroke: (paint: OLIVE, thickness: 1.4pt))

  // ── маркеры конечных значений n=16 + подписи кривых у их правых концов.
  let send05 = calc.pow(0.95, 16)   // ≈0,44
  let send20 = calc.pow(0.80, 16)   // ≈0,03
  circle((px(16), py(send05)), radius: 0.07, fill: INK, stroke: none)
  circle((px(16), py(send20)), radius: 0.07, fill: OLIVE, stroke: none)

  // подпись медленной кривой = СТОЙКИЙ крупный факт (малое p).
  //    Десятичная запятая — в plain-тексте (в матрежиме {,} не работает),
  //    символ p — в матрежиме.
  content((px(16) + 0.22, py(send05) + 0.20), anchor: "west",
          text(size: 9pt)[«городище было»])
  content((px(16) + 0.22, py(send05) - 0.10), anchor: "west",
          text(size: 8.5pt, fill: OLIVE)[$p$ = 0,05 $arrow.r$ 0,44])

  // подпись резкой кривой = ХРУПКАЯ деталь (большое p), у самой оси.
  content((px(16) + 0.22, py(send20) + 0.46), anchor: "west",
          text(size: 9pt, fill: OLIVE)[«где стояло»])
  content((px(16) + 0.22, py(send20) + 0.16), anchor: "west",
          text(size: 8.5pt, fill: OLIVE)[$p$ = 0,2 $arrow.r$ 0,03])
})
