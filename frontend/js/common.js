
const CHART_COLORS = {
  accent: "#89b4fa",
  warn: "#fab387",
  lavender: "#cba6f7",
  muted: "#7f849c",
  grid: "#313244",
};

Chart.defaults.color = CHART_COLORS.muted;
Chart.defaults.borderColor = CHART_COLORS.grid;
Chart.defaults.font.family = "'Archivo', system-ui, sans-serif";

const charts = {};

function renderChart(id, config) {
  if (charts[id]) charts[id].destroy();
  const canvas = document.getElementById(id);
  if (!canvas) return;
  charts[id] = new Chart(canvas, config);
}

function domTick() {
  return window.Alpine && window.Alpine.nextTick
    ? window.Alpine.nextTick()
    : new Promise((res) => requestAnimationFrame(res));
}

const refLine = (from, to, y, label) => ({
  label,
  data: [{ x: from, y }, { x: to, y }],
  borderColor: CHART_COLORS.muted, borderDash: [6, 6], pointRadius: 0,
});

function postJSON(path, body) {
  return fetch(`/api/${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then((r) => {
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  });
}
