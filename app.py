import streamlit as st
import pandas as pd
from supabase import create_client

# === CONFIG ===
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
BUCKET_NAME = "archivos-excel"
BUCKET_FIJO = "datos_fijos"
CLAVE_SECRETA = st.secrets["CLAVE_SECRETA"]
CLAVE_ADMIN = "admin123"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# === FUNCIONES AUXILIARES ===
def apply_styles(login=False):
    """
    Aplica estilos:
    - Si login=True: caja blanca centrada pequeña (lo que tenías).
    - Si login=False: header fijo (60% ancho) y contenido con texto blanco sobre el degradado.
    """
    if login:
        css = """
        <style>
        #MainMenu, header, footer { visibility: hidden; }
        .stApp {
            background: linear-gradient(to bottom, #0082F4, #2542FF);
            background-attachment: fixed;
        }
        [data-testid="stVerticalBlock"] {
            background-color: white;
            padding: 40px 30px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            max-width: 450px;
            margin: 80px auto;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .stButton > button {
            color: white !important;
            background-color: #2542FF;
            border-radius: 8px;
            border: none;
            font-size: 16px;
            margin-top: 15px;
            padding: 10px 40px;
        }
        .stButton > button:hover {
            background-color: #0082F4;
        }

         /* Cambiar el botón "Browse files" de st.file_uploader */
        div[data-testid="stFileUploader"] > div > button {
            background-color: #2542FF;  /* Azul */
        }

        div[data-testid="stFileUploader"] > div > button:hover {
    background-color: #1a32cc;  /* Azul más oscuro al pasar el mouse */
}

        </style>
        """
    else:
        # estilos para header fijo y contenido blanco
        css = """
        <style>
        /* Importar varios pesos de Nunito Sans */
            @import url('https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@300;400;700;900&display=swap');

        /* Ocultar menú y footer nativos */
        #MainMenu, header, footer { visibility: hidden; }

        /* Fondo degradado principal (igual al login) */
        .stApp {
            background: linear-gradient(to bottom, #0082F4, #2542FF);
            background-attachment: fixed;
            color: white; /* Texto por defecto blanco en el contenido */
        }

        /* Header fijo centrado */
        .fixed-header {
            position: fixed;
            top: 0; /* antes estaba en 12px, ahora hasta arriba */
            left: 50%;
            transform: translateX(-50%);
            width: 60%;
            max-width: 1100px;
            min-width: 320px;
            background-color: white;
            box-shadow: 0 8px 30px rgba(0,0,0,0.25);
            padding: 20px 28px;
            z-index: 9999;
            text-align: center;
            border-top-left-radius: 0px;     /* esquinas de arriba sin redondear */
            border-top-right-radius: 0px;
            border-bottom-left-radius: 15px; /* esquinas de abajo redondeadas */
            border-bottom-right-radius: 15px;
        }

        /* Espacio para evitar que el header tape contenido */
        .content-wrapper {
            padding-top: 100px; /* ajusta este valor para que justo empiece debajo del header */
            padding-left: 20px;
            padding-right: 20px;
        }

        /* Estilos del título dentro del header */
        .header-title {
            font-family: 'Nunito Sans', sans-serif;
            font-size: 55px;
            font-weight: 900;
            color: #2542FF; /* azul para mes y año */
            margin-bottom: 0;
            line-height: 1.0;   /* 👈 reduce espacio vertical */
        }
        .header-subtitle {
            font-family: 'Nunito Sans', sans-serif;
            font-weight: 700;
            font-size: 25px;
            color: #333333;
            margin-bottom: 0px;
            line-height: 1.0;   /*  reduce espacio vertical */
        }
        .header-small {
            font-family: 'Nunito Sans', sans-serif;
            font-weight: 300;   /* Light */
            font-size: 12px;
            color: #666666;
            margin-bottom: 10px;
        }

        /* Contenedor de métricas del header (cuatro métricas en fila) */
        .header-metrics {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            margin-top: 10px;
        }
        .metric-box {
            flex: 1;
            padding: 10px 8px;
            border-radius: 8px;
            background: transparent;
            border: 1px solid #f0f0f0;
        }
        .metric-value {
            font-family: 'Nunito Sans', sans-serif;
            font-weight: 400;   /* Light */
            font-size: 30px;
            font-weight: 700;
        }
        .metric-label {
            font-family: 'Nunito Sans', sans-serif;
            font-weight: 400;   /* Light */
            font-size: 12px;
            color: #555;
        }

        /* Recuadro verde claro "meta alcanzada" */
        .meta-alcanzada {
            margin-top: 12px;
            background-color: #e6f9ea;
            color: #1b6f3a;
            padding: 8px 12px;
            border-radius: 10px;
            display: inline-block;
            font-weight: 600;
            border: 1px solid #c8f0d4;
        }

        /* Contenido principal (textos en blanco según solicitud) */
        .main-text, .stMarkdown, .stText {
            color: white !important;
        }

        /* Table styling: ajustar tabla cuando sea renderizada */
        .streamlit-table td, .streamlit-table th {
            color: #ffffff !important; /* texto tabla blanco (si se requiere) */
        }

        
        div.stButton > button {
            background-color: #2542FF;  /* Azul */
        }

        /* Cambiar el botón "Browse files" */
        div[data-testid="stFileUploader"] button {
            background-color: #2542FF !important;
        }

        div[data-testid="stFileUploader"] button:hover {
            background-color: #1a32cc !important;
        }

        /* Responsive adjustments */
        @media (max-width: 900px) {
            .fixed-header { width: 90%; padding: 14px; }
            .header-title { font-size: 20px; }
            .header-metrics { flex-direction: column; }
        }

    
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)


def autenticar():
    apply_styles(login=True)
    st.markdown("### Acceso restringido")
    clave_ingresada = st.text_input("Ingresa tu clave:", type="password")
    if st.button("Entrar"):
        if clave_ingresada == CLAVE_SECRETA:
            st.session_state.autenticado = True
            st.success("✅ Acceso concedido")
            st.rerun()
        else:
            st.error("❌ Clave incorrecta")
    st.stop()

st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)

def cargar_maestro():
    try:
        data = supabase.storage.from_(BUCKET_FIJO).download("maquinas_codigos.xlsx")
        return pd.read_excel(data)
    except Exception as e:
        st.error("❌ No se pudo cargar el archivo maestro.")
        st.stop()






def subir_archivo(uploaded_file):
    try:
        files = supabase.storage.from_(BUCKET_NAME).list()
        for f in files:
            if "name" in f:
                supabase.storage.from_(BUCKET_NAME).remove([f["name"]])
        supabase.storage.from_(BUCKET_NAME).upload(
            "ultimo.xlsx",
            uploaded_file.getvalue(),
            file_options={"upsert": "true"}
        )
        st.success("Archivo subido ✅")
    except Exception as e:
        st.error(f"❌ Error al subir el archivo: {e}")

####### SUBIR ARCHIVO DE EXCEL

def descargar_archivo():
    try:
        data = supabase.storage.from_(BUCKET_NAME).download("ultimo.xlsx")
        return pd.read_excel(data)
    except:
        return pd.DataFrame(columns=["MAQUINA", "CODIGO", "FECHA"])


def color_estado(val):
    if val == "Pendiente":
        return 'background-color: #FF9999'
    if val == "Completado":
        return 'background-color: #99FF99'
    return ''


# === ESTADO INICIAL ===
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "meta_preventivos" not in st.session_state:
    st.session_state.meta_preventivos = 55
if "df_excel" not in st.session_state:
    st.session_state.df_excel = pd.DataFrame(columns=["MAQUINA", "CODIGO", "FECHA"])

# === LOGIN ===
if not st.session_state.autenticado:
    autenticar()
else:
    apply_styles(login=False)





#++++++++++++++++SUBIR ARCHIVO DE EXCEL

# === CARGA DE DATOS ===
# (cargar maestro y archivo subido)
df_maestro = cargar_maestro()

df_excel = descargar_archivo()
st.session_state.df_excel = df_excel



# === CÁLCULOS GLOBALES ===
pares_hechos = set(zip(
    df_excel["MAQUINA"].astype(str).str.strip(),
    df_excel["CODIGO"].astype(str).str.strip()
)) if not df_excel.empty else set()

total_planificados = len(df_maestro)
completados_global = sum(
    (str(r["MAQUINA"]).strip(), str(r["CODIGO"]).strip()) in pares_hechos
    for _, r in df_maestro.iterrows()
)
# evitar división por cero
avance_global = round((completados_global / st.session_state.meta_preventivos) * 100, 1) if st.session_state.meta_preventivos else 0
pendientes_global = max(0, st.session_state.meta_preventivos - completados_global)



# === Obtener el mes y año desde la primera fecha en df_excel ===
titulo_mes = "Sin fecha"

if df_excel is not None and not df_excel.empty:
    # Suponiendo que la columna se llama "FECHA"
    primera_fecha = pd.to_datetime(df_excel["FECHA"].iloc[0], errors="coerce")

    if pd.notnull(primera_fecha):
        meses = {
            1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
            5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
            9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
        }
        mes_nombre = meses[primera_fecha.month]
        titulo_mes = f"{mes_nombre} {primera_fecha.year}"


# === HEADER FIJO (renderizado en HTML para que quede fijo) ===
# Aquí colocamos AGOSTO 2025 como solicitaste
mes_anyo =  titulo_mes
titulo = "Verificador de Preventivos EMS"
texto_pequeno = "Inyección & NFPP 2.0"

# Contenido dinámico del recuadro "meta alcanzada"
meta_alcanzada_html = ""
if completados_global >= st.session_state.meta_preventivos:
    meta_alcanzada_html = f'<div class="meta-alcanzada">Meta alcanzada ({completados_global}/{st.session_state.meta_preventivos})</div>'




header_html = f"""
<div class="fixed-header">
  <div class="header-title">{mes_anyo}</div>
  <div class="header-subtitle">{titulo}</div>
  <div class="header-small">{texto_pequeno}</div>

  <div class="header-metrics" role="list">
    <div class="metric-box" role="listitem">
      <div class="metric-label">✅ Completados</div>
      <div class="metric-value" style="color:#1b6f3a;">{completados_global}</div>
    </div>
    <div class="metric-box" role="listitem">
      <div class="metric-label">🗂️ Planificados</div>
      <div class="metric-value" style="color:#666666;">{st.session_state.meta_preventivos}</div>
    </div>
    <div class="metric-box" role="listitem">
      <div class="metric-label">📊 Avance</div>
      <div class="metric-value" style="color:#2542FF;">{avance_global}%</div>
    </div>
    <div class="metric-box" role="listitem">
      <div class="metric-label">⌛ Pendientes</div>
      <div class="metric-value" style="color:#bf1f1f;">{pendientes_global}</div>
    </div>
  </div>

  {meta_alcanzada_html}
</div>
"""

st.markdown(header_html, unsafe_allow_html=True)


# === CONTENIDO PRINCIPAL (desplazable) ===
# damos el wrapper con padding-top para que el header no tape el contenido
st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)

# Configuración de meta (expander dentro del contenido)
with st.expander("⚙️ Configuración de Meta (solo administradores)"):
    clave_admin = st.text_input("Clave de administrador:", type="password")
    nueva_meta = st.number_input("Nueva meta:", value=st.session_state.meta_preventivos, step=1)
    if st.button("Actualizar Meta") and clave_admin == CLAVE_ADMIN:
        st.session_state.meta_preventivos = nueva_meta
        st.success("✅ Meta actualizada")
    elif clave_admin and clave_admin != CLAVE_ADMIN:
        st.error("❌ Clave incorrecta")

# Selector de máquina
maquina = st.selectbox("Selecciona una máquina", df_maestro["MAQUINA"].unique())

# Filtrar códigos de la máquina seleccionada
df_codigos = df_maestro[df_maestro["MAQUINA"] == maquina].copy()

# Asegurarnos de que exista columna "RESPONSABLE" en la tabla final
if "RESPONSABLE" not in df_codigos.columns:
    df_codigos["RESPONSABLE"] = ""

# Calcular estado y fecha (como antes)
df_codigos["Estado"] = df_codigos["CODIGO"].apply(
    lambda c: "Completado" if (
        (maquina in df_excel["MAQUINA"].values) and
        (c in df_excel[df_excel["MAQUINA"] == maquina]["CODIGO"].values)
    ) else "Pendiente"
)

df_codigos["Fecha"] = df_codigos["CODIGO"].apply(
    lambda c: df_excel[
        (df_excel["MAQUINA"] == maquina) & (df_excel["CODIGO"] == c)
    ]["FECHA"].values[0] if (
        ((df_excel["MAQUINA"] == maquina) & (df_excel["CODIGO"] == c)).any()
    ) else ""
)

# Métricas individuales máquina
total = len(df_codigos)
completados = int((df_codigos["Estado"] == "Completado").sum())
pendientes = int(total - completados)
avance = round((completados / total) * 100, 1) if total else 0

# Mostrar métricas individuales (blancas sobre el fondo degradado)
st.markdown(f"""
<div class="main-text" style="margin-bottom:8px;">
  <h3 style="margin:6px 0 2px 0;color: white;">{maquina}</h3>
</div>
""", unsafe_allow_html=True)


c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"<div style='color:white; text-align:center;'>Completados<div style=\"font-size:20px; font-weight:700\">{completados}</div><div></div></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div style='color:white; text-align:center;'>Pendientes<div style=\"font-size:20px; font-weight:700\">{pendientes}</div><div></div></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div style='color:white; text-align:center;'>Avance<div style=\"font-size:20px; font-weight:700\">{avance}%</div><div></div></div>", unsafe_allow_html=True)

# Preparar tabla final con las columnas: Nombre, Código, Responsable, Estado, Fecha
# Intentamos usar columnas de df_codigos: si no existe "NOMBRE" lo tomamos de MAQUINA u otra columna
if "NOMBRE" in df_codigos.columns:
    nombres = df_codigos["NOMBRE"]
elif "MAQUINA" in df_codigos.columns:
    nombres = df_codigos["MAQUINA"]
else:
    nombres = pd.Series([maquina]*len(df_codigos))

tabla_mostrar = pd.DataFrame({
    "Nombre": nombres.reset_index(drop=True),
    "Código": df_codigos["CODIGO"].reset_index(drop=True),
    "Responsable": df_codigos.get("RESPONSABLE", pd.Series([""]*len(df_codigos))).reset_index(drop=True),
    "Estado": df_codigos["Estado"].reset_index(drop=True),
    "Fecha": df_codigos["Fecha"].reset_index(drop=True)
})





# Mostramos la tabla con estilo: colorear filas según estado (aplicamos style.applymap)
def estilo_tabla(df):
    sty = df.style
    # Aplicar colores de fondo por estado
    def estado_color(v):
        if v == "Completado":
            return 'background-color: #2ecc71; color: black'
        if v == "Pendiente":
            return 'background-color: #ff7675; color: black'
        return ''
    sty = sty.applymap(lambda v: estado_color(v) if v in ["Completado", "Pendiente"] else '', subset=["Estado"])
    return sty


# === CARGA DE DATOS ===
# (cargar maestro y archivo subido)
df_maestro = cargar_maestro()
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])
if uploaded_file:
    subir_archivo(uploaded_file)

df_excel = descargar_archivo()
st.session_state.df_excel = df_excel














st.markdown("<br>", unsafe_allow_html=True)
# Aplicamos la función color_estado solo a la columna "Estado"
st.dataframe(
    tabla_mostrar.style.applymap(color_estado, subset=["Estado"]),
    use_container_width=True
)

# Diccionario de máquinas y sus imágenes de QR
qr_maquinas = {
    "XQMX-2-1-1850T": "imagenes_qr/qr_xqmx_2_1_1850t.png",
    "XQMX-2-2-1850T": "imagenes_qr/qr_xqmx_2_2_1850t.png",
    "XQMX-2-3-1850T": "imagenes_qr/qr_xqmx_2_3_1850t.png"
}

# Mostrar QR y texto en columnas
col1, col2 = st.columns([1, 2])  # Ajusta proporción si quieres más espacio para el texto

with col1:
    st.image(qr_maquinas[maquina], width=200)  # Ajusta el tamaño del QR

with col2:
    st.markdown("""
    **USUARIO:** XINQUAN  
    **CONTRASEÑA:** XQ233445
    """)

    
# Botón cerrar sesión (colocado al final del contenido)
st.markdown("<br>", unsafe_allow_html=True)
if st.button("Cerrar sesión"):
    st.session_state.autenticado = False
    st.experimental_rerun()

# Cierre del content-wrapper
st.markdown('</div>', unsafe_allow_html=True)
