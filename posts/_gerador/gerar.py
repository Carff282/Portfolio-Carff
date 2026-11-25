"""Gerador de carrosseis do @carffcode.

Uso:  python3 posts/_gerador/gerar.py conteudo.json pasta_saida/
Gera 01.jpg, 02.jpg, ... (1080x1350, JPEG) no visual "editor de codigo".

Formato do JSON:
{
  "arquivo": "arquitetura.md",          # nome que aparece na barra do editor
  "slides": [
    {"tipo": "capa", "kicker": "// sistema.design()", "titulo": "Antes de escrever código,",
     "destaque": "desenhe o sistema.", "subtitulo": "Arquitetura em 5 passos"},
    {"tipo": "colunas", "kicker": "01 · ...", "titulo": "...", "colunas": [
        {"titulo": "...", "sub": "...", "itens": ["...", "..."]}, {...}], "rodape": "..."},
    {"tipo": "pilha", "kicker": "...", "titulo": "...", "itens": [{"titulo": "...", "sub": "..."}], "rodape": "..."},
    {"tipo": "codigo", "kicker": "...", "titulo": "...", "codigo": "linha1\\nlinha2", "checks": ["...", "..."]},
    {"tipo": "grade", "kicker": "...", "titulo": "...", "itens": [{"titulo": "...", "sub": "..."}] (4 itens), "rodape": "..."},
    {"tipo": "destaque", "kicker": "...", "titulo": "...", "texto": "...", "itens": ["...", "..."]},
    {"tipo": "fechamento", "kicker": "// resumo", "titulo": "...", "passos": ["...", "..."],
     "cta_titulo": "Salva pra consultar depois", "cta_texto": "e comenta: ..."}
  ]
}
Slides internos recebem automaticamente o rótulo "PASSO NN" se "passo" for informado (ex.: "passo": 1).
Itens de "colunas" que começam com "+ " ou "− " viram prós/contras coloridos.
Mantenha os textos curtos: o gerador reduz a fonte do título se precisar, mas não faz milagre.
"""
import json
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
BG = (13, 17, 23)
PANEL = (22, 27, 34)
CODEBG = (16, 20, 27)
BORDER = (48, 54, 61)
TXT = (230, 237, 243)
MUTED = (139, 148, 158)
GREEN = (63, 185, 80)
BLUE = (88, 166, 255)
PURPLE = (188, 140, 255)
ORANGE = (255, 166, 87)
PINK = (255, 123, 114)
ACCENTS = [BLUE, PURPLE, ORANGE, GREEN, PINK]
HANDLE = "@carffcode"

INTER = "/usr/share/fonts/opentype/inter/"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONOB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def inter(weight, size):
    return ImageFont.truetype(f"{INTER}Inter-{weight}.otf", size)


def mono(size, bold=False):
    return ImageFont.truetype(MONOB if bold else MONO, size)


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


def rbox(d, xy, fill=PANEL, outline=BORDER, w=2, r=22):
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=w)


class Deck:
    def __init__(self, data, out):
        self.data = data
        self.out = out
        self.total = len(data["slides"])
        self.fname = data.get("arquivo", "post.md")
        os.makedirs(out, exist_ok=True)

    def base(self, n, step=None, accent=GREEN):
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im)
        for gx in range(40, W, 40):
            for gy in range(40, H, 40):
                d.point((gx, gy), fill=(28, 33, 40))
        d.rectangle([0, 0, W, 70], fill=PANEL)
        d.line([0, 70, W, 70], fill=BORDER, width=2)
        for i, c in enumerate([PINK, ORANGE, GREEN]):
            d.ellipse([36 + i * 34, 24, 58 + i * 34, 46], fill=c)
        d.text((160, 22), self.fname, font=mono(24), fill=MUTED)
        if step:
            lab = f"PASSO {int(step):02d}"
            d.text((W - 50 - d.textlength(lab, font=mono(24, True)), 22), lab, font=mono(24, True), fill=accent)
        d.line([60, H - 110, W - 60, H - 110], fill=BORDER, width=2)
        d.text((60, H - 82), HANDLE, font=mono(30, True), fill=TXT)
        pg = f"{n}/{self.total}"
        d.text((W - 60 - d.textlength(pg, font=mono(28)), H - 80), pg, font=mono(28), fill=MUTED)
        if n < self.total:
            a = "arrasta →"
            f = inter("Medium", 28)
            d.text(((W - d.textlength(a, font=f)) / 2, H - 80), a, font=f, fill=MUTED)
        return im, d

    def heading(self, d, s, accent, y=150):
        d.text((70, y), s.get("kicker", ""), font=mono(30, True), fill=accent)
        font = fit_title(d, s["titulo"], W - 140)
        return block(d, (70, y + 60), s["titulo"], font, TXT, W - 140, 1.15)

    def footer_text(self, d, y, text):
        if text:
            block(d, (70, y), text, inter("SemiBold", 36), TXT, W - 140)

    # ---- tipos ----
    def capa(self, n, s, accent):
        im, d = self.base(n)
        d.text((70, 220), s.get("kicker", ""), font=mono(36), fill=GREEN)
        big = fit_title(d, s["titulo"] + " " + s.get("destaque", ""), W - 140, size=92, max_lines=4)
        y = block(d, (70, 300), s["titulo"], big, TXT, W - 140, 1.12)
        if s.get("destaque"):
            y = block(d, (70, y), s["destaque"], big, GREEN, W - 140, 1.12)
        y += 50
        if s.get("subtitulo"):
            y = block(d, (70, y), s["subtitulo"], inter("Medium", 44), MUTED, W - 140)
        chips = s.get("chips") or []
        if chips:
            cy = y + 90
            gap = 30
            bw = (W - 140 - gap * (len(chips) - 1)) // len(chips)
            for i, lab in enumerate(chips):
                c = ACCENTS[i % len(ACCENTS)]
                x = 70 + i * (bw + gap)
                rbox(d, [x, cy, x + bw, cy + 110], outline=c, w=3)
                f = mono(30, True)
                d.text((x + (bw - d.textlength(lab, font=f)) / 2, cy + 38), lab, font=f, fill=c)
        return im

    def colunas(self, n, s, accent):
        im, d = self.base(n, s.get("passo"), accent)
        y = self.heading(d, s, accent) + 50
        cols = s["colunas"][:2]
        cw = (W - 140 - 40) // 2
        hmax = 560
        for i, col in enumerate(cols):
            c = ACCENTS[(ACCENTS.index(accent) + i) % len(ACCENTS)]
            x = 70 + i * (cw + 40)
            rbox(d, [x, y, x + cw, y + hmax], outline=c, w=3)
            yy = block(d, (x + 32, y + 32), col["titulo"], inter("Bold", 40), c, cw - 64, 1.15)
            if col.get("sub"):
                yy = block(d, (x + 32, yy + 4), col["sub"], inter("Medium", 28), MUTED, cw - 64)
            yy += 24
            for it in col.get("itens", []):
                mark, txt, mc = "›", it, c
                if it[:2] in ("+ ", "− ", "- "):
                    mark, txt = it[0].replace("-", "−"), it[2:]
                    mc = GREEN if mark == "+" else PINK
                d.text((x + 32, yy), mark, font=mono(34, True), fill=mc)
                yy = block(d, (x + 70, yy + 2), txt, inter("Regular", 32), TXT, cw - 102) + 22
        self.footer_text(d, y + hmax + 50, s.get("rodape"))
        return im

    def pilha(self, n, s, accent):
        im, d = self.base(n, s.get("passo"), accent)
        y = self.heading(d, s, accent) + 40
        items = s["itens"][:5]
        lh = 130 if len(items) <= 4 else 110
        gap = 34
        for i, it in enumerate(items):
            c = ACCENTS[i % len(ACCENTS)]
            yy = y + i * (lh + gap)
            rbox(d, [70, yy, W - 70, yy + lh], outline=c, w=3)
            d.rectangle([70, yy + 20, 80, yy + lh - 20], fill=c)
            d.text((115, yy + 22), it["titulo"], font=inter("Bold", 42), fill=c)
            if it.get("sub"):
                d.text((115, yy + lh - 50), it["sub"], font=mono(26), fill=MUTED)
            if i < len(items) - 1:
                ax = W // 2
                d.line([ax, yy + lh + 4, ax, yy + lh + gap - 8], fill=MUTED, width=3)
                d.polygon([(ax - 9, yy + lh + gap - 14), (ax + 9, yy + lh + gap - 14), (ax, yy + lh + gap - 2)], fill=MUTED)
        self.footer_text(d, y + len(items) * (lh + gap) + 10, s.get("rodape"))
        return im

    TOKEN = re.compile(r"(//.*$|#.*$|'[^']*'|\"[^\"]*\"|`[^`]*`|\b\w+\b|\s+|.)")
    KW = {"const", "let", "var", "function", "return", "if", "else", "for", "while", "class", "interface",
          "type", "async", "await", "import", "from", "export", "new", "def", "true", "false", "null",
          "undefined", "string", "number", "boolean", "void", "try", "catch", "throw", "of", "in", "this"}

    def code_line(self, d, x, y, line, font):
        for m in self.TOKEN.finditer(line):
            t = m.group(0)
            rest = line[m.end():]
            if t.startswith("//") or t.startswith("#"):
                c = MUTED
            elif t[0] in "'\"`":
                c = GREEN
            elif t in self.KW:
                c = PURPLE
            elif re.fullmatch(r"\w+", t) and rest.lstrip().startswith("("):
                c = BLUE
            elif re.fullmatch(r"[A-Z]\w*", t):
                c = ORANGE
            elif re.fullmatch(r"\d+", t):
                c = ORANGE
            else:
                c = TXT
            d.text((x, y), t, font=font, fill=c)
            x += d.textlength(t, font=font)

    def codigo(self, n, s, accent):
        im, d = self.base(n, s.get("passo"), accent)
        y = self.heading(d, s, accent) + 45
        lines = s["codigo"].split("\n")[:11]
        longest = max(lines, key=len) if lines else ""
        size = 34
        while size > 22 and d.textlength(longest, font=mono(size)) > W - 220:
            size -= 2
        font = mono(size)
        lh = int(size * 1.7)
        hbox = lh * len(lines) + 70
        rbox(d, [70, y, W - 70, y + hbox], fill=CODEBG)
        for i, line in enumerate(lines):
            self.code_line(d, 110, y + 35 + i * lh, line, font)
        y += hbox + 45
        for t in s.get("checks", [])[:3]:
            if y > H - 200:
                break
            d.text((70, y), "✓", font=mono(36, True), fill=GREEN)
            y = block(d, (120, y + 2), t, inter("Medium", 34), TXT, W - 190) + 20
        return im

    def grade(self, n, s, accent):
        im, d = self.base(n, s.get("passo"), accent)
        y = self.heading(d, s, accent) + 50
        items = s["itens"][:4]
        cw = (W - 140 - 40) // 2
        ch = 250
        for i, it in enumerate(items):
            c = ACCENTS[i % len(ACCENTS)]
            x = 70 + (i % 2) * (cw + 40)
            yy = y + (i // 2) * (ch + 40)
            rbox(d, [x, yy, x + cw, yy + ch], outline=c, w=3)
            d.text((x + 32, yy + 36), it["titulo"], font=fit_title(d, it["titulo"], cw - 64, 44, 1, "Bold"), fill=c)
            block(d, (x + 32, yy + 115), it.get("sub", ""), inter("Regular", 30), TXT, cw - 64)
        rows = (len(items) + 1) // 2
        self.footer_text(d, y + rows * (ch + 40) + 20, s.get("rodape"))
        return im

    def destaque(self, n, s, accent):
        im, d = self.base(n, s.get("passo"), accent)
        y = self.heading(d, s, accent) + 50
        if s.get("texto"):
            tf = inter("Bold", 40)
            lines = wrap(d, s["texto"], tf, W - 220)
            hb = len(lines) * 52 + 70
            rbox(d, [70, y, W - 70, y + hb], fill=(18, 38, 26), outline=GREEN)
            block(d, (110, y + 35), s["texto"], tf, TXT, W - 220)
            y += hb + 50
        for t in s.get("itens", [])[:5]:
            d.text((70, y), "›", font=mono(38, True), fill=accent)
            y = block(d, (115, y + 2), t, inter("Medium", 36), TXT, W - 185) + 24
        return im

    def fechamento(self, n, s, accent):
        im, d = self.base(n)
        d.text((70, 230), s.get("kicker", "// resumo"), font=mono(36), fill=GREEN)
        big = fit_title(d, s["titulo"], W - 140, size=88, max_lines=3)
        y = block(d, (70, 300), s["titulo"], big, TXT, W - 140, 1.12) + 50
        for i, p in enumerate(s.get("passos", [])[:6]):
            c = ACCENTS[i % len(ACCENTS)]
            d.text((70, y), f"{i + 1:02d}", font=mono(36, True), fill=c)
            d.text((150, y - 2), p, font=inter("SemiBold", 40), fill=TXT)
            y += 66
        y += 40
        if y > H - 340:
            y = H - 340
        rbox(d, [70, y, W - 70, y + 190], fill=(18, 38, 26), outline=GREEN)
        d.text((110, y + 36), s.get("cta_titulo", "Salva pra consultar depois"), font=inter("Bold", 42), fill=GREEN)
        block(d, (110, y + 100), s.get("cta_texto", "e comenta o que achou!"), inter("Medium", 36), TXT, W - 220)
        return im

    def render(self):
        paths = []
        for i, s in enumerate(self.data["slides"], 1):
            accent = ACCENTS[(i - 2) % len(ACCENTS)] if i > 1 else GREEN
            im = getattr(self, s["tipo"])(i, s, accent)
            p = os.path.join(self.out, f"{i:02d}.jpg")
            im.save(p, quality=92)
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
