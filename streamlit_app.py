import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime
from plotly.subplots import make_subplots
import plotly.express as px

# ── Config ──
st.set_page_config(page_title="ValuationPro", page_icon="📊", layout="wide")

# ── Custom CSS ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@300;400;700&family=Outfit:wght@300;400;600&display=swap');
    .stApp { font-family: 'Inter', sans-serif; }
    .block-container { max-width: 1200px; padding-top: 2rem; }
    div[data-testid="stMetric"] { background: rgba(128,128,128,0.05); border: 1px solid rgba(128,128,128,0.1); border-radius: 12px; padding: 16px; transition: all 0.3s ease; }
    div[data-testid="stMetric"]:hover { background: rgba(212,175,55,0.05); border-color: #d4af37; box-shadow: 0 0 15px rgba(212,175,55,0.3); transform: translateY(-2px); }
    div[data-testid="stMetric"] label { font-family: 'Outfit', sans-serif; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; opacity: 0.6; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 300; letter-spacing: -1px; }
    .pine-code { background: rgba(0,0,0,0.2); border: 1px solid rgba(128,128,128,0.2); border-radius: 10px; padding: 16px; font-family: 'JetBrains Mono', monospace; font-size: 11px; overflow-x: auto; white-space: pre; max-height: 400px; overflow-y: auto; }
    .stSlider > div > div > div > div { background-color: var(--primary-color); }
    .big-price { font-family: 'JetBrains Mono', monospace; font-size: 5rem; font-weight: 300; line-height: 1; letter-spacing: -3px; margin: 0; padding: 0; }
    .big-price-sub { font-size: 1.5rem; font-weight: 600; padding-left: 10px; }
    .header-ticker { font-size: 1.5rem; font-weight: 600; opacity: 0.5; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; font-weight: 600; }
    
    /* Clean Sidebar Buttons (Pills) */
    div[data-testid="stSidebar"] button {
        border-radius: 20px;
        border: 1px solid rgba(128,128,128,0.2);
        background-color: transparent;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    div[data-testid="stSidebar"] button:hover {
        border-color: var(--primary-color) !important;
        color: var(--primary-color) !important;
        background-color: rgba(128,128,128,0.05);
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.4) !important;
    }
    
    /* Universal Elements Golden Glow */
    button[kind="secondary"], button[kind="primary"] { transition: all 0.3s ease !important; }
    button[kind="secondary"]:hover, button[kind="primary"]:hover {
        border-color: #d4af37 !important;
        color: #d4af37 !important;
        box-shadow: 0 0 15px rgba(212,175,55,0.3) !important;
    }
    
    div[data-testid="stExpander"] { transition: all 0.3s ease; border-radius: 8px; border: 1px solid transparent; }
    div[data-testid="stExpander"]:hover {
        border-color: #d4af37 !important;
        box-shadow: 0 0 15px rgba(212,175,55,0.2) !important;
    }
    
    .glow-hover { transition: all 0.3s ease; border: 1px solid transparent; }
    .glow-hover:hover {
        border-color: #d4af37 !important;
        box-shadow: 0 0 15px rgba(212,175,55,0.3) !important;
        transform: translateY(-2px);
    }
    
    /* Golden Progress Bar */
    [data-testid="stProgressBar"] > div > div { background-color: #d4af37 !important; box-shadow: 0 0 10px rgba(212,175,55,0.8); }

    /* Á.L.V.A.R.O. Premium Candles Loader */
    [data-testid="stStatusWidget"] * { display: none !important; }
    [data-testid="stStatusWidget"] {
        background-color: transparent !important;
        background-image: 
            linear-gradient(to right, transparent 3px, #d4af37 3px, #d4af37 5px, transparent 5px),
            linear-gradient(to bottom, transparent 25%, #d4af37 25%, #d4af37 75%, transparent 75%) !important;
        width: 8px !important; height: 24px !important;
        filter: drop-shadow(0 0 5px rgba(212, 175, 55, 0.8)) !important;
        border: none !important;
        position: fixed !important; top: 25px !important; right: 250px !important;
        animation: candle-pulse 0.8s ease-in-out infinite alternate !important;
        padding: 0 !important; min-width: 0 !important; display: block !important;
        box-shadow: none !important;
    }
    [data-testid="stStatusWidget"]::before, [data-testid="stStatusWidget"]::after {
        content: ""; position: absolute; width: 8px; height: 24px;
        background-color: transparent;
        background-image: 
            linear-gradient(to right, transparent 3px, #d4af37 3px, #d4af37 5px, transparent 5px),
            linear-gradient(to bottom, transparent 25%, #d4af37 25%, #d4af37 75%, transparent 75%);
        top: 0;
    }
    [data-testid="stStatusWidget"]::before { left: -14px; animation: candle-pulse 0.8s ease-in-out infinite alternate 0.2s; }
    [data-testid="stStatusWidget"]::after { left: 14px; animation: candle-pulse 0.8s ease-in-out infinite alternate 0.4s; }
    
    @keyframes candle-pulse {
        0% { transform: scaleY(0.6) translateY(4px); opacity: 0.6; filter: drop-shadow(0 0 2px rgba(212, 175, 55, 0.4)); }
        100% { transform: scaleY(1.4) translateY(-4px); opacity: 1; filter: drop-shadow(0 0 8px rgba(212, 175, 55, 1)); }
    }
</style>
""", unsafe_allow_html=True)

# ── Ticker Lists ──
MARKETS_BY_COUNTRY = {
    "🇺🇸 Estados Unidos": {
        "iso_alpha": "USA", "lat": 39.0, "lon": -98.0, "index": "^GSPC",
        "sectors": {
            "Tecnología": {"AAPL": "Apple", "MSFT": "Microsoft", "GOOGL": "Alphabet", "AMZN": "Amazon", "META": "Meta", "NVDA": "Nvidia", "AVGO": "Broadcom", "CSCO": "Cisco", "ADBE": "Adobe", "CRM": "Salesforce", "AMD": "AMD", "INTC": "Intel"},
            "Finanzas": {"JPM": "JPMorgan Chase", "V": "Visa", "MA": "Mastercard", "BAC": "Bank of America", "WFC": "Wells Fargo", "GS": "Goldman Sachs", "MS": "Morgan Stanley", "AXP": "American Express"},
            "Salud": {"UNH": "UnitedHealth", "JNJ": "Johnson & Johnson", "LLY": "Eli Lilly", "PFE": "Pfizer", "ABBV": "AbbVie", "MRK": "Merck", "TMO": "Thermo Fisher", "ABT": "Abbott"},
            "Consumo": {"WMT": "Walmart", "PG": "Procter & Gamble", "KO": "Coca-Cola", "PEP": "PepsiCo", "COST": "Costco", "MCD": "McDonald's", "NKE": "Nike", "SBUX": "Starbucks", "HD": "Home Depot"},
            "Energía e Industria": {"XOM": "Exxon Mobil", "CVX": "Chevron", "GE": "General Electric", "CAT": "Caterpillar", "BA": "Boeing", "RTX": "Raytheon", "LMT": "Lockheed Martin"}
        }
    },
    "🇪🇸 España (IBEX 35)": {
        "iso_alpha": "ESP", "lat": 40.0, "lon": -4.0, "index": "^IBEX",
        "sectors": {
            "Banca y Finanzas": {"SAN.MC": "Banco Santander", "BBVA.MC": "BBVA", "CABK.MC": "CaixaBank", "SAB.MC": "Banco Sabadell", "BKT.MC": "Bankinter", "MAP.MC": "Mapfre", "UNI.MC": "Unicaja"},
            "Energía y Utilities": {"IBE.MC": "Iberdrola", "REP.MC": "Repsol", "NTGY.MC": "Naturgy", "ELE.MC": "Endesa", "ENG.MC": "Enagás", "RED.MC": "Redeia"},
            "Consumo y Servicios": {"ITX.MC": "Inditex", "IAG.MC": "IAG", "MEL.MC": "Meliá Hotels", "AENA.MC": "Aena", "AMS.MC": "Amadeus", "LOG.MC": "Logista"},
            "Industria y Construcción": {"FER.MC": "Ferrovial", "ACS.MC": "ACS", "MTS.MC": "ArcelorMittal", "ACX.MC": "Acerinox", "FDR.MC": "Fluidra", "SACY.MC": "Sacyr"},
            "Telecos y Salud": {"TEF.MC": "Telefónica", "CLNX.MC": "Cellnex", "GRF.MC": "Grifols", "ROVI.MC": "Laboratorios Rovi"}
        }
    },
    "🇩🇪 Alemania (DAX)": {
        "iso_alpha": "DEU", "lat": 51.0, "lon": 10.0, "index": "^GDAXI",
        "sectors": {
            "Automoción e Industria": {"VOW3.DE": "Volkswagen", "BMW.DE": "BMW", "MBG.DE": "Mercedes-Benz", "SIE.DE": "Siemens", "AIR.DE": "Airbus", "BAS.DE": "BASF", "BAYN.DE": "Bayer"},
            "Finanzas y Seguros": {"ALV.DE": "Allianz", "MUV2.DE": "Munich Re", "CBK.DE": "Commerzbank", "DBK.DE": "Deutsche Bank"},
            "Tecnología y Otros": {"SAP.DE": "SAP", "IFX.DE": "Infineon", "DTE.DE": "Deutsche Telekom", "DHL.DE": "DHL Group", "ADS.DE": "Adidas"}
        }
    },
    "🇫🇷 Francia (CAC 40)": {
        "iso_alpha": "FRA", "lat": 46.0, "lon": 2.0, "index": "^FCHI",
        "sectors": {
            "Lujo y Consumo": {"MC.PA": "LVMH", "OR.PA": "L'Oréal", "RMS.PA": "Hermès", "KER.PA": "Kering", "BN.PA": "Danone"},
            "Industria y Energía": {"TTE.PA": "TotalEnergies", "SU.PA": "Schneider Electric", "AIR.PA": "Airbus", "CS.PA": "AXA", "SAN.PA": "Sanofi", "BNP.PA": "BNP Paribas"}
        }
    },
    "🇬🇧 Reino Unido (FTSE 100)": {
        "iso_alpha": "GBR", "lat": 53.0, "lon": -2.0, "index": "^FTSE",
        "sectors": {
            "Finanzas y Energía": {"HSBA.L": "HSBC", "BP.L": "BP", "SHEL.L": "Shell", "BARC.L": "Barclays", "LSEG.L": "LSE Group"},
            "Salud y Consumo": {"AZN.L": "AstraZeneca", "GSK.L": "GSK", "ULVR.L": "Unilever", "DGE.L": "Diageo", "BATS.L": "British American Tobacco"}
        }
    },
    "🇯🇵 Japón (Nikkei)": {
        "iso_alpha": "JPN", "lat": 36.0, "lon": 138.0, "index": "^N225",
        "sectors": {
            "Tecnología y Motor": {"7203.T": "Toyota", "6758.T": "Sony", "9984.T": "SoftBank", "8035.T": "Tokyo Electron", "7974.T": "Nintendo", "6981.T": "Murata"},
            "Finanzas e Industria": {"8306.T": "Mitsubishi UFJ", "8058.T": "Mitsubishi Corp", "9432.T": "NTT", "6861.T": "Keyence"}
        }
    },
    "🇨🇳 China y HK": {
        "iso_alpha": "CHN", "lat": 35.0, "lon": 104.0, "index": "^HSI",
        "sectors": {
            "Tecnología": {"0700.HK": "Tencent", "9988.HK": "Alibaba", "3690.HK": "Meituan", "1810.HK": "Xiaomi", "0981.HK": "SMIC"},
            "Finanzas y Consumo": {"0939.HK": "China Construction Bank", "1398.HK": "ICBC", "1299.HK": "AIA Group", "0027.HK": "Galaxy Ent"}
        }
    },
    "🇨🇦 Canadá": {
        "iso_alpha": "CAN", "lat": 56.0, "lon": -106.0, "index": "^GSPTSE",
        "sectors": {
            "Finanzas y Energía": {"RY.TO": "Royal Bank of Canada", "TD.TO": "TD Bank", "ENB.TO": "Enbridge", "CNQ.TO": "Canadian Natural Res"},
            "Tecnología y Otros": {"SHOP.TO": "Shopify", "CNR.TO": "Canadian National Railway", "BAM.TO": "Brookfield"}
        }
    },
    "🇧🇷 Brasil": {
        "iso_alpha": "BRA", "lat": -14.0, "lon": -51.0, "index": "^BVSP",
        "sectors": {
            "Mercado General": {"PETR4.SA": "Petrobras", "VALE3.SA": "Vale", "ITUB4.SA": "Itaú Unibanco", "BBDC4.SA": "Bradesco", "ABEV3.SA": "Ambev", "WEGE3.SA": "WEG"}
        }
    },
    "🇦🇺 Australia": {
        "iso_alpha": "AUS", "lat": -25.0, "lon": 133.0, "index": "^AXJO",
        "sectors": {
            "Mercado General": {"BHP.AX": "BHP Group", "RIO.AX": "Rio Tinto", "CBA.AX": "Commonwealth Bank", "CSL.AX": "CSL", "WBC.AX": "Westpac", "NAB.AX": "NAB"}
        }
    }
}

def fmt_big(n):
    if n is None or pd.isna(n): return "N/A"
    sign = "-" if n < 0 else ""
    a = abs(n)
    if a >= 1e12: return f"{sign}{a/1e12:.1f}T"
    if a >= 1e9: return f"{sign}{a/1e9:.1f}B"
    if a >= 1e6: return f"{sign}{a/1e6:.1f}M"
    return f"{sign}{a:,.0f}"

@st.cache_data(ttl=3600)
def get_risk_free_rate():
    try:
        tnx = yf.Ticker("^TNX")
        rate = tnx.fast_info.last_price
        if rate:
            return rate / 100.0
    except:
        pass
    return 0.043

@st.cache_data(ttl=600)
def get_market_status_v2():
    status = {}
    for country, data in MARKETS_BY_COUNTRY.items():
        if "index" in data:
            try:
                tk = yf.Ticker(data["index"])
                h = tk.history(period="5d")
                if len(h) >= 2:
                    price = float(h['Close'].iloc[-1])
                    prev = float(h['Close'].iloc[-2])
                    pct = (price - prev) / prev
                    status[country] = pct
                else:
                    status[country] = 0.0
            except:
                status[country] = 0.0
    return status

# ── Sidebar ──
c_logo1, c_logo2 = st.sidebar.columns([1, 4])
try:
    c_logo1.image("logo_a.png", use_container_width=True)
except:
    c_logo1.markdown("<h1 style='text-align: right; margin-top: -10px; color: #d4af37;'>V</h1>", unsafe_allow_html=True)
c_logo2.markdown("<h2 style='font-weight: 800; letter-spacing: -1px; margin-top: 5px;'>Valuation<span style='font-weight: 300; color: #d4af37;'>Pro</span></h2>", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style='margin-bottom: 20px; margin-top: -15px;'>
    <div style='font-size: 0.75rem; line-height: 1.3;'>
        <span style='opacity: 0.6;'>Motor de IA: </span><span style='font-weight: 800; letter-spacing: 1px; color: #d4af37; text-shadow: 0 0 5px rgba(212,175,55,0.4);'>Á.L.V.A.R.O.</span><br>
        <span style='font-size: 0.55rem; opacity: 0.4; text-transform: uppercase; letter-spacing: 0.5px;'>Advanced Liquidity & Valuation<br>Algorithm for Research Optimization</span>
    </div>
</div>
""", unsafe_allow_html=True)
st.sidebar.divider()

def set_ticker(t):
    st.session_state["ticker_input"] = t

st.sidebar.markdown("### 🔍 Buscar Acción")
ticker_input = st.sidebar.text_input(" ", placeholder="Escribe un ticker (Ej: AAPL)", key="ticker_input", label_visibility="collapsed")
st.sidebar.button("🌍 Explorador de Mercados", use_container_width=True, on_click=set_ticker, args=("",))

st.sidebar.divider()
st.sidebar.markdown("### ⚙️ Gráfico")
chart_period = st.sidebar.selectbox("Periodo", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"], index=8)
chart_interval = st.sidebar.selectbox("Velas", ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"], index=8)
chart_type = st.sidebar.radio("Tipo", ["Línea Minimalista", "Velas Japonesas"], index=0)

st.sidebar.divider()
st.sidebar.markdown("### 🎨 Estilo")
color_up = st.sidebar.color_picker("Color Alcista", "#00C853")
color_down = st.sidebar.color_picker("Color Bajista", "#FF3D00")

ticker = st.session_state.get("ticker_input", "").strip().upper()

# ── Main ──
if "selected_market" not in st.session_state:
    st.session_state.selected_market = None

if not ticker:
    st.markdown("""
        <div style="text-align: center; margin-top: 4vh; margin-bottom: 20px;">
            <h1 style='font-size: 3.5rem; font-weight: 300; letter-spacing: -2px; margin-bottom: 0;'>Explorador Global</h1>
            <p style='font-size: 1rem; opacity: 0.5; font-weight: 400; margin-top: 5px; letter-spacing: 0.5px;'>Selecciona un mercado brillante en el mapa para descubrir acciones</p>
        </div>
    """, unsafe_allow_html=True)
    
    market_status = get_market_status_v2()
    
    lats = []
    lons = []
    texts = []
    colors = []
    
    for country, data in MARKETS_BY_COUNTRY.items():
        lats.append(data["lat"])
        lons.append(data["lon"])
        pct = market_status.get(country, 0)
        sign = "+" if pct >= 0 else ""
        texts.append(f"{country}<br>{sign}{pct*100:.2f}%")
        colors.append(color_up if pct >= 0 else color_down)
        
    fig_globe = go.Figure()
    
    # Base dark choropleth (no highlighting by default)
    fig_globe.add_trace(go.Choropleth(
        locations=[d["iso_alpha"] for d in MARKETS_BY_COUNTRY.values()],
        z=[1]*len(MARKETS_BY_COUNTRY),
        colorscale=[[0, "rgba(128,128,128,0.1)"], [1, "rgba(128,128,128,0.1)"]],
        showscale=False,
        marker_line_width=0,
        hoverinfo='skip'
    ))
    
    # Glowing Halo (Large transparent dots)
    fig_globe.add_trace(go.Scattergeo(
        lat=lats, lon=lons, text=texts,
        mode="markers",
        marker=dict(size=25, color=colors, opacity=0.15),
        hoverinfo="skip",
        name="Halo"
    ))
    
    # Core nodes
    fig_globe.add_trace(go.Scattergeo(
        lat=lats, lon=lons, text=texts,
        mode="markers",
        marker=dict(size=8, color=colors, line=dict(width=1.5, color="rgba(255,255,255,0.9)")),
        hoverinfo="text",
        name="Markets"
    ))
    
    selected_country = st.session_state.selected_market
    if selected_country and selected_country in MARKETS_BY_COUNTRY:
        iso = MARKETS_BY_COUNTRY[selected_country]["iso_alpha"]
        pct = market_status.get(selected_country, 0)
        sel_color = color_up if pct >= 0 else color_down
        
        fig_globe.add_trace(go.Choropleth(
            locations=[iso], z=[1],
            colorscale=[[0, sel_color], [1, sel_color]],
            showscale=False, marker_line_width=0, marker_opacity=0.25, hoverinfo='skip'
        ))
        center_lat = MARKETS_BY_COUNTRY[selected_country]["lat"]
        center_lon = MARKETS_BY_COUNTRY[selected_country]["lon"]
    else:
        center_lat = 30
        center_lon = 0

    fig_globe.update_geos(
        projection_type="orthographic",
        showcoastlines=True, coastlinecolor="rgba(255, 220, 100, 0.9)", coastlinewidth=2,
        showland=True, landcolor="rgba(0,0,0,0)",
        showocean=True, oceancolor="rgba(0,0,0,0)",
        showcountries=False,
        lonaxis=dict(showgrid=True, gridcolor="rgba(255, 220, 100, 0.25)", gridwidth=1.5, dtick=15),
        lataxis=dict(showgrid=True, gridcolor="rgba(255, 220, 100, 0.25)", gridwidth=1.5, dtick=15),
        bgcolor="rgba(0,0,0,0)",
        center=dict(lat=center_lat, lon=center_lon),
        projection_rotation=dict(lon=center_lon, lat=center_lat, roll=0)
    )
    fig_globe.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=800, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
    
    # Capture clicks
    event = st.plotly_chart(fig_globe, use_container_width=True, config={'displayModeBar': False}, on_select="rerun", selection_mode="points")
    
    if getattr(event, "selection", None) and getattr(event.selection, "points", None):
        pt = event.selection.points[0]
        
        # pt can be a dict or an object depending on Streamlit version
        cnum = pt.get("curve_number") if isinstance(pt, dict) else getattr(pt, "curve_number", None)
        idx = pt.get("point_index") if isinstance(pt, dict) else getattr(pt, "point_index", None)
        
        # For the Halo trace, cnum is 1, for the core nodes, cnum is 2.
        if idx is not None and cnum in [1, 2]:
            countries = list(MARKETS_BY_COUNTRY.keys())
            if 0 <= idx < len(countries):
                if st.session_state.selected_market != countries[idx]:
                    st.session_state.selected_market = countries[idx]
                    st.rerun()
                
    if st.session_state.selected_market:
        sel = st.session_state.selected_market
        st.markdown("---")
        st.markdown(f"<h3 style='text-align: center;'>Empresas en {sel.split(' ', 1)[1] if len(sel.split(' ')) > 1 else sel}</h3>", unsafe_allow_html=True)
        
        region_sectors = MARKETS_BY_COUNTRY[sel]["sectors"]
        
        st.markdown("<p style='font-size: 0.9rem; margin-bottom: 5px; opacity: 0.8;'>Ajustar agresividad del escáner:</p>", unsafe_allow_html=True)
        rsi_limit = st.slider("Filtro RSI (Menos = Oportunidades más extremas y raras)", min_value=15, max_value=45, value=30, step=1)
        
        if st.button("🔍 Escanear Oportunidades Automáticamente", use_container_width=True):
            all_ticks = []
            for group, ticks in region_sectors.items():
                all_ticks.extend(list(ticks.keys()))
                
            prog = st.progress(0)
            stat = st.empty()
            ops = []
            
            @st.cache_data(ttl=1800, show_spinner=False)
            def fetch_scanner_hist(tk_str):
                try:
                    return yf.Ticker(tk_str).history(period="1mo")
                except:
                    return pd.DataFrame()
            
            for i, t in enumerate(all_ticks):
                stat.markdown(f"<p style='text-align:center; font-size:13px; font-weight:600; opacity:0.8; color: #d4af37;'>Analizando {i+1}/{len(all_ticks)}: Buscando anomalías en {t}...</p>", unsafe_allow_html=True)
                
                h = fetch_scanner_hist(t)
                if len(h) >= 2:
                    last = h.iloc[-1]
                    prev = h.iloc[-2]
                    
                    # RSI
                    delta = h['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
                    rs = gain / loss if loss != 0 else 100
                    rsi = 100 - (100 / (1 + rs))
                    
                    # Bullish Engulfing
                    bull = (prev['Close'] < prev['Open']) and (last['Close'] > last['Open']) and (last['Close'] > prev['Open']) and (last['Open'] <= prev['Close'])
                    
                    if pd.notna(rsi) and rsi < rsi_limit:
                        ops.append({"ticker": t, "text": f"🟢 {t}: RSI Sobrevendido ({rsi:.1f})"})
                    if bull:
                        ops.append({"ticker": t, "text": f"🔥 {t}: Envolvente Alcista detectada"})
                
                prog.progress((i + 1) / len(all_ticks))
                
            prog.empty()
            stat.empty()
            
            if ops:
                st.success("Oportunidades Técnicas Encontradas (Haz clic para analizar):")
                for i, o in enumerate(ops):
                    st.button(o["text"], key=f"scan_btn_{o['ticker']}_{i}", on_click=set_ticker, args=(o['ticker'],), use_container_width=True)
            else:
                st.info("Sin señales extremas hoy en este mercado.")
            st.divider()
        
        for group, ticks in region_sectors.items():
            with st.expander(group, expanded=False):
                cols = st.columns(4)
                for i, (t, name) in enumerate(ticks.items()):
                    cols[i % 4].button(t, key=f"btn_main_{sel}_{t}", help=name, use_container_width=True, on_click=set_ticker, args=(t,))
                    
    st.stop()

# ── Load Data ──
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_data(t, per, intv):
    stock = yf.Ticker(t)
    inf = stock.info
    if not inf or inf.get("regularMarketPrice") is None:
        if stock.fast_info is None:
            return None, f"No se encontró el ticker **{t}**"
    inc = stock.financials
    bal = stock.balance_sheet
    cf = stock.cashflow
    h = stock.history(period=per, interval=intv)
    if h is None or h.empty:
        return None, f"No hay datos de precio históricos para **{t}**"
        
    inc = inc if inc is not None else pd.DataFrame()
    bal = bal if bal is not None else pd.DataFrame()
    cf = cf if cf is not None else pd.DataFrame()
    
    return {"info": inf, "income": inc, "balance": bal, "cashflow": cf, "hist": h}, None

with st.spinner(f"Cargando datos de **{ticker}**..."):
    try:
        data_cache, err = fetch_data(ticker, chart_period, chart_interval)
        if err:
            st.error(err)
            st.stop()
            
        info = data_cache["info"]
        income = data_cache["income"]
        balance = data_cache["balance"]
        cashflow = data_cache["cashflow"]
        hist = data_cache["hist"]
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        st.stop()

# ── Parse Info ──
price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose", 0)
currency = info.get("currency", "USD")
sym = "€" if currency == "EUR" else "$"
name = info.get("shortName") or info.get("longName") or ticker
mkt_cap = info.get("marketCap", 0)
beta = info.get("beta", 1.0) or 1.0
sector = info.get("sector", "N/A")
industry = info.get("industry", "N/A")
country = info.get("country", "N/A")
shares_out = info.get("sharesOutstanding", 1)

# ── Header (Trade Republic Style) ──
pct_change = info.get('regularMarketChangePercent', 0)
chg_color = color_up if pct_change >= 0 else color_down
sign = "+" if pct_change >= 0 else ""

div_yield = info.get("dividendYield", 0)
if div_yield is None: div_yield = 0
div_str = f"{div_yield*100:.2f}%" if div_yield > 0 else "0%"

net_cash = info.get("totalCash", 0) - info.get("totalDebt", 0)
dte = info.get("debtToEquity", 0)
if dte is None: dte = 0

if net_cash > 0:
    debt_str = "<span style='color: #00C853;'>🟢 Caja Neta Positiva</span>"
elif dte > 100:
    debt_str = "<span style='color: #FF3D00;'>🔴 Alta Deuda</span>"
elif dte > 0:
    debt_str = "<span style='color: #d4af37;'>🟡 Deuda Moderada</span>"
else:
    debt_str = "⚪ Desconocido"

st.markdown(f"<h1 style='font-weight: 800; font-size: 2.2rem; letter-spacing: -1px; margin-bottom: -15px;'>{name} <span style='font-weight: 300; opacity: 0.4; font-size: 1.5rem;'>{ticker}</span></h1>", unsafe_allow_html=True)
st.markdown(f"""
    <div style="margin-bottom: 30px;">
        <span class='big-price'>{sym}{price:,.2f}</span>
        <span class='big-price-sub' style='color: {chg_color};'>{sign}{pct_change:.2f}%</span>
        <div style="margin-top: 15px; display: flex; gap: 10px;">
            <span style="background: rgba(128,128,128,0.1); border: 1px solid rgba(128,128,128,0.2); padding: 5px 12px; border-radius: 20px; font-size: 0.85rem;">💰 Rentabilidad x Dividendo: <b>{div_str}</b></span>
            <span style="background: rgba(128,128,128,0.1); border: 1px solid rgba(128,128,128,0.2); padding: 5px 12px; border-radius: 20px; font-size: 0.85rem;">🏦 Salud Financiera: <b>{debt_str}</b></span>
        </div>
    </div>
""", unsafe_allow_html=True)

st.caption(f"{sector} · {industry} · {country} · Cap: {fmt_big(mkt_cap)}")

# ── Tabs ──
tab_chart, tab_ta, tab_fin, tab_dcf, tab_comp, tab_thesis, tab_backtest, tab_mc, tab_port = st.tabs([
    "📊 Gráfico", "🕯️ Análisis Técnico", "📈 Tendencias", "💰 Valoración DCF", "⚖️ Comparativa", "📝 Tesis", "🤖 Backtest", "🎲 Monte Carlo", "💼 Mi Cartera"
])

# ── Tab 1: Chart ──
with tab_chart:
    if not hist.empty:
        hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
        hist['SMA_200'] = hist['Close'].rolling(window=200).mean()
        
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))
        
        exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
        exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
        hist['MACD'] = exp1 - exp2
        hist['Signal'] = hist['MACD'].ewm(span=9, adjust=False).mean()
        hist['MACD_Hist'] = hist['MACD'] - hist['Signal']

        body = abs(hist['Close'] - hist['Open'])
        lower_shadow = np.minimum(hist['Close'], hist['Open']) - hist['Low']
        upper_shadow = hist['High'] - np.maximum(hist['Close'], hist['Open'])
        hist['is_hammer'] = (lower_shadow > 2 * body) & (upper_shadow < body) & (body > 0)
        
        prev_close = hist['Close'].shift(1)
        prev_open = hist['Open'].shift(1)
        hist['bullish_eng'] = (prev_close < prev_open) & (hist['Close'] > hist['Open']) & (hist['Close'] > prev_open) & (hist['Open'] <= prev_close)
        hist['bearish_eng'] = (prev_close > prev_open) & (hist['Close'] < hist['Open']) & (hist['Open'] >= prev_close) & (hist['Close'] < prev_open)

        with st.expander("⚙️ Opciones del Gráfico", expanded=False):
            c_opt1, c_opt2, c_opt3, c_opt4 = st.columns(4)
            show_sma = c_opt1.checkbox("Medias Móviles (SMA)", value=False)
            show_patterns = c_opt2.checkbox("Patrones de Velas", value=False)
            show_vol = c_opt3.checkbox("Volumen", value=False)
            show_osc = c_opt4.checkbox("RSI & MACD", value=False)

        rows = 1
        row_heights = [0.5]
        titles = [""]
        
        if show_vol:
            rows += 1
            row_heights.append(0.2)
            titles.append("Volumen")
        if show_osc:
            rows += 1
            row_heights.append(0.3)
            titles.append("RSI (14) & MACD")
            
        fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.03, subplot_titles=titles if len(titles) > 1 else None,
                            row_width=row_heights[::-1])

        # Main Chart Trace
        # We determine main trend color for line chart based on first and last price in the window
        overall_trend_color = color_up if hist['Close'].iloc[-1] >= hist['Close'].iloc[0] else color_down
        
        if chart_type == "Línea Minimalista":
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], line=dict(color=overall_trend_color, width=2),
                                     fill='tozeroy', fillcolor=overall_trend_color.replace(')', ', 0.1)').replace('rgb', 'rgba') if 'rgb' in overall_trend_color else f"rgba(128,128,128,0.1)",
                                     name='Precio'), row=1, col=1)
        else:
            fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], 
                                         increasing_line_color=color_up, decreasing_line_color=color_down, name='Precio'), row=1, col=1)
        
        if show_sma:
            fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_50'], line=dict(color='orange', width=1), name='SMA 50'), row=1, col=1)
            fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_200'], line=dict(color='#00b4d8', width=1), name='SMA 200'), row=1, col=1)
        
        if show_patterns:
            bull_dates = hist[hist['bullish_eng']].index
            bull_prices = hist.loc[hist['bullish_eng'], 'Low'] * 0.98
            fig.add_trace(go.Scatter(x=bull_dates, y=bull_prices, mode='markers', marker=dict(symbol='triangle-up', size=10, color=color_up), name='Envolvente Alcista', hoverinfo='name'), row=1, col=1)

            bear_dates = hist[hist['bearish_eng']].index
            bear_prices = hist.loc[hist['bearish_eng'], 'High'] * 1.02
            fig.add_trace(go.Scatter(x=bear_dates, y=bear_prices, mode='markers', marker=dict(symbol='triangle-down', size=10, color=color_down), name='Envolvente Bajista', hoverinfo='name'), row=1, col=1)

            hammer_dates = hist[hist['is_hammer']].index
            hammer_prices = hist.loc[hist['is_hammer'], 'Low'] * 0.96
            fig.add_trace(go.Scatter(x=hammer_dates, y=hammer_prices, mode='markers', marker=dict(symbol='star', size=8, color='yellow'), name='Martillo', hoverinfo='name'), row=1, col=1)
        
        curr_row = 1
        
        if show_vol:
            curr_row += 1
            colors_vol = [color_up if row['Close'] >= row['Open'] else color_down for _, row in hist.iterrows()]
            fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='Volumen', marker_color=colors_vol, opacity=0.5), row=curr_row, col=1)

        if show_osc:
            curr_row += 1
            fig.add_trace(go.Scatter(x=hist.index, y=hist['RSI'], name='RSI', line=dict(color='purple', width=1.5)), row=curr_row, col=1)
            fig.add_hline(y=70, line_dash="dot", row=curr_row, col=1, line_color=color_down, opacity=0.5)
            fig.add_hline(y=30, line_dash="dot", row=curr_row, col=1, line_color=color_up, opacity=0.5)
            
            colors_macd = [color_up if val >= 0 else color_down for val in hist['MACD_Hist']]
            fig.add_trace(go.Bar(x=hist.index, y=hist['MACD_Hist'], name='MACD Hist', marker_color=colors_macd, opacity=0.5), row=curr_row, col=1)
            fig.add_trace(go.Scatter(x=hist.index, y=hist['MACD'], line=dict(color='blue', width=1), name='MACD'), row=curr_row, col=1)
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Signal'], line=dict(color='orange', width=1), name='Signal'), row=curr_row, col=1)

        fig.update_layout(
            height=400 + (120 if show_vol else 0) + (200 if show_osc else 0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            font=dict(family="Inter"),
            dragmode='pan',
            showlegend=False,
            hovermode='x unified'
        )
        fig.update_xaxes(rangeslider_visible=False, showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.1)")
        
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': False}, theme="streamlit")


# ── Tab 2: Technical Analysis ──
with tab_ta:
    if not hist.empty:
        st.markdown("### Resumen Técnico (Última Sesión)")
        last_row = hist.iloc[-1]
        
        col1, col2, col3 = st.columns(3)
        
        trend = f"Alcista" if last_row['Close'] > last_row['SMA_50'] else f"Bajista"
        if pd.isna(last_row['SMA_50']): trend = "N/A"
        col1.metric("Tendencia a Corto Plazo (vs SMA 50)", trend, help="Compara el precio actual con la media móvil de las últimas 50 sesiones. Si está por encima, la tendencia es alcista (positiva). Si está por debajo, es bajista (negativa).")
        
        rsi_val = last_row['RSI']
        if pd.isna(rsi_val):
            rsi_status = "N/A"
        elif rsi_val > 70:
            rsi_status = "Sobrecomprado"
        elif rsi_val < 30:
            rsi_status = "Sobrevendido"
        else:
            rsi_status = "Neutral"
        col2.metric(f"RSI (14) - {rsi_val:.1f}" if pd.notna(rsi_val) else "RSI", rsi_status, help="El Índice de Fuerza Relativa (RSI) mide si una acción ha subido o bajado demasiado rápido. >70 indica 'Sobrecompra' (posible corrección inminente). <30 indica 'Sobreventa' (posible rebote al alza).")
        
        pattern_status = "Ninguno"
        for i in range(1, min(6, len(hist) + 1)):
            row_hist = hist.iloc[-i]
            if row_hist['bullish_eng']:
                pattern_status = f"Envolvente Alcista" + (f" (hace {i-1} velas)" if i > 1 else "")
                break
            elif row_hist['bearish_eng']:
                pattern_status = f"Envolvente Bajista" + (f" (hace {i-1} velas)" if i > 1 else "")
                break
            elif row_hist['is_hammer']:
                pattern_status = f"Martillo (Alcista)" + (f" (hace {i-1} velas)" if i > 1 else "")
                break
            
        help_texts = {
            "Envolvente Alcista": "Vela verde gigante que 'envuelve' la vela roja anterior. Significa que los compradores acaban de entrar en masa y han tomado el control absoluto. Fuerte señal de subida inminente.",
            "Envolvente Bajista": "Vela roja gigante que 'envuelve' la verde anterior. Significa pánico repentino; los vendedores han tomado el control. Fuerte señal de caída inminente.",
            "Martillo (Alcista)": "El precio cayó muchísimo durante el día, pero los compradores lo empujaron de nuevo hacia arriba cerrando cerca de máximos. Indica que hay gente defendiendo ese precio, posible suelo.",
            "Ninguno": "No se ha detectado ninguna formación geométrica relevante o patrón histórico de giro en las últimas 5 sesiones."
        }
        pat_base = pattern_status.split(" (")[0]
        col3.metric("Patrón (Últimas 5 velas)", pattern_status, help=help_texts.get(pat_base, help_texts["Ninguno"]))
        
        st.divider()
        st.markdown("### 🕵️‍♂️ Flujo Institucional (Mercado de Opciones)")
        st.markdown("<p style='font-size:0.85rem; opacity:0.7; margin-top:-10px;'>Análisis del ratio Put/Call para detectar dónde están apostando los 'Tiburones' de Wall Street.</p>", unsafe_allow_html=True)
        
        try:
            tk_obj = yf.Ticker(ticker)
            opts = tk_obj.options
            if opts:
                exp_date = opts[0]
                chain = tk_obj.option_chain(exp_date)
                vol_calls = chain.calls['volume'].sum() or 0
                vol_puts = chain.puts['volume'].sum() or 0
                
                if vol_calls > 0 or vol_puts > 0:
                    pc_ratio = vol_puts / vol_calls if vol_calls > 0 else 99
                    
                    cc1, cc2, cc3 = st.columns(3)
                    cc1.metric(f"CALLS (Apuestas Alcistas)", f"{int(vol_calls):,}")
                    cc2.metric(f"PUTS (Apuestas Bajistas)", f"{int(vol_puts):,}")
                    
                    if pc_ratio > 1.2:
                        sent = "Extremo Pánico (Bajista)"
                        col_s = color_down
                    elif pc_ratio < 0.7:
                        sent = "Extrema Euforia (Alcista)"
                        col_s = color_up
                    else:
                        sent = "Neutral"
                        col_s = "gray"
                        
                    cc3.metric("Ratio Put/Call", f"{pc_ratio:.2f}", help=">1.2 indica miedo extremo (Puts). <0.7 indica euforia (Calls).")
                    st.markdown(f"<div class='glow-hover' style='border: 1px solid {col_s}; padding: 10px; border-radius: 8px; text-align: center; color: {col_s}; font-weight: 600;'>Veredicto Institucional a corto plazo: {sent} (Vencimiento: {exp_date})</div>", unsafe_allow_html=True)
                else:
                    st.info("Poco volumen de opciones para esta fecha.")
            else:
                st.info("Esta acción no tiene mercado de opciones activo (solo disponible para empresas muy grandes).")
        except Exception as e:
            st.warning("No se pudieron cargar los datos de opciones institucionales en este momento.")


# ── Tab 3: Financial Trends ──
with tab_fin:
    years = income.columns.tolist()
    year_labels = [str(d.year) if hasattr(d, 'year') else str(d) for d in years]

    def safe_row(df, key):
        if key in df.index:
            return [df.loc[key, c] if pd.notna(df.loc[key, c]) else 0 for c in df.columns]
        return [0] * len(df.columns)

    inc_data = {
        "Ingresos": safe_row(income, "Total Revenue"),
        "EBITDA": safe_row(income, "EBITDA"),
    }
    fcf_row = safe_row(cashflow, "Free Cash Flow")
    fcfs = [f if f else 0 for f in fcf_row]

    fig_bar = make_subplots(specs=[[{"secondary_y": True}]])
    fig_bar.add_trace(go.Bar(x=year_labels[::-1], y=inc_data["Ingresos"][::-1], name="Ingresos", marker_color='rgba(128,128,128,0.2)'), secondary_y=False)
    fig_bar.add_trace(go.Bar(x=year_labels[::-1], y=inc_data["EBITDA"][::-1], name="EBITDA", marker_color='rgba(212,175,55,0.4)'), secondary_y=False)
    
    margins = []
    for r, e in zip(inc_data["Ingresos"][::-1], inc_data["EBITDA"][::-1]):
        margins.append((e / r * 100) if r and r > 0 else 0)
        
    fig_bar.add_trace(go.Scatter(x=year_labels[::-1], y=margins, name="Margen EBITDA (%)", mode='lines+markers', line=dict(color='#d4af37', width=3), marker=dict(size=8)), secondary_y=True)

    fig_bar.update_layout(
        barmode='group', height=400,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=30, b=0), font=dict(family="Inter"), dragmode='pan',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_bar.update_xaxes(showgrid=False)
    fig_bar.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.1)", secondary_y=False)
    fig_bar.update_yaxes(showgrid=False, secondary_y=True)
    st.plotly_chart(fig_bar, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': False}, theme="streamlit")
    
    # Growth metric
    revs = inc_data["Ingresos"][::-1]
    if len(revs) >= 2 and revs[0] > 0:
        cagr = ((revs[-1] / revs[0]) ** (1 / (len(revs) - 1)) - 1) * 100
        st.markdown(f"<p style='text-align: center; color: var(--primary-color); font-weight: 600;'>Crecimiento Histórico de Ingresos (CAGR): +{cagr:.1f}% anual</p>", unsafe_allow_html=True)


# ── Tab 4: DCF Valuation ──
with tab_dcf:
    fcfs_pos = [f for f in fcf_row if f and f > 0]
    last_fcf = fcfs_pos[0] if fcfs_pos else 0
    if len(fcfs_pos) >= 2:
        calc_growth = max(0.02, min((fcfs_pos[0] / fcfs_pos[-1]) ** (1 / (len(fcfs_pos) - 1)) - 1, 0.25))
    else:
        calc_growth = 0.08

    risk_free = get_risk_free_rate()
    market_prem = 0.055
    ke = risk_free + beta * market_prem
    total_debt = 0
    total_equity_bs = 0
    tax_rate = 0.25
    interest_exp = 0

    if not balance.empty:
        for key in ["Total Debt", "Long Term Debt"]:
            if key in balance.index:
                v = balance.iloc[:, 0].get(key, 0)
                total_debt = v if pd.notna(v) else 0
                break
        for key in ["Stockholders Equity", "Total Stockholder Equity", "Common Stock Equity"]:
            if key in balance.index:
                v = balance.iloc[:, 0].get(key, 0)
                total_equity_bs = v if pd.notna(v) else 0
                break

    if not income.empty:
        tax_exp = income.iloc[:, 0].get("Tax Provision", 0) or 0
        pretax = income.iloc[:, 0].get("Pretax Income", 0) or 0
        if pretax and pretax != 0:
            tax_rate = abs(tax_exp / pretax)
            tax_rate = min(max(tax_rate, 0.05), 0.45)
        interest_exp = abs(income.iloc[:, 0].get("Interest Expense", 0) or 0)

    equity_val = mkt_cap if mkt_cap else max(total_equity_bs, 1)
    total_cap = total_debt + equity_val
    kd = (interest_exp / total_debt) if total_debt > 0 and interest_exp > 0 else 0.05
    kd = min(max(kd, 0.02), 0.15)
    calc_wacc = (equity_val / total_cap) * ke + (total_debt / total_cap) * kd * (1 - tax_rate) if total_cap > 0 else 0.10
    calc_terminal_g = 0.025

    col_w, col_g, col_tg = st.columns(3)
    user_wacc = col_w.slider("WACC (%)", min_value=2.0, max_value=25.0, value=float(calc_wacc*100), step=0.1, help="Coste Promedio Ponderado de Capital. Es el rendimiento MÍNIMO que los inversores exigen por asumir el riesgo de invertir aquí. A mayor riesgo, mayor WACC (lo que hace que la valoración baje).") / 100.0
    user_growth = col_g.slider("Crecimiento Corto Plazo (%)", min_value=-15.0, max_value=50.0, value=float(calc_growth*100), step=0.5, help="Estimación de cuánto crecerán los flujos de caja libre en los próximos 5 años. Á.L.V.A.R.O. te propone un valor inicial basándose en la tendencia histórica de la empresa.") / 100.0
    user_term_g = col_tg.slider("Crecimiento Terminal (%)", min_value=0.0, max_value=6.0, value=float(calc_terminal_g*100), step=0.1, help="Tasa a la que crecerá la empresa eternamente tras el año 5. Nunca debe ser mayor que el crecimiento histórico del PIB global (2-3%), porque ninguna empresa puede crecer más rápido que el mundo para siempre.") / 100.0

    wacc, growth, terminal_g = user_wacc, user_growth, user_term_g
    proj_years = 5
    proj_fcf, disc_fcf = [], []
    for i in range(1, proj_years + 1):
        f = last_fcf * (1 + growth) ** i
        d = f / (1 + wacc) ** i
        proj_fcf.append(f)
        disc_fcf.append(d)

    tv = (proj_fcf[-1] * (1 + terminal_g)) / (wacc - terminal_g) if wacc > terminal_g else 0
    pv_tv = tv / (1 + wacc) ** proj_years
    ev_dcf = sum(disc_fcf) + pv_tv

    cash = 0
    if not balance.empty:
        for key in ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"]:
            if key in balance.index:
                v = balance.iloc[:, 0].get(key, 0)
                cash = v if pd.notna(v) else 0
                break

    net_debt = total_debt - cash
    equity_value = ev_dcf - net_debt
    dcf_price = equity_value / shares_out if shares_out else 0

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Enterprise Value", fmt_big(ev_dcf), help="Es el valor total de la empresa generado por sus flujos de caja futuros descontados al presente. Es el 'precio teórico' de comprar la empresa entera hoy.")
    c2.metric("Deuda Neta", fmt_big(net_debt), help="Es la deuda total de la empresa menos el dinero en efectivo que tiene en el banco. Si es negativa, la empresa tiene más dinero del que debe (muy sano).")
    c3.metric("Equity Value", fmt_big(equity_value), help="Es el valor que realmente pertenece a los accionistas (Enterprise Value menos la Deuda Neta).")
    c4.metric("Valor por Acción (DCF)", f"{sym}{dcf_price:,.2f}", help="Es el 'Precio Justo' teórico de una sola acción según los cálculos matemáticos del DCF. Compáralo con el precio real para ver si está cara o barata.")
    
    st.divider()
    
    st.markdown("### Matriz de Sensibilidad DCF")
    st.markdown("<p style='font-size:0.85rem; opacity:0.6; margin-top:-10px;'>Simulación del Precio Justo variando el Coste de Capital (WACC) y el Crecimiento Terminal. Te protege contra proyecciones demasiado optimistas.</p>", unsafe_allow_html=True)
    
    wacc_vars = [max(0.01, wacc - 0.02), wacc, wacc + 0.02]
    tg_vars = [max(0.0, terminal_g - 0.01), terminal_g, terminal_g + 0.01]
    
    matrix_data = []
    for w in wacc_vars:
        row = []
        for tg in tg_vars:
            tv_sim = (proj_fcf[-1] * (1 + tg)) / (w - tg) if w > tg else 0
            pv_tv_sim = tv_sim / (1 + w) ** proj_years
            ev_sim = sum([f / (1 + w)**(idx+1) for idx, f in enumerate(proj_fcf)]) + pv_tv_sim
            eq_sim = ev_sim - net_debt
            row.append(eq_sim / shares_out if shares_out else 0)
        matrix_data.append(row)
        
    df_matrix = pd.DataFrame(matrix_data, 
                             index=[f"WACC {w*100:.1f}%" for w in wacc_vars], 
                             columns=[f"Term G. {tg*100:.1f}%" for tg in tg_vars])
    
    # Custom color scale matching the app vibe
    custom_colors = [[0, "rgba(255, 61, 0, 0.8)"], [0.5, "rgba(128, 128, 128, 0.2)"], [1, "rgba(0, 200, 83, 0.8)"]]
    fig_matrix = px.imshow(df_matrix, text_auto=".2f", color_continuous_scale=custom_colors, aspect="auto")
    fig_matrix.update_layout(height=220, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="JetBrains Mono"))
    fig_matrix.update_xaxes(side="top")
    st.plotly_chart(fig_matrix, use_container_width=True, config={'displayModeBar': False})
    
    st.divider()
    
    # Valuation Summary integrated here for minimalism
    net_income = income.iloc[:, 0].get("Net Income", 0) if not income.empty else 0
    ebit = income.iloc[:, 0].get("EBIT", 0) if not income.empty else 0
    methods = [("DCF", dcf_price)]
    
    bvps = total_equity_bs / shares_out if shares_out else 0
    if bvps > 0: methods.append(("Valor Contable", bvps))
    eps = net_income / shares_out if shares_out and net_income else 0
    if eps > 0 and bvps > 0: methods.append(("Nº Graham", np.sqrt(22.5 * eps * bvps)))
    op_income = ebit or 0
    if op_income > 0 and wacc > 0:
        epv_ps = ((op_income * 0.75) / wacc - net_debt) / shares_out
        if epv_ps > 0: methods.append(("EPV", epv_ps))
        
    avg_val = np.mean([v for _, v in methods])
    upside = (avg_val - price) / price if price else 0

    st.markdown("### Resumen Valoración Justa (Fair Value)")
    cc1, cc2 = st.columns([3, 1])
    with cc1:
        cols = st.columns(len(methods))
        for i, (m_name, m_val) in enumerate(methods):
            u = (m_val - price) / price if price else 0
            helps = {
                "DCF": "Basado en la proyección de flujos de caja libre futuros descontados al presente.",
                "Valor Contable": "Lo que quedaría si la empresa cerrara hoy, vendiera todo y pagara sus deudas. Es el valor más conservador.",
                "Nº Graham": "Fórmula de Benjamin Graham para encontrar acciones defensivas e infravaloradas.",
                "EPV": "Earning Power Value: Valor basado únicamente en los beneficios actuales reales, sin asumir ningún crecimiento futuro."
            }
            cols[i].metric(m_name, f"{sym}{m_val:,.2f}", help=helps.get(m_name, ""))
    with cc2:
        val_color = color_up if upside > 0 else color_down
        st.markdown(f"""
            <div class="glow-hover" style="background: rgba(128,128,128,0.1); border-radius: 12px; padding: 16px; text-align: center;">
                <div style="font-size: 12px; text-transform: uppercase; opacity: 0.7; margin-bottom: 5px;">Valor Medio</div>
                <div style="font-size: 2rem; font-weight: 700;">{sym}{avg_val:,.2f}</div>
                <div style="color: {val_color}; font-weight: 600;">{'POTENCIAL' if upside>0 else 'SOBREVAL.'} {abs(upside)*100:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)


# ── Tab 5: Multiples & Comparables ──
with tab_comp:
    ebitda = income.iloc[:, 0].get("EBITDA", 0) if not income.empty else 0
    revenue = income.iloc[:, 0].get("Total Revenue", 0) if not income.empty else 0
    ev = mkt_cap + net_debt

    cols = st.columns(4)
    multiples_data = [
        ("P/E", mkt_cap / net_income if net_income and net_income > 0 else None, "Price to Earnings: Cuántos años tardarías en recuperar tu inversión con los beneficios actuales. Valores bajos suelen indicar acciones baratas."),
        ("EV/EBITDA", ev / ebitda if ebitda and ebitda > 0 else None, "Mide el valor de la empresa frente a su rentabilidad bruta. Muy útil para comparar empresas con distinta deuda. <10x suele ser positivo."),
        ("EV/EBIT", ev / ebit if ebit and ebit > 0 else None, "Similar al EV/EBITDA pero descontando amortizaciones. Muy usado por inversores Value como Joel Greenblatt."),
        ("EV/Revenue", ev / revenue if revenue and revenue > 0 else None, "Valor frente a ventas. Útil para valorar empresas tecnológicas o de alto crecimiento que aún no dan beneficios netos."),
    ]
    for i, (name_m, val, h_text) in enumerate(multiples_data):
        cols[i].metric(name_m, f"{val:.1f}x" if val else "N/A", help=h_text)

    st.markdown("<br>", unsafe_allow_html=True)
    comp_input = st.text_input("Competidores (separados por coma)", placeholder="Ej: PEP, KDP, MNST")
    if comp_input:
        comp_tickers = [c.strip().upper() for c in comp_input.split(",") if c.strip()]
        comp_list = [{"Ticker": ticker, "P/E": multiples_data[0][1], "EV/EBITDA": multiples_data[1][1], "EV/Rev": multiples_data[3][1]}]
        
        with st.spinner("Cargando competidores..."):
            for ct in comp_tickers:
                try:
                    cti = yf.Ticker(ct).info
                    comp_list.append({
                        "Ticker": ct, 
                        "P/E": cti.get("trailingPE"), 
                        "EV/EBITDA": cti.get("enterpriseToEbitda"), 
                        "EV/Rev": cti.get("enterpriseToRevenue")
                    })
                except: pass
        
        df_comp = pd.DataFrame(comp_list).set_index("Ticker")
        st.dataframe(df_comp.style.format("{:.2f}x", na_rep="N/A"), use_container_width=True)

    st.divider()
    st.markdown("### 🥊 Fuerza Relativa (vs S&P 500)")
    st.markdown("<p style='font-size:0.85rem; opacity:0.7; margin-top:-10px;'>¿Está la acción batiendo al mercado global este periodo?</p>", unsafe_allow_html=True)
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def get_sp500(per):
        try: return yf.Ticker("^GSPC").history(period=per)
        except: return pd.DataFrame()
        
    sp500_hist = get_sp500(chart_period)
    if not sp500_hist.empty and not hist.empty:
        base_stock = hist['Close'].iloc[0]
        base_sp = sp500_hist['Close'].iloc[0]
        
        norm_stock = (hist['Close'] / base_stock) * 100
        norm_sp = (sp500_hist['Close'] / base_sp) * 100
        
        fig_rel = go.Figure()
        fig_rel.add_trace(go.Scatter(x=norm_stock.index, y=norm_stock, mode='lines', name=ticker, line=dict(color='#d4af37', width=2)))
        fig_rel.add_trace(go.Scatter(x=norm_sp.index, y=norm_sp, mode='lines', name='S&P 500', line=dict(color='rgba(255,255,255,0.4)', width=2, dash='dot')))
        
        fig_rel.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", hovermode="x unified", font=dict(family="Inter"), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig_rel.update_yaxes(title="Rendimiento Base 100", showgrid=True, gridcolor="rgba(128,128,128,0.1)")
        fig_rel.update_xaxes(showgrid=False)
        st.plotly_chart(fig_rel, use_container_width=True, config={'displayModeBar': False})

# ── Tab 6: Tesis de Inversión ──
with tab_thesis:
    st.markdown("### 📝 Generador de Tesis Fundamental")
    st.markdown("<p style='font-size:0.9rem; opacity:0.7; margin-top:-10px;'>Análisis cualitativo a medio/largo plazo basado en fosos defensivos y margen de seguridad.</p>", unsafe_allow_html=True)
    
    if st.button("Generar Tesis Institucional Automática", use_container_width=True, key="btn_thesis_main"):
        st.session_state[f"thesis_{ticker}"] = True
        
    if st.session_state.get(f"thesis_{ticker}", False):
        st.markdown("<br>", unsafe_allow_html=True)
        # 1. Moat
        net_mgn = (net_income / revenue) if revenue and revenue > 0 else 0
        if net_mgn > 0.15:
            moat_text = f"🛡️ **Foso Defensivo (Moat):** Fuerte ventaja competitiva. Un margen neto del {net_mgn*100:.1f}% demuestra poder de fijación de precios (Pricing Power). La empresa domina su sector y puede trasladar la inflación al consumidor."
        elif net_mgn > 0.05:
            moat_text = f"🛡️ **Foso Defensivo (Moat):** Estándar. Con márgenes del {net_mgn*100:.1f}%, es un negocio estable pero vulnerable a presiones de costes o competidores agresivos."
        else:
            moat_text = f"🛡️ **Foso Defensivo (Moat):** Débil o inexistente. Operar con márgenes tan ajustados ({net_mgn*100:.1f}%) exige vender un volumen masivo para sobrevivir."
            
        # 2. Risk / Valuation
        pe = mkt_cap / net_income if net_income and net_income > 0 else 999
        if upside > 0.20:
            val_txt = f"⚖️ **Margen de Seguridad:** Excelente. El mercado está deprimiendo la acción irracionalmente. Cotizando a un PER de {pe:.1f}x y con un descuento del {upside*100:.1f}%, el riesgo de pérdida a largo plazo es bajo."
        elif upside > 0:
            val_txt = f"⚖️ **Margen de Seguridad:** Aceptable. La acción cotiza por debajo de su valor intrínseco teórico, pero no hay un gran margen para el error en los próximos resultados trimestrales."
        else:
            val_txt = f"⚖️ **Margen de Seguridad:** Inexistente. El mercado asume la perfección absoluta pagando un PER de {pe:.1f}x. Cualquier fallo en su plan de negocio futuro provocará una corrección severa."
            
        # 3. Long Term
        cagr = 0
        if not income.empty and "Total Revenue" in income.index:
            revs = [v for v in income.loc["Total Revenue"].dropna().tolist() if v > 0][::-1]
            if len(revs) >= 2:
                cagr = ((revs[-1] / revs[0]) ** (1 / (len(revs) - 1)) - 1) * 100
                
        if cagr > 10:
            lt_text = f"🚀 **Perspectiva a Largo Plazo:** Crecimiento estructural brillante ({cagr:.1f}% anual). Es una candidata perfecta para estrategia 'Buy & Hold' (Comprar y Olvidar) y dejar que el interés compuesto actúe."
        elif cagr > 0:
            lt_text = f"🐢 **Perspectiva a Largo Plazo:** Negocio maduro tipo 'Cash Cow' ({cagr:.1f}% anual). Ideal para un perfil defensivo que busque dividendos, pero no esperes que duplique su tamaño pronto."
        else:
            lt_text = f"⚠️ **Perspectiva a Largo Plazo:** Contracción. Los ingresos llevan años cayendo. Más que una inversión a largo plazo, esto es una 'Value Trap' (trampa de valor) o un juego especulativo táctico."
            
        st.markdown(f"<div class='glow-hover' style='background: rgba(128,128,128,0.05); padding: 25px; border-radius: 8px; font-size: 1.05rem; line-height: 1.6; border: 1px solid rgba(212,175,55,0.3);'>{moat_text}<br><br>{val_txt}<br><br>{lt_text}</div>", unsafe_allow_html=True)

# ── Tab 7: Backtesting Á.L.V.A.R.O. ──
with tab_backtest:
    st.markdown("### 🤖 Motor de IA: Análisis Estratégico")
    
    st.markdown("#### 🎯 Veredicto Actual (HOY)")
    st.markdown("<p style='font-size:0.85rem; opacity:0.7; margin-top:-10px;'>¿Qué debes hacer AHORA MISMO según la estrategia matemática de Á.L.V.A.R.O?</p>", unsafe_allow_html=True)
    
    if not hist.empty and 'RSI' in hist and not pd.isna(hist['RSI'].iloc[-1]):
        current_rsi = hist['RSI'].iloc[-1]
        
        if current_rsi < 30:
            st.markdown(f"""
            <div style="background: rgba(0, 200, 83, 0.1); border-left: 4px solid #00C853; padding: 16px; border-radius: 4px;">
                <h3 style="color: #00C853; margin: 0;">🔥 ¡SEÑAL ACTIVA DE COMPRA HOY! (RSI: {current_rsi:.1f})</h3>
                <p style="margin: 5px 0 0 0;">El activo acaba de entrar en sobreventa extrema. Este es exactamente el momento óptimo que busca la estrategia para abrir una posición.</p>
            </div>
            """, unsafe_allow_html=True)
        elif 30 <= current_rsi <= 40:
            st.markdown(f"""
            <div style="background: rgba(212, 175, 55, 0.1); border-left: 4px solid #d4af37; padding: 16px; border-radius: 4px;">
                <h3 style="color: #d4af37; margin: 0;">⚠️ ALERTA RADAR: A PUNTO DE CARAMELO (RSI: {current_rsi:.1f})</h3>
                <p style="margin: 5px 0 0 0;">El precio está cayendo y acercándose a la zona crítica (<30). Pon esta acción en tu lista de vigilancia activa, podría dar señal de compra inminente esta misma semana.</p>
            </div>
            """, unsafe_allow_html=True)
        elif current_rsi > 70:
            st.markdown(f"""
            <div style="background: rgba(255, 61, 0, 0.1); border-left: 4px solid #FF3D00; padding: 16px; border-radius: 4px;">
                <h3 style="color: #FF3D00; margin: 0;">🛑 RIESGO: SOBRECOMPRA EXTREMA (RSI: {current_rsi:.1f})</h3>
                <p style="margin: 5px 0 0 0;">La acción ha subido demasiado rápido y está eufórica. Riesgo altísimo de corrección. Según el motor, está matemáticamente prohibido comprar hoy.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: rgba(128, 128, 128, 0.1); border-left: 4px solid rgba(128, 128, 128, 0.5); padding: 16px; border-radius: 4px;">
                <h3 style="color: rgba(255,255,255,0.8); margin: 0;">💤 ZONA NEUTRAL (RSI: {current_rsi:.1f})</h3>
                <p style="margin: 5px 0 0 0; opacity: 0.8;">El precio está en equilibrio. No hay ninguna ineficiencia matemática extrema que explotar hoy. Mantente al margen y ten paciencia.</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("#### ⏳ Verificación Histórica (Últimos 5 Años)")
    st.markdown("""
    **¿Qué estamos simulando?**  
    Simulamos que compraste ciegamente la acción cada vez que saltó la señal de sobreventa en el pasado, vendiendo exactamente **1 mes (20 sesiones) después**.  
    *Ejecuta la prueba para ver si hacerle caso al veredicto de arriba tiene ventaja estadística real.*
    """)
    
    if st.button("🚀 Ejecutar Simulación IA", use_container_width=True):
        with st.spinner("Analizando miles de velas históricas..."):
            try:
                bt_hist = yf.Ticker(ticker).history(period="5y")
                if len(bt_hist) > 50:
                    delta_bt = bt_hist['Close'].diff()
                    gain_bt = (delta_bt.where(delta_bt > 0, 0)).rolling(14).mean()
                    loss_bt = (-delta_bt.where(delta_bt < 0, 0)).rolling(14).mean()
                    rs_bt = gain_bt / loss_bt
                    bt_hist['RSI'] = 100 - (100 / (1 + rs_bt))
                    
                    signals = (bt_hist['RSI'] < 30) & (bt_hist['RSI'].shift(1) >= 30)
                    signal_dates = bt_hist[signals].index
                    
                    wins, losses = 0, 0
                    returns = []
                    dates = []
                    
                    for date in signal_dates:
                        idx = bt_hist.index.get_loc(date)
                        if idx + 20 < len(bt_hist):
                            buy_px = float(bt_hist['Close'].iloc[idx])
                            sell_px = float(bt_hist['Close'].iloc[idx + 20])
                            ret = (sell_px - buy_px) / buy_px
                            returns.append(ret * 100)
                            dates.append(date.strftime("%Y-%m-%d"))
                            if ret > 0: wins += 1
                            else: losses += 1
                            
                    if len(returns) > 0:
                        win_rate = (wins / len(returns)) * 100
                        avg_ret = np.mean(returns)
                        max_win = np.max(returns)
                        max_loss = np.min(returns)
                        
                        st.success(f"✅ **Simulación completada.** Se encontraron **{len(returns)} señales de compra** en los últimos 5 años.")
                        
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Tasa de Acierto", f"{win_rate:.1f}%", help="Porcentaje de veces que la acción subió 1 mes después de saltar la señal.")
                        c2.metric("Rentabilidad Media", f"{avg_ret:.2f}%", help="Beneficio o pérdida media de todas las operaciones simuladas juntas.")
                        c3.metric("Mejor Operación", f"+{max_win:.2f}%", help="La vez que más dinero se habría ganado con esta estrategia (en 1 solo mes).")
                        c4.metric("Peor Operación", f"{max_loss:.2f}%", help="La vez que más dinero se habría perdido con esta estrategia (en 1 solo mes).")
                        
                        colors = [color_up if r > 0 else color_down for r in returns]
                        fig_bt = go.Figure(data=[go.Bar(x=dates, y=returns, marker_color=colors)])
                        fig_bt.update_layout(
                            title="Rendimiento individual de cada operación (%)",
                            height=300, margin=dict(l=0, r=0, t=30, b=0),
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            font=dict(family="Inter")
                        )
                        fig_bt.update_yaxes(title="Beneficio/Pérdida (%)", showgrid=True, gridcolor="rgba(128,128,128,0.1)")
                        st.plotly_chart(fig_bt, use_container_width=True, config={'displayModeBar': False})
                        
                        st.divider()
                        st.markdown("### 💰 Traducción a Dinero Real (El Significado)")
                        total_profit_usd = sum([(1000 * (r/100)) for r in returns])
                        ganancia_color = color_up if total_profit_usd > 0 else color_down
                        
                        st.markdown(f"""
                        <div class="glow-hover" style="background: rgba(128,128,128,0.05); border: 1px solid rgba(128,128,128,0.2); border-radius: 8px; padding: 20px;">
                            <p style="font-size: 1.1rem; margin-bottom: 5px;">Si hubieras invertido ciegamente <b>1.000{sym} exactos</b> cada vez que Á.L.V.A.R.O. detectó esta alerta en los últimos 5 años (un total de {len(returns)} operaciones)...</p>
                            <h2 style="color: {ganancia_color}; margin-top: 0;">Habrías generado {'+' if total_profit_usd>0 else ''}{total_profit_usd:,.2f}{sym} de beneficio neto.</h2>
                            <p style="opacity: 0.6; font-size: 0.85rem; margin-bottom: 0;">*Nota: Simulador bruto sin comisiones, asumiendo inversión lineal, compra perfecta tras la alerta y venta un mes después.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        conclusion = f"**Conclusión del Algoritmo:** De las {len(returns)} veces que se activó la alerta extrema, ganaste dinero en {wins} ocasiones y perdiste en {losses}."
                        if win_rate > 55:
                            st.info(f"{conclusion} **La estrategia muestra una clara ventaja estadística.**")
                        else:
                            st.warning(f"{conclusion} **La estrategia es muy arriesgada y equivale prácticamente a tirar una moneda al aire.**")
                    else:
                        st.warning("No ha habido suficientes caídas extremas en los últimos 5 años para analizar esta señal.")
                else:
                    st.error("No hay suficientes datos históricos para este activo.")
            except Exception as e:
                st.error(f"Error en el backtest: {e}")

# ── Tab 8: Monte Carlo Simulator ──
with tab_mc:
    st.markdown("### 🎲 Simulador de Riesgo Monte Carlo")
    st.markdown("<p style='font-size:0.85rem; opacity:0.7; margin-top:-10px;'>Simulación estocástica de 1.000 escenarios futuros para calcular probabilidades reales de pérdida o ganancia en los próximos 12 meses basándose en volatilidad matemática pura.</p>", unsafe_allow_html=True)
    
    with st.expander("🎓 ¿Cómo funciona este simulador y por qué lo usan los bancos?"):
        st.markdown("""
        **La Bola de Cristal de Wall Street:** En lugar de adivinar si la acción va a subir o bajar, el método Monte Carlo acepta que el mercado es caótico. 
        Lo que hace es medir exactamente cómo se ha movido esta acción en el pasado (su volatilidad media) y utiliza algoritmos de azar (movimiento browniano) para generar **1.000 futuros paralelos**. 
        Al final, contamos en cuántos de esos futuros la acción terminó dando dinero y en cuántos se hundió. Esto te da una *probabilidad real matemática*, quitando las emociones humanas de en medio.
        """)
        
    if st.button("Ejecutar 1.000 Simulaciones Institucionales", use_container_width=True):
        if not hist.empty and len(hist) > 50:
            returns = hist['Close'].pct_change().dropna()
            mu = returns.mean()
            sigma = returns.std()
            
            days = 252 # 1 trading year
            simulations = 1000
            last_price = hist['Close'].iloc[-1]
            
            paths = np.zeros((days, simulations))
            paths[0] = last_price
            
            # Progreso
            with st.spinner("Generando 1.000 realidades alternativas..."):
                for t in range(1, days):
                    rand_rets = np.random.normal(mu, sigma, simulations)
                    paths[t] = paths[t-1] * (1 + rand_rets)
                
            final_prices = paths[-1]
            prob_gain = (final_prices > last_price).mean() * 100
            prob_loss_20 = (final_prices < (last_price * 0.80)).mean() * 100
            
            # Percentiles (Worst 5% and Best 5%)
            p5 = np.percentile(final_prices, 5)
            p95 = np.percentile(final_prices, 95)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Prob. Ganancia (1 Año)", f"{prob_gain:.1f}%", help="Porcentaje de los 1.000 futuros en los que cerrarías el año con dinero extra.")
            c2.metric("Prob. Caída Severa (>20%)", f"{prob_loss_20:.1f}%", help="Mide el riesgo extremo ('Tail Risk'). Probabilidad de perder más de un quinto de tu inversión.")
            c3.metric("Precio Promedio Esperado", f"{sym}{np.mean(final_prices):.2f}", help="La media matemática de los 1.000 escenarios.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            c4, c5 = st.columns(2)
            c4.metric("Peor Escenario (Percentil 5)", f"{sym}{p5:.2f}", help="En el 95% de los escenarios, ganarás más dinero que esto. Es tu 'red de seguridad' pesimista.")
            c5.metric("Mejor Escenario (Percentil 95)", f"{sym}{p95:.2f}", help="En un escenario hiper-optimista (solo un 5% de probabilidad de ser mejor que esto), podrías ganar hasta aquí.")
            
            fig_mc = go.Figure()
            for i in range(50):
                fig_mc.add_trace(go.Scatter(y=paths[:, i], mode='lines', line=dict(color='rgba(212,175,55,0.25)', width=1), showlegend=False))
                
            fig_mc.add_hline(y=last_price, line_dash="dot", line_color="white", annotation_text="Precio Actual")
            fig_mc.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", title="Muestra Visual: 50 Escenarios de Prueba Aleatorios", font=dict(family="Inter"))
            st.plotly_chart(fig_mc, use_container_width=True, config={'displayModeBar': False})
            
            # AI Conclusion
            verdicto = "riesgo aceptable" if prob_loss_20 < 15 else "riesgo MUY ALTO"
            st.markdown(f"""
            <div class='glow-hover' style='background: rgba(128,128,128,0.05); border: 1px solid rgba(212,175,55,0.3); border-radius: 8px; padding: 20px;'>
                <h4 style='color: #d4af37; margin-top: 0;'>🤖 Interpretación de Á.L.V.A.R.O.</h4>
                <p style='font-size: 0.9rem; line-height: 1.5; margin-bottom: 0;'>
                Basado en el caos matemático de los últimos años, si compras hoy, tienes un <b>{prob_gain:.1f}% de posibilidades</b> de terminar el año en positivo. 
                El peor escenario probable (que ocurre solo en un 5% de los multiversos) te dejaría la acción en <b>{sym}{p5:.2f}</b>, mientras que el mejor de los casos la impulsaría a <b>{sym}{p95:.2f}</b>. 
                Dado que hay un {prob_loss_20:.1f}% de probabilidad de que tu cartera caiga más de un 20%, consideramos que es una inversión de <b>{verdicto}</b> desde el punto de vista estadístico.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.warning("No hay suficientes datos históricos para simular volatilidad.")

# ── Tab 9: Portfolio Tracker ──
with tab_port:
    st.markdown("### 💼 Tu Cartera de Inversión Global")
    st.markdown("<p style='font-size:0.85rem; opacity:0.7; margin-top:-10px;'>Añade acciones para visualizar el valor total de tu patrimonio en tiempo real.</p>", unsafe_allow_html=True)
    
    if "portfolio" not in st.session_state:
        st.session_state["portfolio"] = {}
        
    c1, c2, c3 = st.columns([2, 1, 1])
    port_ticker = c1.text_input("Ticker", placeholder="Ej: MSFT", label_visibility="collapsed")
    port_shares = c2.number_input("Acciones", min_value=0.0, step=1.0, value=1.0, label_visibility="collapsed")
    
    if c3.button("➕ Añadir Acción", use_container_width=True):
        if port_ticker:
            st.session_state["portfolio"][port_ticker.upper()] = port_shares
            st.rerun()
            
    port = st.session_state["portfolio"]
    if port:
        port_data = []
        total_value = 0
        
        with st.spinner("Calculando valoración de la cartera en tiempo real..."):
            for t, shares in port.items():
                if shares > 0:
                    try:
                        p_info = yf.Ticker(t).fast_info
                        p_price = p_info.last_price
                        val = p_price * shares
                        total_value += val
                        port_data.append({"Ticker": t, "Acciones": shares, "Precio Actual": p_price, "Valor Total": val})
                    except: pass
                
        if port_data:
            st.markdown(f"<div class='glow-hover' style='background: rgba(212,175,55,0.05); border: 1px solid #d4af37; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 20px;'><h3 style='margin:0; opacity: 0.8;'>Valor Total de la Cartera</h3><h1 style='color: #d4af37; margin:0; font-size: 3rem;'>${total_value:,.2f}</h1></div>", unsafe_allow_html=True)
            
            df_port = pd.DataFrame(port_data).set_index("Ticker")
            
            c_port1, c_port2 = st.columns([1, 1])
            with c_port1:
                premium_colors = ['#d4af37', '#b38d22', '#f9e596', '#8a6e1c', '#e2c764', '#594611', '#fff']
                fig_pie = go.Figure(data=[go.Pie(
                    labels=df_port.index, 
                    values=df_port['Valor Total'], 
                    hole=0.75, 
                    marker=dict(colors=premium_colors, line=dict(color='#0a0b10', width=2)),
                    textinfo='label+percent',
                    textposition='outside',
                    hoverinfo='label+value+percent'
                )])
                fig_pie.update_layout(
                    height=350, 
                    margin=dict(l=20, r=20, t=20, b=20), 
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    font=dict(family="Inter", color="rgba(255,255,255,0.7)"),
                    showlegend=False,
                    annotations=[dict(text="ASSET<br>ALLOCATION", x=0.5, y=0.5, font_size=12, font_color="#d4af37", showarrow=False)]
                )
                st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
            with c_port2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.dataframe(df_port.style.format({"Precio Actual": "${:.2f}", "Valor Total": "${:.2f}"}), use_container_width=True)
            
            st.divider()
            if st.button("🎲 Simulación Monte Carlo Global de Cartera", type="primary", use_container_width=True):
                with st.spinner("Calculando matriz de covarianza y simulando 1.000 futuros globales..."):
                    try:
                        port_hists = {}
                        for tk, sh in port.items():
                            if sh > 0:
                                h_d = yf.Ticker(tk).history(period="1y")['Close']
                                if not h_d.empty:
                                    port_hists[tk] = h_d
                                    
                        if len(port_hists) > 0:
                            df_p = pd.DataFrame(port_hists).ffill().bfill()
                            if not df_p.empty:
                                daily_returns = df_p.pct_change().dropna()
                                
                                # Use simulation close prices to ensure weights sum to exactly 1.0
                                sim_total_val = sum([port[tk] * df_p[tk].iloc[-1] for tk in df_p.columns])
                                weights = np.array([(port[tk] * df_p[tk].iloc[-1]) / sim_total_val for tk in df_p.columns])
                                port_return = daily_returns.dot(weights)
                                
                                mu_p = port_return.mean()
                                sigma_p = port_return.std()
                            
                            days = 252
                            sims = 1000
                            paths_p = np.zeros((days, sims))
                            paths_p[0] = total_value
                            
                            for t in range(1, days):
                                rand_rets = np.random.normal(mu_p, sigma_p, sims)
                                paths_p[t] = paths_p[t-1] * (1 + rand_rets)
                                
                            final_p = paths_p[-1]
                            p5_p = np.percentile(final_p, 5)
                            p95_p = np.percentile(final_p, 95)
                            prob_loss = (final_p < total_value).mean() * 100
                            
                            st.markdown(f"#### 🔮 Proyección a 1 Año (Diversificada)")
                            c_m1, c_m2, c_m3 = st.columns(3)
                            c_m1.metric("Peor Escenario (P5)", f"${p5_p:,.2f}")
                            c_m2.metric("Promedio Esperado", f"${np.mean(final_p):,.2f}")
                            c_m3.metric("Mejor Escenario (P95)", f"${p95_p:,.2f}")
                            
                            fig_pmc = go.Figure()
                            for i in range(50):
                                fig_pmc.add_trace(go.Scatter(y=paths_p[:, i], mode='lines', line=dict(color='rgba(212,175,55,0.25)', width=1), showlegend=False))
                            fig_pmc.add_hline(y=total_value, line_dash="dot", line_color="white", annotation_text="Valor Actual")
                            fig_pmc.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"))
                            st.plotly_chart(fig_pmc, use_container_width=True, config={'displayModeBar': False})
                            
                            st.info(f"Probabilidad estadística de perder dinero este año con la cartera actual: **{prob_loss:.1f}%**")
                    except Exception as e:
                        st.error(f"Error en simulación: {e}")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Vaciar Cartera", type="secondary"):
                st.session_state["portfolio"] = {}
                st.rerun()
    else:
        st.info("Tu cartera está vacía. Añade tu primera acción arriba.")

# ── Export PDF / HTML ──
if ticker and not income.empty:
    st.sidebar.divider()
    st.sidebar.markdown("### 📥 Generar Informe")
    html_export = f"""
    <html><head><meta charset="utf-8"><title>Informe {ticker}</title>
    <style>body{{font-family:'Arial',sans-serif;background:#0a0b10;color:#fff;padding:40px;}}h1,h2,h3{{color:#d4af37;}}</style>
    </head><body>
        <h1>Informe de Valoración Profesional: {name} ({ticker})</h1>
        <h2>Precio Actual en Mercado: {sym}{price:,.2f}</h2>
        <h2>Valor Teórico Calculado (Fair Value): {sym}{avg_val:,.2f}</h2>
        <h3 style="color:{color_up if upside>0 else color_down};">POTENCIAL ESTIMADO: {abs(upside)*100:.1f}% {'ALCISTA' if upside>0 else 'BAJISTA'}</h3>
        <hr>
        <h3>Múltiplos Clave</h3>
        <ul>
            <li>PER (Price/Earnings): {mkt_cap/net_income if net_income and net_income > 0 else 0:.1f}x</li>
            <li>EV/EBITDA: {ev/ebitda if ebitda and ebitda > 0 else 0:.1f}x</li>
        </ul>
        <br><br><p style="opacity:0.5;">Generado por motor de Inteligencia Financiera Á.L.V.A.R.O. | ValuationPro</p>
    </body></html>
    """
    st.sidebar.download_button(label="📄 Descargar Informe (Imprimir PDF)", data=html_export, file_name=f"Informe_{ticker}.html", mime="text/html", use_container_width=True)

    # ── Excel Data Export ──
    @st.cache_data
    def convert_df(df):
        return df.to_csv().encode('utf-8')
        
    if not balance.empty and not income.empty:
        df_export = pd.concat([income, balance])
        csv_data = convert_df(df_export)
        st.sidebar.download_button(
            label="📊 Descargar Datos a Excel (CSV)",
            data=csv_data,
            file_name=f"{ticker}_Finanzas.csv",
            mime="text/csv",
            use_container_width=True
        )

    # ── AI Executive Summary ──
    st.sidebar.divider()
    st.sidebar.markdown("### 🤖 Á.L.V.A.R.O. Resumen Ejecutivo")
    
    margin_text = "márgenes muy rentables" if (ebitda/revenue if revenue and revenue>0 else 0) > 0.20 else "márgenes algo ajustados"
    val_text = "con descuento frente a su precio justo (potencial alcista)" if upside > 0 else "con prima (algo cara frente a su valor teórico)"
    tech_text = "en tendencia alcista a corto plazo" if (hist['Close'].iloc[-1] > hist['SMA_50'].iloc[-1] if not hist.empty and 'SMA_50' in hist else True) else "en tendencia bajista"
    
    ai_summary = f"**{name}** opera en el sector de *{sector}*. Actualmente muestra {margin_text} y, según nuestro modelo DCF, la acción cotiza {val_text}. Desde el punto de vista técnico, se encuentra {tech_text}. "
    
    if upside > 0.15:
        ai_summary += "💡 **Veredicto:** Oportunidad clara de inversión a largo plazo según fundamentales."
    elif upside < -0.15:
        ai_summary += "⚠️ **Veredicto:** Precaución. Riesgo alto de sobrevaloración fundamental."
    else:
        ai_summary += "⚖️ **Veredicto:** Valoración justa. Buscar puntos de entrada tácticos mediante el gráfico."

    st.sidebar.info(ai_summary)
