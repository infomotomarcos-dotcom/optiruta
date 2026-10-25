import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import datetime

st.set_page_config(page_title="OptiRuta Delivery", page_icon="🚀", layout="centered")

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
    df_c_mock = pd.DataFrame([{"Nombre": "Juan Pérez", "Telefono": "595981111111"},{"Nombre": "Carlos Gómez", "Telefono": "595982222222"}])
    df_t_mock = pd.DataFrame([{"Moto": "Moto 1", "Conductor": "Juan Pérez"},{"Moto": "Moto 2", "Conductor": "Carlos Gómez"},{"Moto": "Moto 3", "Conductor": "Sin Asignar"}])
    return pd.DataFrame(), df_c_mock, df_t_mock

df_pedidos, df_conductores, df_turnos = obtener_datos_sistema()

CONDUCTORES_DICT = dict(zip(df_conductores["Nombre"].astype(str), df_conductores["Telefono"].astype(str))) if not df_conductores.empty else {}
TURNOS_DICT = dict(zip(df_turnos["Moto"].astype(str), df_turnos["Conductor"].astype(str))) if not df_turnos.empty else {}

columnas_base = ["ID", "Cliente", "Dirección", "Pedido", "MontoPedido", "Envio", "Total", "Repartidor", "Estado", "Hora", "MetodoPago"]
for col in columnas_base:
    if df_pedidos.empty or col not in df_pedidos.columns:
        df_pedidos[col] = None

if "perfil" not in st.session_state:
    st.session_state.perfil = "Inicio"

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

elif st.session_state.perfil == "Emprendedores":
    if st.button("⬅️ Volver al Inicio"):
        st.session_state.perfil = "Inicio"
        st.rerun()
    
    p_carga, p_admin = st.tabs(["📥 CARGAR NUEVO ENVÍO", "🔒 ACCESO PRIVADO LOCAL"])
    
    with p_carga:
        with st.form("f_cliente", clear_on_submit=True):
            c_nom = st.text_input("Tu Nombre o Comercio *")
            c_tel = st.text_input("Tu Teléfono de Contacto *")
            d_nom = st.text_input("Nombre de quién recibe *")
            d_dir = st.text_input("Dirección Exacta de Entrega *")
            detalles = st.text_area("Contenido del paquete *")
            
            m_pedido = st.number_input("Monto del Pedido (Gs.) *", min_value=0, step=1000, value=0)
            m_envio = st.number_input("Monto del Envío / Flete (Gs.) *", min_value=0, step=1000, value=0)
            
            pago = st.selectbox("¿Cómo pagará al llegar? *", METODOS_PAGO)
            enviar = st.form_submit_button("🚀 Enviar Solicitud", use_container_width=True)
            
        if enviar and c_nom and d_dir and detalles:
            gran_total_calculado = m_pedido + m_envio
            pld_crear = {
                "accion": "crear", 
                "ID": len(df_pedidos)+1, 
                "Cliente": f"{c_nom} ({c_tel})", 
                "Dirección": d_dir, 
                "Pedido": f"Para: {d_nom} - {detalles}", 
                "MontoPedido": m_pedido,
                "Envio": m_envio,
                "Total": gran_total_calculado, 
                "Repartidor": "Sin Asignar", 
                "Estado": "Pendiente", 
                "Hora": datetime.now().strftime("%H:%M"), 
                "MetodoPago": pago
            }
            requests.post(API_URL, json=pld_crear)
            st.success("¡Envío registrado exitosamente!")
            st.cache_data.clear()
            st.rerun()
            
    with p_admin:
        clave = st.text_input("Introduce la clave del local:", type="password")
        if clave == CONTRASEÑA_LOCAL:
            st.markdown("### 📦 GESTIÓN DE PEDIDOS")
            
            lista_emp = ["Todos"]
            if not df_pedidos.empty:
                lista_emp = ["Todos"] + sorted(list(df_pedidos["Cliente"].dropna().unique()))
            
            emp_filtro = st.selectbox("Filtrar por Emprendedor / Comercio:", lista_emp)
            
            if not df_pedidos.empty:
                if emp_filtro != "Todos":
                    df_visibles = df_pedidos[df_pedidos["Cliente"] == emp_filtro]
                else:
                    df_visibles = df_pedidos
            else:
                df_visibles = pd.DataFrame()
            
            if df_visibles.empty:
                st.info("No hay pedidos registrados para mostrar con los filtros seleccionados.")
            else:
                for idx, f in df_visibles.iterrows():
                    with st.container():
                        col1, col2, col3 = st.columns()
                        col1.markdown(f"### `#{f['ID']}`\n⏱️ {f['Hora']}")
                        
                        val_ped = f"{int(f['MontoPedido']):,}".replace(",", ".") if ('MontoPedido' in f and pd.notna(f['MontoPedido'])) else "0"
                        val_env = f"{int(f['Envio']):,}".replace(",", ".") if ('Envio' in f and pd.notna(f['Envio'])) else "0"
                        val_tot = f"{int(f['Total']):,}".replace(",", ".") if pd.notna(f['Total']) else "0"
                        
                        col2.markdown(f"👤 **{f['Cliente']}**\n📍 {f['Dirección']}\n📦 {f['Pedido']}\n💵 *Pedido:* Gs. {val_ped} | 🏍️ *Envío:* Gs. {val_env}")
                        
                        m_elegida = col3.selectbox(f"Vehículo:", ["Sin Asignar"] + MOTOS_FIJAS, index=(["Sin Asignar"] + MOTOS_FIJAS).index(f['Repartidor']) if f['Repartidor'] in (["Sin Asignar"] + MOTOS_FIJAS) else 0, key=f"m_{f['ID']}")
                        e_elegido = col3.selectbox(f"Estado:", ["Pendiente", "En Ruta", "Entregado", "Cancelado"], index=["Pendiente", "En Ruta", "Entregado", "Cancelado"].index(f['Estado']) if f['Estado'] in ["Pendiente", "En Ruta", "Entregado", "Cancelado"] else 0, key=f"e_{f['ID']}")
                        
                        if m_elegida != f['Repartidor'] or e_elegido != f['Estado']:
                            requests.post(API_URL, json={"accion": "actualizar_completo", "id": f['ID'], "repartidor": m_elegida, "estado": e_elegido})
                            st.cache_data.clear()
                            st.rerun()
                            
                        txt_wa = f"*🚀 OPTIRUTA*\n📦 *Orden:* #{f['ID']}\n📍 *Destino:* {f['Dirección']}\n💵 *Pedido:* Gs. {val_ped}\n🏍️ *Envío:* Gs. {val_env}\n💰 *TOTAL A COBRAR:* Gs. {val_tot}"
                        num_destino = CONDUCTORES_DICT.get(TURNOS_DICT.get(m_elegida, ""), "")
                        if num_destino:
                            col3.link_button("📲 Despachar", f"https://wa.me{num_destino}?text={urllib.parse.quote(txt_wa)}", use_container_width=True, type="primary")

            if emp_filtro != "Todos" and not df_pedidos.empty:
                st.markdown("---")
                st.markdown(f"### 💰 Cierre de Caja: {emp_filtro}")
                
                df_entregados = df_pedidos[(df_pedidos["Cliente"] == emp_filtro) & (df_pedidos["Estado"] == "Entregado")]
                
                if not df_entregados.empty:
                    df_calc = df_entregados.copy()
                    df_calc["Total"] = df_calc["Total"].astype(float)
                    
                    efectivo_total = df_calc[df_calc["MetodoPago"].str.contains("Efectivo", na=False)]["Total"].sum()
                    transfe_total = df_calc[df_calc["MetodoPago"].str.contains("Transferencia", na=False)]["Total"].sum()
                    mixto_total = df_calc[df_calc["MetodoPago"].str.contains("Mixto", na=False)]["Total"].sum()
                    gran_total = df_calc["Total"].sum()
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("💵 Total Efectivo", f"Gs. {int(efectivo_total):,}".replace(",", "."))
                    c2.metric("💳 Total Transferencia", f"Gs. {int(transfe_total):,}".replace(",", "."))
                    c3.metric("🔀 Total Mixto", f"Gs. {int(mixto_total):,}".replace(",", "."))
                    
                    st.markdown(f"**Monto Neto Rendido Hoy:** `Gs. {int(gran_total):,}`".replace(",", "."))
                    
                    with st.form("f_cierre_dinamico"):
                        obs = st.text_input("Notas u Observaciones del Arqueo")
                        btn_guardar_cierre = st.form_submit_button("🔒 Archivar Cierre de Caja", use_container_width=True, type="primary")
                        
                        if btn_guardar_cierre:
                            pld_cierre = {
                                "accion": "cierre_caja",
                                "emprendedor": emp_filtro,
                                "total_rendido": gran_total,
                                "observaciones": obs,
                                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
                            }
                            try:
                                requests.post(API_URL, json=pld_cierre)
                                st.success(f"¡Cierre guardado correctamente para {emp_filtro}!")
                                st.cache_data.clear()
