import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(page_title="OptiRuta Delivery", page_icon="🛵", layout="wide")

st.markdown("""
<style>
.stApp {background:#0b1220;color:#edf2f7}
[data-testid="stSidebar"] {background:#111c30}
h1,h2,h3 {color:#f5f7fb}
div.stButton>button {background:#f28c28;color:#111827;border:0;border-radius:10px;font-weight:700}
div.stButton>button:hover {background:#ffad55;color:#111827}
div[data-testid="stMetric"] {background:#14233a;padding:14px;border-radius:12px}
</style>
""", unsafe_allow_html=True)

st.title("🛵 OptiRuta Delivery")
st.caption("Centro de operaciones · Pedidos, conductores, motos y liquidaciones")

def cfg(name, default=""):
    try:
        return st.secrets[name]
    except Exception:
        return default

API_URL = cfg("API_URL")
API_KEY = cfg("API_KEY")

if not API_URL or not API_KEY:
    st.error("Falta configurar API_URL y API_KEY en los secretos de Streamlit. Consultá el manual de instalación.")
    st.stop()

def api(action, **kwargs):
    payload = {"action": action, "api_key": API_KEY, "user": st.session_state.get("user"), **kwargs}
    try:
        r = requests.post(API_URL, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "ok":
            raise RuntimeError(data.get("message", "Error desconocido del servidor"))
        return data
    except Exception as e:
        st.error(f"No se pudo comunicar con Google Sheets: {e}")
        return None

def money(value):
    try:
        return "Gs. " + f"{int(float(value or 0)):,}".replace(",", ".")
    except Exception:
        return "Gs. 0"

if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    with st.container():
        st.subheader("Ingresar a OptiRuta")
        with st.form("login"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            ok = st.form_submit_button("Ingresar", use_container_width=True)
        if ok:
            result = api("login", username=username.strip(), password=password)
            if result and result.get("user"):
                st.session_state.user = result["user"]
                st.rerun()
            elif result:
                st.error("Usuario o contraseña incorrectos, o cuenta inactiva.")
    st.info("Acceso inicial del administrador: usuario **admin**, contraseña **1234**. Cambiala después del primer ingreso.")
    st.stop()

user = st.session_state.user
role = user.get("Rol", "")
uid = user.get("ID_Referencia", "")
with st.sidebar:
    st.markdown("### OPTIRUTA")
    st.write(f"**{user.get('Usuario')}**")
    st.caption(role.upper())
    if st.button("Cerrar sesión", use_container_width=True):
        st.session_state.user = None
        st.rerun()

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

def status_badge(value):
    st.write(f"**Estado:** {value or 'Pendiente'}")

if role == "ADMIN":
    tabs = st.tabs(["Resumen", "Pedidos", "Emprendedores", "Conductores", "Motos", "Caja y movimientos", "Ubicaciones", "Usuarios"])
    with tabs[0]:
        orders = df("PEDIDOS")
        drivers = df("CONDUCTORES")
        entrepreneurs = df("EMPRENDEDORES")
        c1,c2,c3 = st.columns(3)
        c1.metric("Pedidos registrados", len(orders))
        c2.metric("Conductores", len(drivers))
        c3.metric("Emprendedores", len(entrepreneurs))
        if not orders.empty and "Estado_Reparto" in orders:
            st.subheader("Estado de los pedidos")
            st.bar_chart(orders["Estado_Reparto"].fillna("Sin estado").value_counts())
        st.caption("Los indicadores se actualizan leyendo la base de Google Sheets.")
    with tabs[1]:
        st.subheader("Crear pedido")
        entrepreneurs = rows("EMPRENDEDORES")
        drivers = rows("CONDUCTORES")
        motos = rows("MOTOS")
        with st.form("new_order"):
            em_options = {f"{x.get('Nombre_Comercial')} ({x.get('ID_Emprendedor')})": x.get("ID_Emprendedor") for x in entrepreneurs if x.get("Estado","Activo") == "Activo"}
            em_label = st.selectbox("Emprendedor", list(em_options) or ["Sin emprendedores"])
            customer = st.text_input("Nombre del cliente")
            phone = st.text_input("Teléfono")
            address = st.text_input("Dirección de entrega")
            description = st.text_input("Descripción del pedido")
            a,b,c = st.columns(3)
            product_cost = a.number_input("Costo del producto (Gs.)", min_value=0, step=1000)
            shipping = b.number_input("Costo del envío (Gs.)", min_value=0, value=15000, step=1000)
            prepaid = c.number_input("Anticipo ya pagado (Gs.)", min_value=0, step=1000)
            method = st.selectbox("Pago del cliente", ["Efectivo", "Transferencia al emprendedor", "Efectivo + transferencia", "Pagado adelantado"])
            if method == "Efectivo + transferencia":
                transfer = st.number_input("Parte transferida al emprendedor (Gs.)", min_value=0, step=1000)
            elif method == "Transferencia al emprendedor" or method == "Pagado adelantado":
                transfer = int(product_cost + shipping)
            else:
                transfer = 0
            if st.form_submit_button("Registrar pedido", use_container_width=True):
                total = int(product_cost + shipping)
                record = {
                    "ID_Pedido": "", "Fecha_Carga": datetime.now().isoformat(timespec="seconds"),
                    "ID_Emprendedor": em_options.get(em_label,""), "Nombre_Cliente": customer,
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
        st.subheader("Pedidos registrados")
        data = df("PEDIDOS")
        if not data.empty:
            st.dataframe(data, use_container_width=True, hide_index=True)
            ids = data.get("ID_Pedido", pd.Series(dtype=str)).astype(str).tolist()
            selected = st.selectbox("Seleccionar pedido para asignar o modificar", ids)
            chosen = data[data["ID_Pedido"].astype(str) == str(selected)].iloc[0].to_dict() if selected else {}
            active_drivers = [d for d in drivers if d.get("Estado","Activo") == "Activo"]
            active_motos = [m for m in motos if m.get("Estado","Activa") == "Activa"]
            with st.form("assign"):
                driver_map = {f"{d.get('Nombre_Completo')} ({d.get('ID_Conductor')})": d.get("ID_Conductor") for d in active_drivers}
                moto_map = {f"{m.get('Descripcion')} ({m.get('ID_Moto')})": m.get("ID_Moto") for m in active_motos}
                dl = st.selectbox("Conductor", [""] + list(driver_map), index=0)
                ml = st.selectbox("Moto", [""] + list(moto_map), index=0)
                state = st.selectbox("Estado", ["Pendiente","Retirado","En ruta","Entregado","Cancelado"])
                if st.form_submit_button("Guardar asignación"):
                    chosen["ID_Conductor"] = driver_map.get(dl, chosen.get("ID_Conductor",""))
                    chosen["ID_Moto"] = moto_map.get(ml, chosen.get("ID_Moto",""))
                    chosen["Estado_Reparto"] = state
                    if state == "Entregado":
                        chosen["Fecha_Entrega"] = datetime.now().isoformat(timespec="seconds")
                    save("PEDIDOS", chosen)
        else:
            st.info("Todavía no hay pedidos.")
    with tabs[2]:
        st.subheader("Emprendedores")
        with st.form("entrepreneur"):
            name = st.text_input("Nombre comercial")
            phone = st.text_input("Teléfono de contacto")
            address = st.text_input("Dirección")
            fee = st.number_input("Tarifa base de envío (Gs.)", min_value=0, value=15000, step=1000)
            if st.form_submit_button("Agregar emprendedor"):
                save("EMPRENDEDORES", {"ID_Emprendedor":"","Nombre_Comercial":name,"Telefono":phone,"Direccion":address,"Tarifa_Envio_Base":int(fee),"Estado":"Activo","Observaciones":""})
        st.dataframe(df("EMPRENDEDORES"), use_container_width=True, hide_index=True)
    with tabs[3]:
        st.subheader("Conductores")
        with st.form("driver"):
            name = st.text_input("Nombre completo")
            phone = st.text_input("Teléfono", key="driver_phone")
            if st.form_submit_button("Agregar conductor"):
                save("CONDUCTORES", {"ID_Conductor":"","Nombre_Completo":name,"Telefono":phone,"Estado":"Activo","Fecha_Ingreso":datetime.now().date().isoformat(),"Fecha_Baja":"","Observaciones":""})
        st.dataframe(df("CONDUCTORES"), use_container_width=True, hide_index=True)
    with tabs[4]:
        st.subheader("Motos")
        with st.form("bike"):
            desc = st.text_input("Descripción / modelo")
            plate = st.text_input("Patente")
            ownership = st.selectbox("Propiedad", ["OPTIRUTA","CONDUCTOR"])
            owner = st.text_input("Propietario (si es del conductor)")
            if st.form_submit_button("Agregar moto"):
                save("MOTOS", {"ID_Moto":"","Descripcion":desc,"Patente":plate,"Propiedad":ownership,"Propietario":owner,"Conductor_Asignado":"","Estado":"Activa","Observaciones":""})
        st.dataframe(df("MOTOS"), use_container_width=True, hide_index=True)
    with tabs[5]:
        st.subheader("Movimientos y liquidaciones")
        st.dataframe(df("MOVIMIENTOS"), use_container_width=True, hide_index=True)
        st.subheader("Registrar transferencia recibida del emprendedor")
        ems = rows("EMPRENDEDORES")
        emmap = {f"{e.get('Nombre_Comercial')} ({e.get('ID_Emprendedor')})":e.get("ID_Emprendedor") for e in ems}
        with st.form("transfer_in"):
            emlabel = st.selectbox("Emprendedor", list(emmap) or [""])
            amount = st.number_input("Monto recibido (Gs.)", min_value=0, step=1000)
            ref = st.text_input("Referencia / comprobante")
            if st.form_submit_button("Registrar transferencia"):
                api("movement", record={"Tipo_Movimiento":"TRANSFERENCIA_ENVIO_RECIBIDA","ID_Emprendedor":emmap.get(emlabel,""),"Cuenta_Origen":"EMPRENDEDOR","Cuenta_Destino":"OPTIRUTA","Metodo_Pago":"Transferencia","Monto":int(amount),"Estado":"Confirmado","Referencia":ref,"Fecha_Hora":datetime.now().isoformat(timespec="seconds")})
                st.rerun()
        st.subheader("Liquidaciones guardadas")
        st.dataframe(df("LIQUIDACIONES"), use_container_width=True, hide_index=True)
    with tabs[6]:
        st.subheader("Últimas ubicaciones")
        loc = df("UBICACIONES")
        if not loc.empty:
            st.dataframe(loc.sort_values("Fecha_Hora", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("Todavía no hay ubicaciones registradas.")
    with tabs[7]:
        st.subheader("Crear acceso")
        with st.form("user_create"):
            uname = st.text_input("Usuario nuevo")
            pwd = st.text_input("Contraseña inicial", type="password")
            urole = st.selectbox("Rol", ["EMPRENDEDOR","CONDUCTOR"])
            refid = st.text_input("ID de emprendedor o conductor")
            if st.form_submit_button("Crear usuario"):
                result = api("create_user", username=uname, password=pwd, role=urole, reference_id=refid)
                if result: st.success("Usuario creado.")
        st.info("Los usuarios nuevos deben estar vinculados a un registro activo de EMPRENDEDORES o CONDUCTORES.")

elif role == "EMPRENDEDOR":
    st.subheader("Mis pedidos")
    with st.form("entrepreneur_order"):
        customer = st.text_input("Nombre del cliente")
        phone = st.text_input("Teléfono")
        address = st.text_input("Dirección de entrega")
        description = st.text_input("Descripción del pedido")
        a,b,c = st.columns(3)
        product = a.number_input("Costo del producto (Gs.)", min_value=0, step=1000)
        shipping = b.number_input("Costo del envío (Gs.)", min_value=0, step=1000)
        prepaid = c.number_input("Anticipo recibido por el emprendedor (Gs.)", min_value=0, step=1000)
        method = st.selectbox("Método de pago", ["Efectivo al recibir","Transferencia al emprendedor","Efectivo + transferencia","Pagado adelantado"])
        if st.form_submit_button("Enviar pedido"):
            total = int(product + shipping)
            record = {"ID_Pedido":"","Fecha_Carga":datetime.now().isoformat(timespec="seconds"),"ID_Emprendedor":uid,"Nombre_Cliente":customer,"Telefono_Cliente":phone,"Direccion_Entrega":address,"Descripcion_Pedido":description,"Costo_Producto":int(product),"Costo_Envio":int(shipping),"Total_Cobrar":total,"Metodo_Pago":method,"Monto_Anticipado":int(prepaid),"Monto_Efectivo_Cobrado":0,"Monto_Transferencia_Adicional":0,"ID_Conductor":"","ID_Moto":"","Estado_Reparto":"Pendiente","Fecha_Entrega":"","Estado_Liquidacion":"Pendiente","Observaciones":""}
            if customer and address: save("PEDIDOS", record)
            else: st.error("Completá nombre y dirección.")
    data = df("PEDIDOS")
    if not data.empty and "ID_Emprendedor" in data:
        st.dataframe(data[data["ID_Emprendedor"].astype(str)==str(uid)], use_container_width=True, hide_index=True)

elif role == "CONDUCTOR":
    st.subheader("Mis entregas")
    data = df("PEDIDOS")
    if not data.empty and "ID_Conductor" in data:
        mine = data[(data["ID_Conductor"].astype(str)==str(uid)) & (data["Estado_Reparto"].isin(["Retirado","En ruta","Pendiente"]))]
        if mine.empty:
            st.info("No tenés pedidos asignados.")
        for _, order in mine.iterrows():
            with st.container(border=True):
                st.markdown(f"### Paquete {order.get('ID_Pedido')}")
                st.write("**Dirección:**", order.get("Direccion_Entrega"))
                st.write("**Monto a cobrar:**", money(order.get("Total_Cobrar")))
                st.write("**Estado:**", order.get("Estado_Reparto"))
                if st.button("Confirmar entrega", key=f"del_{order.get('ID_Pedido')}"):
                    record = order.to_dict()
                    record["Estado_Reparto"] = "Entregado"
                    record["Fecha_Entrega"] = datetime.now().isoformat(timespec="seconds")
                    record["Estado_Liquidacion"] = "Pendiente"
                    save("PEDIDOS", record)
        st.divider()
        st.subheader("Compartir ubicación")
        try:
            position = streamlit_geolocation()
            if position and position.get("latitude") is not None:
                api("location", record={"ID_Conductor":uid,"ID_Moto":"","Fecha_Hora":datetime.now().isoformat(timespec="seconds"),"Latitud":position["latitude"],"Longitud":position["longitude"],"Precision":position.get("accuracy",""),"Estado_GPS":"Activo"})
                st.success("Ubicación enviada.")
        except Exception:
            st.warning("No se pudo acceder al GPS. Permití la ubicación en el navegador y volvé a intentar.")
    else:
        st.info("No hay pedidos asignados.")
else:
    st.error("Rol no reconocido. Contactá al administrador.")

