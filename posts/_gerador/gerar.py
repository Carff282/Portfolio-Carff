"""Gerador de carrosseis do @carffcode.

Uso:  python3 posts/_gerador/gerar.py conteudo.json pasta_saida/ [preview.jpg]
Gera 01.jpg, 02.jpg, ... (1080x1350, JPEG).

Dois visuais (campo "estilo" no topo do JSON):
  "escuro"  -> tela de editor de código (fundo escuro)
  "caderno" -> folha de caderno pautada, com fita adesiva no topo
Os dois recebem marcações "feitas à mão": marca-texto, anotações tortas, setas e círculos.
As linhas tremem de leve e mudam a cada post (semente = nome da pasta), então nenhum post sai idêntico.

Formato do JSON:
{
  "estilo": "caderno",                  # ou "escuro"
  "arquivo": "arquitetura.md",          # nome que aparece no topo
  "slides": [
    {"tipo": "capa", "kicker": "// sistema.design()", "titulo": "Antes de escrever código,",
     "destaque": "desenhe o sistema.", "subtitulo": "...", "chips": ["UI", "API"], "marcar": "sistema"},
    {"tipo": "colunas", "passo": 1, "kicker": "01 · ...", "titulo": "...", "colunas": [
        {"titulo": "...", "sub": "...", "itens": ["+ pró", "− contra", "item neutro"]}, {...}], "rodape": "..."},
    {"tipo": "pilha", "kicker": "...", "titulo": "...", "itens": [{"titulo": "...", "sub": "..."}], "rodape": "..."},
    {"tipo": "codigo", "kicker": "...", "titulo": "...", "codigo": "linha1\\nlinha2", "checks": ["...", "..."]},
    {"tipo": "grade", "kicker": "...", "titulo": "...", "itens": [{"titulo": "...", "sub": "..."}] (4), "rodape": "..."},
    {"tipo": "destaque", "kicker": "...", "titulo": "...", "texto": "...", "itens": ["...", "..."]},
    {"tipo": "fechamento", "kicker": "// resumo", "titulo": "...", "passos": ["...", "..."],
     "cta_titulo": "Salva pra consultar depois", "cta_texto": "e comenta: ..."}
  ]
}
Campos opcionais em QUALQUER slide (o toque humano):
  "marcar": "palavra"   -> passa marca-texto nessa palavra/trecho do título
  "nota": "texto curto" -> anotação à mão, torta, com seta, no espaço livre de baixo
                           (escreva como gente: "eu errei isso por anos", "isso aqui salva vidas")
  "circular": 2         -> (colunas/grade/pilha) circula à mão o item de índice N (começa em 0)
Use em 2 a 4 slides por post, não em todos. Mantenha textos curtos.
"""
import hashlib
import json
import math
import os
import random
import re
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
HANDLE = "@carffcode"
INTER = "/usr/share/fonts/opentype/inter/"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONOB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
HAND = "/usr/share/fonts/truetype/google-fonts/ofl/comicrelief/ComicRelief-Bold.ttf"

# bloco de código usa sempre a paleta escura (fica bem nos dois estilos)
C_BG, C_TXT, C_MUTED = (22, 27, 34), (230, 237, 243), (139, 148, 158)
C_GREEN, C_BLUE, C_PURPLE, C_ORANGE = (126, 231, 135), (121, 192, 255), (210, 168, 255), (255, 166, 87)

THEMES = {
    "escuro": dict(BG=(13, 17, 23), PANEL=(22, 27, 34), BORDER=(48, 54, 61), TXT=(230, 237, 243),
                   MUTED=(139, 148, 158), GREEN=(63, 185, 80), BLUE=(88, 166, 255), PURPLE=(188, 140, 255),
                   ORANGE=(255, 166, 87), PINK=(255, 123, 114), CALLOUT=(18, 38, 26),
                   MARKER=(250, 204, 21, 95), INK=(250, 204, 21), BOXW=3),
    "caderno": dict(BG=(248, 245, 237), PANEL=(255, 255, 252), BORDER=(45, 45, 50), TXT=(28, 28, 32),
                    MUTED=(105, 105, 112), GREEN=(21, 128, 61), BLUE=(29, 78, 216), PURPLE=(109, 40, 217),
                    ORANGE=(194, 65, 12), PINK=(190, 24, 93), CALLOUT=(236, 252, 203),
                    MARKER=(253, 224, 71, 150), INK=(29, 78, 216), BOXW=3),
}
T = {}


def set_theme(name):
    T.clear()
    T.update(THEMES[name])
    T["NAME"] = name
    T["ACCENTS"] = [T["BLUE"], T["PURPLE"], T["ORANGE"], T["GREEN"], T["PINK"]]


def inter(weight, size):
    return ImageFont.truetype(f"{INTER}Inter-{weight}.otf", size)


def mono(size, bold=False):
    return ImageFont.truetype(MONOB if bold else MONO, size)


def hand(size):
    return ImageFont.truetype(HAND, size)


def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def block(d, xy, text, font, fill, maxw, spacing=1.3):
    x, y = xy
    for line in wrap(d, text, font, maxw):
        d.text((x, y), line, font=font, fill=fill)
        y += int(font.size * spacing)
    return y


def fit_title(d, text, maxw, size=72, max_lines=3, weight="ExtraBold"):
    while size > 44:
        font = inter(weight, size)
        if len(wrap(d, text, font, maxw)) <= max_lines:
            return font
        size -= 4
    return inter(weight, size)


class Deck:
    def __init__(self, data, out):
        self.data = data
        self.out = out
        self.total = len(data["slides"])
        self.fname = data.get("arquivo", "post.md")
        seed = int(hashlib.md5(os.path.abspath(out).encode()).hexdigest()[:8], 16)
        self.rng = random.Random(seed)
        set_theme(data.get("estilo", "escuro"))
        os.makedirs(out, exist_ok=True)

    # ---------- traços "à mão" ----------
    def j(self, a=2.5):
        return self.rng.uniform(-a, a)

    def wobble(self, d, pts, color, width=4, jit=2.2):
        dense = []
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 18))
            for k in range(n):
                t = k / n
                dense.append((x0 + (x1 - x0) * t + self.j(jit), y0 + (y1 - y0) * t + self.j(jit)))
        dense.append(pts[-1])
        d.line(dense, fill=color, width=width, joint="curve")

    def hbox(self, d, xy, outline, width=None, fill=None):
        """retângulo com cantos levemente arredondados e bordas que tremem."""
        x0, y0, x1, y1 = xy
        if fill:
            d.rounded_rectangle(xy, radius=14, fill=fill)
        w = width or T["BOXW"]
        o = 3
        self.wobble(d, [(x0 + self.j(o), y0), (x1, y0 + self.j(o)), (x1 + self.j(o), y1),
                        (x0, y1 + self.j(o)), (x0 + self.j(o), y0 + self.j(o))], outline, w, 1.4)

    def circle(self, d, xy, color):
        x0, y0, x1, y1 = xy
        cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 + 18, (y1 - y0) / 2 + 14
        start = self.rng.uniform(0, math.pi * 2)
        pts = []
        for k in range(46):
            a = start + k / 40 * math.pi * 2  # passa um pouco da volta, como caneta
            r = 1 + self.j(0.03)
            pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
        d.line(pts, fill=color, width=5, joint="curve")

    def arrow(self, d, a, b, color):
        (x0, y0), (x1, y1) = a, b
        mx, my = (x0 + x1) / 2 + self.j(40), (y0 + y1) / 2 - 40
        pts = []
        for k in range(21):
            t = k / 20
            pts.append(((1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t * t * x1 + self.j(1.2),
                        (1 - t) ** 2 * y0 + 2 * (1 - t) * t * my + t * t * y1 + self.j(1.2)))
        d.line(pts, fill=color, width=5, joint="curve")
        ang = math.atan2(y1 - pts[-4][1], x1 - pts[-4][0])
        for s in (-1, 1):
            a2 = ang + math.pi + s * 0.45
            d.line([(x1, y1), (x1 + 30 * math.cos(a2) + self.j(), y1 + 30 * math.sin(a2) + self.j())], fill=color, width=5)

    def highlight(self, im, x0, y0, x1, y1):
        lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        h = y1 - y0
        top = y0 + h * 0.45
        ld.polygon([(x0 - 8 + self.j(), top + self.j(4)), (x1 + 10 + self.j(), top + self.j(4)),
                    (x1 + 6 + self.j(), y1 + 4 + self.j(3)), (x0 - 4 + self.j(), y1 + 2 + self.j(3))], fill=T["MARKER"])
        im.alpha_composite(lay)

    def note(self, im, d, text, y_min):
        f = hand(40)
        lines = wrap(d, text, f, 620)
        lh = 50
        th = lh * len(lines) + 20
        y = y_min + 40
        if y + th > H - 135:
            return
        tw = max(d.textlength(l, font=f) for l in lines) + 20
        lay = Image.new("RGBA", (int(tw) + 40, th + 40), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        for i, l in enumerate(lines):
            ld.text((20, 20 + i * lh), l, font=f, fill=T["INK"])
        lay = lay.rotate(self.rng.uniform(-5, -2), resample=Image.BICUBIC, expand=True)
        x = W - 80 - lay.width
        im.alpha_composite(lay, (int(x), int(y)))
        self.arrow(d, (x + 10, y + lay.height / 2), (x - 70 + self.j(10), y - 25), T["INK"])

    # ---------- base ----------
    def base(self, n, step=None, accent=None):
        accent = accent or T["GREEN"]
        im = Image.new("RGBA", (W, H), T["BG"] + (255,))
        d = ImageDraw.Draw(im)
        if T["NAME"] == "escuro":
            for gx in range(40, W, 40):
                for gy in range(40, H, 40):
                    d.point((gx, gy), fill=(28, 33, 40))
            d.rectangle([0, 0, W, 70], fill=T["PANEL"])
            d.line([0, 70, W, 70], fill=T["BORDER"], width=2)
            for i, c in enumerate([T["PINK"], T["ORANGE"], T["GREEN"]]):
                d.ellipse([36 + i * 34, 24, 58 + i * 34, 46], fill=c)
            d.text((160, 22), self.fname, font=mono(24), fill=T["MUTED"])
        else:
            for gy in range(120, H - 110, 46):
                d.line([0, gy, W, gy], fill=(214, 225, 238), width=2)
            d.line([46, 0, 46, H], fill=(239, 163, 163), width=2)
            # fita adesiva
            lay = Image.new("RGBA", (220, 60), (250, 230, 150, 170))
            lay = lay.rotate(self.rng.uniform(-6, 6), expand=True, resample=Image.BICUBIC)
            im.alpha_composite(lay, (W // 2 - lay.width // 2, -12))
            d.text((70, 28), self.fname, font=mono(24), fill=T["MUTED"])
        if step:
            lab = f"PASSO {int(step):02d}"
            d.text((W - 50 - d.textlength(lab, font=mono(24, True)), 28 if T["NAME"] == "caderno" else 22),
                   lab, font=mono(24, True), fill=accent)
        d.line([60, H - 110, W - 60, H - 110], fill=T["BORDER"] if T["NAME"] == "escuro" else (200, 200, 205), width=2)
        d.text((60, H - 82), HANDLE, font=mono(30, True), fill=T["TXT"])
        pg = f"{n}/{self.total}"
        d.text((W - 60 - d.textlength(pg, font=mono(28)), H - 80), pg, font=mono(28), fill=T["MUTED"])
        if n < self.total:
            a = "arrasta →"
            f = inter("Medium", 28)
            d.text(((W - d.textlength(a, font=f)) / 2, H - 80), a, font=f, fill=T["MUTED"])
        return im, d

    def title_lines(self, im, d, xy, text, font, fill, maxw, marcar=None, spacing=1.15):
        x, y = xy
        for line in wrap(d, text, font, maxw):
            if marcar and marcar.lower() in line.lower():
                i = line.lower().index(marcar.lower())
                x0 = x + d.textlength(line[:i], font=font)
                x1 = x0 + d.textlength(line[i:i + len(marcar)], font=font)
                self.highlight(im, x0, y, x1, y + font.size * 1.05)
            d.text((x, y), line, font=font, fill=fill)
            y += int(font.size * spacing)
        return y

    def heading(self, im, d, s, accent, y=150):
        d.text((70, y), s.get("kicker", ""), font=mono(30, True), fill=accent)
        font = fit_title(d, s["titulo"], W - 140)
        return self.title_lines(im, d, (70, y + 60), s["titulo"], font, T["TXT"], W - 140, s.get("marcar"))

    def footer_text(self, d, y, text):
        if text:
            return block(d, (70, y), text, inter("SemiBold", 36), T["TXT"], W - 140)
        return y

    # ---------- tipos ----------
    def capa(self, im, d, s, accent):
        d.text((70, 220), s.get("kicker", ""), font=mono(36), fill=T["GREEN"])
        big = fit_title(d, s["titulo"] + " " + s.get("destaque", ""), W - 140, size=92, max_lines=4)
        y = self.title_lines(im, d, (70, 300), s["titulo"], big, T["TXT"], W - 140, s.get("marcar"), 1.12)
        if s.get("destaque"):
            y = self.title_lines(im, d, (70, y), s["destaque"], big, T["GREEN"], W - 140, s.get("marcar"), 1.12)
        y += 50
        if s.get("subtitulo"):
            y = block(d, (70, y), s["subtitulo"], inter("Medium", 44), T["MUTED"], W - 140)
        chips = s.get("chips") or []
        if chips:
            cy = y + 90
            gap = 30
            bw = (W - 140 - gap * (len(chips) - 1)) // len(chips)
            for i, lab in enumerate(chips):
                c = T["ACCENTS"][i % 5]
                x = 70 + i * (bw + gap)
                self.hbox(d, [x, cy, x + bw, cy + 110], c, fill=T["PANEL"])
                f = mono(30, True)
                d.text((x + (bw - d.textlength(lab, font=f)) / 2, cy + 38), lab, font=f, fill=c)
            y = cy + 110
        return y

    def colunas(self, im, d, s, accent):
        y = self.heading(im, d, s, accent) + 50
        cw = (W - 140 - 40) // 2
        hmax = 560
        acc = T["ACCENTS"]
        for i, col in enumerate(s["colunas"][:2]):
            c = acc[(acc.index(accent) + i) % 5]
            x = 70 + i * (cw + 40)
            self.hbox(d, [x, y, x + cw, y + hmax], c, fill=T["PANEL"])
            yy = block(d, (x + 32, y + 32), col["titulo"], inter("Bold", 40), c, cw - 64, 1.15)
            if col.get("sub"):
                yy = block(d, (x + 32, yy + 4), col["sub"], inter("Medium", 28), T["MUTED"], cw - 64)
            yy += 24
            for it in col.get("itens", []):
                mark, txt, mc = "›", it, c
                if it[:2] in ("+ ", "− ", "- "):
                    mark, txt = it[0].replace("-", "−"), it[2:]
                    mc = T["GREEN"] if mark == "+" else T["PINK"]
                d.text((x + 32, yy), mark, font=mono(34, True), fill=mc)
                yy = block(d, (x + 70, yy + 2), txt, inter("Regular", 32), T["TXT"], cw - 102) + 22
            if s.get("circular") == i:
                self.circle(d, [x + 10, y + 10, x + cw - 10, y + 90], T["INK"])
        return self.footer_text(d, y + hmax + 50, s.get("rodape"))

    def pilha(self, im, d, s, accent):
        y = self.heading(im, d, s, accent) + 40
        items = s["itens"][:5]
        lh = 130 if len(items) <= 4 else 110
        gap = 34
        for i, it in enumerate(items):
            c = T["ACCENTS"][i % 5]
            yy = y + i * (lh + gap)
            self.hbox(d, [70, yy, W - 70, yy + lh], c, fill=T["PANEL"])
            d.rectangle([76, yy + 20, 86, yy + lh - 20], fill=c)
            d.text((115, yy + 22), it["titulo"], font=inter("Bold", 42), fill=c)
            if it.get("sub"):
                d.text((115, yy + lh - 50), it["sub"], font=mono(26), fill=T["MUTED"])
            if s.get("circular") == i:
                tw = d.textlength(it["titulo"], font=inter("Bold", 42))
                self.circle(d, [105, yy + 18, 125 + tw, yy + 72], T["INK"])
            if i < len(items) - 1:
                ax = W // 2 + self.j(6)
                self.wobble(d, [(ax, yy + lh + 4), (ax, yy + lh + gap - 6)], T["MUTED"], 3, 1)
        return self.footer_text(d, y + len(items) * (lh + gap) + 10, s.get("rodape"))

    TOKEN = re.compile(r"(//.*$|#.*$|'[^']*'|\"[^\"]*\"|`[^`]*`|\b\w+\b|\s+|.)")
    KW = {"const", "let", "var", "function", "return", "if", "else", "for", "while", "class", "interface",
          "type", "async", "await", "import", "from", "export", "new", "def", "true", "false", "null",
          "undefined", "string", "number", "boolean", "void", "try", "catch", "throw", "of", "in", "this"}

    def code_line(self, d, x, y, line, font):
        for m in self.TOKEN.finditer(line):
            t = m.group(0)
            rest = line[m.end():]
            if t.startswith("//") or t.startswith("#"):
                c = C_MUTED
            elif t[0] in "'\"`":
                c = C_GREEN
            elif t in self.KW:
                c = C_PURPLE
            elif re.fullmatch(r"\w+", t) and rest.lstrip().startswith("("):
                c = C_BLUE
            elif re.fullmatch(r"[A-Z]\w*|\d+", t):
                c = C_ORANGE
            else:
                c = C_TXT
            d.text((x, y), t, font=font, fill=c)
            x += d.textlength(t, font=font)

    def codigo(self, im, d, s, accent):
        y = self.heading(im, d, s, accent) + 45
        lines = s["codigo"].split("\n")[:11]
        longest = max(lines, key=len) if lines else ""
        size = 34
        while size > 22 and d.textlength(longest, font=mono(size)) > W - 220:
            size -= 2
        font = mono(size)
        lh = int(size * 1.7)
        hb = lh * len(lines) + 70
        d.rounded_rectangle([70, y, W - 70, y + hb], radius=18, fill=C_BG)
        for i, line in enumerate(lines):
            self.code_line(d, 110, y + 35 + i * lh, line, font)
        y += hb + 45
        for t in s.get("checks", [])[:3]:
            if y > H - 200:
                break
            d.text((70, y), "✓", font=mono(36, True), fill=T["GREEN"])
            y = block(d, (120, y + 2), t, inter("Medium", 34), T["TXT"], W - 190) + 20
        return y

    def grade(self, im, d, s, accent):
        y = self.heading(im, d, s, accent) + 50
        items = s["itens"][:4]
        cw = (W - 140 - 40) // 2
        ch = 250
        for i, it in enumerate(items):
            c = T["ACCENTS"][i % 5]
            x = 70 + (i % 2) * (cw + 40)
            yy = y + (i // 2) * (ch + 40)
            self.hbox(d, [x, yy, x + cw, yy + ch], c, fill=T["PANEL"])
            d.text((x + 32, yy + 36), it["titulo"], font=fit_title(d, it["titulo"], cw - 64, 44, 1, "Bold"), fill=c)
            block(d, (x + 32, yy + 115), it.get("sub", ""), inter("Regular", 30), T["TXT"], cw - 64)
            if s.get("circular") == i:
                tf = fit_title(d, it["titulo"], cw - 64, 44, 1, "Bold")
                self.circle(d, [x + 24, yy + 30, x + 40 + d.textlength(it["titulo"], font=tf), yy + 90], T["INK"])
        rows = (len(items) + 1) // 2
        return self.footer_text(d, y + rows * (ch + 40) + 20, s.get("rodape"))

    def destaque(self, im, d, s, accent):
        y = self.heading(im, d, s, accent) + 50
        if s.get("texto"):
            tf = inter("Bold", 40)
            lines = wrap(d, s["texto"], tf, W - 220)
            hb = len(lines) * 52 + 70
            self.hbox(d, [70, y, W - 70, y + hb], T["GREEN"], fill=T["CALLOUT"])
            block(d, (110, y + 35), s["texto"], tf, T["TXT"], W - 220)
            y += hb + 50
        for t in s.get("itens", [])[:5]:
            d.text((70, y), "›", font=mono(38, True), fill=accent)
            y = block(d, (115, y + 2), t, inter("Medium", 36), T["TXT"], W - 185) + 24
        return y

    def fechamento(self, im, d, s, accent):
        d.text((70, 230), s.get("kicker", "// resumo"), font=mono(36), fill=T["GREEN"])
        big = fit_title(d, s["titulo"], W - 140, size=88, max_lines=3)
        y = self.title_lines(im, d, (70, 300), s["titulo"], big, T["TXT"], W - 140, s.get("marcar"), 1.12) + 50
        for i, p in enumerate(s.get("passos", [])[:6]):
            c = T["ACCENTS"][i % 5]
            d.text((70, y), f"{i + 1:02d}", font=mono(36, True), fill=c)
            d.text((150, y - 2), p, font=inter("SemiBold", 40), fill=T["TXT"])
            y += 66
        y = min(y + 40, H - 340)
        self.hbox(d, [70, y, W - 70, y + 190], T["GREEN"], fill=T["CALLOUT"])
        d.text((110, y + 36), s.get("cta_titulo", "Salva pra consultar depois"), font=inter("Bold", 42), fill=T["GREEN"])
        block(d, (110, y + 100), s.get("cta_texto", "e comenta o que achou!"), inter("Medium", 36), T["TXT"], W - 220)
        return y + 190

    def render(self):
        paths = []
        for i, s in enumerate(self.data["slides"], 1):
            accent = T["ACCENTS"][(i - 2) % 5] if i > 1 else T["GREEN"]
            first_last = s["tipo"] in ("capa", "fechamento")
            im, d = self.base(i, None if first_last else s.get("passo"), accent)
            y_end = getattr(self, s["tipo"])(im, d, s, accent)
            if s.get("nota"):
                self.note(im, d, s["nota"], y_end)
            p = os.path.join(self.out, f"{i:02d}.jpg")
            im.convert("RGB").save(p, quality=92)
            paths.append(p)
        thumbs = [Image.open(p).resize((270, 338)) for p in paths]
        cols = min(4, len(thumbs))
        rows = (len(thumbs) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * 280 + 10, rows * 348 + 10), (40, 40, 40))
        for i, t in enumerate(thumbs):
            sheet.paste(t, (10 + (i % cols) * 280, 10 + (i // cols) * 348))
        return paths, sheet


if __name__ == "__main__":
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    paths, sheet = Deck(data, out).render()
    preview = sys.argv[3] if len(sys.argv) > 3 else "/tmp/preview_carrossel.jpg"
    sheet.save(preview, quality=85)
    print("\n".join(paths))
    print("preview:", preview)
