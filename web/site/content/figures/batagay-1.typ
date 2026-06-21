#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Батагай: тает лёд мерзлоты → грунт проседает → обнажается ещё лёд → разгон (обратная связь).
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // мерзлота (массив) с провалом-ямой
  let prof = ((0,2.6),(1.6,2.6),(2.6,0.5),(4.0,0.2),(5.4,0.5),(6.4,2.6),(8.0,2.6),(8.0,0),(0,0))
  line(..prof, close: true, fill: SAND.lighten(30%), stroke: INK)
  // лёд-«цемент» в массиве
  for (x,y) in ((0.8,1.2),(7.2,1.2),(1.2,0.6),(6.8,0.6)) { content((x,y), text(size: 7pt, fill: OLIVE)[лёд]) }
  // оголённые стенки провала
  content((4.0, 1.6), text(size: 8.5pt)[провал])
  // солнце греет стенки
  circle((4.0, 3.3), radius: 0.2, fill: SUN, stroke: none)
  line((3.5, 3.0), (3.0, 1.0), mark: (end: ">", fill: SUN), stroke: (paint: SUN, thickness: 0.8pt))
  line((4.5, 3.0), (5.0, 1.0), mark: (end: ">", fill: SUN), stroke: (paint: SUN, thickness: 0.8pt))
  // подпись обратной связи
  content((4.0, -0.45), text(size: 8pt, fill: OLIVE)[больше оттаяло → больше поверхности → быстрее таяние])
})
