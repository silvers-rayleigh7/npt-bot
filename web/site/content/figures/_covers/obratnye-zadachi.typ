#import "@preview/cetz:0.4.2"
#set page(width: 440pt, height: 200pt, margin: 0pt, fill: rgb("#FBF8F1"))
#cetz.canvas(length: 1pt, {
  import cetz.draw: *
  rect((0, 0), (440, 200), fill: rgb("#FBF8F1"), stroke: none)
  line((96, 60), (200, 96), stroke: (paint: rgb("#2E9BD6"), thickness: 2pt))
  line((168, 132), (200, 96), stroke: (paint: rgb("#2E9BD6"), thickness: 2pt))
  line((232, 48), (200, 96), stroke: (paint: rgb("#2E9BD6"), thickness: 2pt))
  line((296, 120), (200, 96), stroke: (paint: rgb("#2E9BD6"), thickness: 2pt))
  line((356, 66), (296, 120), stroke: (paint: rgb("#2E9BD6"), thickness: 2pt))
  line((232, 48), (356, 66), stroke: (paint: rgb("#2E9BD6"), thickness: 2pt))
  line((96, 60), (168, 132), stroke: (paint: rgb("#2E9BD6"), thickness: 2pt))
  circle((96, 60), radius: 9, fill: rgb("#22333C"), stroke: none)
  circle((168, 132), radius: 9, fill: rgb("#22333C"), stroke: none)
  circle((232, 48), radius: 9, fill: rgb("#22333C"), stroke: none)
  circle((296, 120), radius: 9, fill: rgb("#22333C"), stroke: none)
  circle((356, 66), radius: 9, fill: rgb("#22333C"), stroke: none)
  circle((200, 96), radius: 13, fill: rgb("#7A6FE0"), stroke: none)
})
