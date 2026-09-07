import streamlit as st
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
    initial_sidebar_state="expanded"
)
init_db()

# Estilos globales — Paleta Clara Minimalista OEM
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root {
  --bg: #F8FAFC;
  --panel: #FFFFFF;
  --line: #E2E8F0;
  --text: #0F172A;
  --muted: #475569;
  --navy: #0F2B48;
  --blue: #0284C7;
  --orange: #D97706;
  --green: #10B981;
}

html, body, [class*="css"], .stApp {
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  background: var(--bg) !important;
  color: var(--text) !important;
}

.stApp {
  background-color: #F8FAFC !important;
}

h1, h2, h3, h4 {
  color: var(--navy) !important;
  font-weight: 800 !important;
  letter-spacing: -0.025em !important;
}

.block-container {
  padding-top: 1.8rem;
  padding-bottom: 4rem;
  max-width: 1400px;
}

/* Sidebar Limpio y Claro */
[data-testid="stSidebar"] {
  background: #FFFFFF !important;
  border-right: 1px solid #E2E8F0 !important;
}
[data-testid="stSidebar"] * {
  color: #1E293B !important;
}

/* Botones principales con alto contraste */
.stButton > button {
  border: none !important;
  border-radius: 12px !important;
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%) !important;
  color: #FFFFFF !important;
  font-weight: 800 !important;
  font-size: 0.95rem !important;
  min-height: 44px;
  box-shadow: 0 4px 14px rgba(217, 119, 6, 0.25);
  transition: .2s ease;
}
.stButton > button:hover {
  transform: translateY(-1px);
  background: linear-gradient(135deg, #D97706 0%, #B45309 100%) !important;
  box-shadow: 0 6px 18px rgba(217, 119, 6, 0.35);
}

/* Inputs claros con texto 100% legible */
.stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox > div > div {
  background: #FFFFFF !important;
  color: #0F172A !important;
  border: 1.5px solid #CBD5E1 !important;
  border-radius: 10px !important;
  font-weight: 500 !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
  border-color: #0284C7 !important;
  box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.15) !important;
}

/* Métricas limpias */
[data-testid="stMetric"] {
  background: #FFFFFF !important;
  border: 1px solid #E2E8F0 !important;
  border-radius: 14px !important;
  padding: 14px 16px !important;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.04) !important;
}
[data-testid="stMetricLabel"] {
  color: #64748B !important;
  font-size: .78rem !important;
  font-weight: 700 !important;
  text-transform: uppercase;
  letter-spacing: .05em;
}
[data-testid="stMetricValue"] {
  color: #0F2B48 !important;
  font-weight: 800 !important;
}

/* Acordeones */
.streamlit-expanderHeader {
  background: #FFFFFF !important;
  border: 1px solid #E2E8F0 !important;
  border-radius: 12px !important;
  color: #0F2B48 !important;
  font-weight: 700 !important;
}

/* Barra de Marca Superior */
.brandbar {
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
}
.brand-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.brand-mark {
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
}
.brand-name {
  font-size: 1.2rem;
  font-weight: 800;
  color: #0F2B48;
}
.brand-name span {
  color: #D97706;
}
.brand-tag {
  font-size: .8rem;
  color: #64748B;
  margin-top: 2px;
}
.brand-service {
  font-size: .78rem;
  color: #475569;
  text-align: right;
  line-height: 1.5;
}
.brand-service b {
  color: #0284C7;
}

/* Sidebar navigation */
.side-title {
  font-size: .74rem;
  text-transform: uppercase;
  letter-spacing: .12em;
  color: #64748B;
  margin: 10px 0 12px;
  font-weight: 800;
}
.side-nav {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.side-nav a {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border: 1px solid transparent;
  border-radius: 10px;
  color: #334155 !important;
  text-decoration: none !important;
  font-size: .85rem;
  font-weight: 600;
  background: #F8FAFC;
}
.side-nav a:hover {
  background: #F1F5F9;
  border-color: #CBD5E1;
  color: #0F2B48 !important;
}
.side-nav .ico {
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0284C7;
}
.side-nav .active {
  background: #EFF6FF !important;
  border-color: #BFDBFE !important;
  color: #0284C7 !important;
}
.side-nav .active .ico {
  color: #0284C7;
}

/* Hero Banner */
.hero {
  border: 1px solid #CBD5E1;
  border-radius: 20px;
  padding: 30px 34px;
  background: linear-gradient(135deg, #0F2B48 0%, #1E3A5F 100%);
  color: #FFFFFF;
  box-shadow: 0 8px 24px rgba(15, 43, 72, 0.12);
  margin-bottom: 20px;
}
.hero-kicker {
  color: #38BDF8;
  font-size: .78rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .12em;
}
.hero h1 {
  color: #FFFFFF !important;
  font-size: 2.1rem;
  margin: 8px 0;
}
.hero h1 span {
  color: #FBBF24;
}
.hero p {
  color: #E2E8F0;
  max-width: 700px;
  font-size: .96rem;
  line-height: 1.6;
  margin: 0;
}
.hero-line {
  height: 4px;
  width: 90px;
  background: linear-gradient(90deg, #F59E0B, #38BDF8);
  border-radius: 9px;
  margin-top: 18px;
}

/* Feature Grid */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin: 18px 0 8px;
}
.feature {
  min-height: 140px;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 18px;
  background: #FFFFFF;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
  transition: .2s ease;
}
.feature:hover {
  transform: translateY(-2px);
  border-color: #0284C7;
  box-shadow: 0 6px 16px rgba(2, 132, 199, 0.10);
}
.feature .fi {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
  background: #F1F5F9;
}
.feature h3 {
  font-size: .95rem;
  color: #0F2B48 !important;
  margin: 0 0 6px;
}
.feature p {
  font-size: .78rem;
  color: #64748B;
  line-height: 1.45;
  margin: 0;
}
.f-blue .fi { color: #0284C7; background: #E0F2FE; }
.f-yellow .fi { color: #D97706; background: #FEF3C7; }
.f-cyan .fi { color: #0891B2; background: #CFFAFE; }
.f-orange .fi { color: #EA580C; background: #FFEDD5; }
.f-green .fi { color: #10B981; background: #D1FAE5; }
.f-purple .fi { color: #7C3AED; background: #EDE9FE; }

.section-title {
  font-size: .8rem;
  text-transform: uppercase;
  letter-spacing: .12em;
  color: #64748B;
  font-weight: 800;
  margin: 24px 0 12px;
}
.mini-note {
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 12px 16px;
  color: #475569;
  background: #F8FAFC;
  font-size: .82rem;
}

/* Tarjeta de Vehículo */
.veh-card {
  background: linear-gradient(135deg, #0F2B48 0%, #1E3A5F 100%);
  color: #FFFFFF !important;
  border-radius: 16px;
  padding: 20px 24px;
  margin: 10px 0 20px;
  box-shadow: 0 6px 18px rgba(15, 43, 72, 0.15);
}
.veh-card h2 {
  color: #FFFFFF !important;
  margin: 0;
  font-size: 1.35rem;
}
.veh-card p {
  color: #CBD5E1 !important;
  margin: 6px 0 0;
  font-size: .9rem;
}

/* Botón WhatsApp */
.btn-wa {
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
}

.side-divider {
  height: 1px;
  background: #E2E8F0;
  margin: 18px 0;
}

/* Atajos */
.app-shortcuts {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin: 16px 0;
}
.shortcut {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 13px 15px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 14px;
  text-decoration: none !important;
  color: #0F2B48 !important;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03);
}
.shortcut:hover {
  border-color: #0284C7;
  transform: translateY(-1px);
}
.shortcut svg {
  color: #0284C7;
  flex: none;
}
.shortcut strong {
  font-size: .82rem;
  color: #0F2B48;
}
.shortcut span {
  display: block;
  color: #64748B;
  font-size: .72rem;
  margin-top: 2px;
}

/* Perfil */
.profile-card {
  border: 1px solid #E2E8F0;
  border-radius: 20px;
  padding: 26px;
  background: #FFFFFF;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}
.profile-logo {
  width: 70px;
  height: 70px;
  border-radius: 18px;
  background: #F59E0B;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  font-weight: 900;
  font-size: 24px;
  margin-bottom: 14px;
}
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  border: 1px solid #A7F3D0;
  background: #ECFDF5;
  color: #047857;
  border-radius: 999px;
  padding: 6px 12px;
  font-size: .75rem;
  font-weight: 700;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10B981;
}

@media(max-width:900px){
  .feature-grid{grid-template-columns:1fr 1fr;}
  .brand-service{display:none;}
  .bottom-nav{
    display:flex;
    position:fixed;
    z-index:999;
    left:12px;
    right:12px;
    bottom:12px;
    height:64px;
    align-items:center;
    justify-content:space-around;
    background:#FFFFFF;
    border:1px solid #CBD5E1;
    border-radius:18px;
    box-shadow:0 8px 30px rgba(0,0,0,.15);
  }
  .bottom-item{
    width:25%;
    height:100%;
    flex-direction:column;
    gap:2px;
    display:flex;
    align-items:center;
    justify-content:center;
    color:#64748B !important;
    text-decoration:none !important;
  }
  .bottom-active{
    color:#0284C7 !important;
  }
  .bottom-active svg{
    color:#0284C7 !important;
  }
  .block-container{padding-bottom:5.5rem;}
}
@media(max-width:600px){
  .feature-grid{grid-template-columns:1fr;}
  .app-shortcuts{grid-template-columns:1fr 1fr;}
  .hero{padding:22px 20px;}
  .hero h1{font-size:1.6rem;}
  [data-testid="stSidebar"]{display:none!important;}
}
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

# Navegación principal
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
        nav_html += f'<a class="{active}" href="?vista={key}"><span class="ico">{svg_icon(path,19)}</span><span>{label}</span></a>'
    nav_html += '</div>'
    st.markdown(nav_html, unsafe_allow_html=True)
    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-title">Herramientas del taller</div>', unsafe_allow_html=True)
    tool_html = '<div class="side-nav">'
    for key in TALLER_NAV:
        label = VISTAS[key][0]; path = VISTAS[key][1]; active = " active" if vista == key else ""
        tool_html += f'<a class="{active}" href="?vista={key}"><span class="ico">{svg_icon(path,18)}</span><span>{label}</span></a>'
    tool_html += '</div>'
    st.markdown(tool_html, unsafe_allow_html=True)
    st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="mini-note"><b>MANUEL AGUIAR</b><br><span style="color:#0284C7">Electrónica automotriz</span><br>Inyección · A/A · DPF/EGR · AdBlue · Reprogramación · Híbridos y eléctricos</div>', unsafe_allow_html=True)

bottom_html = '<div class="bottom-nav">'
for key, label in APP_NAV:
    path = VISTAS[key][1]; active = " bottom-active" if vista == key else ""
    bottom_html += f'<a class="bottom-item{active}" href="?vista={key}"><span>{svg_icon(path,21)}</span><small>{label}</small></a>'
bottom_html += '</div>'
st.markdown(bottom_html, unsafe_allow_html=True)

# -------------------------------------------------------------
# 0. PORTADA / INICIO (WELCOME SCREEN)
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
                st.session_state["patente_activa"] = pat_in
                st.rerun()

    st.markdown("""<div class="app-shortcuts">
      <a class="shortcut" href="?vista=tarjeta"><span><svg width="21" height="21" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M35 35h130v130H35z M65 70h70 M65 100h70 M65 130h45" stroke="currentColor" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></svg></span><div><strong>Mis vehículos</strong><span>Historial y estado</span></div></a>
      <a class="shortcut" href="?vista=alertas"><span><svg width="21" height="21" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M100 25a55 55 0 0 0-55 55v30l-12 20h134l-12-20V80a55 55 0 0 0-55-55 M85 150a18 18 0 0 0 30 0" stroke="currentColor" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></svg></span><div><strong>Alertas</strong><span>Mantenimientos próximos</span></div></a>
      <a class="shortcut" href="?vista=presupuestos"><span><svg width="21" height="21" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M35 45h130v90H80l-30 25 8-25H35z M65 75h70 M65 105h45" stroke="currentColor" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></svg></span><div><strong>Presupuestos</strong><span>Enviar por WhatsApp</span></div></a>
      <a class="shortcut" href="?vista=historial"><span><svg width="21" height="21" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M35 160V80 M85 160V45 M135 160V20 M25 160h130" stroke="currentColor" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></svg></span><div><strong>Historial</strong><span>Todos los trabajos</span></div></a>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Funciones principales</div>', unsafe_allow_html=True)
    features = [
      ("f-blue", "tarjeta", "Tarjeta Digital del Vehículo", "Toda la información del vehículo, siempre a mano."),
      ("f-yellow", "taller", "Cargar Trabajo de Taller", "Diagnósticos, procedimientos, parámetros, repuestos y garantías."),
      ("f-cyan", "datos", "Registrar y Modificar Datos", "Mantené actualizados los datos del titular y del vehículo."),
      ("f-orange", "alertas", "Alertas Preventivas", "Anticipate a services y mantenimientos según kilometraje y fecha."),
      ("f-green", "presupuestos", "Presupuestos WhatsApp", "Prepará y enviá presupuestos técnicos directamente al cliente."),
      ("f-purple", "historial", "Historial General", "Consultá la evolución de todos los trabajos realizados."),
    ]
    html='<div class="feature-grid">'
    for cls,key,title,desc in features:
        path=VISTAS[key][1]
        html += f'<a href="?vista={key}" style="text-decoration:none;color:inherit"><div class="feature {cls}"><div class="fi">{svg_icon(path,24)}</div><h3>{title}</h3><p>{desc}</p></div></a>'
    html+='</div>'
    st.markdown(html, unsafe_allow_html=True)
    st.markdown('<div class="mini-note" style="margin-top:16px"><b>Concepto:</b> CuidandoMiAuto es la tarjeta adhesiva de mantenimiento, llevada al mundo digital: historial completo, alertas y registros propios o de otros talleres.</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# 1. TARJETA DIGITAL
# -------------------------------------------------------------
elif vista == "tarjeta":
    query_params = st.query_params
    patente_url = query_params.get("patente", "") or st.session_state.get("patente_activa", "")
    patente_url = patente_url.upper()
    
    if os.path.exists("banner.png"):
        st.image("banner.png", use_container_width=True)
    else:
        st.markdown("## Tarjeta Digital del Vehículo")
        
    patente_buscada = st.text_input("Ingresá la Patente del Vehículo:", value=patente_url, placeholder="Ej: GFG135").upper().strip()
    
    if patente_buscada:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT v.*, c.nombre, c.telefono, c.localidad FROM vehiculos v LEFT JOIN clientes c ON v.cliente_id = c.id WHERE v.patente = ?", (patente_buscada,))
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
            
            st.markdown(f'<a href="{link_wa}" target="_blank" class="btn-wa">Compartir Libreta Digital por WhatsApp</a>', unsafe_allow_html=True)
            
            st.markdown("#### Semáforo de Mantenimientos Preventivos")
            km_act = vehiculo['km_actuales'] or 0
            
            col_a, col_b, col_c = st.columns(3)
            int_aceite = vehiculo['intervalo_aceite_km'] or 10000
            rest_aceite = int_aceite - (km_act % int_aceite)
            col_a.metric("Aceite y Filtros", f"En {rest_aceite:,} km", delta=f"-{rest_aceite} km" if rest_aceite < 1500 else "Al día")
            
            int_bujias = vehiculo['intervalo_bujias_km'] or 0
            if "100% Electrico" in str(vehiculo['tipo_propulsion']) or (vehiculo['tipo_propulsion'] == "Turbodiesel Common Rail" and int_bujias == 0):
                col_b.metric("Bujías Encendido", "No Aplica")
            elif int_bujias > 0:
                rest_buj = int_bujias - (km_act % int_bujias)
                col_b.metric("Bujías Encendido", f"En {rest_buj:,} km", delta=f"-{rest_buj} km" if rest_buj < 2500 else "Al día")
            else:
                col_b.metric("Bujías Encendido", "No Configurado")
                
            int_dist = vehiculo['intervalo_distribucion_km'] or 0
            if int_dist == 0:
                col_c.metric("Distribución", "Cadena / Libre Mant.")
            else:
                rest_dist = int_dist - (km_act % int_dist)
                col_c.metric("Kit Distribución", f"En {rest_dist:,} km", delta=f"-{rest_dist} km" if rest_dist < 5000 else "Al día")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            with st.expander("1. Informes Técnicos Oficiales Manuel Aguiar (Descargar PDF)", expanded=True):
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
                            label="Descargar Informe Técnico en PDF",
                            data=pdf_bytes,
                            file_name=f"Informe_{patente_buscada}_{st_item['fecha']}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{st_item['id']}"
                        )
                        st.divider()
                else:
                    st.info("No hay intervenciones registradas aún para este vehículo.")

            with st.expander("2. Historial de Mantenimientos Externos (Libre)", expanded=False):
                cursor.execute("SELECT * FROM servicios_externos WHERE patente = ? ORDER BY fecha DESC, id DESC", (patente_buscada,))
                servicios_e = cursor.fetchall()
                if servicios_e:
                    for se in servicios_e:
                        st.markdown(f"**📅 {se['fecha']} — {se['tipo_mantenimiento']} ({se['km_servicio']:,} km)**")
                        st.write(f"**Establecimiento:** {se['establecimiento'] or 'Particular'}")
                        st.text(se['detalle_materiales'])
                        st.divider()
                else:
                    st.info("No hay mantenimientos externos registrados todavía.")

            with st.expander("3. Anotar Nuevo Mantenimiento (Cliente / Lubricentro)", expanded=False):
                with st.form("form_cliente_externo", clear_on_submit=True):
                    col_f1, col_f2 = st.columns(2)
                    f_ext = col_f1.date_input("Fecha de realización:", date.today())
                    km_ext = col_f2.number_input("Kilometraje actual:", min_value=int(km_act), value=int(km_act), step=500)
                    lugar_ext = st.text_input("Lugar / Lubricentro:", placeholder="Ej: Lubricentro San Martín")
                    
                    st.markdown("**Marcar ítems realizados:**")
                    col_k1, col_k2 = st.columns(2)
                    chk_aceite = col_k1.checkbox("Aceite de Motor")
                    txt_aceite = col_k2.text_input("Marca/Viscosidad Aceite:", placeholder="Ej: Elaion F50 5W-40", disabled=not chk_aceite)
                    chk_f_aceite = st.checkbox("Filtro de Aceite")
                    chk_f_aire = st.checkbox("Filtro de Aire de Motor")
                    chk_f_comb = st.checkbox("Filtro de Combustible")
                    chk_f_hab = st.checkbox("Filtro de Habitáculo / A/C")
                    chk_dist = st.checkbox("Kit de Distribución")
                    chk_bomba = st.checkbox("💧 Bomba de Agua & Refrigerante")
                    chk_frenos = st.checkbox("Pastillas / Discos de Freno")
                    chk_bat = st.checkbox("Batería 12V")
                    chk_neu = st.checkbox("Alineación / Balanceo")
                    
                    obs_extra = st.text_area("Notas u observaciones adicionales:")
                    btn_guardar_ext = st.form_submit_button("Guardar Mantenimiento en Libreta")
                    
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

            with st.expander("4. Generador de Código QR para Sticker del Auto", expanded=False):
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
elif vista == "taller":
    st.markdown("## Cargar Trabajo de Taller")
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
            
            cat_t = st.selectbox("Especialidad / Área de Trabajo:", CATEGORIAS_TALLER)
            
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
                p_c1, p_c2, p_c3 = st.columns(4)
                p_baja = p_c1.text_input("Baja (PSI):", placeholder="32 PSI")
                p_alta = p_c2.text_input("Alta (PSI):", placeholder="210 PSI")
                gas_g = p_c3.text_input("Carga Gas:", placeholder="500g R134a")
                params_str = f"Baja: {p_baja} | Alta: {p_alta} | Carga: {gas_g}" if (p_baja or p_alta or gas_g) else ""
            else:
                params_str = st.text_input("Mediciones / Parámetros leídos:", placeholder="Ej: Caudal inyectores, caída de tensión alternador 14.2V...")

            sw_ecu = ""
            if "Soluciones Electrónicas" in cat_t or "Módulos" in cat_t:
                sw_ecu = st.text_input("Software ECU / Archivo Backup:", placeholder="Ej: Hilux_2.8_DPF_OFF_v2.bin")
            
            trabajo_t = st.text_area("Procedimiento y Trabajo Realizado:*", placeholder="Describí los detalles de la reparación o calibración...")
            repuestos_t = st.text_area("Repuestos / Insumos / Componentes Instalados:", placeholder="Ej: Sensor MAF Bosch, Lámpara H7, Carga R134a...")
            
            c3, c4, c5 = st.columns(3)
            garantia_t = c3.selectbox("Garantía Otorgada:", ["3 Meses", "6 Meses", "12 Meses", "Garantía de Fábrica", "Sin garantía especial"])
            prox_km = c4.number_input("Próximo Control Sugerido (KM) — 0 si no aplica:", min_value=0, step=5000, value=0)
            costo_t = c5.number_input("Importe Total ($):", min_value=0.0, step=1000.0)
            
            btn_guardar_taller = st.form_submit_button("Guardar Trabajo Técnico y Actualizar Odómetro")
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
# 3. REGISTRAR, MODIFICAR Y ELIMINAR DATOS
# -------------------------------------------------------------
elif vista == "datos":
    st.markdown("## Registrar y Modificar Datos")
    
    sec_gestion = st.radio(
        "Seleccionar Acción:",
        ["Alta de Cliente", "Alta de Vehículo", "Modificar Vehículo", "Modificar Cliente", "Eliminar Vehículo", "Eliminar Cliente"],
        horizontal=True
    )
    
    conn = get_db()
    cursor = conn.cursor()
    
    if sec_gestion == "Alta de Cliente":
        with st.form("form_alta_cli", clear_on_submit=True):
            col_c1, col_c2 = st.columns(2)
            nom = col_c1.text_input("Nombre y Apellido / Razón Social:*")
            tel = col_c2.text_input("Teléfono / WhatsApp:* (Ej: 2296123456)")
            dire = col_c1.text_input("Dirección:")
            loc = col_c2.text_input("Localidad:", value="Ayacucho")
            if st.form_submit_button("Guardar Cliente"):
                if nom and tel:
                    cursor.execute("INSERT INTO clientes (nombre, telefono, direccion, localidad) VALUES (?, ?, ?, ?)", (nom, tel, dire, loc))
                    conn.commit()
                    st.success(f"Cliente '{nom}' guardado correctamente.")
                else:
                    st.error("Nombre y Teléfono son obligatorios.")

    elif sec_gestion == "Alta de Vehículo":
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
                
                st.markdown("#### Plan de Mantenimiento Personalizado (KM)")
                col_i1, col_i2, col_i3 = st.columns(3)
                int_aceite = col_i1.number_input("Intervalo Aceite (KM):", value=10000, step=1000)
                int_dist = col_i2.number_input("Intervalo Distribución (KM) — 0 si es cadena:", value=60000, step=10000)
                int_buj = col_i3.number_input("Intervalo Bujías (KM) — 0 si no aplica:", value=30000 if "Nafta" in prop else 0, step=10000)
                
                if st.form_submit_button("Guardar Vehículo"):
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

    elif sec_gestion == "Modificar Vehículo":
        cursor.execute("SELECT patente, marca, modelo FROM vehiculos ORDER BY patente")
        vehiculos_edit = cursor.fetchall()
        if vehiculos_edit:
            map_ve = {f"{v['patente']} — {v['marca']} {v['modelo']}": v['patente'] for v in vehiculos_edit}
            sel_pat_edit = st.selectbox("Seleccionar Vehículo a Modificar:", list(map_ve.keys()))
            pat_a_modificar = map_ve[sel_pat_edit]
            cursor.execute("SELECT * FROM vehiculos WHERE patente = ?", (pat_a_modificar,))
            v_curr = cursor.fetchone()
            if v_curr:
                with st.form("form_editar_veh"):
                    st.write(f"### Editando Datos de: `{pat_a_modificar}`")
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
                    
                    st.markdown("#### Ajustar Intervalos de Servicio (KM)")
                    col_ei1, col_ei2, col_ei3 = st.columns(3)
                    e_int_aceite = col_ei1.number_input("Intervalo Aceite (KM):", value=int(v_curr['intervalo_aceite_km'] or 10000), step=1000)
                    e_int_dist = col_ei2.number_input("Intervalo Distribución (KM):", value=int(v_curr['intervalo_distribucion_km'] or 60000), step=10000)
                    e_int_buj = col_ei3.number_input("Intervalo Bujías (KM):", value=int(v_curr['intervalo_bujias_km'] or 30000), step=5000)
                    
                    if st.form_submit_button("Guardar Cambios del Vehículo"):
                        cursor.execute("UPDATE vehiculos SET marca = ?, modelo = ?, anio = ?, tipo_propulsion = ?, motor = ?, km_actuales = ?, intervalo_aceite_km = ?, intervalo_distribucion_km = ?, intervalo_bujias_km = ? WHERE patente = ?", (e_mar, e_mod, int(e_ani), e_prop, e_mot, int(e_km), int(e_int_aceite), int(e_int_dist), int(e_int_buj), pat_a_modificar))
                        conn.commit()
                        st.success("✅ Vehículo actualizado correctamente.")
                        st.rerun()
        else:
            st.info("No hay vehículos registrados para modificar.")

    elif sec_gestion == "Modificar Cliente":
        cursor.execute("SELECT id, nombre, telefono, direccion, localidad FROM clientes ORDER BY nombre")
        clientes_edit = cursor.fetchall()
        if clientes_edit:
            map_cli_edit = {f"{c['nombre']} ({c['telefono']})": c for c in clientes_edit}
            sel_cli_name = st.selectbox("Seleccionar Cliente a Modificar:", list(map_cli_edit.keys()))
            cli_data = map_cli_edit[sel_cli_name]
            with st.form("form_editar_cliente"):
                st.write(f"### Editando Cliente: `{cli_data['nombre']}`")
                col_mc1, col_mc2 = st.columns(2)
                nuevo_nom = col_mc1.text_input("Nombre y Apellido / Razón Social:", value=cli_data['nombre'])
                nuevo_tel = col_mc2.text_input("Teléfono / WhatsApp:", value=cli_data['telefono'])
                nuevo_dir = col_mc1.text_input("Dirección:", value=cli_data['direccion'] or "")
                nueva_loc = col_mc2.text_input("Localidad:", value=cli_data['localidad'] or "Ayacucho")
                if st.form_submit_button("Guardar Cambios del Cliente"):
                    if nuevo_nom and nuevo_tel:
                        cursor.execute("UPDATE clientes SET nombre = ?, telefono = ?, direccion = ?, localidad = ? WHERE id = ?", (nuevo_nom, nuevo_tel, nuevo_dir, nueva_loc, cli_data['id']))
                        conn.commit()
                        st.success("✅ Cliente actualizado correctamente.")
                        st.rerun()
                    else:
                        st.error("El nombre y el teléfono no pueden quedar vacíos.")
        else:
            st.info("No hay clientes registrados para modificar.")

    elif sec_gestion == "Eliminar Vehículo":
        cursor.execute("SELECT patente, marca, modelo FROM vehiculos ORDER BY patente")
        vehiculos_del = cursor.fetchall()
        if vehiculos_del:
            map_v_del = {f"{v['patente']} — {v['marca']} {v['modelo']}": v['patente'] for v in vehiculos_del}
            sel_v_del = st.selectbox("Seleccionar Vehículo a Eliminar:", list(map_v_del.keys()))
            pat_a_borrar = map_v_del[sel_v_del]
            
            st.error(f"**Atención:** Eliminar la patente **{pat_a_borrar}** borrará también todos los informes técnicos, mantenimientos y registros asociados a este vehículo.")
            
            confirmar_v = st.checkbox(f"Confirmo que deseo eliminar definitivamente el vehículo {pat_a_borrar}")
            if st.button("Eliminar Vehículo Definitivamente"):
                if confirmar_v:
                    cursor.execute("DELETE FROM servicios_taller WHERE patente = ?", (pat_a_borrar,))
                    cursor.execute("DELETE FROM servicios_externos WHERE patente = ?", (pat_a_borrar,))
                    cursor.execute("DELETE FROM presupuestos WHERE patente = ?", (pat_a_borrar,))
                    cursor.execute("DELETE FROM vehiculos WHERE patente = ?", (pat_a_borrar,))
                    conn.commit()
                    st.success(f"✅ Vehículo {pat_a_borrar} e historiales eliminados correctamente.")
                    st.rerun()
                else:
                    st.warning("Marcá la casilla de confirmación para proceder con la eliminación.")
        else:
            st.info("No hay vehículos registrados para eliminar.")

    elif sec_gestion == "Eliminar Cliente":
        cursor.execute("SELECT id, nombre, telefono FROM clientes ORDER BY nombre")
        clientes_del = cursor.fetchall()
        if clientes_del:
            map_c_del = {f"{c['nombre']} ({c['telefono']})": c['id'] for c in clientes_del}
            sel_c_del = st.selectbox("Seleccionar Cliente a Eliminar:", list(map_c_del.keys()))
            cli_id_borrar = map_c_del[sel_c_del]
            
            cursor.execute("SELECT patente, marca, modelo FROM vehiculos WHERE cliente_id = ?", (cli_id_borrar,))
            vehs_asociados = cursor.fetchall()
            
            if vehs_asociados:
                lista_v_txt = ", ".join([f"{v['marca']} {v['modelo']} ({v['patente']})" for v in vehs_asociados])
                st.warning(f"Este cliente tiene vehículos registrados a su nombre: **{lista_v_txt}**.")
            
            st.error("Al eliminar el cliente, podés elegir si desvincular sus vehículos o eliminarlos por completo.")
            
            opcion_borrado = st.radio(
                "¿Qué hacer con los vehículos del cliente?:",
                ["Desvincular vehículos (mantener autos en el sistema sin titular)", "Eliminar cliente y también todos sus vehículos e historiales"]
            )
            
            confirmar_c = st.checkbox("Confirmo que deseo eliminar este cliente")
            if st.button("Eliminar Cliente Definitivamente"):
                if confirmar_c:
                    if "Eliminar cliente y también todos" in opcion_borrado:
                        for v in vehs_asociados:
                            p = v['patente']
                            cursor.execute("DELETE FROM servicios_taller WHERE patente = ?", (p,))
                            cursor.execute("DELETE FROM servicios_externos WHERE patente = ?", (p,))
                            cursor.execute("DELETE FROM presupuestos WHERE patente = ?", (p,))
                        cursor.execute("DELETE FROM vehiculos WHERE cliente_id = ?", (cli_id_borrar,))
                    else:
                        cursor.execute("UPDATE vehiculos SET cliente_id = NULL WHERE cliente_id = ?", (cli_id_borrar,))
                    
                    cursor.execute("DELETE FROM clientes WHERE id = ?", (cli_id_borrar,))
                    conn.commit()
                    st.success("✅ Cliente eliminado correctamente.")
                    st.rerun()
                else:
                    st.warning("Marcá la casilla de confirmación para proceder con la eliminación.")
        else:
            st.info("No hay clientes registrados para eliminar.")
            
    conn.close()

# -------------------------------------------------------------
# 4. ALERTAS PREVENTIVAS
# -------------------------------------------------------------
elif vista == "alertas":
    st.markdown("## Alertas Preventivas — Próximos 30 días")
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
                    alertas_generadas.append({"Patente": v['patente'], "Vehiculo": f"{v['marca']} {v['modelo']}", "Cliente": nombre_cli, "Telefono": tel, "Alerta": "Recambio de Bujías", "Detalle": f"Faltan aprox. {rest_buj:,} km", "Mensaje": f"Hola {nombre_cli}! Te recordamos desde el Centro Técnico Manuel Aguiar que tu {v['marca']} {v['modelo']} ({v['patente']}) está próximo al recambio de bujías ({km:,} km). ¿Querés que reservemos un turno?"})
            if v['intervalo_aceite_km'] and v['intervalo_aceite_km'] > 0:
                rest_aceite = v['intervalo_aceite_km'] - (km % v['intervalo_aceite_km'])
                if rest_aceite <= 1500:
                    alertas_generadas.append({"Patente": v['patente'], "Vehiculo": f"{v['marca']} {v['modelo']}", "Cliente": nombre_cli, "Telefono": tel, "Alerta": "Service Aceite y Filtros", "Detalle": f"Faltan aprox. {rest_aceite:,} km", "Mensaje": f"Hola {nombre_cli}! Tu {v['marca']} {v['modelo']} ({v['patente']}) está próximo al service de aceite y filtros ({km:,} km)."})
            if v['intervalo_distribucion_km'] and v['intervalo_distribucion_km'] > 0:
                rest_dist = v['intervalo_distribucion_km'] - (km % v['intervalo_distribucion_km'])
                if rest_dist <= 5000:
                    alertas_generadas.append({"Patente": v['patente'], "Vehiculo": f"{v['marca']} {v['modelo']}", "Cliente": nombre_cli, "Telefono": tel, "Alerta": "Correa de Distribución", "Detalle": f"Faltan aprox. {rest_dist:,} km", "Mensaje": f"Hola {nombre_cli}! Tu {v['marca']} {v['modelo']} ({v['patente']}) está próximo al reemplazo de correa de distribución ({km:,} km)."})
        if alertas_generadas:
            st.write(f"Se encontraron **{len(alertas_generadas)} alertas activas**:")
            for al in alertas_generadas:
                st.markdown(f"**{al['Vehiculo']}** (`{al['Patente']}`) — *{al['Cliente']}*")
                st.write(f"**{al['Alerta']}** — {al['Detalle']}")
                link_wa = "https://wa.me/" + al['Telefono'] + "?text=" + urllib.parse.quote(al['Mensaje'])
                st.markdown(f'<a href="{link_wa}" target="_blank" class="btn-wa" style="width:100%; text-align:center;">Enviar Recordatorio por WhatsApp</a>', unsafe_allow_html=True)
                st.divider()
        else:
            st.success("No hay vehículos con alertas preventivas para los próximos kilómetros.")
    conn.close()

# -------------------------------------------------------------
# 5. PRESUPUESTOS WHATSAPP
# -------------------------------------------------------------
elif vista == "presupuestos":
    st.markdown("## Presupuestos por WhatsApp")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT v.patente, v.marca, v.modelo, c.nombre, c.telefono FROM vehiculos v LEFT JOIN clientes c ON v.cliente_id = c.id ORDER BY v.patente")
    vehiculos_p = cursor.fetchall()
    if vehiculos_p:
        mapa_vp = {f"{v['patente']} — {v['marca']} {v['modelo']} ({v['nombre']})": v for v in vehiculos_p}
        sel_vp = st.selectbox("Seleccionar Vehículo:", list(mapa_vp.keys()))
        dv = mapa_vp[sel_vp]
        with st.form("form_presupuesto"):
            cat_p = st.selectbox("Especialidad:", CATEGORIAS_TALLER)
            det_p = st.text_area("Detalle de mano de obra y procedimiento:")
            rep_p = st.text_area("Detalle de repuestos y materiales:")
            col_pr1, col_pr2 = st.columns(2)
            val_p = col_pr1.number_input("Validez del Presupuesto (días):", value=15, min_value=1)
            tot_p = col_pr2.number_input("Importe Total ($):", min_value=0.0, step=1000.0)
            
            if st.form_submit_button("Generar y Guardar Presupuesto"):
                if tot_p > 0:
                    cursor.execute("INSERT INTO presupuestos (patente, fecha_emision, categoria, validez_dias, detalle_trabajo, repuestos, total) VALUES (?, ?, ?, ?, ?, ?, ?)", (dv['patente'], str(date.today()), cat_p, int(val_p), det_p, rep_p, float(tot_p)))
                    conn.commit()
                    texto_ws = "*PRESUPUESTO TECNICO - MANUEL AGUIAR*\n" + "*Vehiculo:* " + str(dv['marca']) + " " + str(dv['modelo']) + " (" + str(dv['patente']) + ")\n" + "*Trabajo:* " + str(cat_p) + "\n\n" + "*Procedimiento:*\n" + str(det_p) + "\n\n" + "*Repuestos / Insumos:*\n" + str(rep_p) + "\n\n" + f"*TOTAL:* ${tot_p:,.2f}\n" + f"*Validez:* {val_p} dias."
                    link_presu = "https://wa.me/" + str(dv['telefono']).replace('+', '').replace('-', '').replace(' ', '').strip() + "?text=" + urllib.parse.quote(texto_ws)
                    st.success("✅ Presupuesto guardado correctamente.")
                    st.markdown(f'<a href="{link_presu}" target="_blank" class="btn-wa">Enviar Presupuesto por WhatsApp</a>', unsafe_allow_html=True)
    conn.close()

# -------------------------------------------------------------
# 6. HISTORIAL GENERAL
# -------------------------------------------------------------
elif vista == "historial":
    st.markdown("## 📊 Registro Histórico de Trabajos Manuel Aguiar")
    conn = get_db()
    df_taller = pd.read_sql_query("SELECT s.fecha AS Fecha, s.patente AS Patente, v.marca AS Marca, v.modelo AS Modelo, s.categoria AS Especialidad, s.km_servicio AS KM, s.trabajo_realizado AS Trabajo, s.garantia AS Garantia, s.costo_total AS Total FROM servicios_taller s LEFT JOIN vehiculos v ON s.patente = v.patente ORDER BY s.fecha DESC", conn)
    conn.close()
    if not df_taller.empty:
        st.dataframe(df_taller, use_container_width=True)
    else:
        st.info("No hay registros en el historial todavía.")

# -------------------------------------------------------------
# 7. PERFIL / INFORMACION DEL TALLER
# -------------------------------------------------------------
elif vista == "perfil":
    st.markdown("## Perfil")
    st.markdown("""<div class="profile-card"><div class="profile-logo">MA</div><span class="status-pill"><span class="status-dot"></span> Sistema activo</span><h2 style="margin-top:16px">MANUEL AGUIAR</h2><p style="color:#475569;line-height:1.7">Electrónica Automotriz y mantenimiento especializado.</p><p style="color:#334155;line-height:1.8"><b>Especialidades</b><br>Inyección Electrónica · Aire Acondicionado · DPF / EGR · AdBlue · Reprogramación · Servicio y Mantenimiento de Híbridos y Eléctricos</p></div>""", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Accesos del taller</div>', unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        st.markdown(f'<a class="shortcut" href="?vista=datos"><span>{svg_icon(VISTAS["datos"][1],22)}</span><div><strong>Clientes y vehículos</strong><span>Registrar y modificar datos</span></div></a>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<a class="shortcut" href="?vista=taller"><span>{svg_icon(VISTAS["taller"][1],22)}</span><div><strong>Trabajo de taller</strong><span>Cargar una nueva intervención</span></div></a>', unsafe_allow_html=True)