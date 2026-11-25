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


def slides(pasta):
    s = sorted(glob.glob(os.path.join(pasta, "[0-9][0-9].jpg")))
    if not s:
        sys.exit(f"Nenhum slide NN.jpg em {pasta}")
    return s


def fundo():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    for gx in range(40, W, 40):
        for gy in range(40, H, 40):
            d.point((gx, gy), fill=(28, 33, 40))
    return im, d


def centro(d, y, txt, font, fill):
    d.text(((W - d.textlength(txt, font=font)) / 2, y), txt, font=font, fill=fill)


def story(pasta):
    capa = Image.open(slides(pasta)[0]).convert("RGB")
    im, d = fundo()
    centro(d, 150, "NOVO POST NO FEED", ImageFont.truetype(MONOB, 44), GREEN)
    cw = 920
    ch = int(capa.height * cw / capa.width)
    capa = capa.resize((cw, ch))
    y = 260
    d.rounded_rectangle([(W - cw) // 2 - 6, y - 6, (W + cw) // 2 + 6, y + ch + 6], radius=18, outline=GREEN, width=4)
    im.paste(capa, ((W - cw) // 2, y))
    f = ImageFont.truetype(INTER + "Inter-Bold.otf", 54)
    centro(d, y + ch + 90, "Toca no post e salva 🔖".replace(" 🔖", ""), f, TXT)
    centro(d, y + ch + 170, "@carffcode", ImageFont.truetype(MONOB, 40), MUTED)
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
        ImageDraw.Draw(s).rectangle([360, s.height - 90, 720, s.height - 40], fill=BG)
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
    {"story": story, "reel": reel}[sys.argv[1]](sys.argv[2])
