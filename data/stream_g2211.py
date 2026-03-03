"""
Stream G2211 Visit Complexity Billing Data
============================================
Downloads and aggregates G2211 (Visit complexity inherent to E&M) billing
records from the HHS Medicaid Provider Spending Dataset.

G2211 is an add-on code introduced January 2024 for office/outpatient E&M
visits involving:
  - Medical care services that serve as the continuing focal point for all
    needed health care services, AND/OR
  - Medical care services related to a patient's single, serious condition
    or a complex condition

This code operationalizes "serious or complex" medical conditions in claims
data, providing an empirical anchor for the HR1 medical frailty exemption
criterion.

Source: HHS Medicaid Provider Spending Dataset (released February 2026)
Mirror: Hugging Face - cfahlgren1/medicaid-provider-spending
Data: 227 million billing records, NPI x HCPCS x Month, 2018-2024

Outputs:
    data/g2211_by_state_month.parquet  — State x month aggregates
    data/g2211_by_npi.parquet          — NPI-level totals (for specialty analysis)

Usage:
    python3 data/stream_g2211.py
"""

import sys
import pandas as pd
from collections import defaultdict
from pathlib import Path

try:
    from datasets import load_dataset
except ImportError:
    print("Error: 'datasets' library not installed. Run: pip install datasets")
    sys.exit(1)

DATA_DIR = Path(__file__).parent
OUTPUT_STATE = DATA_DIR / "g2211_by_state_month.parquet"
OUTPUT_NPI = DATA_DIR / "g2211_by_npi.parquet"
BILLING_PROVIDERS_FILE = DATA_DIR / "billing_providers.parquet"


def load_npi_lookup() -> tuple:
    """Load NPI -> state and NPI -> taxonomy mappings."""
    if not BILLING_PROVIDERS_FILE.exists():
        print("Downloading billing providers from Hugging Face...")
        billing = load_dataset(
            "cfahlgren1/medicaid-provider-spending",
            data_files={"billing_providers": "billing-providers.parquet"},
            split="billing_providers"
        )
        bp_df = billing.to_pandas()
        bp_df.to_parquet(BILLING_PROVIDERS_FILE, index=False)
    else:
        bp_df = pd.read_parquet(BILLING_PROVIDERS_FILE)

    npi_state = dict(zip(bp_df['npi'].astype(str), bp_df['state']))
    npi_taxonomy = dict(zip(bp_df['npi'].astype(str), bp_df['taxonomy_code'].fillna('')))
    print(f"Loaded {len(npi_state):,} NPI mappings")
    return npi_state, npi_taxonomy


def stream_g2211(npi_state: dict) -> tuple:
    """
    Stream the spending dataset and extract G2211 records.

    Returns:
        state_month_df: state x month aggregates
        npi_df: NPI-level totals for specialty analysis
    """
    print("\nStreaming spending data for G2211 records...")
    print("(Scanning 227M rows — estimated 8-10 minutes)\n")

    ds = load_dataset(
        "cfahlgren1/medicaid-provider-spending",
        data_files={"spending": "medicaid-provider-spending.parquet"},
        split="spending",
        streaming=True
    )

    # State x month aggregates
    state_agg: dict = defaultdict(lambda: defaultdict(lambda: {
        'beneficiaries': 0, 'claims': 0, 'paid': 0.0, 'n_providers': 0
    }))

    # NPI-level totals
    npi_agg: dict = defaultdict(lambda: {
        'beneficiaries': 0, 'claims': 0, 'paid': 0.0, 'n_months': 0
    })

    n_scanned = 0
    n_g2211 = 0
    n_no_state = 0

    for record in ds:
        n_scanned += 1

        if record['HCPCS_CODE'] != 'G2211':
            continue

        npi = str(record['BILLING_PROVIDER_NPI_NUM'])
        state = npi_state.get(npi)
        if state is None:
            n_no_state += 1
            continue

        month = record['CLAIM_FROM_MONTH']
        bene = record['TOTAL_UNIQUE_BENEFICIARIES'] or 0
        claims = record['TOTAL_CLAIMS'] or 0
        paid = record['TOTAL_PAID'] or 0.0

        state_agg[state][month]['beneficiaries'] += bene
        state_agg[state][month]['claims'] += claims
        state_agg[state][month]['paid'] += paid
        state_agg[state][month]['n_providers'] += 1

        npi_agg[npi]['beneficiaries'] += bene
        npi_agg[npi]['claims'] += claims
        npi_agg[npi]['paid'] += paid
        npi_agg[npi]['n_months'] += 1

        n_g2211 += 1

        if n_scanned % 10_000_000 == 0:
            pct = n_scanned / 227_083_361 * 100
            print(f"  {n_scanned/1e6:.0f}M rows ({pct:.1f}%) | "
                  f"{n_g2211:,} G2211 rows | {len(state_agg)} states | "
                  f"{len(npi_agg):,} unique NPIs")

    print(f"\nDone. Scanned {n_scanned:,} rows, found {n_g2211:,} G2211 rows")
    print(f"Unique NPIs billing G2211: {len(npi_agg):,}")
    print(f"States with G2211 billing: {len(state_agg)}")
    print(f"No state match: {n_no_state:,}")

    # Convert state aggregates to DataFrame
    state_rows = []
    for state, months in state_agg.items():
        for month, vals in months.items():
            state_rows.append({'state': state, 'month': month, **vals})
    state_df = pd.DataFrame(state_rows)
    if not state_df.empty:
        state_df['month'] = pd.to_datetime(state_df['month'] + '-01')
        state_df = state_df.sort_values(['state', 'month'])

    # Convert NPI aggregates to DataFrame
    npi_rows = [{'npi': npi, **vals} for npi, vals in npi_agg.items()]
    npi_df = pd.DataFrame(npi_rows)

    return state_df, npi_df


def main():
    print("=" * 60)
    print("HHS Medicaid G2211 Visit Complexity Streaming Pipeline")
    print("Source: cfahlgren1/medicaid-provider-spending (HF)")
    print("=" * 60 + "\n")

    npi_state, npi_taxonomy = load_npi_lookup()
    state_df, npi_df = stream_g2211(npi_state)

    # Add taxonomy codes to NPI-level data
    if not npi_df.empty:
        npi_df['taxonomy_code'] = npi_df['npi'].map(npi_taxonomy)
        npi_df['state'] = npi_df['npi'].map(npi_state)

    # Save
    if not state_df.empty:
        state_df.to_parquet(OUTPUT_STATE, index=False)
        print(f"\nSaved {len(state_df):,} state-month rows to {OUTPUT_STATE}")
    else:
        print("\nWARNING: No G2211 records found (code introduced Jan 2024)")

    if not npi_df.empty:
        npi_df.to_parquet(OUTPUT_NPI, index=False)
        print(f"Saved {len(npi_df):,} NPI-level rows to {OUTPUT_NPI}")

    # Summary
    if not state_df.empty:
        print(f"\nTotal G2211 paid: ${state_df['paid'].sum():,.0f}")
        print(f"Date range: {state_df['month'].min().date()} to {state_df['month'].max().date()}")
        print("\nTop 10 states by G2211 claims:")
        print(
            state_df.groupby('state')['claims'].sum()
            .sort_values(ascending=False)
            .head(10)
            .apply(lambda x: f"{x:,}")
            .to_string()
        )

    if not npi_df.empty:
        print(f"\nTop 10 taxonomies billing G2211:")
        tax_summary = (
            npi_df.groupby('taxonomy_code')
            .agg(n_providers=('npi', 'count'), total_claims=('claims', 'sum'))
            .sort_values('n_providers', ascending=False)
            .head(10)
        )
        print(tax_summary.to_string())


if __name__ == "__main__":
    main()
