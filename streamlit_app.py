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
ticker_input = st.sidebar.text_input(" ", placeholder="Escribe ticker o nombre...", key="ticker_input", label_visibility="collapsed")

if ticker_input and len(ticker_input) > 1:
    search_res = search_ticker_by_name(ticker_input)
    if search_res and search_res[0]["symbol"].upper() != ticker_input.upper():
        st.sidebar.markdown("<p style='font-size:0.8rem; opacity:0.7; margin-bottom:5px; margin-top:-10px;'>¿Querías decir...?</p>", unsafe_allow_html=True)
        for r in search_res:
            st.sidebar.button(f"**{r['symbol']}** · {r['name'][:22]}", key=f"src_{r['symbol']}", on_click=set_ticker, args=(r['symbol'],), use_container_width=True)
        st.sidebar.divider()
        st.stop()

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
def fetch_data_v3(t, per, intv):
    # 1. Histórico mediante yf.download (Mucho más resistente a baneos en la nube)
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
    
    # 3. Info completa (Suele dar error de Rate Limit, si falla no pasa nada)
    try: 
        i_full = stock.info
        if i_full:
            # Filtrar dict para evitar objetos raros
            for k, v in i_full.items():
                if isinstance(v, (int, float, str, bool)):
                    inf[k] = v
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
    
    return {"info": inf, "income": inc if inc is not None else pd.DataFrame(), "balance": bal if bal is not None else pd.DataFrame(), "cashflow": cf if cf is not None else pd.DataFrame(), "hist": h}, None

with st.spinner(f"Cargando datos de **{ticker}**..."):
    try:
        data_cache, err = fetch_data_v3(ticker, chart_period, chart_interval)
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

div_rate = info.get("dividendRate") or info.get("trailingAnnualDividendRate", 0)
if div_rate and price and price > 0:
    div_yield = div_rate / price
else:
    div_yield = info.get("dividendYield") or info.get("trailingAnnualDividendYield", 0)
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
tab_chart, tab_ta, tab_fin, tab_val, tab_thesis, tab_backtest, tab_mc, tab_port = st.tabs([
    "📊 Gráfico", "🕯️ Análisis Técnico", "📈 Tendencias", "💰 Centro de Valoración", "📝 Tesis", "🤖 Backtest", "🎲 Monte Carlo", "💼 Mi Cartera"
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


# ── Tab 4: Centro de Valoración ──
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
            calc_growth = max(0.02, min((fcfs_pos[0] / fcfs_pos[-1]) ** (1 / (len(fcfs_pos) - 1)) - 1, 0.25))
        else:
            calc_growth = 0.08

        calc_terminal_g = 0.025

        col_w, col_g, col_tg = st.columns(3)
        user_wacc = col_w.slider("WACC (%)", min_value=2.0, max_value=25.0, value=float(calc_wacc*100), step=0.1, help="Coste Promedio Ponderado de Capital.") / 100.0
        user_growth = col_g.slider("Crecimiento Corto Plazo (%)", min_value=-15.0, max_value=50.0, value=float(calc_growth*100), step=0.5) / 100.0
        user_term_g = col_tg.slider("Crecimiento Terminal (%)", min_value=0.0, max_value=6.0, value=float(calc_terminal_g*100), step=0.1) / 100.0

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
            st.markdown("<p style='font-size:0.9rem; opacity:0.7; margin-bottom: 20px;'>Fórmula revisada de Benjamin Graham para valorar empresas estables: <b>V = (EPS × (8.5 + 2g) × 4.4) / Y</b></p>", unsafe_allow_html=True)
            col_g_eps, col_g_g, col_g_y = st.columns(3)
            
            # Estimate historical growth for Graham
            fcfs_pos = [f for f in fcf_row if f and f > 0]
            if len(fcfs_pos) >= 2:
                calc_g_graham = max(0.02, min((fcfs_pos[0] / fcfs_pos[-1]) ** (1 / (len(fcfs_pos) - 1)) - 1, 0.25))
            else:
                calc_g_graham = 0.05
                
            g_g = col_g_g.slider("Crecimiento a 5 años (g) [%]", 0.0, 30.0, float(calc_g_graham*100))
            g_y = col_g_y.slider("Rendimiento Bono Corporativo AAA (Y) [%]", 1.0, 10.0, float(risk_free*100 + 1.0))
            
            graham_val = (eps * (8.5 + 2 * (g_g)) * 4.4) / g_y
            upside_g = (graham_val - price) / price if price else 0
            
            c_g1, c_g2 = st.columns(2)
            c_g1.metric("Valor Intrínseco de Graham", f"{sym}{graham_val:,.2f}")
            c_g2.metric("Potencial / Margen Seguridad", f"{upside_g*100:.1f}%")
            
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
            val_txt = f"⚖️ **Margen de Seguridad:** Excelente. El mercado está deprimiendo la acción irracionalmente. Cotizando a un PER de {pe:.1f}x y con un descuento del {thesis_upside*100:.1f}%, el riesgo de pérdida a largo plazo es bajo."
        elif thesis_upside > 0:
            val_txt = f"⚖️ **Margen de Seguridad:** Aceptable. La acción cotiza por debajo de su valor intrínseco teórico (según Graham), pero no hay un gran margen de error."
        else:
            val_txt = f"⚖️ **Margen de Seguridad:** Inexistente. El mercado asume la perfección pagando un PER de {pe:.1f}x. Cualquier fallo en su plan de negocio futuro provocará una corrección severa."
            
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
    
    c_add1, c_add2, c_add3 = st.columns([2, 1, 1])
    port_choice = c_add1.selectbox("Activo", options=all_options, index=None, placeholder="-- Buscar en lista global --", label_visibility="collapsed")
    custom_add = c_add1.text_input("Ticker manual", placeholder="...o escribe un ticker manual (Ej: TSLA)", key="custom_tk", label_visibility="collapsed")
    
    port_shares = c_add2.number_input("Acciones a comprar", min_value=0.0, step=1.0, value=1.0, key="p_sh", label_visibility="collapsed")
    
    if c_add3.button("➕ Añadir a Cartera", use_container_width=True, type="primary"):
        if custom_add and custom_add.strip():
            tk_add = custom_add.strip().upper()
            st.session_state["portfolio"][tk_add] = port_shares
            st.rerun()
        elif port_choice:
            tk_add = port_choice.split(" - ")[0].strip().upper()
            st.session_state["portfolio"][tk_add] = port_shares
            st.rerun()
            
    if c_add3.button("🗑️ Vaciar Cartera", use_container_width=True):
        st.session_state["portfolio"] = {}
        st.rerun()
        
    st.markdown("</div>", unsafe_allow_html=True)
            
    port = st.session_state["portfolio"]
    if port:
        port_data = []
        total_value = 0
        
        with st.spinner("Sincronizando con mercado en tiempo real..."):
            for t, shares in list(port.items()):
                if shares > 0:
                    try:
                        tk_obj = yf.Ticker(t)
                        p_info = tk_obj.fast_info
                        p_price = p_info.last_price
                        val = p_price * shares
                        total_value += val
                        try:
                            name = tk_obj.info.get("shortName", t)
                        except:
                            name = t
                        port_data.append({"Ticker": t, "Empresa": name, "Acciones": shares, "Precio": p_price, "Valor Total": val})
                    except: pass
                else:
                    del st.session_state["portfolio"][t]
                
        if port_data:
            port_data = sorted(port_data, key=lambda x: x["Valor Total"], reverse=True)
            for d in port_data: d["Peso %"] = (d["Valor Total"] / total_value) * 100
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='glow-hover' style='background: linear-gradient(145deg, rgba(20,20,20,1) 0%, rgba(30,30,30,1) 100%); border: 1px solid rgba(212,175,55,0.4); border-radius: 15px; padding: 35px; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.6); margin-bottom: 25px;'>
                <p style='font-family: "Outfit", sans-serif; font-size: 0.95rem; letter-spacing: 3px; text-transform: uppercase; color: #d4af37; margin: 0; opacity: 0.9;'>Patrimonio Líquido Total</p>
                <h1 style='font-family: "JetBrains Mono", monospace; font-size: 4.8rem; font-weight: 300; margin: 5px 0; color: #ffffff; text-shadow: 0 0 25px rgba(212,175,55,0.25); letter-spacing: -2px;'>
                    <span style='color: #d4af37; opacity: 0.8;'>$</span>{total_value:,.2f}
                </h1>
                <p style='font-size: 0.8rem; opacity: 0.5; margin: 0; letter-spacing: 1px;'>ACTUALIZADO EN TIEMPO REAL</p>
            </div>
            """, unsafe_allow_html=True)
            
            df_port = pd.DataFrame(port_data).set_index("Ticker")
            
            c_port1, c_port2 = st.columns([1.3, 1])
            with c_port1:
                st.markdown("<h4 style='color: #d4af37;'>📑 Desglose de Activos</h4>", unsafe_allow_html=True)
                st.dataframe(
                    df_port[["Empresa", "Acciones", "Precio", "Valor Total", "Peso %"]],
                    column_config={
                        "Precio": st.column_config.NumberColumn("Precio", format="$%.2f"),
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
            
            st.divider()
            if st.button("🎲 Simulación Monte Carlo Global de Cartera", type="primary", use_container_width=True):
                with st.spinner("Calculando matriz de covarianza y simulando 1.000 futuros globales..."):
                    try:
                        port_hists = {}
                        valid_tks = [tk for tk, sh in port.items() if sh > 0]
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
                            prob_gain = (final_p > total_value).mean() * 100
                            prob_loss_20 = (final_p < (total_value * 0.80)).mean() * 100
                            
                            st.markdown(f"#### 🔮 Proyección a 1 Año (Diversificada)")
                            c_m1, c_m2, c_m3 = st.columns(3)
                            c_m1.metric("Prob. Ganancia (1 Año)", f"{prob_gain:.1f}%", help="Porcentaje de los 1.000 futuros en los que cerrarías el año con dinero extra.")
                            c_m2.metric("Prob. Caída Severa (>20%)", f"{prob_loss_20:.1f}%", help="Tail Risk de la Cartera. Probabilidad de sufrir un crash fuerte.")
                            c_m3.metric("Valor Promedio Esperado", f"${np.mean(final_p):,.2f}", help="La media matemática de los 1.000 escenarios.")
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            c_m4, c_m5 = st.columns(2)
                            c_m4.metric("Peor Escenario (Percentil 5)", f"${p5_p:,.2f}", help="En el 95% de los escenarios, ganarás más dinero que esto.")
                            c_m5.metric("Mejor Escenario (Percentil 95)", f"${p95_p:,.2f}", help="Escenario hiper-optimista (solo un 5% de probabilidad de superarlo).")
                            
                            fig_pmc = go.Figure()
                            for i in range(50):
                                fig_pmc.add_trace(go.Scatter(y=paths_p[:, i], mode='lines', line=dict(color='rgba(212,175,55,0.25)', width=1), showlegend=False))
                            fig_pmc.add_hline(y=total_value, line_dash="dot", line_color="white", annotation_text="Valor Actual")
                            fig_pmc.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"))
                            st.plotly_chart(fig_pmc, use_container_width=True, config={'displayModeBar': False})
                            
                            verdicto = "riesgo aceptable" if prob_loss_20 < 15 else "riesgo MUY ALTO"
                            st.markdown(f"""
                            <div class='glow-hover' style='background: rgba(128,128,128,0.05); border: 1px solid rgba(212,175,55,0.3); border-radius: 8px; padding: 20px;'>
                                <h4 style='color: #d4af37; margin-top: 0;'>🤖 Interpretación de Cartera de Á.L.V.A.R.O.</h4>
                                <p style='font-size: 0.9rem; line-height: 1.5; margin-bottom: 0;'>
                                Al combinar la volatilidad de todos tus activos, tienes un <b>{prob_gain:.1f}% de posibilidades</b> de terminar el año ganando dinero. 
                                Tu "red de seguridad" (el peor escenario estadístico probable) dejaría tu cartera en <b>${p5_p:,.2f}</b>, mientras que el techo optimista la dispararía a <b>${p95_p:,.2f}</b>. 
                                Dado que hay un {prob_loss_20:.1f}% de probabilidad de sufrir una caída drástica (>20%), consideramos que es una cartera de <b>{verdicto}</b>.
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
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

    html_export = f"""
    <html><head><meta charset="utf-8"><title>Informe {ticker}</title>
    <style>body{{font-family:'Arial',sans-serif;background:#0a0b10;color:#fff;padding:40px;}}h1,h2,h3{{color:#d4af37;}}</style>
    </head><body>
        <h1>Informe de Valoración Profesional: {name} ({ticker})</h1>
        <h2>Precio Actual en Mercado: {sym}{price:,.2f}</h2>
        <h2>Valor Justo Defensivo (Graham): {sym}{e_graham:,.2f}</h2>
        <h3 style="color:{color_up if e_upside>0 else color_down};">POTENCIAL ESTIMADO: {abs(e_upside)*100:.1f}% {'ALCISTA' if e_upside>0 else 'BAJISTA'}</h3>
        <hr>
        <h3>Múltiplos Clave</h3>
        <ul>
            <li>PER (Price/Earnings): {mkt_cap/e_net_income if e_net_income and e_net_income > 0 else 0:.1f}x</li>
            <li>EV/EBITDA: {e_ev/e_ebitda if e_ebitda and e_ebitda > 0 else 0:.1f}x</li>
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
    
    e_revenue = income.iloc[:, 0].get("Total Revenue", 0) if not income.empty else 0
    margin_text = "márgenes muy rentables" if (e_ebitda/e_revenue if e_revenue and e_revenue>0 else 0) > 0.20 else "márgenes algo ajustados"
    val_text = "con descuento frente a su precio justo (potencial alcista)" if e_upside > 0 else "con prima (algo cara frente a su valor teórico)"
    tech_text = "en tendencia alcista a corto plazo" if (hist['Close'].iloc[-1] > hist['SMA_50'].iloc[-1] if not hist.empty and 'SMA_50' in hist else True) else "en tendencia bajista"
    
    ai_summary = f"**{name}** opera en el sector de *{sector}*. Actualmente muestra {margin_text} y, según nuestro análisis conservador, la acción cotiza {val_text}. Desde el punto de vista técnico, se encuentra {tech_text}. "
    
    if e_upside > 0.15:
        ai_summary += "💡 **Veredicto:** Oportunidad clara de inversión a largo plazo según fundamentales."
    elif e_upside < -0.15:
        ai_summary += "⚠️ **Veredicto:** Precaución. Riesgo alto de sobrevaloración fundamental."
    else:
        ai_summary += "⚖️ **Veredicto:** Valoración justa. Buscar puntos de entrada tácticos mediante el gráfico."

    st.sidebar.info(ai_summary)
