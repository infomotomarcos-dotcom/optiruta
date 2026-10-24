import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="OptiRuta Delivery", page_icon="🚀", layout="centered")

API_URL = "https://google.com"
METODOS_PAGO = ["Efectivo", "Transferencia bancaria / Giros", "Mixto (Efectivo + Transferencia)", "Ya pagado / Sin cobro"]
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
    st.markdown("<p style='text-align: center; font-size:18px;'>🇵🇾 Sistema de Control de Repartos (Guaraníes)</p>", unsafe_allow_html=True)
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
            monto = st.number_input("Monto TOTAL neto a cobrar al cliente final (Gs.) - (Pon 0 si ya está pagado) *", min_value=0, step=5000, format="%d")
            pago = st.selectbox("¿Cómo pagará el destinatario al llegar? *", METODOS_PAGO)
            enviar = st.form_submit_button("🚀 Enviar Solicitud de Reparto", use_container_width=True)
            
        if enviar and c_nom and d_dir and detalles:
            payload = {"accion": "crear", "ID": len(df_pedidos)+1, "Cliente": f"{c_nom} ({c_tel})", "Dirección": d_dir, "Pedido": f"Para: {d_nom} - {detalles}", "Total": int(monto), "Repartidor": "Sin Asignar", "Estado": "Pendiente", "Hora": datetime.now().strftime("%H:%M"), "MetodoPago": pago}
            requests.post(API_URL, json=payload)
            st.success("¡Tu solicitud de envío fue registrada con éxito!")
            st.cache_data.clear()
            
    with p_admin:
        st.markdown("### Consola de Administración Central")
        clave = st.text_input("Introduce la clave del local para desbloquear el panel:", type="password")
        
        if clave == CONTRASEÑA_LOCAL:
            st.success("Acceso Autorizado")
            st.markdown("---")
            
            # --- 🏢 SELECCIÓN DE EMPRENDEDOR ---
            st.markdown("### 🔍 Selector de Emprendedor / Comercio")
            lista_emprendedores = ["Todos los Emprendedores"]
            if not df_pedidos.empty and "Cliente" in df_pedidos.columns:
                # Extraer nombres únicos de la columna Cliente
                nombres_unicos = df_pedidos["Cliente"].dropna().unique().tolist()
                lista_emprendedores.extend([str(n) for n in nombres_unicos])
                
            emprendedor_seleccionado = st.selectbox("Filtrar consola por comercio específico:", lista_emprendedores)
            
            # Filtrar el DataFrame de pedidos según la selección
            if emprendedor_seleccionado == "Todos los Emprendedores":
                df_filtrado_local = df_pedidos
            else:
                df_filtrado_local = df_pedidos[df_pedidos["Cliente"] == emprendedor_seleccionado]
                
            st.markdown("---")
            
            # --- 🧮 MODULE DE CIERRE DE CAJA DIARIA FILTRADO ---
            st.markdown(f"### 🧮 Cierre de Caja Diaria ({emprendedor_seleccionado})")
            col_cfg1, col_cfg2 = st.columns(2)
            costo_envio_fijo = col_cfg1.number_input("Establecer pago base por envío al delivery (Gs.):", min_value=0, value=15000, step=1000, format="%d")
            
            if st.button("🔏 Ejecutar Cuadre y Cierre de Caja", use_container_width=True, type="primary"):
                if not df_filtrado_local.empty:
                    df_filtrado_local["Total"] = pd.to_numeric(df_filtrado_local["Total"], errors='coerce').fillna(0).astype(int)
                    df_ok = df_filtrado_local[df_filtrado_local["Estado"] == "Entregado"]
                    
                    total_recaudado = int(df_ok["Total"].sum())
                    transferencias = int(df_ok[df_ok["MetodoPago"].str.contains("Transferencia|Giros", na=False)]["Total"].sum())
                    efectivo = int(df_ok[df_ok["MetodoPago"].str.contains("Efectivo", na=False)]["Total"].sum())
                    
                    cant_envios_ok = len(df_ok)
                    pago_total_deliverys = int(cant_envios_ok * costo_envio_fijo)
                    total_neto_emprendedores = int(total_recaudado - pago_total_deliverys)
                    
                    st.markdown("#### 📝 Reporte de Cierre Consolidado")
                    st.caption(f"Filtro activo: {emprendedor_seleccionado}")
                    st.info(f"📊 **Volumen de Envíos Concluidos:** {cant_envios_ok} entregas.")
                    
                    c_c1, c_c2 = st.columns(2)
                    c_c1.metric("💰 Total Bruto Recaudado", f"Gs. {total_recaudado:,}")
                    c_c1.metric("📱 En Cuenta (Transferencias/Giros)", f"Gs. {transferencias:,}")
                    c_c1.metric("💵 En Mano (Efectivo)", f"Gs. {efectivo:,}")
                    
                    c_c2.metric("🏍️ Nómina Total a Pagar a Deliverys", f"Gs. {pago_total_deliverys:,}", delta=f"-Gs. {costo_envio_fijo:,} c/u", delta_color="inverse")
                    c_c2.metric("🏢 Total Neto a Rendir a Emprendedores", f"Gs. {total_neto_emprendedores:,}")
                    st.toast("Caja cuadrada de forma exitosa.")
                else:
                    st.warning("No hay registros en la selección actual para computar cierres.")
                    
            st.markdown("---")
            
            # --- 📋 LISTADO DE ÓRDENES MONITOREADAS ---
            st.markdown(f"### 📋 Órdenes Monitoreadas ({emprendedor_seleccionado})")
            if df_filtrado_local.empty:
                st.info("No hay movimientos registrados para la selección actual.")
            else:
                for idx, f in df_filtrado_local.iterrows():
                    with st.container():
                        col1, col2, col3 = st.columns()
                        col1.markdown(f"### `#{f['ID']}`\n⏱️ {f['Hora']}")
                        col2.markdown(f"👤 **Cliente:** {f['Cliente']}\n📍 **Destino:** _{f['Dirección']}_\n📦 **Detalles:** {f['Pedido']}")
                        
                        monto_formateado = int(float(f['Total'])) if f['Total'] is not None else 0
                        col3.markdown(f"💰 **Total Cobro:** Gs. {monto_formateado:,} (_{f['MetodoPago']}_)")
                        
                        m_elegida = col3.selectbox(f"Asignar Vehículo a #{f['ID']}:", ["Sin Asignar"] + MOTOS_FIJAS, index=(["Sin Asignar"] + MOTOS_FIJAS).index(f['Repartidor']) if f['Repartidor'] in (["Sin Asignar"] + MOTOS_FIJAS) else 0, key=f"m_{f['ID']}")
