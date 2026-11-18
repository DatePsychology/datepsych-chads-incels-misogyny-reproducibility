#!/usr/bin/env python3
"""Reconstruct published-summary calculations and five companion visuals.

Run from any directory; inputs and outputs are relative to this file.
No participant-level data are used or fabricated.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path
from statistics import NormalDist

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t as student_t
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SOURCE = 'Alexander (2023), Are Chads more misogynistic?'
BLUE = '#173D57'
SLATE = '#607A8D'
LIGHT = '#EFF4F7'
INK = '#1B2F3A'
GOLD = '#B58A45'
RED = '#AE6658'
SEA = '#5E8A8C'


def load_numbers() -> dict[str, float]:
    with (HERE / 'published_summary_inputs.csv').open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    data = {row['key']: float(row['value']) for row in rows}
    assert len(data) == len(rows), 'Duplicate source-summary keys'
    return data


def load_categories() -> list[dict[str, str]]:
    with (HERE / 'ems_item_coding.csv').open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    assert [int(row['item']) for row in rows] == list(range(1, 14))
    cats = [r['reviewer_category'] for r in rows]
    assert cats.count('direct_hostility') == 4
    assert cats.count('negative_generalizations') == 4
    assert cats.count('romantic_experience_distress') == 5
    return rows


def fisher_ci(r: float, n: int) -> tuple[float, float]:
    if n <= 3 or not (-1 < r < 1):
        raise ValueError('Fisher-z CI requires |r|<1 and n>3')
    z = math.atanh(r)
    delta = NormalDist().inv_cdf(.975) / math.sqrt(n - 3)
    return math.tanh(z - delta), math.tanh(z + delta)


def correlation_p(r: float, n: int) -> float:
    statistic = r * math.sqrt((n - 2) / (1 - r**2))
    return float(2 * student_t.sf(abs(statistic), n - 2))


def d_to_t_p(d: float, n1: int, n2: int) -> tuple[float, float]:
    """Illustrative equal-variance Student t reconstruction, NOT a source-data reanalysis."""
    t = d * math.sqrt(n1 * n2 / (n1 + n2))
    return t, float(2 * student_t.sf(abs(t), n1 + n2 - 2))


def compute(v: dict[str, float]) -> tuple[list[dict[str, str]], str]:
    full_n = int(v['alexander_n'])
    r_full = v['full_chad_ems_r']
    r_sub = v['subset_chad_ems_r']
    ci_full = fisher_ci(r_full, full_n)
    ci_230, ci_244 = fisher_ci(r_sub, 230), fisher_ci(r_sub, 244)
    self_gap = v['self_incel_ems_mean'] - v['nonself_ems_mean']
    operational_gap = v['operational_exclusive_ems_mean'] - v['operational_comparison_ems_mean']
    figure3_t, figure3_p = d_to_t_p(v['figure3_d'],45,35)
    ci_selmer = (v['selmer_incel_adjusted_b']-NormalDist().inv_cdf(.975)*v['selmer_incel_adjusted_se'],
                 v['selmer_incel_adjusted_b']+NormalDist().inv_cdf(.975)*v['selmer_incel_adjusted_se'])
    derived = [
        ('full_r_fisher_ci_lower',ci_full[0],'reconstructed Fisher-z, n=348'),
        ('full_r_fisher_ci_upper',ci_full[1],'reconstructed Fisher-z, n=348'),
        ('full_r_p_from_rounded_r',correlation_p(r_full,full_n),'reconstructed; differs from published p because rounded r'),
        ('subset_r_fisher_ci_lower_n230',ci_230[0],'hypothetical n=230'),
        ('subset_r_fisher_ci_upper_n230',ci_230[1],'hypothetical n=230'),
        ('subset_r_fisher_ci_lower_n244',ci_244[0],'hypothetical n=244'),
        ('subset_r_fisher_ci_upper_n244',ci_244[1],'hypothetical n=244'),
        ('subset_r_p_from_rounded_r_n230',correlation_p(r_sub,230),'hypothetical n=230'),
        ('subset_r_p_from_rounded_r_n244',correlation_p(r_sub,244),'hypothetical n=244'),
        ('self_identified_ems_gap',self_gap,'published group means subtracted'),
        ('operational_exclusive_ems_gap',operational_gap,'published group means subtracted'),
        ('self_gap_equal_share_5_of_13',self_gap*5/13,'hypothetical equal item contributions'),
        ('operational_gap_equal_share_5_of_13',operational_gap*5/13,'hypothetical equal item contributions'),
        ('self_gap_remaining_8_of_13',self_gap*8/13,'hypothetical equal item contributions'),
        ('operational_gap_remaining_8_of_13',operational_gap*8/13,'hypothetical equal item contributions'),
        ('self_gap_per_distress_item_to_explain_all',self_gap/5,'hypothetical, other 8 items contribute 0'),
        ('operational_gap_per_distress_item_to_explain_all',operational_gap/5,'hypothetical, other 8 items contribute 0'),
        ('self_incel_ems_mean_per_item',v['self_incel_ems_mean']/13,'reported total divided by 13'),
        ('nonself_ems_mean_per_item',v['nonself_ems_mean']/13,'reported total divided by 13'),
        ('operational_ems_mean_per_item',v['operational_exclusive_ems_mean']/13,'reported total divided by 13'),
        ('operational_comparison_mean_per_item',v['operational_comparison_ems_mean']/13,'reported total divided by 13'),
        ('figure3_student_t_from_rounded_d_45_35',figure3_t,'illustrative t reconstruction; equal variances'),
        ('figure3_p_from_rounded_d_45_35',figure3_p,'illustrative two-sided Student t p'),
        ('selmer_adjusted_incel_ci_lower_0to1',ci_selmer[0],'from rounded b and SE; approximate'),
        ('selmer_adjusted_incel_ci_upper_0to1',ci_selmer[1],'from rounded b and SE; approximate'),
        ('selmer_adjusted_incel_ci_lower_raw_points',ci_selmer[0]*78,'assumes linear rescaling of total range 13–91'),
        ('selmer_adjusted_incel_ci_upper_raw_points',ci_selmer[1]*78,'assumes linear rescaling of total range 13–91'),
        ('no_incel_criterion_n_if_overlap_45',348-(45+104-45),'illustrative overlap assumption'),
        ('no_incel_criterion_n_if_overlap_31',348-(45+104-31),'illustrative overlap assumption'),
    ]
    rows=[{'calculation':k,'value':f'{val:.12g}','status_or_assumption':note} for k,val,note in derived]
    lines=[
        'Chads, Incels, and Misogyny — published-summary reconstruction',
        '='*63,
        'Source numbers are transcribed from the published materials, not generated by this script.',
        'The following are RECONSTRUCTIONS, HYPOTHETICAL EXAMPLES or rounding-based conversions.',
        '',
        f'Full sample: r={r_full:.2f}, n={full_n}; Fisher-z 95% CI [{ci_full[0]:.3f}, {ci_full[1]:.3f}]',
        f'  p from rounded r={correlation_p(r_full,full_n):.3g}, reported p={v["full_chad_ems_p"]:.3g} (not an exact reproduction)',
        f'After excluding both incel categories: r={r_sub:.2f}; exact n NOT published',
        f'  Assumed n=230: 95% CI [{ci_230[0]:.3f}, {ci_230[1]:.3f}], p={correlation_p(r_sub,230):.4f}',
        f'  Assumed n=244: 95% CI [{ci_244[0]:.3f}, {ci_244[1]:.3f}], p={correlation_p(r_sub,244):.4f}',
        '',
        f'Self-identified-incel gap: {self_gap:.2f} total EMS points (reported d={v["self_incel_d"]:.2f}).',
        f'Operational-incel-exclusive gap: {operational_gap:.2f} total EMS points (reported d={v["operational_exclusive_d"]:.2f}).',
        f'Under equal-per-item contribution, five putative distress items would account for {self_gap*5/13:.2f} and {operational_gap*5/13:.2f} points.',
        f'To explain the entire gap if other eight items contribute zero, each of the five would need {self_gap/5:.2f} and {operational_gap/5:.2f} points.',
        'These are not observed item effects; reduced-score effect sizes cannot be computed.',
        '',
        f'Figure 3 illustrative d={v["figure3_d"]:.2f}, n1=45, n2=35: t={figure3_t:.3f}, p={figure3_p:.3g}; published p={v["figure3_p"]:.3g}.',
        'This is a compatibility check and does not establish the identity of the compared groups.',
        '',
        f'Selmer adjusted incel b={v["selmer_incel_adjusted_b"]}, rounded SE={v["selmer_incel_adjusted_se"]}; approximate 95% CI [{ci_selmer[0]:.3f},{ci_selmer[1]:.3f}] on 0–1 scale.',
        f'If 0–1 spans summed score 13–91, bounds correspond to [{ci_selmer[0]*78:.2f},{ci_selmer[1]*78:.2f}] original points.',
        '',
        'Qualitative EMS content categories are NOT factor scores, independently blind-coded labels or estimated effects.',
        'See NOTES_METHODS.md for assumptions, cautions and source links.',
    ]
    return rows, '\n'.join(lines)+'\n'


def style_axis(ax):
    for side in ('top','right','left'):
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color('#CED9E0')
    ax.tick_params(axis='both',colors='#526878')


def figure_01(v):
    entries=[
        ('Self-identified incels versus others',f'{v["self_incel_ems_mean"]:.2f} vs {v["nonself_ems_mean"]:.2f}   •   d = {v["self_incel_d"]:.2f}'),
        ('Operational incels after excluding self-identifiers',f'{v["operational_exclusive_ems_mean"]:.2f} vs {v["operational_comparison_ems_mean"]:.2f}   •   d = {v["operational_exclusive_d"]:.2f}'),
        ('Chad Scale vs EMS — full sample',f'r = {v["full_chad_ems_r"]:.2f}   •   p = {v["full_chad_ems_p"]:.2g}'),
        ('Chad Scale vs EMS — neither-incel subgroup',f'r = {v["subset_chad_ems_r"]:.2f}   •   p = {v["subset_chad_ems_p"]:.3f}'),
        ('Top 10% vs bottom 50% of Chad Scale after exclusions',f'd = {v["chad_top_vs_bottom_d"]:.2f}   •   p = {v["chad_top_vs_bottom_p"]:.3f}'),
    ]
    fig,ax=plt.subplots(figsize=(13,6.0),dpi=160)
    fig.patch.set_facecolor('white');ax.set_xlim(0,1);ax.set_ylim(0,6.3);ax.axis('off')
    ax.text(.02,6.08,'Reported results from Alexander’s survey',weight='bold',color=BLUE,fontsize=20,va='center')
    ax.text(.02,5.68,'Published summary values; no participant-level replication performed',color=SLATE,fontsize=11)
    for i,(label,result) in enumerate(entries):
        y=4.75 - i*.86
        ax.add_patch(plt.Rectangle((.02,y-.35),.96,.72,facecolor=LIGHT if i%2==0 else 'white',edgecolor='#DFE7EC',lw=.6))
        ax.text(.045,y,label,color=INK,fontsize=12,ha='left',va='center')
        ax.text(.965,y,result,color=BLUE,fontsize=11.3,weight='bold',ha='right',va='center')
    ax.text(.02,.12,'EMS means are total summed scores; d, r and p are the author’s reported rounded values.',fontsize=10,color=SLATE)
    fig.savefig(HERE/'figure_01_reported_results.png',dpi=160,bbox_inches='tight',facecolor='white');plt.close(fig)


def figure_02(v):
    r1,r2=v['full_chad_ems_r'],v['subset_chad_ems_r']
    l1,u1=fisher_ci(r1,348)
    l2,u2=fisher_ci(r2,230)
    l3,u3=fisher_ci(r2,244)
    fig,ax=plt.subplots(figsize=(11,5.2),dpi=160)
    fig.patch.set_facecolor('white')
    ax.set_xlim(-.49,.10);ax.set_ylim(.1,2.95)
    ax.axvline(0,color='#879BA7',lw=1.5,ls='--')
    ys=[2,1]
    vals=[(r1,l1,u1),(r2,l2,u2)]
    for (r,lo,hi),y,col in zip(vals,ys,[BLUE,SEA]):
        ax.plot([lo,hi],[y,y],color=col,lw=5,solid_capstyle='round')
        ax.plot([lo,lo],[y-.13,y+.13],color=col,lw=2)
        ax.plot([hi,hi],[y-.13,y+.13],color=col,lw=2)
        ax.scatter([r],[y],s=170,c=col,zorder=3,edgecolors='white',linewidths=1.5)
        ax.text(.085,y,f'r={r:.2f}',color=col,ha='right',va='center',fontsize=11)
    ax.set_yticks(ys,['Full sample (n=348)','Neither-incel subgroup (assume n=230)'])
    ax.tick_params(axis='y',length=0,labelsize=11,pad=12)
    ax.set_xticks(np.arange(-.4,.11,.1))
    ax.set_xlabel('Pearson r: negative values mean higher Chad Scale scores coincide with lower EMS scores',labelpad=12,fontsize=10.5)
    ax.set_title('Approximate 95% Fisher-z confidence intervals',loc='left',fontsize=17,weight='bold',color=BLUE,pad=18)
    style_axis(ax)
    fig.text(.08,.04,f'Alternative assumed subgroup n=244: CI [{l3:.3f}, {u3:.3f}]. Neither subgroup n is verified.',fontsize=9.5,color=SLATE)
    fig.subplots_adjust(left=.30,right=.91,bottom=.23,top=.83)
    fig.savefig(HERE/'figure_02_correlation_intervals.png',dpi=160,facecolor='white');plt.close(fig)


def figure_03(items):
    labels={'direct_hostility':'Direct hostility', 'negative_generalizations':'Negative generalizations',
            'romantic_experience_distress':'Romantic experience / distress'}
    colors={'direct_hostility':RED, 'negative_generalizations':GOLD,'romantic_experience_distress':SEA}
    fig,ax=plt.subplots(figsize=(13.2,9.2),dpi=160)
    fig.patch.set_facecolor('white');ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(0,14.5)
    ax.text(.01,14.12,'Qualitative content map of the 13 EMS items',weight='bold',fontsize=18,color=BLUE)
    ax.text(.01,13.65,'One reviewer’s proposed coding; not validated factor scores or measured effect contributions',fontsize=10.5,color=SLATE)
    for idx,row in enumerate(items):
        y=12.78 - idx*.91
        cat=row['reviewer_category'];shade=colors[cat]
        ax.add_patch(plt.Rectangle((.01,y-.33),.98,.73,facecolor=LIGHT if idx%2==0 else 'white',edgecolor='#DCE5EB',lw=.6))
        ax.add_patch(plt.Rectangle((.013,y-.33),.01,.73,facecolor=shade,lw=0))
        ax.text(.045,y,f'{idx+1:02d}',fontsize=11.3,color=BLUE,weight='bold',va='center')
        ax.text(.11,y,row['short_paraphrase'],fontsize=11.1,color=INK,va='center')
        ax.text(.972,y,labels[cat],fontsize=10.1,color=shade,weight='bold',va='center',ha='right')
    ax.text(.01,.25,'Groups: 4 direct hostility • 4 negative generalizations • 5 romantic experience/distress',fontsize=11,color=SLATE)
    fig.savefig(HERE/'figure_03_ems_item_content.png',dpi=160,bbox_inches='tight',facecolor='white');plt.close(fig)


def figure_04(v):
    a = v['self_incel_ems_mean'] - v['nonself_ems_mean']
    b = v['operational_exclusive_ems_mean'] - v['operational_comparison_ems_mean']
    rows=[
        ('Reported EMS mean gap',f'{a:.2f} points',f'{b:.2f} points'),
        ('Hypothetical five-item share if all 13 items contribute equally',f'{a*5/13:.2f} points',f'{b*5/13:.2f} points'),
        ('Hypothetical remainder across the other eight items',f'{a*8/13:.2f} points',f'{b*8/13:.2f} points'),
        ('Mean difference per distress item needed to explain entire gap',f'{a/5:.2f} of 6',f'{b/5:.2f} of 6'),
    ]
    fig,ax=plt.subplots(figsize=(13.3,6.9),dpi=160)
    fig.patch.set_facecolor('white');ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(0,6)
    ax.text(.01,5.72,'Illustrative EMS sensitivity scenarios',weight='bold',fontsize=19,color=BLUE)
    ax.text(.01,5.31,'Purely hypothetical allocations; the five item-specific contributions are not observed',fontsize=10.5,color=SLATE)
    ax.text(.02,4.78,'SCENARIO',weight='bold',fontsize=10.5,color=SLATE)
    ax.text(.73,4.78,'SELF-IDENTIFIED',weight='bold',fontsize=10.2,color=SLATE,ha='center')
    ax.text(.93,4.78,'OPERATIONAL ONLY',weight='bold',fontsize=10.2,color=SLATE,ha='center')
    for idx,(name,one,two) in enumerate(rows):
        y=4.15-idx*.99
        ax.add_patch(plt.Rectangle((.01,y-.40),.98,.83,facecolor=LIGHT if idx%2==0 else 'white',edgecolor='#DEE6EB',lw=.8))
        if len(name)>65:
            split=name.rfind(' ',0,65)
            ax.text(.025,y+.12,name[:split],fontsize=10.8,color=INK,va='center')
            ax.text(.025,y-.17,name[split+1:],fontsize=10.8,color=INK,va='center')
        else:
            ax.text(.025,y,name,fontsize=10.8,color=INK,va='center')
        ax.text(.73,y,one,fontsize=11.6,weight='bold',color=BLUE,ha='center',va='center')
        ax.text(.93,y,two,fontsize=11.6,weight='bold',color=BLUE,ha='center',va='center')
    ax.text(.01,.10,'Five distress-related items: 1, 3, 10, 11, 13. Corrected effect sizes cannot be inferred without item-level data.',fontsize=10,color=SLATE)
    fig.savefig(HERE/'figure_04_hypothetical_sensitivity.png',dpi=160,bbox_inches='tight',facecolor='white');plt.close(fig)


def image_font(bold=False,size=25):
    path='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    if Path(path).exists():
        return ImageFont.truetype(path,size)
    return ImageFont.load_default()


def figure_05():
    src=[(1,'Self-identified-incel distribution'),(3,'Labeled operational incels — closely matches Figure 1'),
         (2,'Operational incels after excluding self-identifiers')]
    imgs=[Image.open(HERE/'source_plots'/f'alexander_figure_{idx}.jpeg').convert('RGB') for idx,_ in src]
    canvas_w=1100
    img_w=950
    caption_h=76
    new_h=int(imgs[0].height*img_w/imgs[0].width)
    top=116
    bottom=80
    H=top+3*(caption_h+new_h+18)+bottom
    canvas=Image.new('RGB',(canvas_w,H),'white')
    draw=ImageDraw.Draw(canvas)
    font_h=image_font(True,30)
    font_b=image_font(True,25)
    font_s=image_font(False,19)
    draw.text((35,27),'Original figure comparison: Alexander (2023)',fill=BLUE,font=font_h)
    draw.text((35,78),'Panels reordered to make the Figure 1 / Figure 3 similarity visible',fill=SLATE,font=font_s)
    y=top
    for (idx,label),im in zip(src,imgs):
        draw.rounded_rectangle((32,y,canvas_w-32,y+caption_h+new_h+12),radius=10,outline='#D6E1E8',width=2)
        draw.text((50,y+12),f'Alexander Figure {idx}',font=font_b,fill=BLUE)
        draw.text((50,y+44),label,font=font_s,fill=SLATE)
        resize=im.resize((img_w,new_h),Image.Resampling.LANCZOS)
        canvas.paste(resize,((canvas_w-img_w)//2,y+caption_h))
        y += caption_h+new_h+18
    draw.text((35,H-59),'Original plot axes/scales retained; no observations digitized. Source: datepsychology.com.',fill=SLATE,font=font_s)
    canvas.save(HERE/'figure_05_original_plot_comparison.png')


def main():
    v=load_numbers()
    items=load_categories()
    records, report=compute(v)
    with (HERE/'reconstruction_results.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,['calculation','value','status_or_assumption'])
        writer.writeheader();writer.writerows(records)
    (HERE/'reconstruction_results.txt').write_text(report,encoding='utf-8')
    figure_01(v)
    figure_02(v)
    figure_03(items)
    figure_04(v)
    figure_05()
    print(report)
    print('Wrote five PNGs and reconstruction_results.csv/.txt to',HERE)

if __name__ == '__main__':
    main()
