import streamlit as st
import math

st.set_page_config(page_title="Cálculo de Esforços Mecânicos", page_icon="🏗️", layout="wide")
st.title("🏗️ Cálculo de Esforços Mecânicos em Postes")
st.caption("Conforme DIS-NOR-012 Rev.08 e DIS-NOR-014 Rev.2024 — Elektro")

# ─────────────────────────────────────────────────────────────────────────────
# AF = altura − 0,20 m  (DIS-NOR-014 item 6.9.7)
# ─────────────────────────────────────────────────────────────────────────────
ALTURA_FINAL = {9:8.80, 10:9.80, 11:10.80, 12:11.80, 14:13.80, 16:15.80}

# ─────────────────────────────────────────────────────────────────────────────
# TABELAS — todos os valores extraídos da planilha Cálculo_Esforço_2024
# ─────────────────────────────────────────────────────────────────────────────

# Rede Convencional — cabo unitário (daN/cabo)
TRACAO_CONV = {
    # S = Alumínio com alma de aço
    "S04": 219, "S02": 347,  "S20": 696,  "S40": 1108,
    "S33": 1388, "S47": 2497,
    "S40TR": 807, "S33TR": 857, "S47TR": 756,
    # A = Alumínio sem alma de aço
    "A04": 60,  "A02": 86,   "A20": 173,  "A40": 274,
    "A33": 436, "A47": 619,
    # C = Cobre
    "C06": 60,  "C04": 107,  "C02": 171,  "C20": 342,
    "C40": 544, "C25": 106,  "C35": 155,  "C70": 296, "C120": 568,
}
FAMILIAS_CONV = {
    "S — Alumínio c/ alma de aço": ["S04","S02","S20","S40","S33","S47","S40TR","S33TR","S47TR"],
    "A — Alumínio s/ alma de aço": ["A04","A02","A20","A40","A33","A47"],
    "C — Cobre":                   ["C06","C04","C02","C20","C40","C25","C35","C70","C120"],
}

# Pré-reunido PRIMÁRIA (PA) — tração fixa (daN) — planilha Dados
TRACAO_PA = {
    "PA50":  311, "PA70":  375, "PA95":  469,
    "PA120": 527, "PA185": 683, "PA240": 795,
}

# Pré-reunido BT (PB) — tração varia com vão (m)
TRACAO_PB = {
    "PB35":  {5:4,  10:14, 15:32, 20:56,  25:88,  30:127, 35:172, 40:225},
    "PB50":  {5:6,  10:24, 15:51, 20:91,  25:142, 30:204, 35:278, 40:363},
    "PB70":  {5:7,  10:30, 15:67, 20:119, 25:186, 30:267, 35:364, 40:475},
    "PB120": {5:8,  10:33, 15:74, 20:132, 25:206, 30:296, 35:403, 40:527},
}
VOS_PB = [5, 10, 15, 20, 25, 30, 35, 40]

# CAZ / CAW — tração varia com vão (m)
TRACAO_CAZ = {
    "CAZ 3,09":   {50:229,100:256,150:263,200:282,300:318,400:349,500:376,600:400},
    "CAZ 3x2,25": {50:357,100:395,150:406,200:436,300:491,400:540,500:580,600:615},
    "CAW 3,26":   {50:244,100:273,150:276,200:296,300:334,400:368,500:398,600:426},
    "CAW 3x2,59": {50:438,100:492,150:495,200:524,300:588,400:645,500:696,600:741},
    "CAA 04":     {50:217,100:269,150:313,200:324,300:324,400:324,500:324,600:324},
}
VOS_CAZ = [50, 100, 150, 200, 300, 400, 500, 600]

# Rede Protegida — cabo unitário (daN)
TRACAO_PROT = {
    "URBANO15KVA50P":240,  "URBANO15KVA70P":321,  "URBANO15KVA120P":510,
    "RURAL15KVA50P":334,   "RURAL15KVA70P":407,   "RURAL15KVA120P":584,
    "URBANO36,2KVA70P":426,"URBANO36,2KVA120P":581,
    "RURAL36,2KVA70P":524, "RURAL36,2KVA120P":779,
    "URBANO15KVA185P":400, "RURAL15KVA185P":400,
}

# Rede Compacta — tração fixo por vão 40m (daN)
COMPACTA_FIXO = {
    "URBANO15KVA35P":405,  "URBANO15KVA50P":516,  "URBANO15KVA70P":468,
    "URBANO15KVA120P":665, "URBANO15KVA185P":643, "URBANO15KVA240P":720,
    "RURAL15KVA35P":872,   "RURAL15KVA50P":1035,  "RURAL15KVA70P":978,
    "RURAL15KVA120P":1257, "RURAL15KVA185P":1248, "RURAL15KVA240P":1366,
    "URBANO36,2KVA70P":640,"URBANO36,2KVA120P":805,"URBANO36,2KVA185P":822,
    "RURAL36,2KVA70P":1312,"RURAL36,2KVA120P":1577,"RURAL36,2KVA185P":1584,
    "RURAL > 80m15KVA35P":945,  "RURAL > 80m15KVA50P":1795,
    "RURAL > 80m15KVA70P":1067, "RURAL > 80m15KVA120P":1797,
    "RURAL > 80m15KVA185P":1375,"RURAL > 80m15KVA240P":1510,
}

# Rede Compacta — tração varia com vão
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

# ─────────────────────────────────────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────────────────────────────────────

def interpolar(tabela, v):
    keys = sorted(tabela.keys())
    if v <= keys[0]:  return float(tabela[keys[0]])
    if v >= keys[-1]: return float(tabela[keys[-1]])
    for i in range(len(keys)-1):
        k1, k2 = keys[i], keys[i+1]
        if k1 <= v <= k2:
            return float(tabela[k1] + (tabela[k2]-tabela[k1])*(v-k1)/(k2-k1))
    return 0.0

def get_compacta(local, tensao, cabo, vao):
    key = f"{local}{tensao}{cabo}"
    if key in COMPACTA_VAO:
        return interpolar(COMPACTA_VAO[key], vao)
    return float(COMPACTA_FIXO.get(key, 0))

ANGULOS = list(range(0, 365, 5))
def slider_ang(label, default, key):
    return st.select_slider(label, options=ANGULOS, value=default, key=key)

# ─────────────────────────────────────────────────────────────────────────────
# WIDGET CABO — PRIMÁRIA
# ─────────────────────────────────────────────────────────────────────────────

def widget_cabo_at(pfx):
    tipo = st.selectbox("Tipo de rede", [
        "Convencional (S / A / C)",
        "Pré-Reunido Primária (PA)",
        "CAZ / CAW",
        "Protegida",
        "Compacta",
    ], key=f"{pfx}_tipo")
    t = 0.0

    if tipo == "Convencional (S / A / C)":
        c1, c2, c3 = st.columns(3)
        qtd    = c1.number_input("Qtd. cabos/fase", 1, 10, 3, key=f"{pfx}_qtd")
        fam    = c2.selectbox("Família", list(FAMILIAS_CONV.keys()), key=f"{pfx}_fam")
        cabo   = c3.selectbox("Cabo", FAMILIAS_CONV[fam], key=f"{pfx}_cabo")
        t = float(TRACAO_CONV.get(cabo, 0)) * qtd
        st.caption("S=alum. c/ alma aço | A=alum. s/ alma | C=cobre | TR=tração reduzida")

    elif tipo == "Pré-Reunido Primária (PA)":
        c1, c2 = st.columns(2)
        cabo = c1.selectbox("Cabo", list(TRACAO_PA.keys()), key=f"{pfx}_cabo")
        qtd  = c2.number_input("Qtd. cabos", 1, 6, 1, key=f"{pfx}_qtd")
        t = float(TRACAO_PA.get(cabo, 0)) * qtd
        st.caption("Tração fixa conforme planilha DIS-NOR-014.")

    elif tipo == "CAZ / CAW":
        c1, c2 = st.columns(2)
        cabo = c1.selectbox("Cabo", list(TRACAO_CAZ.keys()), key=f"{pfx}_cabo")
        vao  = c2.select_slider("Vão (m)", VOS_CAZ, value=100, key=f"{pfx}_vao")
        t = interpolar(TRACAO_CAZ[cabo], vao)

    elif tipo == "Protegida":
        c1, c2, c3 = st.columns(3)
        local  = c1.selectbox("Local", ["URBANO","RURAL"], key=f"{pfx}_loc")
        tensao = c2.selectbox("Tensão", ["15KV","36,2KV"], key=f"{pfx}_tens")
        cabo   = c3.selectbox("Cabo", ["A50P","A70P","A120P","A185P"], key=f"{pfx}_cabo")
        t = float(TRACAO_PROT.get(f"{local}{tensao}{cabo}", 0))

    elif tipo == "Compacta":
        c1, c2, c3, c4 = st.columns(4)
        local  = c1.selectbox("Local", ["URBANO","RURAL","RURAL > 80m"], key=f"{pfx}_loc")
        tensao = c2.selectbox("Tensão", ["15KV","36,2KV"], key=f"{pfx}_tens")
        cabo   = c3.selectbox("Cabo", ["A35P","A50P","A70P","A120P","A185P","A240P"], key=f"{pfx}_cabo")
        vao    = c4.number_input("Vão (m)", 10, 100, 40, step=5, key=f"{pfx}_vao")
        t = get_compacta(local, tensao, cabo, vao)

    st.caption(f"Tração: **{t:.0f} daN**")
    return float(t)

# ─────────────────────────────────────────────────────────────────────────────
# WIDGET CABO — SECUNDÁRIA BT
# ─────────────────────────────────────────────────────────────────────────────

CABOS_BT_CONV = {
    "A — Alumínio": ["A04","A02","A20","A40","A33","A47"],
    "C — Cobre":    ["C06","C04","C02","C20","C40","C25","C35","C70","C120"],
}

def widget_cabo_bt_conv(pfx, label):
    """Seletor de um cabo BT convencional (fase, neutro ou controle)."""
    st.markdown(f"**{label}**")
    c1, c2 = st.columns(2)
    fam  = c1.selectbox("Família", list(CABOS_BT_CONV.keys()), key=f"{pfx}_fam")
    cabo = c2.selectbox("Cabo", CABOS_BT_CONV[fam], key=f"{pfx}_cabo")
    return float(TRACAO_CONV.get(cabo, 0)), cabo

def widget_cabo_bt(pfx):
    tipo = st.selectbox("Tipo de cabo BT", [
        "Convencional (A / C)",
        "Pré-Reunido BT (PB)",
        "CAZ / CAW",
    ], key=f"{pfx}_tipo")
    t = 0.0

    if tipo == "Convencional (A / C)":
        # Fases
        st.markdown("##### Fases")
        c1, c2, c3 = st.columns(3)
        qtd_f = c1.number_input("Qtd. cabos fase", 1, 4, 3, key=f"{pfx}_qtdf")
        fam_f = c2.selectbox("Família fase", list(CABOS_BT_CONV.keys()), key=f"{pfx}_famf")
        cabo_f = c3.selectbox("Cabo fase", CABOS_BT_CONV[fam_f], key=f"{pfx}_cabof")
        t_fase = float(TRACAO_CONV.get(cabo_f, 0)) * qtd_f
        # Neutro
        st.markdown("##### Neutro")
        c4, c5 = st.columns(2)
        fam_n  = c4.selectbox("Família neutro", list(CABOS_BT_CONV.keys()), key=f"{pfx}_famn")
        cabo_n = c5.selectbox("Cabo neutro", CABOS_BT_CONV[fam_n], key=f"{pfx}_cabon")
        t_neutro = float(TRACAO_CONV.get(cabo_n, 0))
        # Controle
        st.markdown("##### Controle")
        c6, c7 = st.columns(2)
        fam_c  = c6.selectbox("Família controle", list(CABOS_BT_CONV.keys()), key=f"{pfx}_famc")
        cabo_c = c7.selectbox("Cabo controle", CABOS_BT_CONV[fam_c], key=f"{pfx}_caboc")
        t_ctrl = float(TRACAO_CONV.get(cabo_c, 0))
        t = t_fase + t_neutro + t_ctrl
        st.caption(f"Fase: {t_fase:.0f} + Neutro: {t_neutro:.0f} + Controle: {t_ctrl:.0f} = **{t:.0f} daN**")

    elif tipo == "Pré-Reunido BT (PB)":
        c1, c2 = st.columns(2)
        cabo = c1.selectbox("Cabo", list(TRACAO_PB.keys()), key=f"{pfx}_cabo")
        vao  = c2.select_slider("Vão (m)", VOS_PB, value=20, key=f"{pfx}_vao")
        t = interpolar(TRACAO_PB[cabo], vao)

    elif tipo == "CAZ / CAW":
        c1, c2 = st.columns(2)
        cabo = c1.selectbox("Cabo", list(TRACAO_CAZ.keys()), key=f"{pfx}_cabo")
        vao  = c2.select_slider("Vão (m)", VOS_CAZ, value=100, key=f"{pfx}_vao")
        t = interpolar(TRACAO_CAZ[cabo], vao)

    st.caption(f"Tração total: **{t:.0f} daN**")
    return float(t)

# ─────────────────────────────────────────────────────────────────────────────
# PAINEL DE NÍVEL (chegada + saída + cálculo vetorial)
# ─────────────────────────────────────────────────────────────────────────────

def painel_nivel(titulo, idx, alt_default, af, altura_poste, is_bt=False, fixo_alt=False):
    st.markdown(f"#### {titulo}")

    if fixo_alt:
        alt_est = float(alt_default)
        st.info(f"📏 Altura da estrutura (AI): **{alt_est:.2f} m** — fixo conforme norma Elektro")
    else:
        alt_est = st.number_input(
            "Altura da estrutura — AI (m)", 0.0, float(altura_poste),
            value=float(alt_default), step=0.1, key=f"{idx}_alt",
            help="AI = altura onde o cabo está fixado no poste"
        )

    st.markdown("---")
    col_ch, col_sa = st.columns(2)

    with col_ch:
        st.markdown("### ↙ Chegada")
        t_ch = widget_cabo_bt(f"{idx}_ch") if is_bt else widget_cabo_at(f"{idx}_ch")
        ang_ch = slider_ang("Ângulo de chegada (°)", 0, f"{idx}_ang_ch")
        st.caption("0°=Leste | 90°=Norte | 180°=Oeste | 270°=Sul")

    with col_sa:
        st.markdown("### ↗ Saída")
        tipo_saida = st.radio("O cabo...", [
            "Fim de linha (não sai nada)",
            "Sai na tangente — mesmo cabo",
            "Sai na tangente — cabo diferente",
            "Deriva em outro ângulo",
        ], key=f"{idx}_saida")

        t_sa, ang_sa = 0.0, 0

        if tipo_saida == "Fim de linha (não sai nada)":
            st.info("Só a tração de chegada atua no poste.")

        elif tipo_saida == "Sai na tangente — mesmo cabo":
            t_sa   = t_ch
            ang_sa = (ang_ch + 180) % 360
            st.caption(f"Mesmo cabo ({t_ch:.0f} daN) — saída a {ang_sa}°.")
            st.info("Cabo reto, mesma seção → forças se cancelam → **resultante = 0**. Correto.")

        elif tipo_saida == "Sai na tangente — cabo diferente":
            t_sa   = widget_cabo_bt(f"{idx}_sa") if is_bt else widget_cabo_at(f"{idx}_sa")
            ang_sa = (ang_ch + 180) % 360
            st.caption(f"Saída a {ang_sa}° (tangente) — cabos diferentes → resultante = |T₁−T₂|.")

        else:
            t_sa   = widget_cabo_bt(f"{idx}_sa") if is_bt else widget_cabo_at(f"{idx}_sa")
            ang_sa = slider_ang("Ângulo de saída (°)", 90, f"{idx}_ang_sa")

    # Cálculo vetorial
    fx = t_ch * math.cos(math.radians(ang_ch))
    fy = t_ch * math.sin(math.radians(ang_ch))
    if tipo_saida != "Fim de linha (não sai nada)":
        fx += t_sa * math.cos(math.radians(ang_sa))
        fy += t_sa * math.sin(math.radians(ang_sa))
    mag = math.sqrt(fx**2 + fy**2)

    # Ângulo de deflexão α
    if tipo_saida != "Fim de linha (não sai nada)":
        diff  = abs(ang_sa - ang_ch) % 360
        alpha = min(diff, 360 - diff)
    else:
        alpha = 0.0

    # Transferência de altura: Fr = (AI/AF) × TI
    fator = alt_est / af if af > 0 else 1.0
    mag_t = mag * fator
    fx_t  = fx  * fator
    fy_t  = fy  * fator

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tração chegada (daN)", f"{t_ch:.0f}")
    c2.metric("Tração saída (daN)",   f"{t_sa:.0f}")
    c3.metric("Ângulo deflexão α",    f"{alpha:.0f}°")
    c4.metric("🔴 Resultante transf. (daN)", f"{mag_t:.1f}",
              help=f"Fr = (AI={alt_est:.2f} / AF={af:.2f}) × {mag:.1f} daN")

    return fx_t, fy_t, mag_t

# ─────────────────────────────────────────────────────────────────────────────
# INTERFACE PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

with st.expander("📋 Identificação do Pedido", expanded=False):
    c1, c2, c3, c4 = st.columns(4)
    c1.text_input("Nº Pedido"); c2.text_input("Nº OS")
    c3.text_input("Data");      c4.text_input("Local / OI-ODI")

st.divider()

# ── DADOS DO POSTE ─────────────────────────────────────────────────────────
st.subheader("🪝 Dados do Poste")
ALTURAS = [9, 10, 11, 12, 14, 16]
CLASSES = [200, 300, 400, 600, 1000, 1500]

c1, c2, c3 = st.columns(3)
altura_poste = float(c1.selectbox("Altura do poste (m)", ALTURAS, index=ALTURAS.index(12)))
classe_poste = c2.selectbox("Classe do poste (daN)", CLASSES, index=CLASSES.index(600))
af_poste     = ALTURA_FINAL[int(altura_poste)]
_eng         = round(altura_poste * 0.10 + 0.60, 2)
alt_util     = round(altura_poste - 0.20 - _eng, 2)

with c3:
    st.markdown("**Alturas calculadas — Elektro / Norma**")
    st.caption(f"Topo: −0,20 m | Engastamento: −{_eng:.2f} m ({int(altura_poste)}m×10%+0,60)")
    st.info(f"Altura útil (AI ref.): **{alt_util:.2f} m**\nAltura final AF (norma): **{af_poste:.2f} m**")

st.divider()

# ── 1º NÍVEL ───────────────────────────────────────────────────────────────
st.subheader("⚡ 1º Nível — Rede Primária")
tem_n1 = st.checkbox("Este poste possui 1º nível de rede primária")
fx1, fy1, mag1 = 0.0, 0.0, 0.0
if tem_n1:
    with st.container(border=True):
        fx1, fy1, mag1 = painel_nivel("1º Nível", "n1", af_poste, af_poste, altura_poste, fixo_alt=True)

st.divider()

# ── 2º NÍVEL ───────────────────────────────────────────────────────────────
st.subheader("⚡ 2º Nível — Rede Primária (opcional)")
tem_n2 = st.checkbox("Este poste possui 2º nível de rede primária")
fx2, fy2, mag2 = 0.0, 0.0, 0.0
if tem_n2:
    with st.container(border=True):
        fx2, fy2, mag2 = painel_nivel("2º Nível", "n2", max(0.0, af_poste-1.0), af_poste, altura_poste, fixo_alt=True)

st.divider()

# ── SECUNDÁRIA ─────────────────────────────────────────────────────────────
st.subheader("🔋 Rede Secundária — BT")
tem_sec = st.checkbox("Este poste possui saída de rede secundária")
fx_s, fy_s, mag_s = 0.0, 0.0, 0.0
if tem_sec:
    with st.container(border=True):
        fx_s, fy_s, mag_s = painel_nivel("Secundária BT", "sec",
            max(0.0, alt_util - 3.0), af_poste, altura_poste, is_bt=True)

st.divider()

# ── RESULTADO FINAL ─────────────────────────────────────────────────────────
st.subheader("📊 Resultado Final")
rx  = fx1 + fx2 + fx_s
ry  = fy1 + fy2 + fy_s
mag = math.sqrt(rx**2 + ry**2)
ang = math.degrees(math.atan2(ry, rx)) % 360

c1,c2,c3,c4,c5,c6 = st.columns(6)
c1.metric("1º Nível (daN)",           f"{mag1:.1f}")
c2.metric("2º Nível (daN)",           f"{mag2:.1f}" if tem_n2  else "—")
c3.metric("Secundária (daN)",         f"{mag_s:.1f}" if tem_sec else "—")
c4.metric("🔴 Resultante TOTAL (daN)",f"{mag:.1f}")
c5.metric("Ângulo resultante",        f"{ang:.1f}°")
c6.metric("Classe do poste (daN)",    str(classe_poste))

if mag > 0:
    margem = classe_poste - mag
    if margem >= 0:
        st.success(f"✅ Esforço **{mag:.1f} daN** — poste {int(altura_poste)} m / {classe_poste} daN — margem: **{margem:.1f} daN**.")
    else:
        prox = next((c for c in CLASSES if c >= mag), None)
        st.error(f"🔴 Esforço **{mag:.1f} daN** EXCEDE classe {classe_poste} daN em **{abs(margem):.1f} daN**. "
                 + (f"Considere classe **{prox} daN**." if prox else "Consulte engenheiro."))

with st.expander("📐 Fórmulas utilizadas (DIS-NOR-012 / DIS-NOR-014)"):
    st.markdown(f"""
**Transferência de altura (6.9.7):** Fr = (AI / AF) × TI — AF poste {int(altura_poste)}m = **{af_poste:.2f} m**

**Resultante analítica (6.13.6):** R = √(F₁² + F₂² + 2·F₁·F₂·cos β) onde β = 180° − α

**Simplificada F₁=F₂ (6.13.7):** R = 2·F·sen(α/2)

**Tangente mesmo cabo:** R = 0 (correto — forças opostas iguais se cancelam)
""")

st.divider()
st.caption("Cálculos conforme DIS-NOR-012 Rev.08 e DIS-NOR-014 Rev.2024 — Elektro. Validar com engenheiro responsável.")
