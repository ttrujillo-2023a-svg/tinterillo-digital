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

# --- PASO 1: MENÚ PRINCIPAL ---
if st.session_state.step == "menu_principal":
    st.subheader("¿Qué tipo de problema legal o comunitario tienes?")

    # Usando botones interactivos para evitar texto libre
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

# --- PASO 2: SUBMENÚ DE VÍAS (Ejemplo) ---
elif st.session_state.step == "submenu_vias":
    st.subheader("🛣️ Situación en la vía")
    st.markdown("Selecciona el estado exacto del problema:")

    if st.button("1. Hay un hueco o riesgo preventivo (Sin daños aún)"):
        st.session_state.subtipo = "prevencion"
        st.session_state.step = "formulario"
        st.rerun()

    if st.button("2. El estado de la vía causó un daño material o físico"):
        st.session_state.subtipo = "reparacion"
        st.session_state.step = "formulario"
        st.rerun()

    if st.button("🔄 Volver al menú principal"):
        st.session_state.step = "menu_principal"
        st.rerun()

# --- PASO 3: FORMULARIO DE DATOS ---
elif st.session_state.step == "formulario":
    st.subheader("📝 Datos para la solicitud")

    with st.form("form_datos"):
        nombre = st.text_input("Nombre completo")
        cedula = st.text_input("Número de cédula")
        direccion = st.text_input(
            "Dirección de notificación / correo electrónico"
        )
        ubicacion_hecho = st.text_input(
            "Dirección exacta o referencia del daño en la vía"
        )

        submitted = st.form_submit_button("Generar Borrador Legal")
        if submitted:
            st.success(
                "¡Datos recibidos con éxito! Aquí se conectaría la IA para redactar el documento."
            )
            # Aquí llamarías a la función de python-docx para generar el archivo

    if st.button("🔄 Reiniciar consulta"):
        st.session_state.step = "menu_principal"
        st.rerun()