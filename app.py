import streamlit as st

st.set_page_config(
    page_title="Tinterillo Digital - Asistente Legal", page_icon="⚖️", layout="centered"
)

st.title("⚖️ Tinterillo Digital")
st.markdown(
    "Tu asistente comunitario para la orientación legal y redacción de documentos básicos."
)

# Inicializar el estado de la sesión para manejar los pasos del árbol
if "step" not in st.session_state:
    st.session_state.step = "menu_principal"
if "categoria" not in st.session_state:
    st.session_state.categoria = None
if "subtipo" not in st.session_state:
    st.session_state.subtipo = None

# --- PASO 1: MENÚ PRINCIPAL ---
if st.session_state.step == "menu_principal":
    st.subheader("¿Qué tipo de problema legal o comunitario tienes?")

    if st.button("🛣️ A. Daños en la vía o infraestructura vial"):
        st.session_state.categoria = "vias"
        st.session_state.step = "submenu_vias"
        st.rerun()

    if st.button("⚡ B. Servicios públicos (cobros o fallas)"):
        st.session_state.categoria = "servicios"
        st.session_state.step = "submenu_servicios"
        st.rerun()

    if st.button("🏥 C. Salud y EPS (medicamentos o citas)"):
        st.session_state.categoria = "salud"
        st.session_state.step = "submenu_salud"
        st.rerun()

    if st.button("🏠 D. Convivencia vecinal y policía"):
        st.session_state.categoria = "convivencia"
        st.session_state.step = "submenu_convivencia"
        st.rerun()

# --- PASO 2A: SUBMENÚ DE VÍAS ---
elif st.session_state.step == "submenu_vias":
    st.subheader("🛣️ Situación en la vía")
    if st.button("1. Hueco o riesgo preventivo (Sin daños aún)"):
        st.session_state.subtipo = "prevencion_vias"
        st.session_state.step = "formulario"
        st.rerun()
    if st.button("2. El daño causó perjuicios materiales o físicos"):
        st.session_state.subtipo = "reparacion_vias"
        st.session_state.step = "formulario"
        st.rerun()
    if st.button("🔄 Volver al menú principal"):
        st.session_state.step = "menu_principal"
        st.rerun()

# --- PASO 2B: SUBMENÚ DE SERVICIOS PÚBLICOS ---
elif st.session_state.step == "submenu_servicios":
    st.subheader("⚡ Servicios Públicos")
    if st.button("1. Cobro excesivo o facturación injustificada"):
        st.session_state.subtipo = "cobro_excesivo"
        st.session_state.step = "formulario"
        st.rerun()
    if st.button("2. Suspensión o falla continua del servicio"):
        st.session_state.subtipo = "suspension_servicio"
        st.session_state.step = "formulario"
        st.rerun()
    if st.button("3. Negación de conexión o medidor nuevo"):
        st.session_state.subtipo = "negacion_conexion"
        st.session_state.step = "formulario"
        st.rerun()
    if st.button("🔄 Volver al menú principal"):
        st.session_state.step = "menu_principal"
        st.rerun()

# --- PASO 2C: SUBMENÚ DE SALUD ---
elif st.session_state.step == "submenu_salud":
    st.subheader("🏥 Salud y EPS")
    if st.button("1. Negación o demora en entrega de medicamentos"):
        st.session_state.subtipo = "medicamentos_eps"
        st.session_state.step = "formulario"
        st.rerun()
    if st.button("2. Demora en cita con especialista o cirugía"):
        st.session_state.subtipo = "especialista_eps"
        st.session_state.step = "formulario"
        st.rerun()
    if st.button("🔄 Volver al menú principal"):
        st.session_state.step = "menu_principal"
        st.rerun()

# --- PASO 2D: SUBMENÚ DE CONVIVENCIA ---
elif st.session_state.step == "submenu_convivencia":
    st.subheader("🏠 Convivencia Vecinal y Policía")
    if st.button("1. Ruido excesivo o problemas con locales"):
        st.session_state.subtipo = "ruido_vecinal"
        st.session_state.step = "formulario"
        st.rerun()
    if st.button("2. Inconformidad con comparendo o multa de policía"):
        st.session_state.subtipo = "comparendo_policia"
        st.session_state.step = "formulario"
        st.rerun()
    if st.button("🔄 Volver al menú principal"):
        st.session_state.step = "menu_principal"
        st.rerun()

# --- PASO 3: FORMULARIO DE DATOS GENERAL ---
elif st.session_state.step == "formulario":
    st.subheader("📝 Datos para la solicitud")
    st.info(f"Categoría seleccionada: **{st.session_state.categoria}**")

    with st.form("form_datos"):
        nombre = st.text_input("Nombre completo")
        cedula = st.text_input("Número de cédula")
        direccion = st.text_input("Dirección de notificación / correo electrónico")
        detalle_caso = st.text_area("Describa brevemente los hechos (dirección exacta, fechas, qué sucedió)")

        submitted = st.form_submit_button("Generar Borrador Legal")
        if submitted:
            st.success("¡Datos recibidos con éxito! El agente ha procesado la información para tu documento.")

    if st.button("🔄 Reiniciar consulta"):
        st.session_state.step = "menu_principal"
        st.rerun()
