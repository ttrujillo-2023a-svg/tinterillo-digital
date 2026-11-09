import streamlit as st

st.set_page_config(
    page_title="Tinterillo Digital - Asistente Legal", page_icon="⚖️", layout="centered"
)

st.title("⚖️ Tinterillo Digital")
st.markdown(
    "Tu asistente comunitario para la orientación legal y redacción de documentos básicos."
)

# Inicializar el estado de la sesión
if "step" not in st.session_state:
    st.session_state.step = "menu_principal"
if "categoria" not in st.session_state:
    st.session_state.categoria = None
if "subtipo" not in st.session_state:
    st.session_state.subtipo = None
if "documento_generado" not in st.session_state:
    st.session_state.documento_generado = False

# --- PASO 1: MENÚ PRINCIPAL ---
if st.session_state.step == "menu_principal":
    st.subheader("¿Qué tipo de problema legal o comunitario tienes?")

    if st.button("🛣️ A. Daños en la vía o infraestructura vial"):
        st.session_state.categoria = "Daños en la vía / Infraestructura"
        st.session_state.step = "formulario"
        st.rerun()

    if st.button("⚡ B. Servicios públicos (cobros o fallas)"):
        st.session_state.categoria = "Servicios Públicos"
        st.session_state.step = "formulario"
        st.rerun()

    if st.button("🏥 C. Salud y EPS (medicamentos o citas)"):
        st.session_state.categoria = "Salud y EPS"
        st.session_state.step = "formulario"
        st.rerun()

    if st.button("🏠 D. Convivencia vecinal y policía"):
        st.session_state.categoria = "Convivencia Vecinal"
        st.session_state.step = "formulario"
        st.rerun()

# --- PASO 2: FORMULARIO DE DATOS ---
elif st.session_state.step == "formulario":
    st.subheader("📝 Datos para la solicitud")
    st.info(f"Categoría seleccionada: **{st.session_state.categoria}**")

    with st.form("form_datos"):
        nombre = st.text_input("Nombre completo")
        cedula = st.text_input("Número de cédula")
        direccion = st.text_input("Dirección de notificación / correo electrónico")
        detalle_caso = st.text_area("Describa brevemente los hechos (dirección exacta, qué sucedió, fechas)")

        submitted = st.form_submit_button("Generar Borrador Legal")
        if submitted:
            if nombre and cedula and detalle_caso:
                st.session_state.nombre = nombre
                st.session_state.cedula = cedula
                st.session_state.direccion = direccion
                st.session_state.detalle_caso = detalle_caso
                st.session_state.documento_generado = True
            else:
                st.warning("Por favor completa al menos tu nombre, cédula y la descripción de los hechos.")

    # Si ya se generó el documento, lo mostramos debajo del formulario
    if st.session_state.documento_generado:
        st.success("¡Borrador generado con éxito por tu Tinterillo Digital!")

        # Construcción del documento legal formal
        borrador_texto = f"""SEÑORES:
ENTIDAD COMPETENTE (Alcaldía Municipal / Secretaría / Empresa Prestadora)
E. S. D.

REF: DERECHO DE PETICIÓN / SOLICITUD DE INTERVENCIÓN

Yo, {st.session_state.nombre}, identificado con cédula de ciudadanía número {st.session_state.cedula}, obrando en nombre propio, respetuosamente me dirijo a su despacho para presentar formal petición amparada en el Artículo 23 de la Constitución Política de Colombia, fundamentada en los siguientes:

HECHOS:
1. {st.session_state.detalle_caso}
2. La situación descrita afecta directamente a la comunidad y requiere una solución pronta por parte de las autoridades competentes.

PRETENSIONES:
1. Se sirva realizar la verificación o inspección técnica necesaria en el lugar indicado.
2. Se proceda a dar solución, arreglo o mitigación al problema expuesto dentro de los términos legales establecidos para los derechos de petición.

NOTIFICACIONES:
Recibiré notificaciones en la dirección física o correo electrónico: {st.session_state.direccion}.

Atentamente,

_________________________________
Firma: {st.session_state.nombre}
C.C. {st.session_state.cedula}
"""

        st.subheader("📄 Tu Borrador Legal:")
        st.text_area("Copia el texto o descárgalo abajo:", value=borrador_texto, height=320)

        st.download_button(
            label="📥 Descargar Borrador en Archivo de Texto",
            data=borrador_texto,
            file_name="Derecho_de_Peticion_Tinterillo.txt",
            mime="text/plain"
        )

    if st.button("🔄 Reiniciar consulta"):
        st.session_state.step = "menu_principal"
        st.session_state.documento_generado = False
        st.rerun()
