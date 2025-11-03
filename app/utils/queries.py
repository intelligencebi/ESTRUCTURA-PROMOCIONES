from app.utils.supabase_client import supabase

def get_resumen_promocion(promo_name):
    res = supabase.rpc("resumen_por_promocion", {"promo_name": promo_name}).execute()
    return res.data

def get_seguimiento_promocion(promo_name, fecha_inicio=None, fecha_fin=None):
    params = {"promo_name": promo_name}
    if fecha_inicio and fecha_fin:
        params["fecha_inicio"] = fecha_inicio
        params["fecha_fin"] = fecha_fin
    res = supabase.rpc("seguimiento_por_promocion", params).execute()
    return res.data
