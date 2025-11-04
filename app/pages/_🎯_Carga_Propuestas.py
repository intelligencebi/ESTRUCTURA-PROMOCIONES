import streamlit as st
import pandas as pd
from supabase import create_client

# ============================
# Configuración de página
# ============================
st.set_page_config(page_title="Carga de Propuestas", page_icon="🎯", layout="wide")
st.title("🎯 Registro de Propuestas Promocionales")

st.markdown("""
Esta sección te permite **agregar o cargar masivamente** las propuestas promocionales
que luego se usarán en la tabla `contactos_promocionales`.

Cada propuesta define:
- `identificador` (ej: PLATA_ADQ_TERCEROS_01)
- `promo` (PROMO PLATA, PROMO SMS, PROMO ORO, etc.)
- `nombre_propuesta`
- `objetivo`
- `target`
- `bono`
- `mecanica`
- `prioridad`
- `estado`
""")

# ============================
# Conexión a Supabase
# ============================
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)

# ============================
# Opción 1: Carga manual rápida
# ============================
st.subheader("➕ Agregar propuesta individual")

with st.form("add_propuesta"):
    identificador = st.text_input("Identificador", placeholder="PLATA_ADQ_TERCEROS_01")
    promo = st.selectbox("Tipo de Promo", ["PROMO PLATA", "PROMO SMS", "PROMO ORO", "PROMO SPAM"])
    nombre = st.text_input("Nombre de Propuesta", placeholder="Adquisición - Terceros")
    objetivo = st.text_area("Objetivo")
    target = st.text_input("Target", placeholder="VIPs, inactivos, terceros...")
    bono = st.text_input("Bono", placeholder="Bono 100%, Fichas regalo...")
    mecanica = st.text_area("Mecánica")
    prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
    estado = st.selectbox("Estado", ["ACTIVA", "FINALIZADA", "PAUSADA"], index=0)
    
    submitted = st.form_submit_button("Guardar propuesta")

    if submitted:
        try:
            data = {
                "identificador": identificador,
                "promo": promo,
                "nombre_propuesta": nombre,
                "objetivo": objetivo,
                "target": target,
                "bono": bono,
                "mecanica": mecanica,
                "prioridad": prioridad,
                "estado": estado
            }
            supabase.table("propuestas_promocionales").insert(data).execute()
            st.success("✅ Propuesta registrada correctamente.")
        except Exception as e:
            st.error(f"❌ Error al guardar la propuesta: {e}")

# ============================
# Opción 2: Carga masiva desde Excel
# ============================
st.divider()
st.subheader("📂 Carga masiva desde archivo Excel (.xlsx)")

uploaded_file = st.file_uploader("Subí tu archivo con propuestas", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("### Vista previa")
    st.dataframe(df.head(), use_container_width=True)

    if st.button("🚀 Cargar todas las propuestas"):
        try:
            data = df.to_dict(orient="records")
            supabase.table("propuestas_promocionales").insert(data).execute()
            st.success("✅ Propuestas cargadas correctamente en Supabase.")
        except Exception as e:
            st.error(f"❌ Error al subir las propuestas: {e}")
