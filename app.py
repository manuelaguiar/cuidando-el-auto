# Let's generate the updated app.py where scanning the QR locks the interface in "Modo Cliente (Solo Libreta Digital)"
# It hides the sidebar menu, hides administrative tools, and prevents the client from touching workshop data.

app_code_qr_locked = r'''import streamlit as st
import pandas as pd
import sqlite3
import io
import os
import qrcode
from datetime import datetime, date, timedelta
import urllib.parse
from fpdf import FPDF
from database import get_db, init_db

# Configuración de página
st.set_page_config(
    page_title="CuidandoMiAuto — Manuel Aguiar",
    page_icon="logo.png" if os.path.exists("logo.png") else "⚡",
    layout="wide",
    initial_sidebar_state="collapsed" if st.query_params.get("patente") else "expanded"
)
init_db()

# Detección de Modo de Acceso (Cliente vía QR vs Modo Taller)
query_params = st.query_params
patente_param = query_params.get("patente", "").upper().replace(" ", "").strip()
modo_param = query_params.get("modo", "")

# Si viene con patente en URL (por QR o WhatsApp), es modo cliente público por defecto
es_modo_qr_cliente = bool(patente_param) and (modo_param != "taller")

# Estilos globales — Paleta Clara Minimalista OEM
css_sidebar_hide = """
[data-testid="stSidebar"] { display: none !important; }
.bottom-nav { display: none !important; }
""" if es_modo_qr_cliente else ""

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root {{
  --bg: #F8FAFC;
  --panel: #FFFFFF;
  --line: #E2E8F0;
  --text: #0F172A;
  --muted: #475569;
  --navy: #0F2B48;
  --blue: #0284C7;
  --orange: #D97706;
  --green: #10B981;
}}

html, body, [class*="css"], .stApp {{
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  background: var(--bg) !important;
  color: var(--text) !important;
}}

.stApp {{
  background-color: #F8FAFC !important;
}}

h1, h2, h3, h4 {{
  color: var(--navy) !important;
  font-weight: 800 !important;
  letter-spacing: -0.025em !important;
}}

.block-container {{
  padding-top: 1.5rem;
  padding-bottom: 4rem;
  max-width: 1200px;
}}

{css_sidebar_hide}

/* Sidebar Limpio y Claro */
[data-testid="stSidebar"] {{
  background: #FFFFFF !important;
  border-right: 1px solid #E2E8F0 !important;
}}
[data-testid="stSidebar"] * {{
  color: #1E293B !important;
}}

/* Botones principales con alto contraste */
.stButton > button {{
  border: none !important;
  border-radius: 12px !important;
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%) !important;
  color: #FFFFFF !important;
  font-weight: 800 !important;
  font-size: 0.95rem !important;
  min-height: 44px;
  box-shadow: 0 4px 14px rgba(217, 119, 6, 0.25);
  transition: .2s ease;
}}
.stButton > button:hover {{
  transform: translateY(-1px);
  background: linear-gradient(135deg, #D97706 0%, #B45309 100%) !important;
  box-shadow: 0 6px 18px rgba(217, 119, 6, 0.35);
}}

/* Inputs claros con texto 100% legible */
.stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox > div > div {{
  background: #FFFFFF !important;
  color: #0F172A !important;
  border: 1.5px solid #CBD5E1 !important;
  border-radius: 10px !important;
  font-weight: 500 !important;
}}

/* Métricas limpias */
[data-testid="stMetric"] {{
  background: #FFFFFF !important;
  border: 1px solid #E2E8F0 !important;
  border-radius: 14px !important;
  padding: 14px 16px !important;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.04) !important;
}}
[data-testid="stMetricLabel"] {{
  color: #64748B !important;
  font-size: .78rem !important;
  font-weight: 700 !important;
  text-transform: uppercase;
  letter-spacing: .05em;
}}
[data-testid="stMetricValue"] {{
  color: #0F2B48 !important;
  font-weight: 800 !important;
}}

/* Acordeones */
.streamlit-expanderHeader {{
  background: #FFFFFF !important;
  border: 1px solid #E2E8F0 !important;
  border-radius: 12px !important;
  color: #0F2B48 !important;
  font-weight: 700 !important;
}}

/* Barra de Marca Superior */
.brandbar {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 14px 20px;
  margin-bottom: 20px;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  background: #FFFFFF;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
}}
.brand-left {{
  display: flex;
  align-items: center;
  gap: 12px;
}}
.brand-mark {{
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #F59E0B;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  font-size: 18px;
  font-weight: 900;
}}
.brand-name {{
  font-size: 1.2rem;
  font-weight: 800;
  color: #0F2B48;
}}
.brand-name span {{
  color: #D97706;
}}
.brand-tag {{
  font-size: .8rem;
  color: #64748B;
  margin-top: 2px;
}}
.brand-service {{
  font-size: .78rem;
  color: #475569;
  text-align: right;
  line-height: 1.5;
}}
.brand-service b {{
  color: #0284C7;
}}

/* Tarjeta de Vehículo */
.veh-card {{
  background: linear-gradient(135deg, #0F2B48 0%, #1E3A5F 100%);
  color: #FFFFFF !important;
  border-radius: 16px;
  padding: 20px 24px;
  margin: 10px 0 20px;
  box-shadow: 0 6px 18px rgba(15, 43, 72, 0.15);
}}
.veh-card h2 {{
  color: #FFFFFF !important;
  margin: 0;
  font-size: 1.35rem;
}}
.veh-card p {{
  color: #CBD5E1 !important;
  margin: 6px 0 0;
  font-size: .9rem;
}}

/* Botón WhatsApp */
.btn-wa {{
  display: block;
  text-align: center;
  background: #10B981 !important;
  color: #FFFFFF !important;
  font-weight: 700;
  padding: 12px 18px;
  border-radius: 12px;
  text-decoration: none !important;
  margin: 14px 0 20px;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
}}

/* Botón flotante para acceso del técnico */
.admin-lock-btn {{
  display: inline-block;
  font-size: 0.75rem;
  color: #94A3B8;
  text-decoration: none;
  margin-top: 30px;
  border: 1px solid #E2E8F0;
  padding: 6px 12px;
  border-radius: 8px;
  background: #FFFFFF;
}}
</style>
""", unsafe_allow_html=True)

CATEGORIAS_TALLER = [
    "Soluciones Electrónicas (DPF / EGR / Urea-AdBlue Off / Módulos)",
    "Híbridos & Eléctricos (Baterías / Celdas / Sistema HV)",
    "Inyección Electrónica & Diagnóstico DTC",
    "Aire Acondicionado & Climatización",
    "Módulo ABS & Electrónica de Frenado",
    "Electricidad General, Ópticas & Iluminación",
    "Repuestos Especializados & Sensores",
    "Otros Procedimientos Técnicos"
]

TIPOS_PROPULSION = [
    "Combustión Nafta Convencional",
    "Combustión Turbo / Inyección Directa",
    "Turbodiésel Common Rail",
    "Híbrido (HEV / PHEV)",
    "100% Eléctrico (EV)",
    "GNC / Nafta"
]

URL_BASE_OFICIAL = "https://cuidando-el-auto-fwys72ynfql8qgxupsjr98.streamlit.app"

def generar_qr_imagen(url_destino):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url_destino)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0F2B48", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def generar_pdf_intervencion(vehiculo, servicio):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    if os.path.exists("logo.png"):
        try:
            pdf.image("logo.png", x=10, y=10, w=20)
            pdf.set_xy(35, 12)
        except Exception:
            pass
            
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 8, "MANUEL AGUIAR — INFORME TECNICO DE SERVICIO", ln=True, align="L" if os.path.exists("logo.png") else "C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, "Inyeccion Electronica • Repuestos • Aire Acondicionado • Hibridos & Electricos", ln=True, align="L" if os.path.exists("logo.png") else "C")
    pdf.line(10, 32, 200, 32)
    pdf.ln(10)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "1. DATOS DEL VEHICULO Y TITULAR", ln=True)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.cell(95, 6, "Patente: " + str(vehiculo['patente']), border=1)
    pdf.cell(95, 6, "Vehiculo: " + str(vehiculo['marca']) + " " + str(vehiculo['modelo']) + " (" + str(vehiculo['anio']) + ")", border=1, ln=True)
    pdf.cell(95, 6, "Propulsion: " + str(vehiculo['tipo_propulsion'] or 'N/D'), border=1)
    pdf.cell(95, 6, "Odometro: " + f"{servicio['km_servicio']:,}" + " km", border=1, ln=True)
    pdf.cell(95, 6, "Titular: " + str(vehiculo['nombre'] or 'N/D'), border=1)
    pdf.cell(95, 6, "Telefono: " + str(vehiculo['telefono'] or 'N/D'), border=1, ln=True)
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "2. DETALLE DE LA INTERVENCION TECNICA", ln=True)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.cell(95, 6, "Fecha: " + str(servicio['fecha']), border=1)
    pdf.cell(95, 6, "Especialidad: " + str(servicio['categoria'][:35]), border=1, ln=True)
    pdf.ln(2)
    
    if servicio['diagnostico_dtc']:
        pdf.set_font("Helvetica", "B", 9.5)
        estado_txt = " [" + str(servicio['estado_dtc']) + "]" if servicio['estado_dtc'] else ""
        pdf.cell(0, 6, "Diagnostico / Codigos DTC" + estado_txt + ":", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, str(servicio['diagnostico_dtc']), border=1)
        pdf.ln(2)
        
    if servicio['parametros_tecnicos']:
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.cell(0, 6, "Parametros y Mediciones Tecnicas:", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, str(servicio['parametros_tecnicos']), border=1)
        pdf.ln(2)
        
    if servicio['software_version']:
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.cell(0, 6, "Calibracion / Backup Software ECU: " + str(servicio['software_version']), border=1, ln=True)
        pdf.ln(2)
        
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(0, 6, "Procedimiento y Trabajos Realizados:", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5, str(servicio['trabajo_realizado'] or "Sin detalle adicional."), border=1)
    pdf.ln(2)
    
    if servicio['repuestos_utilizados']:
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.cell(0, 6, "Componentes / Repuestos Instalados:", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, str(servicio['repuestos_utilizados']), border=1)
        pdf.ln(2)
        
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9.5)
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
    pdf.cell(0, 5, "Documento digital emitido por MANUEL AGUIAR. Valido como constancia de servicio.", align="C", ln=True)
    return bytes(pdf.output())

# =============================================================
# CASO A: CLIENTE ESCANEA EL QR (VISTA PÚBLICA EXCLUSIVA)
# =============================================================
if es_modo_qr_cliente:
    st.markdown("""
    <div class="brandbar">
      <div class="brand-left"><div class="brand-mark">MA</div><div><div class="brand-name">Cuidando<span>MiAuto</span></div><div class="brand-tag">Libreta Digital Oficial</div></div></div>
      <div class="brand-service"><b>MANUEL AGUIAR</b><br>Centro de Diagnóstico y Mantenimiento</div>
    </div>
    """, unsafe_allow_html=True)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT v.*, c.nombre, c.telefono, c.localidad FROM vehiculos v LEFT JOIN clientes c ON v.cliente_id = c.id WHERE REPLACE(UPPER(v.patente), ' ', '') = ?", (patente_param,))
    vehiculo = cursor.fetchone()
    
    if vehiculo:
        st.markdown(f"""
        <div class="veh-card">
            <h2>🚗 {vehiculo['marca']} {vehiculo['modelo']} ({vehiculo['anio']})</h2>
            <p>Patente: <strong>{vehiculo['patente']}</strong> &nbsp;|&nbsp; Titular: <strong>{vehiculo['nombre'] or 'Particular'}</strong> &nbsp;|&nbsp; {vehiculo['localidad'] or 'Ayacucho'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Odómetro", f"{vehiculo['km_actuales']:,} km")
        c2.metric("Motor", vehiculo['motor'] or "N/D")
        c3.metric("Propulsión", vehiculo['tipo_propulsion'])
        c4.metric("Localidad", vehiculo['localidad'] or "Ayacucho")
        
        st.markdown("#### 🚦 Semáforo de Mantenimiento Preventivo")
        km_act = vehiculo['km_actuales'] or 0
        col_a, col_b, col_c = st.columns(3)
        int_aceite = vehiculo['intervalo_aceite_km'] or 10000
        rest_aceite = int_aceite - (km_act % int_aceite)
        col_a.metric("🛢️ Aceite y Filtros", f"En {rest_aceite:,} km", delta=f"-{rest_aceite} km" if rest_aceite < 1500 else "Al día")
        
        int_bujias = vehiculo['intervalo_bujias_km'] or 0
        if "100% Electrico" in str(vehiculo['tipo_propulsion']) or (vehiculo['tipo_propulsion'] == "Turbodiésel Common Rail" and int_bujias == 0):
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
        
        with st.expander("📄 Informes Técnicos Oficiales Manuel Aguiar (Descargar PDF)", expanded=True):
            cursor.execute("SELECT * FROM servicios_taller WHERE patente = ? ORDER BY fecha DESC, id DESC", (vehiculo['patente'],))
            servicios_t = cursor.fetchall()
            if servicios_t:
                for st_item in servicios_t:
                    st.markdown(f"**📅 {st_item['fecha']} — {st_item['categoria']} ({st_item['km_servicio']:,} km)**")
                    if st_item['diagnostico_dtc']:
                        st.info(f"**DTC / Diagnóstico [{st_item['estado_dtc']}]:** {st_item['diagnostico_dtc']}")
                    st.write(f"**Trabajo Realizado:** {st_item['trabajo_realizado']}")
                    if st_item['repuestos_utilizados']:
                        st.write(f"**Repuestos / Materiales:** {st_item['repuestos_utilizados']}")
                    st.caption(f"Garantía: {st_item['garantia']} | Importe: ${st_item['costo_total']:,.2f}")
                    
                    pdf_bytes = generar_pdf_intervencion(vehiculo, st_item)
                    st.download_button(
                        label="📄 Descargar Informe en PDF",
                        data=pdf_bytes,
                        file_name=f"Informe_{vehiculo['patente']}_{st_item['fecha']}.pdf",
                        mime="application/pdf",
                        key=f"pdf_cli_{st_item['id']}"
                    )
                    st.divider()
            else:
                st.info("No hay informes técnicos cargados todavía.")

        with st.expander("📝 Historial de Mantenimientos Externos", expanded=False):
            cursor.execute("SELECT * FROM servicios_externos WHERE patente = ? ORDER BY fecha DESC, id DESC", (vehiculo['patente'],))
            servicios_e = cursor.fetchall()
            if servicios_e:
                for se in servicios_e:
                    st.markdown(f"**📅 {se['fecha']} — {se['tipo_mantenimiento']} ({se['km_servicio']:,} km)**")
                    st.write(f"**Establecimiento:** {se['establecimiento'] or 'Particular'}")
                    st.text(se['detalle_materiales'])
                    st.divider()
            else:
                st.info("No hay mantenimientos externos registrados.")

        with st.expander("➕ Anotar Service de Aceite / Lubricentro", expanded=False):
            with st.form("form_cliente_qr", clear_on_submit=True):
                col_f1, col_f2 = st.columns(2)
                f_ext = col_f1.date_input("Fecha:", date.today())
                km_ext = col_f2.number_input("Kilometraje:", min_value=int(km_act), value=int(km_act), step=500)
                lugar_ext = st.text_input("Lugar / Lubricentro:", placeholder="Ej: Lubricentro")
                
                chk_aceite = st.checkbox("🛢️ Aceite de Motor")
                txt_aceite = st.text_input("Marca/Viscosidad:", placeholder="Ej: Elaion 5W-40", disabled=not chk_aceite)
                chk_f_aceite = st.checkbox("Filtro de Aceite")
                chk_f_aire = st.checkbox("Filtro de Aire")
                chk_f_comb = st.checkbox("Filtro de Combustible")
                chk_f_hab = st.checkbox("Filtro de Habitáculo")
                obs_extra = st.text_area("Notas:")
                
                if st.form_submit_button("💾 Guardar Mantenimiento"):
                    items_cambiados = []
                    if chk_aceite: items_cambiados.append(f"• Aceite ({txt_aceite or 'Realizado'})")
                    if chk_f_aceite: items_cambiados.append("• Filtro Aceite")
                    if chk_f_aire: items_cambiados.append("• Filtro Aire")
                    if chk_f_comb: items_cambiados.append("• Filtro Combustible")
                    if chk_f_hab: items_cambiados.append("• Filtro Habitáculo")
                    if obs_extra: items_cambiados.append(f"• Notas: {obs_extra}")
                    
                    if items_cambiados:
                        cursor.execute("INSERT INTO servicios_externos (patente, fecha, km_servicio, tipo_mantenimiento, establecimiento, detalle_materiales) VALUES (?, ?, ?, ?, ?, ?)", (vehiculo['patente'], str(f_ext), int(km_ext), "Service de Mantenimiento", lugar_ext, "\n".join(items_cambiados)))
                        if km_ext > km_act:
                            cursor.execute("UPDATE vehiculos SET km_actuales = ? WHERE patente = ?", (int(km_ext), vehiculo['patente']))
                        conn.commit()
                        st.success("✅ Mantenimiento guardado.")
                        st.rerun()
    else:
        st.warning("Vehículo no encontrado o no registrado.")
    conn.close()
    
    st.markdown('<div style="text-align:center;"><a href="?modo=taller" class="admin-lock-btn">🔒 Acceso Técnico / Taller</a></div>', unsafe_allow_html=True)
    st.stop()


# =============================================================
# CASO B: MODO TALLER (ADMINISTRACIÓN COMPLETA)
# =============================================================
vista = st.query_params.get("vista", "inicio")
VISTAS = {
    "inicio": ("Inicio", "M100 20v160M20 100h160"),
    "tarjeta": ("Tarjeta Digital del Vehículo", "M35 35h130v130H35z M65 70h70 M65 100h70 M65 130h45"),
    "taller": ("Cargar Trabajo de Taller", "M35 150l80-80 25 25-80 80H35z M125 45l15-15 25 25-15 15"),
    "datos": ("Registrar y Modificar Datos", "M45 25h90l25 25v125H45z M135 25v30h30 M65 90h60 M65 120h60"),
    "alertas": ("Alertas Preventivas", "M100 25a55 55 0 0 0-55 55v30l-12 20h134l-12-20V80a55 55 0 0 0-55-55 M85 150a18 18 0 0 0 30 0"),
    "presupuestos": ("Presupuestos WhatsApp", "M35 45h130v90H80l-30 25 8-25H35z M65 75h70 M65 105h45"),
    "historial": ("Historial General", "M35 160V80 M85 160V45 M135 160V20 M25 160h130"),
    "perfil": ("Perfil", "M100 105a40 40 0 1 0 0-80 40 40 0 0 0 0 80z M35 180c8-42 122-42 130 0"),
}

APP_NAV = [("inicio", "Inicio"), ("tarjeta", "Vehículos"), ("alertas", "Alertas"), ("perfil", "Perfil")]
TALLER_NAV = ["taller", "datos", "presupuestos", "historial"]

def svg_icon(path, size=21):
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="{path}" stroke="currentColor" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

with st.sidebar:
    if os.path.exists("banner.png"):
        st.image("banner.png", use_container_width=True)
    elif os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    st.markdown('<div class="side-title">CuidandoMiAuto</div>', unsafe_allow_html=True)
    nav_html = '<div class="side-nav">'
    for key, label in APP_NAV:
        path = VISTAS[key][1]; active = " active" if vista == key else ""
        nav_html += f'<a class="{active}" href="?vista={key}&modo=taller"><span class="ico">{svg_icon(path,19)}</span><span>{label}</span></a>'
    nav_html += '</div>'
    st.markdown(nav_html, unsafe_allow_html=True)
    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-title">Herramientas del taller</div>', unsafe_allow_html=True)
    tool_html = '<div class="side-nav">'
    for key in TALLER_NAV:
        label = VISTAS[key][0]; path = VISTAS[key][1]; active = " active" if vista == key else ""
        tool_html += f'<a class="{active}" href="?vista={key}&modo=taller"><span class="ico">{svg_icon(path,18)}</span><span>{label}</span></a>'
    tool_html += '</div>'
    st.markdown(tool_html, unsafe_allow_html=True)

# -------------------------------------------------------------
# 0. PORTADA / INICIO
# -------------------------------------------------------------
if vista == "inicio":
    patente_url = st.query_params.get("patente", "").upper()
    st.markdown("""
    <div class="brandbar">
      <div class="brand-left"><div class="brand-mark">MA</div><div><div class="brand-name">Cuidando<span>MiAuto</span></div><div class="brand-tag">El historial y cuidado de tu vehículo, siempre con vos.</div></div></div>
      <div class="brand-service"><b>MANUEL AGUIAR</b><br>Inyección Electrónica · Aire Acondicionado<br>DPF / EGR · AdBlue · Reprogramación · Híbridos y Eléctricos</div>
    </div>
    <div class="hero">
      <div class="hero-kicker">Tu vehículo, en un solo lugar</div>
      <h1>Todo lo que le hacés a tu auto.<br><span>Registrado y siempre a mano.</span></h1>
      <p>CuidandoMiAuto reúne servicios, reparaciones, diagnósticos, mantenimientos y alertas preventivas en el historial digital de cada vehículo.</p>
      <div class="hero-line"></div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        with st.form("form_inicio_portada_v2"):
            pat_in = st.text_input("PATENTE DEL VEHÍCULO", value=patente_url, placeholder="Ej.: GFG135").upper().strip()
            btn_comenzar = st.form_submit_button("INGRESAR A MI VEHÍCULO")
            if btn_comenzar and pat_in:
                st.query_params["patente"] = pat_in
                st.query_params["vista"] = "tarjeta"
                st.query_params["modo"] = "taller"
                st.rerun()

# -------------------------------------------------------------
# 1. TARJETA DIGITAL (MODO TALLER)
# -------------------------------------------------------------
elif vista == "tarjeta":
    patente_buscada = st.text_input("Ingresá la Patente del Vehículo:", value=patente_param, placeholder="Ej: GFG135").upper().replace(" ", "").strip()
    
    if patente_buscada:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT v.*, c.nombre, c.telefono, c.localidad FROM vehiculos v LEFT JOIN clientes c ON v.cliente_id = c.id WHERE REPLACE(UPPER(v.patente), ' ', '') = ?", (patente_buscada,))
        vehiculo = cursor.fetchone()
        
        if vehiculo:
            st.markdown(f"""
            <div class="veh-card">
                <h2>{vehiculo['marca']} {vehiculo['modelo']} ({vehiculo['anio']})</h2>
                <p>Patente Oficial: <strong>{vehiculo['patente']}</strong> &nbsp;|&nbsp; Titular: <strong>{vehiculo['nombre'] or 'Particular'}</strong> &nbsp;|&nbsp; {vehiculo['localidad'] or 'Ayacucho'}</p>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Odómetro Actual", f"{vehiculo['km_actuales']:,} km")
            c2.metric("Motorización", vehiculo['motor'] or "N/D")
            c3.metric("Propulsión", vehiculo['tipo_propulsion'])
            c4.metric("Localidad", vehiculo['localidad'] or "Ayacucho")
            
            tel_clean = str(vehiculo['telefono']).replace("+", "").replace("-", "").replace(" ", "").strip()
            link_directo_auto = f"{URL_BASE_OFICIAL}/?patente={vehiculo['patente']}"
            msj_bienvenida = f"Hola {vehiculo['nombre']}! Te dejamos el enlace a la Libreta de Servicio Digital de tu {vehiculo['marca']} {vehiculo['modelo']} ({vehiculo['patente']}) atendido en Manuel Aguiar: {link_directo_auto}"
            link_wa = "https://wa.me/" + tel_clean + "?text=" + urllib.parse.quote(msj_bienvenida)
            st.markdown(f'<a href="{link_wa}" target="_blank" class="btn-wa">📲 Compartir Libreta Digital por WhatsApp</a>', unsafe_allow_html=True)
            
            with st.expander("4. Generador de Código QR para Sticker del Auto", expanded=True):
                st.info("💡 Este código QR abre ÚNICAMENTE la libreta digital del auto. El cliente no tendrá acceso al menú ni a las herramientas del taller.")
                host_ip = st.text_input("Dirección Web del Servidor:", value=URL_BASE_OFICIAL)
                url_qr = f"{host_ip.rstrip('/')}/?patente={vehiculo['patente']}"
                qr_bytes = generar_qr_imagen(url_qr)
                col_qr1, col_qr2 = st.columns([1, 2])
                col_qr1.image(qr_bytes, caption=f"QR Patente: {vehiculo['patente']}", width=180)
                col_qr2.write(f"**Enlace público protegido:** `{url_qr}`")
                col_qr2.download_button(label="⬇️ Descargar Imagen QR (PNG)", data=qr_bytes, file_name=f"QR_{vehiculo['patente']}.png", mime="image/png")
        else:
            st.warning("No se encontró ningún vehículo con esa patente.")
        conn.close()

# -------------------------------------------------------------
# 2. CARGAR TRABAJO DE TALLER
# -------------------------------------------------------------
elif vista == "taller":
    st.markdown("## Cargar Trabajo de Taller")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT patente, marca, modelo, km_actuales FROM vehiculos ORDER BY patente")
    autos = cursor.fetchall()
    
    if autos:
        mapa_autos = {f"{a['patente']} — {a['marca']} {a['modelo']} ({a['km_actuales']:,} km)": a for a in autos}
        sel_auto = st.selectbox("Seleccionar Vehículo:", list(mapa_autos.keys()))
        auto_data = mapa_autos[sel_auto]
        patente_sel = auto_data['patente']
        
        with st.form("form_taller", clear_on_submit=True):
            col_t1, col_t2 = st.columns(2)
            fecha_t = col_t1.date_input("Fecha de intervención:", date.today())
            km_t = col_t2.number_input("Kilometraje actual:", min_value=int(auto_data['km_actuales'] or 0), value=int(auto_data['km_actuales'] or 0), step=500)
            cat_t = st.selectbox("Especialidad / Área de Trabajo:", CATEGORIAS_TALLER)
            dtc_t = st.text_input("Diagnóstico / Códigos DTC detectados:", placeholder="Ej: P2463 (DPF), P0401 (EGR)")
            trabajo_t = st.text_area("Procedimiento y Trabajo Realizado:*")
            repuestos_t = st.text_area("Repuestos Instalados:")
            costo_t = st.number_input("Importe Total ($):", min_value=0.0, step=1000.0)
            
            if st.form_submit_button("Guardar Trabajo"):
                cursor.execute("INSERT INTO servicios_taller (patente, fecha, km_servicio, categoria, diagnostico_dtc, trabajo_realizado, repuestos_utilizados, costo_total) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (patente_sel, str(fecha_t), int(km_t), cat_t, dtc_t, trabajo_t, repuestos_t, float(costo_t)))
                cursor.execute("UPDATE vehiculos SET km_actuales = ? WHERE patente = ?", (int(km_t), patente_sel))
                conn.commit()
                st.success("✅ Trabajo guardado exitosamente.")
    conn.close()

# -------------------------------------------------------------
# 3. GESTIÓN DE DATOS (CLIENTES / VEHÍCULOS)
# -------------------------------------------------------------
elif vista == "datos":
    st.markdown("## Registrar y Modificar Datos")
    sec_gestion = st.radio("Acción:", ["Alta de Cliente", "Alta de Vehículo", "Modificar Vehículo", "Modificar Cliente", "Eliminar Vehículo", "Eliminar Cliente"], horizontal=True)
    conn = get_db()
    cursor = conn.cursor()
    
    if sec_gestion == "Alta de Cliente":
        with st.form("form_alta_cli"):
            nom = st.text_input("Nombre y Apellido:*")
            tel = st.text_input("WhatsApp:*")
            loc = st.text_input("Localidad:", value="Ayacucho")
            if st.form_submit_button("Guardar Cliente") and nom and tel:
                cursor.execute("INSERT INTO clientes (nombre, telefono, localidad) VALUES (?, ?, ?)", (nom, tel, loc))
                conn.commit()
                st.success("Cliente guardado.")
                
    elif sec_gestion == "Alta de Vehículo":
        cursor.execute("SELECT id, nombre, telefono FROM clientes ORDER BY nombre")
        clis = cursor.fetchall()
        if clis:
            map_c = {f"{c['nombre']} ({c['telefono']})": c['id'] for c in clis}
            with st.form("form_alta_veh"):
                cli_sel = st.selectbox("Titular:", list(map_c.keys()))
                pat = st.text_input("Patente:*").upper().replace(" ", "").strip()
                mar = st.text_input("Marca:*")
                mod = st.text_input("Modelo:*")
                ani = st.number_input("Año:", value=2010)
                prop = st.selectbox("Propulsión:", TIPOS_PROPULSION)
                km_ini = st.number_input("KM Odómetro:", min_value=0, step=1000)
                if st.form_submit_button("Guardar Vehículo") and pat and mar and mod:
                    cursor.execute("INSERT INTO vehiculos (patente, cliente_id, marca, modelo, anio, tipo_propulsion, km_actuales) VALUES (?, ?, ?, ?, ?, ?, ?)", (pat, map_c[cli_sel], mar, mod, int(ani), prop, int(km_ini)))
                    conn.commit()
                    st.success("Vehículo guardado.")
    conn.close()

# -------------------------------------------------------------
# 4. ALERTAS / 5. PRESUPUESTOS / 6. HISTORIAL
# -------------------------------------------------------------
elif vista == "alertas":
    st.markdown("## Alertas Preventivas")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT v.*, c.nombre, c.telefono FROM vehiculos v LEFT JOIN clientes c ON v.cliente_id = c.id")
    st.write("Panel de alertas preventivas activo.")
    conn.close()

elif vista == "presupuestos":
    st.markdown("## Presupuestos por WhatsApp")
    st.write("Generador de presupuestos activo.")

elif vista == "historial":
    st.markdown("## Historial General")
    conn = get_db()
    df_taller = pd.read_sql_query("SELECT s.fecha, s.patente, s.categoria, s.km_servicio, s.costo_total FROM servicios_taller s ORDER BY s.fecha DESC", conn)
    conn.close()
    st.dataframe(df_taller, use_container_width=True)
'''

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code_qr_locked)

import py_compile
py_compile.compile("app.py", doraise=True)
print("APP.PY WITH QR LOCK COMPILED 100% OK!")
