
import streamlit as st
import pandas as pd
from app.utils.queries import get_seguimiento_promocion

st.set_page_config(page_title="Seguimiento Usuarios", page_icon="👥", layout="wide")

st.title("👥 Seguimiento de Usuarios Convertidos")

promo = st.selectbox("Seleccioná la promoción", ["PROMO ORO", "PROMO PLATA", "PROMO SMS", "PROMO SPAM"])
fecha_inicio = st.date_input("Desde")
fecha_fin = st.date_input("Hasta")

if st.button("🔍 Consultar Seguimiento"):
    data = get_seguimiento_promocion(promo, fecha_inicio, fecha_fin)
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

        col1, col2, col3 = st.columns(3)
        col1.metric("👥 Usuarios Convertidos", len(df))
        col2.metric("💰 Total Cargas", f"${df['total_cargas'].sum():,.2f}")
        col3.metric("📈 Profit Total", f"${df['profit'].sum():,.2f}")
    else:
        st.info("No se encontraron registros para los filtros seleccionados.")
