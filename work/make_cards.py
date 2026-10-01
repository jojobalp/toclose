#!/usr/bin/env python3
# Cards de documento/manchete (fatos reais citados) nas duas orientacoes.
import subprocess, os, sys

ASSETS = "/home/user/toclose/assets"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONOB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIFB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

def esc(t):
    return t.replace("\\", "\\\\").replace("'", "\\'")

def wrap(text, maxc):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        cand = (cur + " " + w).strip()
        if len(cand) <= maxc:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def run(cmd):
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print(r.stderr.decode()[:2000])
        raise SystemExit(1)

def doc_card(out, header, lines, stamp, foot, W, H, port):
    M = 90 if not port else 80
    hdr_size = 52 if not port else 50
    maxc = 999 if not port else 26
    cmd = ["convert", "-size", f"{W}x{H}", "xc:#e7e2d3"]
    cmd += ["-attenuate", "0.16", "+noise", "Gaussian"]
    cmd += ["-fill", "rgba(60,50,30,0.10)", "-draw", f"rectangle 0,0 {W},80"]
    cmd += ["-stroke", "rgba(40,35,25,0.55)", "-strokewidth", "5", "-fill", "none",
            "-draw", f"rectangle {M-30},60 {W-M+30},{H-60}"]
    # header (pode quebrar no portrait)
    y = 150
    for hl in (wrap(header, maxc) if port else [header]):
        cmd += ["-font", MONOB, "-pointsize", str(hdr_size), "-fill", "#2a2620",
                "-draw", f"text {M},{y} '{esc(hl)}'"]
        y += int(hdr_size * 1.5)
    cmd += ["-stroke", "rgba(40,35,25,0.55)", "-strokewidth", "3",
            "-draw", f"line {M},{y-20} {W-M},{y-20}"]
    y += 70
    for size, text, colr in lines:
        sz = size if not port else min(size, 62)
        for wl in (wrap(text, maxc) if port else [text]):
            cmd += ["-font", MONO, "-pointsize", str(sz), "-fill", colr,
                    "-draw", f"text {M},{y} '{esc(wl)}'"]
            y += int(sz * 1.55)
        y += 30
    cmd += ["-font", SANS, "-pointsize", "34" if not port else "30", "-fill", "#5a5347"]
    fy = H - 100
    for wl in (wrap(foot, 46) if port else [foot]):
        cmd += ["-draw", f"text {M},{fy} '{esc(wl)}'"]
        fy += 44
    cmd += ["-fill", "none", "-stroke", "#b03a2e", "-strokewidth", "7",
            "-draw", f"rectangle {W-640},90 {W-100},210"]
    cmd += ["-font", SERIFB, "-pointsize", "58", "-fill", "#b03a2e",
            "-draw", f"text {W-608},180 '{esc(stamp)}'"]
    cmd += ["-quality", "92", out]
    run(cmd)

def brief_card(out, kicker, lines, foot, W, H, port, accent="#e8a33d"):
    M = 130 if not port else 80
    maxc = 999 if not port else 24
    cmd = ["convert", "-size", f"{W}x{H}", "xc:#0b0f14"]
    cmd += ["-attenuate", "0.05", "+noise", "Gaussian"]
    cmd += ["-fill", accent, "-draw", f"rectangle 0,0 22,{H}"]
    y = 200
    for kl in (wrap(kicker, 30) if port else [kicker]):
        cmd += ["-font", MONOB, "-pointsize", "48", "-fill", accent,
                "-draw", f"text {M},{y} '{esc(kl)}'"]
        y += 70
    y += 90
    for size, text, colr in lines:
        sz = size if not port else min(size, 110)
        font = SANSB if size >= 80 else SANS
        for wl in (wrap(text, maxc) if port else [text]):
            cmd += ["-font", font, "-pointsize", str(sz), "-fill", colr,
                    "-draw", f"text {M},{y} '{esc(wl)}'"]
            y += int(sz * 1.45)
        y += 26
    cmd += ["-font", MONO, "-pointsize", "36" if not port else "30", "-fill", "#7d8894"]
    fy = H - 100
    for wl in (wrap(foot, 40) if port else [foot]):
        cmd += ["-draw", f"text {M},{fy} '{esc(wl)}'"]
        fy += 44
    cmd += ["-quality", "92", out]
    run(cmd)

CARDS = [
    ("doc", "02_bluebook", "UNITED STATES AIR FORCE - PROJECT BLUE BOOK", [
        (74, "12,618 avistamentos reportados (1947-1969).", "#26221c"),
        (74, "701 casos NUNCA foram explicados.", "#26221c"),
        (52, "Nenhum avistamento demonstrou ameaça à segurança nacional.", "#5a5347"),
    ], "DECLASSIFIED", "Fonte: AARO, Historical Record Report Vol. 1 (2024) - dados USAF"),
    ("doc", "03_sign", "PROJECT SIGN - USAF - FEVEREIRO DE 1949", [
        (64, "\"Nenhuma evidência definitiva e conclusiva está disponível que prove ou refute a existência desses objetos não identificados como aeronaves reais.\"", "#26221c"),
        (52, "- relatório do Projeto Sign, citado no Historical Record Report", "#5a5347"),
    ], "DECLASSIFIED", "Fonte: AARO, Historical Record Report Vol. 1 (2024)"),
    ("doc", "07_aaro24", "DEPT. OF DEFENSE - AARO - 8 DE MARÇO DE 2024", [
        (66, "\"Até o momento, a AARO não descobriu nenhuma evidência empírica de que qualquer avistamento de UAP representasse tecnologia de outro mundo.\"", "#26221c"),
        (54, "Maioria dos casos: má identificação de objetos e fenômenos comuns.", "#5a5347"),
    ], "DECLASSIFIED", "Fonte: Report on the Historical Record of USG Involvement with UAP, Vol. 1"),
    ("doc", "10_congress", "CÂMARA DOS EUA - COMISSÃO DE SUPERVISÃO - 26/07/2023", [
        (70, "David Grusch (ex-inteligência): \"não-humanos\"", "#26221c"),
        (56, "Baseado em 40+ entrevistas ao longo de 4 anos.", "#26221c"),
        (56, "Nunca viu pessoalmente a nave que alega existir.", "#8a4a2c"),
    ], "TRANSCRITO", "Fonte: transcrição oficial da audiência - House Oversight Committee"),
    ("brief", "12_fy25", "AARO - RELATÓRIO ANUAL FY2025 (2026)", [
        (120, "319", "#f2f5f7"),
        (58, "relatórios de UAP recebidos no período", "#aeb9c4"),
        (120, "114", "#e8a33d"),
        (58, "resolvidos como objetos comuns (balões, aves, satélites, aeronaves, drones, jetpack, foguete)", "#aeb9c4"),
    ], "Fonte: AARO FY2025 Consolidated Annual Report on UAP"),
    ("brief", "13_virginia", "NOVO CASO - COSTA DA VIRGÍNIA (07/2026)", [
        (96, "Marinha dos EUA relata cerca de 100 objetos aéreos e 2 sistemas de superfície", "#f2f5f7"),
        (58, "\"A falta de dados de sensores oportunos e acionáveis continua limitando a capacidade da AARO de resolver casos.\"", "#aeb9c4"),
    ], "Fonte: AARO FY2025 Annual Report / DefenseScoop, 21/07/2026"),
    ("brief", "15_40pct", "AARO - RELATÓRIO DE 05/06/2026 (PURSUE)", [
        (150, "~40%", "#e8a33d"),
        (62, "dos fenômenos revisados seguem sem explicação convencional; o \"orbe laranja\" de 10/2023 continua não resolvido.", "#f2f5f7"),
    ], "Fonte: relatório AARO assinado por J. Kosloski, 05/06/2026 (3ª leva PURSUE)"),
]

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "wide"
    port = (mode == "port")
    W, H = (1296, 2304) if port else (2304, 1296)
    pre = "p" if port else "c"
    for tup in CARDS:
        kind, key = tup[0], tup[1]
        out = f"{ASSETS}/{pre}{key}.jpg"
        if kind == "doc":
            _, _, header, lines, stamp, foot = tup
            doc_card(out, header, lines, stamp, foot, W, H, port)
        else:
            _, _, kicker, lines, foot = tup
            brief_card(out, kicker, lines, foot, W, H, port)
    print("cards", mode, "ok")

main()
