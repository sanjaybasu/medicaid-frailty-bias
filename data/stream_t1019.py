"""
Stream T1019 Personal Care Services Billing Data
==================================================
Downloads and aggregates T1019 (Personal Care Services, per 15 minutes)
billing records from the real HHS Medicaid Provider Spending Dataset.

Source: HHS Medicaid Provider Spending Dataset (released February 2026)
Mirror: Hugging Face - cfahlgren1/medicaid-provider-spending
Data: 227 million billing records, NPI × HCPCS × Month, 2018-2024

This script:
1. Loads the billing_providers reference (617K rows, ~37MB) to build NPI → state lookup
2. Streams the spending split (227M rows) and collects T1019 records (~7% = ~16M rows)
3. Aggregates by state × month and saves to data/t1019_by_state_month.parquet

Runtime: approximately 8-10 minutes on standard connection
Output size: ~500KB parquet file (state-month aggregated)

Usage:
    python3 research/data/stream_t1019.py

Note: Requires `datasets` library (pip install datasets)
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
OUTPUT_FILE = DATA_DIR / "t1019_by_state_month.parquet"
BILLING_PROVIDERS_FILE = DATA_DIR / "billing_providers.parquet"


def load_npi_state_lookup() -> dict:
    """Load or download the NPI → state mapping."""
    if BILLING_PROVIDERS_FILE.exists():
        print(f"Loading billing providers from {BILLING_PROVIDERS_FILE}...")
        bp_df = pd.read_parquet(BILLING_PROVIDERS_FILE)
    else:
        print("Downloading billing providers from Hugging Face...")
        billing = load_dataset(
            "cfahlgren1/medicaid-provider-spending",
            data_files={"billing_providers": "billing-providers.parquet"},
            split="billing_providers"
        )
        bp_df = billing.to_pandas()
        bp_df.to_parquet(BILLING_PROVIDERS_FILE, index=False)
        print(f"Saved to {BILLING_PROVIDERS_FILE}")

    npi_state = dict(zip(bp_df['npi'].astype(str), bp_df['state']))
    print(f"Loaded {len(npi_state):,} NPI → state mappings")
    return npi_state


def stream_and_aggregate_t1019(npi_state: dict) -> pd.DataFrame:
    """
    Stream the spending dataset and aggregate T1019 by state × month.

    Each row in the spending dataset represents:
        (BILLING_PROVIDER_NPI, SERVICING_PROVIDER_NPI, HCPCS_CODE, MONTH):
        total_unique_beneficiaries, total_claims, total_paid

    We filter for HCPCS_CODE == 'T1019' and aggregate by:
        (state [from billing provider NPI], month)
    """
    print("\nStreaming spending data for T1019 records...")
    print("(This will scan 227M rows — estimated 8-10 minutes)\n")

    ds = load_dataset(
        "cfahlgren1/medicaid-provider-spending",
        data_files={"spending": "medicaid-provider-spending.parquet"},
        split="spending",
        streaming=True
    )

    # Accumulate by state × month
    agg: dict = defaultdict(lambda: defaultdict(lambda: {
        'beneficiaries': 0, 'claims': 0, 'paid': 0.0, 'n_providers': 0
    }))

    n_scanned = 0
    n_t1019 = 0
    n_no_state = 0

    for record in ds:
        n_scanned += 1

        if record['HCPCS_CODE'] != 'T1019':
            continue

        npi = str(record['BILLING_PROVIDER_NPI_NUM'])
        state = npi_state.get(npi)
        if state is None:
            n_no_state += 1
            continue

        month = record['CLAIM_FROM_MONTH']
        agg[state][month]['beneficiaries'] += record['TOTAL_UNIQUE_BENEFICIARIES'] or 0
        agg[state][month]['claims'] += record['TOTAL_CLAIMS'] or 0
        agg[state][month]['paid'] += record['TOTAL_PAID'] or 0.0
        agg[state][month]['n_providers'] += 1
        n_t1019 += 1

        if n_scanned % 10_000_000 == 0:
            pct = n_scanned / 227_083_361 * 100
            print(f"  {n_scanned/1e6:.0f}M rows ({pct:.1f}%) | "
                  f"{n_t1019:,} T1019 rows | {len(agg)} states")

    print(f"\nDone. Scanned {n_scanned:,} rows, found {n_t1019:,} T1019 rows")
    print(f"No state match (NPI not in billing_providers): {n_no_state:,}")

    # Convert to DataFrame
    rows = []
    for state, months in agg.items():
        for month, vals in months.items():
            rows.append({'state': state, 'month': month, **vals})

    df = pd.DataFrame(rows)
    df['month'] = pd.to_datetime(df['month'] + '-01')
    df = df.sort_values(['state', 'month'])
    return df


def main():
    print("=" * 60)
    print("HHS Medicaid T1019 Personal Care Streaming Pipeline")
    print("Source: cfahlgren1/medicaid-provider-spending (HF)")
    print("=" * 60 + "\n")

    # Step 1: NPI → state lookup
    npi_state = load_npi_state_lookup()

    # Step 2: Stream and aggregate
    df = stream_and_aggregate_t1019(npi_state)

    # Step 3: Save
    df.to_parquet(OUTPUT_FILE, index=False)
    print(f"\nSaved {len(df):,} state-month rows to {OUTPUT_FILE}")
    print(f"Total T1019 paid: ${df['paid'].sum():,.0f}")
    print(f"Date range: {df['month'].min().date()} to {df['month'].max().date()}")
    print("\nTop states by T1019 spending:")
    print(
        df.groupby('state')['paid'].sum()
        .sort_values(ascending=False)
        .head(10)
        .apply(lambda x: f"${x:,.0f}")
        .to_string()
    )


if __name__ == "__main__":
    main()
