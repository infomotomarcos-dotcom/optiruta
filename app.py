import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="OptiRuta Delivery", page_icon="🚀", layout="centered")

# Variables y Configuración del Sistema
API_URL = "https://google.com"
METODOS_PAGO = ["Efectivo", "Transferencia", "Mixto (Efectivo + Transferencia)", "Ya pagado / Sin cobro"]
MOTOS_FIJAS = ["Moto 1", "Moto 2", "Moto 3"]
CONTRASEÑA_LOCAL = "1234"

@st.cache_data(ttl=2)
def obtener_datos_sistema():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data.get("pedidos", [])), pd.DataFrame(data.get("conductores", [])), pd.DataFrame(data.get("turnos_hoy", []))
    except:
        pass
    # Datos de respaldo (Mock) por si falla la conexión
    df_c_mock = pd.DataFrame([{"Nombre": "Juan Pérez", "Telefono": "595981111111"},{"Nombre": "Carlos Gómez", "Telefono": "595982222222"}])
    df_t_mock = pd.DataFrame([{"Moto": "Moto 1", "Conductor": "Juan Pérez"},{"Moto": "Moto 2", "Conductor": "Carlos Gómez"},{"Moto": "Moto 3", "Conductor": "Sin Asignar"}])
    return pd.DataFrame(), df_c_mock, df_t_mock

# Carga de datos
df_pedidos, df_conductores, df_turnos = obtener_datos_sistema()
CONDUCTORES_DICT = dict(zip(df_conductores["Nombre"].astype(str), df_conductores["Telefono"].astype(str))) if not df_conductores.empty else {}
TURNOS_DICT = dict(zip(df_turnos["Moto"].astype(str), df_turnos["Conductor"].astype(str))) if not df_turnos.empty else {}

columnas_base = ["ID", "Cliente", "Dirección", "Pedido", "Total", "Repartidor", "Estado", "Hora", "MetodoPago"]
for col in columnas_base:
    if df_pedidos.empty or col not in df_pedidos.columns:
        df_pedidos[col] = None

# Asegurar tipos de datos correctos para cálculos numéricos
if not df_pedidos.empty:
    df_pedidos["Total"] = pd.to_numeric(df_pedidos["Total"], errors='coerce').fillna(0.0)

# Control de Navegación (Perfiles)
if "perfil" not in st.session_state:
    st.session_state.perfil = "Inicio"

# ==========================================
# 1. PANTALLA DE INICIO
# ==========================================
if st.session_state.perfil == "Inicio":
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🚀 OptiRuta Delivery</h1>", unsafe_allow_html=True)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🏢 Emprendedores / Clientes", use_container_width=True, type="primary"):
            st.session_state.perfil = "Emprendedores"
            st.rerun()
    with col_btn2:
        if st.button("🏍️ Conductores / Repartidores", use_container_width=True, type="secondary"):
            st.session_state.perfil = "Conductores"
            st.rerun()

# ==========================================
# 2. PERFIL: EMPRENDEDORES / CLIENTES
# ==========================================
elif st.session_state.perfil == "Emprendedores":
    if st.button("⬅️ Volver al Inicio"):
        st.session_state.perfil = "Inicio"
        st.rerun()
    
    p_carga, p_admin = st.tabs(["📥 CARGAR NUEVO ENVÍO", "🔒 ACCESO PRIVADO LOCAL"])
    
    # Pestaña de Carga de Envíos
    with p_carga:
        with st.form("f_cliente", clear_on_submit=True):
            c_nom = st.text_input("Tu Nombre o Comercio *")
            c_tel = st.text_input("Tu Teléfono de Contacto *")
            d_nom = st.text_input("Nombre de quién recibe *")
            d_dir = st.text_input("Dirección Exacta de Entrega *")
            detalles = st.text_area("Contenido del paquete *")
            monto = st.number_input("Monto TOTAL a cobrar ($) *", min_value=0.0, step=1.0)
            pago = st.selectbox("¿Cómo pagará al llegar? *", METODOS_PAGO)
            
            enviar = st.form_submit_button("🚀 Enviar Solicitud", use_container_width=True)
        
        if enviar and c_nom and d_dir and detalles:
            payload = {"accion": "crear", "ID": len(df_pedidos)+1, "Cliente": f"{c_nom} ({c_tel})", "Dirección": d_dir, "Pedido": f"Para: {d_nom} - {detalles}", "Total": monto, "Repartidor": "Sin Asignar", "Estado": "Pendiente", "Hora": datetime.now().strftime("%H:%M"), "MetodoPago": pago}
            requests.post(API_URL, json=payload)
            st.success("¡Envío registrado con éxito!")
            st.cache_data.clear()
            
        st.markdown("---")
        st.link_button("💬 ¿Problemas con tu carga? Contactar Soporte", "https://wa.me", use_container_width=True)

    # Pestaña de Administración Local
    with p_admin:
        clave = st.text_input("Introduce la clave del local:", type="password")
        if clave == CONTRASEÑA_LOCAL:
            
            if st.button("🔄 Sincronizar y Refrescar Pedidos", use_container_width=True, type="primary"):
                st.cache_data.clear()
                st.toast("¡Datos sincronizados!", icon="🔄")
                st.rerun()
            
            # ----------------------------------------------------
            # NUEVA SECCIÓN SELECCIONABLE: ARQUEO DE CAJA RENDICIÓN
            # ----------------------------------------------------
            st.markdown("### 📊 Módulo de Arqueo y Rendición de Caja")
            
            # Filtrar solo pedidos efectivamente completados para rendir dinero real
            df_entregados = df_pedidos[df_pedidos["Estado"] == "Entregado"] if not df_pedidos.empty else pd.DataFrame()
            
            if not df_entregados.empty:
                lista_emprendedores = sorted(list(df_entregados["Cliente"].dropna().unique()))
                emp_seleccionado = st.selectbox("Selecciona Emprendedor para calcular liquidación:", ["Elegir Comercio..."] + lista_emprendedores)
                
                col_costo1, col_costo2 = st.columns(2)
                with col_costo1:
                    costo_delivery = st.number_input("Costo del Delivery por Envío ($):", min_value=0.0, value=15000.0, step=500.0)
                with col_costo2:
                    st.write("") # Espaciador cosmético
                    st.write("")
                    ejecutar_arqueo = st.button("🧮 Generar Listado de Totales a Rendir", use_container_width=True, type="primary")
                
                if emp_seleccionado != "Elegir Comercio..." and ejecutar_arqueo:
                    # Datos específicos del emprendedor seleccionado
                    df_filtrado_emp = df_entregados[df_entregados["Cliente"] == emp_seleccionado]
                    
                    total_cobrado_bruto = df_filtrado_emp["Total"].sum()
                    total_pedidos_entregados = len(df_filtrado_emp)
                    pago_total_deliverys = total_pedidos_entregados * costo_delivery
                    neto_para_emprendedor = total_cobrado_bruto - pago_total_deliverys
                    
                    # Desglose por método de pago para control de flujo
                    efectivo = df_filtrado_emp[df_filtrado_emp["MetodoPago"].str.contains("Efectivo", na=False, case=False)]["Total"].sum()
                    transferencia = df_filtrado_emp[df_filtrado_emp["MetodoPago"].str.contains("Transferencia", na=False, case=False)]["Total"].sum()
                    mixto = df_filtrado_emp[df_filtrado_emp["MetodoPago"].str.contains("Mixto", na=False, case=False)]["Total"].sum()
                    
                    st.info(f"📋 **Resumen de Cuentas para:** {emp_seleccionado}")
                    
                    # Métricas clave en cuadros destacados
                    m1, m2, m3 = st.columns(3)
                    m1.metric(label="Total Recaudado en Calle", value=f"${total_cobrado_bruto:,.0f}")
                    m2.metric(label="Descuento Total Deliverys", value=f"- ${pago_total_deliverys:,.0f}")
                    m3.metric(label="Total Neto a Rendir al Cliente", value=f"${neto_para_emprendedor:,.0f}")
                    
                    # Desglose informativo del dinero
                    st.markdown(f"""
                    **🔎 Desglose de Canales de Cobro Realizados por las Motos:**
                    *   **Total Envíos Entregados:** {total_pedidos_entregados} viajes efectuados.
                    *   **Monto capturado por Efectivo Puro:** ${efectivo:,.0f}
                    *   **Monto capturado por Transferencias:** ${transferencia:,.0f}
                    *   **Monto capturado por Cobros Mixtos:** ${mixto:,.0f}
                    
                    ⚠️ *Nota: El cálculo resta de manera matemática el total retenido para fletes al fondo bruto recolectado antes de liberar la ganancia comercial del emprendedor.*
                    """)
            else:
                st.write("ℹ️ No hay pedidos registrados con el estado 'Entregado' el día de hoy para realizar arqueos.")
            
            st.markdown("---")
            st.markdown("### 📦 Lista General de Órdenes del Día")
            
            for idx, f in df_pedidos.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([1, 2, 1.5])
                    col1.markdown(f"### `#{f['ID']}`\n⏱️ {f['Hora']}")
                    col2.markdown(f"👤 **{f['Cliente']}**\n📍 {f['Dirección']}\n📦 {f['Pedido']}\n💰 *Monto:* ${f['Total']} ({f['MetodoPago']})")
                    
                    m_elegida = col3.selectbox(f"Vehículo:", ["Sin Asignar"] + MOTOS_FIJAS, index=(["Sin Asignar"] + MOTOS_FIJAS).index(f['Repartidor']) if f['Repartidor'] in (["Sin Asignar"] + MOTOS_FIJAS) else 0, key=f"m_{f['ID']}")
                    e_elegido = col3.selectbox(f"Estado:", ["Pendiente", "En Ruta", "Entregado", "Cancelado"], index=["Pendiente", "En Ruta", "Entregado", "Cancelado"].index(f['Estado']) if f['Estado'] in ["Pendiente", "En Ruta", "Entregado", "Cancelado"] else 0, key=f"e_{f['ID']}")
