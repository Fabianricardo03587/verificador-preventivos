import streamlit as st
import pandas as pd
from supabase import create_client, Client
from io import BytesIO


#--- CONFIGURACION DE SUPABASE ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
BUCKET_NAME = "archivos-excel"


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



#--- DATOS FIJOS POR MÁQUINA Y PREVENTIVOS ---




#--- INICIALIZAMOS session_state ---
if "df_excel" not in st.session_state:
    st.session_state.df_excel = pd.DataFrame(columns=["MAQUINA", "CODIGO", "FECHA"])

# --- Autenticación simple por clave ---
CLAVE_SECRETA = st.secrets["CLAVE_SECRETA"]

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("""
        <style>
        /* --- Estilos SOLO para la pantalla de login en PC --- */
        
        #MainMenu {
            visibility: hidden;
        }

        /* Ocultar el encabezado completo de Streamlit */
        header {
            visibility: hidden;
        }

        /* Opcional: ocultar el pie de página "Made with Streamlit" */
            footer {
            visibility: hidden;
        }

        /* Fondo con degradado aplicado al contenedor principal */
        .stApp {
            background: linear-gradient(to bottom, #0082F4, #2542FF);
            background-attachment: fixed;
            background-repeat: no-repeat;
            background-size: cover;
        }


        /* Recuadro principal */
        .login-box {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            width: 400px;
            margin: 20px auto;
            text-align: center;
        }

        /* Recuadro para el título */
        .title-box {
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.15);
            width: 400px;
            margin: 20px auto;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
        }
        
        .block-container {
            max-width: 25%;
            padding-top: 15rem;
        }
        
        /* Contenedor del input */
        .stTextInput > div {
            width: 80%;   /* Ajusta el tamaño del recuadro completo */
            margin: 0 auto; /* Lo centra */
        }

        /* Cajita de texto */
        .stTextInput > div > div > input {
            width: 100%;  /* Ahora ocupa todo el contenedor que limitamos arriba */
            font-size: 16px;
            padding: 8px;
            text-align: center;
}


        .stButton > button {
            display: block;
            margin: 0 auto;        /* centra horizontalmente */
            
            width: 150px;
            height: 40px;
            font-size: 18px;
            border-radius: 10px;
            background-color: #1976d2;
            color: white;
        }


        
        /* Cuando paso el mouse (hover) */
        .stButton > button:hover {
            background-color: #1565c0; /* azul más oscuro */
            transform: scale(1.03); /* efecto zoom suave */
        }
        /* Cuando hago click (active) */
        .stButton > button:active {
            background-color: #0d47a1; /* azul más fuerte */
            transform: scale(0.97); /* se achica un poco */
        }
}


        
        </style>
    """, unsafe_allow_html=True)
    # Tu código de login aquí...


    

    # --- Aquí usas las clases en HTML ---
    st.markdown('<div class="title-box">🔐 Acceso al sistema</div>', unsafe_allow_html=True)

    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    CLAVE_SECRETA = "1234"
    clave_ingresada = st.text_input("Ingresa la clave para continuar:", type="password")

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Entrar"):
            if clave_ingresada == CLAVE_SECRETA:
                st.success("✅ Acceso concedido")
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("❌ Clave incorrecta")

    st.markdown('</div>', unsafe_allow_html=True)  # cierre del login-box
            
    st.stop()

else: 
      st.markdown("""
        <style>
        .block-container {
            max-width: 50%;
            padding-top: 1rem;
        }
        h1, h2, h3 {
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }
        .stDataFrame {
            font-size: 14px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Aquí todo tu contenido de tablas, buscadores, etc.












st.title("Verificador de Preventivos EMS 🚀")


# --- LECTURA DEL ARCHIVO MAESTRO (datos fijos: máquinas, códigos, responsables) ---
BUCKET_FIJO = "datos_fijos"       # donde ya tienes maquinas_codigos.xlsx
try:
    data_maestro = supabase.storage.from_(BUCKET_FIJO).download("maquinas_codigos.xlsx")
    df_maestro = pd.read_excel(data_maestro)
except Exception as e:
    st.error("❌ No se pudo cargar el archivo maestro (maquinas_codigos.xlsx).")
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

# --- Valor de referencia (meta definida por el usuario) ---



# --- Valor de referencia (meta de preventivos) ---
if "meta_preventivos" not in st.session_state:
    st.session_state.meta_preventivos = 55  # valor inicial

st.metric("Meta de Preventivos", st.session_state.meta_preventivos)
CLAVE_ADMIN = "admin123"
# --- Opción para cambiar la meta SOLO con clave admin ---

with st.expander("⚙️ Configuración de Meta (solo administradores)"):
    clave_admin_ingresada = st.text_input("Clave de administrador:", type="password", key="clave_admin")
    nueva_meta = st.number_input("Nueva meta de preventivos:", min_value=0, value=st.session_state.meta_preventivos, step=1)

    if st.button("Actualizar Meta"):
        if clave_admin_ingresada == CLAVE_ADMIN:
            
            st.session_state.meta_preventivos = nueva_meta
            st.success(f"✅ Meta actualizada a {nueva_meta}")
        else:
            st.error("❌ Clave de administrador incorrecta")





# Normalizamos y construimos el set de pares (MAQUINA, CODIGO) encontrados en el Excel
if not df_excel.empty and {"MAQUINA","CODIGO"}.issubset(df_excel.columns):
    pares_hechos = set(
        zip(
            df_excel["MAQUINA"].astype(str).str.strip(),
            df_excel["CODIGO"].astype(str).str.strip()
        )
    )
else:
    pares_hechos = set()



# Totales planificados (según el Excel maestro)
total_planificados = len(df_maestro)

# Completados global (cruce con el Excel de registros)
completados_global = sum(
    1 for _, row in df_maestro.iterrows()
    if (str(row["MAQUINA"]).strip(), str(row["CODIGO"]).strip()) in pares_hechos
)

pendientes_global = total_planificados - completados_global
avance_global = round((completados_global / st.session_state.meta_preventivos) * 100, 1) if total_planificados else 0.0




cG1, cG2, cG3, cG4 = st.columns(4)
cG1.metric("✅ Completados", completados_global)
cG2.metric("🗂️ Planificados", st.session_state.meta_preventivos)
cG3.metric("📊 Avance (Al plan)", f"{avance_global}%")
cG4.metric("⌛ Pendientes (Al plan)", pendientes_global)

# Comparación contra tu meta
if completados_global >= st.session_state.meta_preventivos:
    st.success(f"✅ Meta alcanzada ({completados_global}/{st.session_state.meta_preventivos})")
else:
    st.warning(f"⚠️ Faltan {st.session_state.meta_preventivos - completados_global} para la meta ({completados_global}/{st.session_state.meta_preventivos})")
# ========= FIN CONTADOR GENERAL =========








# --- Selección de máquina desde Excel maestro ------------------------------------------------------------

maquinas = df_maestro["MAQUINA"].unique()
maquina_seleccionada = st.selectbox("Selecciona una máquina", maquinas)

# Filtrar solo los códigos de esa máquina
df_codigos = df_maestro[df_maestro["MAQUINA"] == maquina_seleccionada]

# --- CRUCE DE DATOS CON EL EXCEL DE PREVENTIVOS ---
df = df_codigos.copy()
df["Estado"] = df["CODIGO"].apply(
    lambda c: "Completado" if (
        (maquina_seleccionada in df_excel["MAQUINA"].values) and
        (c in df_excel.loc[df_excel["MAQUINA"] == maquina_seleccionada, "CODIGO"].values)
    ) else "Pendiente"
)
df["Fecha"] = df["CODIGO"].apply(
    lambda c: (
        df_excel.loc[
            (df_excel["MAQUINA"] == maquina_seleccionada) & (df_excel["CODIGO"] == c),
            "FECHA"
        ].values[0]
        if ((df_excel["MAQUINA"] == maquina_seleccionada) & (df_excel["CODIGO"] == c)).any()
        else ""
    )
)

# --- Mostrar en tabla con colores ---
def color_estado(val):
    if val == "Pendiente":
        return 'background-color: #FF9999'
    elif val == "Completado":
        return 'background-color: #99FF99'
    return ''

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

# Eliminamos la columna "MAQUINA" (ya está en el buscador)
if "MAQUINA" in df.columns:
    df = df.drop(columns=["MAQUINA"])

st.subheader(maquina_seleccionada)
st.dataframe(df.style.applymap(color_estado), use_container_width=True)


if st.session_state.autenticado:
    if st.button("Cerrar sesión"):
        st.session_state.autenticado = False
        st.experimental_rerun()

































