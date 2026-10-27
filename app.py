import streamlit as st
import requests
import pandas as pd
import math
from datetime import datetime
from urllib.parse import quote
from streamlit_geolocation import streamlit_geolocation

# ============================================================
# OPTIRUTA DELIVERY - INTERFAZ CLARA AZUL Y ORO (LUQUE)
# Mantiene la API de Google Apps Script de la version anterior.
# ============================================================

st.set_page_config(
    page_title="OptiRuta Delivery",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
:root {
    color-scheme: light !important;
}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #FFFFFF !important;
    color: #17212F !important;
}
[data-testid="stHeader"] { background: #FFFFFF !important; }
[data-testid="stSidebar"] {
    background: #F3F7FC !important;
    border-right: 2px solid #D5A629 !important;
}
/* Texto general: forzar colores oscuros para que no desaparezcan sobre blanco. */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stMain"] p, [data-testid="stMain"] li {
    color: #17212F !important;
}
h1, h2, h3, h4,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
    color: #153F78 !important;
    font-weight: 800 !important;
}
/* Etiquetas de TODOS los campos: texto oscuro y legible. */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] *,
[data-testid="stWidgetLabel"] p,
.stTextInput label, .stTextArea label, .stNumberInput label,
.stSelectbox label, .stMultiSelect label, .stDateInput label,
.stTimeInput label, .stRadio label, .stCheckbox label,
.stSlider label, .stFileUploader label,
[data-testid="stForm"] label,
[data-testid="stForm"] label *,
[data-testid="stMarkdownContainer"] p {
    color: #17212F !important;
    opacity: 1 !important;
    font-weight: 700 !important;
}
/* Texto escrito, opciones y valores seleccionados. */
input, textarea,
[data-baseweb="select"] *,
[data-baseweb="input"] *,
[data-baseweb="textarea"] *,
[data-testid="stDateInput"] input {
    background-color: #FFFFFF !important;
    color: #17212F !important;
    -webkit-text-fill-color: #17212F !important;
    opacity: 1 !important;
}
input::placeholder, textarea::placeholder {
    color: #596579 !important;
    -webkit-text-fill-color: #596579 !important;
    opacity: 1 !important;
}
.stCaption, [data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] * {
    color: #3F4B5B !important;
    opacity: 1 !important;
}
div.stButton > button, div.stFormSubmitButton > button, .stLinkButton a {
    background: #174A91 !important;
    color: #FFFFFF !important;
    border: 2px solid #174A91 !important;
    border-radius: 12px !important;
    min-height: 48px !important;
    font-weight: 800 !important;
    font-size: 16px !important;
}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {
    background: #0F356B !important;
    border-color: #D5A629 !important;
    color: #FFFFFF !important;
}
[data-testid="stMetric"] {
    background: #F1F6FD !important;
    border: 1px solid #B9CBE2 !important;
    border-radius: 14px !important;
    padding: 14px !important;
}
[data-testid="stMetricLabel"] { color: #25364B !important; }
[data-testid="stMetricValue"] { color: #123E79 !important; font-weight: 850 !important; }
[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #C7D5E6 !important;
    border-radius: 14px !important;
}
input, textarea, [data-baseweb="select"] > div {
    background: #FFFFFF !important;
    color: #17212F !important;
}
[data-testid="stDataFrame"] { border: 1px solid #C7D5E6; }
.optiruta-brand {
    color: #174A91; font-weight: 900; letter-spacing: 1.5px;
    font-size: 30px; line-height: 1.1;
}
.optiruta-sub { color: #27384D; font-size: 14px; font-weight: 600; }
.flag-blue { height: 8px; background: #174A91; border-radius: 8px; }
.flag-gold { height: 5px; background: #D5A629; border-radius: 8px; margin-top: 5px; }
.order-number { font-size: 25px; color: #123E79; font-weight: 900; }
.order-address { font-size: 18px; color: #17212F; font-weight: 750; }
.small-note { color: #3F4B5B; font-size: 13px; }
</style>
""", unsafe_allow_html=True)


def cfg(name, default=""):
    try:
        return st.secrets[name]
    except Exception:
        return default

API_URL = cfg("API_URL")
API_KEY = cfg("API_KEY")

if not API_URL or not API_KEY:
    st.error("Falta configurar API_URL y API_KEY en los secretos de Streamlit. No pegues esos datos aquí en el chat.")
    st.stop()


def api(action, **kwargs):
    payload = {
        "action": action,
        "api_key": API_KEY,
        "user": st.session_state.get("user"),
        **kwargs
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        if data.get("status") != "ok":
            st.error(data.get("message", "El servidor devolvió un error."))
            return None
        return data
    except Exception as exc:
        st.error(f"No se pudo comunicar con Google Sheets: {exc}")
        return None


def money(value):
    try:
        return "Gs. " + f"{int(float(value or 0)):,}".replace(",", ".")
    except Exception:
        return "Gs. 0"


def rows(sheet):
    result = api("list", sheet=sheet)
    return result.get("rows", []) if result else []


def df(sheet):
    return pd.DataFrame(rows(sheet))


def save(sheet, record):
    result = api("save", sheet=sheet, record=record)
    if result:
        st.success("Guardado correctamente.")
        st.rerun()


def distance_km(lat1, lon1, lat2, lon2):
    """Distancia aproximada en linea recta entre dos coordenadas GPS."""
    radius = 6371.0
    p1, p2 = math.radians(float(lat1)), math.radians(float(lat2))
    dlat = math.radians(float(lat2) - float(lat1))
    dlon = math.radians(float(lon2) - float(lon1))
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def maps_url(address):
    return "https://www.google.com/maps/search/?api=1&query=" + quote(str(address or ""))


def brand_header(subtitle="Sistema de gestión de delivery"):
    st.markdown('<div class="optiruta-brand">OPTIRUTA</div>', unsafe_allow_html=True)
    st.markdown('<div class="optiruta-sub">DELIVERY · LUQUE</div>', unsafe_allow_html=True)
    st.markdown('<div class="flag-blue"></div><div class="flag-gold"></div>', unsafe_allow_html=True)
    st.caption(subtitle)


if "user" not in st.session_state:
    st.session_state.user = None
if "portal" not in st.session_state:
    st.session_state.portal = None

# -------------------- ACCESO / INICIO --------------------
if not st.session_state.user:
    brand_header("Plataforma de pedidos, reparto y seguimiento")
    st.write("")
    st.title("Bienvenido")
    st.write("Elegí tu acceso para continuar.")
    p1, p2, p3 = st.columns(3)
    with p1:
        if st.button("🏪  EMPRENDEDORES", use_container_width=True):
            st.session_state.portal = "EMPRENDEDOR"
            st.rerun()
    with p2:
        if st.button("🛵  CONDUCTORES DELIVERY", use_container_width=True):
            st.session_state.portal = "CONDUCTOR"
            st.rerun()
    with p3:
        if st.button("⚙️  ADMINISTRADOR", use_container_width=True):
            st.session_state.portal = "ADMIN"
            st.rerun()

    if st.session_state.portal:
        portal_names = {
            "EMPRENDEDOR": "Acceso de emprendedores",
            "CONDUCTOR": "Acceso de conductores",
            "ADMIN": "Acceso de administración"
        }
        st.divider()
        st.subheader(portal_names[st.session_state.portal])
        st.markdown("### 🔐 Ingresá tus datos de acceso")
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("INGRESAR", use_container_width=True)
        if submitted:
            result = api("login", username=username.strip(), password=password)
            if result and result.get("user"):
                logged_user = result["user"]
                actual_role = str(logged_user.get("Rol", "")).upper()
                if actual_role != st.session_state.portal:
                    st.error("Este usuario no corresponde a este tipo de acceso. Elegí el acceso correcto.")
                else:
                    st.session_state.user = logged_user
                    st.rerun()
            elif result:
                st.error("Usuario o contraseña incorrectos, o cuenta inactiva.")
        if st.button("← Volver a los accesos"):
            st.session_state.portal = None
            st.rerun()
    st.stop()

user = st.session_state.user
role = str(user.get("Rol", "")).upper()
uid = user.get("ID_Referencia", "")

with st.sidebar:
    st.markdown("## OPTIRUTA")
    st.markdown('<div class="flag-blue"></div><div class="flag-gold"></div>', unsafe_allow_html=True)
    st.write(f"**{user.get('Usuario', 'Usuario')}**")
    st.caption(role)
    if st.button("CERRAR SESIÓN", use_container_width=True):
        st.session_state.user = None
        st.session_state.portal = None
        st.rerun()

# -------------------- ADMINISTRADOR --------------------
if role == "ADMIN":
    brand_header("Panel de administración")
    section = st.radio(
        "SECCIONES",
        ["Resumen", "Pedidos", "Emprendedores", "Conductores", "Motos", "Caja y movimientos", "Ubicaciones", "Usuarios"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if section == "Resumen":
        orders = df("PEDIDOS")
        drivers = df("CONDUCTORES")
        entrepreneurs = df("EMPRENDEDORES")
        c1, c2, c3 = st.columns(3)
        c1.metric("Pedidos registrados", len(orders))
        c2.metric("Conductores", len(drivers))
        c3.metric("Emprendedores", len(entrepreneurs))
        if not orders.empty and "Estado_Reparto" in orders.columns:
            st.subheader("Estado de los pedidos")
            st.bar_chart(orders["Estado_Reparto"].fillna("Sin estado").value_counts())

    elif section == "Pedidos":
        st.subheader("Registrar pedido")
        entrepreneurs = rows("EMPRENDEDORES")
        drivers = rows("CONDUCTORES")
        motos = rows("MOTOS")
        st.markdown("### 🧾 Datos del nuevo pedido")
        with st.form("new_order"):
            em_options = {
                f"{x.get('Nombre_Comercial')} ({x.get('ID_Emprendedor')})": x.get("ID_Emprendedor")
                for x in entrepreneurs if x.get("Estado", "Activo") == "Activo"
            }
            em_label = st.selectbox("Emprendedor", list(em_options) or ["Sin emprendedores"])
            customer = st.text_input("Nombre del cliente")
            phone = st.text_input("Teléfono")
            address = st.text_input("Dirección de entrega")
            description = st.text_input("Descripción del pedido")
            a, b, c = st.columns(3)
            product_cost = a.number_input("Costo del producto (Gs.)", min_value=0, step=1000)
            shipping = b.number_input("Costo del envío (Gs.)", min_value=0, value=15000, step=1000)
            prepaid = c.number_input("Anticipo ya pagado (Gs.)", min_value=0, step=1000)
            method = st.selectbox("Pago del cliente", ["Efectivo", "Transferencia al emprendedor", "Efectivo + transferencia", "Pagado adelantado"])
            if method == "Efectivo + transferencia":
                transfer = st.number_input("Parte transferida al emprendedor (Gs.)", min_value=0, step=1000)
            elif method in ["Transferencia al emprendedor", "Pagado adelantado"]:
                transfer = int(product_cost + shipping)
            else:
                transfer = 0
            if st.form_submit_button("REGISTRAR PEDIDO", use_container_width=True):
                total = int(product_cost + shipping)
                record = {
                    "ID_Pedido": "", "Fecha_Carga": datetime.now().isoformat(timespec="seconds"),
                    "ID_Emprendedor": em_options.get(em_label, ""), "Nombre_Cliente": customer,
                    "Telefono_Cliente": phone, "Direccion_Entrega": address, "Descripcion_Pedido": description,
                    "Costo_Producto": int(product_cost), "Costo_Envio": int(shipping), "Total_Cobrar": total,
                    "Metodo_Pago": method, "Monto_Anticipado": int(prepaid), "Monto_Efectivo_Cobrado": 0,
                    "Monto_Transferencia_Adicional": int(transfer), "ID_Conductor": "", "ID_Moto": "",
                    "Estado_Reparto": "Pendiente", "Fecha_Entrega": "", "Estado_Liquidacion": "Pendiente",
                    "Observaciones": ""
                }
                if not customer or not address:
                    st.error("Completá el nombre y la dirección.")
                else:
                    save("PEDIDOS", record)

        st.divider()
        st.subheader("Asignar o modificar pedidos")
        data = df("PEDIDOS")
        if not data.empty:
            st.dataframe(data, use_container_width=True, hide_index=True)
            ids = data.get("ID_Pedido", pd.Series(dtype=str)).astype(str).tolist()
            selected = st.selectbox("Pedido", ids)
            chosen = data[data["ID_Pedido"].astype(str) == str(selected)].iloc[0].to_dict() if selected else {}
            active_drivers = [d for d in drivers if d.get("Estado", "Activo") == "Activo"]
            active_motos = [m for m in motos if m.get("Estado", "Activa") == "Activa"]
            driver_map = {f"{d.get('Nombre_Completo')} ({d.get('ID_Conductor')})": d.get("ID_Conductor") for d in active_drivers}
            moto_map = {f"{m.get('Descripcion')} ({m.get('ID_Moto')})": m.get("ID_Moto") for m in active_motos}
            current_driver_label = next((k for k, v in driver_map.items() if str(v) == str(chosen.get("ID_Conductor", ""))), "")
            current_moto_label = next((k for k, v in moto_map.items() if str(v) == str(chosen.get("ID_Moto", ""))), "")
            st.markdown("### 🛵 Datos de asignación y estado")
            with st.form("assign"):
                dl = st.selectbox("Conductor", [""] + list(driver_map), index=(1 + list(driver_map).index(current_driver_label)) if current_driver_label else 0)
                ml = st.selectbox("Moto", [""] + list(moto_map), index=(1 + list(moto_map).index(current_moto_label)) if current_moto_label else 0)
                states = ["Pendiente", "Retirado", "En ruta", "Entregado", "Cancelado"]
                old_state = chosen.get("Estado_Reparto", "Pendiente")
                state = st.selectbox("Estado", states, index=states.index(old_state) if old_state in states else 0)
                if st.form_submit_button("GUARDAR ASIGNACIÓN"):
                    chosen["ID_Conductor"] = driver_map.get(dl, "")
                    chosen["ID_Moto"] = moto_map.get(ml, "")
                    chosen["Estado_Reparto"] = state
                    if state == "Entregado" and not chosen.get("Fecha_Entrega"):
                        chosen["Fecha_Entrega"] = datetime.now().isoformat(timespec="seconds")
                    save("PEDIDOS", chosen)
        else:
            st.info("Todavía no hay pedidos.")

    elif section == "Emprendedores":
        st.subheader("Emprendedores")
        st.markdown("### 🏪 Datos del emprendedor")
        with st.form("entrepreneur"):
            name = st.text_input("Nombre comercial")
            phone = st.text_input("Teléfono de contacto")
            address = st.text_input("Dirección")
            fee = st.number_input("Tarifa base de envío (Gs.)", min_value=0, value=15000, step=1000)
            if st.form_submit_button("AGREGAR EMPRENDEDOR"):
                save("EMPRENDEDORES", {"ID_Emprendedor": "", "Nombre_Comercial": name, "Telefono": phone, "Direccion": address, "Tarifa_Envio_Base": int(fee), "Estado": "Activo", "Observaciones": ""})
        st.dataframe(df("EMPRENDEDORES"), use_container_width=True, hide_index=True)

    elif section == "Conductores":
        st.subheader("Conductores")
        st.markdown("### 👤 Datos del conductor")
        with st.form("driver"):
            name = st.text_input("Nombre completo")
            phone = st.text_input("Teléfono", key="driver_phone")
            if st.form_submit_button("AGREGAR CONDUCTOR"):
                save("CONDUCTORES", {"ID_Conductor": "", "Nombre_Completo": name, "Telefono": phone, "Estado": "Activo", "Fecha_Ingreso": datetime.now().date().isoformat(), "Fecha_Baja": "", "Observaciones": ""})
        st.dataframe(df("CONDUCTORES"), use_container_width=True, hide_index=True)

    elif section == "Motos":
        st.subheader("Motos")
        st.markdown("### 🏍️ Datos de la moto")
        with st.form("bike"):
            desc = st.text_input("Descripción / modelo")
            plate = st.text_input("Patente")
            ownership = st.selectbox("Propiedad", ["OPTIRUTA", "CONDUCTOR"])
            owner = st.text_input("Propietario (si es del conductor)")
            if st.form_submit_button("AGREGAR MOTO"):
                save("MOTOS", {"ID_Moto": "", "Descripcion": desc, "Patente": plate, "Propiedad": ownership, "Propietario": owner, "Conductor_Asignado": "", "Estado": "Activa", "Observaciones": ""})
        st.dataframe(df("MOTOS"), use_container_width=True, hide_index=True)

    elif section == "Caja y movimientos":
        st.subheader("Movimientos")
        st.dataframe(df("MOVIMIENTOS"), use_container_width=True, hide_index=True)
        st.subheader("Registrar transferencia recibida del emprendedor")
        ems = rows("EMPRENDEDORES")
        emmap = {f"{e.get('Nombre_Comercial')} ({e.get('ID_Emprendedor')})": e.get("ID_Emprendedor") for e in ems}
        st.markdown("### 💳 Datos de la transferencia")
        with st.form("transfer_in"):
            emlabel = st.selectbox("Emprendedor", list(emmap) or [""])
            amount = st.number_input("Monto recibido (Gs.)", min_value=0, step=1000)
            ref = st.text_input("Referencia / comprobante")
            if st.form_submit_button("REGISTRAR TRANSFERENCIA"):
                api("movement", record={"Tipo_Movimiento": "TRANSFERENCIA_ENVIO_RECIBIDA", "ID_Emprendedor": emmap.get(emlabel, ""), "Cuenta_Origen": "EMPRENDEDOR", "Cuenta_Destino": "OPTIRUTA", "Metodo_Pago": "Transferencia", "Monto": int(amount), "Estado": "Confirmado", "Referencia": ref, "Fecha_Hora": datetime.now().isoformat(timespec="seconds")})
                st.rerun()
        st.subheader("Liquidaciones guardadas")
        st.dataframe(df("LIQUIDACIONES"), use_container_width=True, hide_index=True)

    elif section == "Ubicaciones":
        st.subheader("Últimas ubicaciones de conductores")
        loc = df("UBICACIONES")
        if not loc.empty:
            st.dataframe(loc.sort_values("Fecha_Hora", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("Todavía no hay ubicaciones registradas.")

    elif section == "Usuarios":
        st.subheader("Crear acceso")
        st.markdown("### 🔑 Datos del nuevo usuario")
        with st.form("user_create"):
            uname = st.text_input("Usuario nuevo")
            pwd = st.text_input("Contraseña inicial", type="password")
            urole = st.selectbox("Rol", ["EMPRENDEDOR", "CONDUCTOR"])
            refid = st.text_input("ID de emprendedor o conductor")
            if st.form_submit_button("CREAR USUARIO"):
                result = api("create_user", username=uname, password=pwd, role=urole, reference_id=refid)
                if result:
                    st.success("Usuario creado.")
        st.info("Cada usuario debe estar vinculado a un registro activo de emprendedor o conductor.")

# -------------------- EMPRENDEDOR --------------------
elif role == "EMPRENDEDOR":
    brand_header("Portal privado del emprendedor")
    st.title("Cargar un pedido")
    st.markdown("### 📦 Información del pedido")
    with st.form("entrepreneur_order"):
        customer = st.text_input("Nombre del cliente")
        phone = st.text_input("Teléfono")
        address = st.text_input("Dirección de entrega")
        description = st.text_input("Descripción del pedido")
        a, b, c = st.columns(3)
        product = a.number_input("Costo del producto (Gs.)", min_value=0, step=1000)
        shipping = b.number_input("Costo del envío (Gs.)", min_value=0, step=1000)
        prepaid = c.number_input("Anticipo recibido (Gs.)", min_value=0, step=1000)
        method = st.selectbox("Método de pago", ["Efectivo al recibir", "Transferencia al emprendedor", "Efectivo + transferencia", "Pagado adelantado"])
        if st.form_submit_button("ENVIAR PEDIDO", use_container_width=True):
            total = int(product + shipping)
            record = {
                "ID_Pedido": "", "Fecha_Carga": datetime.now().isoformat(timespec="seconds"),
                "ID_Emprendedor": uid, "Nombre_Cliente": customer, "Telefono_Cliente": phone,
                "Direccion_Entrega": address, "Descripcion_Pedido": description,
                "Costo_Producto": int(product), "Costo_Envio": int(shipping), "Total_Cobrar": total,
                "Metodo_Pago": method, "Monto_Anticipado": int(prepaid),
                "Monto_Efectivo_Cobrado": 0, "Monto_Transferencia_Adicional": 0,
                "ID_Conductor": "", "ID_Moto": "", "Estado_Reparto": "Pendiente",
                "Fecha_Entrega": "", "Estado_Liquidacion": "Pendiente", "Observaciones": ""
            }
            if customer and address:
                save("PEDIDOS", record)
            else:
                st.error("Completá el nombre y la dirección.")

    st.divider()
    st.subheader("Mis pedidos")
    data = df("PEDIDOS")
    if not data.empty and "ID_Emprendedor" in data.columns:
        mine = data[data["ID_Emprendedor"].astype(str) == str(uid)]
        st.dataframe(mine, use_container_width=True, hide_index=True)
    else:
        st.info("Todavía no tenés pedidos registrados.")

# -------------------- CONDUCTOR --------------------
elif role == "CONDUCTOR":
    brand_header("Aplicación de trabajo del conductor")
    st.title("Mis entregas")
    st.caption("Pantalla clara de alto contraste para facilitar la lectura bajo el sol.")

    # Solicitar ubicación del teléfono. El navegador debe tener permiso GPS.
    gps = None
    try:
        gps = streamlit_geolocation()
    except Exception:
        gps = None

    current_lat = gps.get("latitude") if isinstance(gps, dict) else None
    current_lon = gps.get("longitude") if isinstance(gps, dict) else None
    gps_ok = current_lat is not None and current_lon is not None

    left, right = st.columns([2, 1])
    with left:
        if gps_ok:
            st.success("GPS disponible · ubicación recibida")
        else:
            st.warning("GPS no disponible. Permití la ubicación del teléfono para ordenar los pedidos por cercanía.")
    with right:
        if st.button("ACTUALIZAR PEDIDOS", use_container_width=True):
            st.rerun()

    if gps_ok and st.button("COMPARTIR MI UBICACIÓN CON OPTIRUTA", use_container_width=True):
        loc_result = api("location", record={
            "ID_Conductor": uid, "ID_Moto": "",
            "Fecha_Hora": datetime.now().isoformat(timespec="seconds"),
            "Latitud": current_lat, "Longitud": current_lon,
            "Precision": gps.get("accuracy", ""), "Estado_GPS": "Activo"
        })
        if loc_result:
            st.success("Ubicación compartida con administración.")

    data = df("PEDIDOS")
    if data.empty or "ID_Conductor" not in data.columns:
        st.info("Todavía no tenés pedidos asignados.")
    else:
        active_states = ["Pendiente", "Retirado", "En ruta"]
        mine = data[
            (data["ID_Conductor"].astype(str) == str(uid)) &
            (data["Estado_Reparto"].astype(str).isin(active_states))
        ].copy()

        if mine.empty:
            st.success("No tenés entregas pendientes. ¡Buen trabajo!")
        else:
            mine["Distancia_km"] = None
            if gps_ok and "Latitud_Entrega" in mine.columns and "Longitud_Entrega" in mine.columns:
                def calc_distance(row):
                    try:
                        if pd.notna(row.get("Latitud_Entrega")) and pd.notna(row.get("Longitud_Entrega")):
                            return distance_km(current_lat, current_lon, row.get("Latitud_Entrega"), row.get("Longitud_Entrega"))
                    except Exception:
                        pass
                    return float("inf")
                mine["Distancia_km"] = mine.apply(calc_distance, axis=1)
                mine = mine.sort_values("Distancia_km", ascending=True, na_position="last")
                st.info("Los pedidos con coordenadas guardadas se ordenan por distancia en línea recta. Para una ruta real, abrí la navegación GPS.")
            else:
                mine = mine.sort_values("Fecha_Carga", ascending=True) if "Fecha_Carga" in mine.columns else mine
                st.info("Mostrando pedidos asignados. Para ordenar por cercanía real, necesitamos guardar coordenadas GPS de cada dirección.")

            st.metric("Entregas pendientes", len(mine))
            for position, (_, order) in enumerate(mine.iterrows(), start=1):
                order_id = order.get("ID_Pedido", "-")
                address = order.get("Direccion_Entrega", "Dirección no cargada")
                amount = order.get("Total_Cobrar", 0)
                state = order.get("Estado_Reparto", "Pendiente")
                with st.container(border=True):
                    st.subheader(f"#{position} · PEDIDO {order_id}")
                    st.write(f"**Destino:** {address}")
                    st.write(f"**Monto a cobrar:** {money(amount)}")
                    st.write(f"**Estado:** {state}")
                    if gps_ok and pd.notna(order.get("Distancia_km")) and math.isfinite(float(order.get("Distancia_km"))):
                        st.write(f"**Distancia aproximada:** {float(order.get('Distancia_km')):.1f} km")
                    st.link_button("ABRIR NAVEGACIÓN GPS", maps_url(address), use_container_width=True)
                    if st.button("CONFIRMAR ENTREGA", key=f"del_{order_id}", use_container_width=True):
                        rec = order.drop(labels=["Distancia_km"], errors="ignore").to_dict()
                        rec["Estado_Reparto"] = "Entregado"
                        rec["Fecha_Entrega"] = datetime.now().isoformat(timespec="seconds")
                        rec["Estado_Liquidacion"] = "Pendiente"
                        save("PEDIDOS", rec)

else:
    st.error("Rol no reconocido. Contactá al administrador.")
