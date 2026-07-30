/* Поведение каркаса: тень шапки при скролле и мобильное меню. */
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    var head = document.querySelector('.site-head');
    var burger = document.querySelector('.burger');
    var menu = document.querySelector('.nav-mobile');

    if (head) {
      var onScroll = function () {
        head.classList.toggle('scrolled', window.scrollY > 8);
      };
      window.addEventListener('scroll', onScroll, { passive: true });
      onScroll();
    }

    if (burger && menu) {
      burger.addEventListener('click', function () {
        var open = burger.getAttribute('aria-expanded') === 'true';
        burger.setAttribute('aria-expanded', String(!open));
        menu.classList.toggle('open', !open);
      });
      // Переход по ссылке закрывает меню: иначе после возврата «назад»
      // страница открывается с уже раскрытым меню поверх контента.
      menu.addEventListener('click', function (e) {
        if (e.target.closest('a')) {
          burger.setAttribute('aria-expanded', 'false');
          menu.classList.remove('open');
        }
      });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && menu.classList.contains('open')) {
          burger.setAttribute('aria-expanded', 'false');
          menu.classList.remove('open');
          burger.focus();
        }
      });
    }
  });
})();
