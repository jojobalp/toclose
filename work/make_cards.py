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
    hdr_size = 44 if not port else 44
    avail_w = (W - 2 * M - 40)
    hdr_avail_w = (W - 660 - M) if not port else avail_w
    hdr_maxc = max(18, int(hdr_avail_w / (hdr_size * 0.62)))
    cmd = ["convert", "-size", f"{W}x{H}", "xc:#e7e2d3"]
    cmd += ["-attenuate", "0.16", "+noise", "Gaussian"]
    cmd += ["-fill", "rgba(60,50,30,0.10)", "-draw", f"rectangle 0,0 {W},80"]
    cmd += ["-stroke", "rgba(40,35,25,0.55)", "-strokewidth", "5", "-fill", "none",
            "-draw", f"rectangle {M-30},60 {W-M+30},{H-60}"]
    if port:
        # No portrait, coloca o carimbo no topo direito e inicia o cabeçalho abaixo dele
        cmd += ["-fill", "none", "-stroke", "#b03a2e", "-strokewidth", "7",
                "-draw", f"rectangle {W-610},95 {W-80},205"]
        cmd += ["-font", SERIFB, "-pointsize", "54", "-fill", "#b03a2e",
                "-draw", f"text {W-580},172 '{esc(stamp)}'"]
        y = 280
    else:
        cmd += ["-fill", "none", "-stroke", "#b03a2e", "-strokewidth", "7",
                "-draw", f"rectangle {W-640},90 {W-100},210"]
        cmd += ["-font", SERIFB, "-pointsize", "58", "-fill", "#b03a2e",
                "-draw", f"text {W-608},175 '{esc(stamp)}'"]
        y = 155
    for hl in wrap(header, hdr_maxc):
        cmd += ["-stroke", "none", "-font", MONOB, "-pointsize", str(hdr_size), "-fill", "#2a2620",
                "-draw", f"text {M},{y} '{esc(hl)}'"]
        y += int(hdr_size * 1.45)
    line_y = max(y - 15, 230) if not port else y - 15
    cmd += ["-stroke", "rgba(40,35,25,0.55)", "-strokewidth", "3",
            "-draw", f"line {M},{line_y} {W-M},{line_y}"]
    y = line_y + 85
    for size, text, colr in lines:
        sz = size if not port else min(size, 58)
        maxc = max(16, int(avail_w / (sz * 0.62)))
        for wl in wrap(text, maxc):
            cmd += ["-stroke", "none", "-font", MONO, "-pointsize", str(sz), "-fill", colr,
                    "-draw", f"text {M},{y} '{esc(wl)}'"]
            y += int(sz * 1.48)
        y += 28
    foot_sz = 32 if not port else 28
    foot_maxc = max(24, int(avail_w / (foot_sz * 0.56)))
    foot_lines = wrap(foot, foot_maxc)
    cmd += ["-font", SANS, "-pointsize", str(foot_sz), "-fill", "#5a5347"]
    fy = H - 90 - (len(foot_lines) - 1) * 40
    for wl in foot_lines:
        cmd += ["-draw", f"text {M},{fy} '{esc(wl)}'"]
        fy += 40
    cmd += ["-quality", "92", out]
    run(cmd)

def brief_card(out, kicker, lines, foot, W, H, port, accent="#e8a33d"):
    M = 130 if not port else 80
    avail_w = W - 2 * M - 40
    cmd = ["convert", "-size", f"{W}x{H}", "xc:#0b0f14"]
    cmd += ["-attenuate", "0.05", "+noise", "Gaussian"]
    cmd += ["-fill", accent, "-draw", f"rectangle 0,0 22,{H}"]
    y = 180
    kicker_maxc = max(20, int(avail_w / (48 * 0.62)))
    for kl in wrap(kicker, kicker_maxc):
        cmd += ["-font", MONOB, "-pointsize", "48", "-fill", accent,
                "-draw", f"text {M},{y} '{esc(kl)}'"]
        y += 68
    y += 75
    for size, text, colr in lines:
        if port:
            sz = size if size >= 110 else min(size, 74)
        else:
            sz = size if size >= 110 else min(size, 82)
        font = SANSB if size >= 80 else SANS
        char_factor = 0.62 if size >= 80 else 0.55
        maxc = max(14, int(avail_w / (sz * char_factor)))
        for wl in wrap(text, maxc):
            cmd += ["-font", font, "-pointsize", str(sz), "-fill", colr,
                    "-draw", f"text {M},{y} '{esc(wl)}'"]
            y += int(sz * 1.38)
        y += 26
    foot_sz = 34 if not port else 28
    foot_maxc = max(24, int(avail_w / (foot_sz * 0.61)))
    foot_lines = wrap(foot, foot_maxc)
    cmd += ["-font", MONO, "-pointsize", str(foot_sz), "-fill", "#7d8894"]
    fy = H - 90 - (len(foot_lines) - 1) * 42
    for wl in foot_lines:
        cmd += ["-draw", f"text {M},{fy} '{esc(wl)}'"]
        fy += 42
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
