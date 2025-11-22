import streamlit as st
import pandas as pd
import datetime
from supabase import create_client
import time

# ===============================
# ⚙️ CONFIGURACIÓN DE LA PÁGINA
# ===============================
st.set_page_config(page_title="Carga de Usuarios", page_icon="🧩", layout="wide")
st.title("🧩 Registro de Contactos Promocionales")

# ===============================
# 🔌 CONEXIÓN A SUPABASE
# ===============================
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)

# ===============================
# 📘 INSTRUCCIONES
# ===============================
st.markdown("""
Subí un archivo Excel (.xlsx) con los usuarios contactados y sus datos promocionales.

Cada registro debe incluir:

- **nombre_usuario**
- **fecha_contacto**
- **promo** (PROMO ORO, PROMO PLATA, PROMO SMS, PROMO SPAM)
- **propuesta_id** (ej: PLATA_ADQ_TERCEROS_01)
- **call_to_action**
- **monto_ofrecido**
- **plataforma_origen**
- **plataforma_destino**
- **observaciones**
""")

# ===============================
# 📂 SUBIDA DEL ARCHIVO
# ===============================
uploaded_file = st.file_uploader("📂 Subí el archivo de contactos (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        # Leer archivo Excel
        df = pd.read_excel(uploaded_file)

        st.success(f"Archivo cargado correctamente ({len(df)} filas).")
        st.dataframe(df.head(), use_container_width=True)

        # ===============================
        # 🧹 LIMPIEZA DE DATOS
        # ===============================
        df = df.fillna("")

        # Conversión de tipos específicos
        def convertir_valor(v):
            if isinstance(v, (datetime.datetime, datetime.date, pd.Timestamp)):
                return v.strftime("%Y-%m-%d %H:%M:%S")
            return v

        df = df.applymap(convertir_valor)

        # 🔢 Asegurar que monto_ofrecido sea numérico válido
        if "monto_ofrecido" in df.columns:
            df["monto_ofrecido"] = pd.to_numeric(df["monto_ofrecido"], errors="coerce").fillna(0)

        # Limpieza del campo propuesta_id
        if "propuesta_id" in df.columns:
            df["propuesta_id"] = (
                df["propuesta_id"]
                .astype(str)
                .str.replace("ID:", "", regex=False)
                .str.strip()  # 🔹 Elimina espacios al inicio y al final
            )

        # ===============================
        # 🚀 CARGA A SUPABASE (OPTIMIZADA)
        # ===============================
        if st.button("🚀 Cargar contactos a Supabase"):
            data = df.to_dict(orient="records")
            batch_size = 500  # 🔹 Subir en lotes de 500 filas
            total_rows = len(data)
            success_rows = 0

            progress_bar = st.progress(0)
            status_text = st.empty()

            for i in range(0, total_rows, batch_size):
                batch = data[i:i + batch_size]
                try:
                    response = supabase.table("contactos_promocionales").insert(batch).execute()
                    if response.data is not None:
                        success_rows += len(batch)
                except Exception as e:
                    st.error(f"❌ Error en el lote {i // batch_size + 1}: {e}")
                    continue

                # Actualizar progreso
                progress = min((i + batch_size) / total_rows, 1.0)
                progress_bar.progress(progress)
                status_text.text(f"Lote {i // batch_size + 1} cargado ({success_rows}/{total_rows})")

                # 🔸 Delay corto para evitar throttling
                time.sleep(0.4)

            progress_bar.progress(1.0)
            st.success(f"✅ Carga completada: {success_rows} de {total_rows} filas subidas correctamente.")

    except Exception as e:
        st.error(f"❌ Error al subir los datos: {e}")
