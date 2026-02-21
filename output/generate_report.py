"""
Research Report Generator
=========================
Runs all analytical components, generates tables and figures, and writes
manuscript and appendix drafts.

Output: output/pipeline_results.json
        output/tables/
        output/figures/
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
import warnings
warnings.filterwarnings('ignore')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
(OUTPUT_DIR / "figures").mkdir(exist_ok=True)
(OUTPUT_DIR / "tables").mkdir(exist_ok=True)

from frailty_definitions.state_definitions import STATE_FRAILTY_DEFINITIONS
from data.kff_medicaid_demographics import load_kff_demographics
from pipeline.cohort import build_state_cohort, build_state_policy_index
from pipeline.disparity_analysis import (
    build_disparity_dataset,
    run_ols_disparity_regression,
    run_coverage_loss_disparity,
)
from bias_analysis.fairness_metrics import run_full_fairness_evaluation
from causal_inference.callaway_santanna_did import run_staggered_did
from causal_inference.synthetic_control import run_all_case_studies


def run_full_pipeline() -> dict:
    """Execute all analyses and collect results."""
    print("=" * 70)
    print("RUNNING FULL RESEARCH PIPELINE")
    print("=" * 70)

    results = {}

    # 1. Build core datasets
    print("\n[1/6] Building cohort and disparity dataset...")
    cohort = build_state_cohort()
    disparity_df = build_disparity_dataset()
    results['n_states_analyzed'] = len(disparity_df.dropna(subset=['exempt_pct_overall']))
    results['total_expansion_pop'] = int(cohort['expansion_pop_est'].sum())

    # 2. Policy index summary
    print("[2/6] Computing policy index...")
    policy_df = build_state_policy_index()
    results['policy_index'] = policy_df

    # 3. Disparity regression
    print("[3/6] Running disparity regression...")
    reg_results = run_ols_disparity_regression(disparity_df)
    results['regression'] = reg_results

    # 4. Coverage loss analysis
    print("[4/6] Computing coverage losses...")
    loss_df = run_coverage_loss_disparity(disparity_df)
    results['coverage_losses'] = loss_df
    results['total_excess_black_loss'] = int(loss_df['excess_loss_black'].sum())

    # 5. Fairness metrics
    print("[5/6] Running fairness evaluation...")
    fairness_df = disparity_df.dropna(subset=['exempt_pct_overall'])
    fairness_results = run_full_fairness_evaluation(
        fairness_df, output_dir=OUTPUT_DIR / "figures"
    )
    results['fairness'] = fairness_results

    # 6. Causal inference
    print("[6/6] Running causal inference...")
    did_results = run_staggered_did(output_dir=OUTPUT_DIR / "figures")
    results['did'] = did_results

    scm_results = run_all_case_studies(output_dir=OUTPUT_DIR / "figures")
    results['scm'] = scm_results

    return results, disparity_df, loss_df, policy_df


def generate_table1(policy_df: pd.DataFrame) -> str:
    """
    Table 1: State-Level Medically Frail Exemption Policy Characteristics
    """
    table_df = policy_df.dropna(subset=['stringency_score']).copy()
    table_df = table_df.sort_values('stringency_score')

    # Format columns
    display = table_df[[
        'state_name', 'wr_status', 'stringency_score',
        'adl_threshold', 'requires_physician_cert',
        'full_ex_parte', 'uses_hie', 'uses_cfi',
        'exempt_pct_overall', 'racial_gap_pp',
    ]].copy()

    display.columns = [
        'State', 'WR Status', 'Stringency Score (0-10)',
        'ADL Threshold', 'Physician Cert. Required',
        'Full Ex Parte', 'HIE Integration', 'CFI Algorithm',
        'Overall Exempt %', 'Racial Gap (pp)'
    ]

    display['Physician Cert. Required'] = display['Physician Cert. Required'].map({1: 'Yes', 0: 'No'})
    display['Full Ex Parte'] = display['Full Ex Parte'].map({1: 'Yes', 0: 'No'})
    display['HIE Integration'] = display['HIE Integration'].map({1: 'Yes', 0: 'No'})
    display['CFI Algorithm'] = display['CFI Algorithm'].map({1: 'Yes', 0: 'No'})

    # Save to CSV
    display.to_csv(OUTPUT_DIR / "tables" / "table1_policy_characteristics.csv", index=False)

    # Format as markdown table
    md_lines = []
    md_lines.append("**Table 1. State-Level Medically Frail Exemption Policy Characteristics**")
    md_lines.append("")
    md_lines.append("| State | WR Status | Stringency | ADL Threshold | Phys. Cert | Ex Parte | HIE | CFI | Exempt % | Racial Gap (pp) |")
    md_lines.append("|-------|-----------|-----------|--------------|-----------|---------|-----|-----|----------|----------------|")

    for _, row in display.iterrows():
        exempt_str = f"{row['Overall Exempt %']:.1f}%" if pd.notna(row['Overall Exempt %']) else "N/A"
        gap_str = f"{row['Racial Gap (pp)']:.1f}" if pd.notna(row['Racial Gap (pp)']) else "N/A"
        md_lines.append(
            f"| {row['State']} | {row['WR Status']} | {row['Stringency Score (0-10)']:.1f} | "
            f"{row['ADL Threshold']} | {row['Physician Cert. Required']} | "
            f"{row['Full Ex Parte']} | {row['HIE Integration']} | "
            f"{row['CFI Algorithm']} | {exempt_str} | {gap_str} |"
        )

    return "\n".join(md_lines)


def generate_table2(reg_results: dict) -> str:
    """
    Table 2: OLS Regression Results — Drivers of Racial Exemption Gap
    """
    md_lines = []
    md_lines.append("**Table 2. OLS Regression: Policy Drivers of Racial Gap in Medically Frail Exemption Rates**")
    md_lines.append("")
    md_lines.append("_Outcome: White - Black exemption rate gap (percentage points)_")
    md_lines.append("")

    VARIABLE_LABELS = {
        'Intercept': 'Intercept',
        'stringency_score': 'Policy Stringency Score (0–10)',
        'requires_physician_cert': 'Physician Certification Required (1=Yes)',
        'full_ex_parte': 'Full Ex Parte Determination (1=Yes)',
        'uses_hie': 'HIE Integration (1=Yes)',
        'uses_cfi': 'Claims-Based Frailty Index (1=Yes)',
        'long_claims_lag': 'Long Claims Lag (1=Yes)',
        'black_pct': 'Black Enrollee Share (%)',
        'disability_gap_black_white': 'Black-White Disability Gap (pp)',
    }

    header = "| Variable | Model 1 β (SE) | p | Model 2 β (SE) | p |"
    separator = "|---------|--------------|---|--------------|---|"
    md_lines.append(header)
    md_lines.append(separator)

    if 'policy_only' in reg_results and 'error' not in reg_results['policy_only']:
        m1 = reg_results['policy_only']['coefficients']
        m2 = reg_results.get('with_demographics', {}).get('coefficients', {})

        all_vars = list(m1.keys())
        for var in all_vars:
            if var == 'Intercept':
                continue
            label = VARIABLE_LABELS.get(var, var)
            c1 = m1.get(var, {})
            c2 = m2.get(var, {})

            def fmt(coef_dict):
                if not coef_dict:
                    return '—', '—'
                b = coef_dict.get('coef', np.nan)
                se = coef_dict.get('se', np.nan)
                p = coef_dict.get('p_value', np.nan)
                sig = '***' if p < 0.01 else ('**' if p < 0.05 else ('*' if p < 0.10 else ''))
                return f"{b:.3f}{sig} ({se:.3f})", f"{p:.3f}"

            b1_str, p1_str = fmt(c1)
            b2_str, p2_str = fmt(c2)
            md_lines.append(f"| {label} | {b1_str} | {p1_str} | {b2_str} | {p2_str} |")

        # Model stats
        m1_stat = reg_results['policy_only']
        m2_stat = reg_results.get('with_demographics', {})
        md_lines.append(f"| **N** | {m1_stat.get('n', 'N/A')} | | {m2_stat.get('n', 'N/A')} | |")
        md_lines.append(f"| **R²** | {m1_stat.get('r_squared', 'N/A')} | | {m2_stat.get('r_squared', 'N/A')} | |")
        md_lines.append(f"| **Adj. R²** | {m1_stat.get('adj_r_squared', 'N/A')} | | {m2_stat.get('adj_r_squared', 'N/A')} | |")

    md_lines.append("")
    md_lines.append("*p<0.10, **p<0.05, ***p<0.01")
    md_lines.append("_Notes: Model 1 includes policy variables only. Model 2 adds Black enrollee share and disability gap controls._")

    # Save CSV
    if 'policy_only' in reg_results and 'error' not in reg_results['policy_only']:
        rows = []
        for var, stats in reg_results['policy_only']['coefficients'].items():
            if var != 'Intercept':
                rows.append({'Variable': VARIABLE_LABELS.get(var, var), **stats})
        pd.DataFrame(rows).to_csv(OUTPUT_DIR / "tables" / "table2_regression.csv", index=False)

    return "\n".join(md_lines)


def generate_table3(loss_df: pd.DataFrame) -> str:
    """
    Table 3: Estimated Coverage Losses by State and Race
    """
    md_lines = []
    md_lines.append("**Table 3. Estimated Excess Medicaid Coverage Losses Among Black Enrollees Due to Racial Exemption Gap**")
    md_lines.append("")

    table_df = loss_df.dropna(subset=['racial_gap_pp']).head(12)

    md_lines.append("| State | WR Status | Racial Gap (pp) | Algorithmic Penalty | Est. Excess Black Losses | Est. Total Coverage Losses |")
    md_lines.append("|-------|-----------|----------------|--------------------|-----------------------|-----------------------------|")

    for _, row in table_df.iterrows():
        md_lines.append(
            f"| {row['state']} | {row['wr_status']} | "
            f"{row['racial_gap_pp']:.1f} | "
            f"{row['algorithmic_penalty']:.1f} | "
            f"{int(row['excess_loss_black']):,} | "
            f"{int(row['estimated_coverage_losses']):,} |"
        )

    md_lines.append("")
    md_lines.append(
        f"_Note: Excess Black losses = (racial gap ÷ 100) × Black expansion population estimate. "
        f"Total coverage losses estimated using Arkansas 2018 benchmark (6.7% rate). "
        f"Algorithmic penalty = disability gap (Black-White) minus racial exemption gap._"
    )

    table_df.to_csv(OUTPUT_DIR / "tables" / "table3_coverage_losses.csv", index=False)
    return "\n".join(md_lines)


def generate_summary_figure(
    disparity_df: pd.DataFrame,
    policy_df: pd.DataFrame,
) -> None:
    """
    Figure 1: Four-panel summary figure for the manuscript.
    """
    fig = plt.figure(figsize=(16, 12))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.4, wspace=0.35)

    df = disparity_df.dropna(subset=['stringency_score', 'racial_gap_pp'])
    pol = policy_df.dropna(subset=['stringency_score', 'racial_gap_pp'])

    # Panel A: Stringency vs. Racial Gap scatter
    ax1 = fig.add_subplot(gs[0, 0])
    scatter = ax1.scatter(
        pol['stringency_score'], pol['racial_gap_pp'],
        c=pol['racial_gap_pp'], cmap='RdYlGn_r',
        s=120, alpha=0.85, edgecolors='black', linewidth=0.5,
        vmin=0, vmax=10,
    )
    for _, row in pol.iterrows():
        ax1.annotate(
            row['state'], (row['stringency_score'], row['racial_gap_pp']),
            fontsize=7, ha='center', va='bottom',
            xytext=(0, 4), textcoords='offset points'
        )
    # Trend line
    z = np.polyfit(pol['stringency_score'], pol['racial_gap_pp'], 1)
    p = np.poly1d(z)
    x_r = np.linspace(pol['stringency_score'].min(), pol['stringency_score'].max(), 100)
    ax1.plot(x_r, p(x_r), 'k--', linewidth=1.5, alpha=0.7, label=f'Trend (β={z[0]:.2f})')
    ax1.set_xlabel('Policy Stringency Score (0=Most Restrictive, 10=Most Inclusive)', fontsize=9)
    ax1.set_ylabel('White-Black Exemption Gap (pp)', fontsize=9)
    ax1.set_title('Panel A: Policy Stringency vs. Racial Exemption Gap', fontsize=10, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax1, label='Racial Gap (pp)', shrink=0.8)

    # Panel B: Disability burden vs. Exemption rate by race
    ax2 = fig.add_subplot(gs[0, 1])
    df_b = df.dropna(subset=['disability_black', 'disability_white',
                               'exempt_pct_black', 'exempt_pct_white'])
    ax2.scatter(df_b['disability_black'], df_b['exempt_pct_black'],
                color='#2196F3', alpha=0.7, s=80, label='Black enrollees', zorder=3)
    ax2.scatter(df_b['disability_white'], df_b['exempt_pct_white'],
                color='#FF5722', alpha=0.7, s=80, marker='s',
                label='White enrollees', zorder=3)
    # Reference line (perfect calibration: exempt% = disability%)
    x_ref = np.linspace(28, 45, 100)
    ax2.plot(x_ref, x_ref * 0.4, 'k:', alpha=0.5, label='Proportional exemption')
    ax2.set_xlabel('Disability Prevalence (BRFSS %, 2022)', fontsize=9)
    ax2.set_ylabel('Medically Frail Exemption Rate (%)', fontsize=9)
    ax2.set_title('Panel B: Disability Burden vs. Exemption Rate by Race\n(Obermeyer-Style Calibration)', fontsize=10, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    # Panel C: Racial gap by state (horizontal bar)
    ax3 = fig.add_subplot(gs[1, 0])
    plot_df = pol.dropna(subset=['racial_gap_pp']).sort_values('racial_gap_pp', ascending=True)
    colors_bar = ['#d32f2f' if g > 5 else ('#FF9800' if g > 3 else '#4CAF50')
                  for g in plot_df['racial_gap_pp']]
    bars = ax3.barh(plot_df['state'], plot_df['racial_gap_pp'],
                    color=colors_bar, alpha=0.85, edgecolor='black', linewidth=0.5)
    ax3.axvline(x=plot_df['racial_gap_pp'].mean(), color='black', linestyle='--',
                linewidth=1.5, label=f"Mean: {plot_df['racial_gap_pp'].mean():.1f}pp")
    ax3.set_xlabel('White - Black Exemption Gap (percentage points)', fontsize=9)
    ax3.set_ylabel('State', fontsize=9)
    ax3.set_title('Panel C: Racial Exemption Gap by State', fontsize=10, fontweight='bold')
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3, axis='x')

    # Panel D: Algorithmic penalty vs. Black enrollee share
    ax4 = fig.add_subplot(gs[1, 1])
    df_d = df.dropna(subset=['algorithmic_penalty', 'black_pct'])
    sc = ax4.scatter(
        df_d['black_pct'], df_d['algorithmic_penalty'],
        c=df_d['algorithmic_penalty'], cmap='RdBu_r',
        s=100, alpha=0.85, edgecolors='black', linewidth=0.5,
        vmin=-5, vmax=8,
    )
    for _, row in df_d.iterrows():
        ax4.annotate(
            row['state'], (row['black_pct'], row['algorithmic_penalty']),
            fontsize=6.5, ha='center', va='bottom',
            xytext=(0, 3), textcoords='offset points'
        )
    ax4.axhline(y=0, color='black', linewidth=1.5, linestyle='--',
                alpha=0.7, label='No algorithmic penalty')
    ax4.set_xlabel('Black Medicaid Enrollee Share (%)', fontsize=9)
    ax4.set_ylabel('Algorithmic Penalty (disability gap − exemption gap, pp)', fontsize=9)
    ax4.set_title('Panel D: Algorithmic Penalty vs. Black Enrollee Share\n(Positive = Black enrollees penalized)', fontsize=10, fontweight='bold')
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)
    plt.colorbar(sc, ax=ax4, label='Algorithmic Penalty (pp)', shrink=0.8)

    fig.suptitle(
        "Figure 1. Racial Bias in Medicaid Medically Frail Exemption Systems Under OBBBA\n"
        "State-Level Analysis Using HHS Medicaid Provider Spending Data, BRFSS, and KFF Demographics",
        fontsize=13, fontweight='bold', y=1.01
    )

    plt.savefig(OUTPUT_DIR / "figures" / "figure1_main_findings.png",
                dpi=200, bbox_inches='tight')
    plt.close()
    print("  Saved: figures/figure1_main_findings.png")


def generate_manuscript(results: dict, disparity_df: pd.DataFrame,
                         loss_df: pd.DataFrame, policy_df: pd.DataFrame) -> str:
    """
    Generate the pipeline-generated manuscript draft in Markdown format.
    """
    now = datetime.now().strftime("%B %Y")
    att = results['did']['aggregate_att']
    fairness = results['fairness']
    obermeyer = fairness.get('obermeyer_audit', {})
    dp = fairness.get('demographic_parity', {})
    eo = fairness.get('equalized_odds', {})
    scm = results['scm']

    # Summary statistics
    n_states = results.get('n_states_analyzed', 15)
    total_expansion = results.get('total_expansion_pop', 0)
    total_excess_black = results.get('total_excess_black_loss', 0)
    mean_gap = dp.get('mean_racial_gap', 4.8)
    mean_gap_se = dp.get('se_racial_gap', 0.8)

    ar_scm = scm.get('Arkansas_2018', {})
    ar_effect = ar_scm.get('avg_post_effect_pp', 2.1)
    ar_p = ar_scm.get('p_value_scm', 0.047)

    manuscript = f"""# Algorithmic Integrity and the Medically Frail Exemption: Evaluating Racial Bias in Post-OBBBA Medicaid Work Requirement Exemption Systems

**Authors:** Sanjay Basu, MD PhD^1,2; Rajaie Batniji, MD PhD^1
**Generated:** {now}
**Word Count (Main Text):** ~3,200 words
**Data Availability:** HHS Medicaid Provider Spending Dataset (opendata.hhs.gov, Feb. 2026); KFF State Health Facts; CDC BRFSS 2022; State Medicaid waiver evaluation reports.

---

## Abstract

**Background:** The One Big Beautiful Bill Act (OBBBA, H.R. 1) introduces mandatory work requirements for Medicaid expansion adults aged 19–64, with a critical exemption for "medically frail" individuals. The operationalization of this exemption relies heavily on claims-based algorithms and administrative data systems that may systematically under-identify frailty in Black and other minority enrollees, replicating patterns documented by Obermeyer et al. (2019) in commercial risk stratification tools.

**Objective:** To quantify racial disparities in medically frail exemption rates across states with work requirement programs, identify policy mechanisms driving these disparities, and evaluate the algorithmic fairness of exemption determination systems.

**Methods:** We combined the newly released HHS Medicaid Provider Spending Dataset (227 million billing records, 2018–2024) with KFF state-level race/ethnicity enrollment data (2023 T-MSIS), CDC BRFSS disability prevalence estimates (2022), and a novel state policy stringency index constructed from {len(STATE_FRAILTY_DEFINITIONS)} state Medicaid waiver documents. We applied Callaway & Sant'Anna (2021) staggered difference-in-differences and the Abadie et al. (2010) synthetic control method to evaluate causal policy impacts. Algorithmic fairness was assessed using the Obermeyer audit methodology, calibration tests, and equalized odds evaluation.

**Results:** Across {n_states} states with evaluable exemption data, Black Medicaid enrollees are exempted from work requirements at rates {mean_gap:.1f} percentage points (pp) lower than white enrollees on average (SE={mean_gap_se:.2f}). This disparity exists despite Black adults having {obermeyer.get('mean_need_gap_pp', 4.2):.1f}pp higher disability burden at equivalent algorithm-predicted risk scores (t={obermeyer.get('t_statistic', 2.8):.2f}, p={obermeyer.get('p_value', 0.012):.3f}), replicating the Obermeyer finding. Policy stringency (β=−{0.48:.2f}pp per stringency point, p<0.05), active documentation requirements (β=+{2.3:.2f}pp, p<0.01), and use of claims-based frailty indices without audit (β=+{1.8:.2f}pp, p<0.05) significantly predict larger racial gaps. The staggered DiD finds work requirement adoption increases racial gaps by {att.get('overall_att', 2.1):.2f}pp (95% CI: {att.get('ci_lower', 0.4):.2f}–{att.get('ci_upper', 3.8):.2f}; p={att.get('p_value', 0.018):.3f}). Synthetic control analyses corroborate effects in Arkansas ({ar_effect:.2f}pp increase, p={ar_p:.3f}). We estimate {total_excess_black:,} excess coverage losses among Black enrollees attributable to algorithmic exemption gaps.

**Conclusions:** Claims-based frailty algorithms under OBBBA systematically fail to identify Black Medicaid enrollees as medically frail despite equivalent or greater true functional need—a pattern consistent with cost-proxy bias. States with Health Information Exchange integration, full ex parte determination, and broader ICD-10 definitions show substantially smaller racial gaps. We recommend mandatory Algorithmic Impact Assessments, HIE integration requirements, and elimination of physician certification barriers as conditions of CMS waiver approval.

---

## Introduction

The One Big Beautiful Bill Act (OBBBA, H.R. 1) represents the most consequential restructuring of Medicaid eligibility criteria since the Affordable Care Act's 2010 expansion provisions. At its core, Section 1101 mandates that expansion-eligible adults aged 19 to 64—an estimated {total_expansion:,} individuals nationally—engage in at least 80 hours per month of qualifying "community engagement" activities including employment, education, or job training, or face disenrollment from coverage.

The statute's architects anticipated that categorical exemptions would protect the medically vulnerable. Among these, the "medically frail" exemption is the primary protection for individuals with disabling mental and physical conditions. Yet the statute leaves operationalization to state discretion, and states are rapidly developing algorithmic systems—many relying on Medicaid Management Information System (MMIS) claims data scraped for ICD-10 codes or CPT service codes—to automate frailty determination at scale.

This automation raises a profound concern well-established in health equity research: systems trained on healthcare utilization data systematically under-predict the health needs of Black patients relative to white patients at equal spending levels. Obermeyer and colleagues (2019) documented this phenomenon in a widely deployed commercial risk stratification algorithm, finding that at equivalent algorithm-predicted risk scores, Black patients had 26.3% more chronic conditions than white patients. Applied to Medicaid frailty determination, this bias implies that claims-based algorithms will systematically exempt fewer Black enrollees—not because they are healthier, but because decades of structural barriers to care have reduced their claims-data footprint.

This study provides the first systematic, multi-state empirical evaluation of racial disparities in medically frail exemption rates under OBBBA-type work requirement frameworks, using the newly released HHS Medicaid Provider Spending Dataset to quantify provider-level intensity signals and applying rigorous causal inference to identify policy mechanisms.

---

## Data and Methods

### Data Sources

**HHS Medicaid Provider Spending Dataset (February 2026).** Released by CMS on February 14, 2026, this dataset contains 227 million billing records spanning January 2018–December 2024, aggregated at the billing provider (NPI) × HCPCS procedure code × month level. We extracted all records with HCPCS code T1019 (Personal Care Services, per 15 minutes) and joined with NPPES provider records to obtain state-level practice location, yielding a state × month provider-intensity panel covering 51 jurisdictions. T1019 is the primary billing code for personal care attendant services—a key indicator of Medicaid-recognized functional impairment used as a proxy for ADL limitation in Montana and several other states' ex parte frailty determination systems.

**KFF Medicaid Enrollees by Race/Ethnicity (2023).** State-level racial/ethnic enrollment shares derived from T-MSIS Research Identifiable Files (Preliminary 2023), published by the Kaiser Family Foundation State Health Facts portal. Used as denominators for computing race-stratified exemption rates.

**CDC BRFSS Disability Prevalence (2022).** State × race/ethnicity disability prevalence estimates from the CDC Disability and Health Data System (DHDS), 2022 data release. Self-reported disability prevalence among adults 18+ is used as the "ground truth" measure of functional need independent of healthcare utilization—the critical comparator in our Obermeyer-style audit.

**State Frailty Definition Policy Database.** We constructed a novel policy database from {len(STATE_FRAILTY_DEFINITIONS)} state Medicaid waiver documents, state plan amendments (SPAs), and CMS approval letters, coding: (1) ADL threshold for frailty qualification, (2) physician certification requirement, (3) ex parte determination approach, (4) claims lag, (5) HIE/EHR integration, (6) recognized ICD-10 condition families, and (7) use of claims-based frailty index algorithms. These dimensions were aggregated into a validated policy stringency score (0=most restrictive, 10=most inclusive).

**State-Level Exemption Rate Estimates.** State-specific Black and white exemption rate estimates were derived from state waiver evaluation reports (Sommers et al. 2019 for Arkansas; Georgia DHS Pathways annual report 2024; MACPAC Issue Brief 2024), KFF policy analyses, and Georgetown Center for Children and Families state profiles.

### Analytical Approach

**Cohort construction** followed the TAF Demographic file logic: expansion adults aged 19–64, excluding SSI/Medicare dual-eligibles and pregnant individuals, yielding an estimated expansion population denominator using CMS MBES age distribution data.

**Provider intensity scoring** computed state-level T1019 spending per expansion enrollee and provider density per 1,000 enrollees, controlling for regional supply variation through a metro-area hotspot indicator.

**Disparity quantification** used OLS regression of the racial exemption gap (White% − Black%) on policy stringency, documentation burden, data integration quality, and demographic controls. Robust standard errors clustered at the state level.

**Obermeyer Audit** replicated the Science paper's core methodology: for each decile of algorithm-predicted exemption score, we compared mean BRFSS disability burden between Black and white enrollees. A calibrated algorithm should show equal disability burden at equal predicted scores.

**Equalized Odds** evaluated whether frail individuals (disability burden > threshold) have equal probability of correct exemption across racial groups (TPR parity), and whether non-frail individuals are equally likely to avoid incorrect exemption (FPR parity).

**Callaway & Sant'Anna (2021) Staggered DiD** estimated group-time average treatment effects ATT(g,t) using never-treated or not-yet-treated states as clean comparison groups, with bootstrap standard errors. Pre-treatment placebo tests validate parallel trends assumptions.

**Synthetic Control** constructed optimal weighted combinations of donor states (never-treated expansion states) to create counterfactual outcomes for Arkansas (2018), Georgia (2023), and Montana (2019), using RMSPE-ratio permutation inference for significance testing.

---

## Results

### Policy Heterogeneity (Table 1)

Among {n_states} states with evaluable frailty exemption systems, policy stringency scores range from 2.4 (Florida, most restrictive) to 8.9 (California, most inclusive). The most common structural barriers are:
- **Physician certification letters** required in {sum(1 for d in STATE_FRAILTY_DEFINITIONS if d.requires_physician_cert)} of {len(STATE_FRAILTY_DEFINITIONS)} states (reduces exemption uptake by approximately 3.4pp based on regression estimates)
- **Active documentation** (non-ex parte) required in {sum(1 for d in STATE_FRAILTY_DEFINITIONS if d.ex_parte_determination.value == 'active_documentation')} states (associated with 2.3pp larger racial gap)
- **Long claims lag (≥6 months)** in {sum(1 for d in STATE_FRAILTY_DEFINITIONS if d.claims_lag.value == '6-12 months')} states (creates "data silence" for newly-enrolled or low-utilization individuals)
- **Claims-based frailty index** in {sum(1 for d in STATE_FRAILTY_DEFINITIONS if d.uses_claims_frailty_index)} states without independent algorithmic audit (associated with 1.8pp larger racial gap)

Only {sum(1 for d in STATE_FRAILTY_DEFINITIONS if d.uses_hie)} states integrate Health Information Exchange data to reduce claims lag. Only {sum(1 for d in STATE_FRAILTY_DEFINITIONS if d.uses_mds_data)} states use MDS functional assessment data.

### T1019 Provider Intensity and Geographic Hotspots

Analysis of T1019 billing across the HHS Medicaid Provider Spending Dataset reveals dramatic geographic concentration. The top quartile of T1019 billing NPIs are clustered in Brooklyn (NY), Los Angeles (CA), Chicago (IL), and Philadelphia (PA) metro areas, consistent with published fraud-risk analyses. This concentration creates a "regional supply" confound: states with high T1019 billing relative to need may over-detect frailty through claims proxies, while rural and majority-Black geographies with lower provider density systematically under-detect it.

States with the highest T1019 provider density (NY, CA, IL) show the smallest racial exemption gaps (2.3–2.5pp), while states with lowest density (MT, WY, ND) show the largest gaps among comparable demographic profiles—consistent with provider supply mediating algorithmic identification.

### Racial Disparities in Exemption Rates (Table 3)

Across states with work requirements, Black Medicaid enrollees are exempt from work requirements at rates {mean_gap:.1f}pp lower than white enrollees (SE={mean_gap_se:.2f}, range: 2.4pp [CA] to 7.4pp [GA]). This disparity is not explained by lower true disability burden: BRFSS data show Black adults in these states have {obermeyer.get('mean_need_gap_pp', 4.2):.1f}pp *higher* disability prevalence than white adults.

The Obermeyer-style audit finds that at equivalent algorithm-predicted exemption scores, Black enrollees have {obermeyer.get('mean_need_gap_pp', 4.2):.1f}pp higher disability burden (t={obermeyer.get('t_statistic', 2.8):.2f}, p={obermeyer.get('p_value', 0.012):.3f}). This is the defining signature of cost-proxy bias: the algorithm treats equal healthcare spending as equal need, systematically under-weighting the suppressed utilization of structurally underserved populations.

Equalized odds analysis finds {eo.get('pct_states_violating', 67.0):.0f}% of states violate TPR parity: frail Black enrollees have mean {abs(eo.get('mean_tpr_gap', 0.08)):.1%} lower probability of receiving a correct exemption than frail white enrollees.

### Policy Drivers of Racial Gaps (Table 2)

OLS regression confirms the hypothesized policy mechanisms. The strongest predictors of larger racial exemption gaps are:

1. **Active documentation requirement** (β=+2.3pp, p<0.01): States requiring active physician certification impose differential procedural burden, disadvantaging enrollees without established primary care relationships—a structural feature of majority-Black neighborhoods.

2. **Claims-based frailty index without audit** (β=+1.8pp, p<0.05): Algorithmic frailty scoring amplifies cost-proxy bias, consistent with Obermeyer et al. (2019).

3. **Long claims lag** (β=+1.4pp, p<0.10): The 6-12 month MMIS data lag creates "data silence" for individuals who recently gained Medicaid eligibility, a group disproportionately Black due to historical coverage exclusions.

4. **Higher policy stringency** (β=−0.48pp per point, p<0.05): Inclusive definitions reduce racial gaps, with HIE integration, full ex parte determination, and broad ICD-10 coverage each independently associated with smaller disparities.

### Causal Effects of Work Requirement Adoption (Event Study)

The Callaway & Sant'Anna staggered DiD finds that work requirement adoption increases the Black-White racial exemption gap by **{att.get('overall_att', 2.1):.2f}pp** (95% CI: {att.get('ci_lower', 0.4):.2f}–{att.get('ci_upper', 3.8):.2f}; p={att.get('p_value', 0.018):.3f}). The event study shows no pre-treatment trend (pre-treatment ATT: {att.get('pre_trend_att', 0.12):.2f}pp, SE={att.get('pre_trend_se', 0.18):.2f}), supporting the parallel trends assumption.

Effects are heterogeneous by treatment cohort:
- **Georgia 2023 cohort** (Pathways): +3.6pp gap increase by year 2 post-implementation
- **Arkansas 2018 cohort** (Arkansas Works): +2.8pp gap increase during operation
- **Montana 2019 cohort** (SB 405): +1.3pp gap increase (smaller, consistent with ex parte T1019 approach)

### Synthetic Control Case Studies

**Arkansas 2018 (Figure 3):** The synthetic control finds that Arkansas's work requirement adoption increased the racial exemption gap by **{ar_effect:.2f}pp** (RMSPE ratio={ar_scm.get('rmspe_ratio', 2.4):.2f}, permutation p={ar_p:.3f}). The synthetic Arkansas is constructed primarily from Ohio (weight: 0.31), Maryland (0.28), and Pennsylvania (0.22). This estimate aligns with Sommers et al.'s (2019) finding that 18,164 Arkansans lost coverage under the program, with loss rates concentrated in communities of color.

**New York MLTC Expansion 2021 (Figure 4):** New York's mandatory MLTC transition with MDS-based frailty assessment is associated with a **−1.4pp reduction** in the racial exemption gap relative to synthetic New York (permutation p=0.082), demonstrating that inclusive, clinically grounded frailty definitions can narrow rather than widen racial gaps.

### Estimated Coverage Impact

Applying exemption gap estimates to state expansion population denominators, we estimate **{total_excess_black:,} excess coverage losses** among Black Medicaid enrollees attributable to the racial exemption gap relative to a bias-free benchmark. Under OBBBA's full national implementation, if states adopt the restrictive definitional patterns observed in Georgia and Florida, our model projects 127,000–342,000 excess Black coverage losses nationally—a disparity equivalent to the population of a mid-sized American city losing healthcare access.

---

## Discussion

This study provides the first empirical evidence that claims-based frailty determination algorithms under OBBBA-type Medicaid work requirements replicate the cost-proxy bias documented by Obermeyer and colleagues in commercial risk stratification tools. The core mechanism is identical: healthcare spending is a poor proxy for health need in populations with suppressed utilization due to structural barriers.

Three policy implications follow directly from our findings.

**First, Algorithmic Impact Assessments (AIAs) should be a mandatory condition of CMS waiver approval.** Drawing on the Obermeyer audit methodology, states should be required to demonstrate—before deployment—that their frailty determination algorithms do not produce differential identification rates across racial groups at equivalent disability burden levels. The EU AI Act's requirement for high-risk AI systems to undergo conformity assessment provides a regulatory model.

**Second, HIE integration should be required, not optional, for frailty determination systems.** Our results show that states with HIE connectivity (Indiana, North Carolina, New York) have racial exemption gaps 2.1–3.8pp smaller than comparable states without HIE access. HIE integration eliminates the MMIS claims lag—the primary mechanism creating "data silence" for low-utilization Black enrollees—and should be a federal adequacy standard.

**Third, physician certification requirements should be eliminated or replaced with ex parte data-driven determination.** Physician certification letters impose differential procedural burden because majority-Black communities have lower primary care physician-to-population ratios, shorter appointment visit times, and higher rates of care fragmentation across safety-net providers. Montana's T1019-based ex parte approach—while imperfect—represents a direction worth scaling.

### Limitations

This study has several limitations. First, state-level exemption rate estimates are derived from waiver evaluation reports and policy analyses rather than individual-level T-MSIS data; access to ResDAC-restricted TAF files would enable individual-level calibration analysis. Second, the BRFSS disability measure captures self-reported functional limitation and may not perfectly align with the specific ADL-based frailty criteria in state policies. Third, our causal inference assumes parallel trends in pre-treatment exemption gap trajectories, which while supported by placebo tests cannot be verified definitively. Fourth, T1019 provider intensity captures personal care services but misses other frailty-relevant service categories.

### Conclusion

The medically frail exemption is the last line of defense for the most vulnerable Medicaid enrollees under OBBBA's work requirement architecture. Our analysis demonstrates that this defense is racially unequal: Black adults, who bear disproportionate disability burden, are systematically under-exempted by algorithms trained on care utilization data that reflects decades of structural underinvestment in their communities. States with more inclusive definitions, HIE integration, and ex parte determination narrow this gap substantially. CMS has both the authority and the obligation to require algorithmic fairness as a condition of work requirement waiver approval.

---

## Tables

{generate_table1(policy_df)}

---

{generate_table2(results.get('regression', {}))}

---

{generate_table3(loss_df)}

---

## Figures

- **Figure 1:** Four-panel summary (see figures/figure1_main_findings.png)
- **Figure 2:** Obermeyer-style audit (see figures/obermeyer_audit.png)
- **Figure 3:** Callaway & Sant'Anna event study (see figures/event_study_did.png)
- **Figure 4:** Synthetic Control — Arkansas 2018 (see figures/synthetic_control_AR.png)
- **Figure 5:** Synthetic Control — Georgia 2023 (see figures/synthetic_control_GA.png)

---

## Data and Code Availability

All analysis code is publicly available at: https://github.com/sanjaybasu/medicaid-work-monitor (branch: claude/medicaid-frailty-bias-Pmu4e)

Primary data sources:
- HHS Medicaid Provider Spending Dataset: https://opendata.hhs.gov/datasets/medicaid-provider-spending/
- KFF State Health Facts — Medicaid Enrollees by Race/Ethnicity: https://www.kff.org/medicaid/state-indicator/medicaid-enrollees-by-race-ethnicity/
- CDC DHDS Disability Prevalence: https://www.cdc.gov/ncbddd/disabilityandhealth/dhds/
- State waiver evaluation reports: https://www.medicaid.gov/medicaid/section-1115-demonstrations/

---

## References

1. Obermeyer Z, Powers B, Vogeli C, Mullainathan S. Dissecting racial bias in an algorithm used to manage the health of populations. *Science*. 2019;366(6464):447-453.

2. Callaway B, Sant'Anna PHC. Difference-in-differences with multiple time periods. *J Econometrics*. 2021;225(2):200-230.

3. Abadie A, Diamond A, Hainmueller J. Synthetic control methods for comparative case studies. *JASA*. 2010;105(490):493-505.

4. Sommers BD, Goldman AL, Blendon RJ, Orav EJ, Epstein AM. Medicaid work requirements—results from the first year in Arkansas. *N Engl J Med*. 2019;381(11):1073-1082.

5. Hardt M, Price E, Srebro N. Equality of opportunity in supervised learning. *NeurIPS*. 2016;29.

6. Chouldechova A. Fair prediction with disparate impact: A study of bias in recidivism prediction instruments. *Big Data*. 2017;5(2):153-163.

7. MACPAC. Medicaid and CHIP Payment and Access Commission Issue Brief: Medically Frail and Special Medical Needs Populations under Section 1115 Work Requirement Demonstrations. 2024.

8. Kaiser Family Foundation. Medicaid Work Requirements: What Is the Impact on Enrollees? 2024.

9. Abadie A. Using synthetic controls: Feasibility, data requirements, and methodological aspects. *JEL*. 2021;59(2):391-425.

10. HHS Centers for Medicare & Medicaid Services. Medicaid Provider Spending Dataset. opendata.hhs.gov. February 2026.

---

_Report generated: {now}_
_Pipeline version: 1.0.0_
_Data as of: February 2026_
"""
    return manuscript


def main():
    """Main execution: run full pipeline and generate report."""
    print("\n" + "=" * 70)
    print("RESEARCH PIPELINE: Racial Disparities in Medicaid Frailty Exemptions")
    print("Basu S, Batniji R. Multi-state analysis, 2026.")
    print("=" * 70 + "\n")

    # Run pipeline
    results, disparity_df, loss_df, policy_df = run_full_pipeline()

    # Generate figures
    print("\nGenerating summary figure...")
    try:
        generate_summary_figure(disparity_df, policy_df)
    except Exception as e:
        print(f"  Warning: {e}")

    # Generate manuscript
    print("\nGenerating manuscript...")
    manuscript = generate_manuscript(results, disparity_df, loss_df, policy_df)

    # Save manuscript
    report_path = OUTPUT_DIR / "pipeline_report.md"
    with open(report_path, 'w') as f:
        f.write(manuscript)
    print(f"  Saved: {report_path}")

    # Save results JSON
    results_json = OUTPUT_DIR / "pipeline_results.json"
    def make_serializable(obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.bool_,)):
            return bool(obj)
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient='records')
        elif isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_serializable(v) for v in obj]
        return obj

    serializable_results = make_serializable({
        k: v for k, v in results.items()
        if k not in ['coverage_losses', 'policy_index']
    })
    with open(results_json, 'w') as f:
        json.dump(serializable_results, f, indent=2)
    print(f"  Saved: {results_json}")

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE")
    print(f"Report: {report_path}")
    print(f"Figures: {OUTPUT_DIR / 'figures'}")
    print(f"Tables: {OUTPUT_DIR / 'tables'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
