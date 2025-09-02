import streamlit as st
import pandas as pd
from supabase import create_client, Client

#--- CONFIGURACION DE SUPABASE ---
SUPABASE_URL = "https://wubnausfadmzqqlregzh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1Ym5hdXNmYWRtenFxbHJlZ3poIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY3NDg4MjEsImV4cCI6MjA3MjMyNDgyMX0.rEblj4SSJv3oca4cVKVvVM7eoDo5HpBKwyW5coF1WBs"
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

#--- SUBIDA DE ARCHIVO ---
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if uploaded_file:
    # Eliminar archivos anteriores
    files_list = supabase.storage.from_(BUCKET_NAME).list()
    for f in files_list:
        supabase.storage.from_(BUCKET_NAME).remove([f["name"]])

    # Subir el nuevo archivo
    supabase.storage.from_(BUCKET_NAME).upload("ultimo.xlsx", uploaded_file)
    st.success("Archivo subido y guardado en Supabase Storage ✅")

#--- LECTURA DEL ARCHIVO DESDE SUPABASE ---
try:
    data = supabase.storage.from_(BUCKET_NAME).download("ultimo.xlsx")
    df_excel = pd.read_excel(data)
    st.session_state.df_excel = df_excel  # Guardamos el Excel en session_state

    # Mostrar tabla original subida
    st.subheader("Vista del archivo Excel")
    st.data_editor(df_excel, use_container_width=True)  # permite filtros y edición ligera

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

#--- MOSTRAR RESULTADOS ---
st.subheader(maquina_seleccionada)
st.dataframe(df.style.applymap(color_estado), use_container_width=True)


