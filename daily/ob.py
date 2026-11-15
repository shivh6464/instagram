# Port of slmbot.in ChartDock order-block rule (function Gn): swing t=2, displacement e=1.5 ATR(14), body>=60% of range
def order_blocks(n, t=2, e=1.5):
    s = len(n); i = s
    r = [ (max(c['h']-c['l'], abs(c['h']-n[u-1]['c']), abs(c['l']-n[u-1]['c'])) if u else c['h']-c['l']) for u, c in enumerate(n)]
    def atr(c):
        u = max(0, c-14); return (sum(r[u:c])/(c-u)) if c > u else r[c]
    o = []; h = a = None
    for c in range(t*2+1, i):
        u = c-1-t
        if u >= t:
            w = y = True
            for b in range(u-t, u+t+1):
                if n[b]['h'] > n[u]['h']: w = False
                if n[b]['l'] < n[u]['l']: y = False
            if w: h = dict(i=u, p=n[u]['h'], used=False)
            if y: a = dict(i=u, p=n[u]['l'], used=False)
        d = n[c]; f = d['h']-d['l']; g = abs(d['c']-d['o']); v = atr(c)
        if f >= e*v and f > 0 and g/f >= .6:
            if d['c'] > d['o'] and h and not h['used'] and d['c'] > h['p']:
                w = -1
                for yy in range(c-1, h['i'], -1):
                    if n[yy]['c'] < n[yy]['o']: w = yy; break
                if w < 0:
                    lo = float('inf')
                    for b in range(h['i']+1, c):
                        if n[b]['l'] < lo: lo = n[b]['l']; w = b
                if w >= 0: o.append(dict(dir=1, i=w, lo=n[w]['l'], hi=n[w]['h'], created=c, end=None, tests=0, gap=False))
                h['used'] = True
            elif d['c'] < d['o'] and a and not a['used'] and d['c'] < a['p']:
                w = -1
                for yy in range(c-1, a['i'], -1):
                    if n[yy]['c'] > n[yy]['o']: w = yy; break
                if w < 0:
                    hi = -float('inf')
                    for b in range(a['i']+1, c):
                        if n[b]['h'] > hi: hi = n[b]['h']; w = b
                if w >= 0: o.append(dict(dir=-1, i=w, lo=n[w]['l'], hi=n[w]['h'], created=c, end=None, tests=0, gap=False))
                a['used'] = True
    for ob in o:
        u = False
        for d in range(ob['created']+1, i):
            f = n[d]
            if ob['dir'] > 0:
                if f['c'] < ob['lo']: ob['end'] = d; ob['gap'] = f['o'] < ob['lo']; break
                if f['l'] <= ob['hi']:
                    if u: ob['tests'] += 1
                    u = False
                else: u = True
            else:
                if f['c'] > ob['hi']: ob['end'] = d; ob['gap'] = f['o'] > ob['hi']; break
                if f['h'] >= ob['lo']:
                    if u: ob['tests'] += 1
                    u = False
                else: u = True
        ob['status'] = ("gap broken" if ob['gap'] else "broken") if ob['end'] is not None else (("tested %d times" % ob['tests'] if ob['tests'] > 1 else "tested") if ob['tests'] else "untested")
    return o[-8:]
