// Tropa POI Card Template
// Usage: #import "template.typ": poi-card
// Then: #poi-card(poi_name: ..., poi_number: ..., ...)

#let level-label(level) = {
  if level == "L1" { "Базовый" }
  else if level == "L2" { "С формулами" }
  else if level == "L3" { "Доп. факты" }
  else { level }
}

#let level-color(level) = {
  if level == "L1" { rgb("#2f6f63") }
  else if level == "L2" { rgb("#3c7dd9") }
  else if level == "L3" { rgb("#e0a72f") }
  else { rgb("#2f6f63") }
}

#let poi-card(
  poi_name: "POI Name",
  poi_number: 1,
  poi_color: "#2f6f63",
  topic: "",
  level: "L1",
  content_text: [],
  expert: "",
  tags: (),
  diagram: none,
) = {
  let primary = rgb(poi_color)
  let dark = rgb("#1a4a41")
  let bg = rgb("#f7f8f3")
  let text-color = rgb("#17211d")
  let muted = rgb("#52615a")
  let lvl-color = level-color(level)

  // L1: fixed A5 height (text is short). L2/L3: auto (text with formulas may be long).
  let page-height = if level == "L1" { 148mm } else { auto }

  set page(
    width: 210mm,
    height: page-height,
    margin: (top: 0mm, bottom: 12mm, left: 16mm, right: 16mm),
    fill: bg,
    footer: context {
      set text(size: 7.5pt, fill: muted)
      grid(
        columns: (1fr, auto),
        align: (left, right),
        [#if expert != "" [#emph(expert)]],
        [tropa.fmin.xyz],
      )
    },
  )

  set text(font: "Noto Sans", size: 10pt, fill: text-color, lang: "ru")
  set par(justify: true, leading: 0.6em)

  // Header band
  place(
    top + left,
    dx: -16mm,
    dy: 0mm,
    block(
      width: 210mm,
      height: 22mm,
      fill: primary,
      inset: (x: 16mm, y: 0mm),
      align(horizon, {
        grid(
          columns: (auto, 1fr, auto),
          column-gutter: 12pt,
          align: (center + horizon, left + horizon, right + horizon),
          // Number circle
          place(center + horizon,
            circle(
              radius: 10pt,
              fill: white,
              stroke: none,
              align(center + horizon, text(
                size: 12pt,
                weight: "bold",
                fill: primary,
                [#poi_number],
              )),
            ),
          ),
          // POI name
          text(
            size: 13pt,
            weight: "bold",
            fill: white,
            poi_name,
          ),
          // Level badge
          box(
            fill: white.transparentize(20%),
            radius: 10pt,
            inset: (x: 10pt, y: 4pt),
            text(
              size: 8pt,
              weight: "bold",
              fill: primary,
              level-label(level),
            ),
          ),
        )
      }),
    ),
  )

  v(26mm)

  // Topic subtitle
  if topic != "" {
    text(size: 8.5pt, fill: muted, style: "italic", topic)
    v(6pt)
  }

  // Diagram (only for L1 and L2, not L3 which is text-heavy)
  if diagram != none and (level == "L1" or level == "L2") {
    diagram
    v(4pt)
  }

  // Body content
  set text(size: 9.5pt, fill: text-color)
  content_text

  v(1fr)

  // Tags row
  if tags.len() > 0 {
    let tag-boxes = tags.map(t => {
      box(
        fill: rgb("#e8f0ee"),
        radius: 5pt,
        inset: (x: 7pt, y: 3pt),
        text(size: 7pt, weight: "medium", fill: rgb("#2f6f63"), t),
      )
    })
    stack(dir: ltr, spacing: 6pt, ..tag-boxes)
  }
}
