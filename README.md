# Chads, Incels, and Misogyny — Reproducibility Materials

Code, transcribed published statistics, numerical reconstructions, item-content coding, and companion figures for the [methodological review](https://datepsych.substack.com/p/chads-incels-and-misogyny-what-the) **“Chads, Incels, and Misogyny”**

**Scope:** This is a reproducibility package for the review's *published-summary calculations, qualitative item classification, and figures*. It is **not** a replication of Alexander's (2023) or Selmer et al.'s (2023) participant-level statistical analyses. Neither study's original respondent-level dataset was available for this review. No individual observations have been fabricated, imputed, or reverse-engineered.

## Contents

| File | Purpose |
|---|---|
| `reproduce_chads_incels_figures.py` | Recomputes numerical reconstructions, exports results, and generates all five figures. |
| `published_summary_inputs.csv` | Transcription of study-reported means, effect sizes, correlations, p-values, sample sizes, and regression summary values, with provenance. |
| `ems_item_coding.csv` | Independent one-reviewer classification of the original 13 EMS item contents, **not** a validated scoring system. |
| `reconstruction_results.csv` | Machine-readable derived values, identifying hypothetical assumptions. |
| `reconstruction_results.txt` | Human-readable calculation results and warnings. |
| `figure_01_reported_results.png` | Image summary of Alexander's reported means, effect sizes, and correlations. |
| `figure_02_correlation_intervals.png` | Reconstructed Pearson-correlation confidence intervals, with the subgroup `n` assumption disclosed. |
| `figure_03_ems_item_content.png` | The independent, qualitative 13-item EMS content map. |
| `figure_04_hypothetical_sensitivity.png` | Two explicitly **hypothetical** allocations of EMS group-mean differences. |
| `figure_05_original_plot_comparison.png` | Alexander's original Figures 1, 3, and 2 reordered for a critical comparison, without digitizing individual observations. |
| `source_plots/` | The three underlying figures from Alexander's original article and an attribution note. Included for critical comparison; third-party rights remain with their owner. |
| `NOTES_METHODS.md` | Sources, formulas, provenance, unverified assumptions, and limits. |
| `verify_reconstructions.py` | Sanity and regression tests for inputs, formulas, outputs, and chart generation. |
| `optional_item_level/` | Templates and a *conditional* item-level reanalysis script for use **only if** de-identified author data later become accessible with permission. |
| `requirements.txt` | Python dependencies tested for this package. |

**Mapping to the Substack article:** The article's unnumbered results-summary image corresponds to `figure_01`; its **Figure 1** is `figure_02`; its **Figure 2** is `figure_03`; its unnumbered sensitivity table-image corresponds to `figure_04`; and its **Figure 3** corresponds to `figure_05`. The script regenerates the *same documented numerical content* and substantively equivalent figures; minor typography/layout differences from the pasted Substack image exports are not evidence of changed estimates.

## Reproduce calculations and figures

Python **3.10 or newer** is recommended. In the repository directory:

```bash
python -m pip install -r requirements.txt
python reproduce_chads_incels_figures.py
python verify_reconstructions.py
```

This regenerates `reconstruction_results.csv`, `reconstruction_results.txt`, and all five `figure_*.png` files in place. **Running it overwrites those files**, so use a working copy if preserving the checked-in outputs matters. No network access, downloaded datasets, user credentials, or API keys are required.

For the quantitative audit, use the CSV and TXT output together with `NOTES_METHODS.md`; a chart alone is not sufficient to reproduce the reasoning.

## What is reproduced — and what is not

**Reproducible directly from cited summaries:**

- Group mean differences (`16.06` and `5.42` EMS points) and per-item mean descriptions.
- Fisher-z approximate 95% intervals around the published rounded correlations.
- Illustration of how alternative **assumed** non-incel sample sizes of 230 and 244 affect the interval and the p value computed from rounded `r`.
- A conventional equal-variance t-test *compatibility check* for Alexander's reported Figure 3 comparison, using `d=1.35`, **hypothetical** group sizes 45 and 35, not the authors' raw data.
- Two **hypothetical** allocations of the five disputed EMS items' contributions to group differences.
- An approximate 95% interval for Selmer's *adjusted* incel coefficient using a rounded coefficient/SE and a clearly stated 0–1 rescaling assumption.
- The reviewer's *declared* 4/4/5 item-content categories and the assembly of the original plot comparison.

**Not reproducible without participant-level data or the original software/code:**

- The original authors' correlations, group comparisons, or regressions from individual observations.
- The actual overlap between Alexander's two incel categories and the sample size remaining after exclusions.
- The contribution of each EMS item to either published effect or any **corrected** effect size.
- Psychometric factor structure, response-quality diagnostics, mediation, measurement invariance, causal effects, or the exact Bayesian prior and Bayes factor.
- Original violin density estimates: the comparison assembles attributed source plots but cannot recreate them from unknown raw observations.

The numbers and item classifications in this repository should not be represented as independently validated original-study results. In particular, dividing a scale into hostility, grievance, and distress items is a **qualitative methodological proposal**, not proof that any of the groups' mean differences result from the proposed items.

## Original sources

- [Alexander (2023), “Are Chads more misogynistic?”](https://datepsychology.com/are-chads-more-misogynistic/)
- [Selmer, Lindekilde & Petersen (2023), “Sociosexuality and incel ideology: Does a mismatch between sexual practice and sexual intentions predict extreme misogynist views?”](https://doi.org/10.31234/osf.io/wsvq8) — manuscript version `Article v.2`, especially Table 1 and Appendices A–E.
- [Penke & Asendorpf (2008), original SOI-R documentation](https://www.larspenke.eu/research/soi-r.html)
- [Grunau et al. (2022)](https://doi.org/10.1016/j.paid.2022.111860)
- [Bosson et al. (2022)](https://doi.org/10.1177/01461672211009726)
- [Zhang et al. (2025)](https://doi.org/10.1111/sjop.13062)
- [Walldén, Gunst & Antfolk (2026)](https://doi.org/10.1016/j.paid.2025.113610)

Only summary numbers and short paraphrases are transcribed from research sources. The full manuscripts and the study questionnaires are **not** redistributed here. Three original plot images are included solely as attributed critical comparison material; see `source_plots/ATTRIBUTION.md` for third-party-rights limitations.

## License and version

The original scripts and documentation are offered under the MIT license. **The third-party source plots do not come under that license.** No respondent-level data are included. All reconstructed results use the article version finalized in **November 2026**.
