import streamlit as st
import pandas as pd
from supabase import create_client, Client

#--- CONFIGURACION DE SUPABASE ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
BUCKET_NAME = "archivos-excel"


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Verificador de Preventivos V2.0 🚀")

#--- DATOS FIJOS POR MÁQUINA Y PREVENTIVOS ---
maquinas = {
    "XQMX-2-1-1850T": [
        "XQMX-2-1-1850T-CVYR-01-PM-01",
        "XQMX-2-1-1850T-PM-01",
        "XQMX-2-1-1850T-PRES-01-PM-01",
        "XQMX-2-1-1850T-ROB-01-PM-01",
        "XQMX-2-1-1850T-ROB-01-PM-02",
        "XQMX-2-1-1850T-TCU-01-PM-01"
    ],
    "XQMX-2-2-1850T": [
        "XQMX-2-2-1850T-CVYR-01-PM-01",
        "XQMX-2-2-1850T-PM-01",
        "XQMX-2-2-1850T-ROB-01-PM-02",
        "XQMX-2-2-1850T-ROB-02-PM-01",
        "XQMX-2-2-1850T-ROB-02-PM-02",
        "XQMX-2-2-1850T-TAB-01-PM-01",
        "XQMX-2-2-1850T-TCU-01-PM-01",
        "XQMX-2-2-1850T-TCU-01-PM-02",
        "XQMX-2-2-1850T-TCU-02-PM-01",
        "XQMX-2-2-1850T-TCU-02-PM-02"
    ],
    "XQMX-2-3-1850T": [
        "XQMX-2-3-1850T-CVYR-01-PM-01",
        "XQMX-2-3-1850T-PM-01",
        "XQMX-2-3-1850T-PRES-01-PM-01",
        "XQMX-2-3-1850T-PRO-01-PM-01",
        "XQMX-2-3-1850T-ROB-01-PM-01",
        "XQMX-2-3-1850T-ROB-01-PM-02",
        "XQMX-2-3-1850T-ROB-02-PM-01",
        "XQMX-2-3-1850T-ROB-02-PM-02",
        "XQMX-2-3-1850T-ROB-03-PM-01",
        "XQMX-2-3-1850T-TCU-01-PM-01",
        "XQMX-2-3-1850T-TCU-01-PM-02",
        "XQMX-2-3-1850T-TCU-02-PM-01",
        "XQMX-2-3-1850T-TCU-02-PM-02"
    ]
}

#--- INICIALIZAMOS session_state ---
if "df_excel" not in st.session_state:
    st.session_state.df_excel = pd.DataFrame(columns=["MAQUINA", "CODIGO", "FECHA"])

# --- Autenticación simple por clave ---
CLAVE_SECRETA = st.secrets["CLAVE_SECRETA"]

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.subheader("🔐 Acceso restringido")
    st.markdown("🔓 **Sesión iniciada correctamente**")
    clave_ingresada = st.text_input("Ingresa la clave para continuar:", type="password")
    
    if st.button("Entrar"):
        if clave_ingresada == CLAVE_SECRETA:
            st.session_state.autenticado = True
            st.success("✅ Acceso concedido")
            st.rerun()
        else:
            st.error("❌ Clave incorrecta")
    st.stop()

#--- SUBIDA DE ARCHIVO ---
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if uploaded_file:
    # Eliminar archivos anteriores
    files_list = supabase.storage.from_(BUCKET_NAME).list()
    for f in files_list:
        if "name" in f:
            supabase.storage.from_(BUCKET_NAME).remove([f["name"]])

    try:
        # Subir el nuevo archivo como bytes
        supabase.storage.from_(BUCKET_NAME).upload(
            "ultimo.xlsx", 
            uploaded_file.getvalue(), 
            file_options={"upsert": "true"}
        )
        st.success("Archivo subido y guardado en Supabase Storage ✅")
    except Exception as e:
        st.error(f"❌ Error al subir el archivo: {e}")



#--- LECTURA DEL ARCHIVO DESDE SUPABASE ---
try:
    data = supabase.storage.from_(BUCKET_NAME).download("ultimo.xlsx")
    df_excel = pd.read_excel(data)
    st.session_state.df_excel = df_excel  # Guardamos el Excel en session_state

except Exception as e:
    st.info("No hay archivo guardado en Supabase. Sube uno para comenzar.")
    df_excel = st.session_state.df_excel

#--- SELECCIÓN DE MÁQUINA ---
maquina_seleccionada = st.selectbox("Selecciona una máquina", list(maquinas.keys()))
codigos = maquinas[maquina_seleccionada]

#--- FUNCIÓN PARA COLOREAR ESTADO ---
def color_estado(val):
    if val == "Pendiente":
        return 'background-color: #FF9999'  # rojo claro
    elif val == "Completado":
        return 'background-color: #99FF99'  # verde claro
    return ''

#--- CRUCE DE DATOS CON EL EXCEL ---
df = pd.DataFrame({
    "Código": codigos,
    "Estado": [
        "Completado" if (
            (maquina_seleccionada in df_excel["MAQUINA"].values) and
            (c in df_excel.loc[df_excel["MAQUINA"] == maquina_seleccionada, "CODIGO"].values)
        ) else "Pendiente"
        for c in codigos
    ],
    "Fecha": [
        df_excel.loc[(df_excel["MAQUINA"] == maquina_seleccionada) & (df_excel["CODIGO"] == c), "FECHA"].values[0]
        if ((df_excel["MAQUINA"] == maquina_seleccionada) & (df_excel["CODIGO"] == c)).any()
        else ""
        for c in codigos
    ]
})

# --- CONTADORES ---
total = len(df)
completados = (df["Estado"] == "Completado").sum()
pendientes = total - completados
avance = round((completados / total) * 100, 1)

col1, col2, col3 = st.columns(3)
col1.metric("✅ Completados", completados)
col2.metric("⌛ Pendientes", pendientes)
col3.metric("📊 Avance", f"{avance} %")

#--- MOSTRAR RESULTADOS ---
st.subheader(maquina_seleccionada)
st.dataframe(df.style.applymap(color_estado), use_container_width=True)


if st.session_state.autenticado:
    if st.button("Cerrar sesión"):
        st.session_state.autenticado = False
        st.experimental_rerun()















