import json
DUR = 383.25
raw = open('/home/user/toclose/work/pausas_raw.txt').read().splitlines()
tok = []
for line in raw:
    k, v = line.split(': ')
    tok.append((k.strip(), float(v)))
sil, cur = [], None
for k, v in tok:
    if k == 'silence_start': cur = v
    elif k == 'silence_end' and cur is not None:
        sil.append((cur, v)); cur = None
cuts = [(a + b) / 2 for a, b in sil]
TARGET, MINLEN, MAXLEN = 19.0, 9.0, 24.0
segs, start, last = [], 0.0, 0.0
for c in cuts:
    if c - start >= MAXLEN or (c - last >= MINLEN and c - start >= TARGET):
        segs.append((start, c)); start = c; last = c
segs[-1] = (segs[-1][0], DUR)
out = [{"id": i+1, "t0": round(a,2), "t1": round(b,2), "dur": round(b-a,2)} for i,(a,b) in enumerate(segs)]
json.dump(out, open('/home/user/toclose/work/timeline.json','w'), indent=1)
print("pausas:", len(sil), "| segmentos:", len(out))
print("soma: %.2f s (áudio %.2f)" % (sum(s['dur'] for s in out), DUR))
print("min/max: %.2f / %.2f" % (min(s['dur'] for s in out), max(s['dur'] for s in out)))
for s in out: print("  cena %2d  %7.2f -> %7.2f  (%5.2fs)" % (s['id'], s['t0'], s['t1'], s['dur']))
