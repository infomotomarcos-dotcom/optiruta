import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import datetime

st.set_page_config(page_title="OptiRuta Delivery", page_icon="🚀", layout="wide")

API_URL = "https://google.com"
METODOS_PAGO = ["Efectivo", "Transferencia", "Mixto (Efectivo + Transferencia)", "Ya pagado / Sin cobro"]
MOTOS_FIJAS = ["Moto 1", "Moto 2", "Moto 3"]

@st.cache_data(ttl=2)
def obtener_datos_sistema():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data.get("pedidos", [])), pd.DataFrame(data.get("conductores", [])), pd.DataFrame(data.get("turnos_hoy", []))
    except:
        pass
    df_c_mock = pd.DataFrame([{"Nombre": "Juan Pérez", "Telefono": "595981111111"},{"Nombre": "Carlos Gómez", "Telefono": "595982222222"}])
    df_t_mock = pd.DataFrame([{"Moto": "Moto 1", "Conductor": "Juan Pérez"},{"Moto": "Moto 2", "Conductor": "Carlos Gómez"},{"Moto": "Moto 3", "Conductor": "Sin Asignar"}])
    return pd.DataFrame(), df_c_mock, df_t_mock

df_pedidos, df_conductores, df_turnos = obtener_datos_sistema()
CONDUCTORES_DICT = dict(zip(df_conductores["Nombre"].astype(str), df_conductores["Telefono"].astype(str))) if not df_conductores.empty else {}
TURNOS_DICT = dict(zip(df_turnos["Moto"].astype(str), df_turnos["Conductor"].astype(str))) if not df_turnos.empty else {}

columnas_base = ["ID", "Cliente", "Dirección", "Pedido", "Total", "Repartidor", "Estado", "Hora", "MetodoPago"]
for col in columnas_base:
    if df_pedidos.empty or col not in df_pedidos.columns:
        df_pedidos[col] = None

p_cliente, p_moto, p_local, p_flota = st.tabs(["📦 PORTAL CLIENTES", "🏍️ ACCESO REPARTIDORES", "🏢 CONTROL CENTRAL", "⚙️ TURNOS Y FLOTA"])

# 1. PORTAL DE CLIENTES
with p_cliente:
    st.markdown("### Formulario de Envío - OptiRuta")
    with st.form("f_cliente", clear_on_submit=True):
        c_nom = st.text_input("Tu Nombre / Negocio *")
        c_tel = st.text_input("Tu Teléfono *")
        d_nom = st.text_input("Quién recibe el paquete *")
        d_dir = st.text_input("Dirección de Entrega *")
        detalles = st.text_area("Contenido o descripción del paquete *")
        
        st.markdown("---")
        st.markdown("##### 💰 Información de Cobro")
        monto = st.number_input("Monto TOTAL neto a cobrar al cliente final ($) - Escribe 0 si ya está pagado *", min_value=0.0, step=1.0)
        pago = st.selectbox("¿Cómo pagará el destinatario al llegar? *", METODOS_PAGO)
        enviar = st.form_submit_button("🚀 Solicitar Envío", use_container_width=True)
        
    if enviar and c_nom and d_dir and detalles:
        payload = {
            "accion": "crear", 
            "ID": len(df_pedidos)+1, 
            "Cliente": f"{c_nom} ({c_tel})", 
            "Dirección": d_dir, 
            "Pedido": f"Para: {d_nom} - {detalles}", 
            "Total": monto, 
            "Repartidor": "Sin Asignar", 
            "Estado": "Pendiente", 
            "Hora": datetime.now().strftime("%H:%M"), 
            "MetodoPago": pago
        }
        requests.post(API_URL, json=payload)
        st.success("¡Envío registrado con éxito! Procesaremos tu paquete pronto.")
        st.cache_data.clear()

# 2. VISTA REPARTIDORES (PRIVACIDAD: Oculta costos individuales y desgloses)
with p_moto:
    st.markdown("### 🏍️ Mis Entregas del Día")
    chofer = st.selectbox("Selecciona tu nombre:", ["Seleccionar..."] + list(CONDUCTORES_DICT.keys()))
    if chofer != "Seleccionar...":
        m_hoy = [m for m, c in TURNOS_DICT.items() if c == chofer]
        if not m_hoy:
            st.warning("No tienes ninguna moto asignada el día de hoy.")
        else:
            # Filtrar los pedidos asignados a su moto en estado Pendiente o En Ruta
            # Evitar error si m_hoy es una lista tomando el primer elemento str
            moto_str = m_hoy[0] if isinstance(m_hoy, list) else m_hoy
            df_m = df_pedidos[(df_pedidos["Repartidor"] == moto_str) & (df_pedidos["Estado"].isin(["Pendiente", "En Ruta"]))]
            
            if df_m.empty:
                st.success("¡Excelente! No tienes entregas pendientes de cobro.")
            else:
                for idx, f in df_m.iterrows():
                    with st.container():
                        st.markdown(f"#### 📍 Orden #{f['ID']} — Estado: `{f['Estado']}`")
                        st.markdown(f"**Dirección de Entrega:** {f['Dirección']}")
                        st.markdown(f"**Detalles del Paquete:** {f['Pedido']}")
                        st.markdown(f"💵 **TOTAL A COBRAR EN DESTINO:** `${f['Total']}` (Forma de pago requerida: *{f['MetodoPago']}*)")
                        
                        # Selector para que el conductor confirme cómo le pagaron realmente
                        pago_real = st.selectbox(f"Confirmar método recibido para la Orden #{f['ID']}:", METODOS_PAGO, index=METODOS_PAGO.index(f['MetodoPago']) if f['MetodoPago'] in METODOS_PAGO else 0, key=f"moto_pago_{f['ID']}")
                        
                        if st.button(f"✅ Confirmar Entrega y Rendición #{f['ID']}", use_container_width=True, key=f"btn_moto_{f['ID']}"):
                            requests.post(API_URL, json={"accion": "actualizar_entrega_moto", "id": f['ID'], "estado": "Entregado", "metodo_real": pago_real})
                            st.toast(f"¡Orden #{f['ID']} entregada y reportada al local!")
                            st.cache_data.clear()
                            st.rerun()
                        st.markdown("<hr style='border-top: 1px dotted #10B981;'>", unsafe_allow_html=True)

# 3. PANEL DEL LOCAL (Muestra todo el balance consolidado)
with p_local:
    st.markdown("### 🏢 Consola de Despacho Central")
    if df_pedidos.empty:
        st.info("No hay movimientos o pedidos registrados por los clientes hoy.")
    else:
        for idx, f in df_pedidos.iterrows():
            with st.container():
                col1, col2, col3 = st.columns()
                col1.markdown(f"### `#{f['ID']}`\n⏱️ {f['Hora']}")
                col2.markdown(f"👤 **Remitente:** {f['Cliente']}\n📍 **Destino:** {f['Dirección']}\n📦 **Detalles:** {f['Pedido']}")
                
                col3.markdown(f"💰 **Total Cobro:** ${f['Total']} (_{f['MetodoPago']}_)")
                m_elegida = col3.selectbox(f"Asignar Vehículo:", ["Sin Asignar"] + MOTOS_FIJAS, index=(["Sin Asignar"] + MOTOS_FIJAS).index(f['Repartidor']) if f['Repartidor'] in (["Sin Asignar"] + MOTOS_FIJAS) else 0, key=f"m_{f['ID']}")
                e_elegido = col3.selectbox(f"Estado de Ruta:", ["Pendiente", "En Ruta", "Entregado", "Cancelado"], index=["Pendiente", "En Ruta", "Entregado", "Cancelado"].index(f['Estado']) if f['Estado'] in ["Pendiente", "En Ruta", "Entregado", "Cancelado"] else 0, key=f"e_{f['ID']}")
                
                if m_elegida != f['Repartidor'] or e_elegido != f['Estado']:
                    requests.post(API_URL, json={"accion": "actualizar_completo", "id": f['ID'], "repartidor": m_elegida, "estado": e_elegido})
                    st.cache_data.clear()
                    st.rerun()
                
                txt_wa = f"*🚀 OPTIRUTA DELIVERY*\n📦 *Orden:* #{f['ID']}\n📍 *Destino:* {f['Dirección']}\n📝 *Detalles:* {f['Pedido']}\n💰 *Monto a Cobrar:* ${f['Total']} ({f['MetodoPago']})"
                num_destino = CONDUCTORES_DICT.get(TURNOS_DICT.get(m_elegida, ""), "")
                if num_destino:
                    col3.link_button("📲 Despachar por WhatsApp", f"https://wa.me{num_destino}?text={urllib.parse.quote(txt_wa)}", use_container_width=True, type="primary")
                st.markdown("---")

# 4. GESTIÓN DE TURNOS Y FLOTA
with p_flota:
    st.markdown("### ⚙️ Control de Turnos y Choferes")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Turnos de Hoy**")
        with st.form("f_turnos"):
            nuevos = {}
            for m in MOTOS_FIJAS:
                nuevos[m] = st.selectbox(f"¿Quién maneja la {m}?", ["Seleccionar..."] + list(CONDUCTORES_DICT.keys()), index=(["Seleccionar..."] + list(CONDUCTORES_DICT.keys())).index(TURNOS_DICT.get(m, "Seleccionar...")) if TURNOS_DICT.get(m, "Seleccionar...") in (["Seleccionar..."] + list(CONDUCTORES_DICT.keys())) else 0)
            if st.form_submit_button("🔒 Guardar Turnos", use_container_width=True):
                requests.post(API_URL, json={"accion": "guardar_turnos", "turnos": nuevos})
                st.cache_data.clear()
                st.rerun()
    with col2:
        st.markdown("**Registrar Conductor**")
        with st.form("f_chofer", clear_on_submit=True):
            n_nom = st.text_input("Nombre Completo")
            n_tel = st.text_input("WhatsApp (ej: 549...)")
            if st.form_submit_button("Agregar Chofer"):
                requests.post(API_URL, json={"accion": "crear_conductor", "Nombre": n_nom, "Telefono": n_tel})
                st.cache_data.clear()
                st.rerun()
