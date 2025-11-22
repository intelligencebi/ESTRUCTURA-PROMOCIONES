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

# === 🧮 FILTROS INTERACTIVOS PERSISTENTES ===
st.markdown("### ⚙️ Filtros de visualización")
colf1, colf2 = st.columns(2)
with colf1:
    filtrar_cargaron = st.checkbox(
        "Mostrar solo usuarios con cargas > 0",
        key="filtrar_cargaron",
        value=st.session_state.get("filtrar_cargaron", False),
    )
with colf2:
    filtrar_retiraron = st.checkbox(
        "Mostrar solo usuarios que retiraron sin cargar",
        key="filtrar_retiraron",
        value=st.session_state.get("filtrar_retiraron", False),
    )

# ==========================
# 🚀 BLOQUE 1 - SEGUIMIENTO POR PROMOCIÓN
# ==========================
if st.button("🔍 Consultar Seguimiento"):
    try:
        # 🔄 Recuperar todos los registros en lotes de 1000
        all_data = []
        batch_size = 1000
        offset = 0

        while True:
            batch = (
                supabase.rpc(
                    "seguimiento_por_promocion",
                    {
                        "p_promo_name": promo,
                        "p_fecha_inicio": str(fecha_inicio),
                        "p_fecha_fin": str(fecha_fin)
                    }
                )
                .range(offset, offset + batch_size - 1)
                .execute()
            )

            if not batch.data:
                break

            all_data.extend(batch.data)

            if len(batch.data) < batch_size:
                break

            offset += batch_size

        # ✅ Convertir a DataFrame si hay datos
        if all_data:
            df = pd.DataFrame(all_data)

            # === Aplicar filtros persistentes ===
            df_filtrado = df.copy()

            if filtrar_cargaron:
                df_filtrado = df_filtrado[df_filtrado["total_cargas"] > 0]

            if filtrar_retiraron:
                df_filtrado = df_filtrado[
                    df_filtrado["retiraron_sin_cargar"].notnull()
                    & (df_filtrado["retiraron_sin_cargar"] != "None")
                ]

            # === 📊 MÉTRICAS SUPERIORES ===
            col1, col2, col3, col4 = st.columns(4)
            usuarios_convertidos = (df_filtrado["total_cargas"] > 0).sum()
            col1.metric("👥 Usuarios Convertidos", usuarios_convertidos)
            col2.metric("💰 Total Cargas", f"${df_filtrado['total_cargas'].sum():,.2f}")
            col3.metric("🏧 Total Retirado", f"${df_filtrado['total_retiros'].sum():,.2f}")
            col4.metric("📈 Profit Total", f"${df_filtrado['profit'].sum():,.2f}")

            # === 📋 RESULTADOS COMPLETOS ===
            st.markdown("### 📋 Resultados completos")
            st.dataframe(
                df_filtrado,
                use_container_width=True,
                height=min(900, 40 + len(df_filtrado) * 35),
            )

            # Mostrar cantidad total exacta
            st.caption(f"Mostrando {len(df_filtrado):,} registros filtrados de un total de {len(df):,} obtenidos de Supabase ✅")

            # 📥 Exportar CSV completo o filtrado
            csv = df_filtrado.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📤 Descargar resultados filtrados en CSV",
                csv,
                file_name=f"seguimiento_{promo}_{fecha_inicio}_{fecha_fin}.csv",
                mime="text/csv"
            )

            # ✅ Alternativa: vista paginada si el DataFrame es muy grande
            if len(df_filtrado) > 5000:
                st.warning("⚠️ El dataset es grande, se recomienda descargar el CSV completo para un análisis fluido.")
                page_size = st.slider("📄 Registros por página", 500, 2000, 1000)
                num_pages = (len(df_filtrado) // page_size) + 1
                page = st.number_input("Página", 1, num_pages, 1)
                start = (page - 1) * page_size
                end = start + page_size
                st.dataframe(df_filtrado.iloc[start:end], use_container_width=True, height=600)

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

            total_jugadores = df_ltv["jugadores_sobrevivientes"].iloc[0] if len(df_ltv) > 0 else 0
            total_ltv = df_ltv["ltv_acumulado"].iloc[-1] if len(df_ltv) > 0 else 0
            retencion_actual = df_ltv["retencion_pct"].iloc[-1] if len(df_ltv) > 0 else 0

            c1, c2, c3 = st.columns(3)
            c1.metric("👥 Jugadores Iniciales", f"{total_jugadores:,}")
            c2.metric("💰 LTV Acumulado Total", f"${total_ltv:,.2f}")
            c3.metric("📉 Retención Actual", f"{retencion_actual:.2f}%")

            st.markdown("### 📈 Curva de LTV acumulado y retención")
            chart_data = df_ltv.set_index("mes_actividad")[["ltv_acumulado", "retencion_pct"]]
            st.line_chart(chart_data)

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
