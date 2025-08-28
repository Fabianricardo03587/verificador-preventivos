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
    "XQMX-2-2-1850T": ["XQMX-2-2-1850T-CVYR-01-PM-01",
			"XQMX-2-2-1850T-PM-01",
			"XQMX-2-2-1850T-ROB-01-PM-02",
			"XQMX-2-2-1850T-ROB-02-PM-01",
			"XQMX-2-2-1850T-ROB-02-PM-01",
			"XQMX-2-2-1850T-ROB-02-PM-02",
			"XQMX-2-2-1850T-TAB-01-PM-01",
			"XQMX-2-2-1850T-TCU-01-PM-01",
			"XQMX-2-2-1850T-TCU-01-PM-02",
			"XQMX-2-2-1850T-TCU-02-PM-01",
			"XQMX-2-2-1850T-TCU-02-PM-02"
],
    "XQMX-2-3-1850T": ["XQMX-2-3-1850T-CVYR-01-PM-01",
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
			"XQMX-2-3-1850T-TCU-02-PM-02",
]
}

# Subida de archivo opcional
archivo = st.file_uploader("Sube tu archivo Excel para actualizar estados y fechas", type=["xlsx"])

# Cargamos datos del Excel si existe
if archivo:
    df_excel = pd.read_excel(archivo)
else:
    df_excel = pd.DataFrame(columns=["Código", "Estado", "Fecha"])  # tabla vacía



# Crear columnas
columnas = st.columns(len(maquinas))

# Función para colorear estados
def color_estado(val):
    if val == "Pendiente":
        color = 'background-color: #FF9999'  # rojo claro
    elif val == "Completado":
        color = 'background-color: #99FF99'  # verde claro
    else:
        color = ''
    return color

# Mostrar tablas
for i, (maquina, codigos) in enumerate(maquinas.items()):
    col = columnas[i]
    with col:
        st.subheader(maquina)
        df = pd.DataFrame({
            "Código": codigos,
            "Estado": [df_excel.loc[df_excel["Código"]==c, "Estado"].values[0] if c in df_excel["Código"].values else "Pendiente" for c in codigos],
            "Fecha": [df_excel.loc[df_excel["Código"]==c, "Fecha"].values[0] if c in df_excel["Código"].values else "" for c in codigos]
        })
        # Aplicar colores y mostrar dataframe con mejor espaciado
        st.dataframe(df.style.applymap(color_estado), height=200)
