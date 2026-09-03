# Let's create an optimized mobile-first version of app.py:
# 1. Custom CSS injecting bigger typography, touch-friendly buttons, and high readability for phones.
# 2. Replacing horizontal tabs on "Tarjeta Digital" (PDF, Historial, Cliente, QR) with vertical layout (expanders or direct vertical sections) so users don't need horizontal scrolling.
# 3. Ensuring 100% clean python syntax and compiling with py_compile.

mobile_app_code = r'''import streamlit as st
import pandas as pd
import sqlite3
import io
import qrcode
from datetime import datetime, date, timedelta
import urllib.parse
from fpdf import FPDF
from database import get_db, init_db

# Configuracion inicial optimizada
st.set_page_config(page_title="Centro Tecnico Especializado", page_icon="⚡", layout="wide")
init_db()

# Inyeccion de CSS para vista movil comoda y legible
st.markdown("""
<style>
    /* Aumento de tipografia y legibilidad general para celulares */
    html, body, [class*="css"] {
        font-size: 16px !important;
    }
    h1 {
        font-size: 1.6rem !important;
    }
    h2, h3 {
        font-size: 1.3rem !important;
    }
    p, label, span, input, select, textarea {
        font-size: 1.05rem !important;
    }
    /* Botones mas grandes y comodos para tocar con el pulgar */
    .stButton > button {
        width: 100%;
        padding: 12px 20px !important;
        font-size: 1.1rem !important;
        border-radius: 8px !important;
        margin-top: 5px;
        margin-bottom: 5px;
    }
    /* Espaciado de metricas y semaforos */
    [data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
    }
</style>
""", unsafe_allow_html=True)

CATEGORIAS_TALLER = [
    "💻 Soluciones Electronicas (DPF / EGR / Urea-AdBlue Off / Modulos)",
    "⚡ Hibridos & Electricos (Baterias / Celdas / Sistema HV)",
    "🔌 Inyeccion Electronica & Diagnostico DTC",
    "❄️ Aire Acondicionado & Climatizacion",
    "🛑 Modulo ABS & Electronica de Frenado",
    "💡 Electricidad General, Opticas & Iluminacion",
    "📦 Repuestos Especializados & Sensores",
    "🔧 Otros Procedimientos Tecnicos"
]

TIPOS_PROPULSION = [
    "Combustion Nafta Convencional",
    "Combustion Turbo / Inyeccion Directa",
    "Turbodiesel Common Rail",
    "Hibrido (HEV / PHEV)",
    "100% Electrico (EV)",
    "GNC / Nafta"
]

URL_BASE_OFICIAL = "https://cuidando-el-auto-fwys72ynfql8qgxupsjr98.streamlit.app"

def generar_qr_imagen(url_destino):
    qr = qrcode.QRCode(version=1, box_size=10, border=3)
    qr.add_data(url_destino)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
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
    pdf.cell(0, 6, "Centro de Diagnostico Electronico, Climatizacion & Vehiculos Especializados", ln=True, align="C")
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
    pdf.cell(0, 5, "Documento digital emitido por el Centro Tecnico. Valido como constancia de servicio.", align="C", ln=True)
    return bytes(pdf.output())

st.sidebar.title("⚡ Centro Tecnico")
opcion = st.sidebar.radio(
    "Menu Principal",
    [
        "📋 Tarjeta Digital del Vehiculo",
        "🛠️ Cargar Trabajo de Taller",
        "➕ Registrar y Modificar Datos",
        "🔔 Alertas Preventivas (30 Dias)",
        "💼 Presupuestos WhatsApp",
        "📊 Historial General"
    ]
)

# -------------------------------------------------------------
# 1. TARJETA DIGITAL (DISEÑO VERTICAL COMODO PARA CELULARES)
# -------------------------------------------------------------
if opcion == "📋 Tarjeta Digital del Vehiculo":
    st.title("📋 Ficha Tecnica y Libreta Digital")
    
    query_params = st.query_params
    patente_url = query_params.get("patente", "").upper()
    patente_buscada = st.text_input("Ingresa la Patente del Vehiculo:", value=patente_url).upper().strip()
    
    if patente_buscada:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT v.*, c.nombre, c.telefono, c.localidad FROM vehiculos v LEFT JOIN clientes c ON v.cliente_id = c.id WHERE v.patente = ?", (patente_buscada,))
        vehiculo = cursor.fetchone()
        
        if vehiculo:
            st.success(f"### {vehiculo['marca']} {vehiculo['modelo']} ({vehiculo['anio']})\n**Patente:** `{vehiculo['patente']}`")
            
            # Datos principales en tarjetas verticales/responsive
            c1, c2 = st.columns(2)
            c1.metric("KM Odometro", f"{vehiculo['km_actuales']:,} km")
            c2.metric("Motor", vehiculo['motor'] or "N/D")
            
            c3, c4 = st.columns(2)
            c3.metric("Propulsion", vehiculo['tipo_propulsion'])
            c4.metric("Titular", vehiculo['nombre'])
            
            tel_clean = str(vehiculo['telefono']).replace("+", "").replace("-", "").replace(" ", "").strip()
            link_directo_auto = f"{URL_BASE_OFICIAL}/?patente={vehiculo['patente']}"
            msj_bienvenida = f"Hola {vehiculo['nombre']}! Te dejamos el enlace a la Libreta de Servicio Digital de tu {vehiculo['marca']} {vehiculo['modelo']} ({vehiculo['patente']}). Podes consultar historiales tecnicos, comprobantes PDF y cargar tus services: {link_directo_auto}"
            link_wa = "https://wa.me/" + tel_clean + "?text=" + urllib.parse.quote(msj_bienvenida)
            
            st.markdown(f'<a href="{link_wa}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 16px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%; font-size:1.1rem; margin-top:10px; margin-bottom:15px;">📲 Compartir Libreta por WhatsApp</button></a>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.subheader("🚦 Estado de Mantenimientos Preventivos")
            km_act = vehiculo['km_actuales'] or 0
            
            # Semáforo Preventivo Vertical
            col_a, col_b, col_c = st.columns(3)
            int_aceite = vehiculo['intervalo_aceite_km'] or 10000
            rest_aceite = int_aceite - (km_act % int_aceite)
            col_a.metric("🛢️ Aceite y Filtros", f"En {rest_aceite:,} km", delta=f"-{rest_aceite} km" if rest_aceite < 1500 else None)
            
            int_bujias = vehiculo['intervalo_bujias_km'] or 0
            if "100% Electrico" in str(vehiculo['tipo_propulsion']) or (vehiculo['tipo_propulsion'] == "Turbodiesel Common Rail" and int_bujias == 0):
                col_b.metric("⚡ Bujias Encendido", "No Aplica")
            elif int_bujias > 0:
                rest_buj = int_bujias - (km_act % int_bujias)
                col_b.metric("⚡ Bujias Encendido", f"En {rest_buj:,} km", delta=f"-{rest_buj} km" if rest_buj < 2500 else None)
            else:
                col_b.metric("⚡ Bujias Encendido", "No Configurado")
                
            int_dist = vehiculo['intervalo_distribucion_km'] or 0
            if int_dist == 0:
                col_c.metric("⚙️ Distribucion", "Cadena / Libre Mant.")
            else:
                rest_dist = int_dist - (km_act % int_dist)
                col_c.metric("⚙️ Distribucion", f"En {rest_dist:,} km", delta=f"-{rest_dist} km" if rest_dist < 5000 else None)
            
            st.markdown("---")
            
            # -------------------------------------------------------------
            # SECCIONES EN COLUMNA VERTICAL (DESPLEGABLES / EXPANDERS)
            # -------------------------------------------------------------
            
            # 1. TRABAJOS DEL CENTRO TÉCNICO (CON PDF)
            with st.expander("📄 1. Informes y Trabajos del Taller (Descargar PDF)", expanded=True):
                cursor.execute("SELECT * FROM servicios_taller WHERE patente = ? ORDER BY fecha DESC, id DESC", (patente_buscada,))
                servicios_t = cursor.fetchall()
                if servicios_t:
                    for st_item in servicios_t:
                        st.markdown(f"#### 📅 {st_item['fecha']} — {st_item['categoria']}")
                        st.write(f"**Kilometraje:** {st_item['km_servicio']:,} km")
                        if st_item['diagnostico_dtc']:
                            st.info(f"**DTC / Diagnostico [{st_item['estado_dtc']}]:** {st_item['diagnostico_dtc']}")
                        if st_item['parametros_tecnicos']:
                            st.success(f"**Parametros / Mediciones:** {st_item['parametros_tecnicos']}")
                        if st_item['software_version']:
                            st.warning(f"**Calibracion Software ECU:** {st_item['software_version']}")
                        st.write(f"**Trabajo:** {st_item['trabajo_realizado']}")
                        if st_item['repuestos_utilizados']:
                            st.write(f"**Repuestos / Materiales:** {st_item['repuestos_utilizados']}")
                        st.caption(f"Garantia: {st_item['garantia']} | Costo: ${st_item['costo_total']:,.2f}")
                        
                        pdf_bytes = generar_pdf_intervencion(vehiculo, st_item)
                        st.download_button(
                            label="⬇️ Descargar Informe Tecnico (PDF)",
                            data=pdf_bytes,
                            file_name=f"Informe_{patente_buscada}_{st_item['fecha']}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{st_item['id']}"
                        )
                        st.divider()
                else:
                    st.info("No hay intervenciones oficiales registradas todavia.")

            # 2. HISTORIAL DE MANTENIMIENTOS EXTERNOS
            with st.expander("📝 2. Historial de Mantenimientos Externos", expanded=False):
                cursor.execute("SELECT * FROM servicios_externos WHERE patente = ? ORDER BY fecha DESC, id DESC", (patente_buscada,))
                servicios_e = cursor.fetchall()
                if servicios_e:
                    for se in servicios_e:
                        st.markdown(f"**📅 {se['fecha']} — {se['tipo_mantenimiento']} ({se['km_servicio']:,} km)**")
                        st.write(f"📍 **Lugar:** {se['establecimiento'] or 'Particular'}")
                        st.write("**Detalle realizado:**")
                        st.text(se['detalle_materiales'])
                        st.divider()
                else:
                    st.info("El titular no ha registrado mantenimientos externos todavia.")

            # 3. CLIENTE: ANOTAR MANTENIMIENTO
            with st.expander("➕ 3. Anotar Nuevo Mantenimiento (Cliente / Lubricentro)", expanded=False):
                st.write("Completa los items reemplazados para actualizar la libreta digital:")
                with st.form("form_cliente_externo", clear_on_submit=True):
                    f_ext = st.date_input("Fecha de realizacion:", date.today())
                    km_ext = st.number_input("Kilometraje actual:", min_value=int(km_act), value=int(km_act), step=500)
                    lugar_ext = st.text_input("Lugar / Lubricentro / Taller:", placeholder="Ej: Lubricentro San Martin")
                    
                    st.markdown("---")
                    st.markdown("**Marcar lo que se cambio:**")
                    chk_aceite = st.checkbox("🛢️ Aceite de Motor")
                    txt_aceite = st.text_input("Tipo / Marca de Aceite:", placeholder="Ej: Elaion F50 5W-40", disabled=not chk_aceite)
                    chk_f_aceite = st.checkbox("🛢️ Filtro de Aceite")
                    chk_f_aire = st.checkbox("💨 Filtro de Aire de Motor")
                    chk_f_comb = st.checkbox("⛽ Filtro de Combustible (Nafta / Gasoil)")
                    chk_f_hab = st.checkbox("❄️ Filtro de Habitaculo / Aire Acondicionado")
                    chk_dist = st.checkbox("⚙️ Kit de Distribucion (Correa y Tensores)")
                    chk_bomba = st.checkbox("💧 Bomba de Agua & Liquido Refrigerante")
                    chk_frenos = st.checkbox("🛑 Pastillas / Discos de Freno")
                    chk_bat = st.checkbox("🔋 Reemplazo de Bateria 12V")
                    chk_neu = st.checkbox("🚗 Alineacion / Balanceo de Neumaticos")
                    
                    obs_extra = st.text_area("Notas adicionales (Opcional):", placeholder="Ej: Escobillas, lamparitas...")
                    btn_guardar_ext = st.form_submit_button("💾 Guardar Mantenimiento en la Libreta")
                    
                    if btn_guardar_ext:
                        items_cambiados = []
                        if chk_aceite: items_cambiados.append(f"• Aceite de Motor ({txt_aceite if txt_aceite else 'Realizado'})")
                        if chk_f_aceite: items_cambiados.append("• Filtro de Aceite")
                        if chk_f_aire: items_cambiados.append("• Filtro de Aire")
                        if chk_f_comb: items_cambiados.append("• Filtro de Combustible")
                        if chk_f_hab: items_cambiados.append("• Filtro de Habitaculo / A/C")
                        if chk_dist: items_cambiados.append("• Kit de Distribucion")
                        if chk_bomba: items_cambiados.append("• Bomba de Agua & Refrigerante")
                        if chk_frenos: items_cambiados.append("• Frenos (Pastillas / Discos)")
                        if chk_bat: items_cambiados.append("• Bateria 12V")
                        if chk_neu: items_cambiados.append("• Alineacion / Neumaticos")
                        if obs_extra: items_cambiados.append(f"• Notas: {obs_extra}")
                        
                        if not items_cambiados:
                            st.warning("Por favor marca al menos un casillero o escribi una observacion.")
                        else:
                            detalle_final = "\n".join(items_cambiados)
                            titulo_servicio = "Service de Aceite y Filtros" if chk_aceite and (chk_f_aceite or chk_f_aire) else ("Distribucion / Refrigeracion" if chk_dist or chk_bomba else "Service Lubricentro / Mecanica")
                            cursor.execute("INSERT INTO servicios_externos (patente, fecha, km_servicio, tipo_mantenimiento, establecimiento, detalle_materiales) VALUES (?, ?, ?, ?, ?, ?)", (patente_buscada, str(f_ext), int(km_ext), titulo_servicio, lugar_ext, detalle_final))
                            if km_ext > km_act:
                                cursor.execute("UPDATE vehiculos SET km_actuales = ? WHERE patente = ?", (int(km_ext), patente_buscada))
                            conn.commit()
                            st.success("✅ Mantenimiento guardado y kilometraje actualizado.")
                            st.rerun()

            # 4. CÓDIGO QR PARA STICKER
            with st.expander("🖨️ 4. Generador de Codigo QR para Sticker", expanded=False):
                host_ip = st.text_input("Direccion Web del Taller:", value=URL_BASE_OFICIAL)
                url_qr = f"{host_ip.rstrip('/')}/?patente={patente_buscada}"
                qr_bytes = generar_qr_imagen(url_qr)
                st.image(qr_bytes, caption=f"QR Patente: {patente_buscada}", width=220)
                st.download_button(label="⬇️ Descargar Imagen QR (PNG)", data=qr_bytes, file_name=f"QR_{patente_buscada}.png", mime="image/png")

        else:
            st.warning("No se encontro ningun vehiculo con esa patente.")
        conn.close()

# -------------------------------------------------------------
# 2. CARGAR TRABAJO DE TALLER
# -------------------------------------------------------------
elif opcion == "🛠️ Cargar Trabajo de Taller":
    st.title("🛠️ Registrar Intervencion del Taller")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT patente, marca, modelo, km_actuales FROM vehiculos ORDER BY patente")
    autos = cursor.fetchall()
    
    if not autos:
        st.warning("Primero debes registrar al menos un vehiculo.")
    else:
        mapa_autos = {f"{a['patente']} - {a['marca']} {a['modelo']} ({a['km_actuales']:,} km)": a for a in autos}
        sel_auto = st.selectbox("Seleccionar Vehiculo:", list(mapa_autos.keys()))
        auto_data = mapa_autos[sel_auto]
        patente_sel = auto_data['patente']
        
        with st.form("form_taller", clear_on_submit=True):
            fecha_t = st.date_input("Fecha:", date.today())
            km_t = st.number_input("Kilometraje actual:", min_value=int(auto_data['km_actuales'] or 0), value=int(auto_data['km_actuales'] or 0), step=500)
            cat_t = st.selectbox("Especialidad:", CATEGORIAS_TALLER)
            
            dtc_t = st.text_input("Codigos DTC / Diagnostico previo:", placeholder="Ej: P2463 (DPF), P0401 (EGR), C0035 (ABS), Lampara")
            estado_dtc = st.selectbox("Estado DTC:", ["Resuelto", "En Seguimiento", "Preventivo", "No aplica"])
            
            st.markdown("##### 📊 Parametros Tecnicos & Mediciones (Opcional)")
            if "Hibridos" in cat_t:
                soh = st.text_input("SOH Bateria (%):", placeholder="Ej: 88%")
                delta_v = st.text_input("Delta V Celdas (V):", placeholder="Ej: 0.02V")
                aisl = st.text_input("Resistencia Aislamiento (MΩ):", placeholder="Ej: > 500 MΩ")
                params_str = f"SOH: {soh} | Delta V: {delta_v} | Aislamiento: {aisl}" if (soh or delta_v or aisl) else ""
            elif "Aire" in cat_t:
                p_baja = st.text_input("Presion Baja (PSI):", placeholder="Ej: 32 PSI")
                p_alta = st.text_input("Presion Alta (PSI):", placeholder="Ej: 210 PSI")
                gas_g = st.text_input("Carga Gas (gramos):", placeholder="Ej: 500g R134a")
                temp_tob = st.text_input("Temp. Tobera (°C):", placeholder="Ej: 6.5°C")
                params_str = f"Baja: {p_baja} | Alta: {p_alta} | Carga: {gas_g} | Tobera: {temp_tob}" if (p_baja or p_alta or gas_g or temp_tob) else ""
            else:
                params_str = st.text_input("Mediciones / Parametros leidos:", placeholder="Ej: Caudal inyectores, caida tension 14.2V...")

            sw_ecu = ""
            if "Soluciones Electronicas" in cat_t or "Modulos" in cat_t:
                sw_ecu = st.text_input("Identificacion Software ECU / Backup:", placeholder="Ej: Hilux_2.8_DPF_OFF.bin")
            
            trabajo_t = st.text_area("Trabajo realizado / Procedimiento:*", placeholder="Describi la reparacion o procedimiento...")
            repuestos_t = st.text_area("Repuestos / Insumos instalados:", placeholder="Ej: Sensor MAF, Lámpara H7, Gas R134a...")
            
            garantia_t = st.selectbox("Garantia:", ["3 Meses", "6 Meses", "12 Meses", "Garantia de Fabrica", "Sin garantia especial"])
            prox_km = st.number_input("Proximo control (KM) - 0 si no aplica:", min_value=0, step=5000, value=0)
            costo_t = st.number_input("Costo Total ($):", min_value=0.0, step=1000.0)
            
            btn_guardar_taller = st.form_submit_button("💾 Guardar Trabajo y Actualizar Odometro")
            if btn_guardar_taller:
                if trabajo_t:
                    cursor.execute("INSERT INTO servicios_taller (patente, fecha, km_servicio, categoria, diagnostico_dtc, estado_dtc, trabajo_realizado, repuestos_utilizados, parametros_tecnicos, software_version, garantia, proximo_km, costo_total) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (patente_sel, str(fecha_t), int(km_t), cat_t, dtc_t, estado_dtc, trabajo_t, repuestos_t, params_str, sw_ecu, garantia_t, int(prox_km) if prox_km > 0 else None, float(costo_t)))
                    cursor.execute("UPDATE vehiculos SET km_actuales = ? WHERE patente = ?", (int(km_t), patente_sel))
                    conn.commit()
                    st.success(f"✅ Intervencion registrada para la patente {patente_sel}.")
                else:
                    st.error("El campo 'Trabajo realizado' es obligatorio.")
    conn.close()

# -------------------------------------------------------------
# 3. REGISTRAR Y MODIFICAR DATOS (CLIENTES, AUTOS E INTERVALOS)
# -------------------------------------------------------------
elif opcion == "➕ Registrar y Modificar Datos":
    st.title("➕ Gestion de Clientes y Vehiculos")
    
    sec_gestion = st.radio(
        "Selecciona la operacion a realizar:",
        ["👤 Alta de Cliente", "🚗 Alta de Vehiculo", "✏️ Modificar Vehiculo", "✏️ Modificar Cliente"],
        horizontal=True
    )
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Alta de Cliente
    if sec_gestion == "👤 Alta de Cliente":
        with st.form("form_alta_cli", clear_on_submit=True):
            nom = st.text_input("Nombre y Apellido / Empresa:*")
            tel = st.text_input("Telefono / WhatsApp:* (Ej: 2296123456)")
            dire = st.text_input("Direccion:")
            loc = st.text_input("Localidad:", value="Ayacucho")
            if st.form_submit_button("Guardar Cliente"):
                if nom and tel:
                    cursor.execute("INSERT INTO clientes (nombre, telefono, direccion, localidad) VALUES (?, ?, ?, ?)", (nom, tel, dire, loc))
                    conn.commit()
                    st.success(f"Cliente '{nom}' guardado correctamente.")
                else:
                    st.error("Nombre y Telefono son obligatorios.")

    # 2. Alta de Vehículo
    elif sec_gestion == "🚗 Alta de Vehiculo":
        cursor.execute("SELECT id, nombre, telefono FROM clientes ORDER BY nombre")
        clientes_db = cursor.fetchall()
        if clientes_db:
            map_c = {f"{c['nombre']} ({c['telefono']})": c['id'] for c in clientes_db}
            with st.form("form_alta_veh", clear_on_submit=True):
                cli_sel = st.selectbox("Titular:", list(map_c.keys()))
                pat = st.text_input("Patente:*").upper().strip()
                mar = st.text_input("Marca:* (Ej: Fiat, Toyota, VW)")
                mod = st.text_input("Modelo:* (Ej: Fiorino, Hilux, Gol)")
                ani = st.number_input("Año:", min_value=1980, max_value=date.today().year + 1, value=2010)
                prop = st.selectbox("Propulsion:", TIPOS_PROPULSION)
                mot = st.text_input("Motorizacion:", placeholder="Ej: 1.3 Fire, 2.8 CTDI, 1.4 TSI")
                km_ini = st.number_input("KM Inicial:", min_value=0, step=1000)
                
                st.markdown("#### ⚙️ Plan de Mantenimiento (KM)")
                int_aceite = st.number_input("Intervalo Aceite (KM):", value=10000, step=1000)
                int_dist = st.number_input("Intervalo Distribucion (KM) - 0 si es cadena:", value=60000, step=10000)
                int_buj = st.number_input("Intervalo Bujias (KM) - 0 si no aplica:", value=30000 if "Nafta" in prop else 0, step=10000)
                
                if st.form_submit_button("Guardar Vehiculo"):
                    if pat and mar and mod:
                        try:
                            cursor.execute("INSERT INTO vehiculos (patente, cliente_id, marca, modelo, anio, tipo_propulsion, motor, km_actuales, intervalo_aceite_km, intervalo_distribucion_km, intervalo_bujias_km) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (pat, map_c[cli_sel], mar, mod, int(ani), prop, mot, int(km_ini), int(int_aceite), int(int_dist), int(int_buj)))
                            conn.commit()
                            st.success(f"Vehiculo {mar} {mod} ({pat}) guardado correctamente.")
                        except sqlite3.IntegrityError:
                            st.error("Esa patente ya existe en la base de datos.")
                    else:
                        st.error("Patente, Marca y Modelo son obligatorios.")
        else:
            st.info("Primero registra al menos un cliente.")

    # 3. Modificar Vehículo Existente
    elif sec_gestion == "✏️ Modificar Vehiculo":
        cursor.execute("SELECT patente, marca, modelo FROM vehiculos ORDER BY patente")
        vehiculos_edit = cursor.fetchall()
        if vehiculos_edit:
            map_ve = {f"{v['patente']} - {v['marca']} {v['modelo']}": v['patente'] for v in vehiculos_edit}
            sel_pat_edit = st.selectbox("Seleccionar Vehiculo a Modificar:", list(map_ve.keys()))
            pat_a_modificar = map_ve[sel_pat_edit]
            cursor.execute("SELECT * FROM vehiculos WHERE patente = ?", (pat_a_modificar,))
            v_curr = cursor.fetchone()
            if v_curr:
                with st.form("form_editar_veh"):
                    st.write(f"### Editando Patente: `{pat_a_modificar}`")
                    e_mar = st.text_input("Marca:", value=v_curr['marca'])
                    e_mod = st.text_input("Modelo:", value=v_curr['modelo'])
                    e_ani = st.number_input("Año:", min_value=1980, max_value=date.today().year + 1, value=int(v_curr['anio'] or 2010))
                    
                    idx_prop = 0
                    if v_curr['tipo_propulsion'] in TIPOS_PROPULSION:
                        idx_prop = TIPOS_PROPULSION.index(v_curr['tipo_propulsion'])
                    e_prop = st.selectbox("Propulsion:", TIPOS_PROPULSION, index=idx_prop)
                    e_mot = st.text_input("Motor:", value=v_curr['motor'] or "")
                    e_km = st.number_input("Kilometraje Actual:", min_value=0, value=int(v_curr['km_actuales'] or 0), step=1000)
                    
                    st.markdown("#### ⚙️ Ajustar Intervalos (KM)")
                    e_int_aceite = st.number_input("Intervalo Aceite (KM):", value=int(v_curr['intervalo_aceite_km'] or 10000), step=1000)
                    e_int_dist = st.number_input("Intervalo Distribucion (KM) - 0 si es cadena:", value=int(v_curr['intervalo_distribucion_km'] or 60000), step=10000)
                    e_int_buj = st.number_input("Intervalo Bujias (KM) - 0 si no aplica:", value=int(v_curr['intervalo_bujias_km'] or 30000), step=5000)
                    
                    if st.form_submit_button("💾 Guardar Cambios del Vehiculo"):
                        cursor.execute("UPDATE vehiculos SET marca = ?, modelo = ?, anio = ?, tipo_propulsion = ?, motor = ?, km_actuales = ?, intervalo_aceite_km = ?, intervalo_distribucion_km = ?, intervalo_bujias_km = ? WHERE patente = ?", (e_mar, e_mod, int(e_ani), e_prop, e_mot, int(e_km), int(e_int_aceite), int(e_int_dist), int(e_int_buj), pat_a_modificar))
                        conn.commit()
                        st.success("✅ Datos del vehiculo actualizados correctamente.")
                        st.rerun()
        else:
            st.info("No hay vehiculos registrados para modificar.")

    # 4. Modificar Cliente Existente
    elif sec_gestion == "✏️ Modificar Cliente":
        cursor.execute("SELECT id, nombre, telefono, direccion, localidad FROM clientes ORDER BY nombre")
        clientes_edit = cursor.fetchall()
        if clientes_edit:
            map_cli_edit = {f"{c['nombre']} ({c['telefono']})": c for c in clientes_edit}
            sel_cli_name = st.selectbox("Seleccionar Cliente a Modificar:", list(map_cli_edit.keys()))
            cli_data = map_cli_edit[sel_cli_name]
            with st.form("form_editar_cliente"):
                st.write(f"### Editando datos de: `{cli_data['nombre']}`")
                nuevo_nom = st.text_input("Nombre y Apellido / Empresa:", value=cli_data['nombre'])
                nuevo_tel = st.text_input("Telefono / WhatsApp:", value=cli_data['telefono'])
                nuevo_dir = st.text_input("Direccion:", value=cli_data['direccion'] or "")
                nueva_loc = st.text_input("Localidad:", value=cli_data['localidad'] or "Ayacucho")
                if st.form_submit_button("💾 Guardar Cambios del Cliente"):
                    if nuevo_nom and nuevo_tel:
                        cursor.execute("UPDATE clientes SET nombre = ?, telefono = ?, direccion = ?, localidad = ? WHERE id = ?", (nuevo_nom, nuevo_tel, nuevo_dir, nueva_loc, cli_data['id']))
                        conn.commit()
                        st.success("✅ Datos del cliente actualizados correctamente.")
                        st.rerun()
                    else:
                        st.error("El nombre y el telefono no pueden quedar vacios.")
        else:
            st.info("No hay clientes registrados para modificar.")
    conn.close()

# -------------------------------------------------------------
# 4. ALERTAS PREVENTIVAS
# -------------------------------------------------------------
elif opcion == "🔔 Alertas Preventivas (30 Dias)":
    st.title("🔔 Panel de Alertas Preventivas")
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
                    alertas_generadas.append({"Patente": v['patente'], "Vehiculo": f"{v['marca']} {v['modelo']}", "Cliente": nombre_cli, "Telefono": tel, "Alerta": "⚡ Recambio de Bujias", "Detalle": f"Faltan aprox. {rest_buj:,} km", "Mensaje": f"Hola {nombre_cli}! Te recordamos desde el Centro Tecnico que tu {v['marca']} {v['modelo']} ({v['patente']}) esta proximo al recambio de bujias ({km:,} km). Queres que reservemos un turno?"})
            if v['intervalo_aceite_km'] and v['intervalo_aceite_km'] > 0:
                rest_aceite = v['intervalo_aceite_km'] - (km % v['intervalo_aceite_km'])
                if rest_aceite <= 1500:
                    alertas_generadas.append({"Patente": v['patente'], "Vehiculo": f"{v['marca']} {v['modelo']}", "Cliente": nombre_cli, "Telefono": tel, "Alerta": "🛢️ Service Aceite y Filtros", "Detalle": f"Faltan aprox. {rest_aceite:,} km", "Mensaje": f"Hola {nombre_cli}! Tu {v['marca']} {v['modelo']} ({v['patente']}) esta proximo al service de aceite y filtros ({km:,} km)."})
            if v['intervalo_distribucion_km'] and v['intervalo_distribucion_km'] > 0:
                rest_dist = v['intervalo_distribucion_km'] - (km % v['intervalo_distribucion_km'])
                if rest_dist <= 5000:
                    alertas_generadas.append({"Patente": v['patente'], "Vehiculo": f"{v['marca']} {v['modelo']}", "Cliente": nombre_cli, "Telefono": tel, "Alerta": "⚙️ Correa de Distribucion", "Detalle": f"Faltan aprox. {rest_dist:,} km", "Mensaje": f"Hola {nombre_cli}! Tu {v['marca']} {v['modelo']} ({v['patente']}) esta proximo al reemplazo de correa de distribucion ({km:,} km)."})
        if alertas_generadas:
            st.write(f"Se encontraron **{len(alertas_generadas)} alertas**:")
            for al in alertas_generadas:
                st.markdown(f"**{al['Vehiculo']}** (`{al['Patente']}`) — *{al['Cliente']}*")
                st.write(f"**{al['Alerta']}** — {al['Detalle']}")
                link_wa = "https://wa.me/" + al['Telefono'] + "?text=" + urllib.parse.quote(al['Mensaje'])
                st.markdown(f'<a href="{link_wa}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 16px; border-radius:6px; cursor:pointer; font-weight:bold; width:100%; margin-bottom:15px;">📲 Enviar WhatsApp</button></a>', unsafe_allow_html=True)
                st.divider()
        else:
            st.success("🎉 No hay vehiculos con alertas pendientes.")
    conn.close()

# -------------------------------------------------------------
# 5. PRESUPUESTOS WHATSAPP
# -------------------------------------------------------------
elif opcion == "💼 Presupuestos WhatsApp":
    st.title("💼 Presupuestador Tecnico")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT v.patente, v.marca, v.modelo, c.nombre, c.telefono FROM vehiculos v LEFT JOIN clientes c ON v.cliente_id = c.id ORDER BY v.patente")
    vehiculos_p = cursor.fetchall()
    if vehiculos_p:
        mapa_vp = {f"{v['patente']} - {v['marca']} {v['modelo']} ({v['nombre']})": v for v in vehiculos_p}
        sel_vp = st.selectbox("Vehiculo:", list(mapa_vp.keys()))
        dv = mapa_vp[sel_vp]
        with st.form("form_presupuesto"):
            cat_p = st.selectbox("Especialidad:", CATEGORIAS_TALLER)
            det_p = st.text_area("Detalle de mano de obra:")
            rep_p = st.text_area("Detalle de repuestos:")
            val_p = st.number_input("Validez (dias):", value=15, min_value=1)
            tot_p = st.number_input("Total ($):", min_value=0.0, step=1000.0)
            if st.form_submit_button("Generar y Guardar Presupuesto"):
                if tot_p > 0:
                    cursor.execute("INSERT INTO presupuestos (patente, fecha_emision, categoria, validez_dias, detalle_trabajo, repuestos, total) VALUES (?, ?, ?, ?, ?, ?, ?)", (dv['patente'], str(date.today()), cat_p, int(val_p), det_p, rep_p, float(tot_p)))
                    conn.commit()
                    texto_ws = "*PRESUPUESTO TECNICO*\n" + "🚗 *Vehiculo:* " + str(dv['marca']) + " " + str(dv['modelo']) + " (" + str(dv['patente']) + ")\n" + "🔧 *Trabajo:* " + str(cat_p) + "\n\n" + "*Procedimiento:*\n" + str(det_p) + "\n\n" + "*Repuestos / Insumos:*\n" + str(rep_p) + "\n\n" + f"💵 *TOTAL:* ${tot_p:,.2f}\n" + f"⏳ *Validez:* {val_p} dias."
                    link_presu = "https://wa.me/" + str(dv['telefono']).replace('+', '').replace('-', '').replace(' ', '').strip() + "?text=" + urllib.parse.quote(texto_ws)
                    st.success("✅ Presupuesto guardado.")
                    st.markdown(f'<a href="{link_presu}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 20px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%;">📲 Enviar por WhatsApp</button></a>', unsafe_allow_html=True)
    conn.close()

# -------------------------------------------------------------
# 6. HISTORIAL GENERAL
# -------------------------------------------------------------
elif opcion == "📊 Historial General":
    st.title("📊 Registro Historico de Trabajos")
    conn = get_db()
    df_taller = pd.read_sql_query("SELECT s.fecha AS Fecha, s.patente AS Patente, v.marca AS Marca, v.modelo AS Modelo, s.categoria AS Especialidad, s.km_servicio AS KM, s.trabajo_realizado AS Trabajo, s.garantia AS Garantia, s.costo_total AS Total FROM servicios_taller s LEFT JOIN vehiculos v ON s.patente = v.patente ORDER BY s.fecha DESC", conn)
    conn.close()
    if not df_taller.empty:
        st.dataframe(df_taller, use_container_width=True)
    else:
        st.info("No hay registros en el historial todavia.")
'''

with open("app.py", "w", encoding="utf-8") as f:
    f.write(mobile_app_code)

import py_compile
py_compile.compile("app.py", doraise=True)
print("Mobile-optimized app.py compiled with 0 errors!")
