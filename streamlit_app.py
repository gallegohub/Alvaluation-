import streamlit as st
import yfinance as yf
import requests
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime
from plotly.subplots import make_subplots
import plotly.express as px

@st.cache_data(ttl=3600, show_spinner=False)
def search_ticker_by_name(query):
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=5&newsCount=0"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        res = requests.get(url, headers=headers, timeout=3)
        if res.status_code == 200:
            return [{"symbol": q["symbol"], "name": q["shortname"]} for q in res.json().get("quotes", []) if "symbol" in q and "shortname" in q]
    except: pass
    return []
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
    @keyframes price-fade-up {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .big-price { font-family: 'JetBrains Mono', monospace; font-size: 5rem; font-weight: 300; line-height: 1; letter-spacing: -3px; margin: 0; padding: 0; display: inline-block; animation: price-fade-up 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
    .big-price-sub { font-size: 1.5rem; font-weight: 600; padding-left: 10px; display: inline-block; animation: price-fade-up 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.1s forwards; opacity: 0; }
    .header-ticker { font-size: 1.5rem; font-weight: 600; opacity: 0.5; }
    .stTabs [data-baseweb="tab-list"] { gap: 12px; overflow-x: auto; padding-bottom: 5px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: nowrap; font-weight: 600; padding: 0 10px; font-size: 0.9rem; }
    
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
            "Tecnología": {"AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "GOOGL": "Alphabet", "AMZN": "Amazon", "META": "Meta", "TSLA": "Tesla", "AVGO": "Broadcom", "TSM": "TSMC", "ASML": "ASML", "ORCL": "Oracle", "AMD": "AMD", "QCOM": "Qualcomm", "CRM": "Salesforce", "NFLX": "Netflix", "ADBE": "Adobe", "CSCO": "Cisco", "INTC": "Intel", "IBM": "IBM", "NOW": "ServiceNow", "UBER": "Uber", "INTU": "Intuit", "AMAT": "Applied Materials", "TXN": "Texas Instruments", "MU": "Micron", "PANW": "Palo Alto Networks"},
            "Finanzas": {"JPM": "JPMorgan", "V": "Visa", "MA": "Mastercard", "BAC": "Bank of America", "WFC": "Wells Fargo", "MS": "Morgan Stanley", "GS": "Goldman Sachs", "AXP": "American Express", "BLK": "BlackRock", "C": "Citigroup", "CB": "Chubb", "PGR": "Progressive", "CME": "CME Group", "SPGI": "S&P Global", "MMC": "Marsh McLennan"},
            "Salud": {"UNH": "UnitedHealth", "LLY": "Eli Lilly", "JNJ": "Johnson & Johnson", "MRK": "Merck", "ABBV": "AbbVie", "TMO": "Thermo Fisher", "DHR": "Danaher", "PFE": "Pfizer", "ABT": "Abbott", "AMGN": "Amgen", "ISRG": "Intuitive Surgical", "SYK": "Stryker", "MDT": "Medtronic", "VRTX": "Vertex", "REGN": "Regeneron", "BSX": "Boston Scientific"},
            "Consumo": {"WMT": "Walmart", "PG": "Procter & Gamble", "COST": "Costco", "HD": "Home Depot", "PEP": "PepsiCo", "KO": "Coca-Cola", "MCD": "McDonald's", "NKE": "Nike", "SBUX": "Starbucks", "TGT": "Target", "LOW": "Lowe's", "EL": "Estée Lauder", "PM": "Philip Morris", "MDLZ": "Mondelez", "TJX": "TJX Companies"},
            "Energía e Industria": {"XOM": "Exxon", "CVX": "Chevron", "COP": "ConocoPhillips", "EOG": "EOG Resources", "GE": "General Electric", "CAT": "Caterpillar", "HON": "Honeywell", "BA": "Boeing", "RTX": "Raytheon", "UNP": "Union Pacific", "UPS": "UPS", "LMT": "Lockheed Martin", "DE": "Deere", "SLB": "Schlumberger", "MPC": "Marathon", "ETN": "Eaton"},
            "Telecom y Real Estate": {"AMT": "American Tower", "PLD": "Prologis", "CCI": "Crown Castle", "VZ": "Verizon", "T": "AT&T", "CMCSA": "Comcast", "DIS": "Disney", "NEE": "NextEra", "DUK": "Duke Energy", "SO": "Southern Company", "EQIX": "Equinix"}
        }
    },
    "🇪🇸 España (IBEX 35)": {
        "iso_alpha": "ESP", "lat": 40.0, "lon": -4.0, "index": "^IBEX",
        "sectors": {
            "Banca y Finanzas": {"SAN.MC": "Banco Santander", "BBVA.MC": "BBVA", "CABK.MC": "CaixaBank", "SAB.MC": "Banco Sabadell", "BKT.MC": "Bankinter", "MAP.MC": "Mapfre", "UNI.MC": "Unicaja", "ALB.MC": "Corporación Alba", "CASH.MC": "Prosegur Cash"},
            "Energía y Utilities": {"IBE.MC": "Iberdrola", "REP.MC": "Repsol", "NTGY.MC": "Naturgy", "ELE.MC": "Endesa", "ENG.MC": "Enagás", "RED.MC": "Redeia", "SLR.MC": "Solaria", "ENC.MC": "Ence", "GRE.MC": "Grenergy", "ANE.MC": "Acciona Energía"},
            "Consumo y Servicios": {"ITX.MC": "Inditex", "IAG.MC": "IAG", "MEL.MC": "Meliá Hotels", "AENA.MC": "Aena", "AMS.MC": "Amadeus", "LOG.MC": "Logista", "VIS.MC": "Viscofan", "PUIG.MC": "Puig", "DIA.MC": "Supermercados DIA", "EBRO.MC": "Ebro Foods", "NHH.MC": "NH Hotel Group", "A3M.MC": "Atresmedia", "PSG.MC": "Prosegur"},
            "Inmobiliarias (REITs)": {"MRL.MC": "Merlin Properties", "COL.MC": "Inmobiliaria Colonial"},
            "Industria y Construcción": {"FER.MC": "Ferrovial", "ACS.MC": "ACS", "MTS.MC": "ArcelorMittal", "ACX.MC": "Acerinox", "FDR.MC": "Fluidra", "SACY.MC": "Sacyr", "FCC.MC": "FCC", "ANA.MC": "Acciona", "CIE.MC": "CIE Automotive", "GEST.MC": "Gestamp", "VID.MC": "Vidrala", "CAF.MC": "CAF", "TLGO.MC": "Talgo", "TRE.MC": "Técnicas Reunidas", "OHLA.MC": "OHLA", "TUB.MC": "Tubacex", "ENO.MC": "Elecnor"},
            "Tecnología y Salud": {"TEF.MC": "Telefónica", "CLNX.MC": "Cellnex", "GRF.MC": "Grifols", "ROVI.MC": "Lab Rovi", "IDA.MC": "Indra", "ALM.MC": "Almirall", "PHM.MC": "PharmaMar", "FAE.MC": "Faes Farma"}
        }
    },
    "🇩🇪 Alemania (DAX)": {
        "iso_alpha": "DEU", "lat": 51.0, "lon": 10.0, "index": "^GDAXI",
        "sectors": {
            "Automoción e Industria": {"VOW3.DE": "Volkswagen", "BMW.DE": "BMW", "MBG.DE": "Mercedes-Benz", "PAH3.DE": "Porsche", "SIE.DE": "Siemens", "AIR.DE": "Airbus", "BAS.DE": "BASF", "BAYN.DE": "Bayer", "DTG.DE": "Daimler Truck"},
            "Finanzas y Seguros": {"ALV.DE": "Allianz", "MUV2.DE": "Munich Re", "CBK.DE": "Commerzbank", "DBK.DE": "Deutsche Bank", "HLAG.DE": "Hapag-Lloyd", "HNR1.DE": "Hannover Rück"},
            "Tecnología y Otros": {"SAP.DE": "SAP", "IFX.DE": "Infineon", "DTE.DE": "Deutsche Telekom", "DHL.DE": "DHL Group", "ADS.DE": "Adidas", "MRK.DE": "Merck KGaA", "SY1.DE": "Symrise", "SHL.DE": "Siemens Healthineers", "MTX.DE": "MTU Aero Engines", "RWE.DE": "RWE"}
        }
    },
    "🇫🇷 Francia (CAC 40)": {
        "iso_alpha": "FRA", "lat": 46.0, "lon": 2.0, "index": "^FCHI",
        "sectors": {
            "Lujo y Consumo": {"MC.PA": "LVMH", "OR.PA": "L'Oréal", "RMS.PA": "Hermès", "KER.PA": "Kering", "BN.PA": "Danone", "CDI.PA": "Christian Dior", "RI.PA": "Pernod Ricard"},
            "Industria y Energía": {"TTE.PA": "TotalEnergies", "SU.PA": "Schneider Electric", "AIR.PA": "Airbus", "CS.PA": "AXA", "SAN.PA": "Sanofi", "BNP.PA": "BNP Paribas", "VIV.PA": "Vivendi", "EN.PA": "Bouygues", "SGO.PA": "Saint-Gobain", "DG.PA": "Vinci", "LR.PA": "Legrand"}
        }
    },
    "🇬🇧 Reino Unido (FTSE 100)": {
        "iso_alpha": "GBR", "lat": 53.0, "lon": -2.0, "index": "^FTSE",
        "sectors": {
            "Finanzas y Energía": {"HSBA.L": "HSBC", "BP.L": "BP", "SHEL.L": "Shell", "BARC.L": "Barclays", "LSEG.L": "LSE Group", "STAN.L": "Standard Chartered", "PRU.L": "Prudential", "NWG.L": "NatWest", "AV.L": "Aviva"},
            "Salud y Consumo": {"AZN.L": "AstraZeneca", "GSK.L": "GSK", "ULVR.L": "Unilever", "DGE.L": "Diageo", "BATS.L": "British American Tobacco", "RKT.L": "Reckitt", "TSCO.L": "Tesco", "CPG.L": "Compass Group", "IHG.L": "IHG"},
            "Industria y Materiales": {"RIO.L": "Rio Tinto", "GLEN.L": "Glencore", "AAL.L": "Anglo American", "BA.L": "BAE Systems", "RR.L": "Rolls-Royce", "CRH.L": "CRH", "NXT.L": "Next"}
        }
    },
    "🇨🇭 Suiza": {
        "iso_alpha": "CHE", "lat": 46.8, "lon": 8.2, "index": "^SSMI",
        "sectors": {
            "Salud y Consumo": {"NESN.SW": "Nestlé", "NOVN.SW": "Novartis", "ROG.SW": "Roche", "CFR.SW": "Richemont", "GIVN.SW": "Givaudan", "ALC.SW": "Alcon"},
            "Finanzas e Industria": {"UBSG.SW": "UBS Group", "ZURN.SW": "Zurich Insurance", "ABBN.SW": "ABB", "SIKA.SW": "Sika", "HOLN.SW": "Holcim", "LONN.SW": "Lonza"}
        }
    },
    "🇳🇱 Países Bajos": {
        "iso_alpha": "NLD", "lat": 52.1, "lon": 5.2, "index": "^AEX",
        "sectors": {
            "Tecnología y Finanzas": {"ASML.AS": "ASML", "ADYEN.AS": "Adyen", "INGA.AS": "ING Group", "UNA.AS": "Unilever", "HEIA.AS": "Heineken", "PHIA.AS": "Philips", "DSM.AS": "DSM-Firmenich", "PRX.AS": "Prosus"}
        }
    },
    "🇮🇹 Italia": {
        "iso_alpha": "ITA", "lat": 41.8, "lon": 12.5, "index": "FTSEMIB.MI",
        "sectors": {
            "Finanzas e Industria": {"ISP.MI": "Intesa Sanpaolo", "UCG.MI": "UniCredit", "ENEL.MI": "Enel", "ENI.MI": "Eni", "RACE.MI": "Ferrari", "STLAM.MI": "Stellantis", "G.MI": "Generali", "PRY.MI": "Prysmian"}
        }
    },
    "🇯🇵 Japón (Nikkei)": {
        "iso_alpha": "JPN", "lat": 36.0, "lon": 138.0, "index": "^N225",
        "sectors": {
            "Tecnología y Motor": {"7203.T": "Toyota", "6758.T": "Sony", "9984.T": "SoftBank", "8035.T": "Tokyo Electron", "7974.T": "Nintendo", "6981.T": "Murata", "7267.T": "Honda", "6594.T": "Nidec", "6762.T": "TDK", "7741.T": "HOYA", "6954.T": "FANUC"},
            "Finanzas e Industria": {"8306.T": "Mitsubishi UFJ", "8058.T": "Mitsubishi Corp", "9432.T": "NTT", "6861.T": "Keyence", "4502.T": "Takeda", "4568.T": "Daiichi Sankyo", "6098.T": "Recruit", "6367.T": "Daikin", "8001.T": "ITOCHU", "9983.T": "Fast Retailing"}
        }
    },
    "🇨🇳 China y HK": {
        "iso_alpha": "CHN", "lat": 35.0, "lon": 104.0, "index": "^HSI",
        "sectors": {
            "Tecnología": {"0700.HK": "Tencent", "9988.HK": "Alibaba", "3690.HK": "Meituan", "1810.HK": "Xiaomi", "0981.HK": "SMIC", "BIDU": "Baidu", "JD": "JD.com", "PDD": "Pinduoduo", "NTES": "NetEase", "09618.HK": "JD Logistics"},
            "Finanzas y Consumo": {"0939.HK": "CCB", "1398.HK": "ICBC", "1299.HK": "AIA Group", "0027.HK": "Galaxy Ent", "2318.HK": "Ping An", "3988.HK": "Bank of China", "BYDDF": "BYD", "NIO": "NIO", "XPEV": "XPeng", "LI": "Li Auto", "0883.HK": "CNOOC"}
        }
    },
    "🇰🇷 Corea del Sur": {
        "iso_alpha": "KOR", "lat": 35.9, "lon": 127.7, "index": "^KS11",
        "sectors": {
            "Tecnología e Industria": {"005930.KS": "Samsung Electronics", "000660.KS": "SK Hynix", "005380.KS": "Hyundai Motor", "051910.KS": "LG Chem", "000270.KS": "Kia", "035420.KS": "NAVER", "068270.KS": "Celltrion", "005490.KS": "POSCO", "035720.KS": "Kakao"}
        }
    },
    "🇹🇼 Taiwán": {
        "iso_alpha": "TWN", "lat": 23.6, "lon": 120.9, "index": "^TWII",
        "sectors": {
            "Tecnología e Industria": {"2330.TW": "TSMC", "2317.TW": "Foxconn (Hon Hai)", "2454.TW": "MediaTek", "2308.TW": "Delta Electronics", "2382.TW": "Quanta Computer", "2881.TW": "Fubon Financial", "2412.TW": "Chunghwa Telecom"}
        }
    },
    "🇮🇳 India": {
        "iso_alpha": "IND", "lat": 20.5, "lon": 78.9, "index": "^BSESN",
        "sectors": {
            "Mercado General": {"RELIANCE.NS": "Reliance Industries", "TCS.NS": "Tata Consultancy", "HDFCBANK.NS": "HDFC Bank", "INFY.NS": "Infosys", "ICICIBANK.NS": "ICICI Bank", "SBIN.NS": "State Bank of India", "BHARTIARTL.NS": "Bharti Airtel", "ITC.NS": "ITC", "HINDUNILVR.NS": "Hindustan Unilever"}
        }
    },
    "🇨🇦 Canadá": {
        "iso_alpha": "CAN", "lat": 56.0, "lon": -106.0, "index": "^GSPTSE",
        "sectors": {
            "Finanzas y Energía": {"RY.TO": "RBC", "TD.TO": "TD Bank", "ENB.TO": "Enbridge", "CNQ.TO": "Canadian Natural", "BMO.TO": "Bank of Montreal", "BNS.TO": "Scotiabank", "SU.TO": "Suncor", "TRP.TO": "TC Energy"},
            "Tecnología y Otros": {"SHOP.TO": "Shopify", "CNR.TO": "Canadian National", "BAM.TO": "Brookfield", "CP.TO": "Canadian Pacific", "CSU.TO": "Constellation", "NTR.TO": "Nutrien", "ATD.TO": "Alimentation Couche-Tard"}
        }
    },
    "🇧🇷 Brasil": {
        "iso_alpha": "BRA", "lat": -14.0, "lon": -51.0, "index": "^BVSP",
        "sectors": {
            "Mercado General": {"PETR4.SA": "Petrobras", "VALE3.SA": "Vale", "ITUB4.SA": "Itaú", "BBDC4.SA": "Bradesco", "ABEV3.SA": "Ambev", "WEGE3.SA": "WEG", "B3SA3.SA": "B3", "BBAS3.SA": "Banco do Brasil", "ELET3.SA": "Eletrobras", "RENT3.SA": "Localiza", "SUZB3.SA": "Suzano", "RADL3.SA": "RaiaDrogasil"}
        }
    },
    "🇦🇷 Argentina": {
        "iso_alpha": "ARG", "lat": -38.4, "lon": -63.6, "index": "^MERV",
        "sectors": {
            "Mercado General": {"MELI": "MercadoLibre", "YPF": "YPF", "BMA": "Banco Macro", "GGAL": "Grupo Fin. Galicia", "PAM": "Pampa Energía", "TEO": "Telecom Argentina", "GLOB": "Globant", "DESP": "Despegar", "CEPU": "Central Puerto", "LOMA": "Loma Negra", "CRESY": "Cresud"}
        }
    },
    "🇲🇽 México": {
        "iso_alpha": "MEX", "lat": 23.6, "lon": -102.5, "index": "^MXX",
        "sectors": {
            "Mercado General": {"AMX": "América Móvil", "WALMEX.MX": "Walmart de México", "GMEXICOB.MX": "Grupo México", "FEMSAUBD.MX": "Fomento Económico", "CX": "Cemex", "GFNORTEO.MX": "Banorte", "BBAJIOO.MX": "Banco del Bajío", "KOF": "Coca-Cola FEMSA"}
        }
    },
    "🇨🇱 Chile": {
        "iso_alpha": "CHL", "lat": -35.6, "lon": -71.5, "index": "^IPSA",
        "sectors": {
            "Mercado General": {"SQM": "SQM", "BCH": "Banco de Chile", "ENIA": "Enel Américas", "LTM": "LATAM Airlines", "BSAC": "Banco Santander Chile", "CCU": "Compañía Cervecerías Unidas"}
        }
    },
    "🇨🇴 Colombia": {
        "iso_alpha": "COL", "lat": 4.5, "lon": -74.0, "index": "^COLCAP",
        "sectors": {
            "Mercado General": {"EC": "Ecopetrol", "CIB": "Bancolombia", "AVAL": "Grupo Aval"}
        }
    },
    "🇦🇺 Australia": {
        "iso_alpha": "AUS", "lat": -25.0, "lon": 133.0, "index": "^AXJO",
        "sectors": {
            "Mercado General": {"BHP.AX": "BHP", "RIO.AX": "Rio Tinto", "CBA.AX": "CommBank", "CSL.AX": "CSL", "WBC.AX": "Westpac", "NAB.AX": "NAB", "ANZ.AX": "ANZ", "MQG.AX": "Macquarie", "FMG.AX": "Fortescue", "WES.AX": "Wesfarmers", "TLS.AX": "Telstra", "WOW.AX": "Woolworths", "WDS.AX": "Woodside", "TCL.AX": "Transurban"}
        }
    },
    "🇩🇰 Dinamarca": {
        "iso_alpha": "DNK", "lat": 56.0, "lon": 10.0, "index": "^OMXC20",
        "sectors": {
            "Salud e Industria": {"NVO": "Novo Nordisk", "DSV.CO": "DSV", "MAERSK-B.CO": "A.P. Moller-Maersk", "VWS.CO": "Vestas", "ORSTED.CO": "Orsted", "CARL-B.CO": "Carlsberg", "PNDORA.CO": "Pandora", "NOVOB.CO": "Novozymes"}
        }
    },
    "🇸🇪 Suecia": {
        "iso_alpha": "SWE", "lat": 60.0, "lon": 15.0, "index": "^OMX",
        "sectors": {
            "Industria y Tecnología": {"SPOT": "Spotify", "VOLV-B.ST": "Volvo", "ERIC-B.ST": "Ericsson", "ATCO-A.ST": "Atlas Copco", "ASSA-B.ST": "ASSA ABLOY", "HM-B.ST": "H&M", "SEB-A.ST": "SEB", "SAND.ST": "Sandvik", "EPI-A.ST": "Epiroc"}
        }
    },
    "🇿🇦 Sudáfrica": {
        "iso_alpha": "ZAF", "lat": -30.0, "lon": 25.0, "index": "^J203.JO",
        "sectors": {
            "Minería y Finanzas": {"NPN.JO": "Naspers", "FSR.JO": "FirstRand", "GFI.JO": "Gold Fields", "AGL.JO": "Anglo American SA", "SBK.JO": "Standard Bank", "MTN.JO": "MTN Group", "VOD.JO": "Vodacom"}
        }
    },
    "🇮🇱 Israel": {
        "iso_alpha": "ISR", "lat": 31.0, "lon": 35.0, "index": "^TA125.TA",
        "sectors": {
            "Tecnología y Ciberseguridad": {"CHKP": "Check Point", "TEVA": "Teva Pharma", "CYBR": "CyberArk", "WIX": "Wix", "MNDY": "monday.com", "NICE": "NICE Systems", "FVRR": "Fiverr"}
        }
    },
    "🇸🇬 Singapur": {
        "iso_alpha": "SGP", "lat": 1.3, "lon": 103.8, "index": "^STI",
        "sectors": {
            "Finanzas y Consumo": {"SE": "Sea Ltd", "D05.SI": "DBS Group", "O39.SI": "OCBC Bank", "U11.SI": "UOB", "Z74.SI": "Singtel", "C52.SI": "ComfortDelGro", "GRAB": "Grab"}
        }
    },
    "🇮🇩 Indonesia": {
        "iso_alpha": "IDN", "lat": -2.0, "lon": 118.0, "index": "^JKSE",
        "sectors": {
            "Banca y Telecomunicaciones": {"BBCA.JK": "Bank Central Asia", "BBRI.JK": "Bank Rakyat", "TLKM.JK": "Telkom Indonesia", "BMRI.JK": "Bank Mandiri", "ASII.JK": "Astra International"}
        }
    },
    "🇵🇹 Portugal": {
        "iso_alpha": "PRT", "lat": 39.5, "lon": -8.0, "index": "^PSI20",
        "sectors": {
            "Energía y Consumo": {"EDP.LS": "EDP Renováveis", "GALP.LS": "Galp Energia", "JMT.LS": "Jerónimo Martins", "BCP.LS": "Banco Comercial Português", "SON.LS": "Sonae"}
        }
    },
    "🇮🇪 Irlanda": {
        "iso_alpha": "IRL", "lat": 53.0, "lon": -8.0, "index": "^ISEQ",
        "sectors": {
            "Multinacionales y Aviación": {"ACN": "Accenture", "RYAAY": "Ryanair", "CRH": "CRH PLC", "FLTR.L": "Flutter Ent", "STX": "Seagate", "EAT": "Brinker (Eat)"}
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
def get_risk_free_rate_v2():
    try:
        tnx = yf.Ticker("^TNX")
        rate = tnx.fast_info.last_price
        if rate:
            return rate / 100.0
    except:
        pass
    return 0.043

@st.cache_data(ttl=600)
def get_market_status_v3():
    status = {}
    indices_map = {data["index"]: country for country, data in MARKETS_BY_COUNTRY.items() if "index" in data}
    indices = list(indices_map.keys())
    if indices:
        try:
            h = yf.download(indices, period="5d", progress=False)
            if 'Close' in h:
                closes = h['Close']
                for idx_ticker, country in indices_map.items():
                    try:
                        col = closes[idx_ticker].dropna() if isinstance(closes, pd.DataFrame) else closes.dropna()
                        if len(col) >= 2:
                            price = float(col.iloc[-1])
                            prev = float(col.iloc[-2])
                            status[country] = (price - prev) / prev
                        else: status[country] = 0.0
                    except: status[country] = 0.0
        except: pass
    
    # Rellenar con 0 si algo falló
    for c in MARKETS_BY_COUNTRY.keys():
        if c not in status: status[c] = 0.0
    return status

# ── Sidebar ──
st.sidebar.markdown("""
<style>
    @keyframes alvaro-pulse {
        0%, 100% { text-shadow: 0 0 4px rgba(212,175,55,0.2); opacity: 0.75; }
        50% { text-shadow: 0 0 20px rgba(212,175,55,0.9), 0 0 40px rgba(212,175,55,0.4), 0 0 60px rgba(212,175,55,0.15); opacity: 1; }
    }
    @keyframes dot-pulse {
        0%, 100% { box-shadow: 0 0 4px rgba(212,175,55,0.4); opacity: 0.5; }
        50% { box-shadow: 0 0 12px rgba(212,175,55,1), 0 0 20px rgba(212,175,55,0.5); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

c_logo1, c_logo2 = st.sidebar.columns([1, 4])
try:
    c_logo1.image("logo_a.png", use_container_width=True)
except:
    c_logo1.markdown("""
    <div style='text-align:center; margin-top:5px;'>
        <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="1" y="1" width="34" height="34" rx="8" stroke="#d4af37" stroke-width="1.5" fill="rgba(212,175,55,0.06)"/>
            <rect x="8" y="20" width="4" height="8" rx="1" fill="rgba(212,175,55,0.4)"/>
            <rect x="14" y="14" width="4" height="14" rx="1" fill="rgba(212,175,55,0.6)"/>
            <rect x="20" y="17" width="4" height="11" rx="1" fill="rgba(212,175,55,0.5)"/>
            <rect x="26" y="10" width="4" height="18" rx="1" fill="#d4af37"/>
            <line x1="8" y1="8" x2="14" y2="12" stroke="#d4af37" stroke-width="1" stroke-linecap="round" opacity="0.6"/>
            <line x1="14" y1="12" x2="20" y2="15" stroke="#d4af37" stroke-width="1" stroke-linecap="round" opacity="0.6"/>
            <line x1="20" y1="15" x2="26" y2="8" stroke="#d4af37" stroke-width="1" stroke-linecap="round" opacity="0.6"/>
            <circle cx="8" cy="8" r="2" fill="#d4af37" opacity="0.7"/>
            <circle cx="14" cy="12" r="2" fill="#d4af37" opacity="0.7"/>
            <circle cx="20" cy="15" r="2" fill="#d4af37" opacity="0.7"/>
            <circle cx="26" cy="8" r="2" fill="#d4af37" opacity="0.7"/>
        </svg>
    </div>
    """, unsafe_allow_html=True)
c_logo2.markdown("<h2 style='font-weight: 800; letter-spacing: -1px; margin-top: 5px;'>Valuation<span style='font-weight: 300; color: #d4af37;'>Pro</span></h2>", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style='margin-bottom: 20px; margin-top: -15px; background: linear-gradient(135deg, rgba(212,175,55,0.06) 0%, rgba(0,0,0,0) 100%); border: 1px solid rgba(212,175,55,0.12); border-radius: 10px; padding: 12px 14px;'>
    <div style='display: flex; align-items: center; gap: 8px;'>
        <div style='width: 6px; height: 6px; border-radius: 50%; background: #d4af37; animation: dot-pulse 2s ease-in-out infinite; flex-shrink: 0;'></div>
        <span style='font-size: 0.6rem; text-transform: uppercase; letter-spacing: 2px; opacity: 0.45; font-family: Outfit, sans-serif;'>Powered by</span>
    </div>
    <p style='margin: 4px 0 2px 14px; font-weight: 800; font-size: 1.05rem; letter-spacing: 2px; color: #d4af37; animation: alvaro-pulse 2.5s ease-in-out infinite; font-family: JetBrains Mono, monospace;'>Á.L.V.A.R.O.</p>
    <p style='margin: 0 0 0 14px; font-size: 0.5rem; opacity: 0.35; text-transform: uppercase; letter-spacing: 0.8px; line-height: 1.4; font-family: Outfit, sans-serif;'>Advanced Liquidity & Valuation<br>Algorithm for Research Optimization</p>
</div>
""", unsafe_allow_html=True)
st.sidebar.divider()

def set_ticker(t):
    st.session_state["ticker_input"] = t

# ── Watchlist System ──
if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = []

def _add_to_watchlist(t):
    if t and t not in st.session_state["watchlist"]:
        st.session_state["watchlist"].append(t)

def _remove_from_watchlist(t):
    if t in st.session_state["watchlist"]:
        st.session_state["watchlist"].remove(t)

st.sidebar.markdown("### 🔍 Buscar Acción")
ticker_input = st.sidebar.text_input(" ", placeholder="Escribe ticker o nombre...", key="ticker_input", label_visibility="collapsed")
compare_ticker = st.sidebar.text_input("🆚 Comparar con...", placeholder="Ej: MSFT", key="compare_input").strip().upper()

if ticker_input and len(ticker_input) > 1:
    search_res = search_ticker_by_name(ticker_input)
    if search_res and search_res[0]["symbol"].upper() != ticker_input.upper():
        st.sidebar.markdown("<p style='font-size:0.8rem; opacity:0.7; margin-bottom:5px; margin-top:-10px;'>¿Querías decir...?</p>", unsafe_allow_html=True)
        for r in search_res:
            st.sidebar.button(f"**{r['symbol']}** · {r['name'][:22]}", key=f"src_{r['symbol']}", on_click=set_ticker, args=(r['symbol'],), use_container_width=True)
        st.sidebar.divider()
        st.stop()

st.sidebar.button("🌍 Explorador de Mercados", use_container_width=True, on_click=set_ticker, args=("",))

# ── Watchlist Display ──
if st.session_state["watchlist"]:
    st.sidebar.divider()
    st.sidebar.markdown("### ⭐ Watchlist")
    for _wt in st.session_state["watchlist"]:
        _wc1, _wc2 = st.sidebar.columns([4, 1])
        try:
            _wfi = yf.Ticker(_wt).fast_info
            _wp = _wfi.last_price
            _wprev = _wfi.previous_close
            _wchg = ((_wp - _wprev) / _wprev * 100) if _wprev else 0
            _wcol = "#00C853" if _wchg >= 0 else "#FF3D00"
            _wsign = "+" if _wchg >= 0 else ""
            _wc1.markdown(f"<div style='cursor:pointer; padding:4px 0;'><span style='font-weight:700; font-size:0.85rem;'>{_wt}</span> <span style='font-family:JetBrains Mono,monospace; font-size:0.8rem; opacity:0.8;'>${_wp:,.2f}</span> <span style='color:{_wcol}; font-size:0.75rem; font-weight:600;'>{_wsign}{_wchg:.1f}%</span></div>", unsafe_allow_html=True)
        except:
            _wc1.markdown(f"<span style='font-weight:600;'>{_wt}</span> <span style='opacity:0.4; font-size:0.8rem;'>sin datos</span>", unsafe_allow_html=True)
        _wc2.button("✕", key=f"wl_rm_{_wt}", on_click=_remove_from_watchlist, args=(_wt,))
    # Click watchlist item to navigate
    for _wt in st.session_state["watchlist"]:
        st.sidebar.button(f"📈 Ver {_wt}", key=f"wl_go_{_wt}", on_click=set_ticker, args=(_wt,), use_container_width=True)

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
    # ── Ticker Tape Banner ──
    @st.cache_data(ttl=900, show_spinner=False)
    def get_ticker_tape():
        tape_indices = {
            "S&P 500": "^GSPC", "Nasdaq 100": "^NDX", "Dow Jones": "^DJI",
            "IBEX 35": "^IBEX", "Euro Stoxx 50": "^STOXX50E", "FTSE 100": "^FTSE",
            "Nikkei 225": "^N225", "Hang Seng": "^HSI"
        }
        tape_items = []
        try:
            tickers_list = list(tape_indices.values())
            h = yf.download(tickers_list, period="5d", progress=False)
            if 'Close' in h:
                closes = h['Close']
                for name, tk in tape_indices.items():
                    try:
                        col = closes[tk].dropna() if isinstance(closes, pd.DataFrame) else closes.dropna()
                        if len(col) >= 2:
                            pct = (float(col.iloc[-1]) - float(col.iloc[-2])) / float(col.iloc[-2]) * 100
                            tape_items.append({"name": name, "pct": pct})
                        else:
                            tape_items.append({"name": name, "pct": 0.0})
                    except:
                        tape_items.append({"name": name, "pct": 0.0})
        except: pass
        return tape_items

    tape_data = get_ticker_tape()
    
    if tape_data:
        tape_html_items = ""
        for i, item in enumerate(tape_data):
            pct = item["pct"]
            sign = "+" if pct >= 0 else ""
            color = "#00C853" if pct >= 0 else "#FF3D00"
            arrow = "▲" if pct >= 0 else "▼"
            sep = '<span style="margin: 0 20px; color: rgba(212,175,55,0.3);">◆</span>' if i < len(tape_data) - 1 else ''
            tape_html_items += f'<span style="white-space: nowrap;"><span style="opacity: 0.55; font-weight: 400;">{item["name"]}</span>&nbsp;&nbsp;<span style="color: {color}; font-weight: 600;">{arrow} {sign}{pct:.2f}%</span></span>{sep}'
        
        # Triplicate for seamless loop
        full_sep = '<span style="margin: 0 20px; color: rgba(212,175,55,0.3);">◆</span>'
        tape_content = tape_html_items + full_sep + tape_html_items + full_sep + tape_html_items
        
        st.markdown(f"""
        <style>
            @keyframes ticker-scroll {{
                0% {{ transform: translate3d(0, 0, 0); }}
                100% {{ transform: translate3d(-33.333%, 0, 0); }}
            }}
            .ticker-tape-wrap {{
                overflow: hidden;
                position: relative;
                background: linear-gradient(180deg, rgba(10,11,16,0.98) 0%, rgba(15,16,22,0.95) 100%);
                border-top: 1px solid rgba(212, 175, 55, 0.2);
                border-bottom: 1px solid rgba(212, 175, 55, 0.2);
                box-shadow: 0 2px 20px rgba(212, 175, 55, 0.06), inset 0 0 30px rgba(0,0,0,0.3);
                padding: 12px 0;
                margin-bottom: 20px;
                border-radius: 8px;
            }}
            .ticker-tape-wrap::before,
            .ticker-tape-wrap::after {{
                content: '';
                position: absolute;
                top: 0;
                bottom: 0;
                width: 60px;
                z-index: 2;
                pointer-events: none;
            }}
            .ticker-tape-wrap::before {{
                left: 0;
                background: linear-gradient(to right, rgba(10,11,16,1) 0%, transparent 100%);
            }}
            .ticker-tape-wrap::after {{
                right: 0;
                background: linear-gradient(to left, rgba(10,11,16,1) 0%, transparent 100%);
            }}
            .ticker-tape-inner {{
                display: flex;
                align-items: center;
                width: max-content;
                animation: ticker-scroll 45s linear infinite;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.82rem;
                letter-spacing: 0.3px;
                will-change: transform;
                backface-visibility: hidden;
                -webkit-font-smoothing: antialiased;
            }}
            .ticker-tape-wrap:hover .ticker-tape-inner {{
                animation-play-state: paused;
            }}
        </style>
        <div class="ticker-tape-wrap">
            <div class="ticker-tape-inner">
                {tape_content}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="text-align: center; margin-top: 2vh; margin-bottom: 20px;">
            <h1 style='font-size: 3.5rem; font-weight: 300; letter-spacing: -2px; margin-bottom: 0;'>Explorador Global</h1>
            <p style='font-size: 1rem; opacity: 0.5; font-weight: 400; margin-top: 5px; letter-spacing: 0.5px;'>Selecciona un mercado brillante en el mapa para descubrir acciones</p>
        </div>
    """, unsafe_allow_html=True)
    
    market_status = get_market_status_v3()
    
    lats = []
    lons = []
    texts = []
    colors = []
    
    for country, data in MARKETS_BY_COUNTRY.items():
        lats.append(data["lat"])
        lons.append(data["lon"])
        pct = market_status.get(country, 0)
        sign = "+" if pct >= 0 else ""
        idx_name = data.get("index", "N/A")
        texts.append(f"<b>{country}</b><br>Índice: {idx_name}<br>Cambio: {sign}{pct*100:.2f}%")
        # Gradient intensity: stronger color for bigger moves
        intensity = min(abs(pct) * 30, 1.0)  # Scale: 3.3% move = full intensity
        intensity = max(intensity, 0.25)  # Minimum visibility
        if pct >= 0:
            colors.append(f"rgba(0, 200, 83, {intensity})")
        else:
            colors.append(f"rgba(255, 61, 0, {intensity})")
        
    fig_globe = go.Figure()
    
    # Base dark choropleth (no highlighting by default)
    fig_globe.add_trace(go.Choropleth(
        locations=[d["iso_alpha"] for d in MARKETS_BY_COUNTRY.values()],
        z=[1]*len(MARKETS_BY_COUNTRY),
        colorscale=[[0, "rgba(20,20,30,0.9)"], [1, "rgba(20,20,30,0.9)"]],
        showscale=False,
        marker_line_width=0.5,
        marker_line_color="rgba(212,175,55,0.3)",
        hoverinfo='skip'
    ))
    
    # Glowing Halo (Large transparent dots)
    fig_globe.add_trace(go.Scattergeo(
        lat=lats, lon=lons, text=texts,
        mode="markers",
        marker=dict(size=30, color=colors, opacity=0.2),
        hoverinfo="skip",
        name="Halo"
    ))
    
    # Core nodes
    fig_globe.add_trace(go.Scattergeo(
        lat=lats, lon=lons, text=texts,
        mode="markers",
        marker=dict(size=9, color=colors, line=dict(width=1.5, color="rgba(255,255,255,0.9)")),
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
        showcoastlines=True, coastlinecolor="rgba(212, 175, 55, 0.8)", coastlinewidth=1.5,
        showland=True, landcolor="rgba(10,11,16,0.95)",
        showocean=True, oceancolor="rgba(5,5,10,0.98)",
        showcountries=True, countrycolor="rgba(212,175,55,0.2)", countrywidth=0.5,
        lonaxis=dict(showgrid=True, gridcolor="rgba(212, 175, 55, 0.12)", gridwidth=1, dtick=15),
        lataxis=dict(showgrid=True, gridcolor="rgba(212, 175, 55, 0.12)", gridwidth=1, dtick=15),
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
            
            stat.markdown(f"<p style='text-align:center; font-size:13px; font-weight:600; opacity:0.8; color: #d4af37;'>Descargando datos históricos masivos de {len(all_ticks)} empresas...</p>", unsafe_allow_html=True)
            prog.progress(0.2)
            
            try:
                # Batch download all tickers at once using multithreading
                data = yf.download(all_ticks, period="1mo", progress=False)
                
                closes = data['Close'] if 'Close' in data else pd.DataFrame()
                opens = data['Open'] if 'Open' in data else pd.DataFrame()
                
                if not closes.empty and not opens.empty:
                    for i, t in enumerate(all_ticks):
                        stat.markdown(f"<p style='text-align:center; font-size:13px; font-weight:600; opacity:0.8; color: #d4af37;'>Analizando algoritmos {i+1}/{len(all_ticks)}: Procesando {t}...</p>", unsafe_allow_html=True)
                        
                        # Handle multi-index columns vs single column
                        t_close = closes[t].dropna() if isinstance(closes, pd.DataFrame) and t in closes.columns else (closes.dropna() if len(all_ticks)==1 else pd.Series(dtype=float))
                        t_open = opens[t].dropna() if isinstance(opens, pd.DataFrame) and t in opens.columns else (opens.dropna() if len(all_ticks)==1 else pd.Series(dtype=float))
                        
                        if len(t_close) >= 15:
                            last_c = t_close.iloc[-1]
                            prev_c = t_close.iloc[-2]
                            last_o = t_open.iloc[-1]
                            prev_o = t_open.iloc[-2]
                            
                            # RSI
                            delta = t_close.diff()
                            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
                            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
                            rs = gain / loss if loss != 0 else 100
                            rsi = 100 - (100 / (1 + rs))
                            
                            # Bullish Engulfing
                            bull = (prev_c < prev_o) and (last_c > last_o) and (last_c > prev_o) and (last_o <= prev_c)
                            
                            if pd.notna(rsi) and rsi < rsi_limit:
                                ops.append({"ticker": t, "text": f"🟢 {t}: RSI Sobrevendido ({rsi:.1f})"})
                            if bull:
                                ops.append({"ticker": t, "text": f"🔥 {t}: Envolvente Alcista detectada"})
                                
                        prog.progress(0.2 + (0.8 * (i + 1) / len(all_ticks)))
            except Exception as e:
                st.error(f"Error procesando mercado en bloque: {e}")
                
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
def fetch_data_v4(t, per, intv):
    h = pd.DataFrame()
    try:
        h_dl = yf.download(t, period=per, interval=intv, progress=False)
        if isinstance(h_dl.columns, pd.MultiIndex):
            h = h_dl.xs(t, axis=1, level=1) if t in h_dl.columns.get_level_values(1) else h_dl
        else:
            h = h_dl
    except: pass

    stock = yf.Ticker(t)
    
    if h is None or h.empty:
        try: h = stock.history(period=per, interval=intv)
        except: pass
        
    if h is None or h.empty:
        return None, f"Error severo (Too Many Requests / Rate Limit) al cargar **{t}**. Yahoo Finance ha bloqueado la IP temporalmente. Prueba en un par de minutos."

    inf, inc, bal, cf = {}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    # 2. Info básica (Solo primitivos para que st.cache_data lo pueda serializar con pickle)
    try: 
        fi = stock.fast_info
        inf["currentPrice"] = float(fi.last_price) if getattr(fi, "last_price", None) else None
        inf["marketCap"] = float(fi.market_cap) if getattr(fi, "market_cap", None) else None
        inf["currency"] = str(fi.currency) if getattr(fi, "currency", None) else "USD"
        inf["sharesOutstanding"] = int(fi.shares) if getattr(fi, "shares", None) else 1
    except: pass
    
    # 3. Info completa (Suele dar error de Rate Limit en la nube)
    try: 
        i_full = stock.info
        if i_full:
            # Filtrar dict para evitar objetos raros
            for k, v in i_full.items():
                if isinstance(v, (int, float, str, bool)):
                    inf[k] = v
    except: pass
    
    # 3b. Respaldo directo a la API oculta de Yahoo si falló `info`
    if "sector" not in inf or "totalDebt" not in inf:
        import requests
        try:
            url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{t}?modules=summaryProfile,financialData"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            res = requests.get(url, headers=headers, timeout=3)
            if res.status_code == 200:
                data = res.json().get("quoteSummary", {}).get("result", [])[0]
                if "summaryProfile" in data:
                    inf["sector"] = data["summaryProfile"].get("sector", inf.get("sector"))
                    inf["industry"] = data["summaryProfile"].get("industry", inf.get("industry"))
                    inf["country"] = data["summaryProfile"].get("country", inf.get("country"))
                if "financialData" in data:
                    fd = data["financialData"]
                    if "totalCash" in fd: inf["totalCash"] = fd.get("totalCash", {}).get("raw", 0)
                    if "totalDebt" in fd: inf["totalDebt"] = fd.get("totalDebt", {}).get("raw", 0)
                    if "debtToEquity" in fd: inf["debtToEquity"] = fd.get("debtToEquity", {}).get("raw", 0)
        except: pass
    
    # 4. Respaldo crítico: Si todo falla, sacamos el precio del histórico
    if not inf.get("currentPrice") and not inf.get("regularMarketPrice"):
        if not h.empty and "Close" in h.columns:
            last_p = float(h["Close"].iloc[-1])
            inf["currentPrice"] = last_p
            inf["regularMarketPrice"] = last_p
            if len(h) >= 2:
                prev_p = float(h["Close"].iloc[-2])
                inf["regularMarketChangePercent"] = ((last_p - prev_p) / prev_p) * 100

    # 5. Financieros (Con try/except individual)
    try: inc = stock.financials
    except: pass
    try: bal = stock.balance_sheet
    except: pass
    try: cf = stock.cashflow
    except: pass
    
    inst, insd = pd.DataFrame(), pd.DataFrame()
    try: inst = stock.institutional_holders
    except: pass
    try: insd = stock.insider_transactions
    except: pass
    
    divs = pd.Series(dtype=float)
    cal = {}
    try: divs = stock.dividends
    except: pass
    try: cal = stock.calendar
    except: pass
    
    # 6. Noticias
    news_list = []
    try:
        raw_news = stock.news
        if raw_news:
            for item in raw_news[:8]:
                # Formato antiguo (plano)
                if "title" in item:
                    news_list.append({
                        "title": str(item.get("title", "")),
                        "publisher": str(item.get("publisher", "Yahoo Finance")),
                        "link": str(item.get("link", "")),
                        "time": int(item.get("providerPublishTime", 0))
                    })
                # Formato nuevo (anidado)
                elif "content" in item:
                    content = item.get("content", {})
                    provider = item.get("provider", {})
                    
                    link_info = item.get("clickThroughUrl") or item.get("canonicalUrl") or {}
                    link = link_info.get("url") or content.get("previewUrl", "#")
                    
                    pub_str = content.get("pubDate", "")
                    pub_time = 0
                    if pub_str:
                        try: pub_time = int(datetime.strptime(pub_str.replace("Z", "UTC"), "%Y-%m-%dT%H:%M:%S%Z").timestamp())
                        except:
                            try: pub_time = int(datetime.strptime(pub_str[:19], "%Y-%m-%dT%H:%M:%S").timestamp())
                            except: pass
                            
                    news_list.append({
                        "title": str(content.get("title", "Sin Título")),
                        "publisher": str(provider.get("displayName", "Yahoo Finance")),
                        "link": str(link),
                        "time": pub_time
                    })
    except: pass
    
    return {"info": inf, "income": inc if inc is not None else pd.DataFrame(), "balance": bal if bal is not None else pd.DataFrame(), "cashflow": cf if cf is not None else pd.DataFrame(), "hist": h, "news": news_list, "inst": inst if inst is not None else pd.DataFrame(), "insd": insd if insd is not None else pd.DataFrame(), "divs": divs, "cal": cal}, None

with st.spinner(f"Cargando datos de **{ticker}**..."):
    try:
        data_cache, err = fetch_data_v4(ticker, chart_period, chart_interval)
        if err:
            st.error(err)
            st.stop()
            
        info = data_cache["info"]
        income = data_cache["income"]
        balance = data_cache["balance"]
        cashflow = data_cache["cashflow"]
        hist = data_cache["hist"]
        news_data = data_cache.get("news", [])
        inst_data = data_cache.get("inst", pd.DataFrame())
        insd_data = data_cache.get("insd", pd.DataFrame())
        divs_data = data_cache.get("divs", pd.Series(dtype=float))
        cal_data = data_cache.get("cal", {})
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

div_rate = info.get("dividendRate") or info.get("trailingAnnualDividendRate", 0)
if div_rate and price and price > 0:
    div_yield = div_rate / price
else:
    div_yield = info.get("dividendYield") or info.get("trailingAnnualDividendYield", 0)

if not div_yield and divs_data is not None and not divs_data.empty and price and price > 0:
    try:
        # Fallback: Sum dividends from the last 365 days
        cutoff = pd.Timestamp.now(tz=divs_data.index.tz) - pd.Timedelta(days=365)
        recent_divs = divs_data[divs_data.index >= cutoff]
        if not recent_divs.empty:
            div_yield = recent_divs.sum() / price
    except: pass

if div_yield is None: div_yield = 0
if div_yield > 1.0: div_yield = div_yield / 100.0
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
    debt_str = ""

earnings_date_str = ""
try:
    e_ts = info.get("nextEarningsDate") or info.get("earningsTimestamp")
    if e_ts:
        earnings_date_str = datetime.fromtimestamp(e_ts).strftime('%d %b %Y')
    elif isinstance(cal_data, dict) and "Earnings Date" in cal_data:
        earnings_date_str = pd.to_datetime(cal_data["Earnings Date"][0]).strftime('%d %b %Y')
except: pass

earnings_badge = f'<span style="background: rgba(128,128,128,0.1); border: 1px solid rgba(128,128,128,0.2); padding: 5px 12px; border-radius: 20px; font-size: 0.85rem;">📅 Resultados: <b>{earnings_date_str}</b></span>' if earnings_date_str else ""

_badges = []
_badges.append(f'<span style="background: rgba(128,128,128,0.1); border: 1px solid rgba(128,128,128,0.2); padding: 5px 12px; border-radius: 20px; font-size: 0.85rem;">💰 Dividendo: <b>{div_str}</b></span>')
if earnings_date_str: _badges.append(earnings_badge)
if debt_str: _badges.append(f'<span style="background: rgba(128,128,128,0.1); border: 1px solid rgba(128,128,128,0.2); padding: 5px 12px; border-radius: 20px; font-size: 0.85rem;">🏦 {debt_str}</span>')
if sector and sector != "N/A": _badges.append(f'<span style="background: rgba(128,128,128,0.1); border: 1px solid rgba(128,128,128,0.2); padding: 5px 12px; border-radius: 20px; font-size: 0.85rem;">🏢 {sector}</span>')
if country and country != "N/A": _badges.append(f'<span style="background: rgba(128,128,128,0.1); border: 1px solid rgba(128,128,128,0.2); padding: 5px 12px; border-radius: 20px; font-size: 0.85rem;">🌍 {country}</span>')
_badges.append(f'<span style="background: rgba(128,128,128,0.1); border: 1px solid rgba(128,128,128,0.2); padding: 5px 12px; border-radius: 20px; font-size: 0.85rem;">📊 Cap: <b>{fmt_big(mkt_cap)}</b></span>')

_badges_html = "".join(_badges)

st.markdown(f"<h1 style='font-weight: 800; font-size: 2.2rem; letter-spacing: -1px; margin-bottom: -15px;'>{name} <span style='font-weight: 300; opacity: 0.4; font-size: 1.5rem;'>{ticker}</span></h1>", unsafe_allow_html=True)
st.markdown(f"""
<div style="margin-bottom: 30px;">
    <span class='big-price'>{sym}{price:,.2f}</span>
    <span class='big-price-sub' style='color: {chg_color};'>{sign}{pct_change:.2f}%</span>
    <div style="margin-top: 15px; display: flex; gap: 10px; flex-wrap: wrap;">
        {_badges_html}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Add to Watchlist star ──
if ticker not in st.session_state.get("watchlist", []):
    st.button("☆", key="add_wl_main", on_click=_add_to_watchlist, args=(ticker,), help="Añadir a Watchlist")
else:
    st.button("★", key="rm_wl_main", on_click=_remove_from_watchlist, args=(ticker,), help="Quitar de Watchlist")

# ── Sidebar Mini-Card ──
st.sidebar.divider()
st.sidebar.markdown(f"""
<div style='background:rgba(128,128,128,0.06); border:1px solid rgba(212,175,55,0.25); border-radius:12px; padding:14px; text-align:center; margin-bottom:5px;'>
    <p style='margin:0; font-size:0.7rem; text-transform:uppercase; letter-spacing:1.5px; opacity:0.5; font-family:Outfit,sans-serif;'>Analizando</p>
    <p style='margin:2px 0 0 0; font-weight:800; font-size:1.1rem;'>{name}</p>
    <p style='margin:0; font-family:JetBrains Mono,monospace; font-size:1.5rem; font-weight:300; color:#d4af37;'>{sym}{price:,.2f}</p>
    <span style='color:{chg_color}; font-size:0.9rem; font-weight:600;'>{sign}{pct_change:.2f}%</span>
</div>
""", unsafe_allow_html=True)

# ── Investment Score Calculation (se muestra dentro del tab del gráfico) ──
_score = 50
_score_details = []

_per_raw = info.get("trailingPE") or info.get("forwardPE", 0)
if _per_raw and _per_raw > 0:
    if _per_raw < 12: _score += 20; _score_details.append("PER bajo (+20)")
    elif _per_raw < 20: _score += 12; _score_details.append("PER razonable (+12)")
    elif _per_raw < 30: _score += 5; _score_details.append("PER algo alto (+5)")
    elif _per_raw < 50: _score -= 5; _score_details.append("PER alto (-5)")
    else: _score -= 15; _score_details.append("PER muy elevado (-15)")

_ni_check = income.iloc[:, 0].get("Net Income", 0) if not income.empty else 0
_rev_check = income.iloc[:, 0].get("Total Revenue", 0) if not income.empty else 0
if _rev_check and _rev_check > 0 and _ni_check:
    _m = _ni_check / _rev_check * 100
    if _m > 20: _score += 15; _score_details.append(f"Margen neto excelente ({_m:.0f}%) (+15)")
    elif _m > 10: _score += 10; _score_details.append(f"Margen neto sano ({_m:.0f}%) (+10)")
    elif _m > 0: _score += 3; _score_details.append(f"Margen neto bajo ({_m:.0f}%) (+3)")
    else: _score -= 10; _score_details.append(f"Margen negativo ({_m:.0f}%) (-10)")

if dte is not None and dte > 0:
    if dte < 30: _score += 15; _score_details.append("Deuda muy baja (+15)")
    elif dte < 80: _score += 8; _score_details.append("Deuda controlada (+8)")
    elif dte < 150: _score -= 3; _score_details.append("Deuda elevada (-3)")
    else: _score -= 10; _score_details.append("Deuda excesiva (-10)")

_fcf_check = cashflow.iloc[:, 0].get("Free Cash Flow", 0) if not cashflow.empty else 0
if _fcf_check and _fcf_check > 0:
    _score += 10; _score_details.append("FCF positivo (+10)")
elif _fcf_check and _fcf_check < 0:
    _score -= 8; _score_details.append("FCF negativo (-8)")

if div_yield and div_yield > 0.01:
    _score += 5; _score_details.append("Paga dividendo (+5)")

_score = max(0, min(100, _score))

if _score >= 75: _score_color = "#00C853"; _score_label = "Excelente"
elif _score >= 55: _score_color = "#d4af37"; _score_label = "Bueno"
elif _score >= 35: _score_color = "#FF9800"; _score_label = "Regular"
else: _score_color = "#FF3D00"; _score_label = "Débil"

# ── Quick PER badge for tab label ──
_per_val = mkt_cap / (income.iloc[:, 0].get("Net Income", 0) or 1) if not income.empty else 0
_per_badge = f" 🟢" if 0 < _per_val < 20 else (f" 🔴" if _per_val > 35 else "")

# ── Tabs ──
tab_chart, tab_compare, tab_ta, tab_fin, tab_statements, tab_val, tab_thesis, tab_backtest, tab_mc, tab_port, tab_news, tab_inst = st.tabs([
    "📊 Gráfico", "🆚 Comparativa", "🕯️ Análisis Técnico", "📈 Tendencias", "🗃️ Fundamentales", f"💰 Valoración{_per_badge}", "📝 Tesis", "🤖 Backtest", "🎲 Monte Carlo", "💼 Mi Cartera", "📰 Noticias", "🏦 Institucional"
])

# ── Tab 2: Comparativa ──
with tab_compare:
    if compare_ticker:
        st.markdown(f"### 🆚 Combate Cara a Cara: {ticker} vs {compare_ticker}")
        with st.spinner(f"Cargando datos de {compare_ticker} para comparativa..."):
            try:
                comp_cache, comp_err = fetch_data_v4(compare_ticker, chart_period, chart_interval)
                if comp_err:
                    st.error(f"Error al cargar {compare_ticker}: {comp_err}")
                else:
                    c_info = comp_cache["info"]
                    c_hist = comp_cache["hist"]
                    
                    c_price = c_info.get("currentPrice") or c_info.get("regularMarketPrice", 0)
                    c_pe = c_info.get("forwardPE") or c_info.get("trailingPE", 0)
                    c_div = c_info.get("dividendYield", 0) * 100 if c_info.get("dividendYield") else 0
                    c_mkt = c_info.get("marketCap", 0)
                    
                    # Gráfico de Retorno Relativo
                    if not hist.empty and not c_hist.empty:
                        # Reindex to match
                        common_idx = hist.index.intersection(c_hist.index)
                        if len(common_idx) > 0:
                            p1 = hist.loc[common_idx, 'Close']
                            p2 = c_hist.loc[common_idx, 'Close']
                            
                            p1_pct = (p1 / p1.iloc[0] - 1) * 100
                            p2_pct = (p2 / p2.iloc[0] - 1) * 100
                            
                            n_comp = len(p1_pct)
                            x_comp_idx = np.arange(n_comp)
                            is_intra_comp = (p1_pct.index[1] - p1_pct.index[0]).total_seconds() < 86400 if n_comp > 1 else False
                            comp_labels = p1_pct.index.strftime('%d %b %H:%M' if is_intra_comp else '%d %b %Y')
                            comp_step = max(1, n_comp // 10)
                            comp_tick_pos = list(range(0, n_comp, comp_step))
                            comp_tick_txt = [comp_labels[i] for i in comp_tick_pos]
                            
                            fig_comp = go.Figure()
                            fig_comp.add_trace(go.Scatter(x=x_comp_idx, y=p1_pct.values, name=ticker, line=dict(color='#d4af37', width=2.5)))
                            fig_comp.add_trace(go.Scatter(x=x_comp_idx, y=p2_pct.values, name=compare_ticker, line=dict(color='#26a69a', width=2.5)))
                            fig_comp.update_layout(
                                height=400, margin=dict(l=0, r=50, t=30, b=0), 
                                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,11,16,1)", 
                                font=dict(family="Inter", size=11, color="rgba(255,255,255,0.55)"), hovermode="x unified",
                                hoverlabel=dict(bgcolor="rgba(30,30,30,0.95)", font_family="JetBrains Mono", bordercolor="rgba(255,255,255,0.15)")
                            )
                            fig_comp.update_xaxes(
                                tickvals=comp_tick_pos, ticktext=comp_tick_txt,
                                showgrid=True, gridcolor="rgba(255,255,255,0.04)",
                                showspikes=True, spikemode="across", spikethickness=1, spikedash="dot", spikecolor="rgba(255,255,255,0.3)"
                            )
                            fig_comp.update_yaxes(
                                ticksuffix="%", showgrid=True, gridcolor="rgba(255,255,255,0.04)", side="right",
                                showspikes=True, spikemode="across", spikethickness=1, spikedash="dot", spikecolor="rgba(255,255,255,0.3)"
                            )
                            st.plotly_chart(fig_comp, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': True})
                    
                    # Tabla Comparativa Frontal
                    comp_metrics = {
                        "Métrica": ["Capitalización", "PER", "Dividendo", "Deuda/Capital"],
                        ticker: [fmt_big(mkt_cap), f"{info.get('trailingPE', 0):.1f}x", div_str, f"{info.get('debtToEquity', 0):.1f}%"],
                        compare_ticker: [fmt_big(c_mkt), f"{c_pe:.1f}x", f"{c_div:.2f}%" if c_div > 0 else "0%", f"{c_info.get('debtToEquity', 0):.1f}%"]
                    }
                    st.table(pd.DataFrame(comp_metrics).set_index("Métrica"))
                    
            except Exception as e:
                st.error(f"Fallo al comparar: {e}")
    else:
        st.info("👈 Introduce un ticker en el campo 'Comparar con...' del panel izquierdo para activar el modo comparativa institucional.")

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

        # ── Eje X numérico con etiquetas de fecha (ultra-rápido, sin saltos) ──
        # Usamos índices enteros (0,1,2,...) como eje X real → Plotly renderiza sin gaps y sin lag.
        # Las etiquetas de fecha se muestran sólo en los ticks seleccionados vía tickvals/ticktext.
        n_bars = len(hist)
        x_idx = np.arange(n_bars)
        
        is_intraday = (hist.index[1] - hist.index[0]).total_seconds() < 86400 if n_bars > 1 else False
        date_fmt = '%d %b %H:%M' if is_intraday else '%d %b %Y'
        all_labels = hist.index.strftime(date_fmt)
        
        # Seleccionar ~12 etiquetas equiespaciadas para el eje
        n_ticks = min(12, n_bars)
        tick_step = max(1, n_bars // n_ticks)
        tick_positions = list(range(0, n_bars, tick_step))
        tick_labels = [all_labels[i] for i in tick_positions]
        
        # Colores TradingView
        tv_up = '#26a69a'    # Verde TradingView
        tv_down = '#ef5350'  # Rojo TradingView
        
        # Color de tendencia principal (para línea)
        overall_trend_color = tv_up if hist['Close'].iloc[-1] >= hist['Close'].iloc[0] else tv_down
        
        if chart_type == "Línea Minimalista":
            fig.add_trace(go.Scatter(
                x=x_idx, y=hist['Close'].values,
                line=dict(color=overall_trend_color, width=2),
                name='Precio', hovertemplate='%{customdata}<br>Precio: %{y:,.2f}<extra></extra>',
                customdata=all_labels
            ), row=1, col=1)
        else:
            fig.add_trace(go.Candlestick(
                x=x_idx,
                open=hist['Open'].values, high=hist['High'].values,
                low=hist['Low'].values, close=hist['Close'].values,
                increasing_line_color=tv_up, decreasing_line_color=tv_down,
                increasing_fillcolor=tv_up, decreasing_fillcolor=tv_down,
                line=dict(width=1),
                name='Precio'
            ), row=1, col=1)
        
        if show_sma:
            fig.add_trace(go.Scatter(x=x_idx, y=hist['SMA_50'].values, line=dict(color='#ff9800', width=1.5, dash='solid'), name='SMA 50', hoverinfo='skip'), row=1, col=1)
            fig.add_trace(go.Scatter(x=x_idx, y=hist['SMA_200'].values, line=dict(color='#42a5f5', width=1.5, dash='solid'), name='SMA 200', hoverinfo='skip'), row=1, col=1)
        
        if show_patterns:
            bull_idx = np.where(hist['bullish_eng'].values)[0]
            if len(bull_idx) > 0:
                bull_prices = hist['Low'].values[bull_idx] * 0.98
                fig.add_trace(go.Scatter(x=bull_idx, y=bull_prices, mode='markers', marker=dict(symbol='triangle-up', size=12, color=tv_up), name='Envolvente Alcista', hoverinfo='name'), row=1, col=1)

            bear_idx = np.where(hist['bearish_eng'].values)[0]
            if len(bear_idx) > 0:
                bear_prices = hist['High'].values[bear_idx] * 1.02
                fig.add_trace(go.Scatter(x=bear_idx, y=bear_prices, mode='markers', marker=dict(symbol='triangle-down', size=12, color=tv_down), name='Envolvente Bajista', hoverinfo='name'), row=1, col=1)

            hammer_idx = np.where(hist['is_hammer'].values)[0]
            if len(hammer_idx) > 0:
                hammer_prices = hist['Low'].values[hammer_idx] * 0.96
                fig.add_trace(go.Scatter(x=hammer_idx, y=hammer_prices, mode='markers', marker=dict(symbol='star', size=10, color='#fdd835'), name='Martillo', hoverinfo='name'), row=1, col=1)
        
        curr_row = 1
        
        if show_vol:
            curr_row += 1
            colors_vol = np.where(hist['Close'].values >= hist['Open'].values, tv_up, tv_down)
            fig.add_trace(go.Bar(x=x_idx, y=hist['Volume'].values, name='Volumen', marker_color=colors_vol, opacity=0.5), row=curr_row, col=1)

        if show_osc:
            curr_row += 1
            fig.add_trace(go.Scatter(x=x_idx, y=hist['RSI'].values, name='RSI', line=dict(color='#ab47bc', width=1.5)), row=curr_row, col=1)
            fig.add_hline(y=70, line_dash="dot", row=curr_row, col=1, line_color=tv_down, opacity=0.4)
            fig.add_hline(y=30, line_dash="dot", row=curr_row, col=1, line_color=tv_up, opacity=0.4)
            
            colors_macd = np.where(hist['MACD_Hist'].values >= 0, tv_up, tv_down)
            fig.add_trace(go.Bar(x=x_idx, y=hist['MACD_Hist'].values, name='MACD Hist', marker_color=colors_macd, opacity=0.5), row=curr_row, col=1)
            fig.add_trace(go.Scatter(x=x_idx, y=hist['MACD'].values, line=dict(color='#42a5f5', width=1.5), name='MACD'), row=curr_row, col=1)
            fig.add_trace(go.Scatter(x=x_idx, y=hist['Signal'].values, line=dict(color='#ff9800', width=1.5), name='Signal'), row=curr_row, col=1)

        fig.update_layout(
            height=450 + (130 if show_vol else 0) + (200 if show_osc else 0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,11,16,1)",
            margin=dict(l=0, r=50, t=8, b=0),
            font=dict(family="Inter", size=11, color="rgba(255,255,255,0.55)"),
            dragmode='pan',
            showlegend=False,
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor="rgba(30,30,30,0.95)",
                font_size=12,
                font_family="JetBrains Mono",
                bordercolor="rgba(255,255,255,0.15)"
            )
        )
        
        # Ejes configurados para velocidad y estética TradingView
        fig.update_xaxes(
            tickvals=tick_positions, ticktext=tick_labels,
            showgrid=True, gridcolor="rgba(255,255,255,0.04)",
            zeroline=False,
            showspikes=True, spikemode="across", spikethickness=1, spikedash="dot", spikecolor="rgba(255,255,255,0.3)",
            rangeslider_visible=False
        )
        fig.update_yaxes(
            showgrid=True, gridcolor="rgba(255,255,255,0.04)",
            zeroline=False, side="right",
            showspikes=True, spikemode="across", spikethickness=1, spikedash="dot", spikecolor="rgba(255,255,255,0.3)"
        )
        
        st.plotly_chart(fig, use_container_width=True, config={
            'scrollZoom': True, 
            'displayModeBar': True,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'autoScale2d'],
            'displaylogo': False
        })

    # ── Investment Score (Gauge) inside Chart tab ──
    st.divider()
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=_score,
        title={'text': f"Score de Inversión: {_score_label}", 'font': {'size': 14, 'family': 'Outfit'}},
        number={'font': {'size': 40, 'family': 'JetBrains Mono', 'color': _score_color}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': 'rgba(128,128,128,0.3)'},
            'bar': {'color': _score_color, 'thickness': 0.3},
            'bgcolor': 'rgba(0,0,0,0)',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 35], 'color': 'rgba(255,61,0,0.08)'},
                {'range': [35, 55], 'color': 'rgba(255,152,0,0.08)'},
                {'range': [55, 75], 'color': 'rgba(212,175,55,0.08)'},
                {'range': [75, 100], 'color': 'rgba(0,200,83,0.08)'},
            ],
            'threshold': {'line': {'color': _score_color, 'width': 3}, 'thickness': 0.8, 'value': _score}
        }
    ))
    fig_gauge.update_layout(height=200, margin=dict(l=30, r=30, t=50, b=10), paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"))

    gauge_col1, gauge_col2 = st.columns([1, 1.2])
    with gauge_col1:
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
    with gauge_col2:
        st.markdown("<p style='font-size:0.75rem; text-transform:uppercase; letter-spacing:1px; opacity:0.5; margin-bottom:5px; font-family:Outfit,sans-serif;'>Desglose del Score</p>", unsafe_allow_html=True)
        for _sd in _score_details:
            _sd_col = "#00C853" if "+" in _sd.split("(")[-1] else "#FF3D00"
            st.markdown(f"<span style='font-size:0.8rem; color:{_sd_col};'>{'\u25b2' if '+' in _sd.split('(')[-1] else '\u25bc'} {_sd}</span>", unsafe_allow_html=True)


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
                    
                    st.markdown("#### 🗺️ Mapa de Calor Institucional (Open Interest)")
                    st.markdown("<p style='font-size:0.8rem; opacity:0.7; margin-top:-10px;'>¿Dónde están posicionadas las grandes carteras institucionales? Muestra las apuestas vivas por precio (Strike).</p>", unsafe_allow_html=True)
                    
                    try:
                        calls_df = chain.calls[['strike', 'openInterest']].copy()
                        calls_df['Tipo'] = 'CALLS (Alcista)'
                        puts_df = chain.puts[['strike', 'openInterest']].copy()
                        puts_df['Tipo'] = 'PUTS (Bajista)'
                        
                        curr_p = hist['Close'].iloc[-1] if not hist.empty else 0
                        opts_df = pd.concat([calls_df, puts_df]).dropna()
                        
                        if curr_p > 0 and not opts_df.empty:
                            # Filtrar solo strikes relevantes (+/- 25% del precio actual)
                            opts_df = opts_df[(opts_df['strike'] >= curr_p * 0.75) & (opts_df['strike'] <= curr_p * 1.25)]
                            
                        if not opts_df.empty:
                            pivot_opts = opts_df.pivot(index='Tipo', columns='strike', values='openInterest').fillna(0)
                            
                            fig_hm = go.Figure(data=go.Heatmap(
                                z=pivot_opts.values,
                                x=pivot_opts.columns,
                                y=pivot_opts.index,
                                colorscale='Aggrnyl',  # Estilo financiero/terminal
                                hovertemplate='Strike: %{x}<br>Tipo: %{y}<br>Contratos Abiertos: %{z}<extra></extra>'
                            ))
                            fig_hm.update_layout(
                                height=200, margin=dict(l=0, r=0, t=20, b=0),
                                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                font=dict(family="Inter")
                            )
                            fig_hm.add_vline(x=curr_p, line_dash="dash", line_color="white", annotation_text="Precio Actual", annotation_font=dict(color="white"))
                            st.plotly_chart(fig_hm, use_container_width=True, config={'displayModeBar': False})
                    except Exception as e:
                        st.info("No se pudo generar el heatmap de opciones para esta fecha.")
                        
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

    # Dividend History
    if not divs_data.empty:
        st.divider()
        st.markdown("#### 💸 Historial de Dividendos Pagados")
        if isinstance(divs_data.index, pd.DatetimeIndex):
            divs_yearly = divs_data.groupby(divs_data.index.year).sum()
            divs_yearly = divs_yearly.tail(10)
            
            fig_divs = go.Figure(data=go.Bar(
                x=divs_yearly.index, 
                y=divs_yearly.values, 
                marker_color='#00C853',
                text=[f"${v:.2f}" for v in divs_yearly.values],
                textposition='auto',
                textfont=dict(color='white', family='JetBrains Mono')
            ))
            fig_divs.update_layout(
                height=250, 
                margin=dict(l=0, r=0, t=20, b=0), 
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                font=dict(family="Inter"),
                xaxis=dict(type='category')
            )
            fig_divs.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.1)")
            st.plotly_chart(fig_divs, use_container_width=True, config={'displayModeBar': False})


# ── Tab 4: Fundamentales (Estados Financieros) ──
with tab_statements:
    st.markdown("### 🗃️ Análisis Fundamental Profundo")
    st.markdown("<p style='font-size:0.9rem; opacity:0.7; margin-top:-10px;'>Radiografía contable completa: KPIs, visualizaciones y estados financieros íntegros.</p>", unsafe_allow_html=True)

    # ── Helper: safe extraction with YoY delta ──
    def _safe_get(df, key, col_idx=0):
        if df.empty or key not in df.index: return 0
        v = df.iloc[:, col_idx].get(key, 0)
        return v if pd.notna(v) else 0

    def _yoy(df, key):
        cur = _safe_get(df, key, 0)
        prev = _safe_get(df, key, 1) if len(df.columns) > 1 else 0
        if prev and prev != 0:
            return ((cur - prev) / abs(prev)) * 100
        return None

    # ── Extraer KPIs ──
    f_rev = _safe_get(income, "Total Revenue")
    f_gp = _safe_get(income, "Gross Profit")
    f_ebitda = _safe_get(income, "EBITDA")
    f_ebit = _safe_get(income, "EBIT")
    f_ni = _safe_get(income, "Net Income")
    f_fcf = _safe_get(cashflow, "Free Cash Flow")
    f_opex = _safe_get(income, "Operating Expense")
    f_tax = _safe_get(income, "Tax Provision")
    f_interest = _safe_get(income, "Interest Expense")

    f_total_assets = _safe_get(balance, "Total Assets")
    f_total_liab = _safe_get(balance, "Total Liabilities Net Minority Interest")
    f_equity = 0
    for _ek in ["Stockholders Equity", "Total Stockholder Equity", "Common Stock Equity"]:
        f_equity = _safe_get(balance, _ek)
        if f_equity: break
    f_debt = 0
    for _dk in ["Total Debt", "Long Term Debt"]:
        f_debt = _safe_get(balance, _dk)
        if f_debt: break
    f_cash = 0
    for _ck in ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"]:
        f_cash = _safe_get(balance, _ck)
        if f_cash: break

    f_margin_gross = (f_gp / f_rev * 100) if f_rev else 0
    f_margin_net = (f_ni / f_rev * 100) if f_rev else 0
    f_margin_ebitda = (f_ebitda / f_rev * 100) if f_rev else 0
    f_roe = (f_ni / f_equity * 100) if f_equity else 0
    f_roa = (f_ni / f_total_assets * 100) if f_total_assets else 0

    # ── Función para KPI Card HTML ──
    def _kpi_card(label, value_str, delta_pct=None, icon="📊", accent="#d4af37"):
        delta_html = ""
        if delta_pct is not None:
            d_col = color_up if delta_pct >= 0 else color_down
            d_sign = "+" if delta_pct >= 0 else ""
            delta_html = f"<span style='font-size:0.8rem; color:{d_col}; font-weight:600;'>{d_sign}{delta_pct:.1f}% YoY</span>"
        return f"""
        <div style='background:rgba(128,128,128,0.05); border:1px solid rgba(128,128,128,0.15); border-radius:12px; padding:18px 16px; text-align:center; transition:all 0.3s ease;' class='glow-hover'>
            <p style='margin:0 0 4px 0; font-size:0.7rem; text-transform:uppercase; letter-spacing:1.5px; opacity:0.5; font-family:Outfit,sans-serif;'>{icon} {label}</p>
            <p style='margin:0; font-family:JetBrains Mono,monospace; font-size:1.6rem; font-weight:300; color:{accent};'>{value_str}</p>
            {delta_html}
        </div>"""

    # ── Fila 1: Métricas de Rentabilidad ──
    st.markdown("<h4 style='margin-bottom:10px;'>💰 Rentabilidad</h4>", unsafe_allow_html=True)
    kc1, kc2, kc3, kc4, kc5 = st.columns(5)
    kc1.markdown(_kpi_card("Ingresos", fmt_big(f_rev), _yoy(income, "Total Revenue"), "💵", "#d4af37"), unsafe_allow_html=True)
    kc2.markdown(_kpi_card("Beneficio Bruto", fmt_big(f_gp), _yoy(income, "Gross Profit"), "📦", "#00C853"), unsafe_allow_html=True)
    kc3.markdown(_kpi_card("EBITDA", fmt_big(f_ebitda), _yoy(income, "EBITDA"), "⚡", "#FF9800"), unsafe_allow_html=True)
    kc4.markdown(_kpi_card("EBIT", fmt_big(f_ebit), _yoy(income, "EBIT"), "🔧"), unsafe_allow_html=True)
    kc5.markdown(_kpi_card("Beneficio Neto", fmt_big(f_ni), _yoy(income, "Net Income"), "🏆", "#00C853" if f_ni > 0 else "#FF3D00"), unsafe_allow_html=True)

    st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

    # ── Fila 2: Márgenes y Eficiencia ──
    st.markdown("<h4 style='margin-bottom:10px;'>📐 Márgenes y Eficiencia</h4>", unsafe_allow_html=True)
    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    mc1.markdown(_kpi_card("Margen Bruto", f"{f_margin_gross:.1f}%", None, "📊", "#00C853" if f_margin_gross > 40 else "#FF9800"), unsafe_allow_html=True)
    mc2.markdown(_kpi_card("Margen EBITDA", f"{f_margin_ebitda:.1f}%", None, "📊", "#00C853" if f_margin_ebitda > 25 else "#FF9800"), unsafe_allow_html=True)
    mc3.markdown(_kpi_card("Margen Neto", f"{f_margin_net:.1f}%", None, "📊", "#00C853" if f_margin_net > 15 else ("#FF3D00" if f_margin_net < 0 else "#FF9800")), unsafe_allow_html=True)
    mc4.markdown(_kpi_card("ROE", f"{f_roe:.1f}%", None, "🎯", "#00C853" if f_roe > 15 else "#FF9800"), unsafe_allow_html=True)
    mc5.markdown(_kpi_card("ROA", f"{f_roa:.1f}%", None, "🎯"), unsafe_allow_html=True)

    st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

    # ── Fila 3: Balance / Solvencia ──
    st.markdown("<h4 style='margin-bottom:10px;'>🏦 Solidez Financiera</h4>", unsafe_allow_html=True)
    bc1, bc2, bc3, bc4, bc5 = st.columns(5)
    bc1.markdown(_kpi_card("Activos Totales", fmt_big(f_total_assets), None, "🏗️"), unsafe_allow_html=True)
    bc2.markdown(_kpi_card("Pasivos Totales", fmt_big(f_total_liab), None, "⚠️", "#FF9800"), unsafe_allow_html=True)
    bc3.markdown(_kpi_card("Patrimonio Neto", fmt_big(f_equity), None, "🛡️", "#00C853" if f_equity > 0 else "#FF3D00"), unsafe_allow_html=True)
    bc4.markdown(_kpi_card("Deuda Total", fmt_big(f_debt), None, "🔗", "#FF3D00" if f_debt > f_equity else "#FF9800"), unsafe_allow_html=True)
    bc5.markdown(_kpi_card("Caja / FCF", f"{fmt_big(f_cash)} / {fmt_big(f_fcf)}", _yoy(cashflow, "Free Cash Flow"), "💎", "#00C853"), unsafe_allow_html=True)

    st.divider()

    # ── Gráfico 1: Waterfall P&L (Cascada de Rentabilidad) ──
    st.markdown("<h4>📊 Cascada de Rentabilidad (Último Año)</h4>", unsafe_allow_html=True)
    wf_labels = ["Ingresos", "Coste de Ventas", "Beneficio Bruto", "Gastos Operativos", "EBIT", "Intereses", "Impuestos", "Beneficio Neto"]
    cogs = f_rev - f_gp if f_rev and f_gp else 0
    opex_net = f_gp - f_ebit if f_gp and f_ebit else 0
    wf_values = [f_rev, -abs(cogs), f_gp, -abs(opex_net), f_ebit, -abs(f_interest) if f_interest else 0, -abs(f_tax) if f_tax else 0, f_ni]
    wf_measures = ["absolute", "relative", "total", "relative", "total", "relative", "relative", "total"]
    wf_colors = {"increasing": {"marker": {"color": "#00C853"}}, "decreasing": {"marker": {"color": "#FF3D00"}}, "totals": {"marker": {"color": "#d4af37"}}}

    fig_wf = go.Figure(go.Waterfall(
        x=wf_labels, y=wf_values, measure=wf_measures,
        textposition="outside", text=[fmt_big(v) for v in wf_values],
        connector=dict(line=dict(color="rgba(128,128,128,0.3)", width=1)),
        **wf_colors
    ))
    fig_wf.update_layout(height=350, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", size=11), showlegend=False)
    fig_wf.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.1)")
    st.plotly_chart(fig_wf, use_container_width=True, config={'displayModeBar': False})

    # ── Gráfico 2: Evolución multi-anual (Ingresos, EBITDA, Beneficio Neto, FCF) ──
    if not income.empty:
        st.markdown("<h4>📈 Evolución Financiera Multi-Anual</h4>", unsafe_allow_html=True)
        _years = income.columns.tolist()
        _ylabels = [str(d.year) if hasattr(d, 'year') else str(d) for d in _years][::-1]

        def _sr(df, key):
            if df.empty or key not in df.index: return [0]*len(df.columns)
            return [df.loc[key, c] if pd.notna(df.loc[key, c]) else 0 for c in df.columns][::-1]

        fig_evo = go.Figure()
        fig_evo.add_trace(go.Bar(x=_ylabels, y=_sr(income, "Total Revenue"), name="Ingresos", marker_color="rgba(128,128,128,0.25)"))
        fig_evo.add_trace(go.Bar(x=_ylabels, y=_sr(income, "EBITDA"), name="EBITDA", marker_color="rgba(255,152,0,0.5)"))
        fig_evo.add_trace(go.Scatter(x=_ylabels, y=_sr(income, "Net Income"), name="Beneficio Neto", mode="lines+markers", line=dict(color="#00C853", width=3), marker=dict(size=8)))
        fig_evo.add_trace(go.Scatter(x=_ylabels, y=_sr(cashflow, "Free Cash Flow"), name="Free Cash Flow", mode="lines+markers", line=dict(color="#d4af37", width=3, dash="dot"), marker=dict(size=8, symbol="diamond")))
        fig_evo.update_layout(barmode="group", height=350, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig_evo.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.1)")
        st.plotly_chart(fig_evo, use_container_width=True, config={'displayModeBar': False})

    # ── Gráfico 3: Composición del Balance (Stacked) ──
    if not balance.empty:
        st.markdown("<h4>⚖️ Composición del Balance</h4>", unsafe_allow_html=True)
        _bylabels = [str(d.year) if hasattr(d, 'year') else str(d) for d in balance.columns.tolist()][::-1]

        def _sb(key):
            if key not in balance.index: return [0]*len(balance.columns)
            return [balance.loc[key, c] if pd.notna(balance.loc[key, c]) else 0 for c in balance.columns][::-1]

        fig_bal = make_subplots(rows=1, cols=2, subplot_titles=["Activos", "Pasivos + Patrimonio"], shared_yaxes=True)

        # Activos
        _current_a = _sb("Current Assets")
        _noncurrent_a = [a - ca for a, ca in zip(_sb("Total Assets"), _current_a)]
        fig_bal.add_trace(go.Bar(x=_bylabels, y=_current_a, name="Activo Corriente", marker_color="rgba(0,200,83,0.5)"), row=1, col=1)
        fig_bal.add_trace(go.Bar(x=_bylabels, y=_noncurrent_a, name="Activo No Corriente", marker_color="rgba(0,200,83,0.2)"), row=1, col=1)

        # Pasivos + Equity
        _current_l = _sb("Current Liabilities")
        _noncurrent_l = [t - cl for t, cl in zip(_sb("Total Liabilities Net Minority Interest"), _current_l)]
        _eq_vals = _sb("Stockholders Equity") if "Stockholders Equity" in balance.index else _sb("Common Stock Equity")
        fig_bal.add_trace(go.Bar(x=_bylabels, y=_current_l, name="Pasivo Corriente", marker_color="rgba(255,61,0,0.5)"), row=1, col=2)
        fig_bal.add_trace(go.Bar(x=_bylabels, y=_noncurrent_l, name="Pasivo No Corriente", marker_color="rgba(255,61,0,0.2)"), row=1, col=2)
        fig_bal.add_trace(go.Bar(x=_bylabels, y=_eq_vals, name="Patrimonio Neto", marker_color="rgba(212,175,55,0.5)"), row=1, col=2)

        fig_bal.update_layout(barmode="stack", height=350, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"), legend=dict(orientation="h", yanchor="bottom", y=1.06, xanchor="right", x=1))
        fig_bal.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.1)")
        st.plotly_chart(fig_bal, use_container_width=True, config={'displayModeBar': False})

    st.divider()

    # ── Estados Financieros Completos (Visual) ──
    st.markdown("<h4>📋 Estados Financieros Completos</h4>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.8rem; opacity:0.5;'>Desglose visual de cada estado financiero con evolución interanual.</p>", unsafe_allow_html=True)

    def _format_df_raw(df):
        if df.empty: return pd.DataFrame()
        d = df.copy()
        try: d.columns = [c.strftime('%Y') if hasattr(c, 'strftime') else str(c) for c in d.columns]
        except: pass
        d = d.fillna(0)
        return d

    def _build_visual_statement(df, title, key_rows, chart_color_map):
        """Build a visual financial statement with horizontal bar chart + styled HTML table."""
        if df.empty:
            st.info(f"{title}: datos no disponibles.")
            return

        cols_raw = df.columns.tolist()
        col_labels = [c.strftime('%Y') if hasattr(c, 'strftime') else str(c) for c in cols_raw]

        # ── Chart: key line items across years ──
        fig_stmt = go.Figure()
        for row_key, display_name in key_rows:
            if row_key in df.index:
                vals = [df.loc[row_key, c] if pd.notna(df.loc[row_key, c]) else 0 for c in cols_raw][::-1]
                color = chart_color_map.get(row_key, "rgba(128,128,128,0.4)")
                fig_stmt.add_trace(go.Bar(x=col_labels[::-1], y=vals, name=display_name, marker_color=color))

        fig_stmt.update_layout(
            barmode="group", height=300, margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", size=11),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_stmt.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.1)")
        st.plotly_chart(fig_stmt, use_container_width=True, config={'displayModeBar': False})

        # ── Styled HTML Table ──
        available_rows = [r for r in df.index if any(pd.notna(df.loc[r, c]) and df.loc[r, c] != 0 for c in cols_raw)]

        # Find max absolute value for bar scaling
        all_vals = []
        for r in available_rows:
            for c in cols_raw:
                v = df.loc[r, c]
                if pd.notna(v): all_vals.append(abs(v))
        max_val = max(all_vals) if all_vals else 1

        header_html = "".join([f"<th style='padding:8px 12px; text-align:right; font-family:Outfit,sans-serif; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px; opacity:0.6; border-bottom:2px solid rgba(212,175,55,0.3);'>{lbl}</th>" for lbl in col_labels])
        header_html += "<th style='padding:8px 12px; text-align:right; font-family:Outfit,sans-serif; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px; opacity:0.6; border-bottom:2px solid rgba(212,175,55,0.3);'>YoY</th>"

        rows_html = ""
        for row_name in available_rows:
            # Label styling: bold for key rows
            is_key = any(row_name == kr for kr, _ in key_rows)
            label_style = "font-weight:700; color:#d4af37;" if is_key else "font-weight:400; opacity:0.85;"

            cells = ""
            vals_for_row = []
            for c in cols_raw:
                v = df.loc[row_name, c]
                v = v if pd.notna(v) else 0
                vals_for_row.append(v)
                v_color = "#FF3D00" if v < 0 else "inherit"
                bar_width = min(abs(v) / max_val * 100, 100) if max_val else 0
                bar_col = "rgba(0,200,83,0.15)" if v >= 0 else "rgba(255,61,0,0.15)"
                cells += f"""<td style='padding:6px 12px; text-align:right; font-family:JetBrains Mono,monospace; font-size:0.8rem; color:{v_color}; position:relative;'>
                    <div style='position:absolute; left:0; top:0; bottom:0; width:{bar_width}%; background:{bar_col}; border-radius:4px;'></div>
                    <span style='position:relative;'>{fmt_big(v)}</span>
                </td>"""

            # YoY calculation
            yoy_html = ""
            if len(vals_for_row) >= 2 and vals_for_row[1] and vals_for_row[1] != 0:
                yoy_pct = ((vals_for_row[0] - vals_for_row[1]) / abs(vals_for_row[1])) * 100
                yoy_col = color_up if yoy_pct >= 0 else color_down
                yoy_sign = "+" if yoy_pct >= 0 else ""
                yoy_html = f"<td style='padding:6px 12px; text-align:right; font-family:JetBrains Mono,monospace; font-size:0.8rem; color:{yoy_col}; font-weight:600;'>{yoy_sign}{yoy_pct:.1f}%</td>"
            else:
                yoy_html = "<td style='padding:6px 12px; text-align:right; opacity:0.3; font-size:0.8rem;'>—</td>"

            rows_html += f"""<tr style='border-bottom:1px solid rgba(128,128,128,0.08); transition:background 0.2s;' onmouseover="this.style.background='rgba(212,175,55,0.05)'" onmouseout="this.style.background='transparent'">
                <td style='padding:6px 12px; font-size:0.8rem; {label_style} white-space:nowrap;'>{row_name}</td>
                {cells}{yoy_html}
            </tr>"""

        table_html = f"""
        <div style='overflow-x:auto; border:1px solid rgba(128,128,128,0.12); border-radius:12px; margin-top:10px;'>
            <table style='width:100%; border-collapse:collapse;'>
                <thead><tr>
                    <th style='padding:8px 12px; text-align:left; font-family:Outfit,sans-serif; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px; opacity:0.6; border-bottom:2px solid rgba(212,175,55,0.3);'>Partida</th>
                    {header_html}
                </tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>"""
        st.markdown(table_html, unsafe_allow_html=True)

        # Raw data fallback
        with st.expander("📄 Ver datos en bruto (DataFrame)", expanded=False):
            st.dataframe(_format_df_raw(df), use_container_width=True, height=400)

    # ── 1. Cuenta de Resultados ──
    with st.expander("🧾 Cuenta de Resultados (Income Statement)", expanded=True):
        _build_visual_statement(income, "Cuenta de Resultados", [
            ("Total Revenue", "Ingresos"),
            ("Gross Profit", "Beneficio Bruto"),
            ("EBITDA", "EBITDA"),
            ("EBIT", "EBIT"),
            ("Net Income", "Beneficio Neto"),
        ], {
            "Total Revenue": "rgba(128,128,128,0.3)",
            "Gross Profit": "rgba(0,200,83,0.5)",
            "EBITDA": "rgba(255,152,0,0.5)",
            "EBIT": "rgba(212,175,55,0.5)",
            "Net Income": "rgba(0,200,83,0.8)",
        })

    # ── 2. Balance General ──
    with st.expander("⚖️ Balance General (Balance Sheet)", expanded=False):
        _build_visual_statement(balance, "Balance General", [
            ("Total Assets", "Activos Totales"),
            ("Total Liabilities Net Minority Interest", "Pasivos Totales"),
            ("Stockholders Equity", "Patrimonio Neto"),
            ("Total Debt", "Deuda Total"),
            ("Cash And Cash Equivalents", "Efectivo"),
        ], {
            "Total Assets": "rgba(0,200,83,0.4)",
            "Total Liabilities Net Minority Interest": "rgba(255,61,0,0.4)",
            "Stockholders Equity": "rgba(212,175,55,0.5)",
            "Total Debt": "rgba(255,152,0,0.5)",
            "Cash And Cash Equivalents": "rgba(0,200,83,0.7)",
        })

    # ── 3. Flujo de Caja ──
    with st.expander("💵 Flujo de Caja (Cash Flow Statement)", expanded=False):
        _build_visual_statement(cashflow, "Flujo de Caja", [
            ("Operating Cash Flow", "Flujo Operativo"),
            ("Capital Expenditure", "CapEx"),
            ("Free Cash Flow", "Free Cash Flow"),
            ("Repurchase Of Capital Stock", "Recompra de Acciones"),
            ("Cash Dividends Paid", "Dividendos Pagados"),
        ], {
            "Operating Cash Flow": "rgba(0,200,83,0.5)",
            "Capital Expenditure": "rgba(255,61,0,0.4)",
            "Free Cash Flow": "rgba(212,175,55,0.6)",
            "Repurchase Of Capital Stock": "rgba(255,152,0,0.5)",
            "Cash Dividends Paid": "rgba(128,128,128,0.4)",
        })

# ── Tab 5: Centro de Valoración ──
with tab_val:
    st.markdown("### 🏛️ Modelos de Valoración (Fair Value)")
    
    val_method = st.radio("Selecciona Modelo Matemático", 
                          ["Descuento de Flujos (DCF)", "Fórmula de Graham", "Earning Power Value (EPV)", "Modelo de Dividendos (DDM)", "Múltiplos (Comparativa)"], 
                          horizontal=True, label_visibility="collapsed")
    st.divider()

    # Pre-calculate common variables
    net_income = income.iloc[:, 0].get("Net Income", 0) if not income.empty else 0
    ebit = income.iloc[:, 0].get("EBIT", 0) if not income.empty else 0
    ebitda = income.iloc[:, 0].get("EBITDA", 0) if not income.empty else 0
    revenue = income.iloc[:, 0].get("Total Revenue", 0) if not income.empty else 0
    
    risk_free = get_risk_free_rate_v2()
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
    calc_wacc = max(calc_wacc, 0.08) # Tope conservador: El dinero nunca es "gratis", WACC mínimo del 8%
    
    cash = 0
    if not balance.empty:
        for key in ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"]:
            if key in balance.index:
                v = balance.iloc[:, 0].get(key, 0)
                cash = v if pd.notna(v) else 0
                break
    net_debt = total_debt - cash

    if val_method == "Descuento de Flujos (DCF)":
        fcfs_pos = [f for f in fcf_row if f and f > 0]
        last_fcf = fcfs_pos[0] if fcfs_pos else 0
        if len(fcfs_pos) >= 2:
            calc_growth = max(0.02, min((fcfs_pos[0] / fcfs_pos[-1]) ** (1 / (len(fcfs_pos) - 1)) - 1, 0.15)) # Tope estricto del 15% al crecimiento
        else:
            calc_growth = 0.08

        calc_terminal_g = 0.02 # Crecimiento terminal conservador alineado a la inflación global

        col_w, col_g, col_tg = st.columns(3)
        user_wacc = col_w.slider("WACC (%)", min_value=5.0, max_value=25.0, value=float(calc_wacc*100), step=0.1, help="Coste Promedio Ponderado de Capital.") / 100.0
        user_growth = col_g.slider("Crecimiento Corto Plazo (%)", min_value=-15.0, max_value=30.0, value=float(calc_growth*100), step=0.5) / 100.0
        user_term_g = col_tg.slider("Crecimiento Terminal (%)", min_value=0.0, max_value=4.0, value=float(calc_terminal_g*100), step=0.1) / 100.0

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

        equity_value = ev_dcf - net_debt
        dcf_price = equity_value / shares_out if shares_out else 0

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Enterprise Value", fmt_big(ev_dcf), help="Valor teórico total de la empresa.")
        c2.metric("Deuda Neta", fmt_big(net_debt), help="Deuda total menos caja.")
        c3.metric("Equity Value", fmt_big(equity_value), help="Valor para los accionistas.")
        c4.metric("Valor Justo (DCF)", f"{sym}{dcf_price:,.2f}", help="Precio intrínseco por acción.")
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = float(price),
            delta = {'reference': dcf_price, 'position': "top", 'increasing': {'color': "rgba(255, 61, 0, 0.8)"}, 'decreasing': {'color': "rgba(0, 200, 83, 0.8)"}},
            title = {'text': f"Cotización vs Valor Justo (DCF: {sym}{dcf_price:,.2f})", 'font': {'size': 16, 'color': '#d4af37'}},
            gauge = {
                'axis': {'range': [None, max(float(price), dcf_price)*1.5], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "#d4af37"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 1,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, dcf_price*0.9], 'color': 'rgba(0, 200, 83, 0.15)'},
                    {'range': [dcf_price*0.9, dcf_price*1.1], 'color': 'rgba(128, 128, 128, 0.1)'},
                    {'range': [dcf_price*1.1, max(float(price), dcf_price)*1.5], 'color': 'rgba(255, 61, 0, 0.15)'}],
                'threshold': {
                    'line': {'color': "white", 'width': 3},
                    'thickness': 0.75,
                    'value': dcf_price}}))
        fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"))
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
        
        st.divider()
        st.markdown("#### Matriz de Sensibilidad DCF")
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
            
        df_matrix = pd.DataFrame(matrix_data, index=[f"WACC {w*100:.1f}%" for w in wacc_vars], columns=[f"Term G. {tg*100:.1f}%" for tg in tg_vars])
        custom_colors = [[0, "rgba(255, 61, 0, 0.8)"], [0.5, "rgba(128, 128, 128, 0.2)"], [1, "rgba(0, 200, 83, 0.8)"]]
        fig_matrix = px.imshow(df_matrix, text_auto=".2f", color_continuous_scale=custom_colors, aspect="auto")
        fig_matrix.update_layout(height=220, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="JetBrains Mono"))
        fig_matrix.update_xaxes(side="top")
        st.plotly_chart(fig_matrix, use_container_width=True, config={'displayModeBar': False})

    elif val_method == "Fórmula de Graham":
        eps = net_income / shares_out if shares_out and net_income else 0
        if eps > 0:
            st.markdown("<p style='font-size:0.9rem; opacity:0.7; margin-bottom: 20px;'>Fórmula modernizada y ultra-conservadora de Benjamin Graham: <b>V = (EPS × (8.5 + 1g) × 4.4) / Y</b></p>", unsafe_allow_html=True)
            col_g_eps, col_g_g, col_g_y = st.columns(3)
            
            # Estimate historical growth for Graham
            fcfs_pos = [f for f in fcf_row if f and f > 0]
            if len(fcfs_pos) >= 2:
                calc_g_graham = max(0.02, min((fcfs_pos[0] / fcfs_pos[-1]) ** (1 / (len(fcfs_pos) - 1)) - 1, 0.15)) # Tope 15%
            else:
                calc_g_graham = 0.05
                
            g_g = col_g_g.slider("Crecimiento a 5 años (g) [%]", 0.0, 30.0, float(calc_g_graham*100))
            g_y = col_g_y.slider("Rendimiento Bono Corporativo AAA (Y) [%]", 1.0, 10.0, float(risk_free*100 + 1.0))
            
            graham_val = (eps * (8.5 + 1.0 * (g_g)) * 4.4) / g_y
            upside_g = (graham_val - price) / price if price else 0
            
            c_g1, c_g2 = st.columns(2)
            c_g1.metric("Valor Intrínseco de Graham", f"{sym}{graham_val:,.2f}")
            c_g2.metric("Potencial / Margen Seguridad", f"{upside_g*100:.1f}%")
            
            fig_g_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = float(price),
                delta = {'reference': graham_val, 'position': "top", 'increasing': {'color': "rgba(255, 61, 0, 0.8)"}, 'decreasing': {'color': "rgba(0, 200, 83, 0.8)"}},
                title = {'text': f"Cotización vs Valor Graham ({sym}{graham_val:,.2f})", 'font': {'size': 16, 'color': '#d4af37'}},
                gauge = {
                    'axis': {'range': [None, max(float(price), graham_val)*1.5], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': "#d4af37"},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 1,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, graham_val*0.9], 'color': 'rgba(0, 200, 83, 0.15)'},
                        {'range': [graham_val*0.9, graham_val*1.1], 'color': 'rgba(128, 128, 128, 0.1)'},
                        {'range': [graham_val*1.1, max(float(price), graham_val)*1.5], 'color': 'rgba(255, 61, 0, 0.15)'}],
                    'threshold': {
                        'line': {'color': "white", 'width': 3},
                        'thickness': 0.75,
                        'value': graham_val}}))
            fig_g_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"))
            st.plotly_chart(fig_g_gauge, use_container_width=True, config={'displayModeBar': False})
            
            # Defensive Graham Number
            bvps = total_equity_bs / shares_out if shares_out else 0
            if bvps > 0:
                graham_num = np.sqrt(22.5 * eps * bvps)
                st.divider()
                st.info(f"💡 **Número de Graham (Defensivo): {sym}{graham_num:,.2f}**. Es el precio máximo absoluto que pagaría un inversor ultraconservador para asegurar el valor de los activos físicos de la empresa.")
        else:
            st.warning("La empresa no tiene beneficios netos positivos (EPS < 0). La fórmula de Graham exige que la empresa sea rentable.")

    elif val_method == "Earning Power Value (EPV)":
        if ebit > 0:
            st.markdown("<p style='font-size:0.9rem; opacity:0.7; margin-bottom: 20px;'>Desarrollado por Bruce Greenwald, valora la empresa basándose estrictamente en su capacidad ACTUAL de generar dinero, <b>asumiendo que nunca más crecerá</b>. Ideal para inversores muy conservadores.</p>", unsafe_allow_html=True)
            
            ce1, ce2 = st.columns(2)
            epv_mgn = ce1.slider("Margen Operativo Ajustado (%)", 1.0, 50.0, float((ebit/revenue)*100) if revenue else 10.0) / 100.0
            epv_wacc = ce2.slider("WACC / Tasa de Descuento (%)", 2.0, 20.0, float(calc_wacc*100)) / 100.0
            
            adj_earnings = (revenue * epv_mgn) * (1 - tax_rate)
            epv_val = (adj_earnings / epv_wacc) - net_debt
            epv_price = epv_val / shares_out if shares_out else 0
            upside_epv = (epv_price - price) / price if price else 0
            
            c_e1, c_e2, c_e3 = st.columns(3)
            c_e1.metric("Beneficio Operativo Ajustado", fmt_big(adj_earnings))
            c_e2.metric("Valor Justo (Crecimiento Cero)", f"{sym}{epv_price:,.2f}")
            c_e3.metric("Potencial", f"{upside_epv*100:.1f}%")
            
            if upside_epv > 0:
                st.success("¡Excelente! El precio de la acción es menor que el EPV. Esto significa que estás comprando todo el crecimiento futuro de esta empresa completamente gratis.")
            else:
                st.info("El precio es mayor que el EPV. Esto es normal; significa que el mercado está pagando un extra (una prima) porque confía en que la empresa va a seguir creciendo en el futuro.")
        else:
            st.warning("La empresa tiene pérdidas operativas (EBIT < 0). El EPV asume beneficios constantes, por lo que no puede aplicarse aquí.")

    elif val_method == "Modelo de Dividendos (DDM)":
        if div_yield > 0:
            div_amount = price * div_yield
            st.markdown("<p style='font-size:0.9rem; opacity:0.7; margin-bottom: 20px;'>Modelo de Crecimiento de Gordon (Gordon Growth Model). Valora la empresa proyectando los dividendos futuros hasta el infinito.</p>", unsafe_allow_html=True)
            
            cd1, cd2 = st.columns(2)
            d_g = cd1.slider("Crecimiento Anual del Dividendo (%)", 0.0, 15.0, 3.0) / 100.0
            d_ke = cd2.slider("Retorno Exigido por el Inversor (Ke) (%)", 2.0, 25.0, float(ke*100)) / 100.0
            
            if d_ke > d_g:
                ddm_val = (div_amount * (1 + d_g)) / (d_ke - d_g)
                upside_ddm = (ddm_val - price) / price if price else 0
                
                c_d1, c_d2 = st.columns(2)
                c_d1.metric("Valor Justo (DDM)", f"{sym}{ddm_val:,.2f}")
                c_d2.metric("Potencial", f"{upside_ddm*100:.1f}%")
            else:
                st.error("Matemáticamente imposible: El Retorno Exigido (Ke) debe ser estrictamente mayor que el Crecimiento del Dividendo (g).")
        else:
            st.warning("Esta acción no reparte dividendos, o no se ha reportado el 'Dividend Yield'. El modelo DDM solo funciona para empresas que distribuyen caja a sus accionistas regularmente.")

    elif val_method == "Múltiplos (Comparativa)":
        ev = mkt_cap + net_debt
        cols = st.columns(4)
        multiples_data = [
            ("PER", mkt_cap / net_income if net_income and net_income > 0 else None, "Price to Earnings: Cuántos años tardarías en recuperar la inversión con los beneficios netos actuales."),
            ("EV/EBITDA", ev / ebitda if ebitda and ebitda > 0 else None, "Valor de Empresa sobre Rentabilidad Bruta. Descuenta la deuda, ideal para comparar empresas de distinto tamaño."),
            ("EV/EBIT", ev / ebit if ebit and ebit > 0 else None, "Igual que EV/EBITDA pero descontando amortizaciones (Múltiplo de Acquirer's Multiple)."),
            ("EV/Ventas", ev / revenue if revenue and revenue > 0 else None, "Útil para valorar empresas de alto crecimiento (Growth) que aún no generan beneficios netos."),
        ]
        for i, (name_m, val, h_text) in enumerate(multiples_data):
            cols[i].metric(name_m, f"{val:.1f}x" if val else "N/A", help=h_text)

        st.markdown("<br>", unsafe_allow_html=True)
        comp_input = st.text_input("Añadir Competidores (separados por coma para comparar)", placeholder="Ej: KO, PEP, MNST")
        if comp_input:
            comp_tickers = [c.strip().upper() for c in comp_input.split(",") if c.strip()]
            comp_list = [{"Ticker": ticker, "PER": multiples_data[0][1], "EV/EBITDA": multiples_data[1][1], "EV/Ventas": multiples_data[3][1]}]
            
            with st.spinner("Descargando métricas de competidores..."):
                for ct in comp_tickers:
                    try:
                        cti = yf.Ticker(ct).info
                        comp_list.append({
                            "Ticker": ct, 
                            "PER": cti.get("trailingPE"), 
                            "EV/EBITDA": cti.get("enterpriseToEbitda"), 
                            "EV/Ventas": cti.get("enterpriseToRevenue")
                        })
                    except: pass
            
            df_comp = pd.DataFrame(comp_list).set_index("Ticker")
            st.dataframe(df_comp.style.format("{:.2f}x", na_rep="N/A"), use_container_width=True)

        st.divider()
        st.markdown("#### 🥊 Fuerza Relativa (vs S&P 500)")
        st.markdown("<p style='font-size:0.85rem; opacity:0.7; margin-top:-10px;'>Compara la tendencia histórica real de esta acción contra la media del mercado global.</p>", unsafe_allow_html=True)
        
        @st.cache_data(ttl=3600, show_spinner=False)
        def get_sp500_v2(per):
            try: return yf.Ticker("^GSPC").history(period=per)
            except: return pd.DataFrame()
            
        sp500_hist = get_sp500_v2(chart_period)
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
    st.markdown("### 📝 Informe Institucional de Inversión")
    st.markdown("<p style='font-size:0.9rem; opacity:0.7; margin-top:-10px;'>Análisis cuantitativo y cualitativo estilo Bloomberg Terminal. Incluye Piotroski F-Score, fosos defensivos y veredicto final.</p>", unsafe_allow_html=True)
    
    if st.button("Generar Informe Institucional Completo", use_container_width=True, key="btn_thesis_main"):
        st.session_state[f"thesis_{ticker}"] = True
        
    if st.session_state.get(f"thesis_{ticker}", False):
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ── PIOTROSKI F-SCORE (0-9) ──
        piotroski = 0
        piotroski_details = []
        
        # Extraer datos multi-año si están disponibles
        ni_curr = income.iloc[:, 0].get("Net Income", 0) if not income.empty and len(income.columns) > 0 else 0
        ni_prev = income.iloc[:, 1].get("Net Income", 0) if not income.empty and len(income.columns) > 1 else 0
        rev_curr = income.iloc[:, 0].get("Total Revenue", 0) if not income.empty and len(income.columns) > 0 else 0
        rev_prev = income.iloc[:, 1].get("Total Revenue", 0) if not income.empty and len(income.columns) > 1 else 0
        
        ta_curr, ta_prev = 1, 1
        ltd_curr, ltd_prev = 0, 0
        ca_curr, ca_prev, cl_curr, cl_prev = 0, 0, 0, 0
        shares_curr, shares_prev = shares_out or 1, shares_out or 1
        
        if not balance.empty:
            for k in ["Total Assets"]:
                if k in balance.index:
                    ta_curr = balance.iloc[:, 0].get(k, 1) or 1
                    ta_prev = balance.iloc[:, 1].get(k, ta_curr) if len(balance.columns) > 1 else ta_curr
            for k in ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"]:
                if k in balance.index:
                    ltd_curr = balance.iloc[:, 0].get(k, 0) or 0
                    ltd_prev = balance.iloc[:, 1].get(k, ltd_curr) if len(balance.columns) > 1 else ltd_curr
                    break
            for k in ["Current Assets"]:
                if k in balance.index:
                    ca_curr = balance.iloc[:, 0].get(k, 0) or 0
                    ca_prev = balance.iloc[:, 1].get(k, ca_curr) if len(balance.columns) > 1 else ca_curr
            for k in ["Current Liabilities"]:
                if k in balance.index:
                    cl_curr = balance.iloc[:, 0].get(k, 1) or 1
                    cl_prev = balance.iloc[:, 1].get(k, cl_curr) if len(balance.columns) > 1 else cl_curr
        
        cfo_curr = 0
        if not cashflow.empty:
            for k in ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"]:
                if k in cashflow.index:
                    cfo_curr = cashflow.iloc[:, 0].get(k, 0) or 0
                    break
        
        # 1. ROA positivo
        roa = ni_curr / ta_curr if ta_curr else 0
        if roa > 0: piotroski += 1; piotroski_details.append(("ROA positivo", True, f"ROA = {roa*100:.2f}%"))
        else: piotroski_details.append(("ROA positivo", False, f"ROA = {roa*100:.2f}%"))
        
        # 2. CFO positivo
        if cfo_curr > 0: piotroski += 1; piotroski_details.append(("Cash Flow Operativo positivo", True, f"CFO = {cfo_curr:,.0f}"))
        else: piotroski_details.append(("Cash Flow Operativo positivo", False, f"CFO = {cfo_curr:,.0f}"))
        
        # 3. ROA creciente
        roa_prev = ni_prev / ta_prev if ta_prev else 0
        if roa > roa_prev: piotroski += 1; piotroski_details.append(("ROA creciente vs año anterior", True, f"{roa_prev*100:.2f}% → {roa*100:.2f}%"))
        else: piotroski_details.append(("ROA creciente vs año anterior", False, f"{roa_prev*100:.2f}% → {roa*100:.2f}%"))
        
        # 4. Calidad de beneficios (CFO > Net Income)
        if cfo_curr > ni_curr: piotroski += 1; piotroski_details.append(("Calidad de beneficios (CFO > NI)", True, "Los beneficios son reales, no solo contables"))
        else: piotroski_details.append(("Calidad de beneficios (CFO > NI)", False, "Los beneficios podrían ser artificiales"))
        
        # 5. Deuda a largo plazo decreciente
        if ltd_curr < ltd_prev: piotroski += 1; piotroski_details.append(("Deuda L/P decreciente", True, f"{ltd_prev:,.0f} → {ltd_curr:,.0f}"))
        else: piotroski_details.append(("Deuda L/P decreciente", False, f"{ltd_prev:,.0f} → {ltd_curr:,.0f}"))
        
        # 6. Liquidez (Current Ratio) creciente
        cr_curr = ca_curr / cl_curr if cl_curr else 0
        cr_prev = ca_prev / cl_prev if cl_prev else 0
        if cr_curr > cr_prev: piotroski += 1; piotroski_details.append(("Liquidez (Current Ratio) creciente", True, f"{cr_prev:.2f}x → {cr_curr:.2f}x"))
        else: piotroski_details.append(("Liquidez (Current Ratio) creciente", False, f"{cr_prev:.2f}x → {cr_curr:.2f}x"))
        
        # 7. No dilución de acciones
        if shares_curr <= shares_prev: piotroski += 1; piotroski_details.append(("Sin dilución de accionistas", True, "La empresa no emitió acciones nuevas"))
        else: piotroski_details.append(("Sin dilución de accionistas", False, "La empresa diluyó a los accionistas"))
        
        # 8. Margen bruto creciente
        gp_curr = income.iloc[:, 0].get("Gross Profit", 0) if not income.empty and len(income.columns) > 0 else 0
        gp_prev = income.iloc[:, 1].get("Gross Profit", 0) if not income.empty and len(income.columns) > 1 else 0
        gm_curr = (gp_curr or 0) / rev_curr if rev_curr else 0
        gm_prev = (gp_prev or 0) / rev_prev if rev_prev else 0
        if gm_curr > gm_prev: piotroski += 1; piotroski_details.append(("Margen bruto creciente", True, f"{gm_prev*100:.1f}% → {gm_curr*100:.1f}%"))
        else: piotroski_details.append(("Margen bruto creciente", False, f"{gm_prev*100:.1f}% → {gm_curr*100:.1f}%"))
        
        # 9. Rotación de activos creciente
        at_curr = rev_curr / ta_curr if ta_curr else 0
        at_prev = (rev_prev or 0) / ta_prev if ta_prev else 0
        if at_curr > at_prev: piotroski += 1; piotroski_details.append(("Rotación de activos creciente", True, f"{at_prev:.2f}x → {at_curr:.2f}x"))
        else: piotroski_details.append(("Rotación de activos creciente", False, f"{at_prev:.2f}x → {at_curr:.2f}x"))
        
        # ── Visualización Piotroski ──
        if piotroski >= 7: pio_color, pio_label = "#00C853", "SALUD EXCELENTE"
        elif piotroski >= 4: pio_color, pio_label = "#d4af37", "SALUD ACEPTABLE"
        else: pio_color, pio_label = "#FF3D00", "RIESGO DE DETERIORO"
        
        st.markdown(f"""
        <div style='background: rgba(128,128,128,0.05); border: 1px solid {pio_color}40; border-radius: 12px; padding: 20px; margin-bottom: 20px;'>
            <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px;'>
                <div>
                    <h4 style='margin: 0; color: {pio_color};'>📊 Piotroski F-Score: {piotroski}/9</h4>
                    <p style='margin: 2px 0 0 0; opacity: 0.7; font-size: 0.85rem;'>Métrica institucional de salud financiera (usado por Hedge Funds para detectar quiebras)</p>
                </div>
                <div style='background: {pio_color}20; border: 1px solid {pio_color}; border-radius: 8px; padding: 6px 16px;'>
                    <span style='color: {pio_color}; font-weight: 700; font-size: 0.9rem;'>{pio_label}</span>
                </div>
            </div>
            <div style='background: rgba(255,255,255,0.05); border-radius: 8px; height: 14px; overflow: hidden;'>
                <div style='background: linear-gradient(90deg, {pio_color}, {pio_color}80); height: 100%; width: {piotroski/9*100:.0f}%; border-radius: 8px; transition: width 0.5s;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📋 Desglose de los 9 criterios Piotroski"):
            for name, passed, detail in piotroski_details:
                icon = "✅" if passed else "❌"
                st.markdown(f"{icon} **{name}** — _{detail}_")
        
        st.divider()
        
        # ── SECCIÓN 1: FOSO DEFENSIVO ──
        net_mgn = (net_income / revenue) if revenue and revenue > 0 else 0
        if net_mgn > 0.15:
            moat_text = f"Fuerte ventaja competitiva. Un margen neto del {net_mgn*100:.1f}% demuestra poder de fijación de precios (Pricing Power). La empresa domina su sector y puede trasladar la inflación al consumidor."
            moat_icon, moat_color = "🟢", "#00C853"
        elif net_mgn > 0.05:
            moat_text = f"Estándar. Con márgenes del {net_mgn*100:.1f}%, es un negocio estable pero vulnerable a presiones de costes o competidores agresivos."
            moat_icon, moat_color = "🟡", "#d4af37"
        else:
            moat_text = f"Débil o inexistente. Operar con márgenes tan ajustados ({net_mgn*100:.1f}%) exige vender un volumen masivo para sobrevivir."
            moat_icon, moat_color = "🔴", "#FF3D00"
            
        # ── SECCIÓN 2: MARGEN DE SEGURIDAD ──
        e_net_income = income.iloc[:, 0].get("Net Income", 0) if not income.empty else 0
        e_equity = mkt_cap
        if not balance.empty:
            for k in ["Stockholders Equity", "Total Stockholder Equity"]:
                if k in balance.index: e_equity = balance.iloc[:, 0].get(k, 0); break
        e_eps = e_net_income / shares_out if shares_out and e_net_income else 0
        e_bvps = e_equity / shares_out if shares_out else 0
        e_graham = np.sqrt(22.5 * e_eps * e_bvps) if e_eps > 0 and e_bvps > 0 else e_bvps
        thesis_upside = (e_graham - price) / price if price else 0

        pe = mkt_cap / net_income if net_income and net_income > 0 else 999
        if thesis_upside > 0.20:
            val_txt = f"Excelente. El mercado está deprimiendo la acción irracionalmente. Cotizando a un PER de {pe:.1f}x y con un descuento del {thesis_upside*100:.1f}%, el riesgo de pérdida a largo plazo es bajo."
            val_icon, val_color = "🟢", "#00C853"
        elif thesis_upside > 0:
            val_txt = f"Aceptable. La acción cotiza por debajo de su valor intrínseco teórico (según Graham), pero no hay un gran margen de error."
            val_icon, val_color = "🟡", "#d4af37"
        else:
            val_txt = f"Inexistente. El mercado asume la perfección pagando un PER de {pe:.1f}x. Cualquier fallo en su plan de negocio futuro provocará una corrección severa."
            val_icon, val_color = "🔴", "#FF3D00"
            
        # ── SECCIÓN 3: PERSPECTIVA A LARGO PLAZO ──
        cagr = 0
        if not income.empty and "Total Revenue" in income.index:
            revs = [v for v in income.loc["Total Revenue"].dropna().tolist() if v > 0][::-1]
            if len(revs) >= 2:
                cagr = ((revs[-1] / revs[0]) ** (1 / (len(revs) - 1)) - 1) * 100
                
        if cagr > 10:
            lt_text = f"Crecimiento estructural brillante ({cagr:.1f}% CAGR). Candidata para estrategia 'Buy & Hold' a largo plazo."
            lt_icon, lt_color = "🟢", "#00C853"
        elif cagr > 0:
            lt_text = f"Negocio maduro tipo 'Cash Cow' ({cagr:.1f}% CAGR). Ideal para perfiles defensivos que busquen dividendos estables."
            lt_icon, lt_color = "🟡", "#d4af37"
        else:
            lt_text = f"Contracción. Los ingresos llevan años cayendo. Posible 'Value Trap' o juego especulativo táctico."
            lt_icon, lt_color = "🔴", "#FF3D00"

        # ── RENDERIZADO TIPO BLOOMBERG ──
        st.markdown(f"""
        <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 20px;'>
            <div class='glow-hover' style='background: rgba(128,128,128,0.05); padding: 20px; border-radius: 10px; border-left: 4px solid {moat_color};'>
                <h5 style='color: {moat_color}; margin: 0 0 8px 0;'>🛡️ Foso Defensivo</h5>
                <p style='font-size: 0.9rem; line-height: 1.5; margin: 0;'>{moat_text}</p>
            </div>
            <div class='glow-hover' style='background: rgba(128,128,128,0.05); padding: 20px; border-radius: 10px; border-left: 4px solid {val_color};'>
                <h5 style='color: {val_color}; margin: 0 0 8px 0;'>⚖️ Margen de Seguridad</h5>
                <p style='font-size: 0.9rem; line-height: 1.5; margin: 0;'>{val_txt}</p>
            </div>
            <div class='glow-hover' style='background: rgba(128,128,128,0.05); padding: 20px; border-radius: 10px; border-left: 4px solid {lt_color};'>
                <h5 style='color: {lt_color}; margin: 0 0 8px 0;'>🚀 Perspectiva L/P</h5>
                <p style='font-size: 0.9rem; line-height: 1.5; margin: 0;'>{lt_text}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ── VEREDICTO FINAL ──
        total_score = piotroski
        if thesis_upside > 0.20: total_score += 2
        elif thesis_upside > 0: total_score += 1
        if cagr > 10: total_score += 2
        elif cagr > 0: total_score += 1
        
        if total_score >= 10:
            final_verdict = "COMPRA FUERTE"
            final_color = "#00C853"
            final_desc = "La empresa presenta una salud financiera excepcional, cotiza con descuento respecto a su valor intrínseco y tiene un crecimiento sólido. Reúne todas las condiciones para una inversión de alta convicción."
        elif total_score >= 7:
            final_verdict = "COMPRA MODERADA"
            final_color = "#00C853"
            final_desc = "Los fundamentales son sólidos y el precio es razonable. Es una buena inversión, aunque no está regalada. Considere un tamaño de posición moderado."
        elif total_score >= 4:
            final_verdict = "MANTENER / VIGILAR"
            final_color = "#d4af37"
            final_desc = "La empresa muestra señales mixtas. Los fundamentales no son lo suficientemente fuertes para justificar una compra agresiva, pero tampoco hay razones urgentes para vender."
        else:
            final_verdict = "EVITAR / VENDER"
            final_color = "#FF3D00"
            final_desc = "Múltiples señales de alarma detectadas. Los fundamentales se están deteriorando y el precio no compensa el riesgo asumido. Se recomienda evitar o reducir la exposición."
        
        st.markdown(f"""
        <div class='glow-hover' style='background: {final_color}08; border: 2px solid {final_color}60; border-radius: 12px; padding: 24px; text-align: center;'>
            <p style='font-size: 0.8rem; opacity: 0.6; margin: 0; letter-spacing: 2px;'>VEREDICTO INSTITUCIONAL DE Á.L.V.A.R.O.</p>
            <h2 style='color: {final_color}; margin: 8px 0; font-size: 2rem;'>{final_verdict}</h2>
            <p style='font-size: 0.95rem; margin: 0; max-width: 600px; margin: 0 auto; line-height: 1.5;'>{final_desc}</p>
            <p style='font-size: 0.75rem; opacity: 0.4; margin: 12px 0 0 0;'>Score Combinado: {total_score}/13 (Piotroski {piotroski}/9 + Valoración + Crecimiento)</p>
        </div>
        """, unsafe_allow_html=True)

# ── Tab 7: Backtesting Á.L.V.A.R.O. ──
with tab_backtest:
    st.markdown("### 🤖 Motor de IA: Análisis Estratégico Multi-Modelo")
    
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
    
    bt_strategy = st.selectbox("Selecciona la estrategia a evaluar:", [
        "RSI Sobreventa (< 30)",
        "Cruce de Medias Móviles (SMA 50/200 — Golden Cross)",
        "Rebote de Bandas de Bollinger",
        "Cruce de MACD"
    ], help="Cada estrategia utiliza un indicador técnico distinto para detectar puntos de entrada. Prueba varias y compáralas.")
    
    strategy_descriptions = {
        "RSI Sobreventa (< 30)": "Compra cuando el RSI cruza por debajo de 30 (pánico vendedor). Estrategia clásica de reversión a la media.",
        "Cruce de Medias Móviles (SMA 50/200 — Golden Cross)": "Compra cuando la media móvil de 50 días cruza por encima de la de 200 días (confirmación de tendencia alcista).",
        "Rebote de Bandas de Bollinger": "Compra cuando el precio toca la Banda de Bollinger inferior (2 desviaciones estándar por debajo de la media de 20 días).",
        "Cruce de MACD": "Compra cuando la línea MACD cruza por encima de la línea de señal (cambio de momentum de bajista a alcista)."
    }
    st.markdown(f"<p style='font-size:0.85rem; opacity:0.6;'>{strategy_descriptions[bt_strategy]}</p>", unsafe_allow_html=True)
    
    if st.button("🚀 Ejecutar Simulación IA", use_container_width=True):
        with st.spinner("Analizando miles de velas históricas..."):
            try:
                bt_hist = yf.Ticker(ticker).history(period="5y")
                if len(bt_hist) > 50:
                    
                    # ── Generar señales según estrategia elegida ──
                    if bt_strategy == "RSI Sobreventa (< 30)":
                        delta_bt = bt_hist['Close'].diff()
                        gain_bt = (delta_bt.where(delta_bt > 0, 0)).rolling(14).mean()
                        loss_bt = (-delta_bt.where(delta_bt < 0, 0)).rolling(14).mean()
                        rs_bt = gain_bt / loss_bt
                        bt_hist['RSI'] = 100 - (100 / (1 + rs_bt))
                        signals = (bt_hist['RSI'] < 30) & (bt_hist['RSI'].shift(1) >= 30)
                        
                    elif bt_strategy == "Cruce de Medias Móviles (SMA 50/200 — Golden Cross)":
                        bt_hist['SMA50'] = bt_hist['Close'].rolling(50).mean()
                        bt_hist['SMA200'] = bt_hist['Close'].rolling(200).mean()
                        signals = (bt_hist['SMA50'] > bt_hist['SMA200']) & (bt_hist['SMA50'].shift(1) <= bt_hist['SMA200'].shift(1))
                        
                    elif bt_strategy == "Rebote de Bandas de Bollinger":
                        bt_hist['BB_mid'] = bt_hist['Close'].rolling(20).mean()
                        bt_hist['BB_std'] = bt_hist['Close'].rolling(20).std()
                        bt_hist['BB_low'] = bt_hist['BB_mid'] - (2 * bt_hist['BB_std'])
                        signals = (bt_hist['Close'] <= bt_hist['BB_low']) & (bt_hist['Close'].shift(1) > bt_hist['BB_low'].shift(1))
                        
                    elif bt_strategy == "Cruce de MACD":
                        ema12 = bt_hist['Close'].ewm(span=12, adjust=False).mean()
                        ema26 = bt_hist['Close'].ewm(span=26, adjust=False).mean()
                        bt_hist['MACD'] = ema12 - ema26
                        bt_hist['MACD_signal'] = bt_hist['MACD'].ewm(span=9, adjust=False).mean()
                        signals = (bt_hist['MACD'] > bt_hist['MACD_signal']) & (bt_hist['MACD'].shift(1) <= bt_hist['MACD_signal'].shift(1))
                    
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
                            <p style="font-size: 1.1rem; margin-bottom: 5px;">Si hubieras invertido ciegamente <b>1.000{sym} exactos</b> cada vez que esta estrategia detectó una señal en los últimos 5 años (un total de {len(returns)} operaciones)...</p>
                            <h2 style="color: {ganancia_color}; margin-top: 0;">Habrías generado {'+' if total_profit_usd>0 else ''}{total_profit_usd:,.2f}{sym} de beneficio neto.</h2>
                            <p style="opacity: 0.6; font-size: 0.85rem; margin-bottom: 0;">*Nota: Simulador bruto sin comisiones, asumiendo inversión lineal, compra perfecta tras la alerta y venta un mes después.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        conclusion = f"**Conclusión del Algoritmo:** De las {len(returns)} veces que se activó la señal, ganaste dinero en {wins} ocasiones y perdiste en {losses}."
                        if win_rate > 55:
                            st.info(f"{conclusion} **La estrategia muestra una clara ventaja estadística.**")
                        else:
                            st.warning(f"{conclusion} **La estrategia es muy arriesgada y equivale prácticamente a tirar una moneda al aire.**")
                    else:
                        st.warning("No ha habido suficientes señales de esta estrategia en los últimos 5 años para analizar.")
                else:
                    st.error("No hay suficientes datos históricos para este activo.")
            except Exception as e:
                st.error(f"Error en el backtest: {e}")

# ── Tab 8: Monte Carlo Simulator ──
with tab_mc:
    st.markdown("### 🎲 Simulador de Riesgo Avanzado (Colas Pesadas)")
    st.markdown("<p style='font-size:0.85rem; opacity:0.7; margin-top:-10px;'>Simulación estocástica de 1.000 escenarios futuros usando distribución t-Student para modelar Cisnes Negros (Crash/Pumps extremos).</p>", unsafe_allow_html=True)
    
    with st.expander("🎓 ¿Cómo funciona este simulador y por qué lo usan los bancos?"):
        st.markdown("""
        **La Bola de Cristal de Wall Street:** En lugar de adivinar si la acción va a subir o bajar, el método Monte Carlo acepta que el mercado es caótico. 
        Lo que hace es medir exactamente cómo se ha movido esta acción en el pasado y genera **1.000 futuros paralelos**. 
        **Novedad (Fat Tails):** Ahora usamos un modelo t-Student. En la vida real, el mercado no es una campana perfecta; a veces hay caídas de pánico (COVID) o burbujas. Este modelo inyecta esa posibilidad de eventos extremos, haciéndolo mucho más realista.
        """)
        
    st.markdown("#### 🎯 Calculadora de Objetivos")
    target_mc = st.number_input(f"¿A qué precio te gustaría que llegase esta acción a final de año?", min_value=0.0, value=float(price)*1.2 if price else 100.0, step=1.0)
        
    if st.button("Ejecutar 1.000 Simulaciones Institucionales", use_container_width=True):
        with st.spinner("Descargando histórico diario para cálculo de volatilidad..."):
            try:
                mc_hist = yf.download(ticker, period="2y", interval="1d", progress=False)
                if isinstance(mc_hist.columns, pd.MultiIndex):
                    mc_hist = mc_hist.xs(ticker, axis=1, level=1) if ticker in mc_hist.columns.get_level_values(1) else mc_hist
                if mc_hist.empty:
                    mc_hist = yf.Ticker(ticker).history(period="2y", interval="1d")
            except:
                mc_hist = hist
                
        if not mc_hist.empty and len(mc_hist) > 20:
            returns = mc_hist['Close'].pct_change().dropna()
            
            # Ajuste de escala si los datos son intradiarios (por si falla el fetch y usa hist)
            is_intra = (mc_hist.index[1] - mc_hist.index[0]).total_seconds() < 86400 if len(mc_hist) > 1 else False
            
            mu = returns.mean()
            sigma = returns.std()
            
            # Si es intradiario, anualizamos mu y sigma de forma aproximada (ej. 1h -> 7 barras al día)
            if is_intra:
                bars_per_day = 86400 / max((mc_hist.index[1] - mc_hist.index[0]).total_seconds(), 60)
                mu = mu * bars_per_day
                sigma = sigma * np.sqrt(bars_per_day)
            
            days = 252 # 1 trading year
            simulations = 1000
            last_price = float(mc_hist['Close'].iloc[-1])
            
            paths = np.zeros((days, simulations))
            paths[0] = last_price
            
            # Progreso
            with st.spinner("Generando 1.000 realidades alternativas con riesgo de Cisnes Negros..."):
                # df=4 yields heavy tails (standard in finance). Divide by sqrt(2) to standardize std.
                scale_factor = sigma / np.sqrt(2)
                for t in range(1, days):
                    rand_rets = (np.random.standard_t(df=4, size=simulations) * scale_factor) + mu
                    paths[t] = paths[t-1] * (1 + rand_rets)
                
            final_prices = paths[-1]
            prob_gain = (final_prices > last_price).mean() * 100
            prob_loss_20 = (final_prices < (last_price * 0.80)).mean() * 100
            prob_target = (final_prices >= target_mc).mean() * 100
            
            # Percentiles (Worst 5% and Best 5%)
            p5 = np.percentile(final_prices, 5)
            p95 = np.percentile(final_prices, 95)
            
            st.markdown(f"**Probabilidad de alcanzar {sym}{target_mc:,.2f}:** <span style='color:#d4af37; font-size:1.2rem; font-weight:bold;'>{prob_target:.1f}%</span>", unsafe_allow_html=True)
            st.divider()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Prob. Ganancia (1 Año)", f"{prob_gain:.1f}%", help="Porcentaje de los 1.000 futuros en los que cerrarías el año con dinero extra.")
            c2.metric("Prob. Caída Severa (>20%)", f"{prob_loss_20:.1f}%", help="Mide el riesgo extremo ('Tail Risk'). Probabilidad de perder más de un quinto de tu inversión.")
            c3.metric("Precio Promedio Esperado", f"{sym}{np.mean(final_prices):.2f}", help="La media matemática de los 1.000 escenarios.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            c4, c5 = st.columns(2)
            c4.metric("Peor Escenario (Percentil 5)", f"{sym}{p5:.2f}", help="En el 95% de los escenarios, ganarás más dinero que esto. Es tu 'red de seguridad' pesimista.")
            c5.metric("Mejor Escenario (Percentil 95)", f"{sym}{p95:.2f}", help="En un escenario hiper-optimista (solo un 5% de probabilidad de ser mejor que esto), podrías ganar hasta aquí.")
            
            c_g1, c_g2 = st.columns([2, 1])
            with c_g1:
                fig_mc = go.Figure()
                for i in range(50):
                    fig_mc.add_trace(go.Scatter(y=paths[:, i], mode='lines', line=dict(color='rgba(212,175,55,0.25)', width=1), showlegend=False))
                fig_mc.add_hline(y=last_price, line_dash="dot", line_color="white", annotation_text="Precio Actual")
                fig_mc.add_hline(y=target_mc, line_dash="dash", line_color="#00C853", annotation_text="Objetivo")
                fig_mc.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", title="50 Escenarios de Prueba Aleatorios", font=dict(family="Inter"))
                st.plotly_chart(fig_mc, use_container_width=True, config={'displayModeBar': False})
                
            with c_g2:
                fig_hist = go.Figure(data=[go.Violin(y=final_prices, side='positive', line_color='#d4af37', fillcolor='rgba(212,175,55,0.4)', showlegend=False, points=False, width=3)])
                fig_hist.add_hline(y=last_price, line_dash="dot", line_color="white")
                fig_hist.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", title="Campana Densidad", xaxis_visible=False, font=dict(family="Inter"))
                st.plotly_chart(fig_hist, use_container_width=True, config={'displayModeBar': False})
            
            # AI Conclusion
            verdicto = "riesgo aceptable" if prob_loss_20 < 15 else "riesgo MUY ALTO"
            st.markdown(f"""
            <div class='glow-hover' style='background: rgba(128,128,128,0.05); border: 1px solid rgba(212,175,55,0.3); border-radius: 8px; padding: 20px;'>
                <h4 style='color: #d4af37; margin-top: 0;'>🤖 Interpretación de Á.L.V.A.R.O.</h4>
                <p style='font-size: 0.9rem; line-height: 1.5; margin-bottom: 0;'>
                Basado en el caos matemático de los últimos años (incluyendo el riesgo estadístico de Cisnes Negros), si compras hoy, tienes un <b>{prob_gain:.1f}% de posibilidades</b> de terminar el año en positivo. 
                El peor escenario estadístico probable te dejaría la acción en <b>{sym}{p5:.2f}</b>, mientras que el mejor de los casos la impulsaría a <b>{sym}{p95:.2f}</b>. 
                Hay exactamente un <b>{prob_target:.1f}%</b> de probabilidad de que alcances tu objetivo de {sym}{target_mc:,.2f}. 
                Consideramos que es una inversión de <b>{verdicto}</b> desde el punto de vista del Tail Risk.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.warning("No hay suficientes datos históricos para simular volatilidad.")

# ── Tab 9: Portfolio Tracker ──
with tab_port:
    st.markdown("### 💼 Centro de Gestión de Patrimonio")
    st.markdown("<p style='font-size:0.85rem; opacity:0.7; margin-top:-10px;'>Gestión institucional multi-activo. Visualiza tu exposición, diversificación y riesgo global.</p>", unsafe_allow_html=True)
    
    if "portfolio" not in st.session_state:
        st.session_state["portfolio"] = {}
        
    all_options = []
    for c, data in MARKETS_BY_COUNTRY.items():
        for sec, tks in data.get("sectors", {}).items():
            for tk, name in tks.items():
                all_options.append(f"{tk} - {name}")
    all_options = sorted(list(set(all_options)))

    st.markdown("<div style='background: rgba(128,128,128,0.05); padding: 20px; border-radius: 12px; border: 1px solid rgba(212,175,55,0.2); margin-bottom: 25px;'><p style='margin-top:0; margin-bottom: 15px; color: #d4af37; font-weight: 600; font-size: 0.95rem;'><i class='fas fa-shopping-cart'></i> 🛒 Terminal de Compras (Añadir Activos)</p>", unsafe_allow_html=True)
    
    c_add1, c_add2, c_add3, c_add4 = st.columns([2, 1, 1, 1])
    port_choice = c_add1.selectbox("Activo", options=all_options, index=None, placeholder="-- Buscar en lista global --", label_visibility="collapsed")
    custom_add = c_add1.text_input("Ticker manual", placeholder="...o escribe un ticker manual (Ej: TSLA)", key="custom_tk", label_visibility="collapsed")
    
    tk_preview = None
    if custom_add and custom_add.strip():
        tk_preview = custom_add.strip().upper()
    elif port_choice:
        tk_preview = port_choice.split(" - ")[0].strip().upper()
        
    default_price = 0.0
    if tk_preview:
        if tk_preview == ticker:
            default_price = float(price) if price else 0.0
        else:
            try:
                fast_p = yf.Ticker(tk_preview).fast_info.get("lastPrice")
                if fast_p: default_price = float(fast_p)
            except: pass
            
    port_shares = c_add2.number_input("Nº Acciones", min_value=0.0, step=1.0, value=1.0, key="p_sh", help="Cantidad de acciones compradas")
    
    # Clave dinámica para que Streamlit refresque el valor automáticamente si cambia la acción o la cantidad
    dyn_key = f"p_pr_{tk_preview}_{port_shares}"
    port_cost = c_add3.number_input("Coste Total ($)", min_value=0.0, step=0.01, value=float(default_price * port_shares), key=dyn_key, help="Coste total (Precio actual x Nº Acciones). Puedes editarlo manualmente.")
    
    if c_add4.button("➕ Añadir a Cartera", use_container_width=True, type="primary"):
        tk_add = None
        if custom_add and custom_add.strip():
            tk_add = custom_add.strip().upper()
        elif port_choice:
            tk_add = port_choice.split(" - ")[0].strip().upper()
            
        if tk_add and port_shares > 0:
            current_port = st.session_state["portfolio"].get(tk_add, {})
            # Backward compatibility check
            if isinstance(current_port, (int, float)): 
                current_port = {"shares": current_port, "price": port_cost / port_shares if port_shares > 0 else 0}
                
            old_shares = current_port.get("shares", 0)
            old_price = current_port.get("price", 0)
            
            total_cost = (old_shares * old_price) + port_cost
            new_shares = old_shares + port_shares
            new_avg_price = total_cost / new_shares if new_shares > 0 else 0
            
            st.session_state["portfolio"][tk_add] = {"shares": new_shares, "price": new_avg_price}
            st.rerun()
            
    if c_add4.button("🗑️ Vaciar Cartera", use_container_width=True):
        st.session_state["portfolio"] = {}
        st.rerun()
        
    st.markdown("</div>", unsafe_allow_html=True)
            
    port = st.session_state["portfolio"]
    if port:
        port_data = []
        total_value = 0
        
        with st.spinner("Sincronizando con mercado en tiempo real..."):
            valid_tks_port = []
            for t, val in port.items():
                if isinstance(val, (int, float)) and val > 0:
                    valid_tks_port.append(t)
                    # auto-upgrade
                    port[t] = {"shares": val, "price": 0.0}
                elif isinstance(val, dict) and val.get("shares", 0) > 0:
                    valid_tks_port.append(t)
                    
            if valid_tks_port:
                try:
                    # Descarga masiva para hacer el sparkline y pillar el precio
                    h_port = yf.download(valid_tks_port, period="1mo", progress=False)
                    if 'Close' in h_port:
                        closes_port = h_port['Close']
                        if isinstance(closes_port, pd.Series):
                            closes_port = closes_port.to_frame()
                        
                        for t in valid_tks_port:
                            if t in closes_port.columns:
                                col = closes_port[t].dropna()
                                if len(col) > 0:
                                    p_price = float(col.iloc[-1])
                                    p_data = port[t]
                                    shares = p_data.get("shares", 0)
                                    buy_price = p_data.get("price", 0)
                                    
                                    val = p_price * shares
                                    total_value += val
                                    
                                    pnl_dol = (p_price - buy_price) * shares if buy_price > 0 else 0
                                    pnl_pct = ((p_price / buy_price) - 1) * 100 if buy_price > 0 else 0
                                    
                                    # Generar lista de valores para el sparkline
                                    sparkline_data = col.tolist()
                                    
                                    port_data.append({
                                        "Ticker": t, 
                                        "Empresa": t, 
                                        "Acciones": shares, 
                                        "P. Medio": buy_price,
                                        "Actual": p_price,
                                        "Retorno %": pnl_pct,
                                        "PnL Total": pnl_dol,
                                        "Tendencia (1M)": sparkline_data,
                                        "Valor Total": val
                                    })
                except Exception as e:
                    st.warning(f"Error sincronizando mercado: {e}")
                    
            for t in list(port.keys()):
                val = port[t]
                if isinstance(val, (int, float)) and val <= 0:
                    del st.session_state["portfolio"][t]
                elif isinstance(val, dict) and val.get("shares", 0) <= 0:
                    del st.session_state["portfolio"][t]
                
        if port_data:
            port_data = sorted(port_data, key=lambda x: x["Valor Total"], reverse=True)
            for d in port_data: d["Peso %"] = (d["Valor Total"] / total_value) * 100
            
            total_invested = sum([port[t].get("shares", 0) * port[t].get("price", 0) for t in valid_tks_port if isinstance(port[t], dict)])
            total_pnl = total_value - total_invested if total_invested > 0 else 0
            total_pnl_pct = (total_pnl / total_invested) * 100 if total_invested > 0 else 0
            
            pnl_col = color_up if total_pnl >= 0 else color_down
            pnl_sign = "+" if total_pnl >= 0 else ""
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='glow-hover' style='background: linear-gradient(145deg, rgba(20,20,20,1) 0%, rgba(30,30,30,1) 100%); border: 1px solid rgba(212,175,55,0.4); border-radius: 15px; padding: 35px; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.6); margin-bottom: 25px;'>
                <p style='font-family: "Outfit", sans-serif; font-size: 0.95rem; letter-spacing: 3px; text-transform: uppercase; color: #d4af37; margin: 0; opacity: 0.9;'>Patrimonio Líquido Total</p>
                <h1 style='font-family: "JetBrains Mono", monospace; font-size: 4.8rem; font-weight: 300; margin: 5px 0; color: #ffffff; text-shadow: 0 0 25px rgba(212,175,55,0.25); letter-spacing: -2px;'>
                    <span style='color: #d4af37; opacity: 0.8;'>$</span>{total_value:,.2f}
                </h1>
                <p style='font-size: 1.1rem; color: {pnl_col}; margin: 5px 0; font-weight: 600;'>Beneficio/Pérdida No Realizada: {pnl_sign}${total_pnl:,.2f} ({pnl_sign}{total_pnl_pct:.2f}%)</p>
                <p style='font-size: 0.8rem; opacity: 0.5; margin: 0; letter-spacing: 1px;'>ACTUALIZADO EN TIEMPO REAL</p>
            </div>
            """, unsafe_allow_html=True)
            
            df_port = pd.DataFrame(port_data).set_index("Ticker")
            
            c_port1, c_port2 = st.columns([1.5, 1])
            with c_port1:
                st.markdown("<h4 style='color: #d4af37;'>📑 Desglose de Activos</h4>", unsafe_allow_html=True)
                st.dataframe(
                    df_port[["Empresa", "Acciones", "P. Medio", "Actual", "Retorno %", "PnL Total", "Tendencia (1M)", "Valor Total", "Peso %"]],
                    column_config={
                        "P. Medio": st.column_config.NumberColumn("P. Compra", format="$%.2f"),
                        "Actual": st.column_config.NumberColumn("Actual", format="$%.2f"),
                        "Retorno %": st.column_config.NumberColumn("Retorno %", format="%.2f%%"),
                        "PnL Total": st.column_config.NumberColumn("PnL Total", format="$%.2f"),
                        "Tendencia (1M)": st.column_config.LineChartColumn("Tendencia (1M)"),
                        "Valor Total": st.column_config.NumberColumn("Valor Total", format="$%.2f"),
                        "Peso %": st.column_config.ProgressColumn("Peso %", format="%.1f%%", min_value=0, max_value=100)
                    },
                    use_container_width=True,
                    height=320
                )
                
            with c_port2:
                st.markdown("<h4 style='color: #d4af37; text-align:center;'>🍩 Distribución de Capital</h4>", unsafe_allow_html=True)
                neon_colors = ['#00FFFF', '#FF00FF', '#00FF00', '#FFFF00', '#FF4500', '#1E90FF', '#FF1493', '#7FFF00', '#00FA9A', '#FF0000', '#00BFFF', '#FFD700']
                # Make sure we have enough colors by cycling
                border_colors = [neon_colors[i % len(neon_colors)] for i in range(len(df_port))]
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=df_port.index, 
                    values=df_port['Valor Total'], 
                    hole=0.68, 
                    marker=dict(colors=['#0a0b10']*len(df_port), line=dict(color=border_colors, width=3)),
                    textinfo='label+percent',
                    textposition='outside',
                    hoverinfo='label+value+percent'
                )])
                fig_pie.update_layout(
                    height=320, 
                    margin=dict(l=30, r=30, t=20, b=20), 
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    font=dict(family="Inter", color="rgba(255,255,255,0.7)"),
                    showlegend=False,
                    annotations=[dict(text=f"{len(df_port)}<br>ACTIVOS", x=0.5, y=0.5, font_size=16, font_color="#d4af37", showarrow=False)]
                )
                st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
            
            # ── Matriz de Correlación ──
            st.divider()
            st.markdown("#### 🔗 Matriz de Correlación entre Activos")
            st.markdown("<p style='font-size:0.85rem; opacity:0.7; margin-top:-10px;'>Mide cómo se mueven tus activos entre sí. <b style='color:#FF3D00;'>Rojo intenso</b> = se mueven juntos (riesgo concentrado). <b style='color:#1E90FF;'>Azul intenso</b> = se mueven en dirección opuesta (diversificación real).</p>", unsafe_allow_html=True)
            
            valid_tks_corr = [d["Ticker"] for d in port_data]
            if len(valid_tks_corr) >= 2:
                with st.spinner("Calculando correlaciones históricas (6 meses)..."):
                    try:
                        corr_dl = yf.download(valid_tks_corr, period="6mo", progress=False)
                        if 'Close' in corr_dl:
                            corr_closes = corr_dl['Close']
                            if isinstance(corr_closes, pd.Series):
                                corr_closes = corr_closes.to_frame()
                            corr_returns = corr_closes.pct_change().dropna()
                            corr_matrix = corr_returns.corr()
                            
                            # Heatmap con Plotly
                            fig_corr = go.Figure(data=go.Heatmap(
                                z=corr_matrix.values,
                                x=corr_matrix.columns.tolist(),
                                y=corr_matrix.index.tolist(),
                                colorscale=[
                                    [0.0, '#1E90FF'],
                                    [0.5, '#0a0b10'],
                                    [1.0, '#FF3D00']
                                ],
                                zmin=-1, zmax=1,
                                text=np.round(corr_matrix.values, 2),
                                texttemplate='%{text}',
                                textfont=dict(size=13, family='JetBrains Mono'),
                                hovertemplate='%{x} vs %{y}: %{z:.2f}<extra></extra>',
                                colorbar=dict(
                                    title=dict(text="Corr", side="right"),
                                    tickvals=[-1, -0.5, 0, 0.5, 1],
                                    ticktext=["-1", "-0.5", "0", "+0.5", "+1"]
                                )
                            ))
                            fig_corr.update_layout(
                                height=max(300, len(valid_tks_corr) * 55),
                                margin=dict(l=0, r=0, t=10, b=0),
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(family='Inter', color='rgba(255,255,255,0.8)'),
                                xaxis=dict(side='bottom'),
                                yaxis=dict(autorange='reversed')
                            )
                            st.plotly_chart(fig_corr, use_container_width=True, config={'displayModeBar': False})
                            
                            # Interpretación automática
                            mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
                            upper_vals = corr_matrix.where(mask)
                            avg_corr = upper_vals.stack().mean()
                            max_pair = upper_vals.stack().idxmax()
                            max_val = upper_vals.stack().max()
                            
                            if avg_corr > 0.7:
                                st.warning(f"⚠️ **Correlación media alta ({avg_corr:.2f}).** Tu cartera está muy concentrada en activos que se mueven juntos. Si uno cae, probablemente caerán todos. El par más correlacionado es **{max_pair[0]}/{max_pair[1]}** ({max_val:.2f}).")
                            elif avg_corr > 0.4:
                                st.info(f"ℹ️ **Correlación media moderada ({avg_corr:.2f}).** Diversificación aceptable pero mejorable. El par más correlacionado es **{max_pair[0]}/{max_pair[1]}** ({max_val:.2f}). Considera añadir activos de sectores distintos.")
                            else:
                                st.success(f"✅ **Correlación media baja ({avg_corr:.2f}).** Excelente diversificación. Tus activos se mueven de forma independiente, lo que reduce el riesgo global de la cartera.")
                    except Exception as e:
                        st.error(f"Error al calcular correlaciones: {e}")
            else:
                st.info("Añade al menos 2 activos a la cartera para ver la matriz de correlación.")
            
            st.divider()
            st.markdown("#### 🎯 Calculadora de Objetivos de Cartera")
            target_port = st.number_input("¿A qué valor te gustaría que llegase tu cartera entera a final de año?", min_value=0.0, value=float(total_value)*1.15, step=10.0)

            if st.button("🎲 Ejecutar Simulación Institucional (Cholesky & Fat Tails)", type="primary", use_container_width=True):
                with st.spinner("Calculando matriz de covarianza y simulando 1.000 futuros globales..."):
                    try:
                        port_hists = {}
                        valid_tks = [tk for tk, val in port.items() if (val.get("shares", 0) if isinstance(val, dict) else val) > 0]
                        if valid_tks:
                            h_d = yf.download(valid_tks, period="1y", progress=False)
                            if 'Close' in h_d:
                                close_data = h_d['Close']
                                if len(valid_tks) == 1:
                                    port_hists[valid_tks[0]] = close_data.dropna()
                                else:
                                    for tk in valid_tks:
                                        if tk in close_data.columns:
                                            port_hists[tk] = close_data[tk].dropna()
                                    
                        if len(port_hists) > 0:
                            df_p = pd.DataFrame(port_hists).ffill().bfill()
                            if not df_p.empty:
                                daily_returns = df_p.pct_change().dropna()
                                num_assets = len(df_p.columns)
                                
                                # Matrices de Covarianza
                                cov_matrix = daily_returns.cov().values
                                mu_array = daily_returns.mean().values
                                
                                # Pesos actuales exactos
                                sim_total_val = sum([(port[tk].get("shares", 0) if isinstance(port[tk], dict) else port[tk]) * df_p[tk].iloc[-1] for tk in df_p.columns])
                                weights = np.array([((port[tk].get("shares", 0) if isinstance(port[tk], dict) else port[tk]) * df_p[tk].iloc[-1]) / sim_total_val for tk in df_p.columns])
                            
                                days = 252
                                sims = 1000
                                paths_p = np.zeros((days, sims))
                                paths_p[0] = total_value
                                
                                try:
                                    # Descomposición de Cholesky para correlacionar los activos
                                    L = np.linalg.cholesky(cov_matrix)
                                    for t in range(1, days):
                                        # Variables aleatorias t-Student independientes (Fat Tails)
                                        Z = np.random.standard_t(df=4, size=(sims, num_assets)) / np.sqrt(2)
                                        # Aplicamos Cholesky para correlacionarlas
                                        correlated_rets = mu_array + Z.dot(L.T)
                                        # Retorno diario de la cartera según los pesos
                                        port_day_ret = correlated_rets.dot(weights)
                                        paths_p[t] = paths_p[t-1] * (1 + port_day_ret)
                                except:
                                    # Fallback si Cholesky falla (ej. matriz singular o 1 solo activo)
                                    port_return = daily_returns.dot(weights)
                                    mu_p = port_return.mean()
                                    sigma_p = port_return.std()
                                    scale_factor = sigma_p / np.sqrt(2)
                                    for t in range(1, days):
                                        rand_rets = (np.random.standard_t(df=4, size=sims) * scale_factor) + mu_p
                                        paths_p[t] = paths_p[t-1] * (1 + rand_rets)
                                
                            final_p = paths_p[-1]
                            p5_p = np.percentile(final_p, 5)
                            p95_p = np.percentile(final_p, 95)
                            prob_gain = (final_p > total_value).mean() * 100
                            prob_loss_20 = (final_p < (total_value * 0.80)).mean() * 100
                            prob_target = (final_p >= target_port).mean() * 100
                            
                            st.markdown(f"**Probabilidad de alcanzar ${target_port:,.2f}:** <span style='color:#d4af37; font-size:1.2rem; font-weight:bold;'>{prob_target:.1f}%</span>", unsafe_allow_html=True)
                            st.divider()
                            
                            st.markdown(f"#### 🔮 Proyección a 1 Año (Diversificada y Correlacionada)")
                            c_m1, c_m2, c_m3 = st.columns(3)
                            c_m1.metric("Prob. Ganancia (1 Año)", f"{prob_gain:.1f}%", help="Porcentaje de los 1.000 futuros en los que cerrarías el año con dinero extra.")
                            c_m2.metric("Prob. Caída Severa (>20%)", f"{prob_loss_20:.1f}%", help="Tail Risk de la Cartera. Probabilidad de sufrir un crash fuerte.")
                            c_m3.metric("Valor Promedio Esperado", f"${np.mean(final_p):,.2f}", help="La media matemática de los 1.000 escenarios.")
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            c_m4, c_m5 = st.columns(2)
                            c_m4.metric("Peor Escenario (Percentil 5)", f"${p5_p:,.2f}", help="En el 95% de los escenarios, ganarás más dinero que esto.")
                            c_m5.metric("Mejor Escenario (Percentil 95)", f"${p95_p:,.2f}", help="Escenario hiper-optimista (solo un 5% de probabilidad de superarlo).")
                            
                            c_pg1, c_pg2 = st.columns([2, 1])
                            with c_pg1:
                                fig_pmc = go.Figure()
                                for i in range(50):
                                    fig_pmc.add_trace(go.Scatter(y=paths_p[:, i], mode='lines', line=dict(color='rgba(212,175,55,0.25)', width=1), showlegend=False))
                                fig_pmc.add_hline(y=total_value, line_dash="dot", line_color="white", annotation_text="Valor Actual")
                                fig_pmc.add_hline(y=target_port, line_dash="dash", line_color="#00C853", annotation_text="Objetivo")
                                fig_pmc.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"))
                                st.plotly_chart(fig_pmc, use_container_width=True, config={'displayModeBar': False})
                                
                            with c_pg2:
                                fig_phist = go.Figure(data=[go.Violin(y=final_p, side='positive', line_color='#d4af37', fillcolor='rgba(212,175,55,0.4)', showlegend=False, points=False, width=3)])
                                fig_phist.add_hline(y=total_value, line_dash="dot", line_color="white")
                                fig_phist.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_visible=False, font=dict(family="Inter"))
                                st.plotly_chart(fig_phist, use_container_width=True, config={'displayModeBar': False})
                            
                            verdicto = "riesgo aceptable" if prob_loss_20 < 15 else "riesgo MUY ALTO"
                            st.markdown(f"""
                            <div class='glow-hover' style='background: rgba(128,128,128,0.05); border: 1px solid rgba(212,175,55,0.3); border-radius: 8px; padding: 20px;'>
                                <h4 style='color: #d4af37; margin-top: 0;'>🤖 Interpretación de Cartera de Á.L.V.A.R.O.</h4>
                                <p style='font-size: 0.9rem; line-height: 1.5; margin-bottom: 0;'>
                                Al simular la matriz de covarianza completa (evaluando cómo interactúan tus activos entre sí), tienes un <b>{prob_gain:.1f}% de posibilidades</b> de terminar el año ganando dinero. 
                                Tu "red de seguridad" (el peor escenario estadístico) dejaría tu cartera en <b>${p5_p:,.2f}</b>, mientras que el techo optimista la dispararía a <b>${p95_p:,.2f}</b>. 
                                Tienes exactamente un <b>{prob_target:.1f}%</b> de probabilidad de llegar a tu objetivo de ${target_port:,.2f}. 
                                Consideramos que es una cartera de <b>{verdicto}</b> ante caídas extremas.
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error en simulación: {e}")


    else:
        st.info("Tu cartera está vacía. Añade tu primera acción arriba.")

# ── Tab 9: Noticias ──
with tab_news:
    st.markdown("### 📰 Flujo de Noticias")
    st.markdown("<p style='font-size:0.9rem; opacity:0.7; margin-top:-10px;'>Últimas noticias publicadas que pueden afectar a la cotización a corto plazo.</p>", unsafe_allow_html=True)
    
    if not news_data:
        st.info("No se encontraron noticias recientes para este activo en Yahoo Finance.")
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        for article in news_data:
            title = article.get("title", "Sin Título")
            publisher = article.get("publisher", "Fuente Desconocida")
            pub_time = article.get("time", 0)
                
            dt_str = datetime.fromtimestamp(pub_time).strftime('%d %b %Y, %H:%M') if pub_time else "Reciente"
            
            st.markdown(f"""
            <div class="glow-hover" style="background: rgba(128,128,128,0.05); border: 1px solid rgba(128,128,128,0.2); border-left: 4px solid #d4af37; padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                <h4 style="margin: 0 0 10px 0; font-size: 1.15rem; font-weight: 600;">{title}</h4>
                <div style="font-size: 0.85rem; opacity: 0.7;">
                    <span>🏢 <b>{publisher}</b> · 🕒 {dt_str}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ── Tab 10: Institucional / Insiders ──
with tab_inst:
    st.markdown("### 🏦 Flujo de Dinero Institucional")
    st.markdown("<p style='font-size:0.9rem; opacity:0.7; margin-top:-10px;'>¿Qué están haciendo las grandes 'Manos Fuertes' (Vanguard, Blackrock) y los propios directivos de la empresa?</p>", unsafe_allow_html=True)
    
    col_inst1, col_inst2 = st.columns(2)
    
    with col_inst1:
        st.markdown("#### 🏛️ Principales Accionistas Institucionales")
        if not inst_data.empty and "Holder" in inst_data.columns:
            # Formatear tabla
            df_inst_show = inst_data.copy()
            if "pctChange" in df_inst_show.columns:
                df_inst_show["pctChange"] = (df_inst_show["pctChange"] * 100).apply(lambda x: f"+{x:.2f}%" if x > 0 else f"{x:.2f}%")
            if "Value" in df_inst_show.columns:
                df_inst_show["Value"] = df_inst_show["Value"].apply(lambda x: fmt_big(x) if isinstance(x, (int, float)) else x)
                
            st.dataframe(df_inst_show[["Holder", "Shares", "Value", "pctChange"]].head(10), use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos recientes de tenencia institucional.")
            
    with col_inst2:
        st.markdown("#### 👔 Operaciones de Directivos (Insiders)")
        if not insd_data.empty:
            df_insd_show = insd_data.copy()
            # Limpiar columnas irrelevantes
            cols_to_show = []
            if "Insider" in df_insd_show.columns: cols_to_show.append("Insider")
            if "Position" in df_insd_show.columns: cols_to_show.append("Position")
            if "Transaction" in df_insd_show.columns or "Text" in df_insd_show.columns:
                cols_to_show.append("Transaction" if "Transaction" in df_insd_show.columns else "Text")
            if "Shares" in df_insd_show.columns: cols_to_show.append("Shares")
            
            if cols_to_show:
                st.dataframe(df_insd_show[cols_to_show].head(15), use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_insd_show.head(15), use_container_width=True, hide_index=True)
        else:
            st.info("No se han registrado operaciones de insiders recientemente.")


# ── Export PDF / HTML ──
if ticker and not income.empty:
    st.sidebar.divider()
    st.sidebar.markdown("### 📥 Generar Informe")
    
    # Calculate robust metrics for export report
    e_net_income = income.iloc[:, 0].get("Net Income", 0) if not income.empty else 0
    e_ebitda = income.iloc[:, 0].get("EBITDA", 0) if not income.empty else 0
    e_total_debt, e_cash, e_equity = 0, 0, mkt_cap
    if not balance.empty:
        for k in ["Total Debt", "Long Term Debt"]:
            if k in balance.index: e_total_debt = balance.iloc[:, 0].get(k, 0); break
        for k in ["Cash And Cash Equivalents"]:
            if k in balance.index: e_cash = balance.iloc[:, 0].get(k, 0); break
        for k in ["Stockholders Equity"]:
            if k in balance.index: e_equity = balance.iloc[:, 0].get(k, 0); break
            
    e_net_debt = e_total_debt - e_cash
    e_ev = mkt_cap + e_net_debt
    e_eps = e_net_income / shares_out if shares_out and e_net_income else 0
    e_bvps = e_equity / shares_out if shares_out else 0
    e_graham = np.sqrt(22.5 * e_eps * e_bvps) if e_eps > 0 and e_bvps > 0 else e_bvps
    e_upside = (e_graham - price) / price if price else 0

    # Calcular Piotroski para el export
    _exp_pio = 0
    _ni_c = income.iloc[:, 0].get("Net Income", 0) if not income.empty and len(income.columns) > 0 else 0
    _ta_c = 1
    if not balance.empty and "Total Assets" in balance.index:
        _ta_c = balance.iloc[:, 0].get("Total Assets", 1) or 1
    if _ni_c and _ta_c and (_ni_c / _ta_c) > 0: _exp_pio += 1
    _cfo_c = 0
    if not cashflow.empty:
        for _k in ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"]:
            if _k in cashflow.index: _cfo_c = cashflow.iloc[:, 0].get(_k, 0) or 0; break
    if _cfo_c > 0: _exp_pio += 1
    if _cfo_c > _ni_c: _exp_pio += 1
    _exp_pio_label = "Excelente" if _exp_pio >= 3 else "Aceptable" if _exp_pio >= 2 else "Débil"
    
    html_export = f"""
    <html><head><meta charset="utf-8"><title>Informe {ticker}</title>
    <style>body{{font-family:'Inter','Arial',sans-serif;background:#0a0b10;color:#e0e0e0;padding:40px;max-width:800px;margin:0 auto;}}h1,h2,h3{{color:#d4af37;}}hr{{border-color:rgba(212,175,55,0.3);}}table{{width:100%;border-collapse:collapse;margin:20px 0;}}td,th{{padding:10px;text-align:left;border-bottom:1px solid rgba(128,128,128,0.2);}}th{{color:#d4af37;font-size:0.85rem;text-transform:uppercase;letter-spacing:1px;}}.badge{{display:inline-block;padding:4px 12px;border-radius:20px;font-weight:700;font-size:0.85rem;}}</style>
    </head><body>
        <h1>📊 Informe Institucional: {name} ({ticker})</h1>
        <p style="opacity:0.6;">Sector: {sector} · {industry} · {country}</p>
        <hr>
        <table>
            <tr><th>Métrica</th><th>Valor</th></tr>
            <tr><td>Precio Actual</td><td><b>{sym}{price:,.2f}</b></td></tr>
            <tr><td>Valor Justo (Graham)</td><td><b>{sym}{e_graham:,.2f}</b></td></tr>
            <tr><td>Potencial Estimado</td><td style="color:{color_up if e_upside>0 else color_down};"><b>{abs(e_upside)*100:.1f}% {'ALCISTA' if e_upside>0 else 'BAJISTA'}</b></td></tr>
            <tr><td>PER</td><td>{mkt_cap/e_net_income if e_net_income and e_net_income > 0 else 0:.1f}x</td></tr>
            <tr><td>EV/EBITDA</td><td>{e_ev/e_ebitda if e_ebitda and e_ebitda > 0 else 0:.1f}x</td></tr>
            <tr><td>Dividendo</td><td>{div_str}</td></tr>
            <tr><td>Capitalización</td><td>{fmt_big(mkt_cap)}</td></tr>
            <tr><td>Piotroski F-Score (Parcial)</td><td><b>{_exp_pio}/3</b> — {_exp_pio_label}</td></tr>
        </table>
        <hr>
        <p style="opacity:0.4; font-size:0.8rem; margin-top:40px;">Generado por motor de Inteligencia Financiera Á.L.V.A.R.O. · ValuationPro · {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
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
    
    e_revenue = income.iloc[:, 0].get("Total Revenue", 0) if not income.empty else 0
    _ai_name = info.get("longName") or info.get("shortName") or ticker
    margin_text = "márgenes muy rentables" if (e_ebitda/e_revenue if e_revenue and e_revenue>0 else 0) > 0.20 else "márgenes algo ajustados"
    val_text = "con descuento frente a su precio justo (potencial alcista)" if e_upside > 0 else "con prima (algo cara frente a su valor teórico)"
    tech_text = "en tendencia alcista a corto plazo" if (hist['Close'].iloc[-1] > hist['SMA_50'].iloc[-1] if not hist.empty and 'SMA_50' in hist else True) else "en tendencia bajista"
    
    ai_summary = f"**{_ai_name}** opera en el sector de *{sector}*. Actualmente muestra {margin_text} y, según nuestro análisis conservador, la acción cotiza {val_text}. Desde el punto de vista técnico, se encuentra {tech_text}. "
    
    if e_upside > 0.15:
        ai_summary += "💡 **Veredicto:** Oportunidad clara de inversión a largo plazo según fundamentales."
    elif e_upside < -0.15:
        ai_summary += "⚠️ **Veredicto:** Precaución. Riesgo alto de sobrevaloración fundamental."
    else:
        ai_summary += "⚖️ **Veredicto:** Valoración justa. Buscar puntos de entrada tácticos mediante el gráfico."

    st.sidebar.info(ai_summary)

# ── Footer Profesional ──
st.divider()
st.markdown(f"""
<div style='text-align:center; padding:30px 0 20px 0; opacity:0.6;'>
    <p style='font-family:Outfit,sans-serif; font-size:0.9rem; font-weight:600; letter-spacing:2px; margin-bottom:5px;'>
        <span style='color:#d4af37;'>Valuation</span>Pro
    </p>
    <p style='font-size:0.7rem; margin:3px 0; opacity:0.7;'>Motor de Análisis: Á.L.V.A.R.O. v2.0 · Datos: Yahoo Finance</p>
    <p style='font-size:0.65rem; margin:3px 0; opacity:0.5; max-width:700px; margin-left:auto; margin-right:auto;'>⚠️ Aviso legal: La información proporcionada por ValuationPro tiene carácter exclusivamente informativo y educativo. En ningún caso constituye asesoramiento financiero, recomendación de inversión ni oferta de compra o venta de valores. Toda inversión en mercados financieros conlleva riesgo de pérdida parcial o total del capital invertido. Consulte a un profesional cualificado antes de tomar decisiones de inversión.</p>
    <p style='font-size:0.6rem; margin:8px 0 0 0; opacity:0.35;'>© {datetime.now().year} ValuationPro · Herramienta de análisis con fines educativos</p>
</div>
""", unsafe_allow_html=True)
