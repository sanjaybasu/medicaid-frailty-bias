#!/usr/bin/env python3
"""
Reconceptualized Pipeline: Improved Frailty Algorithm Analysis
===============================================================
Master pipeline that runs the full reconceptualized analysis:

1. Status quo simulation (all 17 states)
2. Improved algorithm simulation (all 17 states)
3. Head-to-head comparison
4. Channel decomposition
5. Multi-dimensional fairness (race + geographic)
6. Sensitivity analysis
7. Coverage impact projection
8. Legacy analyses for eAppendix (DiD, SCM, Obermeyer)
9. G2211 visit complexity validation (requires data/g2211_by_npi.parquet)

Outputs:
    output/improved_algorithm_results.json  — Primary results
    output/g2211_validation_results.json    — G2211 validation
    output/tables/                          — CSV tables for exhibits
"""

import json
import sys
from pathlib import Path

# Ensure project root is on path
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

def main():
    print("=" * 70)
    print("RECONCEPTUALIZED PIPELINE: Improved Frailty Algorithm Analysis")
    print("=" * 70)

    # --- Step 1: Run improved algorithm analysis ---
    print("\n\n[1/5] Running improved algorithm analysis...")
    from bias_analysis.improved_algorithm import run_full_improved_analysis
    results = run_full_improved_analysis(n_sim=300, sample_n=2000)

    # Save primary results
    output_dir = ROOT / 'output'
    output_dir.mkdir(exist_ok=True)
    tables_dir = output_dir / 'tables'
    tables_dir.mkdir(exist_ok=True)

    with open(output_dir / 'improved_algorithm_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  Saved: {output_dir / 'improved_algorithm_results.json'}")

    # --- Step 2: Generate comparison table CSV ---
    print("\n\n[2/5] Generating exhibit tables...")
    import pandas as pd

    # Exhibit 1: State algorithm features + sensitivity
    comparison = pd.DataFrame(results['comparison'])
    comparison.to_csv(tables_dir / 'exhibit1_algorithm_comparison.csv', index=False)
    print(f"  Saved: exhibit1_algorithm_comparison.csv")

    # Exhibit 4: Coverage impact
    coverage = pd.DataFrame(results['coverage_impact'])
    coverage.to_csv(tables_dir / 'exhibit4_coverage_impact.csv', index=False)
    print(f"  Saved: exhibit4_coverage_impact.csv")

    # Decomposition table
    decomp = pd.DataFrame(results['decomposition'])
    decomp.to_csv(tables_dir / 'etable_decomposition.csv', index=False)
    print(f"  Saved: etable_decomposition.csv")

    # --- Step 3: Legacy analyses for eAppendix ---
    print("\n\n[3/5] Running legacy analyses (eAppendix)...")
    try:
        from bias_analysis.algorithm_audit import run_full_audit
        legacy = run_full_audit(n_sim=200, sample_n=1500)
        results['legacy_audit'] = {
            'simulation': legacy['simulation'].to_dict(orient='records') if not legacy['simulation'].empty else [],
            'decomposition': legacy['decomposition'].to_dict(orient='records') if not legacy['decomposition'].empty else [],
            'counterfactual': legacy['counterfactual'].to_dict(orient='records') if not legacy['counterfactual'].empty else [],
            'regression': legacy['regression'],
        }
        print("  Legacy audit complete.")
    except Exception as e:
        print(f"  Legacy audit skipped: {e}")
        results['legacy_audit'] = {'error': str(e)}

    try:
        from pipeline.disparity_analysis import build_disparity_dataset, run_ols_disparity_regression
        df = build_disparity_dataset(use_individual_level=False)
        reg = run_ols_disparity_regression(df)
        results['legacy_regression'] = reg
        print("  Legacy regression complete.")
    except Exception as e:
        print(f"  Legacy regression skipped: {e}")

    # --- Step 4: G2211 visit complexity validation ---
    print("\n\n[4/5] G2211 visit complexity validation...")
    try:
        from bias_analysis.g2211_validation import run_g2211_validation
        g2211_results = run_g2211_validation()
        results['g2211_validation'] = g2211_results

        # Save G2211 results separately
        with open(output_dir / 'g2211_validation_results.json', 'w') as f:
            json.dump(g2211_results, f, indent=2, default=str)
        print(f"  Saved: {output_dir / 'g2211_validation_results.json'}")
    except FileNotFoundError as e:
        print(f"  G2211 validation skipped (data not yet extracted): {e}")
        print("  Run 'python data/stream_g2211.py' first, then re-run pipeline.")
        results['g2211_validation'] = {'error': str(e)}
    except Exception as e:
        print(f"  G2211 validation skipped: {e}")
        results['g2211_validation'] = {'error': str(e)}

    # --- Step 5: Save final combined results ---
    print("\n\n[5/5] Saving final results...")
    with open(output_dir / 'improved_algorithm_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  Final results saved: {output_dir / 'improved_algorithm_results.json'}")

    # Print final summary
    s = results['summary']
    print(f"\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"  States analyzed:              {s['n_states']}")
    print(f"  ACS individuals:              {s['n_acs_individuals']:,}")
    print(f"  Status quo sensitivity:       {s['mean_sq_overall_sensitivity']:.1f}%")
    print(f"  Improved sensitivity:         {s['mean_imp_overall_sensitivity']:.1f}%")
    print(f"  Sensitivity gain:             +{s['mean_sensitivity_gain_pp']:.1f}pp")
    print(f"  B-W gap (status quo):         {s['mean_sq_bw_gap_pp']:.1f}pp")
    print(f"  B-W gap (improved):           {s['mean_imp_bw_gap_pp']:.1f}pp")
    print(f"  Gap reduction:                {s['mean_gap_reduction_pp']:.1f}pp ({s.get('mean_gap_reduction_pct', 0):.0f}%)")
    print(f"  Additional frail identified:  {s['total_additional_identified']:,}")
    print(f"  Coverage losses averted:      {s['total_coverage_losses_averted']:,}")


if __name__ == "__main__":
    main()
