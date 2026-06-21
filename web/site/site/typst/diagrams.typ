// Tropa POI Card Diagrams
// Simple monochrome scientific diagrams using Typst built-in drawing primitives.
// Each function takes a primary color and renders ~38-42mm tall diagram.

// ---- 1. Trilateration (GPS) ----
#let trilateration-diagram(color) = {
  let gray = rgb("#888888")
  let light = color.lighten(70%)
  let h = 42mm

  block(width: 100%, height: h, {
    // Intersection point (center of the diagram)
    let ix = 46%
    let iy = 46%

    // Circle centers — positioned so all three clearly overlap at intersection
    let c1x = 28%
    let c1y = 22%
    let c2x = 55%
    let c2y = 20%
    let c3x = 36%
    let c3y = 74%

    // Circle 1 — top-left
    place(dx: c1x - 16mm, dy: c1y - 16mm,
      circle(radius: 16mm, fill: light.transparentize(70%), stroke: (paint: color, thickness: 0.8pt, dash: "dashed"))
    )
    // Circle 2 — top-right
    place(dx: c2x - 17mm, dy: c2y - 17mm,
      circle(radius: 17mm, fill: light.transparentize(70%), stroke: (paint: color, thickness: 0.8pt, dash: "dashed"))
    )
    // Circle 3 — bottom-center
    place(dx: c3x - 16mm, dy: c3y - 16mm,
      circle(radius: 16mm, fill: light.transparentize(70%), stroke: (paint: color, thickness: 0.8pt, dash: "dashed"))
    )

    // Satellite labels
    place(dx: c1x - 8pt, dy: c1y - 4pt,
      text(size: 6.5pt, fill: color, weight: "bold", "S1")
    )
    place(dx: c2x - 8pt, dy: c2y - 4pt,
      text(size: 6.5pt, fill: color, weight: "bold", "S2")
    )
    place(dx: c3x - 8pt, dy: c3y - 4pt,
      text(size: 6.5pt, fill: color, weight: "bold", "S3")
    )

    // Radius lines (dotted) from centers to intersection
    place(dx: 0pt, dy: 0pt, {
      line(start: (c1x, c1y), end: (ix, iy), stroke: (paint: gray, thickness: 0.5pt, dash: "dotted"))
      line(start: (c2x, c2y), end: (ix, iy), stroke: (paint: gray, thickness: 0.5pt, dash: "dotted"))
      line(start: (c3x, c3y), end: (ix, iy), stroke: (paint: gray, thickness: 0.5pt, dash: "dotted"))
    })

    // Intersection point
    place(dx: ix - 3pt, dy: iy - 3pt,
      circle(radius: 3pt, fill: color, stroke: none)
    )

    // "Ты" label
    place(dx: ix + 5pt, dy: iy - 10pt,
      text(size: 7pt, fill: color, weight: "bold", "Ты")
    )

    // Radius labels (near midpoint of each center-to-intersection line)
    place(dx: 35%, dy: 30%,
      text(size: 5.5pt, fill: gray, style: "italic", [$rho_1$])
    )
    place(dx: 50%, dy: 28%,
      text(size: 5.5pt, fill: gray, style: "italic", [$rho_2$])
    )
    place(dx: 38%, dy: 57%,
      text(size: 5.5pt, fill: gray, style: "italic", [$rho_3$])
    )
  })
}


// ---- 2. Sabine (Acoustics) ----
#let sabine-diagram(color) = {
  let gray = rgb("#888888")
  let h = 38mm

  block(width: 100%, height: h, {
    // Room rectangle
    let rx = 15%
    let ry = 6%
    let rw = 70%
    let rh = 28mm

    place(dx: rx, dy: ry,
      rect(width: rw, height: rh, fill: color.lighten(90%), stroke: (paint: color, thickness: 1.2pt))
    )

    // Sound source (small circle)
    place(dx: 20%, dy: 10mm,
      circle(radius: 2.5pt, fill: color, stroke: none)
    )
    place(dx: 20% + 5pt, dy: 10mm - 4pt,
      text(size: 5.5pt, fill: color, weight: "bold", "источник")
    )

    // Wave arrows bouncing — each reflection weaker
    place(dx: 0pt, dy: 0pt, {
      line(start: (22%, 11mm), end: (82%, 11mm), stroke: (paint: color, thickness: 1pt))
      line(start: (82%, 11mm), end: (55%, 22mm), stroke: (paint: color.lighten(30%), thickness: 0.7pt))
      line(start: (55%, 22mm), end: (18%, 16mm), stroke: (paint: color.lighten(55%), thickness: 0.5pt))
      line(start: (18%, 16mm), end: (50%, 8%), stroke: (paint: color.lighten(75%), thickness: 0.3pt))
    })

    // Arrow head on direct wave
    place(dx: 79%, dy: 11mm - 4pt,
      text(size: 6pt, fill: color, sym.arrow.r)
    )

    // Labels below room
    place(dx: 20%, dy: ry + rh + 1mm,
      text(size: 5.5pt, fill: gray, style: "italic", "поглощение")
    )
    place(dx: 55%, dy: ry + rh + 1mm,
      text(size: 5.5pt, fill: gray, style: "italic", "отражение")
    )

    // Absorption hatching on left wall
    place(dx: rx, dy: ry + 2mm, {
      for i in range(4) {
        place(dx: -2mm, dy: i * 6mm,
          line(start: (0pt, 0pt), end: (-3mm, 3mm), stroke: (paint: gray, thickness: 0.4pt))
        )
      }
    })
  })
}


// ---- 3. SLAM (Predict-Correct Loop) ----
#let slam-diagram(color) = {
  let gray = rgb("#888888")
  let h = 38mm

  block(width: 100%, height: h, {
    let mid-y = 17mm

    // Step 1: Small ellipse (known position)
    place(dx: 5%, dy: mid-y - 7mm,
      ellipse(width: 15mm, height: 11mm, fill: color.lighten(80%), stroke: (paint: color, thickness: 0.8pt))
    )
    place(dx: 5% + 2.5mm, dy: mid-y - 2pt,
      text(size: 5pt, fill: color, "позиция")
    )

    // Arrow: predict
    place(dx: 5% + 17mm, dy: mid-y - 2pt, {
      line(start: (0pt, 0pt), end: (12mm, 0pt), stroke: (paint: gray, thickness: 0.8pt))
    })
    place(dx: 5% + 29mm, dy: mid-y - 3pt,
      text(size: 5pt, fill: gray, sym.arrow.r)
    )
    place(dx: 5% + 18mm, dy: mid-y - 8pt,
      text(size: 5.5pt, fill: gray, weight: "medium", "прогноз")
    )

    // Step 2: Bigger ellipse (grown uncertainty)
    place(dx: 38%, dy: mid-y - 10mm,
      ellipse(width: 20mm, height: 15mm, fill: color.lighten(85%), stroke: (paint: color.lighten(20%), thickness: 0.8pt, dash: "dashed"))
    )
    place(dx: 38% + 2mm, dy: mid-y - 2pt,
      text(size: 5pt, fill: color.lighten(20%), "неопр. " + sym.arrow.t)
    )

    // Arrow: correct
    place(dx: 38% + 22mm, dy: mid-y - 2pt, {
      line(start: (0pt, 0pt), end: (12mm, 0pt), stroke: (paint: gray, thickness: 0.8pt))
    })
    place(dx: 38% + 34mm, dy: mid-y - 3pt,
      text(size: 5pt, fill: gray, sym.arrow.r)
    )
    place(dx: 38% + 21mm, dy: mid-y - 8pt,
      text(size: 5.5pt, fill: gray, weight: "medium", "коррекция")
    )
    place(dx: 38% + 23mm, dy: mid-y + 5pt,
      text(size: 5pt, fill: gray, style: "italic", "(лидар)")
    )

    // Step 3: Small ellipse again (corrected)
    place(dx: 76%, dy: mid-y - 6mm,
      ellipse(width: 13mm, height: 9mm, fill: color.lighten(75%), stroke: (paint: color, thickness: 1pt))
    )
    place(dx: 76% + 1mm, dy: mid-y - 1pt,
      text(size: 5pt, fill: color, "точнее!")
    )

    // Cycle arrow (bottom)
    place(dx: 20%, dy: mid-y + 12mm, {
      line(start: (0pt, 0pt), end: (55%, 0pt), stroke: (paint: gray.lighten(30%), thickness: 0.5pt, dash: "dashed"))
    })
    place(dx: 45%, dy: mid-y + 13mm,
      text(size: 5pt, fill: gray, style: "italic", sym.arrow.ccw + " цикл повторяется")
    )
  })
}


// ---- 4. Faraday (Electromagnetic Induction) ----
#let faraday-diagram(color) = {
  let gray = rgb("#888888")
  let h = 40mm

  block(width: 100%, height: h, {
    let mid-y = 18mm

    // Coil (rectangle with horizontal lines = windings)
    let coil-x = 40%
    let coil-w = 18mm
    let coil-h = 24mm
    place(dx: coil-x, dy: mid-y - coil-h / 2,
      rect(width: coil-w, height: coil-h, fill: none, stroke: (paint: color, thickness: 1.2pt))
    )
    // Windings
    place(dx: coil-x, dy: mid-y - coil-h / 2, {
      for i in range(5) {
        let yy = 2.5mm + i * 4.5mm
        line(start: (0pt, yy), end: (coil-w, yy), stroke: (paint: color.lighten(30%), thickness: 0.6pt))
      }
    })
    place(dx: coil-x + 1mm, dy: mid-y + coil-h / 2 + 1mm,
      text(size: 5pt, fill: color, "катушка (N витков)")
    )

    // Magnet (left of coil)
    let mag-x = 10%
    let mag-w = 20mm
    let mag-h = 11mm
    place(dx: mag-x, dy: mid-y - mag-h / 2, {
      // N pole (colored)
      rect(width: mag-w / 2, height: mag-h, fill: color.lighten(50%), stroke: (paint: color, thickness: 0.8pt))
      // S pole (darker for contrast)
      place(dx: mag-w / 2, dy: 0pt,
        rect(width: mag-w / 2, height: mag-h, fill: gray.lighten(30%), stroke: (paint: gray, thickness: 0.8pt))
      )
    })
    // N/S labels
    place(dx: mag-x + 2mm, dy: mid-y - 4pt,
      text(size: 7pt, fill: white, weight: "bold", "N")
    )
    place(dx: mag-x + mag-w / 2 + 2mm, dy: mid-y - 4pt,
      text(size: 7pt, fill: white, weight: "bold", "S")
    )

    // Motion arrow (magnet -> coil)
    place(dx: mag-x + mag-w + 2mm, dy: mid-y - 2pt, {
      line(start: (0pt, 0pt), end: (8mm, 0pt), stroke: (paint: color, thickness: 1pt))
    })
    place(dx: mag-x + mag-w + 10mm, dy: mid-y - 3pt,
      text(size: 7pt, fill: color, sym.arrow.r)
    )
    place(dx: mag-x + mag-w + 1mm, dy: mid-y - 9pt,
      text(size: 5pt, fill: gray, style: "italic", "движение")
    )

    // Current output arrow (right of coil)
    place(dx: coil-x + coil-w + 3mm, dy: mid-y - 2pt, {
      line(start: (0pt, 0pt), end: (14mm, 0pt), stroke: (paint: color, thickness: 1pt))
    })
    place(dx: coil-x + coil-w + 17mm, dy: mid-y - 3pt,
      text(size: 7pt, fill: color, sym.arrow.r)
    )
    place(dx: coil-x + coil-w + 4mm, dy: mid-y + 4pt,
      text(size: 5.5pt, fill: color, weight: "bold", [ток ($cal(E)$)])
    )

    // Formula at bottom
    place(dx: 28%, dy: h - 6mm,
      text(size: 6.5pt, fill: gray, [$cal(E) = -N dot d Phi slash d t$])
    )
  })
}


// ---- 5. Braess Paradox (Network Graph) ----
#let braess-diagram(color) = {
  let gray = rgb("#888888")
  let h = 42mm

  block(width: 100%, height: h, {
    // Diamond layout — compressed vertically
    let ax = 14%
    let ay = 21mm
    let bx = 46%
    let by = 4mm
    let cx = 46%
    let cy = 38mm
    let dx2 = 78%
    let dy2 = 21mm

    // Edges
    place(dx: 0pt, dy: 0pt, {
      line(start: (ax, ay), end: (bx, by), stroke: (paint: color, thickness: 1pt))
      line(start: (ax, ay), end: (cx, cy), stroke: (paint: color, thickness: 1pt))
      line(start: (bx, by), end: (dx2, dy2), stroke: (paint: color, thickness: 1pt))
      line(start: (cx, cy), end: (dx2, dy2), stroke: (paint: color, thickness: 1pt))
      // B -> C (paradox edge, dashed)
      line(start: (bx, by), end: (cx, cy), stroke: (paint: color, thickness: 1.5pt, dash: "dashed"))
    })

    // Edge labels
    place(dx: 24%, dy: 7mm,
      text(size: 5.5pt, fill: gray, style: "italic", [$t slash 100$])
    )
    place(dx: 24%, dy: 32mm,
      text(size: 5.5pt, fill: gray, style: "italic", "45 мин")
    )
    place(dx: 60%, dy: 7mm,
      text(size: 5.5pt, fill: gray, style: "italic", "45 мин")
    )
    place(dx: 60%, dy: 32mm,
      text(size: 5.5pt, fill: gray, style: "italic", [$t slash 100$])
    )
    // Paradox edge label
    place(dx: bx + 3mm, dy: 19mm,
      text(size: 5.5pt, fill: color, weight: "bold", "0 мин!")
    )

    // Nodes
    for (nx, ny, label) in ((ax, ay, "A"), (bx, by, "B"), (cx, cy, "C"), (dx2, dy2, "D")) {
      place(dx: nx - 5pt, dy: ny - 5pt,
        circle(radius: 5pt, fill: white, stroke: (paint: color, thickness: 1pt))
      )
      place(dx: nx - 3.5pt, dy: ny - 4.5pt,
        text(size: 7pt, fill: color, weight: "bold", label)
      )
    }

    // Caption — short
    place(dx: 6%, dy: 0mm,
      text(size: 5pt, fill: gray, [пунктир = парадокс])
    )
  })
}


// ---- 6. Froude (Walk-Run Transition) ----
#let froude-diagram(color) = {
  let gray = rgb("#888888")
  let h = 40mm

  block(width: 100%, height: h, {
    let ground-y = 34mm

    // Ground line
    place(dx: 5%, dy: ground-y, {
      line(start: (0pt, 0pt), end: (90%, 0pt), stroke: (paint: gray, thickness: 0.5pt))
    })

    // Stick figure
    let hip-x = 38%
    let hip-y = 14mm
    let foot-x = 32%
    let foot-y = ground-y
    let head-y = 4mm

    // Body parts
    place(dx: 0pt, dy: 0pt, {
      // Standing leg (inverted pendulum)
      line(start: (foot-x, foot-y), end: (hip-x, hip-y), stroke: (paint: color, thickness: 1.5pt))
      // Torso
      line(start: (hip-x, hip-y), end: (hip-x, head-y + 3mm), stroke: (paint: color, thickness: 1.5pt))
      // Arms
      line(start: (hip-x - 4mm, head-y + 7mm), end: (hip-x + 4mm, head-y + 7mm), stroke: (paint: color, thickness: 1pt))
    })

    // Head
    place(dx: hip-x - 3pt, dy: head-y - 3pt,
      circle(radius: 3pt, fill: color, stroke: none)
    )

    // Foot pivot point
    place(dx: foot-x - 2pt, dy: foot-y - 2pt,
      circle(radius: 2pt, fill: color, stroke: none)
    )

    // Arc showing CoM path
    place(dx: foot-x - 16mm, dy: hip-y - 7mm, {
      for i in range(8) {
        let px = i * 4.5mm
        let py = if i < 4 { (4 - i) * 1.2mm } else { (i - 4) * 1.2mm }
        place(dx: px, dy: py,
          circle(radius: 0.7pt, fill: gray, stroke: none)
        )
      }
    })

    // Arc label
    place(dx: foot-x - 13mm, dy: hip-y - 11mm,
      text(size: 5pt, fill: gray, style: "italic", "траектория ЦМ")
    )

    // Speed arrow
    place(dx: hip-x + 8mm, dy: hip-y - 2pt, {
      line(start: (0pt, 0pt), end: (15mm, 0pt), stroke: (paint: color, thickness: 1pt))
    })
    place(dx: hip-x + 23mm, dy: hip-y - 3pt,
      text(size: 6pt, fill: color, sym.arrow.r)
    )
    place(dx: hip-x + 10mm, dy: hip-y - 8pt,
      text(size: 6pt, fill: color, weight: "bold", [$v$])
    )

    // L label (leg length)
    place(dx: foot-x - 9mm, dy: (hip-y + foot-y) / 2 - 2mm, {
      line(start: (0pt, -4mm), end: (0pt, 4mm), stroke: (paint: gray, thickness: 0.5pt))
      line(start: (-1.5mm, -4mm), end: (1.5mm, -4mm), stroke: (paint: gray, thickness: 0.5pt))
      line(start: (-1.5mm, 4mm), end: (1.5mm, 4mm), stroke: (paint: gray, thickness: 0.5pt))
    })
    place(dx: foot-x - 15mm, dy: (hip-y + foot-y) / 2 - 4pt,
      text(size: 6pt, fill: gray, weight: "bold", [$L$])
    )

    // Formula
    place(dx: 55%, dy: ground-y - 12mm,
      text(size: 7pt, fill: gray, [Fr $= v^2 slash (g L) approx 0.5$])
    )
    place(dx: 55%, dy: ground-y - 4mm,
      text(size: 5.5pt, fill: gray, style: "italic", [$arrow.r$ переход при $tilde$ 7.5 км/ч])
    )
  })
}


// ---- 7. Tree Water Column ----
#let tree-water-diagram(color) = {
  let gray = rgb("#888888")
  let h = 42mm

  block(width: 100%, height: h, {
    // Trunk (vertical rectangle)
    let trunk-x = 42%
    let trunk-w = 14mm
    let trunk-top = 7mm
    let trunk-bot = 37mm

    place(dx: trunk-x, dy: trunk-top,
      rect(width: trunk-w, height: trunk-bot - trunk-top, fill: color.lighten(85%), stroke: (paint: color, thickness: 0.8pt))
    )

    // Xylem vessels (thin vertical lines inside trunk)
    place(dx: trunk-x, dy: trunk-top, {
      for i in range(3) {
        let xx = 3mm + i * 4mm
        line(start: (xx, 2mm), end: (xx, trunk-bot - trunk-top - 2mm), stroke: (paint: color.lighten(30%), thickness: 0.5pt))
      }
    })

    // Water upward arrows inside trunk
    place(dx: trunk-x, dy: trunk-top, {
      for i in range(3) {
        let xx = 3mm + i * 4mm
        for j in range(3) {
          let yy = 5mm + j * 8mm
          place(dx: xx - 2.5pt, dy: yy,
            text(size: 5pt, fill: color, sym.arrow.t)
          )
        }
      }
    })

    // Crown/leaves (ellipse at top)
    place(dx: trunk-x - 7mm, dy: 0mm,
      ellipse(width: trunk-w + 14mm, height: 10mm, fill: color.lighten(75%), stroke: (paint: color, thickness: 0.6pt))
    )
    place(dx: trunk-x - 2mm, dy: 2.5mm,
      text(size: 5pt, fill: color, "листья")
    )

    // Evaporation arrows from crown
    place(dx: trunk-x - 4mm, dy: -1mm, {
      for i in range(4) {
        place(dx: i * 7mm + 1mm, dy: 0pt,
          text(size: 5pt, fill: gray, sym.arrow.t)
        )
      }
    })
    place(dx: trunk-x + trunk-w + 3mm, dy: 0mm,
      text(size: 5pt, fill: gray, style: "italic", "транспирация")
    )

    // Roots at bottom
    place(dx: trunk-x - 3mm, dy: trunk-bot, {
      line(start: (3mm, 0pt), end: (0mm, 4mm), stroke: (paint: color, thickness: 0.7pt))
      line(start: (7mm, 0pt), end: (7mm, 4mm), stroke: (paint: color, thickness: 0.7pt))
      line(start: (10mm, 0pt), end: (14mm, 3mm), stroke: (paint: color, thickness: 0.7pt))
      line(start: (14mm, 0pt), end: (18mm, 4mm), stroke: (paint: color, thickness: 0.7pt))
    })

    // 10m limit line
    let limit-y = 28mm
    place(dx: 10%, dy: limit-y, {
      line(start: (0pt, 0pt), end: (25%, 0pt), stroke: (paint: gray, thickness: 0.7pt, dash: "dashed"))
    })
    place(dx: 10%, dy: limit-y + 1mm,
      text(size: 5pt, fill: gray, weight: "bold", "10 м " + sym.arrow.l + " предел насоса")
    )

    // Pressure annotations
    place(dx: trunk-x + trunk-w + 3mm, dy: trunk-top + 3mm,
      text(size: 5pt, fill: gray, [$-15$ атм])
    )
    place(dx: trunk-x + trunk-w + 3mm, dy: trunk-bot - 5mm,
      text(size: 5pt, fill: gray, [$+1$ атм])
    )

    // "Когезия" label
    place(dx: 9%, dy: 14mm,
      text(size: 5pt, fill: color, weight: "medium", [когезия #sym.brace.r])
    )
  })
}


// ---- 8. Data Center Energy Flow ----
#let datacenter-diagram(color) = {
  let gray = rgb("#888888")
  let h = 38mm

  block(width: 100%, height: h, {
    let mid-y = 18mm

    // Electricity input arrow
    place(dx: 2%, dy: mid-y - 2pt, {
      line(start: (0pt, 0pt), end: (10mm, 0pt), stroke: (paint: color, thickness: 1pt))
    })
    place(dx: 2% + 10mm, dy: mid-y - 3pt,
      text(size: 6pt, fill: color, sym.arrow.r)
    )
    place(dx: 2%, dy: mid-y - 10pt,
      text(size: 5pt, fill: gray, [электричество])
    )
    place(dx: 2%, dy: mid-y + 5pt,
      text(size: 5pt, fill: gray, sym.zws + [$tilde$10 кВт])
    )

    // Server rack (rectangle with internal server slots)
    let rack-x = 24%
    let rack-w = 18mm
    let rack-h = 24mm
    place(dx: rack-x, dy: mid-y - rack-h / 2,
      rect(width: rack-w, height: rack-h, fill: color.lighten(85%), stroke: (paint: color, thickness: 1pt), radius: 1mm)
    )
    // Server slots — using place with absolute positions to avoid flow issues
    place(dx: rack-x + 2mm, dy: mid-y - rack-h / 2 + 2mm, {
      for i in range(4) {
        place(dx: 0pt, dy: i * 5.2mm,
          rect(width: rack-w - 4mm, height: 3.5mm, fill: color.lighten(70%), stroke: (paint: color.lighten(40%), thickness: 0.4pt))
        )
      }
    })
    place(dx: rack-x + 1mm, dy: mid-y + rack-h / 2 + 1mm,
      text(size: 5pt, fill: color, "серверная стойка")
    )

    // Heat arrows (upward from rack)
    place(dx: rack-x + 2mm, dy: mid-y - rack-h / 2 - 2mm, {
      for i in range(3) {
        place(dx: i * 5mm, dy: 0pt,
          text(size: 5.5pt, fill: rgb("#cc4444"), sym.arrow.t)
        )
      }
    })
    place(dx: rack-x, dy: mid-y - rack-h / 2 - 8mm,
      text(size: 5pt, fill: rgb("#cc4444"), "тепло " + sym.arrow.t)
    )

    // Cooling block
    let cool-x = 56%
    let cool-w = 18mm
    let cool-h = 14mm
    place(dx: cool-x, dy: mid-y - cool-h / 2,
      rect(width: cool-w, height: cool-h, fill: rgb("#d0e8f0"), stroke: (paint: rgb("#4a9ec5"), thickness: 0.8pt), radius: 1mm)
    )
    place(dx: cool-x + 1.5mm, dy: mid-y - 3pt,
      text(size: 5pt, fill: rgb("#2a6e8f"), "охлаждение")
    )

    // Arrow: rack -> cooling
    place(dx: rack-x + rack-w + 2mm, dy: mid-y - 2pt, {
      line(start: (0pt, 0pt), end: (8mm, 0pt), stroke: (paint: gray, thickness: 0.7pt))
    })
    place(dx: rack-x + rack-w + 10mm, dy: mid-y - 3pt,
      text(size: 5pt, fill: gray, sym.arrow.r)
    )

    // Output: heat
    place(dx: cool-x + cool-w + 2mm, dy: mid-y - 7mm, {
      line(start: (0pt, 0pt), end: (10mm, 0pt), stroke: (paint: rgb("#cc4444"), thickness: 0.8pt))
    })
    place(dx: cool-x + cool-w + 12mm, dy: mid-y - 8mm,
      text(size: 5pt, fill: rgb("#cc4444"), [#sym.arrow.r тепло])
    )

    // Output: data
    place(dx: cool-x + cool-w + 2mm, dy: mid-y + 3mm, {
      line(start: (0pt, 0pt), end: (10mm, 0pt), stroke: (paint: color, thickness: 0.8pt))
    })
    place(dx: cool-x + cool-w + 12mm, dy: mid-y + 2mm,
      text(size: 5pt, fill: color, [#sym.arrow.r данные])
    )

    // PUE label at bottom
    place(dx: 28%, dy: h - 5mm,
      text(size: 5.5pt, fill: gray, [PUE $= P_("полн") slash P_("серв")$ , идеал $= 1.0$])
    )
  })
}
