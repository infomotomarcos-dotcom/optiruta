import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import datetime

st.set_page_config(page_title="OptiRuta - Cierre de Caja", page_icon="💰", layout="centered")

API_URL = "https://google.com"
CONTRASEÑA_LOCAL = "1234"

@st.cache_data(ttl=2)
def obtener_datos_pedidos():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data.get("pedidos", []))
            if not df.empty:
                return df
    except:
        pass
    
    # --- DATOS FICTICIOS PARAGUAYOS PARA PRUEBAS ---
    datos_prueba = [
        {"ID": 1, "Cliente": "Novedades Juanita", "Estado": "Entregado", "MontoPedido": 150000, "Envio": 15000, "Total": 165000, "MetodoPago": "Efectivo"},
        {"ID": 2, "Cliente": "Novedades Juanita", "Estado": "Entregado", "MontoPedido": 85000, "Envio": 15000, "Total": 100000, "MetodoPago": "Transferencia"},
        {"ID": 3, "Cliente": "Novedades Juanita", "Estado": "Pendiente", "MontoPedido": 300000, "Envio": 20000, "Total": 320000, "MetodoPago": "Efectivo"},
        {"ID": 4, "Cliente": "Hamburguesería El Bajón", "Estado": "Entregado", "MontoPedido": 45000, "Envio": 10000, "Total": 55000, "MetodoPago": "Efectivo"},
        {"ID": 5, "Cliente": "Hamburguesería El Bajón", "Estado": "Entregado", "MontoPedido": 120000, "Envio": 12000, "Total": 132000, "MetodoPago": "Mixto (Efectivo + Transferencia)"},
        {"ID": 6, "Cliente": "Farmacia San Blas", "Estado": "Entregado", "MontoPedido": 210000, "Envio": 15000, "Total": 225000, "MetodoPago": "Transferencia"},
    ]
    return pd.DataFrame(datos_prueba)

st.markdown("<h1 style='text-align: center; color: #1EBB85;'>💰 Auditoría y Cierre de Caja</h1>", unsafe_allow_html=True)

clave = st.text_input("Introduce la clave del local para auditar:", type="password")
if clave == CONTRASEÑA_LOCAL:
    df_pedidos = obtener_datos_pedidos()
    
    if df_pedidos.empty:
        st.info("No hay pedidos registrados hoy para computar cierres.")
    else:
        # Asegurar columnas desglosadas en el DataFrame
        for col in ["MontoPedido", "Envio", "Total", "Cliente", "Estado", "MetodoPago"]:
            if col not in df_pedidos.columns:
                df_pedidos[col] = 0 if col in ["MontoPedido", "Envio", "Total"] else None

        lista_comercio = sorted(list(df_pedidos["Cliente"].dropna().unique()))
        emp_seleccionado = st.selectbox("Selecciona el Emprendedor / Comercio para cerrar caja:", lista_comercio)
        
        st.markdown(f"## 📊 Resumen Financiero: {emp_seleccionado}")
        df_comercio = df_pedidos[(df_pedidos["Cliente"] == emp_seleccionado) & (df_pedidos["Estado"] == "Entregado")].copy()
        
        if not df_comercio.empty:
            df_comercio["Total"] = df_comercio["Total"].astype(float)
            
            efectivo_total = df_comercio[df_comercio["MetodoPago"].str.contains("Efectivo", na=False)]["Total"].sum()
            transfe_total = df_comercio[df_comercio["MetodoPago"].str.contains("Transferencia", na=False)]["Total"].sum()
            mixto_total = df_comercio[df_comercio["MetodoPago"].str.contains("Mixto", na=False)]["Total"].sum()
            gran_total = df_comercio["Total"].sum()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("💵 Total Efectivo", f"Gs. {int(efectivo_total):,}".replace(",", "."))
            c2.metric("💳 Total Transferencia", f"Gs. {int(transfe_total):,}".replace(",", "."))
            c3.metric("🔀 Total Mixto", f"Gs. {int(mixto_total):,}".replace(",", "."))
            
            st.markdown(f"### **Monto Neto Entregado Hoy:** `Gs. {int(gran_total):,}`".replace(",", "."))
            
            with st.form("f_archivo"):
                notas = st.text_input("Notas u Observaciones del Arqueo")
                btn_enviar = st.form_submit_button("🔒 Archivar Cierre en Historial", use_container_width=True, type="primary")
                if btn_enviar:
                    payload_cierre = {
                        "accion": "cierre_caja",
                        "emprendedor": emp_seleccionado,
                        "total_rendido": gran_total,
                        "observaciones": notas,
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    try:
                        requests.post(API_URL, json=payload_cierre)
                        st.success(f"¡Cierre guardado correctamente para {emp_seleccionado}!")
                        st.cache_data.clear()
                    except:
                        st.error("Error al conectar con Google Sheets.")
        else:
            st.info("Este comercio todavía no cuenta con pedidos con el estado 'Entregado' el día de hoy.")
