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
st.title("📊 Resumen Diario y General por Promoción")

promo = st.selectbox(
    "Seleccioná una promoción",
    ["PROMO ORO", "PROMO PLATA", "PROMO SMS", "PROMO SPAM"]
)

# ---- 📈 BLOQUE 1: Resumen Diario (función existente) ----
st.subheader("📆 Resumen Diario por Promoción")

try:
    response = supabase.rpc("resumen_por_promocion", {"promo_name": promo}).execute()
    data = response.data

    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, height=400)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Total In", f"${df['total_in'].sum():,.2f}")
        col2.metric("💸 Total Out", f"${df['total_out'].sum():,.2f}")
        col3.metric("📈 Ganancia Neta", f"${df['ganancias'].sum():,.2f}")
        col4.metric("🧮 Días Activos", f"{len(df)} días")
    else:
        st.info("No hay datos para esta promoción.")
except Exception as e:
    st.error(f"❌ Error al obtener los datos diarios: {e}")

# ---- 🧾 BLOQUE 2: Resumen Total por Propuesta (DETALLE) ----
st.subheader("📋 Detalle por Identificador de Propuesta")

try:
    response = supabase.rpc("resumen_total_por_propuesta").execute()
    if response.data:
        df_detalle = pd.DataFrame(response.data)
        st.dataframe(df_detalle, use_container_width=True, height=350)

        total_global = df_detalle["total_recaudado"].sum()
        total_usuarios = df_detalle["total_convertidos"].sum()

        col1, col2 = st.columns(2)
        col1.metric("👥 Total Convertidos (Global)", f"{int(total_usuarios):,}")
        col2.metric("💰 Total Recaudado (Global)", f"${total_global:,.2f}")

        # 📥 Descargar CSV
        csv = df_detalle.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📤 Descargar Detalle de Propuestas",
            csv,
            "detalle_por_propuesta.csv",
            "text/csv"
        )
    else:
        st.info("No se encontraron datos por propuesta.")
except Exception as e:
    st.error(f"❌ Error al obtener los totales por propuesta: {e}")

# ---- 🧩 BLOQUE 3: Resumen Agrupado por Nombre (GENERAL) ----
st.subheader("📊 Totales Agrupados por Nombre de Propuesta")

try:
    response = supabase.rpc("resumen_por_nombre_propuesta").execute()
    if response.data:
        df_general = pd.DataFrame(response.data)
        st.dataframe(df_general, use_container_width=True, height=300)
    else:
        st.info("No se encontraron totales agrupados por nombre de propuesta.")
except Exception as e:
    st.error(f"❌ Error al obtener el resumen general: {e}")
