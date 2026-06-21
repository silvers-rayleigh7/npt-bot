#import "/content/figures/_preamble.typ": *
#set page(width: auto, height: auto, margin: 8pt, fill: white)
#set text(font: "Libertinus Serif", size: 10pt, fill: INK)

// Поверхность ~L², объём ~L³: у большого тела поверхности на единицу объёма меньше.
#cetz.canvas(length: 1cm, {
  import cetz.draw: *
  set-style(stroke: (paint: INK, thickness: LINE))

  // маленький куб
  let cube(o, s) = {
    rect((o.at(0), o.at(1)), (o.at(0) + s, o.at(1) + s), fill: SAND.lighten(45%), stroke: INK)
    line((o.at(0), o.at(1) + s), (o.at(0) + s * 0.4, o.at(1) + s * 1.4))
    line((o.at(0) + s, o.at(1) + s), (o.at(0) + s * 1.4, o.at(1) + s * 1.4))
    line((o.at(0) + s, o.at(1)), (o.at(0) + s * 1.4, o.at(1) + s * 0.4))
    line((o.at(0) + s * 0.4, o.at(1) + s * 1.4), (o.at(0) + s * 1.4, o.at(1) + s * 1.4), (o.at(0) + s * 1.4, o.at(1) + s * 0.4))
  }
  cube((0, 0), 1.0);  content((0.7, -0.5), text(size: 8.5pt)[мышь])
  cube((4.0, 0), 2.0); content((5.2, -0.5), text(size: 8.5pt)[слон])

  content((1.7, 2.0), text(size: 9pt)[$L$])
  content((6.6, 2.6), text(size: 9pt)[$2L$])

  content((2.5, -1.4), text(size: 10pt)[поверхность $S prop L^2$, #h(0.2cm) объём $M prop L^3$])
  content((2.5, -2.0), text(size: 9pt, fill: OLIVE)[у крупного тела поверхности на единицу объёма меньше])
})
