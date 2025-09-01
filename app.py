import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Configuración de Supabase
SUPABASE_URL = "https://wubnausfadmzqqlregzh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1Ym5hdXNmYWRtenFxbHJlZ3poIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY3NDg4MjEsImV4cCI6MjA3MjMyNDgyMX0.rEblj4SSJv3oca4cVKVvVM7eoDo5HpBKwyW5coF1WBs"
BUCKET_NAME = "archivos-excel"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Verificador de Preventivos")

# Diccionario de referencia
dict_ref = {
    "XQMX-2-1-1850T": [
        {"Código": "A001", "Descripción": "Motor", "Nombre": "XQMX-2-1-1850T-CVYR-01-PM-01"},
        {"Código": "A002", "Descripción": "Sensor", "Nombre": "XQMX-2-1-1850T-PM-01"},
        {"Código": "A003", "Descripción": "PLC", "Nombre": "XQMX-2-1-1850T-PRES-01-PM-01"},
        # y así con los demás...
    ],

    "XQMX-2-2-1850T": [
        {"Código": "A001", "Descripción": "Motor", "Nombre": "XQMX-2-2-1850T-CVYR-01-PM-01"},
        # etc.
    ]
}

# Subir archivo
uploaded_file = st.file_uploader("Selecciona un archivo Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Leer archivo con pandas
        df = pd.read_excel(uploaded_file)
        st.write("Vista previa del archivo subido:")
        st.dataframe(df)

        # Comparar con diccionario
        st.write("Comparación con el diccionario de referencia:")
        for col in dict_ref.keys():
            if col in df.columns:
                df[f"{col}_exists"] = df[col].isin(dict_ref[col])
            else:
                df[f"{col}_exists"] = False  # columna no existe en el Excel

        st.dataframe(df)

        # Preparar archivo en bytes para subir a Supabase
        uploaded_file.seek(0)
        file_bytes = uploaded_file.read()

        # Subir archivo a Supabase Storage
        supabase.storage.from_(BUCKET_NAME).upload(
            "ultimo.xlsx",
            file_bytes,
            upsert=True
        )

        st.success("Archivo procesado y subido correctamente ✅")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar o subir el archivo: {e}")









