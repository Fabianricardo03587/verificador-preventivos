import streamlit as st

import pandas as pd

from supabase import create_client, Client

#--- CONFIGURACION DE SUPABASE ---

SUPABASE_URL = "https://wubnausfadmzqqlregzh.supabase.co"

SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1Ym5hdXNmYWRtenFxbHJlZ3poIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY3NDg4MjEsImV4cCI6MjA3MjMyNDgyMX0.rEblj4SSJv3oca4cVKVvVM7eoDo5HpBKwyW5coF1WBs"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET_NAME = "archivos-excel"  # Asegúrate de crear este bucket en Supabase Storage

st.title("Verificador de Preventivos V2.0 🚀")

#-------------------------------

#Datos fijos por máquina y preventivos

#-------------------------------

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

Inicializamos session_state para el DataFrame

if "df_excel" not in st.session_state:

st.session_state.df_excel = pd.DataFrame(columns=["MAQUINA", "CODIGO", "FECHA"])

Subida de archivo


#--- SUBIDA DE ARCHIVO ---

uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if uploaded_file:

    

# Eliminar archivo anterior (solo mantenemos 1)

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
    st.session_state.df_excel = df_excel  # <- aquí guardamos el Excel en session_state
except Exception as e:
    st.info("No hay archivo guardado en Supabase. Sube uno para comenzar.")
    df_excel = st.session_state.df_excel


# Mostrar tabla con buscador

st.subheader("Vista del archivo Excel")

st.data_editor(df, use_container_width=True)  # permite filtros y edición ligera

except Exception as e:

st.info("No hay archivo guardado en Supabase. Sube uno para comenzar.")

#Usamos siempre el dataframe guardado en session_state

df_excel = st.session_state.df_excel

#Filtro para elegir la máquina

maquina_seleccionada = st.selectbox("Selecciona una máquina", list(maquinas.keys()))

#Códigos de la máquina seleccionada

codigos = maquinas[maquina_seleccionada]

#Función para colorear estados

def color_estado(val):

if val == "Pendiente":

    return 'background-color: #FF9999'  # rojo claro

elif val == "Completado":

    return 'background-color: #99FF99'  # verde claro

return ''

#Crear dataframe cruzando con Excel

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

#Mostrar resultados

st.subheader(maquina_seleccionada)

st.dataframe(df.style.applymap(color_estado))









