#!/usr/bin/env python3
"""Full re-verification, 2026-08-19 state. Same methodology as the F-033 investigation:
day-dedup (last obs of day), real-underlying identification, provenance trace
(live .BA vs BACKFILL_*), machine-precision circularity test.
"""
import sqlite3, statistics
from pathlib import Path
from collections import defaultdict

HISTFINTS_DB = Path(r'C:\Users\CarlonTinto\AppData\Local\histfints\histfints\histfints.db')
conn = sqlite3.connect(f'file:{HISTFINTS_DB}?mode=ro', uri=True)
conn.row_factory = sqlite3.Row

# ticker -> (cedear_id, real_underlying_id, ratio)
PAIRS = {
    'AAPL': (11305, 33, 20.0),
    'BABA': (11316, 903, 1.0),
    'BIDU': (11317, 1169, 1.0),
    'UBER': (11319, 10165, 1.0),
    'GLD':  (11311, 2, 1.0),
    'MU':   (11323, 6672, 1.0),
    'MSFT': (11324, 6602, 1.0),
    'AMD':  (11325, 426, 1.0),
    'MELI': (11326, 6319, 1.0),
    'QQQ':  (11328, 8193, 1.0),
    'AMZN': (11329, 484, 1.0),
    'NU':   (11327, 7085, 1.0),
    'AZN':  (11354, 892, 1.0),
    'BBD':  (11355, 972, 1.0),
}

def daily_last(sid):
    """Last observation of each calendar day (dedup intraday), plus provider trace."""
    rows = conn.execute('''
        SELECT o.id, DATE(o.observed_at) d, o.value, o.observed_at, pa.priority, pa.provider_series_identifier
        FROM observation o
        JOIN import_run ir ON ir.id = o.import_run_id
        JOIN provider_assignment pa ON pa.id = ir.provider_assignment_id
        WHERE o.series_id=?
        ORDER BY o.observed_at
    ''', (sid,)).fetchall()
    out = {}
    for r in rows:
        if r['value'] is not None:
            out[r['d']] = {'value': r['value'], 'priority': r['priority'], 'ident': r['provider_series_identifier']}
    return out

print('='*140)
print('PART 1: PROVENANCE + COVERAGE, DAY-DEDUPED, 2026-08-19 STATE')
print('='*140)
cedear = {}
underlying = {}
for tk, (cid, uid, ratio) in PAIRS.items():
    cedear[tk] = daily_last(cid)
    underlying[tk] = daily_last(uid)
    dates = sorted(cedear[tk].keys())
    live = sum(1 for d in dates if cedear[tk][d]['priority'] == 1)
    backfill = sum(1 for d in dates if cedear[tk][d]['priority'] == 3)
    other = len(dates) - live - backfill
    print(f"{tk:<6} dedup_obs={len(dates):<6} range={dates[0]}..{dates[-1]:<12} "
          f"live(pri1)={live:<6} backfill(pri3)={backfill:<6} other_priority={other}")
print()

# ============================================================================
print('='*140)
print('PART 2: MACHINE-PRECISION CIRCULARITY TEST, BY PROVENANCE SEGMENT')
print('='*140)
print()

def implied_fx(tk):
    cid, uid, ratio = PAIRS[tk]
    ced, und = cedear[tk], underlying[tk]
    out = {}
    for d in sorted(set(ced) & set(und)):
        u = und[d]['value']
        if u:
            out[d] = {'fx': ced[d]['value'] / (u * ratio), 'priority': ced[d]['priority']}
    return out

ifx = {tk: implied_fx(tk) for tk in PAIRS}

# Segment: live-only dates (post live-fetch start) vs backfill-only dates
SIX_NEW = ['MU','MSFT','AMD','MELI','AMZN','NU']
for seg_name, seg_filter in [('LIVE (priority=1)', lambda p: p==1), ('BACKFILL (priority=3)', lambda p: p==3)]:
    print(f"--- Segment: {seg_name} ---")
    seg_dates = None
    for tk in SIX_NEW + ['QQQ']:
        d = {dt for dt, v in ifx[tk].items() if seg_filter(v['priority'])}
        seg_dates = d if seg_dates is None else (seg_dates & d)
    if not seg_dates:
        print("  no common dates in this segment across the 7 pairs")
        print()
        continue
    seg_dates = sorted(seg_dates)
    rel_ranges = []
    for d in seg_dates:
        vals = [ifx[tk][d]['fx'] for tk in SIX_NEW]  # six previously-blocked pairs only
        med = statistics.median(vals)
        rel_ranges.append((max(vals) - min(vals)) / med if med else 0)
    print(f"  common dates: {len(seg_dates)}  range: {seg_dates[0]}..{seg_dates[-1]}")
    print(f"  six-pair (MU/MSFT/AMD/MELI/AMZN/NU) internal relative range: mean={statistics.mean(rel_ranges):.6e} max={max(rel_ranges):.6e}")
    verdict = 'MACHINE-EPSILON (circular)' if max(rel_ranges) < 1e-8 else 'economically-scaled (independent)'
    print(f"  -> {verdict}")
    # QQQ vs six-pair median
    qqq_dev = []
    for d in seg_dates:
        vals6 = [ifx[tk][d]['fx'] for tk in SIX_NEW]
        med6 = statistics.median(vals6)
        if d in ifx['QQQ']:
            qqq_dev.append((ifx['QQQ'][d]['fx'] - med6) / med6)
    if qqq_dev:
        print(f"  QQQ deviation from six-pair median: mean={statistics.mean(qqq_dev):+.4f} stdev={statistics.stdev(qqq_dev) if len(qqq_dev)>1 else 0:.4f}")
    print()

# ============================================================================
print('='*140)
print('PART 3: CROSS-SECTIONAL IMPLIED-FX SNAPSHOT, LATEST DATE, ALL 14 PAIRS')
print('='*140)
print()
latest_common = sorted(set.intersection(*[set(ifx[tk]) for tk in PAIRS]))
if latest_common:
    d = latest_common[-1]
    print(f"Latest common date across all 14 pairs: {d}")
    vals = {tk: ifx[tk][d]['fx'] for tk in PAIRS}
    for tk, v in sorted(vals.items(), key=lambda x: x[1]):
        print(f"  {tk:<6} implied_fx={v:.4f}  (priority={ifx[tk][d]['priority']})")
    med = statistics.median(list(vals.values()))
    print(f"  median={med:.4f}")
else:
    print("No single date common to all 14 pairs.")
print()

conn.close()
print('Re-verification complete.')

print()
print('='*140)
print('PART 4: DIAGNOSTIC — IS THE SPREAD EXPLAINED BY A STALE-RATIO ISSUE (F-021 PATTERN)?')
print('='*140)
d = latest_common[-1]
vals_no_aapl = {tk: ifx[tk][d]['fx'] for tk in PAIRS if tk != 'AAPL'}
sv = sorted(vals_no_aapl.items(), key=lambda x: x[1])
print(f"Excluding AAPL (known F-021 stale-ratio risk: ratio=20 constant, undated, prior finding confirmed a real step at 2024-01-24):")
for tk, v in sv:
    print(f"  {tk:<6} {v:.4f}")
import statistics as st
vs = list(vals_no_aapl.values())
print(f"  range without AAPL: {min(vs):.2f} .. {max(vs):.2f}  (still {max(vs)/min(vs):.0f}x spread)")
