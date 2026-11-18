# Methods, provenance, and limits

## Published numbers versus reconstructions

`published_summary_inputs.csv` is a manual transcription of rounded values from
Alexander (2023), and Selmer et al. (2023). The script NEVER pretends to recover raw
respondent responses. Numbers printed as *reported* are transcribed; numbers printed as
*reconstructed* derive from openly documented equations. A reconstructed p value for a
rounded correlation need not equal a p value computed from the original unrounded value.

## Correlation intervals

For a Pearson correlation `r`, the approximate 95% Fisher-z confidence interval is:

`z = atanh(r); SE(z) = 1/sqrt(n-3); CI(r) = tanh(z +/- 1.95996398454 * SE(z))`.

For the full-sample correlation, `n=348`. For the subgroup, the original article reports
`r=-.12` and `p=.069` but does not document the exact subgroup `n`. We use **n=230 as a
clearly stated scenario** and provide a second sensitivity scenario with `n=244`, not a
verified bound on possible group sizes. Full and subgroup data overlap, so comparing
confidence interval overlap is NOT a test of whether the two correlations differ.

## Group sizes and Figure 3

Alexander reports self-identified incels `45`, operational incels `104`, and a total of `348`.
The overlap of the categories is not published. If all 45 self-identified incels were also
operational incels, the union would be 104 and the neither-category sample size would be
`244`. If overlap were 31, the union would be 118 and the neither-category size would be
`230`. These are illustrative cases. The Figure 3 calculation assumes `n1=45`, `n2=35`
and published `d=1.35` solely to show numerical consistency:
`t=d*sqrt(n1*n2/(n1+n2))`, with `df=n1+n2-2`; a two-sided Student t tail is used.
This does NOT prove which participants were compared, that equal variances hold, or that the
original analysis used a Student t test.

The `figure_05_original_plot_comparison.png` graphic is assembled from three original
plot images in a saved copy of Alexander's web article (credited). Figures 1 and 3 show
closely matching incel distributions while Figure 2 displays a different distribution;
this supports a **reporting inconsistency** but does not identify its cause. Different
vertical scales are retained from the original panels. No observations are digitized.

## EMS items and scenarios

`ems_item_coding.csv` preserves independent, single-reviewer qualitative item categories.
No factor analysis, blinded second-coder reliability, or item-level inferential tests were
performed. Summed scores are theoretical 13 items rated from 1 to 7, range 13–91.

The self-identified-incel mean difference is `49.45 - 33.39 = 16.06` and the
operational-only mean difference `37.59 - 32.17 = 5.42`. The five hypothesized
nonhostile/distress items have possible total-score range 5–35, maximum difference 30.
Under the *purely hypothetical* equal-per-item contribution scenario, they account
for `(5/13)*gap`. To account for the *entire* gap assuming no difference on the
other eight items, the five would need `(gap/5)` points of between-group difference
per item. These are mathematical examples **not estimates** of the true item contributions.
Subtracting them does not produce corrected Cohen's d values because the covariance and
variance change when items are dropped.

Selmer's adjusted incel coefficient and SE are rounded (`-0.0002`, `.026`) on a
linearly rescaled 0–1 EMS. Assuming this rescaling spans the theoretical 13–91
score range, multiply coefficient limits by 78 to express approximate raw-point
limits. The adjustment set includes demographics and dark personality traits,
and the result is not directly comparable to Alexander's unadjusted comparison.

## Manuscripts / supplementary materials

- Alexander (2023), *Are Chads more misogynistic?*, https://datepsychology.com/are-chads-more-misogynistic/
- Selmer, Lindekilde & Petersen (2023), *Sociosexuality and incel ideology*, https://doi.org/10.31234/osf.io/wsvq8 — supplied manuscript version `Article v.2`, Table 1, Appendix A–E.
- Original SOI-R: https://www.larspenke.eu/research/soi-r.html
- Grunau et al. (2022): https://doi.org/10.1016/j.paid.2022.111860
- Bosson et al. (2022): https://doi.org/10.1177/01461672211009726
- Zhang et al. (2025): https://doi.org/10.1111/sjop.13062
- Walldén et al. (2026): https://doi.org/10.1016/j.paid.2025.113610

No original PDF/DOCX files or whole copies of third-party articles are redistributed.
