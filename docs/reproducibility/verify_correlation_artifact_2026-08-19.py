import sqlite3, statistics, math
from pathlib import Path
from collections import defaultdict

HISTFINTS_DB = Path(r'C:\Users\CarlonTinto\AppData\Local\histfints\histfints\histfints.db')
conn = sqlite3.connect(f'file:{HISTFINTS_DB}?mode=ro', uri=True)
conn.row_factory = sqlite3.Row

REAL_UNDERLYING = {'MU':(11323,6672),'MSFT':(11324,6602),'AMD':(11325,426),'MELI':(11326,6319),
                    'QQQ':(11328,8193),'AMZN':(11329,484),'NU':(11327,7085)}
SIX = ['MU','MSFT','AMD','MELI','AMZN','NU']

def daily_last(sid):
    rows = conn.execute('''SELECT DATE(observed_at) d, value, observed_at FROM observation
                            WHERE series_id=? ORDER BY observed_at''', (sid,)).fetchall()
    out = {}
    for r in rows:
        if r['value'] is not None:
            out[r['d']] = r['value']  # ascending -> last write wins (date-only join, day-dedup)
    return out

cedear = {tk: daily_last(cid) for tk,(cid,uid) in REAL_UNDERLYING.items()}
underlying = {tk: daily_last(uid) for tk,(cid,uid) in REAL_UNDERLYING.items()}

WINDOW_START='2026-05-29'
ifx = {}
for tk in REAL_UNDERLYING:
    ced, und = cedear[tk], underlying[tk]
    common = sorted(d for d in set(ced)&set(und) if d>=WINDOW_START)
    ifx[tk] = {d: ced[d]/und[d] for d in common}

common_dates = sorted(set.intersection(*[set(ifx[tk]) for tk in SIX]))
print(f"Common live-window dates (date-only join): {len(common_dates)}  {common_dates[0]}..{common_dates[-1]}")
print(f"Is 2026-08-18 included? {'2026-08-18' in common_dates}")
print()

def corr(a,b):
    n=len(a); ma=sum(a)/n; mb=sum(b)/n
    cov=sum((a[i]-ma)*(b[i]-mb) for i in range(n))
    va=sum((x-ma)**2 for x in a); vb=sum((x-mb)**2 for x in b)
    return cov/math.sqrt(va*vb) if va and vb else 0

def pct_changes(dates):
    out={}
    for tk in SIX:
        vals=[ifx[tk][d] for d in dates]
        out[tk]=[(vals[i]-vals[i-1])/vals[i-1] for i in range(1,len(vals))]
    return out

for label, dates in [
    ("A: date-only join, INCLUDING 2026-08-18 (original script)", common_dates),
    ("B: date-only join, EXCLUDING 2026-08-18", [d for d in common_dates if d!='2026-08-18']),
]:
    pct = pct_changes(dates)
    corrs=[]
    for i,a in enumerate(SIX):
        for b in SIX[i+1:]:
            corrs.append(corr(pct[a],pct[b]))
    cs=sorted(corrs)
    print(f"{label}")
    print(f"  n_dates={len(dates)}  pairwise correlations: min={min(cs):.4f} median={statistics.median(cs):.4f} max={max(cs):.4f}")
    print()

# Show the day-over-day % change specifically around 2026-08-18 to see the shock magnitude
print("Day-over-day %% change around 2026-08-17 -> 2026-08-18 (date-only, day-deduped):")
for tk in SIX:
    d_prev = [d for d in common_dates if d < '2026-08-18'][-1]
    d_this = '2026-08-18'
    v0, v1 = ifx[tk][d_prev], ifx[tk][d_this]
    print(f"  {tk}: {d_prev}={v0:.4f} -> {d_this}={v1:.4f}  change={((v1-v0)/v0)*100:+.1f}%")

conn.close()
