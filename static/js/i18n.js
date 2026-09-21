/**
 * Charvak i18n Loader (Session G5 / C6)
 * Loads /static/locales/{lang}.json and applies translations to elements
 * marked with [data-i18n], [data-i18n-placeholder], [data-i18n-title].
 *
 * Language selection priority:
 *   1. localStorage.charvak_lang
 *   2. window.CHARVAK_LANG (set inline in base.html)
 *   3. Browser Accept-Language match against supported languages
 *   4. Fallback: 'en'
 *
 * Public API:
 *   changeLanguage(langCode)  -> saves + reloads
 *   t(key, fallback)          -> returns translated string
 */
(function () {
  'use strict';

  var SUPPORTED = ['en','hi','te','ta','kn','ml','mr','bn','gu','pa',
                   'es','fr','de','pt','it','nl','ru','ar','zh','ja',
                   'ko','tr','vi','th','id','ms','fil','sw','am','ha',
                   'yo','ig','zu','so'];
  var DEFAULT_LANG = 'en';
  var STORAGE_KEY = 'charvak_lang';

  var currentLang = detectLanguage();
  var catalog = {};
  var catalogReady = false;

  // ---------- detection ----------
  function detectLanguage() {
    try {
      var stored = localStorage.getItem(STORAGE_KEY);
      if (stored && SUPPORTED.indexOf(stored) !== -1) return stored;
    } catch (e) { /* localStorage blocked */ }

    if (window.CHARVAK_LANG && SUPPORTED.indexOf(window.CHARVAK_LANG) !== -1) {
      return window.CHARVAK_LANG;
    }

    // Accept-Language sniffing (rough)
    var nav = (navigator.language || navigator.userLanguage || '').toLowerCase();
    var short = nav.split('-')[0];
    if (SUPPORTED.indexOf(short) !== -1) return short;

    return DEFAULT_LANG;
  }

  // ---------- catalog ----------
  function loadCatalog(lang, done) {
    // English is the base — always available even if fetch fails
    if (lang === DEFAULT_LANG) {
      fetch('/static/locales/en.json')
        .then(function (r) { return r.ok ? r.json() : {}; })
        .then(function (j) { catalog = j || {}; catalogReady = true; done(); })
        .catch(function () { catalog = {}; catalogReady = true; done(); });
      return;
    }
    // Non-English: fetch both (fallback + target)
    Promise.all([
      fetch('/static/locales/en.json').then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; }),
      fetch('/static/locales/' + lang + '.json').then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; })
    ]).then(function (results) {
      catalog = mergeDeep(results[0] || {}, results[1] || {});
      catalogReady = true;
      done();
    });
  }

  function mergeDeep(base, override) {
    var out = {};
    var k;
    for (k in base) if (base.hasOwnProperty(k)) out[k] = base[k];
    for (k in override) {
      if (!override.hasOwnProperty(k)) continue;
      if (out[k] && typeof out[k] === 'object' && typeof override[k] === 'object') {
        out[k] = mergeDeep(out[k], override[k]);
      } else {
        out[k] = override[k];
      }
    }
    return out;
  }

  // ---------- lookup ----------
  function lookup(key) {
    if (!key) return null;
    var parts = key.split('.');
    var node = catalog;
    for (var i = 0; i < parts.length; i++) {
      if (node == null || typeof node !== 'object') return null;
      node = node[parts[i]];
    }
    return typeof node === 'string' ? node : null;
  }

  function t(key, fallback) {
    var v = lookup(key);
    return v != null ? v : (fallback != null ? fallback : key);
  }

  // ---------- apply ----------
  function apply() {
    // 1. Text content
    var textEls = document.querySelectorAll('[data-i18n]');
    for (var i = 0; i < textEls.length; i++) {
      var el = textEls[i];
      var key = el.getAttribute('data-i18n');
      var val = lookup(key);
      if (val != null) el.textContent = val;
    }

    // 2. Placeholders
    var phEls = document.querySelectorAll('[data-i18n-placeholder]');
    for (var j = 0; j < phEls.length; j++) {
      var el2 = phEls[j];
      var key2 = el2.getAttribute('data-i18n-placeholder');
      var val2 = lookup(key2);
      if (val2 != null) el2.setAttribute('placeholder', val2);
    }

    // 3. Title attributes
    var tiEls = document.querySelectorAll('[data-i18n-title]');
    for (var k = 0; k < tiEls.length; k++) {
      var el3 = tiEls[k];
      var key3 = el3.getAttribute('data-i18n-title');
      var val3 = lookup(key3);
      if (val3 != null) el3.setAttribute('title', val3);
    }

    // 4. Reflect current lang on <html> if it lacks one (RTL handled later)
    if (document.documentElement && !document.documentElement.getAttribute('lang')) {
      document.documentElement.setAttribute('lang', currentLang);
    }
  }

  // ---------- public API ----------
  window.changeLanguage = function (langCode) {
    if (!langCode || SUPPORTED.indexOf(langCode) === -1) return;
    try { localStorage.setItem(STORAGE_KEY, langCode); } catch (e) {}
    window.CHARVAK_LANG = langCode;
    location.reload();
  };

  window.t = t;
  window.currentLang = currentLang;

  // ---------- boot ----------
  function boot() {
    loadCatalog(currentLang, function () {
      // Ensure the dropdown reflects the current language
      var sel = document.getElementById('langSelector');
      if (sel) sel.value = currentLang;
      apply();
      // Fire an event for other scripts that want to react
      try {
        window.dispatchEvent(new CustomEvent('charvak:i18nready', { detail: { lang: currentLang } }));
      } catch (e) {}
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();