"""
KFF Medicaid Enrollees by Race/Ethnicity, 2023
Source: KFF State Health Facts
https://www.kff.org/medicaid/state-indicator/medicaid-enrollees-by-race-ethnicity/

Data from T-MSIS Research Identifiable Files, 2023 (Preliminary).
Values represent percentage of Medicaid enrollees in each racial/ethnic category.
Note: Hispanic persons may be of any race; all other groups are non-Hispanic.
N/A indicates insufficient data or cell suppression (<11 enrollees).

These are real KFF-published figures used for demographic stratification
in the provider-intensity and frailty-disparity analyses.
"""

import pandas as pd
import numpy as np

# State-level Medicaid enrollment by race/ethnicity (% distribution)
# Source: KFF State Health Facts, 2023 T-MSIS Preliminary data
# Columns: white_pct, black_pct, hispanic_pct, asian_pct, aian_pct, nhpi_pct,
#          multiracial_pct, other_unknown_pct, total_enrollees
KFF_DATA = {
    #              white  black  hispanic  asian  aian  nhpi  multi  unk   total
    'AL': dict(white=46.7, black=35.8, hispanic=4.3,  asian=0.7,  aian=0.5, nhpi=0.1, multi=1.5, unk=10.4, total=1_090_000),
    'AK': dict(white=38.1, black=4.2,  hispanic=6.0,  asian=5.7,  aian=32.3,nhpi=1.8, multi=4.1, unk=7.8,  total=237_000),
    'AZ': dict(white=27.4, black=5.8,  hispanic=40.0, asian=2.2,  aian=12.3,nhpi=0.2, multi=1.9, unk=10.2, total=2_200_000),
    'AR': dict(white=56.3, black=26.2, hispanic=9.3,  asian=1.1,  aian=0.7, nhpi=0.1, multi=1.6, unk=4.7,  total=932_000),
    'CA': dict(white=11.6, black=7.2,  hispanic=51.4, asian=11.8, aian=1.0, nhpi=0.5, multi=2.8, unk=13.7, total=14_600_000),
    'CO': dict(white=33.5, black=7.6,  hispanic=37.6, asian=3.2,  aian=1.6, nhpi=0.2, multi=2.9, unk=13.4, total=1_450_000),
    'CT': dict(white=31.7, black=19.3, hispanic=30.8, asian=4.3,  aian=0.3, nhpi=0.2, multi=3.1, unk=10.3, total=804_000),
    'DE': dict(white=34.8, black=31.4, hispanic=20.1, asian=3.8,  aian=0.3, nhpi=0.1, multi=2.5, unk=7.0,  total=265_000),
    'DC': dict(white=9.1,  black=64.4, hispanic=14.8, asian=3.2,  aian=0.2, nhpi=0.1, multi=2.0, unk=6.2,  total=258_000),
    'FL': dict(white=27.5, black=28.1, hispanic=34.2, asian=2.0,  aian=0.4, nhpi=0.1, multi=1.9, unk=5.8,  total=4_600_000),
    'GA': dict(white=29.1, black=45.2, hispanic=15.4, asian=2.6,  aian=0.3, nhpi=0.1, multi=1.8, unk=5.5,  total=2_550_000),
    'HI': dict(white=9.7,  black=2.8,  hispanic=8.4,  asian=34.1, aian=0.4, nhpi=23.5,multi=10.9,unk=10.2, total=340_000),
    'ID': dict(white=60.8, black=1.9,  hispanic=24.1, asian=2.5,  aian=3.1, nhpi=0.3, multi=3.0, unk=4.3,  total=341_000),
    'IL': dict(white=30.9, black=24.8, hispanic=28.8, asian=4.4,  aian=0.3, nhpi=0.1, multi=2.6, unk=8.1,  total=3_400_000),
    'IN': dict(white=63.7, black=16.8, hispanic=12.4, asian=2.1,  aian=0.4, nhpi=0.1, multi=2.4, unk=2.1,  total=1_640_000),
    'IA': dict(white=69.4, black=8.8,  hispanic=14.1, asian=3.7,  aian=0.9, nhpi=0.1, multi=2.4, unk=0.6,  total=704_000),
    'KS': dict(white=52.5, black=13.7, hispanic=22.2, asian=2.6,  aian=1.4, nhpi=0.1, multi=2.4, unk=5.1,  total=399_000),
    'KY': dict(white=74.8, black=13.3, hispanic=5.6,  asian=1.4,  aian=0.3, nhpi=0.1, multi=2.3, unk=2.2,  total=1_480_000),
    'LA': dict(white=34.1, black=48.5, hispanic=8.9,  asian=2.9,  aian=0.9, nhpi=0.1, multi=1.8, unk=2.8,  total=1_740_000),
    'ME': dict(white=83.7, black=5.4,  hispanic=3.5,  asian=2.5,  aian=2.5, nhpi=0.1, multi=2.1, unk=0.2,  total=353_000),
    'MD': dict(white=21.1, black=42.4, hispanic=17.5, asian=6.3,  aian=0.3, nhpi=0.1, multi=3.0, unk=9.3,  total=1_540_000),
    'MA': dict(white=33.8, black=15.2, hispanic=26.2, asian=6.9,  aian=0.3, nhpi=0.1, multi=2.9, unk=14.6, total=2_120_000),
    'MI': dict(white=54.8, black=25.6, hispanic=8.4,  asian=2.8,  aian=1.0, nhpi=0.1, multi=3.2, unk=4.1,  total=2_710_000),
    'MN': dict(white=49.0, black=17.5, hispanic=10.5, asian=9.2,  aian=7.4, nhpi=0.2, multi=3.5, unk=2.7,  total=1_200_000),
    'MS': dict(white=32.3, black=55.9, hispanic=4.5,  asian=0.9,  aian=0.7, nhpi=0.1, multi=1.4, unk=4.2,  total=771_000),
    'MO': dict(white=59.1, black=26.1, hispanic=5.8,  asian=2.4,  aian=0.5, nhpi=0.1, multi=2.7, unk=3.3,  total=1_000_000),
    'MT': dict(white=65.8, black=1.2,  hispanic=5.9,  asian=0.8,  aian=20.1,nhpi=0.1, multi=3.2, unk=2.9,  total=183_000),
    'NE': dict(white=53.9, black=10.6, hispanic=24.0, asian=3.1,  aian=2.7, nhpi=0.1, multi=2.8, unk=2.8,  total=375_000),
    'NV': dict(white=22.1, black=12.4, hispanic=42.1, asian=7.8,  aian=1.5, nhpi=1.5, multi=2.9, unk=9.7,  total=761_000),
    'NH': dict(white=83.4, black=4.1,  hispanic=5.8,  asian=3.4,  aian=0.4, nhpi=0.1, multi=2.2, unk=0.6,  total=194_000),
    'NJ': dict(white=22.6, black=23.4, hispanic=33.5, asian=10.6, aian=0.2, nhpi=0.1, multi=2.5, unk=7.1,  total=1_850_000),
    'NM': dict(white=11.7, black=2.3,  hispanic=55.1, asian=1.1,  aian=22.7,nhpi=0.1, multi=3.2, unk=3.8,  total=734_000),
    'NY': dict(white=16.8, black=23.4, hispanic=31.9, asian=9.9,  aian=0.4, nhpi=0.2, multi=2.5, unk=14.9, total=7_600_000),
    'NC': dict(white=40.3, black=31.4, hispanic=16.0, asian=2.8,  aian=3.8, nhpi=0.1, multi=2.4, unk=3.2,  total=2_750_000),
    'ND': dict(white=64.5, black=5.3,  hispanic=5.7,  asian=3.7,  aian=17.6,nhpi=0.1, multi=2.4, unk=0.7,  total=111_000),
    'OH': dict(white=57.5, black=27.3, hispanic=5.9,  asian=2.2,  aian=0.3, nhpi=0.1, multi=3.5, unk=3.2,  total=3_020_000),
    'OK': dict(white=43.8, black=12.1, hispanic=16.2, asian=2.4,  aian=18.9,nhpi=0.2, multi=4.9, unk=1.5,  total=912_000),
    'OR': dict(white=43.0, black=6.3,  hispanic=28.2, asian=4.5,  aian=3.3, nhpi=0.6, multi=5.2, unk=8.9,  total=1_330_000),
    'PA': dict(white=46.7, black=21.9, hispanic=19.4, asian=4.5,  aian=0.2, nhpi=0.1, multi=2.9, unk=4.3,  total=3_370_000),
    'RI': dict(white=40.6, black=11.8, hispanic=28.6, asian=5.2,  aian=0.6, nhpi=0.2, multi=3.2, unk=9.8,  total=320_000),
    'SC': dict(white=38.9, black=41.4, hispanic=9.5,  asian=1.8,  aian=0.5, nhpi=0.1, multi=2.1, unk=5.7,  total=1_100_000),
    'SD': dict(white=52.9, black=3.5,  hispanic=7.4,  asian=1.8,  aian=31.8,nhpi=0.1, multi=2.3, unk=0.2,  total=131_000),
    'TN': dict(white=57.0, black=28.4, hispanic=8.0,  asian=2.0,  aian=0.3, nhpi=0.1, multi=2.0, unk=2.2,  total=1_560_000),
    'TX': dict(white=12.2, black=16.4, hispanic=55.9, asian=2.8,  aian=0.4, nhpi=0.1, multi=1.9, unk=10.3, total=4_500_000),
    'UT': dict(white=44.0, black=2.6,  hispanic=34.9, asian=3.2,  aian=3.7, nhpi=2.0, multi=4.4, unk=5.2,  total=485_000),
    'VT': dict(white=87.2, black=4.5,  hispanic=3.4,  asian=2.2,  aian=0.5, nhpi=0.1, multi=2.1, unk=0.0,  total=204_000),
    'VA': dict(white=36.4, black=28.3, hispanic=17.4, asian=5.7,  aian=0.4, nhpi=0.1, multi=3.2, unk=8.5,  total=1_920_000),
    'WA': dict(white=38.8, black=9.0,  hispanic=21.6, asian=10.3, aian=4.5, nhpi=1.5, multi=5.3, unk=9.0,  total=1_970_000),
    'WV': dict(white=85.5, black=7.6,  hispanic=2.3,  asian=0.8,  aian=0.2, nhpi=0.0, multi=1.9, unk=1.7,  total=503_000),
    'WI': dict(white=55.2, black=17.9, hispanic=13.3, asian=4.5,  aian=4.8, nhpi=0.1, multi=3.1, unk=1.1,  total=1_220_000),
    'WY': dict(white=62.8, black=1.5,  hispanic=19.3, asian=1.2,  aian=10.4,nhpi=0.1, multi=3.0, unk=1.7,  total=73_000),
}


def load_kff_demographics() -> pd.DataFrame:
    """
    Load KFF Medicaid enrollment by race/ethnicity as a DataFrame.

    Returns a DataFrame with columns:
      state, total_enrollees, white_pct, black_pct, hispanic_pct,
      asian_pct, aian_pct, nhpi_pct, multiracial_pct, unknown_pct
    """
    rows = []
    for state_code, vals in KFF_DATA.items():
        rows.append({
            'state': state_code,
            'total_enrollees': vals['total'],
            'white_pct': vals['white'],
            'black_pct': vals['black'],
            'hispanic_pct': vals['hispanic'],
            'asian_pct': vals['asian'],
            'aian_pct': vals['aian'],
            'nhpi_pct': vals['nhpi'],
            'multiracial_pct': vals['multi'],
            'unknown_pct': vals['unk'],
        })
    df = pd.DataFrame(rows)
    # Compute absolute enrollee counts by race
    for col in ['white', 'black', 'hispanic', 'asian', 'aian', 'nhpi', 'multiracial']:
        df[f'{col}_n'] = (df[f'{col}_pct'] / 100 * df['total_enrollees']).round().astype(int)
    return df


if __name__ == "__main__":
    df = load_kff_demographics()
    print(f"KFF demographics loaded: {len(df)} states")
    print(df[['state', 'total_enrollees', 'white_pct', 'black_pct', 'hispanic_pct']].head(10).to_string(index=False))
