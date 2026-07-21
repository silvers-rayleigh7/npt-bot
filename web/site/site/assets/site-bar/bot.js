/* site-bar — виджет-гид «Тропы».
   Читает текст текущей страницы (сюжет/гид), шлёт вопрос на /api/chat,
   рендерит ответ. Бэкенд: GigaChat-2-Max → OpenRouter fallback. */
(function () {
  "use strict";

  // Эндпоинт можно переопределить через <body data-bot-api="https://...">. По умолчанию — тот же origin.
  var API = (document.body && document.body.dataset.botApi) || "/api/chat";
  var GEO_API = (document.body && document.body.dataset.geoApi) || "/api/geo";
  var MAX_CTX = 6000;
  var geo = null;   // {lat, lon} после того, как пользователь разрешил геолокацию

  // ---- Сбор контекста страницы --------------------------------------------
  function pageContext() {
    var parts = [];
    var h1 = document.querySelector(".sg-hero h1, h1");
    if (h1) parts.push("Заголовок: " + h1.textContent.trim());
    var kicker = document.querySelector(".sg-kicker");
    if (kicker) parts.push("Регион: " + kicker.textContent.trim());
    var deck = document.querySelector(".sg-deck");
    if (deck && deck.textContent.trim()) parts.push(deck.textContent.trim());

    // Все уровни сюжета (Кратко / Как работает / Глубже) — берём из DOM, в т.ч. скрытые табы.
    var levels = document.querySelectorAll(".body.lvl");
    if (levels.length) {
      levels.forEach(function (el) {
        var label = el.previousElementSibling; // не используется, текста уровня достаточно
        var txt = el.textContent.replace(/\s+/g, " ").trim();
        if (txt) parts.push(txt);
      });
    } else {
      // Не сюжет (гид, индекс) — берём основной контейнер.
      var main = document.querySelector(".w") || document.body;
      var txt = main.textContent.replace(/\s+/g, " ").trim();
      if (txt) parts.push(txt);
    }
    return parts.join("\n\n").slice(0, MAX_CTX);
  }

  // ---- Мини-рендер markdown (без внешних либ) + экранирование --------------
  function esc(s) {
    return s.replace(/[&<>]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c];
    });
  }
  function renderMd(text) {
    var html = esc(text);
    html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    // Маркированные списки
    html = html.replace(/(?:^|\n)[-•] (.+)/g, "\n<li>$1</li>");
    html = html.replace(/(<li>[\s\S]*?<\/li>)/g, "<ul>$1</ul>").replace(/<\/ul>\s*<ul>/g, "");
    // Абзацы
    html = html.split(/\n{2,}/).map(function (p) {
      p = p.trim();
      if (!p) return "";
      return /^<(ul|li)/.test(p) ? p : "<p>" + p.replace(/\n/g, "<br>") + "</p>";
    }).join("");
    return html;
  }

  // ---- Построение DOM виджета ---------------------------------------------
  var SVG = {
    chat: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-8.5 8.5 8.5 8.5 0 0 1-3.8-.9L3 21l1.9-5.7a8.5 8.5 0 0 1-.9-3.8 8.38 8.38 0 0 1 8.5-8.5 8.5 8.5 0 0 1 8.5 8.5z"/></svg>',
    leaf: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/><path d="M2 21c0-3 1.85-5.36 5.08-6"/></svg>',
    send: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2 11 13"/><path d="M22 2 15 22l-4-9-9-4z"/></svg>',
    x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>'
  };
  var CHIPS = ["О чём этот сюжет?", "Объясни проще", "Где это можно увидеть?"];
  var GEO_CHIP = "📍 Рядом со мной";

  var fab = document.createElement("button");
  fab.className = "sb-fab";
  fab.setAttribute("aria-label", "Спросить гида");
  fab.innerHTML = SVG.chat + "<span>Чем помочь?</span>";

  var panel = document.createElement("div");
  panel.className = "sb-panel";
  panel.innerHTML =
    '<div class="sb-head">' +
      '<div class="sb-head-ic">' + SVG.leaf + "</div>" +
      '<div><div class="sb-head-t">Гид «Тропы»</div><div class="sb-head-s">спросите про этот сюжет</div></div>' +
      '<button class="sb-head-x" aria-label="Закрыть">' + SVG.x + "</button>" +
    "</div>" +
    '<div class="sb-log" id="sb-log"></div>' +
    '<form class="sb-form" id="sb-form">' +
      '<textarea class="sb-input" id="sb-input" rows="1" placeholder="Спросите о сюжете…"></textarea>' +
      '<button class="sb-send" id="sb-send" type="submit" aria-label="Отправить">' + SVG.send + "</button>" +
    "</form>" +
    '<div class="sb-foot">Гид может ошибаться — проверяйте важные факты</div>';

  document.body.appendChild(fab);
  document.body.appendChild(panel);

  var log = panel.querySelector("#sb-log");
  var form = panel.querySelector("#sb-form");
  var input = panel.querySelector("#sb-input");
  var sendBtn = panel.querySelector("#sb-send");
  var history = [];
  var greeted = false;
  var busy = false;

  // ---- Сообщения в ленте ---------------------------------------------------
  function addMsg(role, text) {
    var el = document.createElement("div");
    el.className = "sb-msg " + (role === "user" ? "sb-user" : "sb-bot");
    el.innerHTML = role === "user" ? esc(text).replace(/\n/g, "<br>") : renderMd(text);
    log.appendChild(el);
    renderMath(el);
    log.scrollTop = log.scrollHeight;
    return el;
  }
  function renderMath(el) {
    if (window.renderMathInElement) {
      try {
        window.renderMathInElement(el, {
          delimiters: [{ left: "$$", right: "$$", display: true }, { left: "$", right: "$", display: false }],
          throwOnError: false, ignoredClasses: ["katex"]
        });
      } catch (e) {}
    }
  }
  function greet() {
    if (greeted) return;
    greeted = true;
    var hint = document.createElement("div");
    hint.className = "sb-hint";
    hint.textContent = "Здравствуйте! Я помогу разобраться с этим сюжетом — спрашивайте.";
    log.appendChild(hint);
    var chips = document.createElement("div");
    chips.className = "sb-chips";
    var gb = document.createElement("button");
    gb.className = "sb-chip sb-chip-geo"; gb.type = "button"; gb.textContent = GEO_CHIP;
    gb.onclick = requestGeo;                       // не текстовый вопрос — запрос геолокации
    chips.appendChild(gb);
    CHIPS.forEach(function (c) {
      var b = document.createElement("button");
      b.className = "sb-chip"; b.type = "button"; b.textContent = c;
      b.onclick = function () { input.value = c; submit(); };
      chips.appendChild(b);
    });
    log.appendChild(chips);
  }

  // ---- Отправка ------------------------------------------------------------
  function submit() {
    var q = input.value.trim();
    if (!q || busy) return;
    busy = true; sendBtn.disabled = true;
    document.querySelectorAll(".sb-chips,.sb-hint").forEach(function (n) { n.remove(); });
    addMsg("user", q);
    input.value = ""; input.style.height = "auto";

    var typing = document.createElement("div");
    typing.className = "sb-msg sb-bot sb-typing";
    typing.innerHTML = "<span></span><span></span><span></span>";
    log.appendChild(typing); log.scrollTop = log.scrollHeight;

    // Пока геолокация задана — идём на /api/geo (ответ учитывает место + ближайшие точки).
    var payload = { question: q, page_context: pageContext(), history: history.slice(-8) };
    if (geo) { payload.lat = geo.lat; payload.lon = geo.lon; }

    fetch(geo ? GEO_API : API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        typing.remove();
        var a = (d && d.answer) || "Извините, ответа не получилось. Попробуйте ещё раз.";
        addMsg("bot", a);
        if (d && d.nearby && d.nearby.length) renderNearby(d.nearby);
        history.push({ role: "user", content: q });
        history.push({ role: "assistant", content: a });
      })
      .catch(function () {
        typing.remove();
        addMsg("bot", "Не получилось связаться с сервером. Проверьте интернет и попробуйте снова.");
      })
      .finally(function () { busy = false; sendBtn.disabled = false; input.focus(); });
  }

  // ---- Геолокация ----------------------------------------------------------
  function fmtDist(m) { return m < 1000 ? Math.round(m) + " м" : (m / 1000).toFixed(1) + " км"; }

  function renderNearby(list) {
    var wrap = document.createElement("div");
    wrap.className = "sb-nearby";
    var t = document.createElement("div");
    t.className = "sb-nearby-t"; t.textContent = "Ближайшие точки тропы:";
    wrap.appendChild(t);
    list.forEach(function (n) {
      var a = document.createElement("a");
      a.className = "sb-nearby-link";
      a.href = n.url; a.target = "_blank"; a.rel = "noopener";
      a.innerHTML = esc(n.title) + ' <span class="sb-nearby-d">' + esc(fmtDist(n.dist_m)) + "</span>";
      wrap.appendChild(a);
    });
    log.appendChild(wrap);
    log.scrollTop = log.scrollHeight;
  }

  function requestGeo() {
    document.querySelectorAll(".sb-chips,.sb-hint").forEach(function (n) { n.remove(); });
    if (!navigator.geolocation) {
      addMsg("bot", "Ваш браузер не поддерживает геолокацию — спросите обычным текстом.");
      return;
    }
    var note = addMsg("bot", "Определяю, где вы…");
    navigator.geolocation.getCurrentPosition(
      function (pos) {
        geo = { lat: pos.coords.latitude, lon: pos.coords.longitude };
        note.innerHTML = renderMd(
          "Нашёл. Координаты уходят только на карты OpenStreetMap, чтобы найти ближайшие точки — ничего не сохраняем."
        );
        input.value = "Что интересного рядом со мной?"; submit();
      },
      function () {
        note.innerHTML = renderMd(
          "Не удалось определить местоположение — нет разрешения или сигнала. Можно спросить обычным текстом."
        );
      },
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 }
    );
  }

  // ---- События -------------------------------------------------------------
  function open() {
    panel.classList.add("sb-open"); fab.classList.add("sb-hidden");
    greet(); setTimeout(function () { input.focus(); }, 200);
  }
  function close() { panel.classList.remove("sb-open"); fab.classList.remove("sb-hidden"); }

  fab.onclick = open;
  panel.querySelector(".sb-head-x").onclick = close;
  form.addEventListener("submit", function (e) { e.preventDefault(); submit(); });
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); }
  });
  input.addEventListener("input", function () {
    input.style.height = "auto"; input.style.height = Math.min(input.scrollHeight, 110) + "px";
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
})();
