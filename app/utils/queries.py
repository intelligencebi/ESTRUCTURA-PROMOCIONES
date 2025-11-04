from app.utils.supabase_client import supabase

# ============================================
# 📊 Consulta de resumen por promoción
# ============================================
def get_resumen_promocion(promo_name: str):
    try:
        res = supabase.rpc("resumen_por_promocion", {"promo_name": promo_name}).execute()
        return res.data or []
    except Exception as e:
        print(f"Error al obtener resumen_promocion: {e}")
        return []


# ============================================
# 👥 Consulta de seguimiento individual
# ============================================
def get_seguimiento_promocion(promo_name: str, fecha_inicio=None, fecha_fin=None):
    try:
        params = {"promo_name": promo_name}
        if fecha_inicio and fecha_fin:
            params["fecha_inicio"] = fecha_inicio
            params["fecha_fin"] = fecha_fin

        res = supabase.rpc("seguimiento_por_promocion", params).execute()
        return res.data or []
    except Exception as e:
        print(f"Error al obtener seguimiento_promocion: {e}")
        return []
