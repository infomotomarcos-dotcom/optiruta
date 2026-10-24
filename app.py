import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
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
            df_p = pd.DataFrame(data.get("pedidos", []))
            df_c = pd.DataFrame(data.get("conductores", []))
            df_t = pd.DataFrame(data.get("turnos_hoy", []))
            return df_p, df_c, df_t
    except:
        pass
    
    df_c_mock = pd.DataFrame([
        {"Nombre": "Juan Pérez", "Telefono": "595981111111"},
        {"Nombre": "Carlos Gómez", "Telefono": "595982222222"},
        {"Nombre": "Luis Rodríguez", "Telefono": "595983333333"}
    ])
    df_t_mock = pd.DataFrame([
        {"Moto": "Moto 1", "Conductor": "Juan Pérez"},
        {"Moto": "Moto 2", "Conductor": "Carlos Gómez"},
        {"Moto": "Moto 3", "Conductor": "Luis Rodríguez"}
    ])
    return pd.DataFrame(), df_c_mock, df_t_mock

df_pedidos, df_conductores, df_turnos = obtener_datos_sistema()

CONDUCTORES_DICT = dict(zip(df_conductores["Nombre"].astype(str), df_conductores["Telefono"].astype(str))) if not df_conductores.empty else {}
TURNOS_DICT = dict(zip(df_turnos["Moto"].astype(str), df_turnos["Conductor"].astype(str))) if not df_turnos.empty else {}

columnas_base = ["ID", "Cliente", "Dirección", "Pedido", "Total", "Repartidor", "Estado", "Hora", "MetodoPago"]
for col in columnas_base:
    if df_pedidos.empty or col not in df_pedidos.columns:
        df_pedidos[col] = None

pestana_cliente, pestana_moto, pestana_local, pestana_flota = st.tabs([
    "📦 PORTAL CLIENTES", 
    "🏍️ ACCESO REPARTIDORES", 
    "🏢 CONTROL CENTRAL",
    "⚙️ CONTROL DE TURNOS Y FLOTA"
])

# 1. PORTAL DE CLIENTES
with pestana_cliente:
    st.markdown("<h2 style='color: #FF4B4B; text-align: center;'>Formulario de Envío - OptiRuta</h2>", unsafe_allow_html=True)
    with st.form("formulario_cliente_directo", clear_on_submit=True):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            cliente_nombre = st.text_input("Tu Nombre / Negocio *")
            cliente_telefono = st.text_input("Tu Teléfono *")
        with col_c2:
            destinatario_nombre = st.text_input("Quién recibe el paquete *")
            direccion_entrega = st.text_input("Dirección de Entrega *")
            
        detalles_paquete = st.text_area("¿Qué contiene el paquete? *")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            monto_cobro = st.number_input("Monto a cobrar en destino ($)", min_value=0.0, step=1.0)
        with col_p2:
            pago_esperado = st.selectbox("¿Cómo pagará el destinatario al llegar? *", METODOS_PAGO)
        
        boton_cliente = st.form_submit_button("🚀 Solicitar Envío", use_container_width=True)
        
    if boton_cliente and cliente_nombre and direccion_entrega and detalles_paquete:
        hora_solicitud = datetime.now().strftime("%H:%M")
        nuevo_id = len(df_pedidos) + 1 if not df_pedidos.empty else 1
        payload = {
            "accion": "crear", "ID": nuevo_id, 
            "Cliente": f"{cliente_nombre} (Tel: {cliente_telefono})",
            "Dirección": direccion_entrega, "Pedido": f"Para: {destinatario_nombre} - {detalles_paquete}",
            "Total": monto_cobro, "Repartidor": "Sin Asignar", "Estado": "Pendiente", "Hora": hora_solicitud,
            "MetodoPago": pago_esperado
        }
        requests.post(API_URL, json=payload)
        st.success("¡Envío registrado!")
        st.cache_data.clear()

# 2. VISTA REPARTIDORES
with pestana_moto:
    st.markdown("<h2 style='color: #10B981;'>🏍️ Mis Entregas del Día</h2>", unsafe_allow_html=True)
    chofer_identidad = st.selectbox("Selecciona tu nombre de Conductor:", ["Seleccionar..."] + list(CONDUCTORES_DICT.keys()))
    
    if chofer_identidad != "Seleccionar...":
        moto_asignada_hoy = [moto for moto, chofer in TURNOS_DICT.items() if chofer == chofer_identidad]
        
        if not moto_asignada_hoy:
            st.warning("⚠️ No tienes ninguna moto asignada el día de hoy.")
        else:
            mi_moto = moto_asignada_hoy[0]
            st.info(f"📋 Conductor: **{chofer_identidad}** | Vehículo Asignado Hoy: **{mi_moto}**")
            
            df_moto_filtrado = df_pedidos[(df_pedidos["Repartidor"] == mi_moto) & (df_pedidos["Estado"].isin(["Pendiente", "En Ruta"]))]
            
            if df_moto_filtrado.empty:
                st.success("¡Felicidades! No tienes entregas pendientes.")
            else:
                for index, fila in df_moto_filtrado.iterrows():
                    id_p = fila.get("ID")
                    dom = fila.get("Dirección")
                    det = fila.get("Pedido")
                    tot = fila.get("Total")
                    est = fila.get("Estado")
                    pago_original = fila.get("MetodoPago", "Efectivo")
                    
                    with st.container():
                        col_m1, col_m2 = st.columns()
                        with col_m1:
                            st.markdown(f"### 📍 Orden #{id_p} (`{est}`)")
                            st.markdown(f"**Dirección:** {dom}")
                            st.markdown(f"**Detalles:** {det}")
                            st.markdown(f"💰 **MONTO A COBRAR:** `${tot}`")
                            st.markdown(f"💳 **Método solicitado:** *{pago_original}*")
                        with col_m2:
                            st.write("")
                            pago_real = st.selectbox(f"Confirmar método recibido #{id_p}:", METODOS_PAGO, index=METODOS_PAGO.index(pago_original) if pago_original in METODOS_PAGO else 0)
                            
                            if st.button("✅ Confirmar Entrega", key=f"entregado_{id_p}", use_container_width=True):
                                payload_moto = {"accion": "actualizar_entrega_moto", "id": id_p, "estado": "Entregado", "metodo_real": pago_real}
                                requests.post(API_URL, json=payload_moto)
                                st.toast("¡Orden completada!")
                                st.cache_data.clear()
                                st.rerun()
                        st.markdown("<hr style='border-top: 1px dotted #10B981;'>", unsafe_allow_html=True)

# 3. PANEL DEL LOCAL
with pestana_local:
    st.markdown("<h2 style='color: #1E3A8A;'>🏢 Consola de Despacho Central</h2>", unsafe_allow_html=True)
    
    if not df_pedidos.empty:
        df_pedidos["Total"] = pd.to_numeric(df_pedidos["Total"], errors='coerce').fillna(0)
        df_entregados = df_pedidos[df_pedidos["Estado"] == "Entregado"]
        
        efectivo_total = df_entregados[df_entregados["MetodoPago"].str.contains("Efectivo", na=False) & ~df_entregados["MetodoPago"].str.contains("Mixto", na=False)]["Total"].sum()
        transfe_total = df_entregados[df_entregados["MetodoPago"].str.contains("Transferencia", na=False) & ~df_entregados["MetodoPago"].str.contains("Mixto", na=False)]["Total"].sum()
        mixto_total = df_entregados[df_entregados["MetodoPago"].str.contains("Mixto", na=False)]["Total"].sum()
        caja_total = df_entregados["Total"].sum()
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("💵 Total Efectivo", f"${efectivo_total:,.2f}")
        col_m2.metric("📱 Total Transferencias", f"${transfe_total:,.2f}")
        col_m3.metric("🔀 Total Mixto", f"${mixto_total:,.2f}")
        col_m4.metric("💰 CAJA GENERAL TOTAL", f"${caja_total:,.2f}")
    
    st.markdown("---")
    
    if df_pedidos.empty:
        st.info("No hay movimientos registrados.")
    else:
        opciones_motos = ["Sin Asignar"] + MOTOS_FIJAS
        for index, fila in df_pedidos.iterrows():
            id_p = fila.get("ID")
            cli = fila.get("Cliente")
            dom = fila.get("Dirección")
            det = fila.get("Pedido")
            tot = fila.get("Total")
            rep = fila.get("Repartidor")
            est = fila.get("Estado")
            pago = fila.get("MetodoPago", "Efectivo")
            
            chofer_actual = TURNOS_DICT.get(rep, "Nadie asignado")
            
            with st.container():
                c1, c2, c3, c4 = st.columns()
                with c1:
                    st.markdown(f"### `#{id_p}`")
                    st.caption(f"⏱️ {fila.get('Hora', '')}")
                    if rep != "Sin Asignar":
                        st.markdown(f"👤 Conductor: **{chofer_actual}**")
                with c2:
                    st.markdown(f"👤 **Cliente:** {cli}")
                    st.markdown(f"📍 **Destino:** _{dom}_")
                    st.markdown(f"📦 **Contenido:** {det}")
                with c3:
                    st.markdown(f"💰 Cobro: **${tot}** (_{pago}_)")
                    idx_moto = opciones_motos.index(rep) if rep in opciones_motos else 0
                    moto_elegida = st.selectbox(f"Asignar Vehículo a #{id_p}", opciones_motos, key=f"local_moto_{id_p}", index=idx_moto)
                    estado_elegido = st.selectbox(f"Estado #{id_p}", ["Pendiente", "En Ruta", "Entregado", "Cancelado"], key=f"local_est_{id_p}", index=["Pendiente", "En Ruta", "Entregado", "Cancelado"].index(est))
                with c4:
                    st.write("")
                    st.write("")
                    if st.button("💾 Guardar Cambios", key=f"l_btn_{id_p}", use_container_width=True):
