# How each round works

The game: you guess first, then the app shows the exact math and a Monte Carlo
simulation. This file explains what each round is about, the formula behind
it, and what the simulation actually does.

## 1. Birthday paradox [combinatorics / counting rules]

Question: in a group of n people, what is P(at least two share a birthday)?

-   Formula: P = 1 − ∏(365 − i)/365 for i = 0…n−1. It is easier to compute the
    complement (all different) and subtract from 1.
-   Why it surprises: the intuition counts comparisons against *you* (n−1),
    but the event is *any* of the C(n,2) pairs colliding. That grows ~n², so
    with n = 23 there are already 253 pairs and P ≈ 50.7%.
-   Simulation: groups of n random birthdays in 0-364; a group "hits" if any
    two coincide. The convergence chart is the classic LLN flipbook.

## 2. Monty Hall [conditional probability]

Question: stay or switch after the host opens an empty door?

-   Key fact: the host's action is informative. He always opens a *goat*
    door, so he concentrates the remaining 2/3 on the other closed door.
-   P(win | stay) = 1/3;  P(win | switch) = 2/3.
-   Simulation: random prize, random first pick; staying wins iff the first
    pick was right. Thousands of runs make both curves converge to 1/3 and
    2/3.

## 3. Medical test with false positives [Bayes' theorem]

Question: you test positive; what is P(sick | positive)?

-   Formula: P(E|+) = P(+|E)·P(E) / [P(+|E)·P(E) + P(+|S)·P(S)].
-   The classic case (prevalence 1%, sensitivity 99%, false positives 1%) is
    symmetric and gives exactly 50%: one true positive per false positive,
    because there are 99 healthy people for each sick one.
-   Simulation: populations of 10,000 colored point by point (sick+,
    sick−, healthy+ (false), healthy−). Seeing that the sky points outnumber
    the red ones *is* Bayes.

## 4. Gambler's fallacy [independence]

Question: after 5 heads in a row, what is P(heads) on the next flip?

-   Answer: still 50%. Flips are independent; the coin has no memory.
-   The fallacy confuses the long-run average (which does even out, Law of
    Large Numbers) with the next single trial (which does not care).
-   Simulation: plays real flips until a streak of 5 heads appears, then
    flips once more and records it. Repeat thousands of times; the running
    mean sticks to 50%.

## 5. Central Limit Theorem [sampling distributions]

Question: sample many times, average each sample; what shape do the means take?

-   Statement: for sample size n, X̄ ≈ N(μ, σ/√n) regardless of the
    population shape (finite variance conditions apply).
-   Inputs: population (uniform U[0,10): μ=5, σ=10/√12; exponential λ=1:
    μ=1, σ=1; bimodal 0/10: μ=5, σ=5).
-   Simulation: builds the histogram of sample means and overlays the exact
    normal density. With n=1 the histogram is the population; raise n and
    watch the bell appear and narrow at rate 1/√n.

## 6. Frequency tables [descriptive statistics, grouped data]

Question: turn a raw list of numbers into a grouped frequency distribution.

-   Sturges' rule: k = 1 + 3.322·log₁₀(n) classes, amplitude A = range/k.
-   Table: class intervals with mark xᵢ, absolute f, cumulative F, relative
    fr, percent.
-   Grouped stats use the marks: mean = Σf·xᵢ/n; median interpolates inside
    the class that accumulates n/2; mode falls in the modal class.
-   The ungrouped mean/median are shown as reference: grouping costs a little
    accuracy. Inconsistencies between them are expected and pedagogical.

## 7. Linear vs. quadratic regression [least squares + model selection]

Question: which model fits (and *predicts*) better?

-   Fit both by least squares. Diagnostics: R² (fit share), adjusted R²
    (penalizes extra parameters), residual standard error s = √(SSE/(n−p)),
    and PRESS = Σ(eᵢ / (1 − hᵢᵢ))² (out-of-sample prediction error,
    one leave-one-out at a time via the hat-matrix diagonal hᵢᵢ).
-   The quadratic almost always wins on R²; PRESS decides if it genuinely
    predicts better or is just overfitting. The app picks by PRESS.
-   Output: scatter with both curves, residuals of the best model, and a
    prediction at x₀ from both models.

## 8. Confidence interval for a proportion [statistical inference]

Question: 300 of 400 voters approve; what is the real support p?

-   Wald interval: p̂ ± z·√(p̂(1−p̂)/n) with z = 1.645/1.96/2.576 for
    90/95/99%. For 300/400 at 99%: [69.42%, 80.58%].
-   The opinion in the round is biased on purpose: guessing 75% feels right
    because p̂ = 75%, but the sample is not the population; the honest
    answer is the whole interval plus its margin.
-   Interpretation: "99% confidence" is a property of the *method*, not of
    one interval: in repeated sampling, the interval traps the true p about
    99% of the time.
-   Simulation: builds an interval from thousands of fresh surveys
    (p = p̂) and measures the coverage: the share that actually contains
    the true p. It converges to the nominal level.
