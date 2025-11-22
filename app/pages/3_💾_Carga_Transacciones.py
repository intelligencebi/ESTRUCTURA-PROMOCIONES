import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
import datetime
import time
from app.utils.supabase_client import supabase

st.set_page_config(page_title="Registro general de jugadores", page_icon="📋", layout="wide")

st.title("📋 Registro general de jugadores")
st.caption("Seleccioná el casino al que pertenece este reporte y subí el archivo Excel (.xlsx o .csv).")

# 1️⃣ Seleccionar la plataforma
plataforma = st.selectbox(
    "🎰 Seleccioná la plataforma del reporte:",
    ["Fénix", "Eros", "Bet Argento", "Atlantis", "Spirita", "Mi Jugada"]
)

# 2️⃣ Subir el archivo Excel o CSV
uploaded_file = st.file_uploader("📂 Subí el archivo del reporte (.xlsx o .csv)", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # Leer Excel o CSV automáticamente
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success(f"Archivo cargado correctamente ({len(df)} filas).")
        st.dataframe(df.head(10), use_container_width=True)

        if st.button("🚀 Subir a Supabase"):
            # Mapeo de columnas
            column_map = {
                "ID": "id_excel",
                "operación": "operacion",
                "Depositar": "depositar",
                "Retirar": "retirar",
                "Wager": "wager",
                "Límites": "limites",
                "Balance antes de operación": "balance_antes_operacion",
                "Fecha": "fecha",
                "Tiempo": "tiempo",
                "Iniciador": "iniciador",
                "Del usuario": "del_usuario",
                "Sistema": "sistema",
                "Al usuario": "al_usuario",
                "IP": "ip"
            }
            df = df.rename(columns=column_map)

            # Normalización básica
            df["depositar"] = pd.to_numeric(df["depositar"], errors="coerce").fillna(0)
            df["retirar"] = pd.to_numeric(df["retirar"], errors="coerce").fillna(0)
            df["wager"] = pd.to_numeric(df["wager"], errors="coerce").fillna(0)

            # Agregar la columna de plataforma
            df["plataforma"] = plataforma

            # Eliminar columna ID de Excel
            if "id_excel" in df.columns:
                df = df.drop(columns=["id_excel"])

            # 🔧 Limpieza de NaN
            df = df.fillna("")

            # 🔧 Conversión universal a string si el valor es datetime o date o time
            def convertir_valor(v):
                if isinstance(v, (datetime.datetime, datetime.date, datetime.time, pd.Timestamp)):
                    return v.strftime("%Y-%m-%d %H:%M:%S")
                return v

            df = df.applymap(convertir_valor)

            # ===============================
            # 🚀 CARGA A SUPABASE (EN LOTES)
            # ===============================
            data = df.to_dict(orient="records")
            total_rows = len(data)
            batch_size = 1000  # 🔹 Tamaño del lote
            success_rows = 0
            errores = []

            progress_bar = st.progress(0)
            status_text = st.empty()

            for i in range(0, total_rows, batch_size):
                batch = data[i:i + batch_size]
                try:
                    response = supabase.table("transacciones").insert(batch).execute()
                    if response.data is not None:
                        success_rows += len(batch)
                except Exception as e:
                    errores.append(f"Lote {i // batch_size + 1}: {e}")
                    st.warning(f"⚠️ Error en el lote {i // batch_size + 1}: {e}")
                    continue

                # Actualizar progreso
                progreso = min((i + batch_size) / total_rows, 1.0)
                progress_bar.progress(progreso)
                status_text.text(f"Lote {i // batch_size + 1} cargado ({success_rows}/{total_rows})")

                # 🔸 Delay corto para evitar throttling
                time.sleep(0.4)

            progress_bar.progress(1.0)

            if errores:
                st.warning(f"⚠️ {len(errores)} lotes fallaron. Mostrando los primeros 3:")
                st.write(errores[:3])

            st.success(f"✅ Carga completada: {success_rows} de {total_rows} filas subidas correctamente a '{plataforma}'.")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
