
const PRESETS = {
  birthday: (s) => { s.birthday = { people: 23, trials: 10000 }; },
  monty: (s) => { s.monty = { trials: 10000 }; },
  bayes: (s) => { s.bayes = { prevalence: 0.01, sensitivity: 0.99, false_positive_rate: 0.01, population: 10000 }; },
  gambler: (s) => { s.gambler = { streaks: 500 }; },
  clt: (s) => { s.clt = { distribution: 'exponential', sample_size: 5, samples: 20000 }; },
  frequencies: (s) => { s.freq.raw = PRESET_DATA.frequencies; },
  regression: (s) => { s.reg = { xRaw: PRESET_DATA.regressionX, yRaw: PRESET_DATA.regressionY, x0: 5.5, error: '' }; },
  confidence: (s) => { s.confidence = { hits: 300, total: 400, level: 0.99 }; },
};

function app() {
  return {
    active: 'birthday',
    loading: false,
    modal: { open: false, title: '', sub: '', value: '', _resolve: null, _round: null },
    tabs: [
      { id: 'birthday' }, { id: 'monty' }, { id: 'bayes' }, { id: 'gambler' },
      { id: 'clt' }, { id: 'frequencies' }, { id: 'regression' }, { id: 'confidence' },
      { id: 'score' },
    ],
    birthday: { people: 30, trials: 10000 },
    monty: { trials: 5000 },
    bayes: { prevalence: 0.01, sensitivity: 0.99, false_positive_rate: 0.01, population: 10000 },
    gambler: { streaks: 200 },
    clt: { distribution: 'uniform', sample_size: 5, samples: 20000 },
    freq: { raw: '', error: '' },
    reg: { xRaw: '', yRaw: '', x0: '', error: '' },
    confidence: { hits: 300, total: 400, level: 0.99 },
    results: {},

    ...probRounds(),
    ...statRounds(),

    switchTab(id) {
      this.active = id;
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    pct(v) {
      return v == null ? '-' : (v * 100).toFixed(1) + '%';
    },

    setGuess(round, question) {
      return new Promise((resolve) => {
        this.modal = {
          open: true,
          title: question,
          sub: t('modal.sub'),
          value: '',
          _resolve: resolve,
          _round: round,
        };
        setTimeout(() => document.getElementById('modal-input')?.focus(), 60);
      });
    },

    submitGuess() {
      const g = parseFloat(this.modal.value);
      if (isNaN(g) || g < 0 || g > 100) return;
      const { _resolve, _round } = this.modal;
      this.modal.open = false;
      this.results[_round] = { ...this.results[_round], guess: g / 100 };
      _resolve(true);
    },

    cancelGuess() {
      const { _resolve } = this.modal;
      this.modal.open = false;
      _resolve(false);
    },

    preset(round) {
      PRESETS[round](this);
    },

    async run(key, fn) {
      this.loading = true;
      try {
        await fn();
      } catch (e) {
        alert(t('common.error_alert', { msg: e.message }));
        console.error(e);
      } finally {
        this.loading = false;
      }
    },

    score() {
      const rows = this.scoredRounds();
      if (!rows.length) return null;
      const avg = rows.reduce((s, r) => s + r.error, 0) / rows.length;
      return 100 - avg;
    },

    scoredRounds() {
      const rows = [];
      const add = (key, round, real) => {
        const r = this.results[key];
        if (r && r.guess != null) rows.push({ round, guess: r.guess, real, error: Math.abs(r.guess - real) * 100 });
      };
      add('birthday', 'score.r1', this.results.birthday?.theoretical);
      add('bayes', 'score.r3', this.results.bayes?.theoretical);
      add('gambler', 'score.r4', 0.5);
      add('confidence', 'score.r8', this.results.confidence?.interval?.p_hat);
      return rows;
    },

    verdict() {
      const s = this.score();
      if (s >= 90) return t('score.v90');
      if (s >= 75) return t('score.v75');
      if (s >= 60) return t('score.v60');
      return t('score.v0');
    },

    scoreRows() {
      return [...this.scoredRounds()];
    },
  };
}
