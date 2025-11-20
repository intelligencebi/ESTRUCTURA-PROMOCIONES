import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

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

promo = st.selectbox(
    "Seleccioná una promoción",
    ["PROMO ORO", "PROMO PLATA", "PROMO SMS", "PROMO SPAM"]
)

# ---- Bloque 1: Resumen Diario existente ----
try:
    response = supabase.rpc("resumen_por_promocion", {"promo_name": promo}).execute()
    data = response.data

    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Total In", f"${df['total_in'].sum():,.2f}")
        col2.metric("💸 Total Out", f"${df['total_out'].sum():,.2f}")
        col3.metric("📈 Ganancia Neta", f"${df['ganancias'].sum():,.2f}")
        col4.metric("🧮 Días Activos", f"{len(df)} días")
    else:
        st.warning("No hay datos para esta promoción.")
except Exception as e:
    st.error(f"❌ Error al obtener los datos diarios: {e}")

# ---- Bloque 2: Resumen General por Identificador ----
st.subheader("📋 Resumen General por Identificador")

try:
    response = supabase.rpc("resumen_general_promos").execute()
    if response.data:
        df_general = pd.DataFrame(response.data)
        st.dataframe(df_general, use_container_width=True, height=400)

        total_global = df_general["total_recaudado"].sum()
        st.metric("💰 Total Recaudado (General)", f"${total_global:,.2f}")

        # Opción de descarga
        csv = df_general.to_csv(index=False).encode("utf-8")
        st.download_button("📤 Descargar Resumen General", csv, "resumen_general_promos.csv", "text/csv")
    else:
        st.info("No se encontraron datos generales.")
except Exception as e:
    st.error(f"❌ Error al obtener el resumen general: {e}")

# ---- Bloque 3: Resumen Total por Nombre de Propuesta ----
st.subheader("📊 Totales por Nombre de Propuesta")

try:
    response = supabase.rpc("resumen_total_por_propuesta").execute()
    if response.data:
        df_total = pd.DataFrame(response.data)
        st.dataframe(df_total, use_container_width=True, height=300)
    else:
        st.info("No se encontraron totales por propuesta.")
except Exception as e:
    st.error(f"❌ Error al obtener los totales por propuesta: {e}")
