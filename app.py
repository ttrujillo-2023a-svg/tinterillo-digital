# -*- coding: utf-8 -*-
"""
TINTERILLO DIGITAL - Orientación legal comunitaria y preventiva (Colombia)
Aplicación Streamlit basada en botones y estados (st.session_state).

Flujo:
  menu -> submenu -> asesoria -> formulario -> documento

Ejecutar en local:   streamlit run app.py
Despliegue:          Streamlit Community Cloud (repositorio GitHub con app.py + requirements.txt)
"""

import re
from datetime import date
from io import BytesIO

import streamlit as st

# python-docx es opcional: si no está instalado, solo se ofrece la descarga en .txt
try:
    from docx import Document
    DOCX_DISPONIBLE = True
except ImportError:
    DOCX_DISPONIBLE = False


# =============================================================================
# 1. CONFIGURACIÓN GENERAL DE LA PÁGINA
# =============================================================================
st.set_page_config(
    page_title="Tinterillo Digital",
    page_icon="⚖️",
    layout="centered",
)

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

AVISO_LEGAL = (
    "Esta herramienta ofrece **orientación general y educativa**; no reemplaza a un abogado "
    "ni a un consultorio jurídico. Las normas y los plazos pueden cambiar: verifica siempre "
    "la información vigente. Tus datos NO se guardan: solo viven en esta sesión del navegador."
)


# =============================================================================
# 2. CATÁLOGO DE CATEGORÍAS (MENÚ PRINCIPAL Y SUBMENÚS)
# =============================================================================
CATEGORIAS = {
    "A": {
        "icono": "🛣️",
        "nombre": "Daños en la vía o infraestructura vial",
        "detalle": "Huecos, postes caídos, fallas.",
        "subs": ["A1", "A2"],
    },
    "B": {
        "icono": "💡",
        "nombre": "Servicios públicos",
        "detalle": "Cobros excesivos o cortes injustificados.",
        "subs": ["B1", "B2"],
    },
    "C": {
        "icono": "🏥",
        "nombre": "Salud y EPS",
        "detalle": "Medicamentos, citas con especialistas o cirugías.",
        "subs": ["C1", "C2", "C3"],
    },
    "D": {
        "icono": "🏘️",
        "nombre": "Convivencia vecinal y policía",
        "detalle": "Problemas de ruido o comparendos.",
        "subs": ["D1", "D2"],
    },
}


# =============================================================================
# 3. CATÁLOGO DE CASOS (ASESORÍA PEDAGÓGICA + PLANTILLA DEL DOCUMENTO)
#    Cada caso contiene todo lo necesario para la "Cápsula de Asesoría Legal"
#    y para construir el borrador formal.
# =============================================================================
CASOS = {
    # ------------------------------------------------------------------ A1
    "A1": {
        "titulo": "Hueco o riesgo preventivo en la vía",
        "tipo": "Derecho de Petición de Interés General",
        "plazo": "15 días hábiles",
        "silencio": (
            "Si la entidad no responde a tiempo (omisión), se vulnera tu derecho de petición. "
            "Podrás escalar interponiendo una **Acción de Tutela** (no necesitas abogado) o "
            "poniendo una queja ante la **Personería Municipal**."
        ),
        "destino": "Secretaría de Infraestructura (o dependencia de obras públicas) de la Alcaldía Municipal",
        "destino_nota": (
            "Se radica en la **ventanilla única / oficina de correspondencia** de la Alcaldía. "
            "Si la vía es departamental o nacional, la petición va a la Gobernación o al INVÍAS/ANI; "
            "si te equivocas de entidad, esta debe remitirla a la competente e informarte (Ley 1755 de 2015)."
        ),
        "entidad_label": "Municipio o Alcaldía (opcional)",
        "entidad_requerida": False,
        "dependencia": "Secretaría de Infraestructura",
        "destino_default": "Alcaldía Municipal\nSecretaría de Infraestructura",
        "asunto": "Derecho de petición de interés general - Hueco / riesgo en la vía pública",
        "intro": (
            "en ejercicio del derecho fundamental de petición consagrado en el artículo 23 de la "
            "Constitución Política y desarrollado por la Ley 1755 de 2015, presento PETICIÓN DE "
            "INTERÉS GENERAL"
        ),
        "solicitudes": [
            "Realizar una visita técnica al sitio descrito en los hechos para verificar el estado de la vía.",
            "Ordenar la reparación y/o señalización preventiva inmediata del daño, dado el riesgo para peatones y conductores.",
            "Informarme por escrito las acciones adoptadas y el cronograma estimado de intervención.",
            "En caso de no ser competentes, remitir esta petición a la entidad competente e informarme de ello dentro de los términos de ley.",
        ],
        "fundamentos": (
            "- Artículo 23 de la Constitución Política (derecho de petición).\n"
            "- Ley 1755 de 2015 (regula el derecho de petición): respuesta de fondo, clara y oportuna dentro de 15 días hábiles.\n"
            "- Artículo 2 de la Constitución Política: las autoridades están instituidas para proteger la vida y bienes de los residentes."
        ),
        "anexos": [
            "Fotografías del daño (con fecha, si es posible).",
            "Ubicación exacta (dirección, barrio, puntos de referencia).",
            "Fotocopia de la cédula de ciudadanía.",
        ],
        "tengo_a_mano": "Fotos del daño, dirección exacta y puntos de referencia.",
    },
    # ------------------------------------------------------------------ A2
    "A2": {
        "titulo": "Daño material o físico causado por el estado de la vía",
        "tipo": "Reclamación administrativa de perjuicios (petición de indemnización)",
        "plazo": "15 días hábiles para que la entidad responda tu reclamación",
        "silencio": (
            "Si no responde o te niega la indemnización, la vía se alarga: puedes pedir una **conciliación "
            "extrajudicial ante la Procuraduría** y, si no hay acuerdo, presentar una demanda de "
            "**reparación directa** ante la jurisdicción contencioso-administrativa. Ojo: esa demanda "
            "tiene un plazo de **caducidad de 2 años** desde que ocurrió el daño. La tutela sirve para "
            "obligar a que te respondan, pero **no** para ordenar el pago de la indemnización."
        ),
        "destino": "Alcaldía Municipal - Secretaría de Infraestructura con copia a la Oficina Jurídica / Secretaría General",
        "destino_nota": (
            "Se radica en la **ventanilla única** de la Alcaldía (o de la entidad dueña de la vía). "
            "Si el daño fue grande (por ejemplo, un accidente con lesiones o un costo alto), busca un "
            "abogado o el **consultorio jurídico de una universidad**, que suele atender gratis."
        ),
        "entidad_label": "Municipio o Alcaldía (opcional)",
        "entidad_requerida": False,
        "dependencia": "Secretaría de Infraestructura / Oficina Jurídica",
        "destino_default": "Alcaldía Municipal\nSecretaría de Infraestructura - Oficina Jurídica",
        "asunto": "Reclamación administrativa por perjuicios causados por el mal estado de la vía",
        "intro": (
            "en ejercicio del derecho de petición (artículo 23 de la Constitución Política y Ley 1755 de 2015), "
            "presento RECLAMACIÓN ADMINISTRATIVA por los perjuicios que sufrí debido al mal estado de la vía pública"
        ),
        "solicitudes": [
            "Reconocer que el daño descrito en los hechos se originó en el mal estado o la falta de mantenimiento/señalización de la vía.",
            "Indemnizarme por los perjuicios materiales causados, según las facturas, cotizaciones y demás pruebas que anexo.",
            "Informarme por escrito el trámite y el plazo en que se realizará el pago, o los motivos de la negativa.",
            "Reparar y/o señalizar el punto de la vía para evitar que otras personas sufran daños similares.",
        ],
        "fundamentos": (
            "- Artículo 90 de la Constitución Política: el Estado responde patrimonialmente por los daños antijurídicos que le sean imputables.\n"
            "- Artículo 23 de la Constitución Política y Ley 1755 de 2015 (derecho de petición).\n"
            "- Ley 1437 de 2011 (CPACA): medio de control de reparación directa y requisito de conciliación previa."
        ),
        "anexos": [
            "Fotografías y videos del daño y del lugar de los hechos.",
            "Facturas, cotizaciones o informe técnico del taller/médico (según el daño).",
            "Informe de tránsito o denuncia, si existe.",
            "Datos de testigos (nombre y teléfono), si los hay.",
            "Tarjeta de propiedad del vehículo o documento que acredite el bien afectado.",
            "Fotocopia de la cédula de ciudadanía.",
        ],
        "tengo_a_mano": "Fotos, facturas o cotizaciones, informe de tránsito (si hay) y datos de testigos.",
    },
    # ------------------------------------------------------------------ B1
    "B1": {
        "titulo": "Cobro excesivo en la factura",
        "tipo": "Reclamo (PQR) con recurso de reposición y apelación en subsidio (Ley 142 de 1994)",
        "plazo": "15 días hábiles",
        "silencio": (
            "En servicios públicos domiciliarios, si la empresa no responde dentro del plazo, "
            "opera el **silencio administrativo positivo**: se entiende resuelto a tu favor. "
            "Si te la niegan, puedes apelar ante la **Superintendencia de Servicios Públicos "
            "Domiciliarios (SSPD)**. También puedes pedir apoyo a la Personería Municipal."
        ),
        "destino": "La empresa prestadora del servicio - Oficina de Peticiones, Quejas y Reclamos (PQR)",
        "destino_nota": (
            "Se radica en la **oficina de atención al usuario** de la empresa (acueducto, energía, gas, aseo) "
            "o por su canal oficial de PQR. Presenta el reclamo **cuanto antes** (por regla general dentro de "
            "los 5 meses siguientes a la factura) y **paga la parte que no discutes**, porque eso suele "
            "ser requisito para que te tramiten el recurso."
        ),
        "entidad_label": "Nombre de la empresa prestadora (ej. empresa de acueducto o energía)",
        "entidad_requerida": True,
        "dependencia": "Oficina de Peticiones, Quejas y Reclamos (PQR)",
        "destino_default": "Empresa prestadora del servicio público\nOficina de PQR",
        "asunto": "Reclamo por cobro excesivo en la facturación - Recurso de reposición y apelación en subsidio",
        "intro": (
            "en mi calidad de usuario del servicio y en ejercicio del derecho de petición (artículo 23 de la "
            "Constitución Política), presento RECLAMO por facturación y, en subsidio, interpongo RECURSO DE "
            "REPOSICIÓN Y APELACIÓN conforme a la Ley 142 de 1994"
        ),
        "solicitudes": [
            "Revisar la facturación del periodo señalado en los hechos y verificar la lectura del medidor y el consumo real.",
            "Corregir la factura y ajustar el valor cobrado, aplicando los valores a mi favor en la siguiente facturación.",
            "Abstenerse de suspender o cortar el servicio mientras se resuelve este reclamo, respecto de los valores discutidos.",
            "Enviarme por escrito la respuesta de fondo, con el detalle de la revisión técnica realizada.",
            "En subsidio, y si la decisión me es desfavorable, dar trámite al recurso de apelación ante la Superintendencia de Servicios Públicos Domiciliarios.",
        ],
        "fundamentos": (
            "- Ley 142 de 1994 (régimen de servicios públicos domiciliarios): derecho a presentar peticiones, quejas y recursos; respuesta en 15 días hábiles y silencio administrativo positivo.\n"
            "- Artículo 23 de la Constitución Política y Ley 1755 de 2015 (derecho de petición).\n"
            "- Facturación basada en consumos reales y debidamente medidos."
        ),
        "anexos": [
            "Copia de la factura(s) reclamada(s).",
            "Copia de facturas anteriores para comparar el consumo.",
            "Fotografía de la lectura del medidor (si aplica).",
            "Comprobante de pago de la parte no discutida.",
            "Fotocopia de la cédula de ciudadanía.",
        ],
        "tengo_a_mano": "La factura reclamada, facturas anteriores, número de contrato/cuenta y foto del medidor.",
    },
    # ------------------------------------------------------------------ B2
    "B2": {
        "titulo": "Corte o suspensión injustificada del servicio",
        "tipo": "Reclamo (PQR) y solicitud de reconexión (Ley 142 de 1994)",
        "plazo": "15 días hábiles (pero si el corte afecta tu salud, el agua o a menores/adultos mayores, puedes ir directo a tutela)",
        "silencio": (
            "Si la empresa no responde, opera el **silencio administrativo positivo** previsto en la Ley 142. "
            "Si el corte es grave o urgente (por ejemplo, afecta el agua potable o la salud), puedes "
            "presentar una **Acción de Tutela** sin esperar los 15 días. También puedes quejarte ante la "
            "**SSPD** y la **Personería Municipal**."
        ),
        "destino": "La empresa prestadora del servicio - Oficina de PQR (con copia a la SSPD si es necesario)",
        "destino_nota": (
            "Se radica en la **oficina de atención al usuario** de la empresa o por su canal oficial. "
            "Pide que te den un **número de radicado** y guarda la constancia."
        ),
        "entidad_label": "Nombre de la empresa prestadora (ej. empresa de acueducto o energía)",
        "entidad_requerida": True,
        "dependencia": "Oficina de Peticiones, Quejas y Reclamos (PQR)",
        "destino_default": "Empresa prestadora del servicio público\nOficina de PQR",
        "asunto": "Reclamo por suspensión/corte injustificado del servicio y solicitud de reconexión inmediata",
        "intro": (
            "en mi calidad de usuario del servicio y en ejercicio del derecho de petición (artículo 23 de la "
            "Constitución Política), presento RECLAMO por la suspensión o corte injustificado del servicio, "
            "conforme a la Ley 142 de 1994"
        ),
        "solicitudes": [
            "Restablecer de manera inmediata el servicio público suspendido o cortado en mi inmueble.",
            "Informarme por escrito el motivo exacto del corte y la fecha y forma en que se me notificó previamente.",
            "Verificar que no existan valores pendientes mal liquidados o reclamos en trámite que impidan el corte.",
            "Abstenerse de cobrar cargos de reconexión si se demuestra que el corte fue injustificado.",
            "Dar respuesta de fondo dentro del término legal y, en subsidio, dar trámite al recurso de apelación ante la SSPD.",
        ],
        "fundamentos": (
            "- Ley 142 de 1994: causales y requisitos de la suspensión y el corte; derecho a reclamar y a recurrir; silencio administrativo positivo.\n"
            "- Artículo 23 de la Constitución Política y Ley 1755 de 2015 (derecho de petición).\n"
            "- Los servicios públicos domiciliarios están ligados a la dignidad humana y, en el caso del agua, a derechos fundamentales."
        ),
        "anexos": [
            "Copia de la factura(s) reciente(s) y comprobantes de pago.",
            "Aviso de corte o suspensión, si lo recibiste.",
            "Fotos o evidencias del corte (con fecha).",
            "Fotocopia de la cédula de ciudadanía.",
        ],
        "tengo_a_mano": "Facturas, comprobantes de pago, número de contrato/cuenta y evidencia del corte.",
    },
    # ------------------------------------------------------------------ C1
    "C1": {
        "titulo": "Negación o demora en la entrega de medicamentos",
        "tipo": "Derecho de Petición a la EPS (con copia a la Superintendencia de Salud)",
        "plazo": "15 días hábiles (si hay riesgo para tu vida o salud, no tienes que esperar: puedes ir directo a tutela)",
        "silencio": (
            "Si la EPS no responde o sigue sin entregarte el medicamento, se vulneran tu derecho de petición "
            "y tu derecho a la salud. Puedes presentar una **Acción de Tutela** (sin abogado), una queja ante "
            "la **Superintendencia Nacional de Salud** y pedir apoyo a la **Personería Municipal** o la **Defensoría del Pueblo**."
        ),
        "destino": "Tu EPS - Oficina de Atención al Usuario / Gerencia (con copia a la Superintendencia Nacional de Salud)",
        "destino_nota": (
            "Se radica en la **oficina de atención al usuario** de tu EPS o por su canal oficial de PQRS. "
            "Pide siempre el **número de radicado** y una copia sellada."
        ),
        "entidad_label": "Nombre de tu EPS",
        "entidad_requerida": True,
        "dependencia": "Oficina de Atención al Usuario / Gerencia",
        "destino_default": "EPS\nOficina de Atención al Usuario",
        "asunto": "Derecho de petición - Entrega de medicamentos formulados",
        "intro": (
            "en ejercicio del derecho fundamental de petición (artículo 23 de la Constitución Política y "
            "Ley 1755 de 2015) y en defensa de mi derecho fundamental a la salud (Ley 1751 de 2015), "
            "presento la siguiente PETICIÓN"
        ),
        "solicitudes": [
            "Autorizar y entregar de manera inmediata los medicamentos formulados por mi médico tratante, en la cantidad y periodicidad ordenadas.",
            "Informarme por escrito el lugar, la fecha y la hora exactos de entrega; si no hay existencias, indicarme la fecha cierta de entrega y garantizar el suministro sin costo adicional.",
            "Si se niega la entrega, explicarme por escrito los motivos y las normas en que se basa la negativa.",
            "Abstenerse de imponerme trámites o cobros no autorizados por la ley para acceder al medicamento.",
        ],
        "fundamentos": (
            "- Artículo 49 de la Constitución Política y Ley 1751 de 2015 (Estatutaria de Salud): la salud es un derecho fundamental.\n"
            "- Artículo 23 de la Constitución Política y Ley 1755 de 2015 (derecho de petición).\n"
            "- Las EPS deben garantizar entrega oportuna de los medicamentos ordenados por el médico tratante."
        ),
        "anexos": [
            "Fórmula médica vigente.",
            "Historia clínica o resumen que soporte el diagnóstico (si la tienes).",
            "Constancia o evidencia de la negación o demora (tirilla de 'pendiente', respuesta escrita, pantallazo).",
            "Copia del carné de afiliación a la EPS.",
            "Fotocopia de la cédula de ciudadanía.",
        ],
        "tengo_a_mano": "Fórmula médica, constancia de que no te entregaron el medicamento y número de afiliación.",
    },
    # ------------------------------------------------------------------ C2
    "C2": {
        "titulo": "Demora o negación de cita con especialista",
        "tipo": "Derecho de Petición a la EPS (con copia a la Superintendencia de Salud)",
        "plazo": "15 días hábiles (si tu salud está en riesgo, puedes ir directo a tutela)",
        "silencio": (
            "Si la EPS no responde o no te asigna la cita, puedes presentar una **Acción de Tutela** "
            "(sin abogado), una queja ante la **Superintendencia Nacional de Salud** y acudir a la "
            "**Personería Municipal** o la **Defensoría del Pueblo**."
        ),
        "destino": "Tu EPS - Oficina de Atención al Usuario / Gerencia (con copia a la Superintendencia Nacional de Salud)",
        "destino_nota": (
            "Se radica en la **oficina de atención al usuario** de tu EPS o por su canal oficial de PQRS. "
            "Guarda el **número de radicado** y la copia sellada."
        ),
        "entidad_label": "Nombre de tu EPS",
        "entidad_requerida": True,
        "dependencia": "Oficina de Atención al Usuario / Gerencia",
        "destino_default": "EPS\nOficina de Atención al Usuario",
        "asunto": "Derecho de petición - Asignación de cita con médico especialista",
        "intro": (
            "en ejercicio del derecho fundamental de petición (artículo 23 de la Constitución Política y "
            "Ley 1755 de 2015) y en defensa de mi derecho fundamental a la salud (Ley 1751 de 2015), "
            "presento la siguiente PETICIÓN"
        ),
        "solicitudes": [
            "Asignar de manera prioritaria la cita con el médico especialista ordenada por mi médico tratante, indicándome fecha, hora y lugar.",
            "Informarme por escrito la razón de la demora y los plazos máximos que la normativa exige para la asignación.",
            "Garantizar la atención con la red de prestadores contratada por la EPS, sin costos adicionales para mí.",
            "Si no hay agenda disponible, autorizar la atención con otro prestador, dentro o fuera de la red.",
        ],
        "fundamentos": (
            "- Artículo 49 de la Constitución Política y Ley 1751 de 2015 (Estatutaria de Salud): derecho fundamental a la salud, con oportunidad y continuidad.\n"
            "- Artículo 23 de la Constitución Política y Ley 1755 de 2015 (derecho de petición).\n"
            "- La normativa de salud fija plazos máximos para la asignación de citas especializadas."
        ),
        "anexos": [
            "Orden médica o remisión al especialista.",
            "Historia clínica o resumen que soporte el diagnóstico (si la tienes).",
            "Evidencia de las solicitudes de cita ya realizadas y sin respuesta.",
            "Copia del carné de afiliación a la EPS.",
            "Fotocopia de la cédula de ciudadanía.",
        ],
        "tengo_a_mano": "Orden de remisión, fechas en que pediste la cita y número de afiliación.",
    },
    # ------------------------------------------------------------------ C3
    "C3": {
        "titulo": "Autorización de cirugía o procedimiento",
        "tipo": "Derecho de Petición a la EPS (con copia a la Superintendencia de Salud)",
        "plazo": "15 días hábiles (si hay riesgo para tu vida o salud, puedes ir directo a tutela)",
        "silencio": (
            "Si la EPS no responde o no autoriza el procedimiento, puedes presentar una **Acción de Tutela** "
            "(sin abogado), una queja ante la **Superintendencia Nacional de Salud** y pedir apoyo a la "
            "**Personería Municipal** o la **Defensoría del Pueblo**. Si la urgencia es grave, no esperes: "
            "la tutela puede presentarse de inmediato."
        ),
        "destino": "Tu EPS - Oficina de Atención al Usuario / Gerencia (con copia a la Superintendencia Nacional de Salud)",
        "destino_nota": (
            "Se radica en la **oficina de atención al usuario** de tu EPS o por su canal oficial de PQRS. "
            "Guarda el **número de radicado** y la copia sellada."
        ),
        "entidad_label": "Nombre de tu EPS",
        "entidad_requerida": True,
        "dependencia": "Oficina de Atención al Usuario / Gerencia",
        "destino_default": "EPS\nOficina de Atención al Usuario",
        "asunto": "Derecho de petición - Autorización y programación de cirugía o procedimiento",
        "intro": (
            "en ejercicio del derecho fundamental de petición (artículo 23 de la Constitución Política y "
            "Ley 1755 de 2015) y en defensa de mi derecho fundamental a la salud (Ley 1751 de 2015), "
            "presento la siguiente PETICIÓN"
        ),
        "solicitudes": [
            "Autorizar de manera inmediata la cirugía o procedimiento ordenado por mi médico tratante, según los hechos que describo.",
            "Programar la fecha, hora y lugar de la intervención y comunicármelos por escrito.",
            "Autorizar los exámenes, insumos, medicamentos y valoraciones previas necesarias para el procedimiento.",
            "Si se niega, explicarme por escrito los motivos y las normas en que se basa la negativa.",
        ],
        "fundamentos": (
            "- Artículo 49 de la Constitución Política y Ley 1751 de 2015 (Estatutaria de Salud): derecho fundamental a la salud.\n"
            "- Artículo 23 de la Constitución Política y Ley 1755 de 2015 (derecho de petición).\n"
            "- La orden del médico tratante es el criterio principal para determinar el servicio que requiere el paciente."
        ),
        "anexos": [
            "Orden médica de la cirugía o procedimiento.",
            "Historia clínica o resumen que soporte la necesidad del procedimiento.",
            "Respuesta escrita de la EPS o evidencia de la negativa/demora.",
            "Copia del carné de afiliación a la EPS.",
            "Fotocopia de la cédula de ciudadanía.",
        ],
        "tengo_a_mano": "Orden médica de la cirugía, historia clínica y la negativa o evidencia de demora.",
    },
    # ------------------------------------------------------------------ D1
    "D1": {
        "titulo": "Problema de ruido o perturbación de la convivencia",
        "tipo": "Queja / querella por perturbación de la convivencia (Código Nacional de Seguridad y Convivencia Ciudadana, Ley 1801 de 2016)",
        "plazo": "15 días hábiles para responder tu petición (en emergencias, llama a la línea 123 para atención inmediata)",
        "silencio": (
            "Si la autoridad no responde o no actúa, puedes reiterar la solicitud, poner una queja ante la "
            "**Personería Municipal** o la **Procuraduría**, y presentar una **Acción de Tutela** si se vulnera "
            "tu derecho de petición o tu tranquilidad."
        ),
        "destino": "Inspección de Policía del municipio (con copia a la Policía Nacional - Estación de Policía)",
        "destino_nota": (
            "Se radica en la **Inspección de Policía** o en la **ventanilla única** de la Alcaldía. "
            "Antes, intenta **hablar con tu vecino** y, si es posible, deja constancia (mensaje, acta o testigos). "
            "Para el ruido en el momento, la Policía puede intervenir por la línea 123."
        ),
        "entidad_label": "Municipio o Inspección de Policía (opcional)",
        "entidad_requerida": False,
        "dependencia": "Inspección de Policía",
        "destino_default": "Inspección de Policía Municipal",
        "asunto": "Queja por perturbación de la convivencia (ruido) y solicitud de medidas correctivas",
        "intro": (
            "en ejercicio del derecho de petición (artículo 23 de la Constitución Política y Ley 1755 de 2015) "
            "y conforme al Código Nacional de Seguridad y Convivencia Ciudadana (Ley 1801 de 2016), presento QUEJA"
        ),
        "solicitudes": [
            "Dar trámite a esta queja por afectación de la tranquilidad y la convivencia, conforme al Código de Seguridad y Convivencia.",
            "Citar a las partes a audiencia y adoptar las medidas correctivas que correspondan frente al ruido descrito.",
            "Realizar visitas o mediciones de ruido en el lugar para verificar los hechos.",
            "Informarme por escrito el avance del trámite y la decisión adoptada.",
        ],
        "fundamentos": (
            "- Ley 1801 de 2016 (Código Nacional de Seguridad y Convivencia Ciudadana): comportamientos que afectan la tranquilidad y las medidas correctivas.\n"
            "- Artículo 23 de la Constitución Política y Ley 1755 de 2015 (derecho de petición).\n"
            "- Derecho a la tranquilidad y al goce de un ambiente sano."
        ),
        "anexos": [
            "Videos, audios o fotos que evidencien el ruido (con fecha y hora, si puedes).",
            "Datos de testigos (vecinos) que firmen o confirmen los hechos.",
            "Constancia de los intentos previos de diálogo, si existen.",
            "Fotocopia de la cédula de ciudadanía.",
        ],
        "tengo_a_mano": "Fechas y horas del ruido, evidencias (audio/video), dirección del vecino y datos de testigos.",
    },
    # ------------------------------------------------------------------ D2
    "D2": {
        "titulo": "Comparendo que quiero controvertir",
        "tipo": "Solicitud de audiencia pública y revisión de la orden de comparendo (Ley 1801 de 2016)",
        "plazo": (
            "El plazo para presentarte y pedir audiencia es **muy corto** (por regla general pocos días hábiles, "
            "suele ser 3). **Revisa el plazo escrito en tu comparendo y no lo dejes vencer**"
        ),
        "silencio": (
            "Si no te citan a audiencia o no te responden, puedes reiterar la solicitud, poner una queja ante "
            "la **Personería Municipal** o la **Procuraduría**, y acudir a la **Acción de Tutela** si se "
            "vulnera tu derecho al debido proceso o de petición."
        ),
        "destino": "Inspección de Policía del municipio (Inspector/a de Policía)",
        "destino_nota": (
            "Se radica o se presenta **personalmente** ante la **Inspección de Policía** dentro del plazo. "
            "Lleva tu comparendo y todas las pruebas. Si es posible, acude acompañado de un testigo."
        ),
        "entidad_label": "Municipio o Inspección de Policía (opcional)",
        "entidad_requerida": False,
        "dependencia": "Inspección de Policía",
        "destino_default": "Inspección de Policía Municipal\nInspector(a) de Policía",
        "asunto": "Solicitud de audiencia pública y revisión de orden de comparendo",
        "intro": (
            "en ejercicio del derecho al debido proceso (artículo 29 de la Constitución Política) y del "
            "derecho de petición (artículo 23), y conforme a la Ley 1801 de 2016, presento SOLICITUD DE "
            "AUDIENCIA PÚBLICA para controvertir la orden de comparendo que se me impuso"
        ),
        "solicitudes": [
            "Programar la audiencia pública para controvertir la orden de comparendo y practicar las pruebas que aporto.",
            "Dejar sin efectos o revisar el comparendo si se demuestra que el comportamiento imputado no ocurrió o fue mal calificado.",
            "Informarme por escrito la fecha, hora y lugar de la audiencia, y garantizar mi derecho de defensa.",
            "Abstenerse de aplicar medidas o sanciones mientras se surte el trámite correspondiente.",
        ],
        "fundamentos": (
            "- Artículo 29 de la Constitución Política: debido proceso y derecho de defensa.\n"
            "- Ley 1801 de 2016 (Código Nacional de Seguridad y Convivencia Ciudadana): procedimiento de comparendo y audiencia.\n"
            "- Artículo 23 de la Constitución Política y Ley 1755 de 2015 (derecho de petición)."
        ),
        "anexos": [
            "Copia de la orden de comparendo.",
            "Pruebas que desvirtúen los hechos (fotos, videos, testigos, documentos).",
            "Fotocopia de la cédula de ciudadanía.",
        ],
        "tengo_a_mano": "El comparendo (con su fecha), tus pruebas y datos de testigos.",
    },
}


# =============================================================================
# 4. FUNCIONES AUXILIARES (ESTADO Y NAVEGACIÓN)
# =============================================================================
def iniciar_estado():
    """Crea las variables de estado la primera vez que se abre la app."""
    defaults = {
        "paso": "menu",       # menu | submenu | asesoria | formulario | documento
        "categoria": None,    # A, B, C o D
        "caso": None,         # A1, A2, B1, ...
        "datos": {},          # datos del formulario
        "borrador": "",       # texto del documento generado
    }
    for clave, valor in defaults.items():
        if clave not in st.session_state:
            st.session_state[clave] = valor


def ir_a(paso, **kwargs):
    """Callback de navegación: cambia de paso y actualiza variables de estado."""
    st.session_state["paso"] = paso
    for clave, valor in kwargs.items():
        st.session_state[clave] = valor


def reiniciar():
    """Vuelve al menú principal y borra todo (incluyendo datos personales)."""
    st.session_state["paso"] = "menu"
    st.session_state["categoria"] = None
    st.session_state["caso"] = None
    st.session_state["datos"] = {}
    st.session_state["borrador"] = ""


def fecha_formal():
    hoy = date.today()
    return f"{hoy.day} de {MESES[hoy.month - 1]} de {hoy.year}"


def indicador_progreso():
    """Barra de progreso visual según el paso actual."""
    pasos = {"menu": 1, "submenu": 2, "asesoria": 3, "formulario": 4, "documento": 5}
    actual = pasos[st.session_state["paso"]]
    st.progress(actual / 5, text=f"Paso {actual} de 5")


# =============================================================================
# 5. GENERACIÓN DEL BORRADOR LEGAL
# =============================================================================
def generar_borrador(caso_id, datos):
    """Construye el texto formal del documento a partir de la plantilla del caso."""
    caso = CASOS[caso_id]

    # Destinatario: si el usuario escribió la entidad se usa; si no, el destino por defecto
    entidad = datos["entidad"].strip()
    if entidad:
        destinatario = f"Señores\n{entidad}\n{caso['dependencia']}"
    else:
        destinatario = f"Señores\n{caso['destino_default']}"

    ciudad = datos["ciudad"].strip()
    solicitudes = "\n".join(f"{i}. {s}" for i, s in enumerate(caso["solicitudes"], start=1))
    anexos = "\n".join(f"- {a}" for a in caso["anexos"])

    texto = f"""{ciudad}, {fecha_formal()}

{destinatario}
{ciudad}

REF.: {caso['asunto']}

Respetados señores:

Yo, {datos['nombre'].strip().upper()}, mayor de edad, identificado(a) con cédula de ciudadanía No. {datos['cedula']}, actuando en nombre propio, {caso['intro']}, con base en los siguientes:

I. HECHOS

{datos['hechos'].strip()}

II. PETICIONES

Con fundamento en lo anterior, solicito respetuosamente:

{solicitudes}

III. FUNDAMENTOS DE DERECHO

{caso['fundamentos']}

IV. PRUEBAS Y ANEXOS

Adjunto los siguientes documentos:

{anexos}

V. NOTIFICACIONES

Recibiré notificaciones en: {datos['direccion'].strip()}

Solicito que la respuesta sea clara, completa y de fondo, dentro del término legal.

Atentamente,


______________________________
{datos['nombre'].strip().upper()}
C.C. No. {datos['cedula']}
"""
    return texto


def crear_docx(texto):
    """Convierte el borrador en un archivo .docx en memoria (requiere python-docx)."""
    doc = Document()
    for linea in texto.split("\n"):
        doc.add_paragraph(linea)
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def lista_chequeo(caso_id):
    """Lista de chequeo de radicación específica del caso."""
    caso = CASOS[caso_id]
    return [
        "Revisé que mis datos (nombre, cédula, dirección o correo) estén correctos.",
        "Imprimí el documento **dos veces** y lo **firmé** en ambas copias.",
        "Anexé las pruebas: " + "; ".join(a.rstrip(".") for a in caso["anexos"]) + ".",
        f"Lo radiqué en: {caso['destino']}.",
        "Pedí que **sellen y feches** mi copia, y que me den el **número de radicado**.",
        "Guardé una foto o escaneo de mi copia sellada y todos los anexos.",
        "Anoté la fecha límite de respuesta contando **solo días hábiles** (sin sábados, domingos ni festivos).",
        "Si pasa el plazo sin respuesta, ya sé el siguiente paso: " + caso["silencio"].split(".")[0].lower() + ".",
    ]


# =============================================================================
# 6. VISTAS (UNA POR CADA PASO DEL FLUJO)
# =============================================================================
def vista_menu():
    """PASO 1: Menú principal con las 4 opciones."""
    st.title("⚖️ Tinterillo Digital")
    st.markdown(
        "¡Hola! Soy tu **orientador legal comunitario**. Te explico tus derechos en palabras "
        "sencillas, te cuento el paso a paso y te dejo listo un borrador para radicar."
    )
    st.subheader("¿Con qué tema necesitas ayuda?")

    for cat_id, cat in CATEGORIAS.items():
        st.button(
            f"{cat['icono']}  [{cat_id}] {cat['nombre']}",
            key=f"btn_cat_{cat_id}",
            help=cat["detalle"],
            use_container_width=True,
            on_click=ir_a,
            kwargs={"paso": "submenu", "categoria": cat_id},
        )
        st.caption(cat["detalle"])


def vista_submenu():
    """PASO 2: Submenú específico de la categoría elegida."""
    cat = CATEGORIAS[st.session_state["categoria"]]
    st.header(f"{cat['icono']} {cat['nombre']}")
    st.subheader("¿Cuál de estas situaciones se parece más a la tuya?")

    for caso_id in cat["subs"]:
        st.button(
            f"{caso_id}. {CASOS[caso_id]['titulo']}",
            key=f"btn_sub_{caso_id}",
            use_container_width=True,
            on_click=ir_a,
            kwargs={"paso": "asesoria", "caso": caso_id},
        )

    st.divider()
    st.button("⬅️ Volver al menú principal", key="volver_menu", on_click=ir_a, kwargs={"paso": "menu"})


def vista_asesoria():
    """PASO 3: Cápsula de Asesoría Legal OBLIGATORIA, antes de pedir datos personales."""
    caso = CASOS[st.session_state["caso"]]
    st.header("📚 Cápsula de Asesoría Legal")
    st.subheader(caso["titulo"])

    st.info(
        f"""
**1. ¿Qué vía legal vamos a usar?**
{caso['tipo']}.

**2. ¿Cuánto tiempo tiene la entidad para responder?**
{caso['plazo']}.

**3. ¿Qué pasa si no responde (omisión o silencio)?**
{caso['silencio']}

**4. ¿A quién se entrega?**
{caso['destino']}.
{caso['destino_nota']}

**5. ¿Qué es bueno tener a la mano?**
{caso['tengo_a_mano']}
        """
    )

    st.markdown("**¿Listo para proceder?** Si todo te quedó claro, continúa y te pediré tus datos para redactar el borrador.")

    col1, col2 = st.columns(2)
    with col1:
        st.button(
            "✅ Entendido, continuar",
            key="continuar_asesoria",
            type="primary",
            use_container_width=True,
            on_click=ir_a,
            kwargs={"paso": "formulario"},
        )
    with col2:
        st.button(
            "⬅️ Volver",
            key="volver_submenu",
            use_container_width=True,
            on_click=ir_a,
            kwargs={"paso": "submenu"},
        )


def vista_formulario():
    """PASO 4: Formulario de datos personales y hechos."""
    caso_id = st.session_state["caso"]
    caso = CASOS[caso_id]

    st.header("📝 Tus datos")
    st.caption(f"Caso: {caso['titulo']}")

    previos = st.session_state["datos"]  # para no perder lo escrito si hay un error

    with st.form("formulario_datos"):
        nombre = st.text_input("Nombre completo *", value=previos.get("nombre", ""))
        cedula = st.text_input("Número de cédula *", value=previos.get("cedula", ""), help="Solo números.")
        direccion = st.text_input(
            "Dirección o correo electrónico de notificación *",
            value=previos.get("direccion", ""),
        )
        ciudad = st.text_input("Ciudad o municipio *", value=previos.get("ciudad", ""), placeholder="Ej: Medellín")
        etiqueta = caso["entidad_label"] + (" *" if caso["entidad_requerida"] else "")
        entidad = st.text_input(etiqueta, value=previos.get("entidad", ""))
        hechos = st.text_area(
            "Descripción detallada de los hechos *",
            value=previos.get("hechos", ""),
            height=220,
            help="Cuenta qué pasó, cuándo, dónde y cómo te afecta. Incluye fechas y datos concretos.",
        )
        st.caption("Los campos con * son obligatorios. Tus datos no se guardan en ningún servidor.")
        enviado = st.form_submit_button("Generar mi borrador", type="primary", use_container_width=True)

    if enviado:
        cedula_limpia = re.sub(r"[.\s]", "", cedula)
        datos = {
            "nombre": nombre, "cedula": cedula_limpia, "direccion": direccion,
            "ciudad": ciudad, "entidad": entidad, "hechos": hechos,
        }
        st.session_state["datos"] = datos  # se conserva aunque haya errores

        errores = []
        if len(nombre.strip().split()) < 2:
            errores.append("Escribe tu nombre completo (nombre y apellido).")
        if not (cedula_limpia.isdigit() and 5 <= len(cedula_limpia) <= 12):
            errores.append("La cédula debe contener solo números (entre 5 y 12 dígitos).")
        if not direccion.strip():
            errores.append("Indica una dirección o correo de notificación.")
        if not ciudad.strip():
            errores.append("Indica la ciudad o municipio.")
        if caso["entidad_requerida"] and not entidad.strip():
            errores.append(f"Indica: {caso['entidad_label'].lower()}.")
        if len(hechos.strip()) < 40:
            errores.append("Describe los hechos con más detalle (mínimo unas 2 o 3 frases).")

        if errores:
            for e in errores:
                st.error(e)
        else:
            st.session_state["borrador"] = generar_borrador(caso_id, datos)
            st.session_state["paso"] = "documento"
            st.rerun()

    st.button("⬅️ Volver a la asesoría", key="volver_asesoria", on_click=ir_a, kwargs={"paso": "asesoria"})


def vista_documento():
    """PASO 5: Borrador en pantalla, descarga y lista de chequeo de radicación."""
    caso_id = st.session_state["caso"]
    caso = CASOS[caso_id]

    st.header("📄 Tu borrador está listo")
    st.success("Puedes revisarlo y editarlo aquí mismo. Lo que veas en el recuadro es lo que se descargará.")

    # Recuadro editable: el texto editado se conserva en la clave "borrador"
    texto = st.text_area("Borrador del documento", key="borrador", height=520)

    # --- Botones de descarga ---
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇️ Descargar en .txt",
            data=texto.encode("utf-8"),
            file_name=f"borrador_{caso_id}.txt",
            mime="text/plain",
            use_container_width=True,
            type="primary",
        )
    with col2:
        if DOCX_DISPONIBLE:
            st.download_button(
                "⬇️ Descargar en .docx",
                data=crear_docx(texto),
                file_name=f"borrador_{caso_id}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        else:
            st.caption("Para habilitar .docx agrega `python-docx` a requirements.txt.")

    # --- Lista de chequeo de radicación ---
    st.subheader("✅ Lista de chequeo de radicación")
    for i, item in enumerate(lista_chequeo(caso_id)):
        st.checkbox(item, key=f"chk_{caso_id}_{i}")

    st.warning(
        f"**Si no te responden a tiempo:** {caso['silencio']}"
    )

    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        st.button("✏️ Editar mis datos", key="editar_datos", use_container_width=True,
                  on_click=ir_a, kwargs={"paso": "formulario"})
    with col_b:
        st.button("🏠 Nuevo trámite", key="nuevo_tramite", use_container_width=True, on_click=reiniciar)


# =============================================================================
# 7. PROGRAMA PRINCIPAL
# =============================================================================
def main():
    iniciar_estado()

    # Barra lateral: aviso legal y reinicio
    with st.sidebar:
        st.markdown("### ⚖️ Tinterillo Digital")
        st.caption(AVISO_LEGAL)
        st.button("🔄 Empezar de nuevo", key="reiniciar_sidebar", use_container_width=True, on_click=reiniciar)

    indicador_progreso()

    # Enrutador de vistas según el estado
    vistas = {
        "menu": vista_menu,
        "submenu": vista_submenu,
        "asesoria": vista_asesoria,
        "formulario": vista_formulario,
        "documento": vista_documento,
    }
    vistas[st.session_state["paso"]]()


if __name__ == "__main__":
    main()
