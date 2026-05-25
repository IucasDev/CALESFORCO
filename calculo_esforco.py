import streamlit as st
import math

st.set_page_config(page_title="Cálculo de Esforços Mecânicos", page_icon="🏗️", layout="wide")

st.title("🏗️ Cálculo de Esforços Mecânicos em Postes")
st.caption("Conforme DIS-NOR-012 Rev.08 e DIS-NOR-014 Rev.2024 — Electro")

# ─────────────────────────────────────────────────────────────────────────────
# ALTURA FINAL (AF) — valores fixos conforme DIS-NOR-012 item 6.13.4
# AF = altura transferida a 0,10 m do topo
# Exemplos da norma: 9 m → 7,4 m | 11 m → 9,2 m | 12 m → 10,1 m
# Para os demais: AF = altura - 0,20 - (altura×10% + 0,60)
# ─────────────────────────────────────────────────────────────────────────────
ALTURA_FINAL = {
    9:  7.4,
    10: 8.3,
    11: 9.2,
    12: 10.1,
    14: 11.8,
    16: 13.6,
}

# ─────────────────────────────────────────────────────────────────────────────
# TABELAS DE DADOS — Condutores e trações (daN)
# ─────────────────────────────────────────────────────────────────────────────

# Condutores nus (Tabela 14 — DIS-NOR-012)
TRACAO_NUS = {
    # Alumínio sem alma de aço (CA)
    "4 CA":     60,
    "2 CA":     86,
    "2/0 CA":   173,
    "4/0 CA":   274,
    "336,4 CA": 436,
    # Alumínio com alma de aço (CAA)
    "4 CAA":      75,
    "1/0 CAA":   173,
    "4/0 CAA":   347,
    "336,4 CAA": 551,
    # Cobre nu
    "35mm² Cu":  244,
    "70mm² Cu":  477,
    "95mm² Cu":  663,
    "120mm² Cu": 892,
    # Alumínio liga (CAL)
    "77,47 MCM CAL":  72,
    "155,4 MCM CAL":  144,
    "246,9 MCM CAL":  227,
    "465,4 MCM CAL":  427,
}

# Cabos convencionais AT/MT (planilha original)
TRACAO_CABO = {
    "A02": 86,  "A04": 60,  "A20": 173, "A33": 436, "A40": 274,
    "A47": 619, "C02": 171, "C04": 107, "C06": 60,  "C20": 342,
    "C25": 106, "C35": 155, "C40": 544, "C70": 296, "C120": 568,
    "S04": 219, "S02": 347, "S20": 696, "S40": 1108,
    "S33": 1388, "S47": 2497,
    "A50P": 245, "A70P": 268, "A120P": 317, "A180P": 359,
}

# Pré-reunido / multiplexado BT — tração varia com vão (m)
TRACAO_PRE_REUNIDO = {
    "PB35":  {5:4,  10:14, 15:32, 20:56,  25:88,  30:127, 35:172, 40:225},
    "PB50":  {5:6,  10:24, 15:51, 20:91,  25:142, 30:204, 35:278, 40:363},
    "PB70":  {5:7,  10:30, 15:67, 20:119, 25:186, 30:267, 35:364, 40:475},
    "PB120": {5:8,  10:33, 15:74, 20:132, 25:206, 30:296, 35:403, 40:527},
}
VOS_PR = [5, 10, 15, 20, 25, 30, 35, 40]

# CAZ / CAW — tração varia com vão (m)
TRACAO_CAZ_CAW = {
    "CAZ 3,09":   {50:229,100:256,150:263,200:282,300:318,400:349,500:376,600:400},
    "CAZ 3x2,25": {50:357,100:395,150:406,200:436,300:491,400:540,500:580,600:615},
    "CAW 3,26":   {50:244,100:273,150:276,200:296,300:334,400:368,500:398,600:426},
    "CAW 3x2,59": {50:438,100:492,150:495,200:524,300:588,400:645,500:696,600:741},
    "CAA 04":     {50:217,100:269,150:313,200:324,300:324,400:324,500:324,600:324},
}
VOS_CAZ = [50, 100, 150, 200, 300, 400, 500, 600]

# Rede Protegida — cabo unitário
TRACAO_PROTEGIDA = {
    "URBANO15KVA50P":240,"URBANO15KVA70P":321,"URBANO15KVA120P":510,
    "RURAL15KVA50P":334,"RURAL15KVA70P":407,"RURAL15KVA120P":584,
    "URBANO36,2KVA70P":426,"URBANO36,2KVA120P":581,
    "RURAL36,2KVA70P":524,"RURAL36,2KVA120P":779,
    "URBANO15KVA185P":400,"RURAL15KVA185P":400,
}

# Rede Compacta — valores fixos
TRACAO_COMPACTA_FIXA = {
    "RURALS04":325,"RURALS02":454,"RURALS20":763,"RURALS40":1212,
    "RURALS33":1517,"RURALC25":315,"RURALC35":454,"RURALC70":864,
    "RURALC120":1658,"RURALS40TR":807,"RURALS33TR":857,"RURALS47TR":756,
    "URBANOA04":60,"URBANOA02":86,"URBANOA20":173,"URBANOA40":274,
    "URBANOA33":436,"URBANOA47":619,"URBANOC06":60,"URBANOC04":107,
    "URBANOC02":171,"URBANOC20":342,"URBANOC40":544,"URBANOC25":106,
    "URBANOC35":155,"URBANOC70":296,"URBANOC120":598,
}

# Rede Compacta — tração varia com vão
TABELA_COMPACTA = {
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

def get_tracao_compacta(local, tensao, cabo, vao):
    key = f"{local}{tensao}{cabo}"
    if key in TABELA_COMPACTA:
        return interpolar(TABELA_COMPACTA[key], vao)
    return float(TRACAO_COMPACTA_FIXA.get(f"{local}{cabo}", 0))

def calcular_resultante_norma(f1, f2, alpha_deg):
    """
    Fórmula analítica conforme DIS-NOR-012 item 6.13.6:
      R = sqrt(F1² + F2² + 2·F1·F2·cos β)
      β = 180° - α  (α = ângulo de deflexão entre os dois cabos)
    Quando F1 == F2 usa a simplificada 6.13.7: R = 2·F·sen(α/2)
    """
    beta = math.radians(180.0 - alpha_deg)
    return math.sqrt(f1**2 + f2**2 + 2*f1*f2*math.cos(beta))

def transferir_altura(tracao, ai, af):
    """
    Transferência de tração para AF conforme DIS-NOR-012 item 6.13.4:
      Fr = (AI / AF) × TI
    AI = altura inicial (onde o cabo está fixado)
    AF = altura final (0,10 m do topo, valor fixo por poste)
    """
    if af <= 0:
        return tracao
    return tracao * (ai / af)

ANGULOS = list(range(0, 365, 5))

def slider_ang(label, default, key):
    return st.select_slider(label, options=ANGULOS, value=default, key=key)

# ─────────────────────────────────────────────────────────────────────────────
# WIDGET DE SELEÇÃO DE CABO
# ─────────────────────────────────────────────────────────────────────────────

def widget_cabo(prefixo, label_cabecalho):
    st.markdown(f"**{label_cabecalho}**")
    tipo = st.selectbox(
        "Tipo de rede",
        ["Convencional (cabo nu)","Convencional (cabo isolado)","Protegida","Compacta"],
        key=f"{prefixo}_tipo"
    )
    tracao = 0.0

    if tipo == "Convencional (cabo nu)":
        c1, c2 = st.columns(2)
        qtd  = c1.number_input("Qtd. cabos por fase", 1, 6, 1, key=f"{prefixo}_qtd")
        cabo = c2.selectbox("Cabo", list(TRACAO_NUS.keys()), key=f"{prefixo}_cabo")
        tracao = float(TRACAO_NUS.get(cabo, 0)) * qtd

    elif tipo == "Convencional (cabo isolado)":
        c1, c2, c3 = st.columns(3)
        qtd   = c1.number_input("Qtd. cabos", 1, 10, 3, key=f"{prefixo}_qtd")
        local = c2.selectbox("Local", ["RURAL","URBANO"], key=f"{prefixo}_loc")
        cabo  = c3.selectbox("Cabo", list(TRACAO_CABO.keys()), key=f"{prefixo}_cabo")
        tracao = float(TRACAO_CABO.get(cabo, 0)) * qtd

    elif tipo == "Protegida":
        c1, c2, c3 = st.columns(3)
        local  = c1.selectbox("Local", ["URBANO","RURAL"], key=f"{prefixo}_locp")
        tensao = c2.selectbox("Tensão", ["15KV","36,2KV"], key=f"{prefixo}_tensp")
        cabo   = c3.selectbox("Cabo", ["A50P","A70P","A120P","A185P"], key=f"{prefixo}_cabop")
        tracao = float(TRACAO_PROTEGIDA.get(f"{local}{tensao}{cabo}", 0))

    elif tipo == "Compacta":
        c1, c2, c3, c4 = st.columns(4)
        local  = c1.selectbox("Local", ["URBANO","RURAL","RURAL > 80m"], key=f"{prefixo}_locc")
        tensao = c2.selectbox("Tensão", ["15KV","36,2KV"], key=f"{prefixo}_tensc")
        cabo   = c3.selectbox("Cabo", ["A35P","A50P","A70P","A120P","A185P","A240P"], key=f"{prefixo}_caboc")
        vao    = c4.number_input("Vão (m)", 10, 100, 30, step=5, key=f"{prefixo}_vaoc")
        tracao = get_tracao_compacta(local, tensao, cabo, vao)

    st.caption(f"Tração: **{tracao:.0f} daN**")
    return tracao

def widget_cabo_bt(prefixo, label_cabecalho):
    st.markdown(f"**{label_cabecalho}**")
    tipo = st.selectbox("Tipo de cabo", ["Pré-Reunido","CAZ/CAW","Convencional BT"], key=f"{prefixo}_tipo")
    tracao = 0.0

    if tipo == "Pré-Reunido":
        c1, c2 = st.columns(2)
        cabo = c1.selectbox("Cabo", list(TRACAO_PRE_REUNIDO.keys()), key=f"{prefixo}_cabo")
        vao  = c2.select_slider("Vão (m)", VOS_PR, value=20, key=f"{prefixo}_vao")
        tracao = interpolar(TRACAO_PRE_REUNIDO[cabo], vao)

    elif tipo == "CAZ/CAW":
        c1, c2 = st.columns(2)
        cabo = c1.selectbox("Cabo", list(TRACAO_CAZ_CAW.keys()), key=f"{prefixo}_cabo")
        vao  = c2.select_slider("Vão (m)", VOS_CAZ, value=100, key=f"{prefixo}_vao")
        tracao = interpolar(TRACAO_CAZ_CAW[cabo], vao)

    elif tipo == "Convencional BT":
        st.markdown("##### Fases")

        c1, c2 = st.columns(2)

        qtd_fase = c1.number_input(
            "Qtd. fases",
            1, 6, 3,
            key=f"{prefixo}_qtd_fase"
        )

        cabo_fase = c2.selectbox(
            "Cabo das fases",
            list(TRACAO_CABO.keys()),
            key=f"{prefixo}_cabo_fase"
        )

        tracao_fase = float(TRACAO_CABO.get(cabo_fase, 0)) * qtd_fase

        st.markdown("##### Neutro")

        usar_neutro = st.checkbox(
            "Possui neutro",
            value=True,
            key=f"{prefixo}_usa_neutro"
        )

        tracao_neutro = 0

        if usar_neutro:
            c3, c4 = st.columns(2)

            qtd_neutro = c3.number_input(
                "Qtd. neutro",
                1, 4, 1,
                key=f"{prefixo}_qtd_neutro"
            )

            cabo_neutro = c4.selectbox(
                "Cabo do neutro",
                list(TRACAO_CABO.keys()),
                key=f"{prefixo}_cabo_neutro"
            )

            tracao_neutro = float(TRACAO_CABO.get(cabo_neutro, 0)) * qtd_neutro

        st.markdown("##### Controle")

        usar_controle = st.checkbox(
            "Possui controle",
            value=False,
            key=f"{prefixo}_usa_controle"
        )

        tracao_controle = 0

        if usar_controle:
            c5, c6 = st.columns(2)

            qtd_controle = c5.number_input(
                "Qtd. controle",
                1, 4, 1,
                key=f"{prefixo}_qtd_controle"
            )

            cabo_controle = c6.selectbox(
                "Cabo do controle",
                list(TRACAO_CABO.keys()),
                key=f"{prefixo}_cabo_controle"
            )

            tracao_controle = float(TRACAO_CABO.get(cabo_controle, 0)) * qtd_controle

        tracao = tracao_fase + tracao_neutro + tracao_controle

    return tracao

# ─────────────────────────────────────────────────────────────────────────────
# PAINEL COMPLETO DE UM NÍVEL
# ─────────────────────────────────────────────────────────────────────────────

def painel_nivel(titulo, idx, alt_default, altura_util, af, altura_poste, is_bt=False):
    """
    Retorna (fx_transf, fy_transf, mag_transf, detalhes_dict)
    Usa fórmula analítica DIS-NOR-012 6.13.6 para a resultante,
    e transferência de altura 6.13.4 para escalar ao AF do poste.
    """
    st.markdown(f"#### {titulo}")

    alt_est = st.number_input(
        "Altura da estrutura — AI (m)", 0.0, float(altura_poste),
        value=float(alt_default), step=0.1, key=f"{idx}_alt",
        help="Altura onde o cabo está fixado no poste (AI na norma)"
    )

    st.markdown("---")
    col_ch, col_sa = st.columns(2)

    # ── CHEGADA ──────────────────────────────────────────────────────────────
    with col_ch:
        st.markdown("### ↙ Chegada")
        if is_bt:
            t_chegada = widget_cabo_bt(f"{idx}_ch", "Cabo que CHEGA")
        else:
            t_chegada = widget_cabo(f"{idx}_ch", "Cabo que CHEGA")
        ang_chegada = slider_ang("Ângulo de chegada (°)", 0, f"{idx}_ang_ch")
        st.caption("0°=Leste  90°=Norte  180°=Oeste  270°=Sul")

    # ── SAÍDA ─────────────────────────────────────────────────────────────────
    with col_sa:
        st.markdown("### ↗ Saída")
        tipo_saida = st.radio(
            "O cabo...",
            [
                "Fim de linha (não sai nada)",
                "Sai na tangente — mesmo cabo",
                "Sai na tangente — cabo diferente",
                "Deriva em outro ângulo",
            ],
            key=f"{idx}_tipo_saida",
        )

        t_saida  = 0.0
        ang_saida = 0

        if tipo_saida == "Fim de linha (não sai nada)":
            st.info("Só a tração de chegada atua no poste.")

        elif tipo_saida == "Sai na tangente — mesmo cabo":
            t_saida   = t_chegada
            ang_saida = (ang_chegada + 180) % 360
            st.caption(f"Mesmo cabo ({t_chegada:.0f} daN) — saída a {ang_saida}°.")

        elif tipo_saida == "Sai na tangente — cabo diferente":
            if is_bt:
                t_saida = widget_cabo_bt(f"{idx}_sa", "Cabo que SAI")
            else:
                t_saida = widget_cabo(f"{idx}_sa", "Cabo que SAI")
            ang_saida = (ang_chegada + 180) % 360
            st.caption(f"Saída a {ang_saida}° (tangente) — cabos diferentes → há resultante.")

        else:  # Deriva
            if is_bt:
                t_saida = widget_cabo_bt(f"{idx}_sa", "Cabo que SAI")
            else:
                t_saida = widget_cabo(f"{idx}_sa", "Cabo que SAI")
            ang_saida = slider_ang("Ângulo de saída (°)", 90, f"{idx}_ang_sa")

    # ── CÁLCULO VETORIAL (soma de vetores) ────────────────────────────────────
    ar = math.radians(ang_chegada)
    fx = t_chegada * math.cos(ar)
    fy = t_chegada * math.sin(ar)

    if tipo_saida != "Fim de linha (não sai nada)":
        sr = math.radians(ang_saida)
        fx += t_saida * math.cos(sr)
        fy += t_saida * math.sin(sr)

    mag = math.sqrt(fx**2 + fy**2)

    # ── ÂNGULO DE DEFLEXÃO α para exibir na fórmula da norma ─────────────────
    if tipo_saida != "Fim de linha (não sai nada)":
        diff = abs(ang_saida - ang_chegada) % 360
        alpha_deflexao = min(diff, 360 - diff)   # ângulo entre os dois cabos
    else:
        alpha_deflexao = 0.0

    # ── TRANSFERÊNCIA DE ALTURA conforme 6.13.4: Fr = (AI/AF) × TI ───────────
    fator = alt_est / af if af > 0 else 1.0
    fx_t  = fx  * fator
    fy_t  = fy  * fator
    mag_t = mag * fator

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tração chegada (daN)", f"{t_chegada:.0f}")
    c2.metric("Tração saída (daN)",   f"{t_saida:.0f}")
    c3.metric("Ângulo deflexão α",    f"{alpha_deflexao:.0f}°")
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

# ── DADOS DO POSTE ────────────────────────────────────────────────────────────
st.subheader("🪝 Dados do Poste")

ALTURAS_POSTE = [9, 10, 11, 12, 14, 16]
CLASSES_POSTE = [200, 300, 400, 600, 1000, 1500]

c1, c2, c3 = st.columns(3)

altura_poste = float(c1.selectbox(
    "Altura do poste (m)", ALTURAS_POSTE, index=ALTURAS_POSTE.index(12)
))

classe_poste = c2.selectbox(
    "Classe do poste (daN)", CLASSES_POSTE, index=CLASSES_POSTE.index(600),
    help="Esforço nominal suportado pelo poste"
)

# AF conforme DIS-NOR-012 6.13.4 (valores fixos da norma)
af_poste      = ALTURA_FINAL[int(altura_poste)]
# AI padrão = AF (altura útil ≈ AF para estruturas no topo)
_engastamento = round(altura_poste * 0.10 + 0.60, 2)
altura_util   = round(altura_poste - 0.20 - _engastamento, 2)

with c3:
    st.markdown("**Alturas calculadas (Electro / Norma)**")
    st.caption(
        f"Topo: −0,20 m | Engastamento: −{_engastamento:.2f} m "
        f"({int(altura_poste)}m×10%+0,60)"
    )
    st.info(
        f"Altura útil (AI ref.): **{altura_util:.2f} m**  \n"
        f"Altura final AF (norma): **{af_poste:.1f} m**"
    )

st.divider()

# ── 1º NÍVEL ─────────────────────────────────────────────────────────────────
st.subheader("⚡ 1º Nível — Rede Primária")
with st.container(border=True):
    fx1, fy1, mag1 = painel_nivel(
        "1º Nível", "n1", altura_util, altura_util, af_poste, altura_poste
    )

st.divider()

# ── 2º NÍVEL (opcional) ───────────────────────────────────────────────────────
st.subheader("⚡ 2º Nível — Rede Primária (opcional)")
tem_n2 = st.checkbox("Este poste possui 2º nível de rede primária")
fx2, fy2, mag2 = 0.0, 0.0, 0.0
if tem_n2:
    with st.container(border=True):
        fx2, fy2, mag2 = painel_nivel(
            "2º Nível", "n2",
            max(0.0, altura_util - 1.5), altura_util, af_poste, altura_poste
        )

st.divider()

# ── SECUNDÁRIA ────────────────────────────────────────────────────────────────
st.subheader("🔋 Rede Secundária — BT")
tem_sec = st.checkbox("Este poste possui saída de rede secundária")
fx_s, fy_s, mag_s = 0.0, 0.0, 0.0
if tem_sec:
    with st.container(border=True):
        fx_s, fy_s, mag_s = painel_nivel(
            "Secundária BT", "sec",
            max(0.0, altura_util - 3.0), altura_util, af_poste, altura_poste,
            is_bt=True
        )

st.divider()

# ── RESULTADO FINAL ───────────────────────────────────────────────────────────
st.subheader("📊 Resultado Final")

rx_tot  = fx1 + fx2 + fx_s
ry_tot  = fy1 + fy2 + fy_s
mag_tot = math.sqrt(rx_tot**2 + ry_tot**2)
ang_res = math.degrees(math.atan2(ry_tot, rx_tot)) % 360

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("1º Nível (daN)",            f"{mag1:.1f}")
c2.metric("2º Nível (daN)",            f"{mag2:.1f}" if tem_n2  else "—")
c3.metric("Secundária (daN)",          f"{mag_s:.1f}" if tem_sec else "—")
c4.metric("🔴 Resultante TOTAL (daN)", f"{mag_tot:.1f}")
c5.metric("Ângulo resultante",         f"{ang_res:.1f}°")
c6.metric("Classe do poste (daN)",     str(classe_poste))

if mag_tot > 0:
    margem = classe_poste - mag_tot
    if margem >= 0:
        st.success(
            f"✅ Esforço **{mag_tot:.1f} daN** — poste {int(altura_poste)} m / {classe_poste} daN "
            f"suporta com margem de **{margem:.1f} daN**."
        )
    else:
        proxima = next((c for c in CLASSES_POSTE if c >= mag_tot), None)
        sugestao = f"Considere classe **{proxima} daN**." if proxima else "Sem classe disponível — consulte engenheiro."
        st.error(
            f"🔴 Esforço **{mag_tot:.1f} daN** EXCEDE a classe {classe_poste} daN "
            f"em **{abs(margem):.1f} daN**. {sugestao}"
        )

with st.expander("📐 Referência das fórmulas utilizadas (DIS-NOR-012)"):
    st.markdown(f"""
**6.13.4 — Transferência de altura:**
> Fr = (AI / AF) × TI
> AF do poste {int(altura_poste)} m = **{af_poste} m**

**6.13.6 — Resultante analítica:**
> R = √(F₁² + F₂² + 2·F₁·F₂·cos β)  onde β = 180° − α

**6.13.7 — Simplificada (F₁ = F₂):**
> R = 2·F·sen(α/2)
""")

st.divider()
st.caption("Cálculos conforme DIS-NOR-012 Rev.08 e DIS-NOR-014 Rev.2024. Validar com engenheiro responsável.")
