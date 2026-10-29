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
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
:root { color-scheme: light !important; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background:#F5F7FB !important; color:#17243A !important;
}
[data-testid="stHeader"] { background:rgba(245,247,251,.94) !important; }
[data-testid="stMainBlockContainer"] { max-width:1480px; padding-top:3.8rem; padding-bottom:3rem; }
[data-testid="stSidebar"] { background:#FFFFFF !important; border-right:1px solid #DCE4EF !important; }
[data-testid="stSidebar"] > div:first-child { padding-top:1.2rem; }
html, body, p, li, label, span, div { color:inherit; }
[data-testid="stMain"] p, [data-testid="stMain"] li { color:#34445B !important; }
h1,h2,h3,h4,[data-testid="stMarkdownContainer"] h1,[data-testid="stMarkdownContainer"] h2,[data-testid="stMarkdownContainer"] h3 {
  color:#0750B8 !important; font-weight:850 !important; letter-spacing:-.025em;
}
h1 { font-size:2.15rem !important; }
h2 { font-size:1.55rem !important; }
h3 { font-size:1.15rem !important; }
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *,
.stTextInput label,.stTextArea label,.stNumberInput label,.stSelectbox label,
.stMultiSelect label,.stDateInput label,.stTimeInput label,.stRadio label,
.stCheckbox label,.stSlider label,.stFileUploader label,
[data-testid="stForm"] label,[data-testid="stForm"] label * {
  color:#1C2D45 !important; opacity:1 !important; font-weight:700 !important;
}
input,textarea,[data-baseweb="select"] *,[data-baseweb="input"] *,[data-baseweb="textarea"] *,
[data-testid="stDateInput"] input {
  background:#FFFFFF !important; color:#17243A !important; -webkit-text-fill-color:#17243A !important;
  border-color:#C8D4E3 !important; opacity:1 !important;
}
input::placeholder,textarea::placeholder { color:#718096 !important; -webkit-text-fill-color:#718096 !important; opacity:1 !important; }
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] * { color:#64748B !important; opacity:1 !important; }
[data-testid="stVerticalBlockBorderWrapper"] { background:#FFFFFF !important; border:1px solid #DFE6EF !important; border-radius:18px !important; box-shadow:0 5px 18px rgba(21,47,82,.045); }
[data-testid="stMetric"] { background:#FFFFFF !important; border:1px solid #DFE6EF !important; border-radius:18px !important; padding:16px 18px !important; box-shadow:0 5px 18px rgba(21,47,82,.045); }
[data-testid="stMetricLabel"] { color:#52627A !important; font-weight:700 !important; }
[data-testid="stMetricValue"] { color:#0750B8 !important; font-weight:900 !important; }
div.stButton > button:not([kind="secondary"]), div.stFormSubmitButton > button, .stLinkButton a {
  background:#0750B8 !important; color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important;
  border:1px solid #0750B8 !important; border-radius:12px !important; min-height:46px !important;
  padding:.55rem 1rem !important; font-weight:800 !important; font-size:15px !important;
  box-shadow:0 3px 8px rgba(23,74,145,.12);
}
div.stButton > button:not([kind="secondary"]) *, div.stFormSubmitButton > button *, .stLinkButton a * {
  color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important;
}
div.stButton > button:not([kind="secondary"]):hover, div.stFormSubmitButton > button:hover, .stLinkButton a:hover {
  background:#043B89 !important; border-color:#E9A817 !important; color:#FFFFFF !important;
  -webkit-text-fill-color:#FFFFFF !important;
}
div.stButton > button:not([kind="secondary"]):hover *, div.stFormSubmitButton > button:hover *, .stLinkButton a:hover * {
  color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important;
}
button[kind="secondary"] { background:#FFFFFF !important; color:#0750B8 !important; -webkit-text-fill-color:#0750B8 !important; border:1px solid #B8C9DE !important; }
button[kind="secondary"] * { color:#0750B8 !important; -webkit-text-fill-color:#0750B8 !important; }
[data-testid="stDataFrame"] { border:1px solid #DCE4EF !important; border-radius:14px !important; overflow:hidden; }
[data-testid="stForm"] { background:#FFFFFF; border:1px solid #E0E7F0; border-radius:18px; padding:1.1rem 1.2rem .7rem; }
hr { border-color:#E0E7F0 !important; }
.optiruta-top { background:linear-gradient(115deg,#0750B8 0%,#0750B8 72%,#E9A817 72%,#E9A817 100%); border-radius:20px; padding:28px 28px; color:#FFFFFF; margin-bottom:22px; box-shadow:0 8px 22px rgba(18,59,112,.12); animation: optirutaEntrada .9s ease-out both; }
.optiruta-top * { color:#FFFFFF !important; }
.optiruta-brand { font-size:clamp(42px, 5vw, 66px); font-weight:950; letter-spacing:3px; line-height:1.08; animation: optirutaLogo .85s cubic-bezier(.2,.8,.2,1) both; text-shadow:0 3px 10px rgba(0,0,0,.12); }
@keyframes optirutaEntrada { from { opacity:0; transform:translateY(18px); } to { opacity:1; transform:translateY(0); } }
@keyframes optirutaLogo { from { opacity:0; transform:scale(.88); letter-spacing:10px; } to { opacity:1; transform:scale(1); letter-spacing:3px; } }
.optiruta-tag { display:inline-block; margin-top:12px; background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.28); border-radius:30px; padding:5px 11px; font-size:12px; font-weight:700; }
.sidebar-brand { color:#0750B8 !important; font-size:25px; font-weight:950; letter-spacing:1.5px; }
.sidebar-caption { color:#65758B !important; font-size:12px; font-weight:700; letter-spacing:1px; }
.flag-blue { height:7px; background:#0750B8; border-radius:7px; }
.flag-gold { height:4px; background:#E9A817; border-radius:7px; margin-top:5px; }
.order-number { font-size:25px; color:#0750B8; font-weight:900; }
.order-address { font-size:18px; color:#17212F; font-weight:750; }
.small-note { color:#64748B; font-size:13px; }
.priority-high { color:#A32121; font-weight:900; }
.priority-normal { color:#0750B8; font-weight:800; }
/* Identidad visual inspirada en la referencia OptiRuta para PC */
.optiruta-top {
  display:flex; align-items:center; justify-content:space-between; gap:24px;
  background:linear-gradient(112deg,#FFFFFF 0%,#FFFFFF 66%,#FFFAEB 100%);
  border:1px solid #DCE6F3; border-left:7px solid #0750B8; border-radius:20px;
  padding:24px 28px; margin:0 0 24px; box-shadow:0 8px 24px rgba(18,59,112,.075);
  animation:optirutaEntrada .55s ease-out both;
}
.optiruta-brand {
  color:#0750B8 !important; font-size:clamp(34px,4vw,54px); font-weight:950;
  letter-spacing:-2px; line-height:1; text-shadow:none; animation:none; white-space:nowrap;
}
.optiruta-brand .gold { color:#E9A817 !important; }
.optiruta-brand .delivery { display:block; margin-top:5px; color:#0750B8 !important; font-size:11px;
  letter-spacing:7px; font-weight:850; text-align:right; }
.optiruta-slogan { border-left:2px solid #E9A817; padding-left:20px; color:#0750B8 !important;
  font-size:clamp(15px,1.6vw,21px); font-weight:850; line-height:1.25; max-width:260px; }
.optiruta-slogan small { display:block; margin-top:7px; color:#6B7890 !important; font-size:12px; font-weight:650; }
.optiruta-tag { margin-top:0; background:#0750B8; color:#FFFFFF !important; border:1px solid #0750B8;
  border-radius:999px; padding:11px 16px; font-size:13px; font-weight:800; text-align:center; }
.sidebar-brand { font-size:28px; letter-spacing:-1px; }
.sidebar-brand .gold { color:#E9A817 !important; }
.sidebar-caption { letter-spacing:1.8px; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong { color:#0750B8 !important; }
[data-testid="stSidebar"] [role="radiogroup"] { gap:5px; }
[data-testid="stSidebar"] [role="radiogroup"] label {
  background:#F7F9FD; border:1px solid #E1E8F2; border-radius:10px; padding:9px 10px;
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
  background:#EAF2FF; border-color:#8FB5EF; box-shadow:inset 3px 0 #0750B8;
}
[data-testid="stSidebar"] [data-testid="stButton"] button { min-height:42px !important; }
[data-testid="stDataFrame"] { box-shadow:0 4px 15px rgba(18,59,112,.04); }
@media (max-width: 760px) {
 [data-testid="stMainBlockContainer"] { padding-left:1rem; padding-right:1rem; padding-top:2.6rem; }
 h1 { font-size:1.7rem !important; }
 .optiruta-top { padding:17px; }
}
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


def _normalizar_busqueda(value):
    """Normaliza texto para buscar sin distinguir mayúsculas ni tildes."""
    import unicodedata
    text = str(value or "").strip().casefold()
    text = "".join(ch for ch in unicodedata.normalize("NFD", text) if unicodedata.category(ch) != "Mn")
    return " ".join(text.split())


def buscar_cliente(prefix):
    """Busca en CLIENTES y copia los datos exactos del registro seleccionado."""
    st.markdown("### 👤 Buscar cliente existente")
    clientes = rows("CLIENTES")
    query = st.text_input(
        "Buscar por nombre o teléfono",
        key=f"{prefix}_client_search",
        placeholder="Escribí el nombre o el teléfono"
    ).strip()

    coincidencias = []
    q = _normalizar_busqueda(query)
    if q:
        for index, client in enumerate(clientes):
            if not isinstance(client, dict):
                continue
            nombre = str(client.get("Nombre_Cliente", "") or "").strip()
            telefono = str(client.get("Telefono_Cliente", "") or "").strip()
            if q in _normalizar_busqueda(nombre) or q in _normalizar_busqueda(telefono):
                client_id = str(client.get("ID_Cliente", "") or "").strip()
                # La etiqueta incorpora ID y fila para distinguir incluso registros duplicados.
                label = f"{nombre or '(Sin nombre)'} · {telefono or 'Sin teléfono'} · {client_id or 'fila ' + str(index + 1)}"
                identity = f"{client_id or 'sin-id'}::fila-{index}"
                coincidencias.append((label, client, identity))

    options = ["— No seleccionar un cliente existente —"] + [item[0] for item in coincidencias]
    choice_key = f"{prefix}_client_choice"
    if st.session_state.get(choice_key) not in options:
        st.session_state[choice_key] = options[0]
    selected_label = st.selectbox(
        "Resultados de clientes", options, key=choice_key,
        help="Elegí un resultado para cargar sus datos guardados."
    )
    selected = next((item for item in coincidencias if item[0] == selected_label), None)
    identity_key = f"{prefix}_loaded_client_identity"
    previous_identity = st.session_state.get(identity_key)

    if selected:
        _, client, identity = selected
        # Sin caché de valores: cada selección aplica el registro que corresponde.
        if previous_identity != identity:
            st.session_state[f"{prefix}_customer_name"] = str(client.get("Nombre_Cliente", "") or "")
            st.session_state[f"{prefix}_customer_phone"] = str(client.get("Telefono_Cliente", "") or "")
            st.session_state[f"{prefix}_customer_address"] = str(client.get("Direccion_Habitual", "") or "")
            st.session_state[f"{prefix}_customer_maps"] = str(client.get("Ubicacion_Google_Maps", "") or "")
            st.session_state[identity_key] = identity
    elif previous_identity:
        # Al deseleccionar un cliente, limpiar sus datos para no dejar los del anterior.
        for field in ("customer_name", "customer_phone", "customer_address", "customer_maps"):
            st.session_state[f"{prefix}_{field}"] = ""
        st.session_state[identity_key] = None

    if q and not coincidencias:
        st.info("No encontramos coincidencias. Podés ingresar un cliente nuevo; no se crea desde la búsqueda.")
    elif not q:
        st.caption("La búsqueda consulta la hoja CLIENTES. Elegí un resultado para recuperar sus datos.")
    return selected[1] if selected else None


def _digits_phone(value):
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def _same_customer(a, b):
    """Compara identidad por teléfono normalizado o, si falta, por nombre normalizado."""
    phone_a, phone_b = _digits_phone(a.get("Telefono_Cliente")), _digits_phone(b.get("Telefono_Cliente"))
    name_a, name_b = _normalizar_busqueda(a.get("Nombre_Cliente")), _normalizar_busqueda(b.get("Nombre_Cliente"))
    return bool((phone_a and phone_b and phone_a == phone_b) or (name_a and name_b and name_a == name_b))


def asegurar_cliente(record):
    """Registra al cliente una sola vez desde el flujo existente de pedido; no agrega formularios."""
    name = str(record.get("Nombre_Cliente", "") or "").strip()
    phone = str(record.get("Telefono_Cliente", "") or "").strip()
    if not name or not phone:
        return
    clientes = rows("CLIENTES")
    if any(_same_customer(record, client) for client in clientes if isinstance(client, dict)):
        return
    client_record = {
        "ID_Cliente": "",
        "Nombre_Cliente": name,
        "Telefono_Cliente": phone,
        "Direccion_Habitual": str(record.get("Direccion_Entrega", "") or "").strip(),
        "Ubicacion_Google_Maps": str(record.get("Ubicacion_Google_Maps", "") or "").strip(),
        "Fecha_Registro": datetime.now().isoformat(timespec="seconds"),
        "Estado": "Activo",
        "ID_Emprendedor": str(record.get("ID_Emprendedor", "") or "")
    }
    # Si la agenda no puede actualizarse, no bloqueamos el pedido; la API reportará el error.
    api("save", sheet="CLIENTES", record=client_record)


def pedido_duplicado_reciente(record, segundos=30):
    """Evita reenvíos accidentales del mismo pedido dentro de una ventana breve."""
    now = datetime.now()
    fields = ("ID_Emprendedor", "Nombre_Cliente", "Telefono_Cliente", "Direccion_Entrega",
              "Descripcion_Pedido", "Costo_Producto", "Costo_Envio", "Metodo_Pago")
    for old in rows("PEDIDOS"):
        if not isinstance(old, dict):
            continue
        try:
            stamp = str(old.get("Fecha_Carga", "") or "").replace("Z", "+00:00")
            old_dt = datetime.fromisoformat(stamp)
            if old_dt.tzinfo is not None:
                old_dt = old_dt.replace(tzinfo=None)
            if abs((now - old_dt).total_seconds()) > segundos:
                continue
        except Exception:
            continue
        same = True
        for field in fields:
            if field in ("Nombre_Cliente", "Direccion_Entrega", "Descripcion_Pedido", "Metodo_Pago"):
                same = _normalizar_busqueda(old.get(field)) == _normalizar_busqueda(record.get(field))
            elif field == "Telefono_Cliente":
                same = _digits_phone(old.get(field)) == _digits_phone(record.get(field))
            else:
                same = str(old.get(field, "") or "") == str(record.get(field, "") or "")
            if not same:
                break
        if same:
            return True
    return False


def guardar_pedido_seguro(record):
    """Centraliza la protección contra pedidos repetidos y clientes duplicados."""
    if pedido_duplicado_reciente(record):
        st.warning("No se guardó: encontramos un pedido idéntico registrado hace muy poco. Revisá la lista de pedidos antes de volver a enviarlo.")
        return
    asegurar_cliente(record)
    save("PEDIDOS", record)


def save(sheet, record):
    result = api("save", sheet=sheet, record=record)
    if result:
        if result.get("duplicate"):
            st.warning(result.get("message", "No se guardó porque el registro ya existe."))
            return False
        st.success(result.get("message", "Guardado correctamente."))
        st.rerun()
        return True
    return False


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
    # Cabecera de marca adaptada al panel de PC; conserva las funciones y la API.
    safe_subtitle = (str(subtitle).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    st.markdown(
        '<div class="optiruta-top">'
        '<div class="optiruta-brand">Opti<span class="gold">Ruta</span>'
        '<span class="delivery">DELIVERY</span></div>'
        '<div class="optiruta-slogan">Tu ruta,<br>nuestro compromiso'
        '<small>Gestión de pedidos y entregas</small></div>'
        f'<div class="optiruta-tag">{safe_subtitle}</div>'
        '</div>',
        unsafe_allow_html=True
    )


if "user" not in st.session_state:
    st.session_state.user = None
if "portal" not in st.session_state:
    st.session_state.portal = None

# -------------------- ACCESO / INICIO --------------------
if not st.session_state.user:
    if not st.session_state.portal:
        brand_header("Plataforma de pedidos, reparto y seguimiento · PYG")
        st.title("Bienvenido a OptiRuta")
        st.write("Elegí tu perfil para ingresar al espacio de trabajo correspondiente.")
    if not st.session_state.portal:
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
        brand_header(portal_names[st.session_state.portal])
        st.subheader(portal_names[st.session_state.portal])
        st.markdown("### 🔐 Ingresá tus datos de acceso")
        with st.form("login_form", enter_to_submit=True):
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
    st.markdown('<div class="sidebar-brand">Opti<span class="gold">Ruta</span></div><div class="sidebar-caption">DELIVERY MANAGEMENT</div>', unsafe_allow_html=True)
    st.markdown('<div class="flag-blue"></div><div class="flag-gold"></div>', unsafe_allow_html=True)
    st.write("")
    st.write(f"**{user.get('Usuario', 'Usuario')}**")
    st.caption({"ADMIN":"Administración", "EMPRENDEDOR":"Portal emprendedor", "CONDUCTOR":"Portal conductor"}.get(role, role))
    if role == "ADMIN":
        st.markdown("**MENÚ PRINCIPAL**")
        st.radio(
            "Secciones", ["Resumen", "Pedidos", "Emprendedores", "Conductores", "Motos", "Caja y movimientos", "Ubicaciones", "Usuarios"],
            key="admin_section", label_visibility="collapsed"
        )
    st.divider()
    if st.button("↩ CERRAR SESIÓN", use_container_width=True):
        st.session_state.user = None
        st.session_state.portal = None
        st.rerun()

# -------------------- ADMINISTRADOR --------------------
if role == "ADMIN":
    brand_header("Panel de administración · Moneda: PYG")
    st.caption("En los formularios, usá Tab para pasar al siguiente campo y Enter dentro de los campos de texto multilínea para escribir otro renglón. En el inicio de sesión, Enter confirma el acceso.")
    section = st.session_state.get("admin_section", "Resumen")

    if section == "Resumen":
        orders = df("PEDIDOS")
        drivers = df("CONDUCTORES")
        entrepreneurs = df("EMPRENDEDORES")
        if not orders.empty and "Estado_Registro" in orders.columns:
            orders = orders[orders["Estado_Registro"].astype(str) != "Eliminado"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Pedidos registrados", len(orders))
        c2.metric("Conductores", len(drivers))
        c3.metric("Emprendedores", len(entrepreneurs))
        if not orders.empty and "Estado_Reparto" in orders.columns:
            st.subheader("Estado de los pedidos")
            counts = orders["Estado_Reparto"].fillna("Sin estado").value_counts()
            cols = st.columns(4)
            for i, state_name in enumerate(["Pendiente", "Retirado", "En ruta", "Entregado"]):
                with cols[i]:
                    st.metric(state_name, int(counts.get(state_name, 0)))
                    if st.button(f"Ver {state_name.lower()}", key=f"quick_{state_name}", use_container_width=True):
                        st.session_state["orders_filter"] = state_name
                        st.session_state["admin_section"] = "Pedidos"
                        st.rerun()
            st.bar_chart(counts)
            q1, q2 = st.columns(2)
            with q1:
                if st.button("🛵 REASIGNAR PEDIDOS", use_container_width=True):
                    st.session_state["orders_filter"] = "Todos"
                    st.session_state["admin_section"] = "Pedidos"
                    st.rerun()
            with q2:
                if st.button("＋ NUEVO PEDIDO", use_container_width=True):
                    st.session_state["orders_filter"] = "Todos"
                    st.session_state["admin_section"] = "Pedidos"
                    st.rerun()

    elif section == "Pedidos":
        st.subheader("Registrar pedido")
        entrepreneurs = rows("EMPRENDEDORES")
        drivers = rows("CONDUCTORES")
        motos = rows("MOTOS")
        st.markdown("### 🧾 Datos del nuevo pedido")
        buscar_cliente("admin_order")
        with st.form("new_order", enter_to_submit=False):
            em_options = {
                f"{x.get('Nombre_Comercial')} ({x.get('ID_Emprendedor')})": x.get("ID_Emprendedor")
                for x in entrepreneurs if x.get("Estado", "Activo") == "Activo"
            }
            em_label = st.selectbox("Emprendedor", list(em_options) or ["Sin emprendedores"])
            customer = st.text_input("Nombre del cliente", key="admin_order_customer_name")
            phone = st.text_input("Teléfono", key="admin_order_customer_phone")
            address = st.text_input("Dirección de entrega", key="admin_order_customer_address")
            maps_location = st.text_input("Ubicación de Google Maps", placeholder="Pegá el enlace compartido", key="admin_order_customer_maps")
            description = st.text_area("Descripción del pedido", height=90)
            priority = st.selectbox("Prioridad del pedido", ["Normal", "Alta", "Urgente"])
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
            transfer_status = st.selectbox("Estado de la transferencia del cliente", ["No corresponde", "Pendiente de confirmar", "Acreditada al emprendedor"], index=2 if method == "Pagado adelantado" else (1 if transfer > 0 else 0))
            payment_note = st.text_area("Acuerdo de pago conversado por WhatsApp", height=70)
            if st.form_submit_button("REGISTRAR PEDIDO", use_container_width=True):
                total = int(product_cost + shipping)
                record = {
                    "ID_Pedido": "", "Fecha_Carga": datetime.now().isoformat(timespec="seconds"),
                    "ID_Emprendedor": em_options.get(em_label, ""), "Nombre_Cliente": customer,
                    "Telefono_Cliente": phone, "Direccion_Entrega": address,
                    "Ubicacion_Google_Maps": maps_location.strip(), "Descripcion_Pedido": description,
                    "Prioridad": priority, "Costo_Producto": int(product_cost), "Costo_Envio": int(shipping), "Total_Cobrar": total,
                    "Metodo_Pago": method, "Monto_Anticipado": int(prepaid), "Monto_Efectivo_Cobrado": 0,
                    "Monto_Transferencia_Adicional": int(transfer), "Estado_Transferencia_Cliente": transfer_status,
                    "Instrucciones_Pago": payment_note, "ID_Conductor": "", "ID_Moto": "",
                    "Estado_Reparto": "Pendiente", "Fecha_Entrega": "", "Estado_Liquidacion": "Pendiente",
                    "Estado_Registro": "Activo", "Observaciones": ""
                }
                if not customer or not address:
                    st.error("Completá el nombre y la dirección.")
                else:
                    guardar_pedido_seguro(record)

        st.divider()
        st.subheader("Asignar o modificar pedidos")
        data = df("PEDIDOS")
        if not data.empty:
            if "Estado_Registro" in data.columns:
                active_data = data[data["Estado_Registro"].astype(str) != "Eliminado"].copy()
                show_deleted = st.checkbox("Mostrar pedidos eliminados", value=False)
                if show_deleted:
                    data_view = data
                else:
                    data_view = active_data
            else:
                data_view = data
            filter_options = ["Todos", "Pendiente", "Retirado", "En ruta", "Entregado", "Cancelado"]
            default_filter = st.session_state.pop("orders_filter", "Todos")
            filter_state = st.selectbox("Filtrar por estado", filter_options, index=filter_options.index(default_filter) if default_filter in filter_options else 0)
            if filter_state != "Todos" and "Estado_Reparto" in data_view.columns:
                data_view = data_view[data_view["Estado_Reparto"].astype(str) == filter_state]
            st.dataframe(data_view, use_container_width=True, hide_index=True)
            ids = data_view.get("ID_Pedido", pd.Series(dtype=str)).astype(str).tolist()
            if not ids:
                st.info("No hay pedidos para el filtro seleccionado.")
                st.stop()
            selected = st.selectbox("Pedido", ids)
            chosen = data[data["ID_Pedido"].astype(str) == str(selected)].iloc[0].to_dict() if selected else {}
            active_drivers = [d for d in drivers if d.get("Estado", "Activo") == "Activo"]
            active_motos = [m for m in motos if m.get("Estado", "Activa") == "Activa"]
            driver_map = {f"{d.get('Nombre_Completo')} ({d.get('ID_Conductor')})": d.get("ID_Conductor") for d in active_drivers}
            moto_map = {f"{m.get('Descripcion')} ({m.get('ID_Moto')})": m.get("ID_Moto") for m in active_motos}
            current_driver_label = next((k for k, v in driver_map.items() if str(v) == str(chosen.get("ID_Conductor", ""))), "")
            current_moto_label = next((k for k, v in moto_map.items() if str(v) == str(chosen.get("ID_Moto", ""))), "")
            st.markdown("### 🛵 Datos de asignación y estado")
            with st.form("assign", enter_to_submit=False):
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
            st.divider()
            st.markdown("### 🗑️ Dar de baja un pedido")
            st.caption("La baja es lógica: el pedido queda oculto de la lista habitual y conserva su historial. No se borra físicamente de la hoja.")
            confirm_delete = st.checkbox(f"Confirmo dar de baja el pedido {selected}", key=f"confirm_delete_{selected}")
            if st.button("DAR DE BAJA PEDIDO", disabled=not confirm_delete, type="secondary", use_container_width=True):
                chosen["Estado_Registro"] = "Eliminado"
                chosen["Estado_Reparto"] = "Cancelado"
                chosen["Observaciones"] = (str(chosen.get("Observaciones", "")) + " | Baja lógica por administración " + datetime.now().isoformat(timespec="seconds")).strip(" |")
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
        st.subheader("Caja y movimientos")
        st.markdown("### 🧾 Rendición y cierre de caja del conductor")
        drivers_for_cash = rows("CONDUCTORES")
        driver_cash_map = {f"{d.get('Nombre_Completo')} ({d.get('ID_Conductor')})": d.get('ID_Conductor') for d in drivers_for_cash if d.get("Estado", "Activo") == "Activo"}
        delivered = df("PEDIDOS")
        if not delivered.empty and "Estado_Reparto" in delivered.columns:
            delivered = delivered[delivered["Estado_Reparto"].astype(str) == "Entregado"].copy()
            if "Estado_Registro" in delivered.columns:
                delivered = delivered[delivered["Estado_Registro"].astype(str) != "Eliminado"]
        if not delivered.empty and "Estado_Liquidacion" in delivered.columns:
            pending_cash = delivered[delivered["Estado_Liquidacion"].astype(str).isin(["Pendiente", "", "nan"])].copy()
        else:
            pending_cash = delivered.copy()

        with st.form("driver_cash_close", enter_to_submit=False):
            driver_label = st.selectbox("Conductor que rinde", list(driver_cash_map) or [""])
            driver_id = driver_cash_map.get(driver_label, "")
            driver_orders = pending_cash[pending_cash.get("ID_Conductor", pd.Series(index=pending_cash.index, dtype=str)).astype(str) == str(driver_id)] if not pending_cash.empty else pending_cash
            st.caption("Se muestran pedidos entregados y todavía no incluidos en una liquidación.")
            if not driver_orders.empty:
                display_cols = [c for c in ["ID_Pedido", "Nombre_Cliente", "Total_Cobrar", "Metodo_Pago", "Monto_Anticipado", "Monto_Transferencia_Adicional", "Instrucciones_Pago"] if c in driver_orders.columns]
                st.dataframe(driver_orders[display_cols], use_container_width=True, hide_index=True)
                def expected_cash(row):
                    try:
                        total = float(row.get("Total_Cobrar", 0) or 0)
                        prepaid_amt = float(row.get("Monto_Anticipado", 0) or 0)
                        transfer_amt = float(row.get("Monto_Transferencia_Adicional", 0) or 0)
                        transfer_state = str(row.get("Estado_Transferencia_Cliente", ""))
                        credited_transfer = transfer_amt if transfer_state == "Acreditada al emprendedor" else 0
                        return max(0, total - prepaid_amt - credited_transfer)
                    except Exception:
                        return 0
                expected_total = int(driver_orders.apply(expected_cash, axis=1).sum())
            else:
                expected_total = 0
                st.info("Este conductor no tiene pedidos entregados pendientes de rendición.")
            st.metric("Efectivo esperado para entregar", money(expected_total))
            cash_delivered = st.number_input("Efectivo que entrega físicamente el conductor (Gs.)", min_value=0, step=1000, value=int(expected_total))
            cash_note = st.text_area("Observaciones de caja", height=70, placeholder="Diferencias, faltantes, aclaraciones...")
            close_submit = st.form_submit_button("REGISTRAR RENDICIÓN Y CERRAR CAJA", use_container_width=True, disabled=(not driver_id or driver_orders.empty))
        if close_submit:
            liquidation_id = "LIQ-" + datetime.now().strftime("%Y%m%d%H%M%S")
            order_ids = driver_orders.get("ID_Pedido", pd.Series(dtype=str)).astype(str).tolist()
            transfer_summary = []
            for _, r in driver_orders.iterrows():
                tr = int(float(r.get("Monto_Transferencia_Adicional", 0) or 0))
                if tr > 0:
                    transfer_summary.append({"ID_Pedido": str(r.get("ID_Pedido", "")), "Cliente": str(r.get("Nombre_Cliente", "")), "Transferencia_a_emprendedor": tr, "Estado": str(r.get("Estado_Transferencia_Cliente", "Pendiente de confirmar")), "Instrucciones": str(r.get("Instrucciones_Pago", ""))})
            # La estructura coincide con las columnas existentes de LIQUIDACIONES.
            # Total_Pedidos representa productos sin envío; Total_Envios queda separado.
            total_products = int(pd.to_numeric(driver_orders.get("Costo_Producto", 0), errors="coerce").fillna(0).sum()) if "Costo_Producto" in driver_orders.columns else 0
            total_shipping = int(pd.to_numeric(driver_orders.get("Costo_Envio", 0), errors="coerce").fillna(0).sum()) if "Costo_Envio" in driver_orders.columns else 0
            total_transfers = 0
            total_prepaid = int(pd.to_numeric(driver_orders.get("Monto_Anticipado", 0), errors="coerce").fillna(0).sum()) if "Monto_Anticipado" in driver_orders.columns else 0
            if "Monto_Transferencia_Adicional" in driver_orders.columns:
                for _, transfer_row in driver_orders.iterrows():
                    if str(transfer_row.get("Estado_Transferencia_Cliente", "")) == "Acreditada al emprendedor":
                        try:
                            total_transfers += int(float(transfer_row.get("Monto_Transferencia_Adicional", 0) or 0))
                        except Exception:
                            pass
            liquidation = {
                "ID_Liquidacion": liquidation_id,
                "Fecha_Hora": datetime.now().isoformat(timespec="seconds"),
                "Tipo_Liquidacion": "RENDICION_CONDUCTOR",
                "ID_Conductor": driver_id,
                "ID_Emprendedor": "",
                "Pedidos_Incluidos": ",".join(order_ids),
                "Total_Pedidos": total_products,
                "Total_Envios": total_shipping,
                "Total_Efectivo": int(expected_total),
                "Total_Transferencias": int(total_transfers),
                "Total_Anticipos": int(total_prepaid),
                "Pago_Conductor": "",
                "Pago_Emprendedor": "",
                "Ganancia_OptiRuta": "",
                "Total_Rendido": int(cash_delivered),
                "Diferencia": int(cash_delivered - expected_total),
                "Estado": "Registrada",
                "Observaciones": cash_note + (" | Transferencias: " + str(transfer_summary) if transfer_summary else "")
            }
            result = api("save", sheet="LIQUIDACIONES", record=liquidation)
            if result:
                movement_result = api("movement", record={
                    "Tipo_Movimiento": "RENDICION_CONDUCTOR",
                    "ID_Conductor": driver_id,
                    "Cuenta_Origen": "CONDUCTOR",
                    "Cuenta_Destino": "OPTIRUTA",
                    "Metodo_Pago": "Efectivo",
                    "Monto": int(cash_delivered),
                    "Efectivo_Esperado": int(expected_total),
                    "Diferencia_Caja": int(cash_delivered - expected_total),
                    "ID_Liquidacion": liquidation_id,
                    "Estado": "Registrado",
                    "Referencia": ",".join(order_ids),
                    "Fecha_Hora": datetime.now().isoformat(timespec="seconds"),
                    "Observaciones": cash_note
                })
                if movement_result:
                    for _, r in driver_orders.iterrows():
                        rec = r.to_dict()
                        rec["Estado_Liquidacion"] = "Rendido"
                        rec["ID_Liquidacion"] = liquidation_id
                        api("save", sheet="PEDIDOS", record=rec)
                    st.success(f"Rendición {liquidation_id} registrada. Revisá la diferencia de caja antes de darla por aprobada.")
                    st.rerun()
                else:
                    st.error("La liquidación se guardó, pero no se pudo registrar el movimiento de caja. Revisá antes de volver a intentar para evitar duplicados.")

        st.divider()
        st.subheader("Registrar transferencia recibida del emprendedor")
        ems = rows("EMPRENDEDORES")
        emmap = {f"{e.get('Nombre_Comercial')} ({e.get('ID_Emprendedor')})": e.get("ID_Emprendedor") for e in ems}
        with st.form("transfer_in", enter_to_submit=False):
            emlabel = st.selectbox("Emprendedor", list(emmap) or [""])
            amount = st.number_input("Monto recibido (Gs.)", min_value=0, step=1000)
            ref = st.text_input("Referencia / comprobante")
            if st.form_submit_button("REGISTRAR TRANSFERENCIA"):
                api("movement", record={"Tipo_Movimiento": "TRANSFERENCIA_ENVIO_RECIBIDA", "ID_Emprendedor": emmap.get(emlabel, ""), "Cuenta_Origen": "EMPRENDEDOR", "Cuenta_Destino": "OPTIRUTA", "Metodo_Pago": "Transferencia", "Monto": int(amount), "Estado": "Confirmado", "Referencia": ref, "Fecha_Hora": datetime.now().isoformat(timespec="seconds")})
                st.rerun()
        st.subheader("Historial de movimientos")
        st.dataframe(df("MOVIMIENTOS"), use_container_width=True, hide_index=True)
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
    brand_header("Portal privado del emprendedor · Moneda: PYG")
    st.caption("Usá Tab para pasar al siguiente campo. En descripción e instrucciones podés presionar Enter para escribir otro renglón.")
    st.title("Cargar un pedido")
    st.markdown("### 📦 Información del pedido")
    buscar_cliente("entrepreneur_order")
    with st.form("entrepreneur_order", enter_to_submit=False):
        customer = st.text_input("Nombre del cliente", key="entrepreneur_order_customer_name")
        phone = st.text_input("Teléfono", key="entrepreneur_order_customer_phone")
        address = st.text_input("Dirección de entrega", key="entrepreneur_order_customer_address")
        maps_location = st.text_input(
            "Ubicación de Google Maps (pegá el enlace compartido)",
            placeholder="https://maps.app.goo.gl/...",
            key="entrepreneur_order_customer_maps"
        )
        st.caption("En Google Maps: abrí la ubicación del cliente, tocá Compartir y copiá el enlace.")
        description = st.text_area("Descripción del pedido", height=90)
        priority = st.selectbox("Prioridad del pedido", ["Normal", "Alta", "Urgente"], help="Urgente solo para pedidos que realmente requieren atención inmediata.")
        a, b, c = st.columns(3)
        product = a.number_input("Costo del producto (Gs.)", min_value=0, step=1000)
        shipping = b.number_input("Costo del envío (Gs.)", min_value=0, step=1000)
        prepaid = c.number_input("Anticipo recibido (Gs.)", min_value=0, step=1000)
        method = st.selectbox("Método de pago acordado por WhatsApp", ["Efectivo al recibir", "Transferencia al emprendedor", "Efectivo + transferencia", "Pagado adelantado"])
        if method == "Efectivo + transferencia":
            transfer_amount = st.number_input("Monto que el cliente transferirá al emprendedor (Gs.)", min_value=0, step=1000)
        elif method in ["Transferencia al emprendedor", "Pagado adelantado"]:
            transfer_amount = int(product + shipping)
        else:
            transfer_amount = 0
        if transfer_amount > 0:
            transfer_status = st.selectbox("Estado de la transferencia", ["Pendiente de confirmar", "Acreditada al emprendedor"], help="Marcá acreditada únicamente después de verificar el ingreso en la cuenta.")
        else:
            transfer_status = "No corresponde"
        payment_note = st.text_area("Instrucciones / acuerdo conversado por WhatsApp", height=75, placeholder="Ej.: el cliente ya transfirió Gs. 20.000 al emprendedor; el resto se cobra en efectivo.")
        st.caption("El conductor no contactará al cliente. Dejá asentado el acuerdo. Solo marcá la transferencia como acreditada cuando ya verificaste el dinero.")
        if st.form_submit_button("ENVIAR PEDIDO", use_container_width=True):
            total = int(product + shipping)
            record = {
                "ID_Pedido": "", "Fecha_Carga": datetime.now().isoformat(timespec="seconds"),
                "ID_Emprendedor": uid, "Nombre_Cliente": customer, "Telefono_Cliente": phone,
                "Direccion_Entrega": address, "Ubicacion_Google_Maps": maps_location.strip(),
                "Descripcion_Pedido": description, "Prioridad": priority,
                "Costo_Producto": int(product), "Costo_Envio": int(shipping), "Total_Cobrar": total,
                "Metodo_Pago": method, "Monto_Anticipado": int(prepaid),
                "Monto_Efectivo_Cobrado": 0, "Monto_Transferencia_Adicional": int(transfer_amount),
                "Instrucciones_Pago": payment_note, "Estado_Transferencia_Cliente": transfer_status,
                "ID_Conductor": "", "ID_Moto": "", "Estado_Reparto": "Pendiente",
                "Fecha_Entrega": "", "Estado_Liquidacion": "Pendiente", "Estado_Registro": "Activo", "Observaciones": ""
            }
            if customer and address:
                guardar_pedido_seguro(record)
            else:
                st.error("Completá el nombre y la dirección.")

    st.divider()
    st.subheader("Mis pedidos")
    data = df("PEDIDOS")
    if not data.empty and "ID_Emprendedor" in data.columns:
        mine = data[data["ID_Emprendedor"].astype(str) == str(uid)].copy()
        if "Estado_Registro" in mine.columns:
            mine = mine[mine["Estado_Registro"].astype(str) != "Eliminado"]
        st.dataframe(mine, use_container_width=True, hide_index=True)

        if not mine.empty and "ID_Pedido" in mine.columns:
            st.markdown("### ✏️ Modificar un pedido")
            st.caption("Podés corregir los datos de tus pedidos que todavía no fueron entregados ni rendidos.")
            order_ids = mine["ID_Pedido"].astype(str).tolist()
            selected_order_id = st.selectbox("Elegí el pedido que querés modificar", order_ids, key="entrepreneur_edit_order_id")
            selected_rows = mine[mine["ID_Pedido"].astype(str) == str(selected_order_id)]
            if not selected_rows.empty:
                original = selected_rows.iloc[0].to_dict()
                order_state = str(original.get("Estado_Reparto", "Pendiente") or "Pendiente")
                settlement_state = str(original.get("Estado_Liquidacion", "Pendiente") or "Pendiente")
                can_edit = order_state not in ["Entregado", "Cancelado"] and settlement_state != "Rendido"

                if not can_edit:
                    st.warning("Este pedido ya fue entregado, cancelado o rendido, por lo que no se puede modificar desde este portal. Si necesitás corregirlo, contactá a administración.")
                else:
                    def edit_text(value):
                        return "" if pd.isna(value) else str(value)
                    def edit_number(value):
                        try:
                            return max(0, int(float(value or 0)))
                        except (TypeError, ValueError):
                            return 0

                    # Streamlit conserva el estado de los widgets con key entre reruns.
                    # Al cambiar el pedido, cargar explícitamente todos los valores del nuevo registro.
                    if st.session_state.get("_entrepreneur_edit_loaded_id") != str(selected_order_id):
                        st.session_state["_entrepreneur_edit_loaded_id"] = str(selected_order_id)
                        priorities = ["Normal", "Alta", "Urgente"]
                        payment_methods = ["Efectivo al recibir", "Transferencia al emprendedor", "Efectivo + transferencia", "Pagado adelantado"]
                        transfer_states = ["No corresponde", "Pendiente de confirmar", "Acreditada al emprendedor"]
                        old_priority = edit_text(original.get("Prioridad", "Normal"))
                        old_method = edit_text(original.get("Metodo_Pago", "Efectivo al recibir"))
                        old_transfer_state = edit_text(original.get("Estado_Transferencia_Cliente", "No corresponde"))
                        st.session_state["edit_customer"] = edit_text(original.get("Nombre_Cliente"))
                        st.session_state["edit_phone"] = edit_text(original.get("Telefono_Cliente"))
                        st.session_state["edit_address"] = edit_text(original.get("Direccion_Entrega"))
                        st.session_state["edit_map"] = edit_text(original.get("Ubicacion_Google_Maps"))
                        st.session_state["edit_description"] = edit_text(original.get("Descripcion_Pedido"))
                        st.session_state["edit_priority"] = old_priority if old_priority in priorities else "Normal"
                        st.session_state["edit_product"] = edit_number(original.get("Costo_Producto"))
                        st.session_state["edit_shipping"] = edit_number(original.get("Costo_Envio"))
                        st.session_state["edit_prepaid"] = edit_number(original.get("Monto_Anticipado"))
                        st.session_state["edit_method"] = old_method if old_method in payment_methods else "Efectivo al recibir"
                        st.session_state["edit_transfer"] = edit_number(original.get("Monto_Transferencia_Adicional"))
                        st.session_state["edit_transfer_state"] = old_transfer_state if old_transfer_state in transfer_states else ("Pendiente de confirmar" if edit_number(original.get("Monto_Transferencia_Adicional")) > 0 else "No corresponde")
                        st.session_state["edit_payment_note"] = edit_text(original.get("Instrucciones_Pago"))

                    with st.form("entrepreneur_edit_order_form", enter_to_submit=False):
                        edit_customer = st.text_input("Nombre del cliente", key="edit_customer")
                        edit_phone = st.text_input("Teléfono", key="edit_phone")
                        edit_address = st.text_input("Dirección de entrega", key="edit_address")
                        edit_map = st.text_input("Ubicación de Google Maps", key="edit_map")
                        edit_description = st.text_area("Descripción del pedido", height=90, key="edit_description")
                        priorities = ["Normal", "Alta", "Urgente"]
                        edit_priority = st.selectbox("Prioridad", priorities, key="edit_priority")
                        ea, eb, ec = st.columns(3)
                        edit_product = ea.number_input("Costo del producto (Gs.)", min_value=0, step=1000, key="edit_product")
                        edit_shipping = eb.number_input("Costo del envío (Gs.)", min_value=0, step=1000, key="edit_shipping")
                        edit_prepaid = ec.number_input("Anticipo recibido (Gs.)", min_value=0, step=1000, key="edit_prepaid")
                        payment_methods = ["Efectivo al recibir", "Transferencia al emprendedor", "Efectivo + transferencia", "Pagado adelantado"]
                        edit_method = st.selectbox("Método de pago acordado", payment_methods, key="edit_method")
                        old_transfer = edit_number(original.get("Monto_Transferencia_Adicional"))
                        if edit_method == "Efectivo + transferencia":
                            edit_transfer = st.number_input("Monto que el cliente transferirá al emprendedor (Gs.)", min_value=0, step=1000, value=old_transfer, key="edit_transfer")
                        elif edit_method in ["Transferencia al emprendedor", "Pagado adelantado"]:
                            edit_transfer = int(edit_product + edit_shipping)
                            st.caption("La transferencia se calcula con el total del pedido.")
                        else:
                            edit_transfer = 0
                        transfer_states = ["No corresponde", "Pendiente de confirmar", "Acreditada al emprendedor"]
                        edit_transfer_state = st.selectbox("Estado de la transferencia", transfer_states, key="edit_transfer_state")
                        edit_payment_note = st.text_area("Instrucciones / acuerdo de pago", height=75, key="edit_payment_note")
                        update_order = st.form_submit_button("GUARDAR CAMBIOS DEL PEDIDO", use_container_width=True)

                    if update_order:
                        if not edit_customer.strip() or not edit_address.strip():
                            st.error("Completá el nombre del cliente y la dirección de entrega.")
                        else:
                            updated = dict(original)
                            updated.update({
                                "Nombre_Cliente": edit_customer.strip(),
                                "Telefono_Cliente": edit_phone.strip(),
                                "Direccion_Entrega": edit_address.strip(),
                                "Ubicacion_Google_Maps": edit_map.strip(),
                                "Descripcion_Pedido": edit_description,
                                "Prioridad": edit_priority,
                                "Costo_Producto": int(edit_product),
                                "Costo_Envio": int(edit_shipping),
                                "Total_Cobrar": int(edit_product + edit_shipping),
                                "Monto_Anticipado": int(edit_prepaid),
                                "Metodo_Pago": edit_method,
                                "Monto_Transferencia_Adicional": int(edit_transfer),
                                "Estado_Transferencia_Cliente": edit_transfer_state if edit_transfer > 0 else "No corresponde",
                                "Instrucciones_Pago": edit_payment_note,
                            })
                            save("PEDIDOS", updated)
    else:
        st.info("Todavía no tenés pedidos registrados.")

# -------------------- CONDUCTOR --------------------
elif role == "CONDUCTOR":
    brand_header("Aplicación de trabajo del conductor · Moneda: PYG")
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
                    priority_value = str(order.get("Prioridad", "Normal") or "Normal")
                    if priority_value == "Urgente":
                        st.error("PRIORIDAD URGENTE")
                    elif priority_value == "Alta":
                        st.warning("PRIORIDAD ALTA")
                    if gps_ok and pd.notna(order.get("Distancia_km")) and math.isfinite(float(order.get("Distancia_km"))):
                        st.write(f"**Distancia aproximada:** {float(order.get('Distancia_km')):.1f} km")
                    saved_map_link = str(order.get("Ubicacion_Google_Maps", "") or "").strip()
                    navigation_url = saved_map_link if saved_map_link.startswith(("https://", "http://")) else maps_url(address)
                    st.link_button("ABRIR NAVEGACIÓN GPS", navigation_url, use_container_width=True)
                    if st.button("CONFIRMAR ENTREGA", key=f"del_{order_id}", use_container_width=True):
                        rec = order.drop(labels=["Distancia_km"], errors="ignore").to_dict()
                        rec["Estado_Reparto"] = "Entregado"
                        rec["Fecha_Entrega"] = datetime.now().isoformat(timespec="seconds")
                        rec["Estado_Liquidacion"] = "Pendiente"
                        save("PEDIDOS", rec)

else:
    st.error("Rol no reconocido. Contactá al administrador.")
