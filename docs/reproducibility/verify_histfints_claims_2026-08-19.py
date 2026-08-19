import sqlite3, statistics, math
from pathlib import Path
from collections import defaultdict

HISTFINTS_DB = Path(r'C:\Users\CarlonTinto\AppData\Local\histfints\histfints\histfints.db')
conn = sqlite3.connect(f'file:{HISTFINTS_DB}?mode=ro', uri=True)
conn.row_factory = sqlite3.Row

# real underlying ids (found via label search + price-plausibility, F-033 investigation)
REAL_UNDERLYING = {'MU':(11323,6672),'MSFT':(11324,6602),'AMD':(11325,426),'MELI':(11326,6319),
                    'QQQ':(11328,8193),'AMZN':(11329,484),'NU':(11327,7085)}
# corrupted FK target ids (series.underlying_series_id, documented in F-033 as duplicate-of-self)
FK_UNDERLYING = {}
for tk,(cid,_) in REAL_UNDERLYING.items():
    r = conn.execute("SELECT underlying_series_id FROM series WHERE id=?", (cid,)).fetchone()
    FK_UNDERLYING[tk] = (cid, r['underlying_series_id'])

print("="*130)
print("CLAIM CHECK 1: does the FK (series.underlying_series_id) equal the REAL underlying I used?")
print("="*130)
for tk,(cid,uid) in REAL_UNDERLYING.items():
    fk = FK_UNDERLYING[tk][1]
    print(f"  {tk}: real_underlying_used={uid}  FK(series.underlying_series_id)={fk}  SAME? {uid==fk}")
print()

print("="*130)
print("CLAIM CHECK 2: implied FX on HistFinTS's 4 sample dates, FK-underlying vs REAL-underlying")
print("="*130)
sample_dates = ['2016-06-15','2020-03-16','2024-01-10','2026-05-27']
for d in sample_dates:
    print(f"--- {d} ---")
    for tk,(cid,uid) in REAL_UNDERLYING.items():
        fk = FK_UNDERLYING[tk][1]
        c = conn.execute("SELECT value FROM observation WHERE series_id=? AND DATE(observed_at)=?", (cid,d)).fetchone()
        u_real = conn.execute("SELECT value FROM observation WHERE series_id=? AND DATE(observed_at)=?", (uid,d)).fetchone()
        u_fk = conn.execute("SELECT value FROM observation WHERE series_id=? AND DATE(observed_at)=?", (fk,d)).fetchone() if fk else None
        if c:
            fx_real = c['value']/u_real['value'] if u_real else None
            fx_fk = c['value']/u_fk['value'] if u_fk else None
            print(f"    {tk}: cedear={c['value']:.2f}  fx(REAL underlying {uid})={fx_real}  fx(FK underlying {fk})={fx_fk}")
    print()
conn.close()
