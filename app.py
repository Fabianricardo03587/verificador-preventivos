import streamlit as st
import pandas as pd

st.title("Verificador de Preventivos 🚀")

# -------------------------------
# Datos fijos por máquina y preventivos
# -------------------------------
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

# Inicializamos session_state para el DataFrame
if "df_excel" not in st.session_state:
    st.session_state.df_excel = pd.DataFrame(columns=["MAQUINA", "CODIGO", "FECHA"])

# Subida de archivo
archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo:
    st.session_state.df_excel = pd.read_excel(archivo)

# Usamos siempre el dataframe guardado en session_state
df_excel = st.session_state.df_excel

# Filtro para elegir la máquina
maquina_seleccionada = st.selectbox("Selecciona una máquina", list(maquinas.keys()))

# Códigos de la máquina seleccionada
codigos = maquinas[maquina_seleccionada]

# Función para colorear estados
def color_estado(val):
    if val == "Pendiente":
        return 'background-color: #FF9999'  # rojo claro
    elif val == "Completado":
        return 'background-color: #99FF99'  # verde claro
    return ''

# Crear dataframe cruzando con Excel
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

# Mostrar resultados
st.subheader(maquina_seleccionada)
st.dataframe(df.style.applymap(color_estado))
