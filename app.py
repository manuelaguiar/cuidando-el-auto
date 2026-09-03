import streamlit as st
import pandas as pd
import sqlite3
import io
import qrcode
from datetime import datetime, date, timedelta
import urllib.parse
from fpdf import FPDF
from database import get_db, init_db

# Configuración de página - Adaptada a la nueva identidad
st.set_page_config(
    page_title="Manuel Aguiar — Centro Técnico Especializado",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)
init_db()

# Rutas a los nuevos archivos de imagen (Actualizar estas rutas si cambian de ubicación)
LOGO_CIRCULAR = "image_8.png"  # El logo de la 'M'
MARCA_ESTILIZADA = "image_9.png" # El nombre 'Manuel Aguiar' con especialidades

# Inyección de Estilo Minimalista OEM con la Nueva Paleta de Manuel Aguiar
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"], .stApp {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }}
    
    /* Encabezados - Usando el azul oscuro de Manuel Aguiar */
    h1, h2, h3, h4 {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        color: #0F2B48 !important; /* Azul oscuro de Manuel Aguiar */
        letter-spacing: -0.02em !important;
    }}
    
    /* Contenedor tipo Tarjeta Minimalista */
    .oem-card {{
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.05);
    }}
    
    /* Cabecera Principal - Usando el degradado de Manuel Aguiar */
    .oem-header {{
        background: linear-gradient(135deg, #0F2B48 0%, #0189A2 100%); /* Degradado de azul a turquesa */
        color: #FFFFFF !important;
        border-radius: 16px;
        padding: 22px 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 14px 0 rgba(15, 43, 72, 0.15);
        display: flex;
        align-items: center;
    }}
    .oem-header img {{
        max-height: 80px;
        margin-right: 20px;
    }}
    .oem-header h2 {{
        color: #FFFFFF !important;
        margin: 0;
        font-size: 1.45rem;
    }}
    .oem-header p {{
        color: #CBD5E1 !important;
        margin: 4px 0 0 0;
        font-size: 0.92rem;
    }}
    
    /* Métricas / Semáforos */
    [data-testid="stMetric"] {{
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}
    [data-testid="stMetricValue"] {{
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }}
    
    /* Botones Modernos - Usando el azul oscuro de Manuel Aguiar */
    .stButton > button {{
        background-color: #0F2B48 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 18px !important;
        width: 100%;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(15, 43, 72, 0.12);
    }}
    .stButton > button:hover {{
        background-color: #0189A2 !important; /* Turquesa al pasar el mouse */
        box-shadow: 0 4px 10px rgba(15, 43, 72, 0.2);
        transform: translateY(-1px);
    }}
    
    /* Botón WhatsApp */
    .btn-wa {{
        display: block;
        text-align: center;
        background-color: #10B981 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 12px 18px !important;
        border-radius: 10px !important;
        text-decoration: none !important;
        box-shadow: 0 2px 6px rgba(16, 185, 129, 0.25);
        margin: 10px 0;
        transition: all 0.2s ease;
    }}
    .btn-wa:hover {{
        background-color: #059669 !important;
        transform: translateY(-1px);
    }}
    
    /* Inputs y Formularios */
    input, select, textarea, .stTextInput > div > div > input {{
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        font-size: 0.95rem !important;
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }}
    
    /* Expanders limpios */
    .streamlit-expanderHeader {{
        font-weight: 600 !important;
        color: #1E293B !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }}
    [data-testid="stSidebar"] .stRadio label {{
        font-weight: 500;
        color: #334155;
    }}
    /* Asegurar que la imagen de marca en el sidebar ocupe todo el ancho */
    [data-testid="stSidebar"] img {{
        width: 100%;
        max-width: 100%;
        height: auto;
    }}
</style>
""", unsafe_allow_html=True)

CATEGORIAS_TALLER = [
    "💻 Soluciones Electrónicas (DPF / EGR / Urea-AdBlue Off / Módulos)",
    "⚡ Híbridos & Eléctricos (Baterías / Celdas / Sistema HV)",
    "🔌 Inyección Electrónica & Diagnóstico DTC",
    "❄️ Aire Acondicionado & Climatización",
    "🛑 Módulo ABS & Electrónica de Frenado",
    "💡 Electricidad General, Ópticas & Iluminación",
    "📦 Repuestos Especializados & Sensores",
    "🔧 Otros Procedimientos Técnicos"
]

TIPOS_PROPULSION = [
    "Combustión Nafta Convencional",
    "Combustión Turbo / Inyección Directa",
    "Turbodiesel Common Rail",
    "Híbrido (HEV / PHEV)",
    "100% Eléctrico (EV)",
    "GNC / Nafta"
]

URL_BASE_OFICIAL = "https://cuidando-el-auto-fwys72ynfql8qgxupsjr98.streamlit.app"

def generar_qr_imagen(url_destino):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url_destino)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0F2B48", back_color="white") # Azul oscuro de Manuel Aguiar
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def generar_pdf_intervencion(vehiculo, servicio):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "INFORME TECNICO DE SERVICIO", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "Manuel Aguiar - Centro de Diagnostico Electronico, Climatizacion & Vehiculos Especializados", ln=True, align="C")
    pdf.line(10, 28, 200, 28)
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "1. DATOS DEL VEHICULO Y TITULAR", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 6, "Patente: " + str(vehiculo['patente']), border=1)
    pdf.cell(95, 6, "Vehiculo: " + str(vehiculo['marca']) + " " + str(vehiculo['modelo']) + " (" + str(vehiculo['anio']) + ")", border=1, ln=True)
    pdf.cell(95, 6, "Propulsion: " + str(vehiculo['tipo_propulsion'] or 'N/D'), border=1)
    pdf.cell(95, 6, "Odometro: " + f"{servicio['km_servicio']:,}" + " km", border=1, ln=True)
    pdf.cell(95, 6, "Titular: " + str(vehiculo['nombre'] or 'N/D'), border=1)
    pdf.cell(95, 6, "Telefono: " + str(vehiculo['telefono'] or 'N/D'), border=1, ln=True)
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "2. DETALLE DE LA INTERVENCION TECNICA", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 6, "Fecha: " + str(servicio['fecha']), border=1)
    pdf.cell(95, 6, "Especialidad: " + str(servicio['categoria'][:35]), border=1, ln=True)
    pdf.ln(2)
    if servicio['diagnostico_dtc']:
        pdf.set_font("Helvetica", "B", 10)
        estado_txt = " [" + str(servicio['estado_dtc']) + "]" if servicio['estado_dtc'] else ""
        pdf.cell(0, 6, "Diagnostico / Codigos DTC" + estado_txt + ":", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, str(servicio['diagnostico_dtc']), border=1)
        pdf.ln(2)
    if servicio['parametros_tecnicos']:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, "Parametros y Mediciones Tecnicas:", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, str(servicio['parametros_tecnicos']), border=1)
        pdf.ln(2)
    if servicio['software_version']:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, "Calibracion / Backup Software ECU: " + str(servicio['software_version']), border=1, ln=True)
        pdf.ln(2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Procedimiento y Trabajos Realizados:", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5, str(servicio['trabajo_realizado'] or "Sin detalle adicional."), border=1)
    pdf.ln(2)
    if servicio['repuestos_utilizados']:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, "Componentes / Repuestos Instalados:", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, str(servicio['repuestos_utilizados']), border=1)
        pdf.ln(2)
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(95, 6, "Garantia Otorgada: " + str(servicio['garantia'] or 'Estandar'), border=1)
    costo_txt = "$" + f"{servicio['costo_total']:,.2f}" if servicio['costo_total'] else "Consultar"
    pdf.cell(95, 6, "Importe Total: " + costo_txt, border=1, ln=True)
    if servicio['proximo_km'] or servicio['proxima_fecha']:
        pdf.ln(2)
        pdf.set_font("Helvetica", "I", 9)
        txt_prox = "Proximo control sugerido: " + f"{servicio['proximo_km']:,}" + " km" if servicio['proximo_km'] else ""
        if servicio['proxima_fecha']:
            txt_prox += " / Fecha estimada: " + str(servicio['proxima_fecha'])
        pdf.cell(0, 6, txt_prox, border=1, ln=True)
    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 5, "Documento digital emitido por Manuel Aguiar. Valido como constancia de servicio.", align="C", ln=True)
    return bytes(pdf.output())

# Sidebar Corporativo de Manuel Aguiar
with st.sidebar:
    # Usar la marca estilizada completa en la barra lateral
    if io.os.path.exists(MARCA_ESTILIZADA):
        st.image(MARCA_ESTILIZADA, use_column_width=True)
    else:
        # Fallback si no está el archivo
        st.markdown("""
        <div style="padding: 10px 0 20px 0;">
            <h3 style="margin: 0; color: #0F2B48;">⚡ Manuel Aguiar</h3>
            <p style="margin: 0; font-size: 0.85rem; color: #64748B;">Centro Técnico Especializado</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    opcion = st.radio(
        "Navegación Principal",
        [
            "📋 Tarjeta Digital del Vehículo",
            "🛠️ Cargar Trabajo de Taller",
            "➕ Registrar y Modificar Datos",
            "🔔 Alertas Preventivas (30 Días)",
            "💼 Presupuestos WhatsApp",
            "📊 Historial General"
        ]
    )

# -------------------------------------------------------------
# 1. TARJETA DIGITAL (DISEÑO MINIMALISTA DE MANUEL AGUIAR)
# -------------------------------------------------------------
if opcion == "📋 Tarjeta Digital del Vehículo":
    query_params = st.query_params
    patente_url = query_params.get("patente", "").upper()
    
    st.markdown("## 📋 Libreta de Servicio Digital")
    patente_buscada = st.text_input("Ingresá la Patente del Vehículo:", value=patente_url, placeholder="Ej: GFG135").upper().strip()
    
    if patente_buscada:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT v.*, c.nombre, c.telefono, c.localidad FROM vehiculos v LEFT JOIN clientes c ON v.cliente_id = c.id WHERE v.patente = ?", (patente_buscada,))
        vehiculo = cursor.fetchone()
        
        if vehiculo:
            # Banner principal del vehículo con el logo circular de Manuel Aguiar
            logo_base64 = ""
            if io.os.path.exists(LOGO_CIRCULAR):
                import base64
                with open(LOGO_CIRCULAR, "rb") as img_file:
                    logo_base64 = base64.b64encode(img_file.read()).decode('utf-8')

            st.markdown(f"""
            <div class="oem-header">
                {'<img src="data:image/png;base64,' + logo_base64 + '" />' if logo_base64 else ''}
                <div>
                    <h2>{vehiculo['marca']} {vehiculo['modelo']} ({vehiculo['anio']})</h2>
                    <p>Patente Oficial: <strong>{vehiculo['patente']}</strong> &nbsp;|&nbsp; Titular: <strong>{vehiculo['nombre'] or 'Particular'}</strong></p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Fila de métricas
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Odómetro Actual", f"{vehiculo['km_actuales']:,} km")
            c2.metric("Motorización", vehiculo['motor'] or "N/D")
            c3.metric("Propulsión", vehiculo['tipo_propulsion'])
            c4.metric("Localidad", vehiculo['localidad'] or "Ayacucho")
            
            tel_clean = str(vehiculo['telefono']).replace("+", "").replace("-", "").replace(" ", "").strip()
            link_directo_auto = f"{URL_BASE_OFICIAL}/?patente={vehiculo['patente']}"
            msj_bienvenida = f"Hola {vehiculo['nombre']}! Te dejamos el enlace a la Libreta de Servicio Digital de tu {vehiculo['marca']} {vehiculo['modelo']} ({vehiculo['patente']}). Podés consultar los historiales técnicos y cargar services: {link_directo_auto}"
            link_wa = "https://wa.me/" + tel_clean + "?text=" + urllib.parse.quote(msj_bienvenida)
            
            st.markdown(f'<a href="{link_wa}" target="_blank" class="btn-wa">📲 Compartir Libreta Digital por WhatsApp</a>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 🚦 Semáforo de Mantenimientos Preventivos")
            km_act = vehiculo['km_actuales'] or 0
            
            col_a, col_b, col_c = st.columns(3)
            int_aceite = vehiculo['intervalo_aceite_km'] or 10000
            rest_aceite = int_aceite - (km_act % int_aceite)
            col_a.metric("🛢️ Aceite y Filtros", f"En {rest_aceite:,} km", delta=f"-{rest_aceite} km" if rest_aceite < 1500 else "Al día")
            
            int_bujias = vehiculo['intervalo_bujias_km'] or 0
            if "100% Electrico" in str(vehiculo['tipo_propulsion']) or (vehiculo['tipo_propulsion'] == "Turbodiesel Common Rail" and int_bujias == 0):
                col_b.metric("⚡ Bujías Encendido", "No Aplica")
            elif int_bujias > 0:
                rest_buj = int_bujias - (km_act % int_bujias)
                col_b.metric("⚡ Bujías Encendido", f"En {rest_buj:,} km", delta=f"-{rest_buj} km" if rest_buj < 2500 else "Al día")
            else:
                col_b.metric("⚡ Bujías Encendido", "No Configurado")
                
            int_dist = vehiculo['intervalo_distribucion_km'] or 0
            if int_dist == 0:
                col_c.metric("⚙️ Distribución", "Cadena / Libre Mant.")
            else:
                rest_dist = int_dist - (km_act % int_dist)
                col_c.metric("⚙️ Kit Distribución", f"En {rest_dist:,} km", delta=f"-{rest_dist} km" if rest_dist < 5000 else "Al día")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Secciones verticales minimalistas
            with st.expander("📄 1. Informes y Trabajos Oficiales de Manuel Aguiar (Descargar PDF)", expanded=True):
                cursor.execute("SELECT * FROM servicios_taller WHERE patente = ? ORDER BY fecha DESC, id DESC", (patente_buscada,))
                servicios_t = cursor.fetchall()
                if servicios_t:
                    for st_item in servicios_t:
                        st.markdown(f"**📅 {st_item['fecha']} — {st_item['categoria']} ({st_item['km_servicio']:,} km)**")
                        if st_item['diagnostico_dtc']:
                            st.info(f"**DTC / Diagnóstico [{st_item['estado_dtc']}]:** {st_item['diagnostico_dtc']}")
                        if st_item['parametros_tecnicos']:
                            st.success(f"**Parámetros / Mediciones:** {st_item['parametros_tecnicos']}")
                        if st_item['software_version']:
                            st.warning(f"**Calibración Software ECU:** {st_item['software_version']}")
                        st.write(f"**Trabajo Realizado:** {st_item['trabajo_realizado']}")
                        if st_item['repuestos_utilizados']:
                            st.write(f"**Repuestos / Materiales:** {st_item['repuestos_utilizados']}")
                        st.caption(f"Garantía: {st_item['garantia']} | Importe: ${st_item['costo_total']:,.2f}")
                        
                        pdf_bytes = generar_pdf_intervencion(vehiculo, st_item)
                        st.download_button(
                            label="📄 Descargar Informe Técnico en PDF",
                            data=pdf_bytes,
                            file_name=f"Informe_{patente_buscada}_{st_item['fecha']}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{st_item['id']}"
                        )
                        st.divider()
                else:
                    st.info("No hay intervenciones oficiales registradas aún por Manuel Aguiar.")

            with st.expander("📝 2. Historial de Mantenimientos Externos (Libre)", expanded=False):
                cursor.execute("SELECT * FROM servicios_externos WHERE patente = ? ORDER BY fecha DESC, id DESC", (patente_buscada,))
                servicios_e = cursor.fetchall()
                if servicios_e:
                    for se in servicios_e:
                        st.markdown(f"**📅 {se['fecha']} — {se['tipo_mantenimiento']} ({se['km_servicio']:,} km)**")
                        st.write(f"📍 **Establecimiento:** {se['establecimiento'] or 'Particular'}")
                        st.text(se['detalle_materiales'])
                        st.divider()
                else:
                    st.info("El titular no ha registrado mantenimientos externos todavía.")

            with st.expander("➕ 3. Anotar Nuevo Mantenimiento (Cliente / Lubricentro)", expanded=False):
                with st.form("form_cliente_externo", clear_on_submit=True):
                    col_f1, col_f2 = st.columns(2)
                    f_ext = col_f1.date_input("Fecha de realización:", date.today())
                    km_ext = col_f2.number_input("Kilometraje actual:", min_value=int(km_act), value=int(km_act), step=500)
                    lugar_ext = st.text_input("Lugar / Lubricentro:", placeholder="Ej: Lubricentro San Martín")
                    
                    st.markdown("**Marcar los ítems realizados:**")
                    col_k1, col_k2 = st.columns(2)
                    chk_aceite = col_k1.checkbox("🛢️ Aceite de Motor")
                    txt_aceite = col_k2.text_input("Marca/Viscosidad Aceite:", placeholder="Ej: Elaion F50 5W-40", disabled=not chk_aceite)
                    
                    chk_f_aceite = st.checkbox("🛢️ Filtro de Aceite")
                    chk_f_aire = st.checkbox("💨 Filtro de Aire de Motor")
                    chk_f_comb = st.checkbox("⛽ Filtro de Combustible (Nafta / Gasoil)")
                    chk_f_hab = st.checkbox("❄️ Filtro de Habitáculo / Aire Acondicionado")
                    chk_dist = st.checkbox("⚙️ Kit de Distribución")
                    chk_bomba = st.checkbox("💧 Bomba de Agua & Refrigerante")
                    chk_frenos = st.checkbox("🛑 Pastillas / Discos de Freno")
                    chk_bat = st.checkbox("🔋 Reemplazo de Batería 12V")
                    chk_neu = st.checkbox("🚗 Alineación / Balanceo")
                    
                    obs_extra = st.text_area("Notas u observaciones adicionales:")
                    btn_guardar_ext = st.form_submit_button("💾 Guardar Mantenimiento en Libreta")
                    
                    if btn_guardar_ext:
                        items_cambiados = []
                        if chk_aceite: items_cambiados.append(f"• Aceite de Motor ({txt_aceite if txt_aceite else 'Realizado'})")
                        if chk_f_aceite: items_cambiados.append("• Filtro de Aceite")
                        if chk_f_aire: items_cambiados.append("• Filtro de Aire")
                        if chk_f_comb: items_cambiados.append("• Filtro de Combustible")
                        if chk_f_hab: items_cambiados.append("• Filtro de Habitáculo / A/C")
                        if chk_dist: items_cambiados.append("• Kit de Distribución")
                        if chk_bomba: items_cambiados.append("• Bomba de Agua & Refrigerante")
                        if chk_frenos: items_cambiados.append("• Frenos (Pastillas / Discos)")
                        if chk_bat: items_cambiados.append("• Batería 12V")
                        if chk_neu: items_cambiados.append("• Alineación / Neumáticos")
                        if obs_extra: items_cambiados.append(f"• Notas: {obs_extra}")
                        
                        if not items_cambiados:
                            st.warning("Por favor marcá al menos un casillero o escribí una observación.")
                        else:
                            detalle_final = "\n".join(items_cambiados)
                            titulo_servicio = "Service de Aceite y Filtros" if chk_aceite and (chk_f_aceite or chk_f_aire) else ("Distribución / Refrigeración" if chk_dist or chk_bomba else "Service Lubricentro / Mecánica")
                            cursor.execute("INSERT INTO servicios_externos (patente, fecha, km_servicio, tipo_mantenimiento, establecimiento, detalle_materiales) VALUES (?, ?, ?, ?, ?, ?)", (patente_buscada, str(f_ext), int(km_ext), titulo_servicio, lugar_ext, detalle_final))
                            if km_ext > km_act:
                                cursor.execute("UPDATE vehiculos SET km_actuales = ? WHERE patente = ?", (int(km_ext), patente_buscada))
                            conn.commit()
                            st.success("✅ Mantenimiento guardado y kilometraje actualizado.")
                            st.rerun()

            with st.expander("🖨️ 4. Generador de Código QR Manuel Aguiar para Sticker", expanded=False):
                host_ip = st.text_input("Dirección Web del Servidor:", value=URL_BASE_OFICIAL)
                url_qr = f"{host_ip.rstrip('/')}/?patente={patente_buscada}"
                qr_bytes = generar_qr_imagen(url_qr)
                col_qr1, col_qr2 = st.columns([1, 2])
                col_qr1.image(qr_bytes, caption=f"QR Patente: {patente_buscada}", width=180)
                col_qr2.write(f"**Enlace público:** `{url_qr}`")
                col_qr2.download_button(label="⬇️ Descargar Imagen QR (PNG)", data=qr_bytes, file_name=f"QR_{patente_buscada}.png", mime="image/png")

        else:
            st.warning("No se encontró ningún vehículo con esa patente.")
        conn.close()

# -------------------------------------------------------------
# 2. CARGAR TRABAJO DE TALLER
# -------------------------------------------------------------
elif opcion == "🛠️ Cargar Trabajo de Taller":
    st.markdown("## 🛠️ Registrar Intervención Técnica Oficial Manuel Aguiar")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT patente, marca, modelo, km_actuales FROM vehiculos ORDER BY patente")
    autos = cursor.fetchall()
    
    if not autos:
        st.warning("Primero debés registrar al menos un vehículo.")
    else:
        mapa_autos = {f"{a['patente']} — {a['marca']} {a['modelo']} ({a['km_actuales']:,} km)": a for a in autos}
        sel_auto = st.selectbox("Seleccionar Vehículo:", list(mapa_autos.keys()))
        auto_data = mapa_autos[sel_auto]
        patente_sel = auto_data['patente']
        
        with st.form("form_taller", clear_on_submit=True):
            col_t1, col_t2 = st.columns(2)
            fecha_t = col_t1.date_input("Fecha de intervención:", date.today())
            km_t = col_t2.number_input("Kilometraje actual:", min_value=int(auto_data['km_actuales'] or 0), value=int(auto_data['km_actuales'] or 0), step=500)
            
            cat_t = st.selectbox("Especialidad / Área de Trabajo Manuel Aguiar:", CATEGORIAS_TALLER)
            
            c_dtc1, c_dtc2 = st.columns([3, 1])
            dtc_t = c_dtc1.text_input("Diagnóstico / Códigos DTC detectados:", placeholder="Ej: P2463 (DPF), P0401 (EGR), C0035 (ABS)")
            estado_dtc = c_dtc2.selectbox("Estado DTC:", ["Resuelto", "En Seguimiento", "Preventivo", "No aplica"])
            
            st.markdown("##### 📊 Parámetros Técnicos & Mediciones (Opcional)")
            if "Híbridos" in cat_t:
                p_c1, p_c2, p_c3 = st.columns(3)
                soh = p_c1.text_input("SOH Batería (%):", placeholder="Ej: 88%")
                delta_v = p_c2.text_input("Delta V Celdas (V):", placeholder="Ej: 0.02V")
                aisl = p_c3.text_input("Resistencia Aislamiento (MΩ):", placeholder="Ej: > 500 MΩ")
                params_str = f"SOH: {soh} | Delta V: {delta_v} | Aislamiento: {aisl}" if (soh or delta_v or aisl) else ""
            elif "Aire" in cat_t:
                p_c1, p_c2, p_c3, p_c4 = st.columns(4)
                p_baja = p_c1.text_input("Baja (PSI):", placeholder="32 PSI")
                p_alta = p_c2.text_input("Alta (PSI):", placeholder="210 PSI")
                gas_g = p_c3.text_input("Carga Gas:", placeholder="500g R134a")
                temp_tob = p_c4.text_input("Temp. Tobera:", placeholder="6.5°C")
                params_str = f"Baja: {p_baja} | Alta: {p_alta} | Carga: {gas_g} | Tobera: {temp_tob}" if (p_baja or p_alta or gas_g or temp_tob) else ""
            else:
                params_str = st.text_input("Mediciones / Parámetros leídos:", placeholder="Ej: Caudal inyectores, caída de tensión alternador 14.2V...")

            sw_ecu = ""
            if "Soluciones Electrónicas" in cat_t or "Módulos" in cat_t:
                sw_ecu = st.text_input("Software ECU / Archivo Backup Manuel Aguiar:", placeholder="Ej: Hilux_2.8_DPF_OFF_v2.bin")
            
            trabajo_t = st.text_area("Procedimiento y Trabajo Realizado:*", placeholder="Describí los detalles de la reparación o calibración...")
            repuestos_t = st.text_area("Repuestos / Insumos / Componentes Instalados:", placeholder="Ej: Sensor MAF Bosch, Lámpara H7, Carga R134a...")
            
            c3, c4, c5 = st.columns(3)
            garantia_t = c3.selectbox("Garantía Otorgada Manuel Aguiar:", ["3 Meses", "6 Meses", "12 Meses", "Garantía de Fábrica", "Sin garantía especial"])
            prox_km = c4.number_input("Próximo Control Sugerido (KM) — 0 si no aplica:", min_value=0, step=5000, value=0)
            costo_t = c5.number_input("Importe Total Manuel Aguiar ($):", min_value=0.0, step=1000.0)
            
            btn_guardar_taller = st.form_submit_button("💾 Guardar Trabajo Técnico y Actualizar Odómetro")
            if btn_guardar_taller:
                if trabajo_t:
                    cursor.execute("INSERT INTO servicios_taller (patente, fecha, km_servicio, categoria, diagnostico_dtc, estado_dtc, trabajo_realizado, repuestos_utilizados, parametros_tecnicos, software_version, garantia, proximo_km, costo_total) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (patente_sel, str(fecha_t), int(km_t), cat_t, dtc_t, estado_dtc, trabajo_t, repuestos_t, params_str, sw_ecu, garantia_t, int(prox_km) if prox_km > 0 else None, float(costo_t)))
                    cursor.execute("UPDATE vehiculos SET km_actuales = ? WHERE patente = ?", (int(km_t), patente_sel))
                    conn.commit()
                    st.success(f"✅ Intervención registrada correctamente para {patente_sel}.")
                else:
                    st.error("El campo 'Procedimiento y Trabajo Realizado' es obligatorio.")
    conn.close()

# -------------------------------------------------------------
# 3. REGISTRAR Y MODIFICAR DATOS (CLIENTES, AUTOS E INTERVALOS)
# -------------------------------------------------------------
elif opcion == "➕ Registrar y Modificar Datos":
    st.markdown("## ➕ Gestión de Clientes y Vehículos Manuel Aguiar")
    
    sec_gestion = st.radio(
        "Seleccionar Acción:",
        ["👤 Alta de Cliente", "🚗 Alta de Vehículo", "✏️ Modificar Vehículo", "✏️ Modificar Cliente"],
        horizontal=True
    )
    
    conn = get_db()
    cursor = conn.cursor()
    
    if sec_gestion == "👤 Alta de Cliente":
        with st.form("form_alta_cli", clear_on_submit=True):
            col_c1, col_c2 = st.columns(2)
            nom = col_c1.text_input("Nombre y Apellido / Razón Social:*")
            tel = col_c2.text_input("Teléfono / WhatsApp:* (Ej: 2296123456)")
            dire = col_c1.text_input("Dirección:")
            loc = col_c2.text_input("Localidad:", value="Ayacucho")
            if st.form_submit_button("Guardar Cliente Manuel Aguiar"):
                if nom and tel:
                    cursor.execute("INSERT INTO clientes (nombre, telefono, direccion, localidad) VALUES (?, ?, ?, ?)", (nom, tel, dire, loc))
                    conn.commit()
                    st.success(f"Cliente '{nom}' guardado correctamente.")
                else:
                    st.error("Nombre y Teléfono son obligatorios.")

    elif sec_gestion == "🚗 Alta de Vehículo":
        cursor.execute("SELECT id, nombre, telefono FROM clientes ORDER BY nombre")
        clientes_db = cursor.fetchall()
        if clientes_db:
            map_c = {f"{c['nombre']} ({c['telefono']})": c['id'] for c in clientes_db}
            with st.form("form_alta_veh", clear_on_submit=True):
                cli_sel = st.selectbox("Titular:", list(map_c.keys()))
                c1, c2, c3 = st.columns(3)
                pat = c1.text_input("Patente:*").upper().strip()
                mar = c2.text_input("Marca:* (Ej: Fiat, Toyota, VW)")
                mod = c3.text_input("Modelo:* (Ej: Fiorino, Hilux, Gol)")
                c4, c5, c6 = st.columns(3)
                ani = c4.number_input("Año:", min_value=1980, max_value=date.today().year + 1, value=2010)
                prop = c5.selectbox("Propulsión:", TIPOS_PROPULSION)
                mot = c6.text_input("Motorización:", placeholder="Ej: 1.3 Fire, 2.8 CTDI, 1.4 TSI")
                km_ini = st.number_input("KM Inicial Odómetro:", min_value=0, step=1000)
                
                st.markdown("#### ⚙️ Plan de Mantenimiento Personalizado Manuel Aguiar (KM)")
                col_i1, col_i2, col_i3 = st.columns(3)
                int_aceite = col_i1.number_input("Intervalo Aceite (KM):", value=10000, step=1000)
                int_dist = col_i2.number_input("Intervalo Distribución (KM) — 0 si es cadena:", value=60000, step=10000)
                int_buj = col_i3.number_input("Intervalo Bujías (KM) — 0 si no aplica:", value=30000 if "Nafta" in prop else 0, step=10000)
                
                if st.form_submit_button("Guardar Vehículo Manuel Aguiar"):
                    if pat and mar and mod:
                        try:
                            cursor.execute("INSERT INTO vehiculos (patente, cliente_id, marca, modelo, anio, tipo_propulsion, motor, km_actuales, intervalo_aceite_km, intervalo_distribucion_km, intervalo_bujias_km) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (pat, map_c[cli_sel], mar, mod, int(ani), prop, mot, int(km_ini), int(int_aceite), int(int_dist), int(int_buj)))
                            conn.commit()
                            st.success(f"Vehículo {mar} {mod} ({pat}) guardado correctamente.")
                        except sqlite3.IntegrityError:
                            st.error("Esa patente ya existe en la base de datos.")
                    else:
                        st.error("Patente, Marca y Modelo son obligatorios.")
        else:
            st.info("Primero registrá al menos un cliente.")

    elif sec_gestion == "✏️ Modificar Vehículo":
        cursor.execute("SELECT patente, marca, modelo FROM vehiculos ORDER BY patente")
        vehiculos_edit = cursor.fetchall()
        if vehiculos_edit:
            map_ve = {f"{v['patente']} — {v['marca']} {v['modelo']}": v['patente'] for v in vehiculos_edit}
            sel_pat_edit = st.selectbox("Seleccionar Vehículo:", list(map_ve.keys()))
            pat_a_modificar = map_ve[sel_pat_edit]
            cursor.execute("SELECT * FROM vehiculos WHERE patente = ?", (pat_a_modificar,))
            v_curr = cursor.fetchone()
            if v_curr:
                with st.form("form_editar_veh"):
                    st.write(f"### Editando Datos Manuel Aguiar de: `{pat_a_modificar}`")
                    col_m1, col_m2 = st.columns(2)
                    e_mar = col_m1.text_input("Marca:", value=v_curr['marca'])
                    e_mod = col_m2.text_input("Modelo:", value=v_curr['modelo'])
                    
                    col_m3, col_m4, col_m5 = st.columns(3)
                    e_ani = col_m3.number_input("Año:", min_value=1980, max_value=date.today().year + 1, value=int(v_curr['anio'] or 2010))
                    idx_prop = 0
                    if v_curr['tipo_propulsion'] in TIPOS_PROPULSION:
                        idx_prop = TIPOS_PROPULSION.index(v_curr['tipo_propulsion'])
                    e_prop = col_m4.selectbox("Propulsión:", TIPOS_PROPULSION, index=idx_prop)
                    e_mot = col_m5.text_input("Motor:", value=v_curr['motor'] or "")
                    
                    e_km = st.number_input("Kilometraje Actual:", min_value=0, value=int(v_curr['km_actuales'] or 0), step=1000)
                    
                    st.markdown("#### ⚙️ Ajustar Intervalos de Servicio Manuel Aguiar (KM)")
                    col_ei1, col_ei2, col_ei3 = st.columns(3)
                    e_int_aceite = col_ei1.number_input("Intervalo Aceite (KM):", value=int(v_curr['intervalo_aceite_km'] or 10000), step=1000)
                    e_int_dist = col_ei2.number_input("Intervalo Distribución (KM):", value=int(v_curr['intervalo_distribucion_km'] or 60000), step=10000)
                    e_int_buj = col_ei3.number_input("Intervalo Bujías (KM):", value=int(v_curr['intervalo_bujias_km'] or 30000), step=5000)
                    
                    if st.form_submit_button("💾 Guardar Cambios de Manuel Aguiar"):
                        cursor.execute("UPDATE vehiculos SET marca = ?, modelo = ?, anio = ?, tipo_propulsion = ?, motor = ?, km_actuales = ?, intervalo_aceite_km = ?, intervalo_distribucion_km = ?, intervalo_bujias_km = ? WHERE patente = ?", (e_mar, e_mod, int(e_ani), e_prop, e_mot, int(e_km), int(e_int_aceite), int(e_int_dist), int(e_int_buj), pat_a_modificar))
                        conn.commit()
                        st.success("✅ Vehículo actualizado correctamente.")
                        st.rerun()
        else:
            st.info("No hay vehículos registrados para modificar.")

    elif sec_gestion == "✏️ Modificar Cliente":
        cursor.execute("SELECT id, nombre, telefono, direccion, localidad FROM clientes ORDER BY nombre")
        clientes_edit = cursor.fetchall()
        if clientes_edit:
            map_cli_edit = {f"{c['nombre']} ({c['telefono']})": c for c in clientes_edit}
            sel_cli_name = st.selectbox("Seleccionar Cliente:", list(map_cli_edit.keys()))
            cli_data = map_cli_edit[sel_cli_name]
            with st.form("form_editar_cliente"):
                st.write(f"### Editando Cliente: `{cli_data['nombre']}`")
                col_mc1, col_mc2 = st.columns(2)
                nuevo_nom = col_mc1.text_input("Nombre y Apellido / Razón Social:", value=cli_data['nombre'])
                nuevo_tel = col_mc2.text_input("Teléfono / WhatsApp:", value=cli_data['telefono'])
                nuevo_dir = col_mc1.text_input("Dirección:", value=cli_data['direccion'] or "")
                nueva_loc = col_mc2.text_input("Localidad:", value=cli_data['localidad'] or "Ayacucho")
                if st.form_submit_button("💾 Guardar Cambios de Manuel Aguiar"):
                    if nuevo_nom and nuevo_tel:
                        cursor.execute("UPDATE clientes SET nombre = ?, telefono = ?, direccion = ?, localidad = ? WHERE id = ?", (nuevo_nom, nuevo_tel, nuevo_dir, nueva_loc, cli_data['id']))
                        conn.commit()
                        st.success("✅ Cliente actualizado correctamente.")
                        st.rerun()
                    else:
                        st.error("El nombre y el teléfono no pueden quedar vacíos.")
        else:
            st.info("No hay clientes registrados para modificar.")
    conn.close()

# -------------------------------------------------------------
# 4. ALERTAS PREVENTIVAS
# -------------------------------------------------------------
elif opcion == "🔔 Alertas Preventivas (30 Días)":
    st.markdown("## 🔔 Panel de Alertas Preventivas Manuel Aguiar")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT v.*, c.nombre, c.telefono FROM vehiculos v LEFT JOIN clientes c ON v.cliente_id = c.id ORDER BY v.patente")
    vehiculos = cursor.fetchall()
    if vehiculos:
        alertas_generadas = []
        for v in vehiculos:
            km = v['km_actuales'] or 0
            nombre_cli = v['nombre'] or "Estimado cliente"
            tel = str(v['telefono']).replace("+", "").replace("-", "").replace(" ", "").strip()
            if v['intervalo_bujias_km'] and v['intervalo_bujias_km'] > 0:
                rest_buj = v['intervalo_bujias_km'] - (km % v['intervalo_bujias_km'])
                if rest_buj <= 2500:
                    alertas_generadas.append({"Patente": v['patente'], "Vehiculo": f"{v['marca']} {v['modelo']}", "Cliente": nombre_cli, "Telefono": tel, "Alerta": "⚡ Recambio de Bujías Manuel Aguiar", "Detalle": f"Faltan aprox. {rest_buj:,} km", "Mensaje": f"Hola {nombre_cli}! Te recordamos desde el Centro Técnico Manuel Aguiar que tu {v['marca']} {v['modelo']} ({v['patente']}) está próximo al recambio de bujías ({km:,} km). ¿Querés que reservemos un turno?"})
            if v['intervalo_aceite_km'] and v['intervalo_aceite_km'] > 0:
                rest_aceite = v['intervalo_aceite_km'] - (km % v['intervalo_aceite_km'])
                if rest_aceite <= 1500:
                    alertas_generadas.append({"Patente": v['patente'], "Vehiculo": f"{v['marca']} {v['modelo']}", "Cliente": nombre_cli, "Telefono": tel, "Alerta": "🛢️ Service Aceite y Filtros Manuel Aguiar", "Detalle": f"Faltan aprox. {rest_aceite:,} km", "Mensaje": f"Hola {nombre_cli}! Tu {v['marca']} {v['modelo']} ({v['patente']}) está próximo al service de aceite y filtros ({km:,} km)."})
            if v['intervalo_distribucion_km'] and v['intervalo_distribucion_km'] > 0:
                rest_dist = v['intervalo_distribucion_km'] - (km % v['intervalo_distribucion_km'])
                if rest_dist <= 5000:
                    alertas_generadas.append({"Patente": v['patente'], "Vehiculo": f"{v['marca']} {v['modelo']}", "Cliente": nombre_cli, "Telefono": tel, "Alerta": "⚙️ Correa de Distribución Manuel Aguiar", "Detalle": f"Faltan aprox. {rest_dist:,} km", "Mensaje": f"Hola {nombre_cli}! Tu {v['marca']} {v['modelo']} ({v['patente']}) está próximo al reemplazo de correa de distribución ({km:,} km)."})
        if alertas_generadas:
            st.write(f"Se encontraron **{len(alertas_generadas)} alertas activas** de Manuel Aguiar:")
            for al in alertas_generadas:
                st.markdown(f"**{al['Vehiculo']}** (`{al['Patente']}`) — *{al['Cliente']}*")
                st.write(f"**{al['Alerta']}** — {al['Detalle']}")
                link_wa = "https://wa.me/" + al['Telefono'] + "?text=" + urllib.parse.quote(al['Mensaje'])
                st.markdown(f'<a href="{link_wa}" target="_blank" class="btn-wa" style="width:100%; text-align:center;">📲 Enviar Recordatorio de Manuel Aguiar</a>', unsafe_allow_html=True)
                st.divider()
        else:
            st.success("🎉 No hay vehículos con alertas preventivas Manuel Aguiar para los próximos kilómetros.")
    conn.close()

# -------------------------------------------------------------
# 5. PRESUPUESTOS WHATSAPP
# -------------------------------------------------------------
elif opcion == "💼 Presupuestos WhatsApp":
    st.markdown("## 💼 Presupuestador Técnico Manuel Aguiar")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT v.patente, v.marca, v.modelo, c.nombre, c.telefono FROM vehiculos v LEFT JOIN clientes c ON v.cliente_id = c.id ORDER BY v.patente")
    vehiculos_p = cursor.fetchall()
    if vehiculos_p:
        mapa_vp = {f"{v['patente']} — {v['marca']} {v['modelo']} ({v['nombre']})": v for v in vehiculos_p}
        sel_vp = st.selectbox("Seleccionar Vehículo:", list(mapa_vp.keys()))
        dv = mapa_vp[sel_vp]
        with st.form("form_presupuesto"):
            cat_p = st.selectbox("Especialidad Manuel Aguiar:", CATEGORIAS_TALLER)
            det_p = st.text_area("Detalle de mano de obra y procedimiento:")
            rep_p = st.text_area("Detalle de repuestos y materiales:")
            col_pr1, col_pr2 = st.columns(2)
            val_p = col_pr1.number_input("Validez del Presupuesto (días):", value=15, min_value=1)
            tot_p = col_pr2.number_input("Importe Total Manuel Aguiar ($):", min_value=0.0, step=1000.0)
            
            if st.form_submit_button("Generar y Guardar Presupuesto Manuel Aguiar"):
                if tot_p > 0:
                    cursor.execute("INSERT INTO presupuestos (patente, fecha_emision, categoria, validez_dias, detalle_trabajo, repuestos, total) VALUES (?, ?, ?, ?, ?, ?, ?)", (dv['patente'], str(date.today()), cat_p, int(val_p), det_p, rep_p, float(tot_p)))
                    conn.commit()
                    texto_ws = "*PRESUPUESTO TECNICO - MANUEL AGUIAR*\n" + "🚗 *Vehiculo:* " + str(dv['marca']) + " " + str(dv['modelo']) + " (" + str(dv['patente']) + ")\n" + "🔧 *Trabajo:* " + str(cat_p) + "\n\n" + "*Procedimiento:*\n" + str(det_p) + "\n\n" + "*Repuestos / Insumos:*\n" + str(rep_p) + "\n\n" + f"💵 *TOTAL:* ${tot_p:,.2f}\n" + f"⏳ *Validez:* {val_p} dias."
                    link_presu = "https://wa.me/" + str(dv['telefono']).replace('+', '').replace('-', '').replace(' ', '').strip() + "?text=" + urllib.parse.quote(texto_ws)
                    st.success("✅ Presupuesto Manuel Aguiar guardado correctamente.")
                    st.markdown(f'<a href="{link_presu}" target="_blank" class="btn-wa">📲 Enviar Presupuesto por WhatsApp</a>', unsafe_allow_html=True)
    conn.close()

# -------------------------------------------------------------
# 6. HISTORIAL GENERAL
# -------------------------------------------------------------
elif opcion == "📊 Historial General":
    st.markdown("## 📊 Registro Histórico de Trabajos Manuel Aguiar")
    conn = get_db()
    df_taller = pd.read_sql_query("SELECT s.fecha AS Fecha, s.patente AS Patente, v.marca AS Marca, v.modelo AS Modelo, s.categoria AS Especialidad, s.km_servicio AS KM, s.trabajo_realizado AS Trabajo, s.garantia AS Garantia, s.costo_total AS Total FROM servicios_taller s LEFT JOIN vehiculos v ON s.patente = v.patente ORDER BY s.fecha DESC", conn)
    conn.close()
    if not df_taller.empty:
        st.dataframe(df_taller, use_container_width=True)
    else:
        st.info("No hay registros Manuel Aguiar en el historial todavía.")
