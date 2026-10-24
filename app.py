import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="OptiRuta Delivery", page_icon="🚀", layout="centered")

API_URL = "https://google.com"
METODOS_PAGO = ["Efectivo", "Transferencia", "Mixto (Efectivo + Transferencia)", "Ya pagado / Sin cobro"]
MOTOS_FIJAS = ["Moto 1", "Moto 2", "Moto 3"]
CONTRASEÑA_LOCAL = "1234" # <<-- CAMBIA AQUÍ TU CONTRASEÑA PRIVADA DEL LOCAL

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

# --- INICIALIZACIÓN DEL PERFIL DE USUARIO ---
if "perfil" not in st.session_state:
    st.session_state.perfil = "Inicio"

# =========================================================
# PANTALLA DE INICIO LIMPIA (BIENVENIDA)
# =========================================================
if st.session_state.perfil == "Inicio":
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🚀 OptiRuta Delivery</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size:18px;'>Bienvenido al Centro de Control de Repartos</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Selecciona tu perfil de acceso para continuar:</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🏢 Emprendedores / Clientes", use_container_width=True, type="primary"):
            st.session_state.perfil = "Emprendedores"
            st.rerun()
            
    with col_btn2:
        if st.button("🏍️ Conductores / Repartidores", use_container_width=True, type="secondary"):
            st.session_state.perfil = "Conductores"
            st.rerun()

# =========================================================
# VISTA: EMPRENDEDORES Y LOCAL
# =========================================================
elif st.session_state.perfil == "Emprendedores":
    if st.button("⬅️ Volver al Inicio"):
        st.session_state.perfil = "Inicio"
        st.rerun()
        
    st.markdown("<h2 style='color: #FF4B4B;'>🏢 Panel de Emprendedores y Clientes</h2>", unsafe_allow_html=True)
    
    p_carga, p_admin = st.tabs(["📥 CARGAR NUEVO ENVÍO", "🔒 ACCESO PRIVADO LOCAL"])
    
    with p_carga:
        with st.form("f_cliente", clear_on_submit=True):
            c_nom = st.text_input("Tu Nombre o Comercio *")
            c_tel = st.text_input("Tu Teléfono de Contacto *")
            d_nom = st.text_input("Nombre de quién recibe el paquete *")
            d_dir = st.text_input("Dirección Exacta de Entrega *")
            detalles = st.text_area("Contenido o descripción del paquete *")
            monto = st.number_input("Monto TOTAL neto a cobrar al cliente final ($) - (Pon 0 si ya está pagado) *", min_value=0.0, step=1.0)
            pago = st.selectbox("¿Cómo pagará el destinatario al llegar? *", METODOS_PAGO)
            enviar = st.form_submit_button("🚀 Enviar Solicitud de Reparto", use_container_width=True)
            
        if enviar and c_nom and d_dir and detalles:
            payload = {"accion": "crear", "ID": len(df_pedidos)+1, "Cliente": f"{c_nom} ({c_tel})", "Dirección": d_dir, "Pedido": f"Para: {d_nom} - {detalles}", "Total": monto, "Repartidor": "Sin Asignar", "Estado": "Pendiente", "Hora": datetime.now().strftime("%H:%M"), "MetodoPago": pago}
            requests.post(API_URL, json=payload)
            st.success("¡Tu solicitud de envío fue registrada con éxito!")
            st.cache_data.clear()
            
    with p_admin:
        st.markdown("### Consola de Administración Central")
        clave = st.text_input("Introduce la clave del local para desbloquear el panel:", type="password")
        
        if clave == CONTRASEÑA_LOCAL:
            st.success("Acceso Autorizado")
            st.markdown("---")
            if df_pedidos.empty:
                st.info("No hay movimientos registrados hoy.")
            else:
                for idx, f in df_pedidos.iterrows():
                    with st.container():
                        col1, col2, col3 = st.columns([1, 2, 2])
                        col1.markdown(f"### `#{f['ID']}`\n⏱️ {f['Hora']}")
                        col2.markdown(f"👤 **Cliente:** {f['Cliente']}\n📍 **Destino:** {f['Dirección']}\n📦 {f['Pedido']}")
                        col3.markdown(f"💰 **Total Cobro:** ${f['Total']} (_{f['MetodoPago']}_)")
                        
                        m_elegida = col3.selectbox(f"Asignar Vehículo a #{f['ID']}:", ["Sin Asignar"] + MOTOS_FIJAS, index=(["Sin Asignar"] + MOTOS_FIJAS).index(f['Repartidor']) if f['Repartidor'] in (["Sin Asignar"] + MOTOS_FIJAS) else 0, key=f"m_{f['ID']}")
                        e_elegido = col3.selectbox(f"Estado de Ruta a #{f['ID']}:", ["Pendiente", "En Ruta", "Entregado", "Cancelado"], index=["Pendiente", "En Ruta", "Entregado", "Cancelado"].index(f['Estado']) if f['Estado'] in ["Pendiente", "En Ruta", "Entregado", "Cancelado"] else 0, key=f"e_{f['ID']}")
                        
                        if m_elegida != f['Repartidor'] or e_elegido != f['Estado']:
                            requests.post(API_URL, json={"accion": "actualizar_completo", "id": f['ID'], "repartidor": m_elegida, "estado": e_elegido})
                            st.cache_data.clear()
                            st.rerun()
                        
                        txt_wa = f"*🚀 OPTIRUTA DELIVERY*\n📦 *Orden:* #{f['ID']}\n📍 *Destino:* {f['Dirección']}\n📝 *Detalles:* {f['Pedido']}\n💰 *Monto a Cobrar:* ${f['Total']} ({f['MetodoPago']})"
                        num_destino = CONDUCTORES_DICT.get(TURNOS_DICT.get(m_elegida, ""), "")
                        if num_destino:
                            col3.link_button("📲 Despachar por WhatsApp", f"https://wa.me{num_destino}?text={urllib.parse.quote(txt_wa)}", use_container_width=True, type="primary")
                        st.markdown("---")
                        
                st.markdown("### ⚙️ Control de Turnos Diarios")
                col_fl1, col_fl2 = st.columns(2)
                with col_fl1:
                    st.markdown("**Asignación de Motos**")
                    with st.form("f_turnos"):
                        nuevos = {}
                        for m in MOTOS_FIJAS:
                            nuevos[m] = st.selectbox(f"¿Quién maneja la {m} hoy?", ["Seleccionar..."] + list(CONDUCTORES_DICT.keys()), index=(["Seleccionar..."] + list(CONDUCTORES_DICT.keys())).index(TURNOS_DICT.get(m, "Seleccionar...")) if TURNOS_DICT.get(m, "Seleccionar...") in (["Seleccionar..."] + list(CONDUCTORES_DICT.keys())) else 0)
                        if st.form_submit_button("🔒 Guardar Turnos de Hoy", use_container_width=True):
                            requests.post(API_URL, json={"accion": "guardar_turnos", "turnos": nuevos})
                            st.cache_data.clear()
                            st.rerun()
                with col_fl2:
                    st.markdown("**Registrar Nuevo Chofer**")
                    with st.form("f_chofer", clear_on_submit=True):
                        n_nom = st.text_input("Nombre Completo")
                        n_tel = st.text_input("WhatsApp (ej: 549...)")
                        if st.form_submit_button("Agregar Chofer"):
                            requests.post(API_URL, json={"accion": "crear_conductor", "Nombre": n_nom, "Telefono": n_tel})
                            st.cache_data.clear()
                            st.rerun()
        elif clave != "":
            st.error("Clave incorrecta. Acceso denegado.")

# =========================================================
# VISTA: CONDUCTORES (Máxima privacidad de costos)
# =========================================================
elif st.session_state.perfil == "Conductores":
    if st.button("⬅️ Volver al Inicio"):
        st.session_state.perfil = "Inicio"
        st.rerun()
        
    st.markdown("<h2 style='color: #10B981;'>🏍️ Acceso de Conductores</h2>", unsafe_allow_html=True)
    chofer = st.selectbox("Selecciona tu nombre de Conductor:", ["Seleccionar..."] + list(CONDUCTORES_DICT.keys()))
    
    if chofer != "Seleccionar...":
        m_hoy = [m for m, c in TURNOS_DICT.items() if c == chofer]
        if not m_hoy:
            st.warning("⚠️ No tienes ninguna moto asignada el día de hoy. Solicita tu asignación en la base.")
        else:
            moto_str = m_hoy if isinstance(m_hoy, list) else m_hoy
            df_m = df_pedidos[(df_pedidos["Repartidor"] == moto_str) & (df_pedidos["Estado"].isin(["Pendiente", "En Ruta"]))]
