#!/usr/bin/env python3
# Monta o final via concat demuxer (stream copy) + audio original. Sem re-encode.
import subprocess, sys, os

ROOT = "/home/user/toclose"
FF = f"{ROOT}/tools/ffmpeg"
WORK = f"{ROOT}/work"
AUDIO = f"{ROOT}/A_falha_humana_na_investigação_de_OVNIs.m4a"

mode = sys.argv[1] if len(sys.argv) > 1 else "wide"
outdir = f"{WORK}/renders/{mode}"
lst = f"{WORK}/concat_{mode}.txt"
with open(lst, "w") as f:
    for i in range(1, 17):
        f.write(f"file '{outdir}/seg{i:02d}.mp4'\n")
out = f"{ROOT}/video_final_{mode}.mp4"
cmd = [FF, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
       "-i", AUDIO, "-map", "0:v", "-map", "1:a", "-c", "copy",
       "-movflags", "+faststart", out]
print("montando", mode, "...", flush=True)
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print("ERRO:", r.stderr[:2000]); raise SystemExit(1)
print("ok:", out)
