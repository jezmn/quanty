
window.probRounds = () => ({
  async runBirthday() {
    const t = this.results.birthday;
    if (!t || t.people !== this.birthday.people) {
      const guessOk = await this.setGuess('birthday',
        window.t('r1.q', { n: this.birthday.people }));
      if (!guessOk) return;
    }
    await this.run('birthday', async () => {
      const r = await postJSON('birthday', { people: this.birthday.people, trials: this.birthday.trials });
      this.results.birthday = { ...this.results.birthday, ...r };
      await domTick();
      renderChart('chart-birthday', {
        type: 'line',
        data: {
          datasets: [{
            label: window.t('f.b1.lbl_theory'),
            data: r.theoretical_curve.map(p => ({ x: p.n, y: p.p * 100 })),
            borderColor: CHART_COLORS.accent, pointRadius: 0, tension: 0.2,
          }],
        },
        options: {
          scales: {
            x: { type: 'linear', title: { display: true, text: window.t('f.b1.ax_x') } },
            y: { title: { display: true, text: window.t('f.b1.ax_y') } },
          },
          plugins: { tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${c.parsed.y.toFixed(2)}%` } } },
        },
      });
      renderChart('chart-birthday-conv', {
        type: 'line',
        data: {
          datasets: [{
            label: window.t('f.b1.lbl_sim'),
            data: r.convergence.map(p => ({ x: p.trial, y: p.estimate * 100 })),
            borderColor: CHART_COLORS.lavender, pointRadius: 0,
          }],
        },
        options: {
          scales: {
            x: { type: 'linear', title: { display: true, text: window.t('f.b1.ax_x_sim') } },
            y: { title: { display: true, text: window.t('f.b1.ax_y') } },
          },
          plugins: { tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${c.parsed.y.toFixed(2)}%` } } },
        },
      });
      this.results.birthday.formula =
        `<code>${window.t('f.b1.head')} =\n` +
        `        1 − (365/365)(364/365)…((365−${this.birthday.people}+1)/365) = ${this.pct(r.theoretical)}</code>\n\n` +
        `${window.t('f.b1.sim', {
          a: r.groups_shared.toLocaleString(tLocale()), b: r.groups_total.toLocaleString(tLocale()),
          c: this.pct(r.simulated),
        })}\n` +
        ` ${window.t('f.b1.diff', { d: (Math.abs(r.theoretical - r.simulated) * 100).toFixed(2) })}\n` +
        `${window.t('f.b1.lln')}`;
    });
  },

  async runMonty() {
    await this.run('monty', async () => {
      const r = await postJSON('monty-hall', { trials: this.monty.trials });
      this.results.monty = r;
      await domTick();
      const last = r.convergence.at(-1).trial;
      renderChart('chart-monty', {
        type: 'line',
        data: {
          datasets: [
            {
              label: window.t('f.m2.lbl_stay'),
              data: r.convergence.map(p => ({ x: p.trial, y: p.stay * 100 })),
              borderColor: CHART_COLORS.lavender, pointRadius: 0,
            },
            {
              label: window.t('f.m2.lbl_switch'),
              data: r.convergence.map(p => ({ x: p.trial, y: p.switch * 100 })),
              borderColor: CHART_COLORS.accent, pointRadius: 0,
            },
            refLine(1, last, 33.33, '1/3'),
            refLine(1, last, 66.67, '2/3'),
          ],
        },
        options: {
          scales: {
            x: { type: 'linear', title: { display: true, text: window.t('f.m2.ax_x') } },
            y: { title: { display: true, text: window.t('f.m2.ax_y') } },
          },
        },
      });
      this.results.monty.formula =
        `${window.t('f.m2.t1')}\n`
        + `${window.t('f.m2.t2')}\n`
        + `${window.t('f.m2.t3')}\n\n`
        + window.t('f.m2.sim', {
          a: this.monty.trials.toLocaleString(tLocale()),
          s: this.pct(r.simulated.stay), w: this.pct(r.simulated.switch),
        });
    });
  },

  async runBayes() {
    if (!this.results.bayes) {
      const guessOk = await this.setGuess('bayes', window.t('r3.q'));
      if (!guessOk) return;
    }
    await this.run('bayes', async () => {
      const r = await postJSON('bayes', this.bayes);
      this.results.bayes = { ...this.results.bayes, ...r };
      await domTick();
      this.drawBayesGrid(r.population);
      renderChart('chart-bayes', {
        type: 'line',
        data: {
          datasets: [{
            label: window.t('f.b3.lbl'),
            data: r.convergence.map(p => ({ x: p.trial, y: p.estimate * 100 })),
            borderColor: CHART_COLORS.accent, pointRadius: 0,
          }],
        },
        options: {
          scales: {
            x: { type: 'linear', title: { display: true, text: window.t('f.b3.ax_x') } },
            y: { title: { display: true, text: window.t('f.b3.ax_y') } },
          },
        },
      });
      const p = this.bayes;
      this.results.bayes.formula =
        `${window.t('f.b3.formula')}\n`
        + `             = <code>${p.sensitivity}·${p.prevalence} /\n`
        + `             (${p.sensitivity}·${p.prevalence} + ${p.false_positive_rate}·${(1 - p.prevalence).toFixed(2)})\n`
        + `             = ${this.pct(r.theoretical)}</code>\n\n`
        + window.t('f.b3.sim', {
          a: r.population.sick_positive.toLocaleString(tLocale()),
          b: r.population.healthy_positive.toLocaleString(tLocale()),
        }) + '\n'
        + window.t('f.b3.key');
    });
  },

  drawBayesGrid(pop) {
    const grid = document.getElementById('bayes-grid');
    grid.innerHTML = '';
    const total = pop.sick_positive + pop.sick_negative + pop.healthy_positive + pop.healthy_negative;
    const scale = Math.max(1, Math.ceil(total / 1000));
    const add = (count, className) => {
      for (let i = 0; i < Math.floor(count / scale); i++) {
        const el = document.createElement('span');
        el.className = className;
        grid.appendChild(el);
      }
    };
    add(pop.sick_positive, 'bg-rose-500');
    add(pop.sick_negative, 'bg-amber-400');
    add(pop.healthy_positive, 'bg-sky-500');
    add(pop.healthy_negative, 'bg-slate-600');
  },

  async runGambler() {
    if (!this.results.gambler) {
      const guessOk = await this.setGuess('gambler', window.t('r4.q'));
      if (!guessOk) return;
    }
    await this.run('gambler', async () => {
      const r = await postJSON('gambler', { streaks: this.gambler.streaks });
      this.results.gambler = { ...this.results.gambler, ...r };
      await domTick();
      renderChart('chart-gambler', {
        type: 'line',
        data: {
          datasets: [
            {
              label: window.t('stats.simulated'),
              data: r.convergence.map(p => ({ x: p.trial, y: p.estimate * 100 })),
              borderColor: CHART_COLORS.accent, pointRadius: 0,
            },
            refLine(1, Math.max(r.convergence.length, 2), 50, window.t('f.g4.ref')),
          ],
        },
        options: { scales: { x: { type: 'linear' }, y: { title: { display: true, text: window.t('f.g4.ax_y') } } } },
      });
      this.results.gambler.formula =
        `${window.t('f.g4.indep')}\n\n`
        + `${window.t('f.g4.sim', {
          a: r.streaks_found.toLocaleString(tLocale()), b: r.flips_used.toLocaleString(tLocale()),
          c: this.pct(r.simulated),
        })}\n`
        + window.t('f.g4.myth');
    });
  },

  async runClt() {
    await this.run('clt', async () => {
      const r = await postJSON('clt', this.clt);
      this.results.clt = r;
      await domTick();
      renderChart('chart-clt', {
        type: 'bar',
        data: {
          labels: r.histogram.centers.map(v => v.toFixed(2)),
          datasets: [
            {
              type: 'bar', label: window.t('f.c5.lbl_means'), data: r.histogram.density,
              backgroundColor: 'rgba(137, 180, 250, 0.30)', borderColor: CHART_COLORS.accent, borderWidth: 1,
            },
            {
              type: 'line', label: window.t('f.c5.lbl_normal'), data: r.histogram.normal,
              borderColor: CHART_COLORS.warn, pointRadius: 0, tension: 0.3,
            },
          ],
        },
        options: { scales: { y: { title: { display: true, text: window.t('f.c5.ax_y') } } } },
      });
      this.results.clt.formula =
        `${window.t('f.c5.pop', { d: this.clt.distribution })} ·\n`
        + `${window.t('f.c5.params', { mu: r.theoretical.mu.toFixed(3), sigma: r.theoretical.sigma.toFixed(3) })}\n`
        + `${window.t('f.c5.head')}\n`
        + window.t('f.c5.se', { th: r.theoretical.se.toFixed(3), em: r.empirical.std.toFixed(3) }) + '\n\n'
        + window.t('f.c5.gauss', { n: this.clt.sample_size }) + '\n'
        + window.t('f.c5.tail');
    });
  },
});
