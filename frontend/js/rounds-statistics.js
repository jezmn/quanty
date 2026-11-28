
window.statRounds = () => ({
  async runFrequencies() {
    await this.run('frequencies', async () => {
      const values = this.parseList(this.freq.raw);
      if (!values) { this.freq.error = window.t('r6.err'); return; }
      this.freq.error = '';
      const r = await postJSON('frequencies', { values });
      this.results.frequencies = r;
      await domTick();
      renderChart('chart-frequencies', {
        type: 'bar',
        data: {
          labels: r.histogram.labels,
          datasets: [
            {
              label: window.t('f.f6.lbl_f'), data: r.histogram.frequency,
              backgroundColor: 'rgba(137, 180, 250, 0.30)', borderColor: CHART_COLORS.accent, borderWidth: 1,
            },
            {
              type: 'line', label: window.t('f.f6.lbl_F'), data: r.table.map(t => t.cumulative),
              borderColor: CHART_COLORS.warn, pointRadius: 3, yAxisID: 'y2',
            },
          ],
        },
        options: {
          scales: {
            y: { title: { display: true, text: 'f' }, beginAtZero: true },
            y2: {
              position: 'right', title: { display: true, text: window.t('f.f6.ax_F') },
              beginAtZero: true, grid: { drawOnChartArea: false },
            },
          },
        },
      });
      const s = r.summary;
      this.results.frequencies.formula =
        `${window.t('f.f6.head1', { n: s.n, r: s.range.toFixed(2) })} ·\n`
        + `${window.t('f.f6.head2', { k: s.classes })} ·\n`
        + `${window.t('f.f6.head3', { a: s.amplitude.toFixed(2) })}\n\n`
        + window.t('f.f6.grp', {
          m: r.mean.toFixed(2), md: r.median.toFixed(2), mo: r.mode.toFixed(2),
          q1: r.q1.toFixed(2), q3: r.q3.toFixed(2),
        }) + '\n'
        + window.t('f.f6.raw', { m: r.raw.mean.toFixed(2), md: r.raw.median.toFixed(2) }) + '\n'
        + window.t('f.f6.note');
    });
  },

  parseList(text) {
    const values = text.split(/[\s,;]+/).filter(Boolean).map(Number);
    if (!values.length || values.some(isNaN)) return null;
    return values;
  },

  async runRegression() {
    await this.run('regression', async () => {
      const x = this.parseList(this.reg.xRaw), y = this.parseList(this.reg.yRaw);
      if (!x || !y || x.length !== y.length || x.length < 4) {
        this.reg.error = window.t('r7.err'); return;
      }
      this.reg.error = '';
      const r = await postJSON('regression', { x, y, x0: this.reg.x0 === '' ? null : this.reg.x0 });
      this.results.regression = r;
      await domTick();
      const lin = r.models.linear, quad = r.models.quadratic;
      renderChart('chart-regression', {
        type: 'scatter',
        data: {
          datasets: [
            {
              type: 'scatter', label: window.t('f.r7.lbl_data'),
              data: r.scatter.x.map((v, i) => ({ x: v, y: r.scatter.y[i] })),
              borderColor: CHART_COLORS.accent, backgroundColor: CHART_COLORS.accent, pointRadius: 4,
            },
            {
              type: 'line', label: window.t('f.r7.lbl_curve_lin', { r2: lin.r2.toFixed(3) }),
              data: r.curves.linear.x.map((v, i) => ({ x: v, y: r.curves.linear.y[i] })),
              borderColor: CHART_COLORS.accent, pointRadius: 0,
            },
            {
              type: 'line', label: window.t('f.r7.lbl_curve_quad', { r2: quad.r2.toFixed(3) }),
              data: r.curves.quadratic.x.map((v, i) => ({ x: v, y: r.curves.quadratic.y[i] })),
              borderColor: CHART_COLORS.warn, pointRadius: 0, borderDash: [6, 6],
            },
          ],
        },
        options: { scales: { x: { title: { display: true, text: 'x' } }, y: { title: { display: true, text: 'y' } } } },
      });
      renderChart('chart-residuals', {
        type: 'line',
        data: {
          datasets: [
            {
              type: 'scatter', label: window.t('f.r7.ax_res'),
              data: r.residuals.x.map((v, i) => ({ x: v, y: r.residuals.y[i] })),
              borderColor: CHART_COLORS.accent, backgroundColor: CHART_COLORS.accent, pointRadius: 4,
            }, refLine(r.scatter.x[0], r.scatter.x.at(-1), 0, 'residual = 0'),
          ],
        },
        options: { scales: { x: { type: 'linear', title: { display: true, text: 'x' } }, y: { title: { display: true, text: window.t('f.r7.ax_res') } } } },
      });
      const coefs = (m) =>
        m.coefficients
          .map((c, i) => (i ? `${c >= 0 ? '+' : ''}${c.toFixed(4)}x${i > 1 ? '^' + i : ''}` : `${c.toFixed(4)}`))
          .join(' ');
      const metrics = (m) => window.t('f.r7.metrics', {
        r2: m.r2.toFixed(4), r2a: m.r2_adjusted.toFixed(4),
        s: m.se.toFixed(4), p: m.press.toFixed(3),
      });
      this.results.regression.formula =
        window.t('f.r7.lin', { c: coefs(lin) }) + ' · ' + metrics(lin)
        + window.t('f.r7.quad', { c: coefs(quad) }) + ' · ' + metrics(quad)
        + window.t('f.r7.best', { m: r.best === 'linear' ? window.t('f.r7.best_lin') : window.t('f.r7.best_quad') })
        + (r.prediction
          ? '\n' + window.t('f.r7.pred', {
            x0: r.prediction.x0, l: r.prediction.linear.toFixed(3), q: r.prediction.quadratic.toFixed(3),
          })
          : '')
        + '\n' + window.t('f.r7.punch');
    });
  },

  async runConfidence() {
    if (!this.results.confidence) {
      const guessOk = await this.setGuess('confidence',
        window.t('r8.q', { total: this.confidence.total, hits: this.confidence.hits }));
      if (!guessOk) return;
    }
    await this.run('confidence', async () => {
      const r = await postJSON('confidence', {
        hits: this.confidence.hits, total: this.confidence.total,
        confidence: this.confidence.level,
      });
      this.results.confidence = { ...this.results.confidence, ...r };
      await domTick();
      const ic = r.interval, cov = r.coverage;
      renderChart('chart-confidence', {
        type: 'line',
        data: {
          datasets: [
            {
              label: window.t('f.c8.lbl_low'),
              data: cov.intervals_sample.map((v, i) => ({ x: i + 1, y: v.lower * 100 })),
              borderColor: CHART_COLORS.lavender, pointRadius: 0,
            },
            {
              label: window.t('f.c8.lbl_up'),
              data: cov.intervals_sample.map((v, i) => ({ x: i + 1, y: v.upper * 100 })),
              borderColor: CHART_COLORS.accent, pointRadius: 0,
            },
            refLine(1, cov.intervals_sample.length, cov.true_p * 100, window.t('f.c8.lbl_p')),
          ],
        },
        options: {
          scales: {
            x: { type: 'linear', title: { display: true, text: window.t('f.c8.ax_x') } },
            y: { title: { display: true, text: window.t('f.c8.ax_y') } },
          },
        },
      });
      this.results.confidence.formula =
        `${window.t('f.c8.phat', { h: this.confidence.hits, t: this.confidence.total, p: ic.p_hat.toFixed(3) })}\n`
        + `${window.t('f.c8.se', { se: ic.se.toFixed(4) })}\n`
        + `${window.t('f.c8.ci', { lvl: Math.round(ic.confidence * 100) })} =\n`
        + ` <code>p̂ ± z·EE = ${ic.p_hat.toFixed(3)} ± ${ic.z}·${ic.se.toFixed(4)}</code>\n`
        + ` → <code>[${(ic.lower * 100).toFixed(2)}%, ${(ic.upper * 100).toFixed(2)}%]</code>`
        + window.t('f.c8.margin', { m: this.pct(ic.margin) }) + '\n\n'
        + `${window.t('f.c8.sim', {
          a: cov.replicates.toLocaleString(tLocale()), n: cov.n,
          p: (cov.coverage * 100).toFixed(1),
        })}\n`
        + window.t('f.c8.interp', { l: Math.round(ic.confidence * 100) });
    });
  },
});

window.PRESET_DATA = {
  frequencies:
    '75,37,89,95,67,60,55,43,32,39,40,58,69,74,80,96,92,40,35,39,51,73,70,77,86,84' +
    ',80,75,77,42,49,52,68,64,60,76,74,73,71,87,98,91,46,62,60,42,50,76,70,64',
  regressionX: '0,1,2,3,4,5,6,7,8,9',
  regressionY: '9.1,7.3,3.2,4.6,4.8,2.9,5.7,7.1,8.8,10.2',
};
