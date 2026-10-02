#!/usr/bin/env python3
# Renderiza os 16 segmentos de video (wide ou port) com Ken Burns + overlays.
import json, subprocess, sys, os

ROOT = "/home/user/toclose"
FF = f"{ROOT}/tools/ffmpeg"
ASSETS = f"{ROOT}/assets"
WORK = f"{ROOT}/work"
T = 1.0
FPS = 24

timeline = json.load(open(f"{WORK}/timeline.json"))

SCENES = [
    ("s01_ceu",      "zin"),
    ("c02_bluebook", "card"),
    ("c03_sign",     "card"),
    ("s04_olho",     "pan_r"),
    ("s05_hangar",   "zin"),
    ("s06_flir",     "zout"),
    ("c07_aaro24",   "card"),
    ("s08_u2",       "pan_l"),
    ("s09_orb",      "zout"),
    ("s10_sat",      "zin"),
    ("s11_congress", "pan_r"),
    ("c12_fy25",     "card"),
    ("c13_virginia", "card"),
    ("s14_navymar",  "zin"),
    ("c15_40pct",    "card"),
    ("s16_conselho", "zout"),
]

BIAS = {
    "s01_ceu": 0.62, "s04_olho": 0.5, "s05_hangar": 0.5, "s06_flir": 0.5,
    "s08_u2": 0.5, "s09_orb": 0.5, "s10_sat": 0.5, "s11_congress": 0.5,
    "s14_navymar": 0.45, "s16_conselho": 0.5,
}

def zoompan(motion, F, OUT):
    c = "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    if motion == "zin":
        z = f"z='min(1+0.12*on/{F},1.12)'"
    elif motion == "zout":
        z = f"z='if(lte(on,1),1.12,max(1.12-0.12*on/{F},1.0))'"
    elif motion == "pan_r":
        z = "z='1.10'"; c = f"x='(iw-iw/zoom)*(0.15+0.7*on/{F})':y='(ih-ih/zoom)/2'"
    elif motion == "pan_l":
        z = "z='1.10'"; c = f"x='(iw-iw/zoom)*(0.85-0.7*on/{F})':y='(ih-ih/zoom)/2'"
    else:
        z = f"z='min(1+0.05*on/{F},1.05)'"
    return f"zoompan={z}:{c}:d={F}:s={OUT}:fps={FPS}"

import os as _os
def render(mode):
    _only = _os.environ.get("ONLY")
    _only = [int(x) for x in _only.split(",")] if _only else None
    port = mode == "port"
    outdir = f"{WORK}/renders/{mode}"
    os.makedirs(outdir, exist_ok=True)
    OUT = "1080x1920" if port else "1920x1080"
    title_png = f"{WORK}/title_{'p' if port else 'w'}.png"
    credits_png = f"{WORK}/credits_{'p' if port else 'w'}.png"
    for i, (sc, motion) in enumerate(SCENES):
        if _only and i+1 not in _only: continue
        seg = timeline[i]
        dur = seg["dur"]
        F = int(round(dur * FPS))
        is_card = sc.startswith("c")
        if is_card:
            img = f"{ASSETS}/{'p' if port else 'c'}{sc[1:]}.jpg"
        else:
            img = f"{ASSETS}/{sc}.jpg"
        vf = []
        if is_card:
            vf.append("scale=1296:2304:flags=lanczos" if port else "scale=2304:1296:flags=lanczos")
        else:
            if port:
                b = BIAS[sc]
                vf.append(f"scale=2304:1296:flags=lanczos,crop=729:1296:x='(iw-729)*{b}',scale=1296:2304:flags=lanczos")
            else:
                vf.append("scale=2304:1296:flags=lanczos")
        vf.append(zoompan(motion, F, OUT))
        if not is_card:
            vf.append("vignette=PI/4.5")
        if i == 0:
            vf.append("fade=t=in:st=0:d=0.7")
        else:
            vf.append("fade=t=in:st=0:d=0.5")
        if i == len(SCENES) - 1:
            vf.append(f"fade=t=out:st={dur-1.0:.2f}:d=1.0")
        else:
            vf.append(f"fade=t=out:st={dur-0.5:.2f}:d=0.5")
        base = "[0:v]" + ",".join(vf) + "[base];"
        fc = base
        if i == 0:
            fc += f"[1:v]fade=t=in:st=0.8:d=0.8:alpha=1,fade=t=out:st=6.8:d=1.0:alpha=1[tt];[base][tt]overlay=0:0[outv]"
            extra = ["-loop", "1", "-t", f"{dur:.3f}", "-i", title_png]
        elif i == len(SCENES) - 1:
            fc += f"[1:v]fade=t=in:st={dur-7.0:.2f}:d=1.0:alpha=1[tt];[base][tt]overlay=0:0[outv]"
            extra = ["-loop", "1", "-t", f"{dur:.3f}", "-i", credits_png]
        else:
            fc += "[base]null[outv]"
            extra = []
        out = f"{outdir}/seg{i+1:02d}.mp4"
        cmd = [FF, "-y", "-loglevel", "error", "-i", img] + extra + [
               "-filter_complex", fc, "-map", "[outv]", "-r", str(FPS),
               "-c:v", "libx264", "-preset", "ultrafast", "-crf", "15",
               "-pix_fmt", "yuv420p", out]
        print(f"[{mode}] seg {i+1:02d} {sc} {dur:.2f}s ...", flush=True)
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode != 0:
            print("ERRO:", r.stderr.decode()[:1500])
            raise SystemExit(1)
    print(f"[{mode}] segmentos ok")

render(sys.argv[1] if len(sys.argv) > 1 else "wide")
