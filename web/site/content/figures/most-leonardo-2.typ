#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Аналогия из L1: каменная арка из клиньев-вуссуаров. Вес сверху (load) давит на
// замко́вый камень, тот передаёт усилие НЕ вниз, а в стороны — соседним клиньям,
// и так до опор. Абстрактная геометрия: полукруглая арка из N трапеций-клиньев,
// радиальные швы, стрелка нагрузки сверху, стрелки распора вдоль арки к опорам.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  let O = (0, 0)
  let ri = 2.1          // внутренний радиус арки
  let ro = 2.95         // внешний радиус
  let N = 7             // число клиньев
  let a0 = 0deg
  let a1 = 180deg
  let pt(r, a) = (r * calc.cos(a), r * calc.sin(a))

  // ── клинья-вуссуары: каждый — трапеция между двумя радиальными швами
  for i in range(N) {
    let aa = a0 + (a1 - a0) * (i / N)
    let ab = a0 + (a1 - a0) * ((i + 1) / N)
    let p1 = pt(ri, aa)
    let p2 = pt(ro, aa)
    let p3 = pt(ro, ab)
    let p4 = pt(ri, ab)
    // замко́вый камень (верхний, центральный) — чуть подсвечен песком
    let mid = (i + 0.5) / N
    let fill = if calc.abs(mid - 0.5) < (0.5 / N) { SAND.lighten(40%) } else { white }
    line(p1, p2, p3, p4, close: true, fill: fill, stroke: (paint: INK, thickness: LINE))
  }

  // ── опоры (абатменты): короткие столбики под пятами арки
  let spL = pt(ri, a1)        // левая пята (внутр.)
  let spLo = pt(ro, a1)
  let spR = pt(ri, a0)
  let spRo = pt(ro, a0)
  rect((spLo.at(0), -0.7), (spL.at(0), 0.0), fill: SAND.lighten(55%), stroke: (paint: INK, thickness: LINE))
  rect((spR.at(0), -0.7), (spRo.at(0), 0.0), fill: SAND.lighten(55%), stroke: (paint: INK, thickness: LINE))

  // ── нагрузка сверху на замковый камень: стрелка вниз
  let kc = pt((ri + ro) / 2, 90deg)
  line((kc.at(0), ro + 0.95), (kc.at(0), ro + 0.12),
    stroke: (paint: INK, thickness: 1.3pt), mark: (end: ">", fill: INK, scale: 0.6))
  content((kc.at(0), ro + 1.12), anchor: "south", text(size: 10pt)[вес])

  // ── распор: дуги-стрелки от замка вдоль арки к обеим опорам (усилие идёт в стороны)
  let rm = (ri + ro) / 2
  arc((0,0), radius: rm, start: 88deg, stop: 30deg, anchor: "origin",
    stroke: (paint: OLIVE, thickness: 1.0pt), mark: (end: ">", fill: OLIVE, scale: 0.5))
  arc((0,0), radius: rm, start: 92deg, stop: 150deg, anchor: "origin",
    stroke: (paint: OLIVE, thickness: 1.0pt), mark: (end: ">", fill: OLIVE, scale: 0.5))
  content(pt(rm - 0.0, 158deg), anchor: "east", text(size: 9pt, fill: OLIVE)[распор])

  // ── реакции опор: короткие стрелки наружу-вниз у пят
  content((kc.at(0), -1.05), text(size: 9.5pt)[вес давит вниз — клинья гонят его в стороны, к опорам])
})
