"""Daily order-block chart post for @s_l_m_bot.
Usage: python3 chart_png.py SYMBOL bars.txt out.jpg caption.txt
bars.txt: one bar per line 'YYYY-MM-DD,o,h,l,c' (daily bars, oldest first, completed sessions only).
Draws the last ~90 sessions with the slmbot.in order-block rule, writes a 1080x1350 JPEG and a caption."""
import sys, os, datetime as dt
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ob import order_blocks

HERE = os.path.dirname(os.path.abspath(__file__)); F = HERE + "/fonts/"
def font(name, size): return ImageFont.truetype(F + name, size)
BG = (11, 10, 16); PANEL = (18, 17, 26); CREAM = (245, 230, 189); GOLD = (224, 192, 112); RED = (192, 80, 63)
MUT = (163, 154, 128); GRID = (42, 39, 51); GREEN = (79, 178, 134); GREEN_T = (127, 211, 172); RED_T = (224, 138, 124)

def rupee(v):  # Inter latin subset may lack the rupee glyph; use Rs.
    return f"Rs {v:,.1f}"

def render(sym, bars, out_jpg):
    n = bars; obs = order_blocks(n)
    START = max(0, len(n) - 90); v = n[START:]; N = len(v)
    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img, "RGBA")
    # header
    logo = Image.open(F + "logo.png").convert("RGBA").resize((86, 86))
    img.paste(logo, (60, 48), logo)
    d.text((164, 58), "SLM", font=font("Cormorant-600.ttf", 44), fill=CREAM)
    d.text((166, 108), "SMART LIQUIDITY MANAGEMENT", font=font("Inter-800.ttf", 18), fill=GOLD)
    d.text((60, 170), f"{sym} · daily order blocks", font=font("Cormorant-600.ttf", 70), fill=CREAM)
    last = n[-1]
    d.text((62, 258), f"Data to {last['t'].strftime('%d %b %Y')} close · last close {rupee(last['c'])}", font=font("Inter-500.ttf", 26), fill=MUT)
    # chart panel
    px0, py0, px1, py1 = 50, 310, 1030, 1040
    d.rounded_rectangle((px0, py0, px1, py1), 22, fill=PANEL, outline=(42, 38, 24), width=2)
    L, T, R, B = px0 + 20, py0 + 30, px1 - 120, py1 - 50
    vis = [o for o in obs if o['end'] is None or o['end'] >= START]
    lo = min(min(b['l'] for b in v), min([o['lo'] for o in vis] or [1e18])) ; hi = max(b['h'] for b in v)
    pad = (hi - lo) * 0.04; lo -= pad; hi += pad
    sp = (R - L) / N
    X = lambda i: L + (i - START + .5) * sp
    Y = lambda p: T + (hi - p) / (hi - lo) * (B - T)
    # grid + price labels
    import math
    raw = (hi - lo) / 6; mag = 10 ** math.floor(math.log10(raw)); step = min([1, 2, 2.5, 5, 10], key=lambda m: abs(m * mag - raw)) * mag
    p = math.ceil(lo / step) * step; fs = font("Inter-500.ttf", 20)
    while p < hi:
        y = Y(p); d.line((L, y, R, y), fill=GRID, width=1); d.text((R + 10, y - 12), f"{p:,.0f}" if step >= 1 else f"{p:,.1f}", font=fs, fill=MUT); p += step
    prev = None
    for i in range(START, len(n)):
        m = n[i]['t'].strftime('%b')
        if prev and m != prev: d.text((X(i) - 18, B + 12), m, font=fs, fill=MUT)
        prev = m
    # zones
    k = 0; legend = []
    for o in vis:
        k += 1; col = GREEN if o['dir'] > 0 else RED
        x0 = X(max(o['i'], START)) - sp / 2; x1 = X(o['end']) + sp / 2 if o['end'] is not None else R
        active = o['end'] is None
        d.rectangle((x0, Y(o['hi']), x1, Y(o['lo'])), fill=col + ((72,) if active else (30,)), outline=col + ((230,) if active else (110,)), width=2)
        o['k'] = k; legend.append(o)
    # candles
    for i in range(START, len(n)):
        b = n[i]; col = GOLD if b['c'] >= b['o'] else RED; x = X(i)
        d.line((x, Y(b['h']), x, Y(b['l'])), fill=col, width=2)
        top, bot = Y(max(b['o'], b['c'])), Y(min(b['o'], b['c']))
        if bot - top < 2: bot = top + 2
        d.rectangle((x - sp * .32, top, x + sp * .32, bot), fill=col)
    # markers
    fm = font("Inter-800.ttf", 17)
    for o in legend:
        col = GREEN_T if o['dir'] > 0 else RED_T
        cx = X(max(o['i'], START)) - sp / 2; cy = Y(o['lo']) + 16 if o['dir'] > 0 else Y(o['hi']) - 16
        d.ellipse((cx - 13, cy - 13, cx + 13, cy + 13), fill=col); d.text((cx, cy), str(o['k']), font=fm, fill=BG, anchor="mm")
    # last price tag
    y = Y(last['c'])
    for xx in range(int(L), int(R), 10): d.line((xx, y, xx + 4, y), fill=CREAM, width=1)
    d.rounded_rectangle((R + 4, y - 16, px1 - 8, y + 16), 6, fill=CREAM); d.text((R + 12, y), f"{last['c']:,.1f}", font=font("Inter-800.ttf", 19), fill=BG, anchor="lm")
    # legend
    ly = 1065; fl = font("Inter-500.ttf", 24); flb = font("Inter-800.ttf", 24)
    for o in legend[-5:]:
        col = GREEN_T if o['dir'] > 0 else RED_T; act = o['end'] is None
        d.ellipse((64, ly + 2, 90, ly + 28), fill=col); d.text((77, ly + 15), str(o['k']), font=fm, fill=BG, anchor="mm")
        d.text((104, ly), ("Bull OB (demand)" if o['dir'] > 0 else "Bear OB (supply)"), font=flb if act else fl, fill=CREAM if act else MUT)
        d.text((380, ly), f"{rupee(o['lo'])} – {rupee(o['hi'])}", font=flb, fill=col)
        d.text((720, ly), "ACTIVE" if act else o['status'], font=flb if act else fl, fill=CREAM if act else MUT)
        ly += 38
    d.line((60, 1268, 1020, 1268), fill=(80, 70, 40), width=1)
    d.text((540, 1292), "For educational purposes only. Not a buy or sell recommendation.", font=font("Inter-800.ttf", 25), fill=CREAM, anchor="mm")
    d.text((540, 1324), "Zones: SLM order-block rule on daily bars · slmbot.in · not SEBI-registered", font=font("Inter-500.ttf", 18), fill=MUT, anchor="mm")
    img.save(out_jpg, quality=92)
    return obs, legend

def caption(sym, bars, legend):
    last = bars[-1]; act = [o for o in legend if o['end'] is None]; brk = [o for o in legend if o['end'] is not None]
    hi20 = max(b['h'] for b in bars[-20:]); lo20 = min(b['l'] for b in bars[-20:])
    lines = [f"{sym} · Daily order blocks 📊", "",
             f"SLM order-block rule, daily chart (data to {last['t'].strftime('%d %b %Y')} close, last close ₹{last['c']:,.1f}):", ""]
    for o in act:
        lines.append(f"{'🟢 Active demand zone' if o['dir']>0 else '🔴 Active supply zone'}: ₹{o['lo']:,.1f} – ₹{o['hi']:,.1f} ({o['status']}, formed {bars[o['i']]['t'].strftime('%d %b')})")
    for o in brk[-2:]:
        lines.append(f"⚪ {'Demand' if o['dir']>0 else 'Supply'} zone ₹{o['lo']:,.1f} – ₹{o['hi']:,.1f}: {o['status']}")
    if not act: lines.append("⚪ Abhi koi active zone nahi: saare recent zones broken hain")
    lines += [f"📍 20-day range: ₹{lo20:,.1f} – ₹{hi20:,.1f}", "",
              "Rule: confirmed swing + 1.5× ATR displacement + last opposite candle = zone. Candle close through zone = broken.", "",
              "📩 DM karo 'SLM' → free Telegram group + charting tools ka link turant milega.",
              "💬 Comment mein next stock ka naam likho 👇", "Follow karo @s_l_m_bot, roz ek naya chart 📊", "",
              "⚠️ For educational purposes only. Not a buy or sell recommendation.",
              "SLM is not a SEBI-registered investment adviser or research analyst. Do your own research.", "",
              f"#{sym.lower()} #orderblocks #stockmarketindia #nifty50 #priceaction #smartmoneyconcepts #technicalanalysis #sharemarket #smartliquiditymanagement #slm"]
    return "\n".join(lines)

if __name__ == "__main__":
    sym, src, out, capf = sys.argv[1:5]
    bars = []
    for ln in open(src):
        ln = ln.strip()
        if not ln: continue
        t, o, h, l, c = ln.split(",")
        bars.append(dict(t=dt.date.fromisoformat(t), o=float(o), h=float(h), l=float(l), c=float(c)))
    obs, legend = render(sym, bars, out)
    open(capf, "w").write(caption(sym, bars, legend))
    print("ok", len(bars), "bars,", len(legend), "zones")
