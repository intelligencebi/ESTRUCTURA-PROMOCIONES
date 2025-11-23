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

# Función auxiliar para formato monetario argentino 🇦🇷
def formatear_moneda(valor):
    try:
        return f"$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return valor


# ===============================================
# 📈 BLOQUE 1: Resumen Diario por Promoción
# ===============================================
st.subheader("📆 Resumen Diario por Promoción")

try:
    response = supabase.rpc("resumen_por_promocion", {"promo_name": promo}).execute()
    data = response.data

    if data:
        df = pd.DataFrame(data)

        # Formatear columnas monetarias
        for col in ["total_in", "total_out", "ganancias"]:
            if col in df.columns:
                df[col] = df[col].apply(formatear_moneda)

        st.dataframe(df, use_container_width=True, height=400)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Total In", f"{formatear_moneda(pd.to_numeric(df['total_in'].str.replace('$','').str.replace('.','').str.replace(',','.'), errors='coerce').sum())}")
        col2.metric("💸 Total Out", f"{formatear_moneda(pd.to_numeric(df['total_out'].str.replace('$','').str.replace('.','').str.replace(',','.'), errors='coerce').sum())}")
        col3.metric("📈 Ganancia Neta", f"{formatear_moneda(pd.to_numeric(df['ganancias'].str.replace('$','').str.replace('.','').str.replace(',','.'), errors='coerce').sum())}")
        col4.metric("🧮 Días Activos", f"{len(df)} días")
    else:
        st.warning("No hay datos para esta promoción.")
except Exception as e:
    st.error(f"❌ Error al obtener los datos diarios: {e}")


# ===============================================
# 🧾 BLOQUE 2: DETALLE POR IDENTIFICADOR
# ===============================================
st.subheader("📋 Detalle por Identificador de Propuesta")

# ======= FILTROS =======
st.markdown("### 🎯 Filtros")

# Fechas
col_f1, col_f2 = st.columns(2)
fecha_inicio = col_f1.date_input("📅 Fecha Inicio", pd.to_datetime("2024-01-01"))
fecha_fin = col_f2.date_input("📅 Fecha Fin", pd.to_datetime("today"))

# Obtener identificadores disponibles
response_ident = supabase.rpc("resumen_total_por_propuesta").execute()

if response_ident.data:
    df_identificadores = pd.DataFrame(response_ident.data)
    lista_identificadores = sorted(df_identificadores["identificador"].dropna().unique())
else:
    lista_identificadores = []

identificador = st.selectbox("🧩 Seleccionar Identificador", ["Todos"] + lista_identificadores)

# ======= CONSULTA FINAL FILTRADA =======
try:
    filtros = {
        "p_promo_name": None if identificador == "Todos" else identificador,
        "p_fecha_inicio": fecha_inicio.isoformat(),
        "p_fecha_fin": fecha_fin.isoformat()
    }

    response = supabase.rpc("resumen_total_por_propuesta", filtros).execute()

    if response.data:
        df_detalle = pd.DataFrame(response.data)

        # Formato monetario
        if "total_recaudado" in df_detalle.columns:
            df_detalle["total_recaudado"] = df_detalle["total_recaudado"].apply(formatear_moneda)

        st.dataframe(df_detalle, use_container_width=True, height=350)

        total_global = pd.to_numeric(
            df_detalle["total_recaudado"]
            .replace("[^0-9,]", "", regex=True)
            .str.replace(".", "")
            .str.replace(",", "."),
            errors="coerce"
        ).sum()

        total_usuarios = df_detalle["total_convertidos"].sum()

        col1, col2 = st.columns(2)
        col1.metric("👥 Total Convertidos", f"{int(total_usuarios):,}".replace(",", "."))
        col2.metric("💰 Total Recaudado", formatear_moneda(total_global))

        # Descargar CSV
        csv = df_detalle.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📤 Descargar Detalle de Propuestas",
            csv,
            "detalle_por_propuesta.csv",
            "text/csv"
        )
    else:
        st.info("No se encontraron datos para los filtros seleccionados.")

except Exception as e:
    st.error(f"❌ Error al obtener el detalle filtrado: {e}")


# ===============================================
# 🧩 BLOQUE 3: RESUMEN AGRUPADO POR NOMBRE
# ===============================================
st.subheader("📊 Totales Agrupados por Nombre de Propuesta")

try:
    response = supabase.rpc("resumen_por_nombre_propuesta").execute()
    if response.data:
        df_general = pd.DataFrame(response.data)

        if "total_recaudado" in df_general.columns:
            df_general["total_recaudado"] = df_general["total_recaudado"].apply(formatear_moneda)

        st.dataframe(df_general, use_container_width=True, height=300)
    else:
        st.info("No se encontraron totales agrupados por nombre de propuesta.")
except Exception as e:
    st.error(f"❌ Error al obtener el resumen general: {e}")
