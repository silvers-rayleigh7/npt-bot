#import "@preview/cetz:0.4.2"
#set page(width: 440pt, height: 200pt, margin: 0pt, fill: rgb("#FBF8F1"))
#cetz.canvas(length: 1pt, {
  import cetz.draw: *
  rect((0, 0), (440, 200), fill: rgb("#FBF8F1"), stroke: none)
  circle((220, 100), radius: 17, fill: rgb("#7A6FE0"), stroke: none)
  circle((220, 100), radius: 44, fill: none, stroke: (paint: rgb("#22333C"), thickness: 2pt, dash: none))
  circle((220, 100), radius: 68, fill: none, stroke: (paint: rgb("#2E9BD6"), thickness: 2pt, dash: none))
  circle((220, 100), radius: 92, fill: none, stroke: (paint: rgb("#22333C"), thickness: 2pt, dash: none))
  circle((264, 100), radius: 8, fill: rgb("#22333C"), stroke: none)
  circle((172, 148), radius: 6.5, fill: rgb("#2E9BD6"), stroke: none)
  circle((285, 35), radius: 5, fill: rgb("#7A6FE0"), stroke: none)
})
