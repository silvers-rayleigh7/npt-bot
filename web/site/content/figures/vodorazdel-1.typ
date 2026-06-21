#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 11pt, fill: INK)

// Поперечный профиль водораздела (конёк крыши). Абстрактная диаграмма (НЕ ландшафт):
// симметричный гребень по центру, два склона вниз к двум ложбинам. В вершине —
// капля; от неё ДВЕ стрелки расходятся вниз по разным склонам (вода делится).
// Под склонами — лёгкая штриховка водосборов A и B; внизу — стоки.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE), mark: (fill: INK, scale: 0.6))

  // ── ключевые точки профиля (симметрично относительно вершины)
  let peakx = 5.0
  let peaky = 3.6          // вершина гребня
  let valy  = 0.7          // дно ложбин
  let lvalx = 0.6          // левая ложбина
  let rvalx = 9.4          // правая ложбина

  // ── линия-профиль: ложбина — склон — вершина — склон — ложбина
  line(
    (lvalx, valy), (peakx, peaky), (rvalx, valy),
    stroke: (paint: INK, thickness: 1.6pt),
  )

  // ── штриховка водосборов: короткие вертикальные штрихи под каждым склоном,
  //    приглушённые (намёк на площадь сбора, без заливки). Короткие, чтобы не
  //    спорить со стрелками стока, спускающимися по склону.
  let hatch(x0, y0, x1, y1, n) = {
    for i in range(1, n) {
      let t = i / n
      let bx = x0 + t * (x1 - x0)
      let by = y0 + t * (y1 - y0)
      line((bx, by), (bx, by - 0.26), stroke: (paint: SAND, thickness: 0.5pt))
    }
  }
  hatch(lvalx, valy, peakx, peaky, 8)
  hatch(rvalx, valy, peakx, peaky, 8)

  // ── капля в вершине (иконка Lucide), сидит на самом коньке
  content((peakx, peaky + 0.34), image("icons/droplet.svg", width: 0.55cm))

  // ── две стрелки расходятся от вершины вниз по разным склонам (вода делится).
  //    Стартуют под каплей, идут параллельно склонам чуть НИЖЕ профиля,
  //    остриё ближе к ложбине — ясно читается «стекает в свой водосбор».
  line((peakx - 0.62, peaky - 0.62), (peakx - 2.60, peaky - 1.92),
       mark: (end: ">"), stroke: (paint: INK, thickness: 1.1pt))
  line((peakx + 0.62, peaky - 0.62), (peakx + 2.60, peaky - 1.92),
       mark: (end: ">"), stroke: (paint: INK, thickness: 1.1pt))

  // ── подпись вершины «водораздел» — над каплей, с воздухом
  content((peakx, peaky + 1.10), text(size: 11pt)[водораздел])

  // ── подписи водосборов — по центру каждого склона, под штриховкой
  content((2.5, valy - 0.78), text(size: 10pt, fill: OLIVE)[водосбор A])
  content((7.5, valy - 0.78), text(size: 10pt, fill: OLIVE)[водосбор B])

  // ── стоки: короткая стрелка от каждой ложбины наружу-вниз (вода покидает
  //    водосбор), подпись «сток» рядом с остриём, в чистой зоне у края.
  line((lvalx, valy), (lvalx - 0.85, valy - 0.42),
       mark: (end: ">"), stroke: (paint: OLIVE, thickness: 0.9pt))
  content((lvalx - 1.05, valy - 0.72), anchor: "east", text(size: 9.5pt, fill: OLIVE)[сток])
  line((rvalx, valy), (rvalx + 0.85, valy - 0.42),
       mark: (end: ">"), stroke: (paint: OLIVE, thickness: 0.9pt))
  content((rvalx + 1.05, valy - 0.72), anchor: "west", text(size: 9.5pt, fill: OLIVE)[сток])
})
