"""KYBR cosmic design system — derived from the first carousel (Business Psychology).
Reusable for every future carousel/story. Import and call.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random, math

# ---------- TOKENS ----------
BG_DEEP   = (6, 11, 20)       # outer space
BG_MID    = (13, 23, 41)      # nebula core
WHITE     = (240, 245, 250)
ACCENT    = (140, 196, 240)   # light blue — italic headline, highlights
LABEL     = (98, 140, 186)    # letterspaced caps labels
MUTED     = (112, 134, 164)   # body sublines
RULE      = (52, 74, 104)     # thin dividers
CARD      = (16, 28, 48)      # panel fill
CARD_EDGE = (36, 56, 84)

GF = "/usr/share/fonts/truetype/google-fonts/"
PF = "/home/claude/fonts/"

def serif(size, weight="Bold", italic=False):
    p = PF + ("PlayfairDisplay-Italic[wght].ttf" if italic else "PlayfairDisplay[wght].ttf")
    f = ImageFont.truetype(p, size)
    f.set_variation_by_name(weight + (" Italic" if italic else ""))
    return f

def sans(size, w="Regular"):
    return ImageFont.truetype(GF + f"Poppins-{w}.ttf", size)

# ---------- TEXT ----------
def wrap(d, t, f, mw):
    ws, ls, cur = t.split(), [], ""
    for w_ in ws:
        tt = (cur + " " + w_).strip()
        if d.textlength(tt, font=f) <= mw: cur = tt
        else:
            if cur: ls.append(cur)
            cur = w_
    if cur: ls.append(cur)
    return ls

def dw(d, t, f, x, y, mw, fill, ls=1.28):
    lh = int(f.size * ls)
    lines = wrap(d, t, f, mw)
    for i, l in enumerate(lines): d.text((x, y + i*lh), l, font=f, fill=fill)
    return y + len(lines)*lh

def tracked(d, t, f, x, y, fill, track=6):
    """Letterspaced caps — the signature label style."""
    cx = x
    for ch in t:
        d.text((cx, y), ch, font=f, fill=fill)
        cx += d.textlength(ch, font=f) + track
    return cx

def tracked_w(d, t, f, track=6):
    return sum(d.textlength(c, font=f) + track for c in t) - track

# ---------- COSMIC BACKGROUND ----------
def _nebula(img, spots):
    lay = Image.new("RGB", img.size, BG_DEEP)
    dl = ImageDraw.Draw(lay)
    for (cx, cy, r, col) in spots:
        dl.ellipse([cx-r, cy-r, cx+r, cy+r], fill=col)
    lay = lay.filter(ImageFilter.GaussianBlur(190))
    return Image.blend(img, lay, 0.92)

def starfield(img, seed, n=170):
    rng = random.Random(seed)
    d = ImageDraw.Draw(img)
    W, H = img.size
    for _ in range(n):
        x, y = rng.randint(0, W), rng.randint(0, H)
        b = rng.choice([38, 55, 75, 95, 130, 170, 215])
        r = 1 if b < 120 else rng.choice([1, 1, 2])
        c = (b, int(b*1.03), min(255, int(b*1.15)))
        d.ellipse([x-r, y-r, x+r, y+r], fill=c)
    # a few 4-point sparkles
    for _ in range(5):
        x, y = rng.randint(60, W-60), rng.randint(60, H-60)
        s = rng.choice([7, 9, 12])
        c = (205, 222, 245)
        d.line([(x-s, y), (x+s, y)], fill=c, width=1)
        d.line([(x, y-s), (x, y+s)], fill=c, width=1)
    return img

def cosmos(W, H, seed=7, glow=None):
    """Base canvas: deep space + nebula + stars."""
    img = Image.new("RGB", (W, H), BG_DEEP)
    spots = glow if glow else [(int(W*0.28), int(H*0.24), int(W*0.42), BG_MID),
                               (int(W*0.86), int(H*0.14), int(W*0.30), (16, 30, 52))]
    img = _nebula(img, spots)
    return starfield(img, seed)

# ---------- MOTIFS ----------
def planet(img, cx, cy, r, ring=True):
    """Dark wireframe orb with ring + soft glow — top-right anchor motif."""
    W, H = img.size
    g = Image.new("RGBA", (W, H), (0,0,0,0)); dg = ImageDraw.Draw(g)
    dg.ellipse([cx-r*1.22, cy-r*1.22, cx+r*1.22, cy+r*1.22], fill=(30, 62, 104, 60))
    g = g.filter(ImageFilter.GaussianBlur(48))
    img.alpha_composite(g) if img.mode == "RGBA" else img.paste(
        Image.alpha_composite(img.convert("RGBA"), g).convert("RGB"), (0,0))

    o = Image.new("RGBA", (W, H), (0,0,0,0)); do = ImageDraw.Draw(o)
    # body: banded radial gradient
    steps = 46
    for i in range(steps, 0, -1):
        t = i/steps
        rr = r*t
        v = int(14 + 26*(1-t)**1.7)
        do.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], fill=(v, int(v*1.5), int(v*2.2), 255))
    # inner light bloom (upper-left)
    bl = Image.new("RGBA", (W, H), (0,0,0,0)); db = ImageDraw.Draw(bl)
    db.ellipse([cx-r*0.55, cy-r*0.72, cx+r*0.28, cy-r*0.02], fill=(60, 96, 140, 70))
    bl = bl.filter(ImageFilter.GaussianBlur(40))
    o.alpha_composite(bl)
    # wireframe geometry
    dw_ = ImageDraw.Draw(o)
    wc = (78, 118, 165, 92)
    pts = [(cx + r*0.72*math.cos(a), cy + r*0.72*math.sin(a))
           for a in [math.radians(x) for x in range(-90, 270, 60)]]
    dw_.polygon(pts, outline=wc)
    for i in range(len(pts)):
        dw_.line([pts[i], pts[(i+2) % len(pts)]], fill=(70, 108, 152, 60), width=1)
    dw_.ellipse([cx-r*0.72, cy-r*0.30, cx+r*0.72, cy+r*0.30], outline=(66, 102, 146, 70))
    dw_.line([(cx, cy-r*0.72), (cx, cy+r*0.72)], fill=(66, 102, 146, 55), width=1)
    # rim
    dw_.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(58, 92, 134, 120))
    if ring:
        dw_.ellipse([cx-r*1.42, cy-r*0.30, cx+r*1.42, cy+r*0.30], outline=(92, 138, 190, 110))
        dw_.ellipse([cx-r*1.38, cy-r*0.26, cx+r*1.38, cy+r*0.26], outline=(60, 96, 140, 70))
    base = img.convert("RGBA"); base.alpha_composite(o)
    return base.convert("RGB")

def crystal(img, cx, cy, h, glow=True):
    """Faceted blue crystal — the KYBR gem motif."""
    W, H = img.size
    w = h*0.30
    if glow:
        g = Image.new("RGBA", (W, H), (0,0,0,0)); dg = ImageDraw.Draw(g)
        dg.ellipse([cx-w*1.9, cy-h*0.72, cx+w*1.9, cy+h*0.72], fill=(96, 156, 214, 62))
        g = g.filter(ImageFilter.GaussianBlur(34))
        base = img.convert("RGBA"); base.alpha_composite(g); img = base.convert("RGB")
    o = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(o)
    top, bot = cy - h*0.5, cy + h*0.5
    sh_t, sh_b = cy - h*0.16, cy + h*0.20
    L, R = cx - w, cx + w
    # facets: left (bright), right (mid), lower-left, lower-right, top cap
    d.polygon([(cx, top), (L, sh_t), (L, sh_b), (cx, bot)], fill=(178, 214, 244, 255))
    d.polygon([(cx, top), (R, sh_t), (R, sh_b), (cx, bot)], fill=(104, 152, 200, 255))
    d.polygon([(cx, top), (L, sh_t), (cx, sh_t + h*0.06), (R, sh_t)], fill=(214, 236, 252, 255))
    d.polygon([(L, sh_b), (cx, bot), (R, sh_b), (cx, cy + h*0.30)], fill=(140, 184, 224, 255))
    d.line([(cx, top), (cx, bot)], fill=(232, 244, 254, 190), width=2)
    d.line([(L, sh_t), (L, sh_b)], fill=(206, 232, 250, 120), width=1)
    d.line([(R, sh_t), (R, sh_b)], fill=(150, 190, 228, 110), width=1)
    # sparkle
    sx, sy, s = cx - w*0.15, top + h*0.02, h*0.09
    d.line([(sx-s, sy), (sx+s, sy)], fill=(255,255,255,215), width=2)
    d.line([(sx, sy-s), (sx, sy+s)], fill=(255,255,255,215), width=2)
    base = img.convert("RGBA"); base.alpha_composite(o)
    return base.convert("RGB")

def vcheck(d, cx, cy, r):
    d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=ACCENT, width=2)
    w = max(3, r//5)
    d.line([(cx-r*0.42, cy+r*0.02), (cx-r*0.10, cy+r*0.38)], fill=ACCENT, width=w)
    d.line([(cx-r*0.10, cy+r*0.38), (cx+r*0.46, cy-r*0.34)], fill=ACCENT, width=w)

# ---------- CHROME ----------
def chrome(img, category, W, H, margin=80):
    """KYBR wordmark top-left + category top-right."""
    d = ImageDraw.Draw(img)
    tracked(d, "KYBR", serif(34, "Bold"), margin, margin - 8, ACCENT, track=7)
    f = sans(24, "Medium")
    w_ = tracked_w(d, category.upper(), f, track=5)
    tracked(d, category.upper(), f, W - margin - w_, margin - 2, LABEL, track=5)
    return d

def swipe_footer(img, W, H, text="SWIPE THROUGH", margin=80):
    d = ImageDraw.Draw(img)
    f = sans(24, "Medium")
    tw = tracked_w(d, text, f, track=5)
    x0 = margin
    y = H - margin - 6
    d.line([(x0, y+12), (x0+70, y+12)], fill=RULE, width=1)
    tracked(d, text, f, x0+92, y, LABEL, track=5)
    d.line([(x0+92+tw+22, y+12), (x0+92+tw+92, y+12)], fill=RULE, width=1)

def slide_footer(img, W, H, n, total, margin=80):
    """Handle + site + page pips for content slides."""
    d = ImageDraw.Draw(img)
    f = sans(26, "Medium")
    d.text((margin, H - margin - 8), "@kybr.me", font=f, fill=(74, 96, 126))
    t = "mykybr.ca"
    d.text((W - margin - d.textlength(t, font=f), H - margin - 8), t, font=f, fill=(74, 96, 126))
    pw, gap = 34, 12
    tw = total*pw + (total-1)*gap
    sx = (W - tw)//2
    for i in range(total):
        c = ACCENT if i == n-1 else (40, 58, 84)
        d.rounded_rectangle([sx+i*(pw+gap), H-margin-2, sx+i*(pw+gap)+pw, H-margin+4], 3, fill=c)
