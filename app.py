# Let's create an updated version of the app with an OEM Light / Clean Theme.
# We replace the ultra-dark palette (--bg: #050B16, #0A1526, etc.) with a clean automotive dealer style:
# Background: #F8FAFC (clean light slate/off-white)
# Panels / Cards: #FFFFFF with subtle borders #E2E8F0 and shadows
# Headings / Primary Text: #0F2B48 (deep navy Manuel Aguiar brand color)
# Body / Secondary Text: #334155 (slate 700, maximum legibility)
# Accent / Highlights: #F59E0B (brand amber/orange) and #0284C7 (cyan/blue)
# Inputs: clean white background with clear slate borders and dark crisp text

updated_css = """
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

p, span, label, div {
  color: inherit;
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

/* Botones principales con excelente contraste */
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

/* Métricas limpias tipo concesionario */
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
"""

# Let's read the full code and replace the style block with updated_css
with open("app.py", "r", encoding="utf-8") as f:
    full_code = f.read()

# Let's construct the complete, refined app.py with updated light theme CSS
import re
new_full_code = re.sub(r'<style>.*?</style>', updated_css.strip(), full_code, flags=re.DOTALL)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(new_full_code)

import py_compile
py_compile.compile("app.py", doraise=True)
print("APP.PY LIGHT OEM THEME COMPILED 100% OK!")
