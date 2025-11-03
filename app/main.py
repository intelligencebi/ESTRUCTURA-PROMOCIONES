import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Seguimiento Promos", page_icon="🎯", layout="wide")

st.title("🎯 Strike Promos Tracker")
st.write("Sistema de seguimiento de promociones y conversiones de jugadores.")

st.markdown("""
**Secciones disponibles:**
- 📊 *Resumen Promos*: visión diaria por tipo de promoción.
- 👥 *Seguimiento Usuarios*: análisis individual de conversiones.
- 📝 *Carga de Contactos*: registrar nuevos contactos y ofertas.
""")

# ===============================
# 🔌 PRUEBA DE CONEXIÓN A SUPABASE
# ===============================
st.subheader("🔌 Test de conexión a Supabase")

try:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    supabase = create_client(url, key)

    res = supabase.table("jugadores").select("*").limit(5).execute()
    st.success("✅ Conexión exitosa con Supabase")
    st.write(res.data)
except Exception as e:
    st.error(f"❌ Error al conectar: {e}")
