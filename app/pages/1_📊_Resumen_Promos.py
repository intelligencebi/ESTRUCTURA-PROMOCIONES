import streamlit as st
import pandas as pd
from app.utils.queries import get_resumen_promocion

st.title("📊 Resumen de Promociones")

promo = st.selectbox("Seleccioná una promoción", ["PROMO ORO", "PROMO PLATA", "PROMO SMS", "PROMO SPAM"])

data = get_resumen_promocion(promo)
df = pd.DataFrame(data)
st.dataframe(df)

st.metric("Total In", df["total_in"].sum())
st.metric("Total Out", df["total_out"].sum())
st.metric("Profit", df["ganancias"].sum())
