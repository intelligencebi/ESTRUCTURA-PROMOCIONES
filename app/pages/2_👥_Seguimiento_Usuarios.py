import streamlit as st
import pandas as pd
from app.utils.supabase_client import supabase  # ✅ usamos el cliente directo
from datetime import date

st.set_page_config(page_title="Seguimiento Usuarios", page_icon="👥", layout="wide")
st.title("👥 Seguimiento de Usuarios Convertidos")

# 📋 Filtros de búsqueda
promo = st.selectbox(
    "Seleccioná la promoción",
    ["PROMO ORO", "PROMO PLATA", "PROMO SMS", "PROMO SPAM"],
    index=2  # por defecto muestra PROMO SMS
)

fecha_inicio = st.date_input("Desde", date(2025, 11, 1))
fecha_fin = st.date_input("Hasta", date(2025, 11, 19))

# 🚀 Acción: ejecutar la función de Supabase
if st.button("🔍 Consultar Seguimiento"):
    try:
        response = supabase.rpc(
            "seguimiento_por_promocion",
            {
                "p_promo_name": promo,
                "p_fecha_inicio": str(fecha_inicio),
                "p_fecha_fin": str(fecha_fin)
            }
        ).execute()

        if response.data:
            df = pd.DataFrame(response.data)

            # ✅ Métricas superiores
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("👥 Usuarios Convertidos", len(df))
            col2.metric("💰 Total Cargas", f"${df['total_cargas'].sum():,.2f}")
            col3.metric("🏧 Total Retirado", f"${df['total_retiros'].sum():,.2f}")
            col4.metric("📈 Profit Total", f"${df['profit'].sum():,.2f}")
            # 📊 Tabla de resultados
            st.dataframe(df, use_container_width=True, height=600)

            # 📥 Exportar a CSV
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📤 Descargar resultados en CSV",
                csv,
                file_name=f"seguimiento_{promo}_{fecha_inicio}_{fecha_fin}.csv",
                mime="text/csv"
            )

        else:
            st.info("No se encontraron registros para los filtros seleccionados.")

    except Exception as e:
        st.error(f"❌ Error al consultar los datos: {e}")
