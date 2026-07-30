#import "@preview/cetz:0.4.2"
#set page(width: 440pt, height: 200pt, margin: 0pt, fill: rgb("#FBF8F1"))
#cetz.canvas(length: 1pt, {
  import cetz.draw: *
  rect((0, 0), (440, 200), fill: rgb("#FBF8F1"), stroke: none)

  merge-path(fill: rgb("#2E9BD6"), stroke: none, {
    line((154, 114), (187.0, 152), (253.0, 152), (286, 114), close: true) })
  merge-path(fill: rgb("#7A6FE0"), stroke: none, {
    line((187.0, 152), (223.96, 152), (209.44, 114), close: true) })
  merge-path(fill: rgb("#22333C"), stroke: none, {
    line((154, 114), (286, 114), (220, 32), close: true) })
  merge-path(fill: rgb("#7A6FE0"), stroke: none, {
    line((200.2, 114), (239.8, 114), (220, 32), close: true) })
  set-style(stroke: (paint: rgb("#FBF8F1"), thickness: 3pt))
  line((154, 114), (286, 114))
  line((187.0, 152), (209.44, 114))
  line((253.0, 152), (230.56, 114))
})
