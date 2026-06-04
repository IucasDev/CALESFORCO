import streamlit as st
import math

st.set_page_config(
    page_title="Esforços Mecânicos — Elektro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── TEMA VISUAL ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;500;600;700&family=Barlow+Condensed:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
    background: #0d1117;
    color: #e6edf3;
}
.stApp { background: #0d1117; }

/* Cabeçalho */
.app-header {
    background: linear-gradient(135deg, #1a2332 0%, #0d1117 100%);
    border-bottom: 2px solid #f6a800;
    padding: 20px 32px 16px;
    margin: -2rem -2rem 0;
    display: flex;
    align-items: center;
    gap: 16px;
}
.app-header h1 {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: #fff;
    margin: 0;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.app-header .sub {
    font-size: 0.78rem;
    color: #8b949e;
    margin: 2px 0 0;
    font-weight: 300;
}
.badge {
    background: #f6a800;
    color: #0d1117;
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 0.7rem;
    padding: 3px 8px;
    border-radius: 3px;
    letter-spacing: 1px;
}

/* Painel lateral — formulários */
.panel-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    color: #f6a800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 0 0 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid #21262d;
}
.section-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 16px 18px;
    margin-bottom: 12px;
}
.section-card.active {
    border-color: #f6a800;
    box-shadow: 0 0 0 1px #f6a800;
}

/* Métricas resultado */
.result-card {
    background: linear-gradient(135deg, #1a2332, #161b22);
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 14px 16px;
    text-align: center;
}
.result-card .label {
    font-size: 0.68rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 500;
}
.result-card .value {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #f6a800;
    line-height: 1.1;
}
.result-card .value.ok   { color: #3fb950; }
.result-card .value.warn { color: #d29922; }
.result-card .value.err  { color: #f85149; }

/* Inputs */
div[data-baseweb="select"] > div {
    background: #21262d !important;
    border-color: #30363d !important;
    border-radius: 6px !important;
    color: #e6edf3 !important;
}
.stSelectbox label, .stNumberInput label, .stRadio label,
.stCheckbox label, .stSlider label {
    color: #8b949e !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}
div[data-testid="stNumberInput"] input {
    background: #21262d !important;
    border-color: #30363d !important;
    color: #e6edf3 !important;
    border-radius: 6px !important;
}
.stRadio div[role="radiogroup"] { gap: 6px; }
div[data-baseweb="radio"] > div:first-child {
    background: #21262d;
    border-color: #f6a800 !important;
}

/* Checkbox */
.stCheckbox > label > div:first-child {
    background: #21262d !important;
    border-color: #30363d !important;
}

/* Divisor */
hr { border-color: #21262d !important; margin: 8px 0 !important; }

/* Métricas nativas */
[data-testid="metric-container"] {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 10px 14px;
}
[data-testid="metric-container"] label { color: #8b949e !important; font-size: 0.7rem !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #f6a800 !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1.6rem !important;
}

/* Info / success / error */
.stAlert { border-radius: 6px !important; }

/* Expander */
.streamlit-expanderHeader {
    background: #161b22 !important;
    border-radius: 6px !important;
    color: #8b949e !important;
    font-size: 0.78rem !important;
}
/* Select slider */
.stSlider [data-testid="stThumbValue"] { color: #f6a800 !important; }
</style>
""", unsafe_allow_html=True)

# ── DADOS ─────────────────────────────────────────────────────────────────────

ALTURA_FINAL = {9:8.80, 10:9.80, 11:10.80, 12:11.80, 14:13.80, 16:15.80}

TRACAO_CONV = {
    "S04":219,"S02":347,"S20":696,"S40":1108,"S33":1388,"S47":2497,
    "S40TR":807,"S33TR":857,"S47TR":756,
    "A04":60,"A02":86,"A20":173,"A40":274,"A33":436,"A47":619,
    "C06":60,"C04":107,"C02":171,"C20":342,"C40":544,
    "C25":106,"C35":155,"C70":296,"C120":568,
}
FAMILIAS_CONV = {
    "S — Alum. c/ alma de aço": ["S04","S02","S20","S40","S33","S47","S40TR","S33TR","S47TR"],
    "A — Alum. s/ alma de aço": ["A04","A02","A20","A40","A33","A47"],
    "C — Cobre":                 ["C06","C04","C02","C20","C40","C25","C35","C70","C120"],
}
CABOS_BT = {
    "A — Alumínio": ["A04","A02","A20","A40","A33","A47"],
    "C — Cobre":    ["C06","C04","C02","C20","C40","C25","C35","C70","C120"],
}
TRACAO_PA = {"PA50":311,"PA70":375,"PA95":469,"PA120":527,"PA185":683,"PA240":795}
TRACAO_PB = {
    "PB35":{5:4,10:14,15:32,20:56,25:88,30:127,35:172,40:225},
    "PB50":{5:6,10:24,15:51,20:91,25:142,30:204,35:278,40:363},
    "PB70":{5:7,10:30,15:67,20:119,25:186,30:267,35:364,40:475},
    "PB120":{5:8,10:33,15:74,20:132,25:206,30:296,35:403,40:527},
}
VOS_PB = [5,10,15,20,25,30,35,40]
TRACAO_CAZ = {
    "CAZ 3,09":  {50:229,100:256,150:263,200:282,300:318,400:349,500:376,600:400},
    "CAZ 3x2,25":{50:357,100:395,150:406,200:436,300:491,400:540,500:580,600:615},
    "CAW 3,26":  {50:244,100:273,150:276,200:296,300:334,400:368,500:398,600:426},
    "CAW 3x2,59":{50:438,100:492,150:495,200:524,300:588,400:645,500:696,600:741},
    "CAA 04":    {50:217,100:269,150:313,200:324,300:324,400:324,500:324,600:324},
}
VOS_CAZ = [50,100,150,200,300,400,500,600]
TRACAO_PROT = {
    "URBANO15KVA50P":240,"URBANO15KVA70P":321,"URBANO15KVA120P":510,
    "RURAL15KVA50P":334,"RURAL15KVA70P":407,"RURAL15KVA120P":584,
    "URBANO36,2KVA70P":426,"URBANO36,2KVA120P":581,
    "RURAL36,2KVA70P":524,"RURAL36,2KVA120P":779,
    "URBANO15KVA185P":400,"RURAL15KVA185P":400,
}
COMPACTA_VAO = {
    "URBANO15KVA35P":{15:342,20:349,25:355,30:365,35:386,40:405,45:422,50:438,55:451,60:464},
    "URBANO15KVA70P":{15:366,20:383,25:400,30:417,35:444,40:468,45:490,50:511,55:529,60:546},
    "URBANO15KVA185P":{15:442,20:487,25:528,30:567,35:603,40:643,45:680,50:714,55:746,60:775},
    "URBANO15KVA240P":{15:478,20:533,25:584,30:631,35:674,40:720,45:763,50:803,55:840,60:875},
    "RURAL15KVA35P":{15:401,20:459,25:512,30:560,35:603,40:643,45:680,50:714,55:745,60:774,65:801,70:827,75:850,80:872,85:892,90:911,95:929,100:945},
    "RURAL15KVA70P":{15:435,20:501,25:561,30:616,35:665,40:711,45:754,50:793,55:830,60:864,65:895,70:925,75:953,80:978,85:1003,90:1025,95:1047,100:1067},
    "RURAL15KVA185P":{15:521,20:608,25:685,30:756,35:822,40:883,45:939,50:992,55:1041,60:1088,65:1131,70:1172,75:1211,80:1248,85:1282,90:1315,95:1345,100:1375},
    "RURAL15KVA240P":{15:559,20:654,25:740,30:818,35:890,40:958,45:1020,50:1079,55:1134,60:1186,65:1235,70:1281,75:1324,80:1366,85:1405,90:1442,95:1477,100:1510},
    "URBANO36,2KVA70P":{15:366,20:383,25:400,30:417,35:444,40:468,45:490,50:511,55:529,60:546},
    "URBANO36,2KVA185P":{15:521,20:588,25:650,30:707,35:767,40:822,45:874,50:922,55:966,60:1008},
    "RURAL36,2KVA70P":{15:542,20:633,25:715,30:790,35:859,40:923,45:983,50:1039,55:1092,60:1141,65:1187,70:1231,75:1273,80:1312,85:1349,90:1384,95:1417,100:1448},
    "RURAL36,2KVA185P":{15:630,20:741,25:840,30:932,35:1017,40:1096,45:1170,50:1239,55:1305,60:1367,65:1425,70:1481,75:1534,80:1584,85:1631,90:1677,95:1720,100:1761},
}
COMPACTA_FIXO = {
    "URBANO15KVA35P":405,"URBANO15KVA50P":516,"URBANO15KVA70P":468,
    "URBANO15KVA120P":665,"URBANO15KVA185P":643,"URBANO15KVA240P":720,
    "RURAL15KVA35P":872,"RURAL15KVA50P":1035,"RURAL15KVA70P":978,
    "RURAL15KVA120P":1257,"RURAL15KVA185P":1248,"RURAL15KVA240P":1366,
    "URBANO36,2KVA70P":640,"URBANO36,2KVA120P":805,"URBANO36,2KVA185P":822,
    "RURAL36,2KVA70P":1312,"RURAL36,2KVA120P":1577,"RURAL36,2KVA185P":1584,
    "RURAL > 80m15KVA35P":945,"RURAL > 80m15KVA50P":1795,
    "RURAL > 80m15KVA70P":1067,"RURAL > 80m15KVA120P":1797,
    "RURAL > 80m15KVA185P":1375,"RURAL > 80m15KVA240P":1510,
}

def interp(tab, v):
    k = sorted(tab.keys())
    if v<=k[0]: return float(tab[k[0]])
    if v>=k[-1]: return float(tab[k[-1]])
    for i in range(len(k)-1):
        if k[i]<=v<=k[i+1]:
            return float(tab[k[i]]+(tab[k[i+1]]-tab[k[i]])*(v-k[i])/(k[i+1]-k[i]))
    return 0.0

def get_compacta(local, tens, cabo, vao):
    key = f"{local}{tens}{cabo}"
    return interp(COMPACTA_VAO[key], vao) if key in COMPACTA_VAO else float(COMPACTA_FIXO.get(key,0))

ANGULOS = list(range(0,365,5))
def ang_slider(lbl, default, key):
    return st.select_slider(lbl, ANGULOS, value=default, key=key)

# ── DESENHO SVG DO POSTE ───────────────────────────────────────────────────────

def desenho_poste(altura_m, tem_n1, tipo_n1, tem_n2, tipo_n2, tem_sec, tipo_sec,
                  af, ang_ch_n1=0, tipo_saida_n1="Fim de linha",
                  ang_ch_n2=0, tipo_saida_n2="Fim de linha",
                  ang_ch_sec=0, tipo_saida_sec="Fim de linha"):

    W, H = 360, 520
    # Escala: poste vai de y=60 (topo) a y=460 (base no chão)
    POSTE_TOP_Y = 60
    POSTE_BOT_Y = 460
    POSTE_H_PX  = POSTE_BOT_Y - POSTE_TOP_Y
    CX = 180  # centro horizontal

    def m2y(metros):
        """Converte metros desde o solo para y no SVG (base=460, topo=60)."""
        frac = metros / altura_m
        return POSTE_BOT_Y - frac * POSTE_H_PX

    solo_y = POSTE_BOT_Y

    # Alturas das estruturas
    af_y   = m2y(af)
    n2_y   = m2y(max(0, af - 1.0))
    sec_y  = m2y(max(0, af - 3.5))
    eng_y  = m2y(0)  # nível do solo

    def cabo_svg(cx, y, ang_grau, tipo_rede, lado="esq", comprimento=90):
        """Gera elemento SVG de cabo saindo do poste."""
        cores = {
            "Convencional": "#a8b4bf",
            "Protegida":    "#4fc3f7",
            "Compacta":     "#81c784",
            "PA":           "#ffb74d",
            "PB":           "#ce93d8",
            "CAZ":          "#ef9a9a",
            "default":      "#a8b4bf",
        }
        cor = next((v for k,v in cores.items() if k.lower() in (tipo_rede or "").lower()), cores["default"])
        espessura = 3 if "compacta" in (tipo_rede or "").lower() else 2
        rad = math.radians(ang_grau)
        x2 = cx + math.cos(rad) * comprimento
        y2 = y  - math.sin(rad) * comprimento
        return f'<line x1="{cx}" y1="{y}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{cor}" stroke-width="{espessura}" stroke-linecap="round"/>'

    def braço_svg(cx, y, label, cor_label="#f6a800"):
        """Braço horizontal da estrutura."""
        return f'''
<line x1="{cx-40}" y1="{y}" x2="{cx+40}" y2="{y}" stroke="#6e7681" stroke-width="2"/>
<circle cx="{cx-40}" cy="{y}" r="4" fill="#4d90fe" opacity="0.9"/>
<circle cx="{cx+40}" cy="{y}" r="4" fill="#4d90fe" opacity="0.9"/>
<text x="{cx+50}" y="{y+4}" font-size="9" fill="{cor_label}" font-family="Barlow Condensed,sans-serif" font-weight="700">{label}</text>'''

    linhas = []

    # Fundo
    linhas.append(f'<rect width="{W}" height="{H}" fill="#0d1117" rx="10"/>')

    # Grade de fundo sutil
    for yi in range(60, 470, 40):
        linhas.append(f'<line x1="20" y1="{yi}" x2="{W-20}" y2="{yi}" stroke="#161b22" stroke-width="1"/>')

    # Solo
    linhas.append(f'<rect x="20" y="{solo_y}" width="{W-40}" height="60" fill="#1a2332" rx="4"/>')
    linhas.append(f'<line x1="20" y1="{solo_y}" x2="{W-20}" y2="{solo_y}" stroke="#30363d" stroke-width="1.5"/>')
    linhas.append(f'<text x="{CX}" y="{solo_y+18}" text-anchor="middle" font-size="9" fill="#444d56" font-family="Barlow,sans-serif">SOLO</text>')

    # Engastamento (parte enterrada)
    eng_px = int(POSTE_H_PX * 0.10 + (0.60/altura_m)*POSTE_H_PX)
    linhas.append(f'<rect x="{CX-6}" y="{solo_y-eng_px}" width="12" height="{eng_px+40}" fill="#21262d" rx="2"/>')

    # Poste principal
    linhas.append(f'<defs><linearGradient id="pg" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#3a4a5c"/><stop offset="40%" stop-color="#5a7a9c"/><stop offset="100%" stop-color="#2a3a4c"/></linearGradient></defs>')
    linhas.append(f'<rect x="{CX-6}" y="{POSTE_TOP_Y}" width="12" height="{POSTE_H_PX}" fill="url(#pg)" rx="3"/>')

    # Topo do poste
    linhas.append(f'<ellipse cx="{CX}" cy="{POSTE_TOP_Y}" rx="7" ry="3" fill="#6a8aac"/>')

    # Cotas
    linhas.append(f'<line x1="{CX-45}" y1="{POSTE_TOP_Y}" x2="{CX-45}" y2="{solo_y}" stroke="#21262d" stroke-width="1" stroke-dasharray="3,3"/>')
    linhas.append(f'<text x="{CX-50}" y="{(POSTE_TOP_Y+solo_y)//2+4}" text-anchor="middle" font-size="9" fill="#484f58" font-family="Barlow Condensed,sans-serif" transform="rotate(-90,{CX-50},{(POSTE_TOP_Y+solo_y)//2+4})">{altura_m:.0f} m</text>')

    # AF — linha de referência (0,20 do topo)
    linhas.append(f'<line x1="{CX-35}" y1="{af_y:.0f}" x2="{CX+35}" y2="{af_y:.0f}" stroke="#f6a800" stroke-width="0.8" stroke-dasharray="4,3" opacity="0.5"/>')
    linhas.append(f'<text x="{CX+46}" y="{af_y+3:.0f}" font-size="8" fill="#f6a800" opacity="0.6" font-family="Barlow,sans-serif">AF={af:.2f}m</text>')

    # 1º NÍVEL
    if tem_n1:
        linhas.append(braço_svg(CX, af_y, "1º NÍV"))
        linhas.append(cabo_svg(CX-40, af_y, ang_ch_n1+180, tipo_n1, comprimento=85))
        if "tangente" in tipo_saida_n1.lower() or "deriva" in tipo_saida_n1.lower():
            linhas.append(cabo_svg(CX+40, af_y, ang_ch_n1, tipo_n1, comprimento=85))

    # 2º NÍVEL
    if tem_n2:
        linhas.append(braço_svg(CX, n2_y, "2º NÍV", "#58a6ff"))
        linhas.append(cabo_svg(CX-40, n2_y, ang_ch_n2+180, tipo_n2, comprimento=80))
        if "tangente" in tipo_saida_n2.lower() or "deriva" in tipo_saida_n2.lower():
            linhas.append(cabo_svg(CX+40, n2_y, ang_ch_n2, tipo_n2, comprimento=80))

    # SECUNDÁRIA
    if tem_sec:
        linhas.append(braço_svg(CX, sec_y, "SEC BT", "#3fb950"))
        linhas.append(cabo_svg(CX-40, sec_y, ang_ch_sec+180, tipo_sec, comprimento=75))
        if "tangente" in tipo_saida_sec.lower() or "deriva" in tipo_saida_sec.lower():
            linhas.append(cabo_svg(CX+40, sec_y, ang_ch_sec, tipo_sec, comprimento=75))

    # Altura do poste (label)
    linhas.append(f'<rect x="5" y="5" width="80" height="22" rx="4" fill="#f6a800"/>')
    linhas.append(f'<text x="45" y="20" text-anchor="middle" font-size="11" font-weight="700" fill="#0d1117" font-family="Barlow Condensed,sans-serif">{altura_m:.0f} m / CONCRETO</text>')

    svg = f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-height:520px;border-radius:10px;background:#0d1117">{"".join(linhas)}</svg>'
    return svg

# ── WIDGETS ────────────────────────────────────────────────────────────────────

def w_cabo_at(pfx):
    tipo = st.selectbox("Tipo de rede", [
        "Convencional (S / A / C)",
        "Pré-Reunido Primária (PA)",
        "CAZ / CAW",
        "Protegida",
        "Compacta",
    ], key=f"{pfx}_tipo")
    t = 0.0
    nome_tipo = tipo.split("(")[0].strip()

    if tipo == "Convencional (S / A / C)":
        c1,c2,c3 = st.columns([1,2,2])
        qtd  = c1.number_input("Qtd/fase", 1, 10, 3, key=f"{pfx}_qtd")
        fam  = c2.selectbox("Família", list(FAMILIAS_CONV.keys()), key=f"{pfx}_fam")
        cabo = c3.selectbox("Cabo", FAMILIAS_CONV[fam], key=f"{pfx}_cabo")
        t    = float(TRACAO_CONV.get(cabo,0)) * qtd

    elif tipo == "Pré-Reunido Primária (PA)":
        c1,c2 = st.columns(2)
        cabo = c1.selectbox("Cabo", list(TRACAO_PA.keys()), key=f"{pfx}_cabo")
        qtd  = c2.number_input("Qtd.", 1, 6, 1, key=f"{pfx}_qtd")
        t    = float(TRACAO_PA.get(cabo,0)) * qtd
        nome_tipo = "PA"

    elif tipo == "CAZ / CAW":
        c1,c2 = st.columns(2)
        cabo = c1.selectbox("Cabo", list(TRACAO_CAZ.keys()), key=f"{pfx}_cabo")
        vao  = c2.select_slider("Vão (m)", VOS_CAZ, value=100, key=f"{pfx}_vao")
        t    = interp(TRACAO_CAZ[cabo], vao)
        nome_tipo = "CAZ"

    elif tipo == "Protegida":
        c1,c2,c3 = st.columns(3)
        loc  = c1.selectbox("Local", ["URBANO","RURAL"], key=f"{pfx}_loc")
        tens = c2.selectbox("Tensão", ["15KV","36,2KV"], key=f"{pfx}_tens")
        cabo = c3.selectbox("Cabo", ["A50P","A70P","A120P","A185P"], key=f"{pfx}_cabo")
        t    = float(TRACAO_PROT.get(f"{loc}{tens}{cabo}",0))

    elif tipo == "Compacta":
        c1,c2,c3,c4 = st.columns(4)
        loc  = c1.selectbox("Local", ["URBANO","RURAL","RURAL > 80m"], key=f"{pfx}_loc")
        tens = c2.selectbox("Tensão", ["15KV","36,2KV"], key=f"{pfx}_tens")
        cabo = c3.selectbox("Cabo", ["A35P","A50P","A70P","A120P","A185P","A240P"], key=f"{pfx}_cabo")
        vao  = c4.number_input("Vão (m)", 10, 100, 40, step=5, key=f"{pfx}_vao")
        t    = get_compacta(loc, tens, cabo, vao)

    st.caption(f"⚡ Tração: **{t:.0f} daN**")
    return float(t), nome_tipo

def w_cabo_bt(pfx):
    tipo = st.selectbox("Tipo de cabo BT", ["Convencional (A / C)","Pré-Reunido BT (PB)","CAZ / CAW"], key=f"{pfx}_tipo")
    t = 0.0
    nome = tipo.split("(")[0].strip()

    if tipo == "Convencional (A / C)":
        st.markdown("**Fases**")
        c1,c2,c3 = st.columns([1,2,2])
        qtdf  = c1.number_input("Qtd/fase",1,4,3,key=f"{pfx}_qtdf")
        famf  = c2.selectbox("Família",list(CABOS_BT.keys()),key=f"{pfx}_famf")
        cabof = c3.selectbox("Cabo",CABOS_BT[famf],key=f"{pfx}_cabof")
        t_f   = float(TRACAO_CONV.get(cabof,0))*qtdf
        st.markdown("**Neutro**")
        c4,c5 = st.columns(2)
        famn  = c4.selectbox("Família",list(CABOS_BT.keys()),key=f"{pfx}_famn")
        cabon = c5.selectbox("Cabo",CABOS_BT[famn],key=f"{pfx}_cabon")
        t_n   = float(TRACAO_CONV.get(cabon,0))
        st.markdown("**Controle**")
        c6,c7 = st.columns(2)
        famc  = c6.selectbox("Família",list(CABOS_BT.keys()),key=f"{pfx}_famc")
        caboc = c7.selectbox("Cabo",CABOS_BT[famc],key=f"{pfx}_caboc")
        t_c   = float(TRACAO_CONV.get(caboc,0))
        t     = t_f + t_n + t_c
        st.caption(f"Fase {t_f:.0f} + Neutro {t_n:.0f} + Ctrl {t_c:.0f} = **{t:.0f} daN**")
        nome = "BT Conv"

    elif tipo == "Pré-Reunido BT (PB)":
        c1,c2 = st.columns(2)
        cabo = c1.selectbox("Cabo",list(TRACAO_PB.keys()),key=f"{pfx}_cabo")
        vao  = c2.select_slider("Vão (m)",VOS_PB,value=20,key=f"{pfx}_vao")
        t    = interp(TRACAO_PB[cabo],vao)
        nome = "PB"

    elif tipo == "CAZ / CAW":
        c1,c2 = st.columns(2)
        cabo = c1.selectbox("Cabo",list(TRACAO_CAZ.keys()),key=f"{pfx}_cabo")
        vao  = c2.select_slider("Vão (m)",VOS_CAZ,value=100,key=f"{pfx}_vao")
        t    = interp(TRACAO_CAZ[cabo],vao)
        nome = "CAZ"

    st.caption(f"⚡ Tração: **{t:.0f} daN**")
    return float(t), nome

def painel_nivel(titulo, idx, alt_default, af, altura_poste, is_bt=False, fixo_alt=False):
    if fixo_alt:
        alt_est = float(alt_default)
        st.markdown(f'<div style="background:#1a2d1a;border:1px solid #3fb950;border-radius:6px;padding:8px 12px;font-size:0.8rem;color:#3fb950;margin-bottom:8px">📏 AI = <strong>{alt_est:.2f} m</strong> — fixo conforme norma Elektro</div>', unsafe_allow_html=True)
    else:
        alt_est = st.number_input("Altura da estrutura — AI (m)", 0.0, float(altura_poste), value=float(alt_default), step=0.1, key=f"{idx}_alt")

    col_ch, col_sa = st.columns(2)
    with col_ch:
        st.markdown('<div class="panel-title">↙ CHEGADA</div>', unsafe_allow_html=True)
        if is_bt:
            t_ch, nome_ch = w_cabo_bt(f"{idx}_ch")
        else:
            t_ch, nome_ch = w_cabo_at(f"{idx}_ch")
        ang_ch = ang_slider("Ângulo chegada (°)", 0, f"{idx}_ang_ch")
        st.caption("0°=L · 90°=N · 180°=O · 270°=S")

    with col_sa:
        st.markdown('<div class="panel-title">↗ SAÍDA</div>', unsafe_allow_html=True)
        tipo_saida = st.radio("O cabo...", [
            "Fim de linha",
            "Tangente — mesmo cabo",
            "Tangente — cabo diferente",
            "Deriva em outro ângulo",
        ], key=f"{idx}_saida")
        t_sa, ang_sa = 0.0, 0

        if tipo_saida == "Fim de linha":
            st.info("Só tração de chegada atua.")
        elif tipo_saida == "Tangente — mesmo cabo":
            t_sa, _ = t_ch, None
            ang_sa  = (ang_ch + 180) % 360
            st.caption(f"Mesmo cabo · saída {ang_sa}°")
            st.info("Forças opostas iguais → **resultante = 0** ✓")
        elif tipo_saida == "Tangente — cabo diferente":
            t_sa, _ = (w_cabo_bt(f"{idx}_sa") if is_bt else w_cabo_at(f"{idx}_sa"))
            ang_sa  = (ang_ch + 180) % 360
            st.caption(f"Tangente · cabos diferentes → resultante = |T₁−T₂|")
        else:
            t_sa, _ = (w_cabo_bt(f"{idx}_sa") if is_bt else w_cabo_at(f"{idx}_sa"))
            ang_sa  = ang_slider("Ângulo saída (°)", 90, f"{idx}_ang_sa")

    fx = t_ch*math.cos(math.radians(ang_ch))
    fy = t_ch*math.sin(math.radians(ang_ch))
    if tipo_saida != "Fim de linha":
        fx += t_sa*math.cos(math.radians(ang_sa))
        fy += t_sa*math.sin(math.radians(ang_sa))
    mag   = math.sqrt(fx**2+fy**2)
    fator = alt_est/af if af>0 else 1.0
    mag_t = mag*fator

    st.markdown("---")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("T. chegada (daN)", f"{t_ch:.0f}")
    c2.metric("T. saída (daN)",   f"{t_sa:.0f}")
    c3.metric("Deflexão α",       f"{min(abs(ang_sa-ang_ch)%360,360-abs(ang_sa-ang_ch)%360):.0f}°")
    c4.metric("🔴 Result. transf. (daN)", f"{mag_t:.1f}",
              help=f"Fr = (AI={alt_est:.2f}/AF={af:.2f}) × {mag:.1f}")

    return fx*fator, fy*fator, mag_t, nome_ch, tipo_saida, ang_ch

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div>
    <div style="font-size:2rem;line-height:1">⚡</div>
  </div>
  <div>
    <h1>Cálculo de Esforços Mecânicos</h1>
    <div class="sub">DIS-NOR-012 Rev.08 · DIS-NOR-014 Rev.2024 · Elektro</div>
  </div>
  <div style="margin-left:auto"><span class="badge">REV 2024</span></div>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── LAYOUT PRINCIPAL: esquerda=formulários, direita=poste ─────────────────────
col_form, col_viz = st.columns([3, 2], gap="large")

# Variáveis de visualização
viz_tipo_n1 = viz_tipo_n2 = viz_tipo_sec = "Conv"
viz_ang_n1 = viz_ang_n2 = viz_ang_sec = 0
viz_saida_n1 = viz_saida_n2 = viz_saida_sec = "Fim de linha"
fx1=fy1=mag1=fx2=fy2=mag2=fx_s=fy_s=mag_s=0.0
tem_n1=tem_n2=tem_sec=False

with col_form:
    # ── IDENTIFICAÇÃO ──────────────────────────────────────────────────────
    with st.expander("📋  Identificação do Pedido", expanded=False):
        c1,c2,c3,c4 = st.columns(4)
        c1.text_input("Nº Pedido"); c2.text_input("Nº OS")
        c3.text_input("Data");      c4.text_input("Local / OI-ODI")

    # ── POSTE ──────────────────────────────────────────────────────────────
    st.markdown('<div class="panel-title">DADOS DO POSTE</div>', unsafe_allow_html=True)
    with st.container(border=False):
        c1,c2 = st.columns(2)
        ALTURAS=[9,10,11,12,14,16]; CLASSES=[200,300,400,600,1000,1500]
        altura_poste = float(c1.selectbox("Altura (m)", ALTURAS, index=ALTURAS.index(12)))
        classe_poste = c2.selectbox("Classe (daN)", CLASSES, index=CLASSES.index(600))
        af_poste  = ALTURA_FINAL[int(altura_poste)]
        _eng      = round(altura_poste*0.10+0.60, 2)
        alt_util  = round(altura_poste-0.20-_eng, 2)
        st.markdown(f"""
<div style="background:#161b22;border:1px solid #21262d;border-radius:6px;padding:10px 14px;font-size:0.8rem;display:flex;gap:24px;margin-top:4px">
  <span style="color:#8b949e">Engastamento: <strong style="color:#e6edf3">{_eng:.2f} m</strong></span>
  <span style="color:#8b949e">Altura útil: <strong style="color:#e6edf3">{alt_util:.2f} m</strong></span>
  <span style="color:#f6a800">AF (norma): <strong>{af_poste:.2f} m</strong></span>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 1º NÍVEL ───────────────────────────────────────────────────────────
    st.markdown('<div class="panel-title">1º NÍVEL — REDE PRIMÁRIA</div>', unsafe_allow_html=True)
    tem_n1 = st.checkbox("Possui 1º nível de rede primária", key="cb_n1")
    if tem_n1:
        with st.container(border=True):
            fx1,fy1,mag1,viz_tipo_n1,viz_saida_n1,viz_ang_n1 = painel_nivel("1º Nível","n1",af_poste,af_poste,altura_poste,fixo_alt=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 2º NÍVEL ───────────────────────────────────────────────────────────
    st.markdown('<div class="panel-title">2º NÍVEL — REDE PRIMÁRIA (OPCIONAL)</div>', unsafe_allow_html=True)
    tem_n2 = st.checkbox("Possui 2º nível de rede primária", key="cb_n2")
    if tem_n2:
        with st.container(border=True):
            fx2,fy2,mag2,viz_tipo_n2,viz_saida_n2,viz_ang_n2 = painel_nivel("2º Nível","n2",max(0.0,af_poste-1.0),af_poste,altura_poste,fixo_alt=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── SECUNDÁRIA ─────────────────────────────────────────────────────────
    st.markdown('<div class="panel-title">REDE SECUNDÁRIA — BT</div>', unsafe_allow_html=True)
    tem_sec = st.checkbox("Possui rede secundária (BT)", key="cb_sec")
    if tem_sec:
        with st.container(border=True):
            fx_s,fy_s,mag_s,viz_tipo_sec,viz_saida_sec,viz_ang_sec = painel_nivel("Secundária BT","sec",max(0.0,alt_util-3.0),af_poste,altura_poste,is_bt=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── RESULTADO ──────────────────────────────────────────────────────────
    st.markdown('<div class="panel-title">RESULTADO FINAL</div>', unsafe_allow_html=True)
    rx  = fx1+fx2+fx_s
    ry  = fy1+fy2+fy_s
    mag = math.sqrt(rx**2+ry**2)
    ang = math.degrees(math.atan2(ry,rx))%360
    margem = classe_poste - mag

    c1,c2,c3 = st.columns(3)
    c1.metric("1º Nível (daN)",  f"{mag1:.1f}")
    c2.metric("2º Nível (daN)",  f"{mag2:.1f}" if tem_n2  else "—")
    c3.metric("Secundária (daN)",f"{mag_s:.1f}" if tem_sec else "—")

    st.markdown("<br>", unsafe_allow_html=True)
    cor_mag = "ok" if margem>=0 else "err"
    st.markdown(f"""
<div style="display:flex;gap:12px;margin-bottom:8px">
  <div style="flex:2;background:#161b22;border:1px solid {'#3fb950' if margem>=0 else '#f85149'};border-radius:10px;padding:16px;text-align:center">
    <div style="font-size:0.68rem;color:#8b949e;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Resultante Total</div>
    <div style="font-family:'Barlow Condensed',sans-serif;font-size:2.8rem;font-weight:700;color:{'#3fb950' if margem>=0 else '#f85149'};line-height:1">{mag:.1f}</div>
    <div style="font-size:0.75rem;color:#8b949e">daN · {ang:.1f}°</div>
  </div>
  <div style="flex:1;background:#161b22;border:1px solid #21262d;border-radius:10px;padding:16px;text-align:center">
    <div style="font-size:0.68rem;color:#8b949e;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Margem</div>
    <div style="font-family:'Barlow Condensed',sans-serif;font-size:2rem;font-weight:700;color:{'#3fb950' if margem>=0 else '#f85149'};line-height:1">{margem:+.0f}</div>
    <div style="font-size:0.75rem;color:#8b949e">daN ({classe_poste} daN classe)</div>
  </div>
</div>
""", unsafe_allow_html=True)

    if margem >= 0:
        st.success(f"✅ Poste {int(altura_poste)} m / {classe_poste} daN suporta com margem de **{margem:.1f} daN**.")
    else:
        prox = next((c for c in CLASSES if c>=mag), None)
        st.error(f"🔴 Excede em **{abs(margem):.1f} daN**." + (f" Use classe **{prox} daN**." if prox else ""))

    with st.expander("📐 Fórmulas (DIS-NOR-012 / DIS-NOR-014)"):
        st.markdown(f"""
**Transferência (6.9.7):** Fr = (AI / AF) × TI — AF poste {int(altura_poste)}m = **{af_poste:.2f} m**

**Resultante (6.13.6):** R = √(F₁² + F₂² + 2·F₁·F₂·cos β),  β = 180°−α

**Tangente mesmo cabo:** R = 0 — forças opostas iguais cancelam.
""")

# ── COLUNA DIREITA — VISUALIZAÇÃO DO POSTE ────────────────────────────────────
with col_viz:
    st.markdown('<div class="panel-title">VISUALIZAÇÃO DO POSTE</div>', unsafe_allow_html=True)
    svg = desenho_poste(
        altura_m   = altura_poste,
        tem_n1     = tem_n1,    tipo_n1  = viz_tipo_n1,
        tem_n2     = tem_n2,    tipo_n2  = viz_tipo_n2,
        tem_sec    = tem_sec,   tipo_sec = viz_tipo_sec,
        af         = af_poste,
        ang_ch_n1  = viz_ang_n1,  tipo_saida_n1  = viz_saida_n1,
        ang_ch_n2  = viz_ang_n2,  tipo_saida_n2  = viz_saida_n2,
        ang_ch_sec = viz_ang_sec, tipo_saida_sec = viz_saida_sec,
    )
    st.markdown(svg, unsafe_allow_html=True)

    # Legenda
    st.markdown("""
<div style="margin-top:12px;background:#161b22;border-radius:8px;padding:12px 14px">
  <div style="font-size:0.65rem;color:#8b949e;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;font-family:'Barlow Condensed',sans-serif">LEGENDA DE CABOS</div>
  <div style="display:flex;flex-wrap:wrap;gap:8px;font-size:0.72rem">
    <span><span style="color:#a8b4bf">━</span> Convencional</span>
    <span><span style="color:#4fc3f7">━</span> Protegida</span>
    <span><span style="color:#81c784">━</span> Compacta</span>
    <span><span style="color:#ffb74d">━</span> Pré-Reunido (PA)</span>
    <span><span style="color:#ce93d8">━</span> Pré-Reunido (PB)</span>
    <span><span style="color:#ef9a9a">━</span> CAZ/CAW</span>
    <span><span style="color:#4d90fe">●</span> Isolador</span>
  </div>
</div>
""", unsafe_allow_html=True)

    # Tabela resumo compacta
    if tem_n1 or tem_n2 or tem_sec:
        st.markdown("""<div style="margin-top:12px;background:#161b22;border-radius:8px;padding:12px 14px">
<div style="font-size:0.65rem;color:#8b949e;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;font-family:'Barlow Condensed',sans-serif">RESUMO DAS ESTRUTURAS</div>""", unsafe_allow_html=True)
        rows = []
        if tem_n1:  rows.append(("1º Nível", f"{af_poste:.2f} m",  f"{mag1:.1f} daN"))
        if tem_n2:  rows.append(("2º Nível", f"{af_poste-1.0:.2f} m", f"{mag2:.1f} daN"))
        if tem_sec: rows.append(("Secundária",f"{alt_util-3.0:.2f} m",f"{mag_s:.1f} daN"))
        for r in rows:
            st.markdown(f"""<div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #21262d;font-size:0.78rem">
<span style="color:#8b949e">{r[0]}</span><span>{r[1]}</span><span style="color:#f6a800;font-weight:600">{r[2]}</span></div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div style="margin-top:24px;text-align:center;font-size:0.7rem;color:#484f58">Cálculos conforme DIS-NOR-012 Rev.08 e DIS-NOR-014 Rev.2024 — Elektro · Validar com engenheiro responsável</div>', unsafe_allow_html=True)
