#!/usr/bin/env python3
"""Renderiza a edição cinematográfica 16:9 usando os assets existentes.

Pipeline: Ken Burns mais suave, grade teal/amber discreta, cartelas de capítulo,
dissolves entre cenas, legendas extraídas do MP4 do projeto e trilha original
ambiente sintetizada (sem faixa comercial/licenciada de terceiros).

Uso: python3 work/render_cinematic.py
Teste parcial: ONLY=1,4,6,16 python3 work/render_cinematic.py
"""
from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FF = ROOT / "tools" / "ffmpeg"
WORK = ROOT / "work"
ASSETS = ROOT / "assets"
TIMELINE = json.loads((WORK / "timeline.json").read_text())
RENDER_DIR = WORK / "renders" / "cinematic"
TMP_DIR = WORK / "tmp"
OVERLAY_DIR = WORK / "cinematic_assets"
AUDIO = ROOT / "A_falha_humana_na_investigação_de_OVNIs.m4a"
SUBTITLE_ZIP = ROOT / "A_falha_humana_na_investigação_de_OVNIs.zip"
SUBTITLE_VIDEO = TMP_DIR / "cinematic_subtitles.mp4"
SCORE_FILE = TMP_DIR / "cinematic_score.flac"
OUTPUT = ROOT / "video_cinematic_wide.mp4"

FPS = 24
TRANSITION_FRAMES = 18
TRANSITION = TRANSITION_FRAMES / FPS
DURATION = sum(float(s["dur"]) for s in TIMELINE)
TARGET_FRAMES = round(DURATION * FPS)

SCENES = [
    ("s01_ceu", "zin", "title.png"),
    ("c02_bluebook", "card", None),
    ("c03_sign", "card", None),
    ("s04_olho", "pan_r", "scene04.png"),
    ("s05_hangar", "zin", "scene05.png"),
    ("s06_flir", "zout", None),
    ("c07_aaro24", "card", None),
    ("s08_u2", "pan_l", "scene08.png"),
    ("s09_orb", "zout", "scene09.png"),
    ("s10_sat", "zin", "scene10.png"),
    ("s11_congress", "pan_r", "scene11.png"),
    ("c12_fy25", "card", None),
    ("c13_virginia", "card", None),
    ("s14_navymar", "zin", "scene14.png"),
    ("c15_40pct", "card", None),
    ("s16_conselho", "zout", "credits.png"),
]

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and result.returncode:
        print("\nCOMANDO FALHOU:", " ".join(map(str, cmd)), file=sys.stderr)
        print(result.stderr[-5000:], file=sys.stderr)
        raise SystemExit(result.returncode)
    return result


def make_overlay(path: Path, commands: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    run(["convert", "-size", "1920x1080", "xc:none", *commands, "PNG32:" + str(path)])


def make_overlays() -> None:
    OVERLAY_DIR.mkdir(parents=True, exist_ok=True)
    gold = "#d8a55e"
    pale_gold = "#e0b66d"
    white = "#f5f3ee"
    gray = "#c8ced6"
    muted = "#aeb6c1"

    make_overlay(OVERLAY_DIR / "title.png", [
        "-fill", "rgba(4,8,14,0.58)", "-draw", "roundrectangle 86,260 1086,910 20,20",
        "-fill", gold, "-draw", "rectangle 86,260 98,910",
        "-font", FONT_MONO, "-pointsize", "24", "-fill", pale_gold, "-gravity", "NorthWest",
        "-annotate", "+145+350", "DOSSIÊ UAP  •  INVESTIGAÇÃO ESPECIAL",
        "-font", FONT_BOLD, "-pointsize", "82", "-fill", white,
        "-annotate", "+142+480", "A FALHA É",
        "-font", FONT_BOLD, "-pointsize", "126", "-fill", "#e3aa54",
        "-annotate", "+140+635", "HUMANA",
        "-font", FONT, "-pointsize", "29", "-fill", white,
        "-annotate", "+147+785", "NA INVESTIGAÇÃO DE OVNIs",
        "-font", FONT_MONO, "-pointsize", "19", "-fill", muted,
        "-annotate", "+147+842", "ARQUIVOS DOS EUA  /  1947—2026",
    ])

    cards = {
        "scene04.png": ("PERCEPÇÃO", "O OBSERVADOR", "Quando percepção vira evidência"),
        "scene05.png": ("ARQUIVO MILITAR", "TECNOLOGIA SECRETA", "U-2 • stealth • drones"),
        "scene06.png": ("VÍDEO / FLIR", "O ÂNGULO ENGANA", "Paralaxe • distância • sensores"),
        "scene08.png": ("AVIAÇÃO / 1950–80", "O CÉU CONFIDENCIAL", "Programas secretos vistos do chão"),
        "scene09.png": ("OBSERVAÇÃO", "UM PONTO DE LUZ", "O que uma imagem não consegue provar"),
        "scene10.png": ("ÓRBITA", "O CÉU TEM TRÁFEGO", "Satélites • reflexos • confusões"),
        "scene11.png": ("CAPITÓLIO / 2023", "O DEBATE CHEGA AO CONGRESSO", "Testemunhos • alegações • evidências"),
        "scene14.png": ("MARINHA DOS EUA", "RELATOS NO MAR", "Sensores • testemunhas • contexto"),
    }
    for name, (label, title, subtitle) in cards.items():
        make_overlay(OVERLAY_DIR / name, [
            "-fill", "rgba(4,8,14,0.64)", "-draw", "roundrectangle 88,104 1040,366 18,18",
            "-fill", gold, "-draw", "roundrectangle 88,104 99,366 4,4",
            "-font", FONT_MONO, "-pointsize", "20", "-fill", pale_gold, "-gravity", "NorthWest",
            "-annotate", "+142+149", label,
            "-font", FONT_BOLD, "-pointsize", "40", "-fill", white,
            "-annotate", "+140+220", title,
            "-font", FONT, "-pointsize", "24", "-fill", gray,
            "-annotate", "+142+280", subtitle,
        ])

    make_overlay(OVERLAY_DIR / "credits.png", [
        "-fill", "rgba(4,8,14,0.58)", "-draw", "roundrectangle 86,306 950,760 20,20",
        "-fill", gold, "-draw", "rectangle 86,306 98,760",
        "-font", FONT_MONO, "-pointsize", "22", "-fill", pale_gold, "-gravity", "NorthWest",
        "-annotate", "+145+375", "ENCERRAMENTO  /  O QUE OS DADOS PERMITEM",
        "-font", FONT_BOLD, "-pointsize", "62", "-fill", white,
        "-annotate", "+142+500", "A FALHA É HUMANA",
        "-font", FONT, "-pointsize", "27", "-fill", gray,
        "-annotate", "+147+576", "DOCUMENTOS • CONTEXTO • EVIDÊNCIAS",
        "-font", FONT, "-pointsize", "22", "-fill", muted,
        "-annotate", "+147+640", "Fontes: AARO • USAF Blue Book • Congresso dos EUA",
    ])


def frame_counts() -> list[int]:
    frames = [round(float(s["dur"]) * FPS) for s in TIMELINE]
    frames[-1] += TARGET_FRAMES - sum(frames)
    if sum(frames) != TARGET_FRAMES:
        raise ValueError("Não foi possível ajustar a timeline à duração total em frames")
    return frames


def image_for(scene: str) -> Path:
    if scene.startswith("c"):
        return ASSETS / f"{scene}.jpg"
    return ASSETS / f"{scene}.jpg"


def zoompan(motion: str, frames: int) -> str:
    denom = max(1, frames - 1)
    center = "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    if motion == "zin":
        zoom = f"z='min(1+0.085*on/{denom},1.085)'"
    elif motion == "zout":
        zoom = f"z='max(1.085-0.085*on/{denom},1.0)'"
    elif motion == "pan_r":
        zoom = "z='1.07'"
        center = f"x='(iw-iw/zoom)*(0.12+0.66*on/{denom})':y='(ih-ih/zoom)/2'"
    elif motion == "pan_l":
        zoom = "z='1.07'"
        center = f"x='(iw-iw/zoom)*(0.82-0.66*on/{denom})':y='(ih-ih/zoom)/2'"
    else:  # cards: keep the text fully readable with only a restrained 2.2% push-in
        zoom = f"z='min(1+0.022*on/{denom},1.022)'"
    return f"zoompan={zoom}:{center}:d={frames}:s=1920x1080:fps={FPS}"


def render_segment(index: int, frame_total: list[int]) -> None:
    name, motion, overlay_name = SCENES[index]
    spec = TIMELINE[index]
    frames = frame_total[index]
    dur = frames / FPS
    is_card = name.startswith("c")
    img = image_for(name)
    out = RENDER_DIR / f"seg{index + 1:02d}.mp4"

    if is_card:
        # Process each still once, before zoompan, to keep the full-length render fast.
        filters = [
            "eq=contrast=1.025:brightness=0.002:saturation=0.91:gamma=0.99",
            "unsharp=5:5:0.18:3:3:0.0",
            "scale=2304:1296:flags=lanczos",
            zoompan(motion, frames),
        ]
    else:
        filters = [
            "eq=contrast=1.075:brightness=-0.008:saturation=0.86:gamma=0.99",
            "colorbalance=rs=-0.025:gs=0.000:bs=0.035:rm=0.000:gm=0.005:bm=0.010:rh=0.020:gh=0.008:bh=-0.020",
            "vignette=PI/5.2",
            "noise=alls=1:allf=u",
            "scale=2304:1296:flags=lanczos",
            zoompan(motion, frames),
        ]
    base = "[0:v]" + ",".join(filters) + "[base0]"
    cmd = [str(FF), "-y", "-hide_banner", "-loglevel", "error", "-i", str(img)]
    fc = base
    if overlay_name:
        overlay_path = OVERLAY_DIR / overlay_name
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur + TRANSITION:.3f}", "-i", str(overlay_path)]
        if overlay_name == "title.png":
            alpha = "fade=t=in:st=0.7:d=0.95:alpha=1,fade=t=out:st=7.2:d=1.0:alpha=1"
        elif overlay_name == "credits.png":
            alpha = f"fade=t=in:st={max(0.0, dur - 9.2):.3f}:d=1.2:alpha=1,fade=t=out:st={max(0.0, dur - 2.0):.3f}:d=1.4:alpha=1"
        else:
            alpha = "fade=t=in:st=0.65:d=0.7:alpha=1,fade=t=out:st=5.4:d=0.9:alpha=1"
        fc += f";[1:v]format=rgba,{alpha}[ov];[base0][ov]overlay=0:0:eof_action=pass:repeatlast=0:shortest=0:format=auto[comp]"
    else:
        fc += ";[base0]null[comp]"
    fc += ";[comp]format=yuv420p[outv]"
    expected_frames = frames
    cmd += [
        "-filter_complex", fc,
        "-map", "[outv]", "-an", "-frames:v", str(expected_frames),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-tune", "stillimage",
        "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FPS),
        str(out),
    ]
    print(f"[cinema] cena {index + 1:02d}/16 {name} ({spec['dur']:.2f}s) ...", flush=True)
    run(cmd)


def extract_subtitles() -> Path:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    if SUBTITLE_VIDEO.exists() and SUBTITLE_VIDEO.stat().st_size > 1_000_000:
        return SUBTITLE_VIDEO
    with zipfile.ZipFile(SUBTITLE_ZIP) as zf:
        candidates = [n for n in zf.namelist() if n.lower().endswith(".mp4")]
        if not candidates:
            raise FileNotFoundError("O ZIP não contém o vídeo de legendas esperado")
        with zf.open(candidates[0]) as src, SUBTITLE_VIDEO.open("wb") as dst:
            shutil.copyfileobj(src, dst)
    return SUBTITLE_VIDEO


def build_score() -> Path:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    duration = f"{DURATION:.3f}"
    # Quiet D-minor-inspired pads, detuned slightly for width and movement.
    left = (
        "0.035*sin(2*PI*55*t+0.15*sin(2*PI*0.035*t))+"
        "0.024*sin(2*PI*73.42*t+0.10*sin(2*PI*0.021*t))+"
        "0.018*sin(2*PI*110*t+0.10*sin(2*PI*0.018*t))+"
        "0.010*sin(2*PI*146.83*t+0.10*sin(2*PI*0.015*t))+"
        "0.008*sin(2*PI*174.61*t+0.10*sin(2*PI*0.013*t))+"
        "0.006*sin(2*PI*220*t+0.10*sin(2*PI*0.011*t))"
    )
    right = (
        "0.035*sin(2*PI*55*t+0.08+0.15*sin(2*PI*0.035*t))+"
        "0.024*sin(2*PI*73.42*t+0.07+0.10*sin(2*PI*0.021*t))+"
        "0.018*sin(2*PI*110*t-0.06+0.10*sin(2*PI*0.018*t))+"
        "0.010*sin(2*PI*146.83*t+0.14+0.10*sin(2*PI*0.015*t))+"
        "0.008*sin(2*PI*174.61*t-0.09+0.10*sin(2*PI*0.013*t))+"
        "0.006*sin(2*PI*220*t-0.12+0.10*sin(2*PI*0.011*t))"
    )
    events = [0.0, 65.52, 135.64, 226.14, 297.67, 342.47]
    hit_terms = []
    for event in events:
        x = f"(t-{event:.3f})"
        hit_terms.append(
            f"if(between(t,{event:.3f},{event + 0.85:.3f}),"
            f"0.028*exp(-5*{x})*sin(2*PI*(52*{x}-16*{x}*{x})),0)"
        )
    hits = "+".join(hit_terms)
    hit_right = "+".join(
        term.replace("0.028*exp", "0.026*exp") for term in hit_terms
    )
    pad_src = f"aevalsrc=exprs='{left}|{right}':s=48000:d={duration}"
    hit_src = f"aevalsrc=exprs='{hits}|{hit_right}':s=48000:d={duration}"
    noise_src = f"anoisesrc=color=pink:amplitude=0.002:duration={duration}:sample_rate=48000"
    graph = (
        "[0:a]aecho=0.78:0.82:110|220:0.16|0.08[pad];"
        "[1:a]volume=1.0[hits];"
        "[2:a]pan=stereo|c0=c0|c1=c0,highpass=f=180,lowpass=f=2600,volume=0.20[air];"
        "[pad][hits][air]amix=inputs=3:duration=first:normalize=0,"
        "afade=t=in:st=0:d=5,afade=t=out:st=378.25:d=5,alimiter=limit=0.7[out]"
    )
    cmd = [
        str(FF), "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", pad_src,
        "-f", "lavfi", "-i", hit_src,
        "-f", "lavfi", "-i", noise_src,
        "-filter_complex", graph, "-map", "[out]",
        "-ar", "48000", "-c:a", "flac", "-compression_level", "5", str(SCORE_FILE),
    ]
    print("[cinema] compondo trilha ambiente original ...", flush=True)
    run(cmd)
    return SCORE_FILE


def render_chunk(chunk_index: int, start: int, stop: int, frame_total: list[int]) -> Path:
    """Crossfade a small group at a time to keep FFmpeg's memory bounded."""
    chunk_dir = RENDER_DIR / "chunks"
    chunk_dir.mkdir(parents=True, exist_ok=True)
    output = chunk_dir / f"chunk{chunk_index + 1:02d}.mp4"
    segment_ids = list(range(start, stop))
    cmd = [str(FF), "-y", "-hide_banner", "-loglevel", "error", "-filter_complex_threads", "3"]
    for i in segment_ids:
        cmd += ["-i", str(RENDER_DIR / f"seg{i + 1:02d}.mp4")]

    parts = []
    for local, global_index in enumerate(segment_ids):
        parts.append(
            f"[{local}:v]setpts=PTS-STARTPTS,fps={FPS},"
            f"tpad=stop_mode=clone:stop_duration={TRANSITION:.6f},settb=AVTB,format=yuv420p[v{local}]"
        )
    previous = "[v0]"
    cumulative = frame_total[segment_ids[0]]
    for local in range(1, len(segment_ids)):
        offset = cumulative / FPS
        label = f"xf{local}"
        parts.append(
            f"{previous}[v{local}]xfade=transition=fade:duration={TRANSITION:.6f}:offset={offset:.6f}[{label}]"
        )
        previous = f"[{label}]"
        cumulative += frame_total[segment_ids[local]]
    chunk_frames = sum(frame_total[i] for i in segment_ids)
    output_frames = chunk_frames + TRANSITION_FRAMES
    parts.append(f"{previous}trim=end_frame={output_frames},setpts=PTS-STARTPTS[vout]")
    cmd += [
        "-filter_complex", ";".join(parts), "-map", "[vout]", "-an",
        "-frames:v", str(output_frames),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-tune", "stillimage",
        "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FPS), str(output),
    ]
    print(f"[cinema] dissolve do bloco {chunk_index + 1}/4 ...", flush=True)
    run(cmd)
    return output


def assemble(frame_total: list[int]) -> None:
    subtitle_path = extract_subtitles()
    score_path = build_score()
    chunk_paths = []
    chunk_ranges = [(0, 4), (4, 8), (8, 12), (12, 16)]
    chunk_frames = []
    for chunk_index, (start, stop) in enumerate(chunk_ranges):
        chunk_paths.append(render_chunk(chunk_index, start, stop, frame_total))
        chunk_frames.append(sum(frame_total[start:stop]))

    # A second, small xfade graph joins just four block renders. This avoids
    # holding all sixteen full-HD streams in one large filter graph.
    cmd = [str(FF), "-y", "-hide_banner", "-loglevel", "error", "-filter_complex_threads", "3"]
    for path in chunk_paths:
        cmd += ["-i", str(path)]
    cmd += ["-i", str(AUDIO), "-i", str(subtitle_path), "-i", str(score_path)]

    parts = []
    for i in range(len(chunk_paths)):
        parts.append(f"[{i}:v]setpts=PTS-STARTPTS,fps={FPS},settb=AVTB,format=yuv420p[v{i}]")
    previous = "[v0]"
    cumulative = chunk_frames[0]
    for i in range(1, len(chunk_paths)):
        offset = cumulative / FPS
        label = f"xf{i}"
        parts.append(
            f"{previous}[v{i}]xfade=transition=fade:duration={TRANSITION:.6f}:offset={offset:.6f}[{label}]"
        )
        previous = f"[{label}]"
        cumulative += chunk_frames[i]
    parts.append(f"{previous}trim=end_frame={TARGET_FRAMES},setpts=PTS-STARTPTS[vbase]")
    parts.append(
        "[5:v]setpts=PTS-STARTPTS,fps=24,scale=1728:886:flags=lanczos,"
        "colorkey=0x000000:0.12:0.03,format=rgba[subtitles]"
    )
    parts.append(
        "[vbase][subtitles]overlay=x=96:y=130:eof_action=pass:repeatlast=0:shortest=0:format=auto,"
        "fade=t=in:st=0:d=1.15,fade=t=out:st=381.55:d=1.70,format=yuv420p[vout]"
    )
    parts.append(
        "[4:a]aresample=48000,highpass=f=75,lowpass=f=15000,"
        "equalizer=f=200:t=q:w=1:g=-1.5,equalizer=f=3300:t=q:w=1:g=1.5,"
        "acompressor=threshold=-20dB:ratio=2.2:attack=12:release=160:makeup=2,"
        "loudnorm=I=-16:TP=-1.5:LRA=10,asplit=2[voice][voicekey]"
    )
    parts.append("[6:a]aresample=48000[score]")
    parts.append(
        "[score][voicekey]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=650:makeup=1[ducked]"
    )
    parts.append(
        "[voice][ducked]amix=inputs=2:duration=first:dropout_transition=2:normalize=0,"
        "afade=t=in:st=0:d=0.55,afade=t=out:st=380.50:d=2.75,"
        "loudnorm=I=-14:TP=-1.0:LRA=11[aout]"
    )
    cmd += [
        "-filter_complex", ";".join(parts),
        "-map", "[vout]", "-map", "[aout]",
        "-frames:v", str(TARGET_FRAMES), "-t", f"{DURATION:.3f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "24", "-tune", "film",
        "-profile:v", "high", "-level", "4.1", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-g", "48", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart",
        "-metadata", "title=A Falha Humana na Investigação de OVNIs — Edição Cinematográfica",
        "-metadata", "comment=Full HD 1920x1080; dissolves, legendas e trilha ambiente original",
        str(OUTPUT),
    ]
    print("[cinema] montando blocos, legendas e mix de áudio ...", flush=True)
    run(cmd)
    print(f"[cinema] pronto: {OUTPUT} ({OUTPUT.stat().st_size / 1_000_000:.1f} MB)", flush=True)


def main() -> None:
    if not FF.is_file():
        raise FileNotFoundError(f"FFmpeg não encontrado em {FF}")
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    make_overlays()
    frames = frame_counts()
    only = os.environ.get("ONLY")
    chosen = [int(x) for x in only.split(",")] if only else list(range(1, len(SCENES) + 1))
    for i in chosen:
        if not 1 <= i <= len(SCENES):
            raise ValueError(f"Índice de cena fora do intervalo: {i}")
        expected = RENDER_DIR / f"seg{i:02d}.mp4"
        if not os.environ.get("FORCE") and expected.is_file() and expected.stat().st_size > 500_000:
            print(f"[cinema] cena {i:02d} já renderizada; reutilizando", flush=True)
            continue
        render_segment(i - 1, frames)
    if only:
        print("[cinema] render parcial concluído; montagem final ignorada")
        return
    assemble(frames)


if __name__ == "__main__":
    main()
