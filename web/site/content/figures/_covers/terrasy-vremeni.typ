#import "@preview/cetz:0.4.2"
#set page(width: 440pt, height: 200pt, margin: 0pt, fill: rgb("#FBF8F1"))
#cetz.canvas(length: 1pt, {
  import cetz.draw: *
  rect((0, 0), (440, 200), fill: rgb("#FBF8F1"), stroke: none)
  merge-path(fill: rgb("#22333C"), stroke: none, { line((80, 30), (236, 30), (236, 46), (80, 46), close: true) })
  merge-path(fill: rgb("#22333C"), stroke: none, { line((236, 19), (360, 19), (360, 35), (236, 35), close: true) })
  merge-path(fill: rgb("#4EA75D"), stroke: none, { line((80, 49), (236, 49), (236, 59), (80, 59), close: true) })
  merge-path(fill: rgb("#4EA75D"), stroke: none, { line((236, 38), (360, 38), (360, 48), (236, 48), close: true) })
  merge-path(fill: rgb("#E9863B"), stroke: none, { line((80, 62), (236, 62), (236, 82), (80, 82), close: true) })
  merge-path(fill: rgb("#E9863B"), stroke: none, { line((236, 51), (360, 51), (360, 71), (236, 71), close: true) })
  merge-path(fill: rgb("#4EA75D"), stroke: none, { line((80, 85), (236, 85), (236, 93), (80, 93), close: true) })
  merge-path(fill: rgb("#4EA75D"), stroke: none, { line((236, 74), (360, 74), (360, 82), (236, 82), close: true) })
  merge-path(fill: rgb("#22333C"), stroke: none, { line((80, 96), (236, 96), (236, 110), (80, 110), close: true) })
  merge-path(fill: rgb("#22333C"), stroke: none, { line((236, 85), (360, 85), (360, 99), (236, 99), close: true) })
  merge-path(fill: rgb("#E9863B"), stroke: none, { line((80, 113), (236, 113), (236, 124), (80, 124), close: true) })
  merge-path(fill: rgb("#E9863B"), stroke: none, { line((236, 102), (360, 102), (360, 113), (236, 113), close: true) })
  line((236, 14), (236, 172), stroke: (paint: rgb("#FBF8F1"), thickness: 4pt))
})
