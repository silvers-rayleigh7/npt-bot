/* Появление блоков при скролле.

   Элементам с классом .rev проставляется .in, когда они попадают в кадр.
   Наблюдение снимается сразу после срабатывания: блок появляется один раз,
   при обратном скролле не мигает.

   initReveal() вызывается повторно после динамической отрисовки (фильтры
   библиотеки, результат конструктора) — новые узлы тоже должны появиться. */
(function () {
  'use strict';

  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Прячем блоки только если умеем их показать: наблюдатель есть и движение
  // не отключено системно. Без этого класса стили появления не работают вовсе,
  // и контент виден сразу — страница остаётся читаемой при любой осечке скрипта.
  if (!reduce && 'IntersectionObserver' in window) {
    document.documentElement.classList.add('js-reveal');
  }

  // Типы появления: .rev — базовый, остальные подобраны под смысл блока
  // (карточки выходят снизу, парные блоки — с боков, схемы — приближением,
  // списки — каскадом, шаги маршрута — вместе с линией тропы).
  var SEL = ['.rev', '.rise', '.slide-l', '.slide-r', '.zoom', '.stagger', '.steps', '.step', '.track']
    .map(function (c) { return c + ':not(.in)'; }).join(',');

  function initReveal(root) {
    var nodes = (root || document).querySelectorAll(SEL);
    if (!nodes.length) return;

    // Нет поддержки наблюдателя или анимации отключены системно —
    // показываем сразу, без промежуточного невидимого состояния.
    if (reduce || !('IntersectionObserver' in window)) {
      nodes.forEach(function (n) { n.classList.add('in'); });
      return;
    }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12 });

    nodes.forEach(function (n) { io.observe(n); });
  }

  window.initReveal = initReveal;
  document.addEventListener('DOMContentLoaded', function () { initReveal(); });
})();
