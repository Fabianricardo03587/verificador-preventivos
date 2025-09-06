import streamlit as st
import pandas as pd
from supabase import create_client, Client

# === CONFIG ===
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
BUCKET_NAME = "archivos-excel"
BUCKET_FIJO = "datos_fijos"
CLAVE_SECRETA = st.secrets["CLAVE_SECRETA"]
CLAVE_ADMIN = "admin123"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === FUNCIONES AUXILIARES ===
def apply_styles(login=False):
    st.markdown("""
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
        max-width: %s;
        margin: 50px auto;
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
    </style>
    """ % ("450px" if login else "100%"), unsafe_allow_html=True)

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

def cargar_maestro():
    try:
        data = supabase.storage.from_(BUCKET_FIJO).download("maquinas_codigos.xlsx")
        return pd.read_excel(data)
    except:
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

def descargar_archivo():
    try:
        data = supabase.storage.from_(BUCKET_NAME).download("ultimo.xlsx")
        return pd.read_excel(data)
    except:
        return pd.DataFrame(columns=["MAQUINA", "CODIGO", "FECHA"])

def color_estado(val):
    if val == "Pendiente": return 'background-color: #FF9999'
    if val == "Completado": return 'background-color: #99FF99'
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
    apply_styles()

# === TÍTULO ===
st.title("Verificador de Preventivos EMS 🚀")

# === ARCHIVO MAESTRO Y SUBIDA ===
df_maestro = cargar_maestro()
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])
if uploaded_file:
    subir_archivo(uploaded_file)

df_excel = descargar_archivo()
st.session_state.df_excel = df_excel

# === META PREVENTIVOS ===
st.metric("Meta de Preventivos", st.session_state.meta_preventivos)
with st.expander("⚙️ Configuración de Meta (solo administradores)"):
    clave_admin = st.text_input("Clave de administrador:", type="password")
    nueva_meta = st.number_input("Nueva meta:", value=st.session_state.meta_preventivos, step=1)
    if st.button("Actualizar Meta") and clave_admin == CLAVE_ADMIN:
        st.session_state.meta_preventivos = nueva_meta
        st.success("✅ Meta actualizada")
    elif clave_admin and clave_admin != CLAVE_ADMIN:
        st.error("❌ Clave incorrecta")

# === CONTADOR GLOBAL ===
pares_hechos = set(zip(
    df_excel["MAQUINA"].astype(str).str.strip(),
    df_excel["CODIGO"].astype(str).str.strip()
)) if not df_excel.empty else set()

total_planificados = len(df_maestro)
completados_global = sum(
    (str(r["MAQUINA"]).strip(), str(r["CODIGO"]).strip()) in pares_hechos
    for _, r in df_maestro.iterrows()
)
avance_global = round((completados_global / st.session_state.meta_preventivos) * 100, 1)
pendientes_global = st.session_state.meta_preventivos - completados_global

c1, c2, c3, c4 = st.columns(4)
c1.metric("✅ Completados", completados_global)
c2.metric("🗂️ Planificados", st.session_state.meta_preventivos)
c3.metric("📊 Avance", f"{avance_global}%")
c4.metric("⌛ Pendientes", pendientes_global)

if completados_global >= st.session_state.meta_preventivos:
    st.success("✅ Meta alcanzada")
else:
    st.warning(f"⚠️ Faltan {pendientes_global} para la meta")

# === FILTRO POR MÁQUINA ===
maquina = st.selectbox("Selecciona una máquina", df_maestro["MAQUINA"].unique())
df_codigos = df_maestro[df_maestro["MAQUINA"] == maquina].copy()

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

# === MÉTRICAS Y TABLA ===
total = len(df_codigos)
completados = (df_codigos["Estado"] == "Completado").sum()
pendientes = total - completados
avance = round((completados / total) * 100, 1) if total else 0

st.subheader(maquina)
c1, c2, c3 = st.columns(3)
c1.metric("✅ Completados", completados)
c2.metric("⌛ Pendientes", pendientes)
c3.metric("📊 Avance", f"{avance}%")

df_codigos.drop(columns=["MAQUINA"], inplace=True)
st.dataframe(df_codigos.style.applymap(color_estado), use_container_width=True
