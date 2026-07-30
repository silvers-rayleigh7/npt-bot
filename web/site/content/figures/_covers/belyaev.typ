#import "@preview/cetz:0.4.2"
#set page(width: 440pt, height: 200pt, margin: 0pt, fill: rgb("#FBF8F1"))
#cetz.canvas(length: 1pt, {
  import cetz.draw: *
  rect((0, 0), (440, 200), fill: rgb("#FBF8F1"), stroke: none)
  circle((140, 72), radius: 26, fill: rgb("#F26B57"), stroke: none)
  circle((196, 108), radius: 34, fill: rgb("#7A6FE0"), stroke: none)
  circle((196, 108), radius: 13, fill: rgb("#FBF8F1"), stroke: none)
  circle((256, 66), radius: 22, fill: rgb("#22333C"), stroke: none)
  circle((300, 116), radius: 28, fill: rgb("#F26B57"), stroke: none)
  circle((170, 136), radius: 18, fill: rgb("#7A6FE0"), stroke: none)
  circle((170, 136), radius: 7, fill: rgb("#FBF8F1"), stroke: none)
  circle((246, 138), radius: 15, fill: rgb("#22333C"), stroke: none)
  circle((330, 62), radius: 13, fill: rgb("#F26B57"), stroke: none)
})
