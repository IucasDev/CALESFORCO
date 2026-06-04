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

# AF = altura transferida a 0,10 m do topo (DIS-NOR-012 item 6.13.4)
# Exemplos da norma: 9m→7,4  11m→9,2  12m→10,1
ALTURA_FINAL = {9:7.4, 10:8.3, 11:9.2, 12:10.1, 14:11.9, 16:13.7}

# Tabela 14 — Trações por fase dos condutores nus (DIS-NOR-012 item 6.13.9)
# Usados em rede primária convencional nua e rede secundária nua
TRACAO_CONV = {
    # CA — Alumínio SEM alma de aço (Tabela 14)
    "A04":    60,
    "A02":    86,
    "A20":  173,
    "A40":  274,
    "A336":436,
    "A477":619,
    "C02":  171,
    "C04":  107,
    "C06":  60,
    "C120": 568,
    "C20":  342,
    "C25":  106,
    "C35":  155,
    "C40":  544,
    "C70":  296,
    "S04":  219,
    "S02":  347,
    "S20":  696,
    "S40":  1108,
    "S336": 1388,
    "S477": 2497,
}
FAMILIAS_CONV = {
    "CA — Alum. s/ alma de aço": ["A04","A02","A20","A40","A336","A477"],
    "CAA — Alum. c/ alma de aço":["C02","C04","C06","C120","C20","C25","C35","C40","C70"],
    "Cu — Cobre nu":             ["S04","S02","S20","S40","S336","S477"],
}
CABOS_BT = {
    "CA — Alumínio": ["A04","A02","A20","A40","A336","A477"],
    "Cu — Cobre":    ["S04","S02","S20","S40","S336","S477"],
}
TRACAO_PA = {"PA50":311,"PA70":375,"PA95":469,"PA120":527,"PA185":683,"PA240":796}
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
    "A50P":      {10:461,15:469,20:477,25:486,30:495,35:503,40:516,45:537,50:555,55:571,60:586,65:600,70:612,75:623,80:632},
    "A70P":      {10:468,15:483,20:498,25:514,30:530,35:544,40:558,45:582,50:604,55:624,60:641,65:657,70:672,75:685,80:697},
    "A120P":     {10:489,15:521,20:553,25:584,30:614,35:641,40:665,45:692,50:722,55:749,60:774,65:797,70:818,75:837,80:854},
    "A180P":     {10:514,15:562,20:610,25:655,30:697,35:735,40:770,45:802,50:837,55:872,60:903,65:933,70:960,75:985,80:1008},
}
VOS_CAZ = [50,100,150,200,300,400,500,600]
TRACAO_PROT = {
    "URBANO15KVA50P":240,"URBANO15KVA70P":321,"URBANO15KVA120P":510,
    "URBANO15KVA185P":400,"URBANO15KVA240P":720,
    "RURAL15KVA50P":334,"RURAL15KVA70P":407,"RURAL15KVA120P":584,
    "RURAL15KVA185P":400,"RURAL15KVA240P":1366,
    "URBANO36,2KVA70P":426,"URBANO36,2KVA120P":581,
    "URBANO36,2KVA185P":822,
    "RURAL36,2KVA70P":524,"RURAL36,2KVA120P":779,
    "RURAL36,2KVA185P":1584,
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
    "URBANO36,2KVA70P":{15:433,20:475,25:514,30:557,35:600,40:640,45:676,50:710,55:741,60:770},
    "URBANO36,2KVA185P":{15:521,20:588,25:650,30:707,35:767,40:822,45:874,50:922,55:966,60:1008},
    "RURAL36,2KVA70P":{15:542,20:633,25:715,30:790,35:859,40:923,45:983,50:1039,55:1092,60:1141,65:1187,70:1231,75:1273,80:1312,85:1349,90:1384,95:1417,100:1448},
    "RURAL36,2KVA185P":{15:630,20:741,25:840,30:932,35:1017,40:1096,45:1170,50:1239,55:1305,60:1367,65:1425,70:1481,75:1534,80:1584,85:1631,90:1677,95:1720,100:1761},
}
COMPACTA_FIXO = {
    "URBANO15KVA50P":240,"URBANO15KVA70P":321,"URBANO15KVA120P":510,
    "RURAL15KVA50P":334,"RURAL15KVA70P":407,"RURAL15KVA120P":584,
    "URBANO36,2KVA70P":426,"URBANO36,2KVA120P":581,
    "RURAL36,2KVA70P":524,"RURAL36,2KVA120P":779,
    "URBANO15KVA185P":400,"RURAL15KVA185P":400,
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
        cabo = c3.selectbox("Cabo", ["A50P","A70P","A120P","A185P","A240P"], key=f"{pfx}_cabo")
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
    st.markdown(f"""
<div class="section-card {'active' if alt_default>0 else ''}">
  <p class="panel-title">{titulo}</p>
""", unsafe_allow_html=True)

    if fixo_alt:
        alt_est = float(alt_default)
        st.markdown(f'<div style="background:#1a2d1a;border:1px solid #3fb950;border-radius:6px;padding:10px 12px;margin-bottom:12px;font-size:0.8rem">Altura estimada: <b>{alt_est:.2f} m</b></div>', unsafe_allow_html=True)
    else:
        alt_est = st.number_input("Altura estimada (m)", 0.0, float(altura_poste), alt_default, key=f"{idx}_alt")

    c1,c2 = st.columns(2)
    ang = ang_slider("Ângulo (α)", 0, key=f"{idx}_ang")
    if is_bt:
        tracao, nome_tipo = w_cabo_bt(idx)
    else:
        tracao, nome_tipo = w_cabo_at(idx)

    # ── CÁLCULO ───────────────────────────────────────────────────────────────────
    # Fr = (AI / AF) × TI
    # AI = altura estimada
    # AF = altura transferida a 0,10 m do topo (ALTURA_FINAL)
    # TI = tração inicial
    
    if af == 0:
        st.error("Erro: Altura final (AF) é zero. Verifique a altura do poste.")
        return 0.0, 0.0, 0.0

    fr = (alt_est / af) * tracao

    st.caption(f"⚡ Força resultante: **{fr:.0f} daN**")

    # Componentes retangulares
    fx = fr * math.cos(math.radians(ang))
    fy = fr * math.sin(math.radians(ang))

    st.markdown("</div>", unsafe_allow_html=True)
    return fx, fy, fr


# ── INTERFACE ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <img src="https://www.elektro.com.br/Static/img/logo.png" width="40" />
  <div>
    <h1>Esforços Mecânicos</h1>
    <p class="sub">Cálculo de esforços em postes conforme DIS-NOR-012 e DIS-NOR-014 <span class="badge">v1.0</span></p>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

c1,c2 = st.columns(2)
altura_poste = c1.selectbox("Altura do poste (m)", list(ALTURA_FINAL.keys()), index=2)
classe_poste = c2.selectbox("Classe do poste (daN)", [150,200,300,400,600,1000,1500,2000,3000,4000], index=3)

af_poste = ALTURA_FINAL.get(altura_poste, 0.0)
alt_util = af_poste # Definindo alt_util como a altura útil (AF) para cálculos secundários

st.markdown("<br>", unsafe_allow_html=True)

# ── PRIMÁRIA ──────────────────────────────────────────────────────────────────
st.markdown('<div class="panel-title">REDE PRIMÁRIA</div>', unsafe_allow_html=True)

# 1º Nível
fx1,fy1,mag1 = painel_nivel("1º Nível","n1",altura_poste-1.0,af_poste,altura_poste,fixo_alt=True)

st.markdown("<br>", unsafe_allow_html=True)

# 2º Nível
tem_n2 = st.checkbox("Possui 2º nível de rede primária", key="cb_n2")
if tem_n2:
    fx2,fy2,mag2 = painel_nivel("2º Nível","n2",altura_poste-2.0,af_poste,altura_poste)
else:
    fx2,fy2,mag2 = 0.0,0.0,0.0

st.markdown("<br>", unsafe_allow_html=True)

# ── SECUNDÁRIA ─────────────────────────────────────────────────────────
st.markdown('<div class="panel-title">REDE SECUNDÁRIA — BT</div>', unsafe_allow_html=True)
tem_sec = st.checkbox("Possui rede secundária (BT)", key="cb_sec")
if tem_sec:
    with st.container(border=True):
        fx_s,fy_s,mag_s = painel_nivel("Secundária BT","sec",max(0.0,alt_util-3.0),af_poste,altura_poste,is_bt=True)
else:
    fx_s,fy_s,mag_s = 0.0,0.0,0.0

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
    CLASSES = [150,200,300,400,600,1000,1500,2000,3000,4000]
    prox = next((c for c in CLASSES if c>=mag), None)
    st.error(f"🔴 Excede em **{abs(margem):.1f} daN**." + (f" Use classe **{prox} daN**." if prox else ""))

with st.expander("📐 Fórmulas (DIS-NOR-012 / DIS-NOR-014)"):
    st.markdown(f"""
**Transferência (6.13.4):** Fr = (AI / AF) × TI — AF = altura − 0,10m do topo → poste {int(altura_poste)}m = **{af_poste:.2f} m**

**Resultante (6.13.6):** R = √(F₁² + F₂² + 2·F₁·F₂·cos β),  β = 180°−α

**Tangente mesmo cabo:** R = 0 — forças opostas iguais cancelam.
""")
