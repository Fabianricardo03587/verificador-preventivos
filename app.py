import streamlit as st

import streamlit as st
import pandas as pd

# Inicializar variables en session_state
if "df_excel" not in st.session_state:
    st.session_state.df_excel = pd.DataFrame(columns=["MAQUINA", "CODIGO", "FECHA"])

if "maquinas" not in st.session_state:
    # Ejemplo: diccionario con máquinas y sus códigos
    st.session_state.maquinas = {
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

# Subir archivo Excel
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if uploaded_file:
    df_excel_new = pd.read_excel(uploaded_file)
    st.session_state.df_excel = df_excel_new  # Reemplaza el anterior por el nuevo
    st.success("Archivo cargado correctamente!")

# Función para colorear estado
def color_estado(val):
    if val == "Realizado":
        return "background-color: lightgreen"
    elif val == "Pendiente":
        return "background-color: lightcoral"
    else:
        return ""

# Mostrar tablas por máquina
columnas = st.columns(len(st.session_state.maquinas))

for i, (maquina, codigos) in enumerate(st.session_state.maquinas.items()):
    col = columnas[i]
    with col:
        st.subheader(maquina)
        df = pd.DataFrame({
            "Código": codigos,
            "Estado": [
                "Realizado" if ((st.session_state.df_excel["MAQUINA"]==maquina) & 
                                (st.session_state.df_excel["CODIGO"]==c)).any() 
                else "Pendiente" for c in codigos
            ],
            "Fecha": [
                st.session_state.df_excel.loc[
                    (st.session_state.df_excel["MAQUINA"]==maquina) &
                    (st.session_state.df_excel["CODIGO"]==c),
                    "FECHA"
                ].values[0] if ((st.session_state.df_excel["MAQUINA"]==maquina) & 
                                (st.session_state.df_excel["CODIGO"]==c)).any() else "" 
                for c in codigos
            ]
        })
        st.dataframe(df.style.applymap(color_estado))

