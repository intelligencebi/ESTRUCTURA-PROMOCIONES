import streamlit as st
import pandas as pd
from supabase import create_client

# ==========================
# 🔌 CONEXIÓN A SUPABASE
# ==========================
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)

# ==========================
# 🎯 PÁGINA: RESUMEN DE PROMOS
# ==========================
st.set_page_config(page_title="Resumen Promos", page_icon="📊", layout="wide")
st.title("📊 Resumen Diario por Promoción")

# Selector de promoción
promo = st.selectbox(
    "Seleccioná una promoción",
    ["PROMO ORO", "PROMO PLATA", "PROMO SMS", "PROMO SPAM"]
)

# Llamada a la función SQL en Supabase
try:
    response = supabase.rpc("resumen_por_promocion", {"promo_name": promo}).execute()
    data = response.data

    if not data:
        st.warning("No hay datos para esta promoción.")
    else:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Total In", f"${df['total_in'].sum():,.2f}")
        col2.metric("💸 Total Out", f"${df['total_out'].sum():,.2f}")
        col3.metric("📈 Ganancia Neta", f"${df['ganancias'].sum():,.2f}")
        col4.metric("🧮 Días Activos", f"{len(df)} días")

except Exception as e:
    st.error(f"❌ Error al obtener los datos: {e}")
