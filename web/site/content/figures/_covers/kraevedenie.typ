#import "@preview/cetz:0.4.2"
#set page(width: 440pt, height: 200pt, margin: 0pt, fill: rgb("#FBF8F1"))
#cetz.canvas(length: 1pt, {
  import cetz.draw: *
  rect((0, 0), (440, 200), fill: rgb("#FBF8F1"), stroke: none)

  circle((300, 132), radius: 26, fill: rgb("#4EA75D"), stroke: none)
  merge-path(fill: rgb("#E9863B"), stroke: none, {
    line((60, 96), (150, 128), (232, 92), (312, 122), (380, 96), (380, 60), (60, 60), close: true) })
  merge-path(fill: rgb("#22333C"), stroke: none, {
    line((60, 62), (128, 88), (208, 56), (288, 84), (380, 54), (380, 24), (60, 24), close: true) })
})
