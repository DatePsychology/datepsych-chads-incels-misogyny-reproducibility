#!/usr/bin/env python3
"""Offline numerical / packaging verification for the companion reproductions."""
from pathlib import Path
from math import isclose
from PIL import Image

from reproduce_chads_incels_figures import (
    HERE, load_numbers, load_categories, fisher_ci, correlation_p, d_to_t_p, compute,
)


def check():
    v=load_numbers()
    rows=load_categories()
    assert len(rows)==13
    assert [int(x['item']) for x in rows if x['reviewer_category']=='romantic_experience_distress'] == [1,3,10,11,13]

    assert isclose(v['self_incel_ems_mean']-v['nonself_ems_mean'],16.06,abs_tol=1e-9)
    assert isclose(v['operational_exclusive_ems_mean']-v['operational_comparison_ems_mean'],5.42,abs_tol=1e-9)
    assert isclose((16.06*5)/13,6.176923076923077,abs_tol=1e-10)
    assert isclose((5.42*5)/13,2.0846153846153843,abs_tol=1e-10)
    assert isclose(16.06/5,3.212,abs_tol=1e-10)
    assert isclose(5.42/5,1.084,abs_tol=1e-10)

    lo,hi=fisher_ci(-.29,348)
    assert isclose(lo,-.383,abs_tol=.002) and isclose(hi,-.191,abs_tol=.002)
    lo,hi=fisher_ci(-.12,230)
    assert isclose(lo,-.246,abs_tol=.002) and isclose(hi,.010,abs_tol=.002)
    lo,hi=fisher_ci(-.12,244)
    assert isclose(lo,-.242,abs_tol=.002) and isclose(hi,.006,abs_tol=.002)
    assert isclose(correlation_p(-.12,230),.0693,abs_tol=.0003)
    _,p=d_to_t_p(1.35,45,35)
    assert isclose(p,6.09e-8,rel_tol=.03)

    results,report=compute(v)
    assert len(results)>=20 and 'HYPOTHETICAL' in report and 'NOT published' in report
    for stem in ['01_reported_results','02_correlation_intervals',
                 '03_ems_item_content','04_hypothetical_sensitivity','05_original_plot_comparison']:
        img=HERE/f'figure_{stem}.png'
        assert img.is_file(),f'Missing figure: {img}'
        with Image.open(img) as im:
            im.verify()
    for f in ['reconstruction_results.csv','reconstruction_results.txt','published_summary_inputs.csv','ems_item_coding.csv']:
        assert (HERE/f).is_file(),f'Missing: {f}'
    for j in range(1,4):
        assert (HERE/'source_plots'/f'alexander_figure_{j}.jpeg').is_file()
    print('PASS: transcribed inputs, quantitative formulas, declared EMS groups, five PNGs, and output files.')


if __name__=='__main__':
    check()
