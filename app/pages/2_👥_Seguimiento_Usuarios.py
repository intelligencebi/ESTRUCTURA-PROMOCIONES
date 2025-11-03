import streamlit as st
import pandas as pd
from app.utils.queries import get_seguimiento_promocion

st.title("👥 Seguimiento de Usuarios Convertidos")

promo = st.selectbox("Seleccioná la promoción", ["PROMO ORO", "PROMO PLATA", "PROMO SMS", "PROMO SPAM"])
fecha_inicio = st.date_input("Desde")
fecha_fin = st.date_input("Hasta")

data = get_seguimiento_promocion(promo, fecha_inicio, fecha_fin)
df = pd.DataFrame(data)
st.dataframe(df)

st.metric("Usuarios Convertidos", len(df))
st.metric("Total Cargas", df["total_cargas"].sum())
st.metric("Profit Total", df["profit"].sum())
