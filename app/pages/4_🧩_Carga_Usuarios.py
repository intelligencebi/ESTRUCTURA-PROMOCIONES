import streamlit as st
import pandas as pd
import datetime
from supabase import create_client

# ===============================
# ⚙️ CONFIGURACIÓN DE LA PÁGINA
# ===============================
st.set_page_config(page_title="Carga de Usuarios", page_icon="🧩", layout="wide")
st.title("🧩 Registro de Contactos Promocionales")

# ===============================
# 🔌 CONEXIÓN A SUPABASE
# ===============================
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)

# ===============================
# 📘 INSTRUCCIONES
# ===============================
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

# ===============================
# 📂 SUBIDA DEL ARCHIVO
# ===============================
uploaded_file = st.file_uploader("📂 Subí el archivo de contactos (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        # Leer archivo Excel
        df = pd.read_excel(uploaded_file)

        st.success(f"Archivo cargado correctamente ({len(df)} filas).")
        st.dataframe(df.head(), use_container_width=True)

        # ===============================
        # 🧹 LIMPIEZA DE DATOS
        # ===============================
        # Reemplaza NaN por texto vacío o 0 según corresponda
        df = df.fillna("")

        # Conversión universal de datetime, date o timestamp → string
        def convertir_valor(v):
            if isinstance(v, (datetime.datetime, datetime.date, pd.Timestamp)):
                return v.strftime("%Y-%m-%d %H:%M:%S")
            return v

        df = df.applymap(convertir_valor)

        # ===============================
        # 🚀 CARGA A SUPABASE
        # ===============================
        if st.button("🚀 Cargar contactos a Supabase"):
            data = df.to_dict(orient="records")

            # Inserción masiva
            response = supabase.table("contactos_promocionales").insert(data).execute()

            if response.data:
                st.success(f"✅ {len(df)} contactos cargados correctamente en Supabase.")
            else:
                st.warning("⚠️ No se insertaron datos. Verificá los nombres de columnas o el formato.")

    except Exception as e:
        st.error(f"❌ Error al subir los datos: {e}")
