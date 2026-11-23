
const I18N_STORAGE_KEY = 'quanty.lang';

function i18nDetect() {
  const saved = localStorage.getItem(I18N_STORAGE_KEY);
  if (saved === 'es' || saved === 'en') return saved;
  return (navigator.language || '').toLowerCase().startsWith('en') ? 'en' : 'es';
}

function i18nLookup(dict, path) {
  return path.split('.').reduce((node, key) => (node == null ? node : node[key]), dict);
}

function i18nFormat(text, vars) {
  if (!vars) return text;
  return text.replace(/\{(\w+)\}/g, (m, k) => (vars[k] != null ? vars[k] : m));
}

function t(key, vars) {
  const lang = window.Alpine && Alpine.store('i18n') ? Alpine.store('i18n').lang : 'es';
  const dicts = { es: window.I18N_ES, en: window.I18N_EN };
  const value = i18nLookup(dicts[lang], key);
  const fallback = value == null ? i18nLookup(dicts[lang === 'es' ? 'en' : 'es'], key) : value;
  return i18nFormat(fallback != null ? fallback : key, vars);
}

function tLocale() {
  return window.Alpine && Alpine.store('i18n') ? Alpine.store('i18n').lang : 'es';
}

document.addEventListener('alpine:init', () => {
  const initial = i18nDetect();
  Alpine.store('i18n', {
    lang: initial,
    t: (key, vars) => t(key, vars),
    toggle() {
      this.lang = this.lang === 'es' ? 'en' : 'es';
      localStorage.setItem(I18N_STORAGE_KEY, this.lang);
      document.documentElement.lang = this.lang;
    },
  });
  document.documentElement.lang = initial;
});
