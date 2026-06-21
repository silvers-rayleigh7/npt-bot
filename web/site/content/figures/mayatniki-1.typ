#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Две пары маятников на общей балке. Абстрактная диаграмма (НЕ объекты):
// линии-нити, круги-грузы, тонкие дуги размаха со стрелкой, засечки подвеса.
// Левая пара: равные нити, разные массы (×2,5), в фазе → один ритм
//   (период НЕ зависит от массы). Правая пара: равные грузы, длина ×4 →
//   период ×2 (T ∝ √L) — длинный качается вдвое медленнее.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE), mark: (fill: INK, scale: 0.5))

  // ── общая балка (рама) сверху
  let beam_y = 6.4
  let beam_l = 0.2
  let beam_r = 13.6
  line((beam_l, beam_y), (beam_r, beam_y), stroke: (paint: INK, thickness: 1.6pt))
  // штриховка опоры над балкой (намёк на жёсткую раму)
  for x in range(0, 28) {
    let xx = beam_l + 0.5 * x
    if xx <= beam_r {
      line((xx, beam_y), (xx - 0.22, beam_y + 0.26), stroke: (paint: SAND, thickness: 0.6pt))
    }
  }

  // ── точка подвеса: маленькая засечка на балке (короткий вертикальный штрих)
  let pivot(x) = line((x, beam_y), (x, beam_y - 0.16), stroke: (paint: INK, thickness: 1.4pt))

  // ── координата груза: подвес (px), угол ang (от вертикали, вправо +), длина L.
  //    Чистые функции (НЕ draw) — могут возвращать значение.
  let bobx(px, ang, L) = px + L * calc.sin(ang)
  let boby(ang, L) = beam_y - L * calc.cos(ang)

  // ── маятник: нить от подвеса до груза + круг-груз. Draw-функция (без return).
  let pend(px, ang, L, r) = {
    let bx = bobx(px, ang, L)
    let by = boby(ang, L)
    line((px, beam_y), (bx, by))                          // нить
    circle((bx, by), radius: r, fill: INK, stroke: none)  // груз
  }

  // ── дуга размаха: тонкая дуга OLIVE радиуса R вокруг подвеса (px).
  //    Груз стоит на правом краю (+ang); дуга идёт ОТ груза к противоположному
  //    краю (-ang) — путь, по которому груз качнётся. Стрелка на дальнем (левом)
  //    конце, чтобы не утыкаться в круг-груз.
  //    CeTZ arc: 0deg = вправо, против часовой. Вертикаль вниз = -90deg.
  //    Дуга строится от старта к стопу — задаём start = +ang (у груза),
  //    stop = -ang (стрелка), delta отрицательная.
  let swing(px, R, ang) = {
    let a = ang / 1deg
    arc(
      (px, beam_y), radius: R,
      start: (-90 + a) * 1deg, stop: (-90 - a) * 1deg,
      anchor: "origin",
      stroke: (paint: OLIVE, thickness: 0.7pt),
      mark: (end: ">", fill: OLIVE, scale: 0.42),
    )
  }

  // ════════ ЛЕВАЯ ПАРА: равные нити, разные массы, в фазе (один угол) ════════
  let Lleft = 3.9          // равная длина нитей
  let angL = 17deg          // одинаковое отклонение (в фазе)
  let xL1 = 1.6
  let xL2 = 4.6             // пара сжата — читается как ОДНА группа

  pivot(xL1); pivot(xL2)
  // масса ×2,5 → площадь круга ∝ массе → радиус ×√2,5 ≈ ×1,58
  let rsmall = 0.20
  let rbig = 0.32
  pend(xL1, angL, Lleft, rsmall)
  pend(xL2, angL, Lleft, rbig)
  // дуги размаха — одинаковые (один ритм, один размах)
  swing(xL1, Lleft, angL)
  swing(xL2, Lleft, angL)

  // подпись левой пары — под дугами, plain-текст (× и запятая без матрежима)
  content((3.1, -0.7), text(size: 10pt)[масса ×2,5 — один ритм])

  // ── разделитель пар: тонкий пунктир между группами (зазор > внутрипарного)
  line((7.1, -0.3), (7.1, beam_y - 0.3),
    stroke: (paint: SAND, thickness: 0.6pt, dash: "dotted"))

  // ════════ ПРАВАЯ ПАРА: равные грузы, длина ×4 → период ×2 ════════
  let Llong = 4.6          // длинная нить
  let Lshort = Llong / 4   // вчетверо короче = 1.15
  let angLong = 16deg       // углы скромные — суть в РАЗНИЦЕ ДЛИН, не в размахе
  let angShort = 26deg
  let xR1 = 9.8            // длинный
  let xR2 = 12.6           // короткий
  let req = 0.26           // равные грузы

  pivot(xR1); pivot(xR2)
  pend(xR1, angLong, Llong, req)
  pend(xR2, angShort, Lshort, req)
  swing(xR1, Llong, angLong)
  swing(xR2, Lshort, angShort)

  // метка длины у длинного маятника: «×4» слева от длинной нити
  // (единая рамка сравнения: и метка, и подпись пары — в направлении ×4)
  content((bobx(xR1, angLong, Llong) - 0.45, boby(angLong, Llong) + 0.6), anchor: "east", text(size: 9pt, fill: OLIVE)[длина ×4])

  // подпись правой пары — под маятниками, plain-текст (× и → без матрежима)
  content((11.2, -0.7), text(size: 10pt)[длина ×4 → период ×2])
})
