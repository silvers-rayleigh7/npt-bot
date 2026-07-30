/* Конструктор маршрута.

   Подбор идёт по реальному банку сюжетов (assets/storylines-index.json), а не
   по выдуманному списку: если под заданные параметры ничего не находится, так
   и говорим — не подставляем случайное, чтобы результат выглядел «как бы
   собранным».

   Время считаем прозрачно: 7 минут на точку + 5 минут переход между точками.
*/
(function () {
  'use strict';

  var MIN_AT_POINT = 7;
  var MIN_BETWEEN = 5;

  // Аудитории отличаются акцентом, языком результата и приоритетом дисциплин.
  var TRACKS = {
    place:   { color: 'var(--grass)',  label: 'маршрут',   goal: 'Маршрут для площадки' },
    guide:   { color: 'var(--sky)',    label: 'экскурсия', goal: 'Канва экскурсии' },
    teacher: { color: 'var(--terra)',  label: 'урок',      goal: 'Урок под открытым небом' }
  };

  var root = document.getElementById('builder');
  if (!root) return;

  var state = { track: 'place', field: '', minutes: 60 };
  var bank = [];

  var elResult = document.getElementById('b-result');
  var elField = document.getElementById('b-field-sel');
  var elTime = document.getElementById('b-time');
  var elRun = document.getElementById('b-run');

  fetch('/assets/storylines-index.json')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      bank = data;
      fillOptions();
      elRun.disabled = false;
    })
    .catch(function () {
      elResult.innerHTML = '<p class="b-empty">Не удалось загрузить банк сюжетов. ' +
        'Обновите страницу или откройте <a href="/storylines/">библиотеку</a>.</p>';
    });

  function fillOptions() {
    var fields = {};
    bank.forEach(function (s) {
      (s.tags || []).forEach(function (t) { fields[t] = (fields[t] || 0) + 1; });
    });
    // В список попадает только то, что реально есть в банке, с количеством —
    // человек сразу видит, где материала много, а где один сюжет.
    add(elField, fields, 'Любая дисциплина', 3);
  }

  function add(sel, counts, anyLabel, minCount) {
    var keys = Object.keys(counts).filter(function (k) {
      return !minCount || counts[k] >= minCount;
    }).sort(function (a, b) { return counts[b] - counts[a]; });
    sel.innerHTML = '<option value="">' + anyLabel + '</option>' +
      keys.map(function (k) {
        return '<option value="' + k + '">' + k + ' — ' + counts[k] + '</option>';
      }).join('');
  }

  function pick() {
    var maxPoints = Math.max(1, Math.floor(
      (state.minutes + MIN_BETWEEN) / (MIN_AT_POINT + MIN_BETWEEN)));

    var matched = bank.filter(function (s) {
      return !state.field || (s.tags || []).indexOf(state.field) >= 0;
    });

    // Точки с привязкой к местности идут первыми: по ним маршрут можно пройти
    // ногами, остальные годятся как материал.
    matched.sort(function (a, b) { return (b.geo ? 1 : 0) - (a.geo ? 1 : 0); });

    // Чередуем дисциплины, чтобы подряд не шли три сюжета об одном и том же.
    var used = {}, spread = [], rest = [];
    matched.forEach(function (s) {
      var key = (s.tags || [])[0] || '—';
      if (!used[key]) { used[key] = 1; spread.push(s); } else { rest.push(s); }
    });
    return { points: spread.concat(rest).slice(0, maxPoints), total: matched.length };
  }

  function render() {
    var res = pick();
    var t = TRACKS[state.track];

    if (!res.points.length) {
      elResult.innerHTML = '<p class="b-empty">Под эти параметры в банке пока нет сюжетов. ' +
        'Попробуйте расширить условия — снять ограничение по местности или дисциплине.</p>';
      elResult.classList.add('show');
      return;
    }

    var n = res.points.length;
    var minutes = n * MIN_AT_POINT + Math.max(0, n - 1) * MIN_BETWEEN;
    var withGeo = res.points.filter(function (s) { return s.geo; }).length;

    var html =
      '<div class="b-res-head">' +
        '<h3>' + t.goal + '</h3>' +
        '<div class="b-chips">' +
          '<span class="chip">' + n + ' ' + plural(n, 'точка', 'точки', 'точек') + '</span>' +
          '<span class="chip">≈ ' + minutes + ' мин</span>' +
          (withGeo ? '<span class="chip">' + withGeo + ' с привязкой к месту</span>' : '') +
        '</div>' +
        '<p class="b-res-note">Время посчитано как ' + MIN_AT_POINT + ' минут на точку и ' +
          MIN_BETWEEN + ' минут переход. Подобрано из ' + res.total +
          ' подходящих ' + plural(res.total, 'сюжета', 'сюжетов', 'сюжетов') + ' банка.</p>' +
      '</div><ol class="b-points">';

    res.points.forEach(function (s, i) {
      html += '<li class="b-point" style="--pc:' + t.color + '">' +
        '<span class="b-point-n">' + (i + 1) + '</span>' +
        '<span class="b-point-body">' +
          '<a href="/storylines/' + s.slug + '/">' + esc(s.title) + '</a>' +
          '<span class="b-point-meta">' +
            (s.tags || []).slice(0, 2).join(' · ') +
            (s.geo ? '' : ' · без точки на карте') +
          '</span>' +
        '</span></li>';
    });

    html += '</ol><div class="b-res-actions">' +
      (state.track === 'teacher'
        ? '<a href="/teacher/" class="btn btn-primary">Собрать методичку к уроку</a>'
        : '<a href="/routes/" class="btn btn-primary">Посмотреть готовый маршрут</a>') +
      '<button class="btn btn-ghost" type="button" id="b-again">Пересобрать</button>' +
      '</div>';

    elResult.innerHTML = html;
    elResult.classList.add('show');
    document.getElementById('b-again').onclick = function () {
      // Пересборка меняет порядок внутри отобранного, а не подмешивает случайное:
      // набор остаётся честным ответом на заданные параметры.
      bank.push(bank.shift());
      render();
    };
    if (window.initReveal) window.initReveal(elResult);
  }

  function plural(n, one, few, many) {
    var a = Math.abs(n) % 100, b = a % 10;
    if (a > 10 && a < 20) return many;
    if (b > 1 && b < 5) return few;
    return b === 1 ? one : many;
  }
  function esc(s) {
    return String(s).replace(/[&<>]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c];
    });
  }

  root.addEventListener('click', function (e) {
    var tab = e.target.closest('.b-tab');
    if (!tab) return;
    root.querySelectorAll('.b-tab').forEach(function (x) {
      x.classList.toggle('active', x === tab);
      x.setAttribute('aria-selected', String(x === tab));
    });
    state.track = tab.dataset.track;
    root.style.setProperty('--accent', TRACKS[state.track].color);
  });

  elField.addEventListener('change', function () { state.field = this.value; });
  elTime.addEventListener('change', function () { state.minutes = parseInt(this.value, 10); });
  elRun.addEventListener('click', render);
})();
