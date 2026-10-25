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

# --- 10 DATOS FALSOS PARAGUAYOS PARA REVISAR EL FUNCIONAMIENTO ---
df_pedidos = pd.DataFrame([
    {"ID": 1, "Cliente": "Novedades Juanita", "Dirección": "Av. Mariscal López 1450", "Pedido": "Para: María - Ropa", "Estado": "En Ruta", "MontoPedido": 150000, "Envio": 15000, "Total": 165000, "MetodoPago": "Efectivo", "Hora": "10:30", "Repartidor": "Moto 1"},
    {"ID": 2, "Cliente": "Novedades Juanita", "Dirección": "Calle Palma esq. Chile", "Pedido": "Para: Pedro - Reloj", "Estado": "Pendiente", "MontoPedido": 85000, "Envio": 15000, "Total": 100000, "MetodoPago": "Transferencia", "Hora": "11:15", "Repartidor": "Moto 2"},
    {"ID": 3, "Cliente": "Novedades Juanita", "Dirección": "Aviadores del Chaco 2200", "Pedido": "Para: Ana - Cartera", "Estado": "Pendiente", "MontoPedido": 300000, "Envio": 20000, "Total": 320000, "MetodoPago": "Efectivo", "Hora": "14:00", "Repartidor": "Sin Asignar"},
    {"ID": 4, "Cliente": "Hamburguesería El Bajón", "Dirección": "Sajonia - Carlos A. López", "Pedido": "Para: Luis - 2 Combos", "Estado": "En Ruta", "MontoPedido": 45000, "Envio": 10000, "Total": 55000, "MetodoPago": "Efectivo", "Hora": "20:15", "Repartidor": "Moto 1"},
    {"ID": 5, "Cliente": "Hamburguesería El Bajón", "Dirección": "Villa Morra - Mcal Estigarribia", "Pedido": "Para: Fernando - Lomito", "Estado": "En Ruta", "MontoPedido": 120000, "Envio": 12000, "Total": 132000, "MetodoPago": "Mixto (Efectivo + Transferencia)", "Hora": "21:00", "Repartidor": "Moto 3"},
    {"ID": 6, "Cliente": "Farmacia San Blas", "Dirección": "Fernando de la Mora esq. 1ro de Mayo", "Pedido": "Para: Gabriela - Remedios", "Estado": "En Ruta", "MontoPedido": 210000, "Envio": 15000, "Total": 225000, "MetodoPago": "Transferencia", "Hora": "16:45", "Repartidor": "Moto 2"},
    {"ID": 7, "Cliente": "Farmacia San Blas", "Dirección": "Luque - Centro", "Pedido": "Para: Roque - Pañales", "Estado": "Pendiente", "MontoPedido": 95000, "Envio": 15000, "Total": 110000, "MetodoPago": "Efectivo", "Hora": "17:30", "Repartidor": "Moto 1"},
    {"ID": 8, "Cliente": "Pizzería La Bella", "Dirección": "San Lorenzo - UNA", "Pedido": "Para: Carlos - Pizza Familiar", "Estado": "En Ruta", "MontoPedido": 70000, "Envio": 12000, "Total": 82000, "MetodoPago": "Efectivo", "Hora": "19:40", "Repartidor": "Moto 3"},
    {"ID": 9, "Cliente": "Pizzería La Bella", "Dirección": "Lambaré - Av. Cacique", "Pedido": "Para: Diego - 2 Pizzas Medianas", "Estado": "Pendiente", "MontoPedido": 110000, "Envio": 15000, "Total": 125000, "MetodoPago": "Transferencia", "Hora": "20:00", "Repartidor": "Sin Asignar"},
    {"ID": 10, "Cliente": "Comercial San Cayetano", "Dirección": "Mariano Roque Alonso", "Pedido": "Para: Sol - Pack de Gaseosas", "Estado": "Cancelado", "MontoPedido": 180000, "Envio": 25000, "Total": 205000, "MetodoPago": "Efectivo", "Hora": "12:10", "Repartidor": "Moto 2"},
])

# --- MODIFICADO: 3 CONDUCTORES Y ASIGNACIONES DE MOTOS FIJAS ---
df_conductores = pd.DataFrame([
    {"Nombre": "Juan Pérez", "Telefono": "595981111111"},
    {"Nombre": "Carlos Gómez", "Telefono": "595982222222"},
    {"Nombre": "Lucas Benítez", "Telefono": "595983333333"}
])

df_turnos = pd.DataFrame([
    {"Moto": "Moto 1", "Conductor": "Juan Pérez"},
    {"Moto": "Moto 2", "Conductor": "Carlos Gómez"},
    {"Moto": "Moto 3", "Conductor": "Lucas Benítez"}
])
# -----------------------------------------------------------------

CONDUCTORES_DICT = dict(zip(df_conductores["Nombre"].astype(str), df_conductores["Telefono"].astype(str)))
TURNOS_DICT = dict(zip(df_turnos["Moto"].astype(str), df_turnos["Conductor"].astype(str)))

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
            
        if enviar:
            st.success("¡Envío registrado exitosamente! (Simulado)")
            
    with p_admin:
        clave = st.text_input("Introduce la clave del local:", type="password")
        if clave == CONTRASEÑA_LOCAL:
            
            tab_gestion, tab_cierre = st.tabs(["📦 GESTIÓN DE PEDIDOS", "💰 AUDITORÍA DE CIERRE"])
            
            with tab_gestion:
                lista_emp = ["Todos"] + sorted(list(df_pedidos["Cliente"].dropna().unique()))
                emp_filtro = st.selectbox("Filtrar por Emprendedor / Comercio:", lista_emp, key="filtro_adm")
                
                if emp_filtro != "Todos":
                    df_visibles = df_pedidos[df_pedidos["Cliente"] == emp_filtro]
                else:
                    df_visibles = df_pedidos
                
                for idx, f in df_visibles.iterrows():
                    with st.container():
                        col1, col2, col3 = st.columns(3)
                        col1.markdown(f"### `#{f['ID']}`\n⏱️ {f['Hora']}")
                        
                        val_ped = f"{int(f['MontoPedido']):,}".replace(",", ".")
                        val_env = f"{int(f['Envio']):,}".replace(",", ".")
                        val_tot = f"{int(f['Total']):,}".replace(",", ".")
                        
                        col2.markdown(f"👤 **{f['Cliente']}**\n📍 {f['Dirección']}\n📦 {f['Pedido']}\n💵 *Pedido:* Gs. {val_ped} | 🏍️ *Envío:* Gs. {val_env}")
                        
                        m_elegida = col3.selectbox(f"Vehículo:", ["Sin Asignar"] + MOTOS_FIJAS, index=(["Sin Asignar"] + MOTOS_FIJAS).index(f['Repartidor']) if f['Repartidor'] in (["Sin Asignar"] + MOTOS_FIJAS) else 0, key=f"m_{f['ID']}")
                        e_elegido = col3.selectbox(f"Estado:", ["Pendiente", "En Ruta", "Entregado", "Cancelado"], index=["Pendiente", "En Ruta", "Entregado", "Cancelado"].index(f['Estado']) if f['Estado'] in ["Pendiente", "En Ruta", "Entregado", "Cancelado"] else 0, key=f"e_{f['ID']}")
                        
                        txt_wa = f"*🚀 OPTIRUTA*\n📦 *Orden:* #{f['ID']}\n📍 *Destino:* {f['Dirección']}\n💵 *Pedido:* Gs. {val_ped}\n🏍️ *Envío:* Gs. {val_env}\n💰 *TOTAL A COBRAR:* Gs. {val_tot}"
                        num_destino = CONDUCTORES_DICT.get(TURNOS_DICT.get(m_elegida, ""), "")
                        if num_destino:
                            col3.link_button("📲 Despachar", f"https://wa.me{num_destino}?text={urllib.parse.quote(txt_wa)}", use_container_width=True, type="primary")

            with tab_cierre:
                lista_cierre = sorted(list(df_pedidos["Cliente"].dropna().unique()))
                emp_cierre = st.selectbox("Selecciona el Comercio para sumar totales:", lista_cierre, key="filtro_cie")
                st.markdown(f"### 📊 Rendición del Día: **{emp_cierre}**")
                
                df_calc = df_pedidos[(df_pedidos["Cliente"] == emp_cierre) & (df_pedidos["Estado"] == "Entregado")].copy()
                
                if not df_calc.empty:
                    df_calc["Total"] = df_calc["Total"].astype(float)
                    
                    efectivo_total = df_calc[df_calc["MetodoPago"].str.contains("Efectivo", na=False)]["Total"].sum()
                    transfe_total = df_calc[df_calc["MetodoPago"].str.contains("Transferencia", na=False)]["Total"].sum()
                    mixto_total = df_calc[df_calc["MetodoPago"].str.contains("Mixto", na=False)]["Total"].sum()
                    gran_total = df_calc["Total"].sum()
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("💵 Total Efectivo", f"Gs. {int(efectivo_total):,}".replace(",", "."))
                    c2.metric("💳 Total Transferencia", f"Gs. {int(transfe_total):,}".replace(",", "."))
                    c3.metric("🔀 Total Mixto", f"Gs. {int(mixto_total):,}".replace(",", "."))
                    
                    st.markdown(f"### **Monto Neto Entregado Hoy:** `Gs. {int(gran_total):,}`".replace(",", "."))
                    
                    with st.form("f_cierre_seguro", clear_on_submit=True):
