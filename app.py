import streamlit as st
import pandas as pd

st.title("Verificador de Preventivos 🚀")

# Subir archivo
archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

# Lista de preventivos y máquina fija
maquina = "XQMX-2-1-1850T"
preventivos = [
    "XQMX-2-1-1850T-CVYR-01-PM-01",
    "XQMX-2-1-1850T-PM-01",
    "XQMX-2-1-1850T-PRES-01-PM-01",
    "XQMX-2-1-1850T-ROB-01-PM-01",
    "XQMX-2-1-1850T-ROB-01-PM-02",
    "XQMX-2-1-1850T-TCU-01-PM-01"
]

if archivo:
    df = pd.read_excel(archivo)

    # Crear lista de resultados
    resultados = []
    for code in preventivos:
        # Filtrar filas donde coincide la máquina y el preventivo
        fila = df[(df['J'] == maquina) & (df['F'] == code)]
        
        if not fila.empty:
            estado = "✅ OK"
            fecha = fila.iloc[0]['AB']
        else:
            estado = "---"
            fecha = "---"
        
        resultados.append({
            "Código Preventivo": code,
            "Estado": estado,
            "Fecha": fecha
        })
    
    # Convertir a DataFrame para mostrar
    df_result = pd.DataFrame(resultados)
    
    st.subheader(f"Resultados para la máquina: {maquina}")
    st.dataframe(df_result)

