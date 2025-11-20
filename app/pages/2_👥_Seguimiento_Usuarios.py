import streamlit as st
import pandas as pd
from app.utils.supabase_client import supabase
from datetime import date

# ==========================
# 🎯 CONFIGURACIÓN DE PÁGINA
# ==========================
st.set_page_config(page_title="Seguimiento Usuarios", page_icon="👥", layout="wide")
st.title("👥 Seguimiento de Usuarios Convertidos")

# ==========================
# 📋 FILTROS SEGUIMIENTO GENERAL
# ==========================
promo = st.selectbox(
    "Seleccioná la promoción",
    ["PROMO ORO", "PROMO PLATA", "PROMO SMS", "PROMO SPAM"],
    index=2
)

fecha_inicio = st.date_input("Desde", date(2025, 11, 1))
fecha_fin = st.date_input("Hasta", date(2025, 11, 19))

# ==========================
# 🚀 BLOQUE 1 - SEGUIMIENTO POR PROMOCIÓN
# ==========================
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

# =======================================================
# 📈 BLOQUE 2 - ANÁLISIS LTV POR COHORTE
# =======================================================
st.markdown("---")
st.subheader("📊 Análisis LTV por Cohorte")

col1, col2, col3 = st.columns(3)
with col1:
    nombre_propuesta = st.selectbox(
        "📋 Nombre de propuesta",
        ["ADQUISICION - TERCEROS", "RECUPERACION INACTIVOS", "RECUPERACION TELEFONOS MUERTOS"]
    )
with col2:
    # 🔄 Obtener identificadores válidos desde la base
    try:
        response_ids = supabase.rpc(
            "obtener_identificadores_validos",
            {"p_nombre_propuesta": nombre_propuesta}
        ).execute()

        if response_ids.data:
            lista_identificadores = sorted([r["identificador"] for r in response_ids.data])
        else:
            lista_identificadores = []

    except Exception as e:
        st.error(f"❌ Error al cargar identificadores: {e}")
        lista_identificadores = []

    identificador = st.selectbox(
        "🧩 Identificador",
        lista_identificadores if lista_identificadores else ["(Sin identificadores disponibles)"]
    )
with col3:
    mes_ingreso = st.date_input("🗓️ Mes de ingreso", date(2025, 11, 1))

if st.button("📈 Analizar Cohorte"):
    try:
        response = supabase.rpc(
            "ltv_por_cohorte",
            {
                "p_nombre_propuesta": nombre_propuesta,
                "p_identificador": identificador,
                "p_mes_ingreso": str(mes_ingreso)
            }
        ).execute()

        if response.data:
            df_ltv = pd.DataFrame(response.data)

            st.markdown("### 📅 Evolución mensual de la cohorte seleccionada")
            st.dataframe(df_ltv, use_container_width=True, height=500)

            # === MÉTRICAS RESUMEN ===
            total_jugadores = df_ltv["jugadores_sobrevivientes"].iloc[0] if len(df_ltv) > 0 else 0
            total_ltv = df_ltv["ltv_acumulado"].iloc[-1] if len(df_ltv) > 0 else 0
            retencion_actual = df_ltv["retencion_pct"].iloc[-1] if len(df_ltv) > 0 else 0

            c1, c2, c3 = st.columns(3)
            c1.metric("👥 Jugadores Iniciales", f"{total_jugadores:,}")
            c2.metric("💰 LTV Acumulado Total", f"${total_ltv:,.2f}")
            c3.metric("📉 Retención Actual", f"{retencion_actual:.2f}%")

            # === VISUALIZACIÓN ===
            st.markdown("### 📈 Curva de LTV acumulado y retención")
            chart_data = df_ltv.set_index("mes_actividad")[["ltv_acumulado", "retencion_pct"]]
            st.line_chart(chart_data)

            # === EXPORTAR CSV ===
            csv_ltv = df_ltv.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📤 Descargar análisis LTV",
                csv_ltv,
                file_name=f"ltv_cohorte_{identificador}_{mes_ingreso}.csv",
                mime="text/csv"
            )
        else:
            st.info("⚠️ No se encontraron datos para la cohorte seleccionada.")
    except Exception as e:
        st.error(f"❌ Error al consultar la cohorte: {e}")
