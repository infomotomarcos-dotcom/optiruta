import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="OptiRuta Delivery", page_icon="🚀", layout="centered")

API_URL = "https://google.com" # <-- Cambia esto por tu endpoint real o URL de Webhook
METODOS_PAGO = ["Efectivo", "Transferencia", "Mixto (Efectivo + Transferencia)", "Ya pagado / Sin cobro"]
MOTOS_FIJAS = ["Moto 1", "Moto 2", "Moto 3"]
CONTRASEÑA_LOCAL = "1234" # <-- Cambia aquí tu contraseña privada del local

# Columnas requeridas para el correcto funcionamiento del DataFrame de pedidos
COLUMNAS_BASE = ["ID", "Cliente", "Dirección", "Pedido", "Total", "Repartidor", "Estado", "Hora", "MetodoPago"]

@st.cache_data(ttl=2)
def obtener_datos_sistema():
    # Inicializamos estructuras vacías por defecto con sus columnas correspondientes
    df_p = pd.DataFrame(columns=COLUMNAS_BASE)
    df_c = pd.DataFrame(columns=["Nombre", "Telefono"])
    df_t = pd.DataFrame(columns=["Moto", "Conductor"])
    
    try:
        response = requests.get(API_URL, timeout=3)
        if response.status_code == 200:
            data = response.json()
            if "pedidos" in data: df_p = pd.DataFrame(data["pedidos"])
            if "conductores" in data: df_c = pd.DataFrame(data["conductores"])
            if "turnos_hoy" in data: df_t = pd.DataFrame(data["turnos_hoy"])
            return df_p, df_c, df_t
    except:
        pass # Si falla la API, cargamos de forma segura los datos de prueba de abajo
        
    # Datos Mock/Prueba en caso de error de conexión con la API
    df_c_mock = pd.DataFrame([
        {"Nombre": "Juan Pérez", "Telefono": "595981111111"},
        {"Nombre": "Carlos Gómez", "Telefono": "595982222222"}
    ])
    df_t_mock = pd.DataFrame([
        {"Moto": "Moto 1", "Conductor": "Juan Pérez"},
        {"Moto": "Moto 2", "Conductor": "Carlos Gómez"},
        {"Moto": "Moto 3", "Conductor": "Sin Asignar"}
    ])
    return df_p, df_c_mock, df_t_mock

# --- CARGA E INICIALIZACIÓN DE DATOS ---
df_pedidos, df_conductores, df_turnos = obtener_datos_sistema()

# Garantizar que todas las columnas existan siempre para evitar KeyErrors
for col in COLUMNAS_BASE:
    if col not in df_pedidos.columns:
        df_pedidos[col] = None

CONDUCTORES_DICT = dict(zip(df_conductores["Nombre"].astype(str), df_conductores["Telefono"].astype(str))) if not df_conductores.empty else {}
TURNOS_DICT = dict(zip(df_turnos["Moto"].astype(str), df_turnos["Conductor"].astype(str))) if not df_turnos.empty else {}

# --- INICIALIZACIÓN DEL PERFIL DE USUARIO ---
if "perfil" not in st.session_state:
    st.session_state.perfil = "Inicio"

# =========================================================
# PANTALLA DE INICIO (BIENVENIDA)
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
            payload = {
                "accion": "crear", 
                "ID": len(df_pedidos) + 1, 
                "Cliente": f"{c_nom} ({c_tel})", 
                "Dirección": d_dir, 
                "Pedido": f"Para: {d_nom} - {detalles}", 
                "Total": monto, 
                "Repartidor": "Sin Asignar", 
                "Estado": "Pendiente", 
                "Hora": datetime.now().strftime("%H:%M"), 
                "MetodoPago": pago
            }
            try:
                requests.post(API_URL, json=payload, timeout=3)
                st.success("¡Tu solicitud de envío fue registrada con éxito!")
                st.cache_data.clear()
            except:
                st.error("No se pudo conectar con el servidor para registrar el pedido.")
            
    with p_admin:
        st.markdown("### Consola de Administración Central")
        clave = st.text_input("Introduce la clave del local para desbloquear el panel:", type="password")
        
        if clave == CONTRASEÑA_LOCAL:
            st.success("Acceso Autorizado")
            st.markdown("---")
            
            df_filtrado = df_pedidos.dropna(subset=["ID"])
            
            if df_filtrado.empty:
                st.info("No hay movimientos registrados hoy.")
            else:
                with st.form("panel_control_pedidos"):
                    cambios_pedidos = []
                    
                    for idx, f in df_filtrado.iterrows():
                        with st.container():
                            col1, col2, col3 = st.columns()
                            col1.markdown(f"### `#{int(f['ID'])}`\n⏱️ {f['Hora']}")
                            col2.markdown(f"👤 **Cliente:** {f['Cliente']}\n📍 **Destino:** {f['Dirección']}\n📦 {f['Pedido']}")
                            col3.markdown(f"💰 **Total Cobro:** ${f['Total']} (_{f['MetodoPago']}_)")
                            
                            idx_moto = (["Sin Asignar"] + MOTOS_FIJAS).index(f['Repartidor']) if f['Repartidor'] in (["Sin Asignar"] + MOTOS_FIJAS) else 0
                            idx_estado = ["Pendiente", "En Ruta", "Entregado", "Cancelado"].index(f['Estado']) if f['Estado'] in ["Pendiente", "En Ruta", "Entregado", "Cancelado"] else 0
                            
                            m_elegida = col3.selectbox(f"Asignar Vehículo a #{int(f['ID'])}:", ["Sin Asignar"] + MOTOS_FIJAS, index=idx_moto, key=f"m_{f['ID']}")
                            e_elegido = col3.selectbox(f"Estado de Ruta a #{int(f['ID'])}:", ["Pendiente", "En Ruta", "Entregado", "Cancelado"], index=idx_estado, key=f"e_{f['ID']}")
                            
                            cambios_pedidos.append({
                                "id": f['ID'], 
                                "repartidor": m_elegida, 
                                "estado": e_elegido, 
                                "original_m": f['Repartidor'], 
                                "original_e": f['Estado']
                            })
                            
                            txt_wa = f"*🚀 OPTIRUTA DELIVERY*\n📦 *Orden:* #{int(f['ID'])}\n📍 *Destino:* {f['Dirección']}\n📝 *Detalles:* {f['Pedido']}\n💰 *Monto a Cobrar:* ${f['Total']} ({f['MetodoPago']})"
                            num_destino = CONDUCTORES_DICT.get(TURNOS_DICT.get(m_elegida, ""), "")
                            if num_destino:
                                # Aquí puedes ver la barra corregida para WhatsApp:
                                col3.link_button("📲 Despachar por WhatsApp", f"https://wa.me{num_destino}?text={urllib.parse.quote(txt_wa)}", use_container_width=True, type="primary")
                            st.markdown("---")
                    
                    if st.form_submit_button("💾 Actualizar Todos los Estados / Motos", use_container_width=True):
                        hubo_cambios = False
                        for c in cambios_pedidos:
                            if c["repartidor"] != c["original_m"] or c["estado"] != c["original_e"]:
                                try:
                                    requests.post(API_URL, json={"accion": "actualizar_completo", "id": c["id"], "repartidor": c["repartidor"], "estado": c["estado"]}, timeout=3)
                                    hubo_cambios = True
                                except:
                                    pass 
                        if hubo_cambios:
                            st.cache_data.clear()
                            st.rerun()
                        
                # --- CONTROL DE TURNOS DIARIOS ---
                st.markdown("### ⚙️ Control de Turnos Diarios")
                col_fl1, col_fl2 = st.columns(2)
                with col_fl1:
                    st.markdown("**Asignación de Motos**")
