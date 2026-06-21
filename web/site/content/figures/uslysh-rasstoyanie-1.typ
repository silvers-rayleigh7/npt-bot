#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Измерение расстояния эхом. Абстрактная диаграмма (НЕ объекты):
// слева точка-источник «ты», справа вертикаль-преграда (склон) со штриховкой.
// Фронты-дуги ВЫХОДЯТ из источника, выгнуты вправо (звук идёт к склону, путь s);
// фронты-дуги эха выходят от склона, выгнуты влево (эхо возвращается, ещё s).
// НЕТ прямых стрелок поверх дуг (убрано двойное кодирование пути): направление
// несёт сама кривизна фронтов. Путь s — одной тонкой размерной линией внизу.
// Итог: туда-обратно = 2s, s = v·t/2, v ≈ 340 м/с.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE), mark: (fill: INK, scale: 0.55))

  let sx = 0.7          // источник звука «ты»
  let wx = 9.0          // стена-преграда (вертикаль)
  let cy = 2.6          // центральная ось (источник, стена, лучи)
  let wt = 0.5          // низ стены
  let wb = 4.7          // верх стены

  // ── ПРЕГРАДА: вертикаль + штриховка с тыльной стороны (намёк на склон/массив)
  line((wx, wt), (wx, wb), stroke: (paint: INK, thickness: 1.7pt))
  for k in range(0, 9) {
    let yy = wt + 0.5 * k
    if yy <= wb {
      line((wx, yy), (wx + 0.28, yy + 0.26), stroke: (paint: SAND, thickness: 0.6pt))
    }
  }
  content((wx + 0.36, wb + 0.02), anchor: "west", text(size: 9pt, fill: OLIVE)[склон])

  // ── тонкая ось-луч источник↔стена (приглушённо), чтобы путь читался как единая линия
  line((sx, cy), (wx, cy), stroke: (paint: SAND, thickness: 0.5pt, dash: "dotted"))

  // ── ИСТОЧНИК: маленький круг-маркер «ты» (центр чёрных фронтов исходит отсюда)
  circle((sx, cy), radius: 0.16, fill: INK, stroke: none)
  content((sx - 0.06, cy - 0.5), anchor: "east", text(size: 9.5pt)[ты])

  // ════════ ЗВУК ИДЁТ К СКЛОНУ ════════
  // чёрные фронты-дуги ВЫХОДЯТ из источника, выгнуты ВПРАВО (к склону)
  for R in (1.6, 2.4, 3.2) {
    arc((sx, cy), radius: R, start: -40deg, stop: 40deg, anchor: "origin",
        stroke: (paint: INK, thickness: 0.8pt))
  }
  // короткая подпись направления в чистой полосе НАД чёрными фронтами
  content((0.9, 4.55), anchor: "west", text(size: 10pt)[звук $arrow.r$])

  // ════════ ЭХО ВОЗВРАЩАЕТСЯ ════════
  // оливковые фронты-дуги от склона, выгнуты ВЛЕВО (назад к источнику)
  for R in (1.6, 2.4) {
    arc((wx, cy), radius: R, start: 140deg, stop: 220deg, anchor: "origin",
        stroke: (paint: OLIVE, thickness: 0.8pt))
  }
  // короткая подпись направления эха, у оливковых фронтов, в чистой зоне
  content((6.55, 0.85), anchor: "east", text(size: 10pt, fill: OLIVE)[$arrow.l$ эхо])

  // ── РАЗМЕР s: тонкая размерная линия источник↔стена внизу с засечками
  let dimy = -1.05
  line((sx, dimy), (wx, dimy), stroke: (paint: SAND, thickness: 0.7pt),
       mark: (start: "|", end: "|", fill: SAND, scale: 0.5))
  content(((sx + wx) / 2, dimy - 0.45), text(size: 9.5pt)[расстояние $s$])

  // ── ИТОГ: путь туда-обратно и формула — над сценой, в чистой зоне
  content(((sx + wx) / 2, wb + 0.7), text(size: 10pt)[туда и обратно $= 2 s$])
  content(((sx + wx) / 2, wb + 1.3),
          text(size: 11pt)[$s = v dot t \/ 2$#h(0.9em)$v approx 340$ м/с])
})
