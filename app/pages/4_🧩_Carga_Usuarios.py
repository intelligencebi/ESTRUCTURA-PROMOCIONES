import streamlit as st
import pandas as pd
from supabase import create_client

# Config
st.set_page_config(page_title="Carga de Usuarios", page_icon="🧩", layout="wide")
st.title("🧩 Registro de Contactos Promocionales")

# Conexión a Supabase
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)

# Explicación
st.markdown("""
Subí un archivo Excel (.xlsx) con los usuarios contactados y sus datos promocionales.
Cada registro debe incluir:
- **nombre_usuario**
- **fecha_contacto**
- **promo** (PROMO ORO, PROMO PLATA, PROMO SMS, PROMO SPAM)
- **propuesta_id** (ej: PLATA_ADQ_TERCEROS_01)
- **call_to_action**
- **monto_ofrecido**
- **plataforma_origen**
- **plataforma_destino**
- **observaciones**
""")

# Subida del archivo
uploaded_file = st.file_uploader("📂 Subí el archivo de contactos (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("### Vista previa de los datos")
    st.dataframe(df.head(), use_container_width=True)

    # Confirmación
    if st.button("🚀 Cargar contactos a Supabase"):
        try:
            data = df.to_dict(orient="records")
            for row in data:
                supabase.table("contactos_promocionales").insert(row).execute()
            st.success("✅ Contactos cargados correctamente en Supabase.")
        except Exception as e:
            st.error(f"❌ Error al subir los datos: {e}")
