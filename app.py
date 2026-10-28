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
    with st.form("entrepreneur_order", enter_to_submit=False):
        customer = st.text_input("Nombre del cliente")
        phone = st.text_input("Teléfono")
        address = st.text_input("Dirección de entrega")
        maps_location = st.text_input(
            "Ubicación de Google Maps (pegá el enlace compartido)",
            placeholder="https://maps.app.goo.gl/..."
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
