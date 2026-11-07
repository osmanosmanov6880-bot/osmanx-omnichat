/* OSMANX OMNICHAT - first-party website messenger, external CSS and no tracking. */
(function () {
  'use strict';
  var script = document.currentScript;
  if (!script || !script.src) return;
  var key = script.getAttribute('data-omnichat-key') || '';
  if (!/^[a-zA-Z0-9_-]{20,70}$/.test(key)) return;
  var origin = new URL(script.src, location.href).origin;
  var id = 'omnichat-site-' + key.slice(0, 8);
  if (document.getElementById(id)) return;
  var left = script.getAttribute('data-position') === 'left';
  var link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = origin + '/assets/embed.css';
  document.head.appendChild(link);
  var wrap = document.createElement('div');
  wrap.id = id;
  wrap.className = 'omnichat-embed' + (left ? ' omnichat-left' : '');
  wrap.setAttribute('data-omnichat-root', '');
  var button = document.createElement('button');
  button.type = 'button';
  button.setAttribute('aria-label', 'Open customer support chat');
  button.setAttribute('aria-expanded', 'false');
  button.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 11.5a8.5 8.5 0 0 1-8.5 8.5H5l-2 2v-6.5a8.5 8.5 0 1 1 17-4Z"/><path d="M8 11h8M8 15h5"/></svg>';
  var frame = document.createElement('iframe');
  frame.src = origin + '/widget/' + encodeURIComponent(key);
  frame.setAttribute('title', 'Customer support chat');
  frame.setAttribute('loading', 'lazy');
  frame.setAttribute('allow', 'clipboard-write');
  button.addEventListener('click', function () {
    var isOpen = wrap.classList.toggle('open');
    button.setAttribute('aria-expanded', String(isOpen));
    button.setAttribute('aria-label', isOpen ? 'Close customer support chat' : 'Open customer support chat');
  });
  wrap.appendChild(frame); wrap.appendChild(button);
  document.body.appendChild(wrap);
}());
