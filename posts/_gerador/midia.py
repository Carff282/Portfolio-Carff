"""Gera Story (imagem 9:16) e Reel (vídeo 9:16) a partir dos slides de um post.

Uso:
  python3 posts/_gerador/midia.py story <pasta_do_post>   -> <pasta>/story.jpg
  python3 posts/_gerador/midia.py reel  <pasta_do_post>   -> <pasta>/reel.mp4
Os slides 01.jpg, 02.jpg, ... precisam existir (gerados por gerar.py).
"""
import glob
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
BG = (13, 17, 23)
TXT = (230, 237, 243)
MUTED = (139, 148, 158)
GREEN = (63, 185, 80)
INTER = "/usr/share/fonts/opentype/inter/"
MONOB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
HAND = "/usr/share/fonts/truetype/google-fonts/ofl/comicrelief/ComicRelief-Bold.ttf"


def slides(pasta):
    s = sorted(glob.glob(os.path.join(pasta, "[0-9][0-9].jpg")))
    if not s:
        sys.exit(f"Nenhum slide NN.jpg em {pasta}")
    return s


TEMA = {}


def detectar_tema(pasta):
    """Lê a cor do fundo do slide 01 para combinar story/reel com o estilo do post."""
    global BG, TXT, MUTED, GREEN
    px = Image.open(slides(pasta)[0]).convert("RGB").getpixel((20, 700))
    claro = sum(px) > 450
    TEMA["claro"] = claro
    if claro:
        BG, TXT, MUTED, GREEN = (248, 245, 237), (28, 28, 32), (105, 105, 112), (21, 128, 61)


def fundo():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    if TEMA.get("claro"):
        for gy in range(80, H, 46):
            d.line([0, gy, W, gy], fill=(214, 225, 238), width=2)
        d.line([46, 0, 46, H], fill=(239, 163, 163), width=2)
    else:
        for gx in range(40, W, 40):
            for gy in range(40, H, 40):
                d.point((gx, gy), fill=(28, 33, 40))
    return im, d


def centro(d, y, txt, font, fill):
    d.text(((W - d.textlength(txt, font=font)) / 2, y), txt, font=font, fill=fill)


def story(pasta):
    import random
    rng = random.Random(os.path.abspath(pasta))
    capa = Image.open(slides(pasta)[0]).convert("RGB")
    im, d = fundo()
    hand = ImageFont.truetype(HAND, 72)
    tinta = (29, 78, 216) if TEMA.get("claro") else (250, 204, 21)
    frase = rng.choice(["saiu post novo!", "post novo no ar", "corre lá no feed", "fiz um post novo"])
    t = Image.new("RGBA", (900, 120), (0, 0, 0, 0))
    td = ImageDraw.Draw(t)
    td.text(((900 - td.textlength(frase, font=hand)) / 2, 20), frase, font=hand, fill=tinta)
    t = t.rotate(rng.uniform(-4, -1), expand=True, resample=Image.BICUBIC)
    im.paste(t, ((W - t.width) // 2, 120), t)
    # capa levemente torta, com sombra, como um print colado
    cw = 880
    ch = int(capa.height * cw / capa.width)
    capa = capa.resize((cw, ch)).convert("RGBA")
    sombra = Image.new("RGBA", (cw + 40, ch + 40), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rectangle([20, 20, cw + 20, ch + 20], fill=(0, 0, 0, 70))
    from PIL import ImageFilter
    sombra = sombra.filter(ImageFilter.GaussianBlur(12))
    ang = rng.uniform(-2.5, 2.5)
    sombra = sombra.rotate(ang, expand=True, resample=Image.BICUBIC)
    capa = capa.rotate(ang, expand=True, resample=Image.BICUBIC)
    y = 290
    im.paste(sombra, ((W - sombra.width) // 2 + 6, y - 10), sombra)
    im.paste(capa, ((W - capa.width) // 2, y), capa)
    hy = y + capa.height + 70
    f = ImageFont.truetype(HAND, 50)
    centro(d, hy, "o post completo tá no feed", f, TXT)
    centro(d, hy + 80, "@carffcode", ImageFont.truetype(MONOB, 40), MUTED)
    out = os.path.join(pasta, "story.jpg")
    im.save(out, quality=92)
    print(out)


def reel(pasta, seg=4.0, fade=0.5):
    paths = slides(pasta)
    tmp = tempfile.mkdtemp()
    frames = []
    for i, p in enumerate(paths):
        s = Image.open(p).convert("RGB")
        # no vídeo não existe "arrasta →": apaga o aviso do rodapé
        ImageDraw.Draw(s).rectangle([360, s.height - 90, 720, s.height - 40], fill=s.getpixel((700, s.height - 30)))
        im, d = fundo()
        y = (H - s.height) // 2
        im.paste(s, (0, y))
        # barra de progresso estilo stories
        n = len(paths)
        gap, x0 = 10, 60
        bw = (W - 2 * x0 - gap * (n - 1)) / n
        for k in range(n):
            x = x0 + k * (bw + gap)
            d.rounded_rectangle([x, 120, x + bw, 128], radius=4, fill=GREEN if k <= i else (48, 54, 61))
        centro(d, 170, "@carffcode", ImageFont.truetype(MONOB, 38), TXT)
        fp = os.path.join(tmp, f"f{i:02d}.png")
        im.save(fp)
        frames.append(fp)

    n = len(frames)
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for fp in frames:
        cmd += ["-loop", "1", "-t", str(seg), "-i", fp]
    cmd += ["-f", "lavfi", "-t", str(n * seg - (n - 1) * fade), "-i", "anullsrc=r=44100:cl=stereo"]
    filt, last = [], "[0:v]"
    for k in range(1, n):
        off = k * (seg - fade)
        lab = f"[v{k}]"
        filt.append(f"{last}[{k}:v]xfade=transition=fade:duration={fade}:offset={off:.2f}{lab}")
        last = lab
    filt.append(f"{last}format=yuv420p,fps=30[vout]" if n > 1 else "[0:v]format=yuv420p,fps=30[vout]")
    out = os.path.join(pasta, "reel.mp4")
    cmd += ["-filter_complex", ";".join(filt), "-map", "[vout]", "-map", f"{n}:a",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-c:a", "aac", "-b:a", "128k",
            "-shortest", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print(out)


if __name__ == "__main__":
    detectar_tema(sys.argv[2])
    {"story": story, "reel": reel}[sys.argv[1]](sys.argv[2])
