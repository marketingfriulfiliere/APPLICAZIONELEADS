# -*- coding: utf-8 -*-
"""
FRIUL FILIERE LEAD ENGINE
Piattaforma di Lead Generation, Profilazione, Outreach Commerciale B2B
e Integrazione Ufficiale Registro Imprese / InfoCheck (Abbrevia X).

Unico file app.py - Streamlit
Avvio:
    streamlit run app.py
"""

import io
import json
import random
from datetime import datetime, timedelta

import pandas as pd
import requests
import streamlit as st
from fpdf import FPDF


# =========================================================================
# CONFIGURAZIONE PAGINA
# =========================================================================

st.set_page_config(
    page_title="Friul Filiere Lead Engine",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================================
# TEMA / CSS
# =========================================================================

CUSTOM_CSS = """
<style>
:root {
    --blu-scuro: #0E1F3D;
    --rosso: #C8102E;
    --grigio-metal: #B0B7BD;
    --grigio-chiaro: #F2F3F5;
}

.stApp {
    background-color: #F5F6F8;
}

section[data-testid="stSidebar"] {
    background-color: var(--blu-scuro);
}
section[data-testid="stSidebar"] * {
    color: #EAECEF !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-size: 0.95rem;
}

h1, h2, h3 {
    color: var(--blu-scuro);
    font-weight: 800;
}

.ffe-header {
    background: linear-gradient(90deg, var(--blu-scuro) 0%, #16305e 100%);
    padding: 22px 30px;
    border-radius: 10px;
    border-left: 8px solid var(--rosso);
    margin-bottom: 22px;
}
.ffe-header h1 {
    color: white !important;
    margin: 0;
    font-size: 1.9rem;
}
.ffe-header p {
    color: var(--grigio-metal) !important;
    margin: 4px 0 0 0;
    font-size: 0.95rem;
}

.ffe-card {
    background: white;
    border-radius: 10px;
    padding: 18px 20px;
    border: 1px solid #E1E4E8;
    border-top: 4px solid var(--rosso);
    box-shadow: 0 2px 6px rgba(14,31,61,0.06);
    margin-bottom: 14px;
}

.ffe-metric {
    background: var(--blu-scuro);
    color: white;
    border-radius: 10px;
    padding: 16px 18px;
    text-align: center;
}
.ffe-metric .val {
    font-size: 2rem;
    font-weight: 800;
    color: white;
}
.ffe-metric .lbl {
    font-size: 0.8rem;
    color: var(--grigio-metal);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.ffe-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    margin-right: 4px;
}
.ffe-badge-alta { background: var(--rosso); color: white; }
.ffe-badge-media { background: #E8A33D; color: white; }
.ffe-badge-bassa { background: var(--grigio-metal); color: var(--blu-scuro); }
.ffe-badge-info { background: var(--blu-scuro); color: white; }
.ffe-badge-abbrevia { background: #0070BA; color: white; }

.ffe-divider {
    border: none;
    border-top: 2px solid #E1E4E8;
    margin: 18px 0;
}

.stButton>button {
    background-color: var(--rosso);
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 700;
    padding: 0.5em 1.2em;
}
.stButton>button:hover {
    background-color: #a10c22;
    color: white;
}

div[data-testid="stMetricValue"] {
    color: var(--blu-scuro);
    font-weight: 800;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# =========================================================================
# COSTANTI E MAPPATURE
# =========================================================================

SETTORI = [
    "Automotive", "Medicale", "Edilizia", "Packaging alimentare",
    "Arredamento", "Elettrodomestici", "Serramenti", "Agricoltura",
    "Cavi e condotte", "Water management", "Arredo urbano", "Nautica",
]

PAESI = [
    "Italia", "Germania", "Francia", "Spagna", "Polonia", "Turchia",
    "Romania", "Paesi Bassi", "Stati Uniti", "Messico", "Brasile",
    "India", "Cina", "Vietnam", "Regno Unito", "Austria",
]

DIMENSIONI_AZIENDA = [
    "Micro (< 10 dip.)", "Piccola (10-49 dip.)",
    "Media (50-249 dip.)", "Grande (250+ dip.)",
]

LIVELLI_URGENZA = ["Alta", "Media", "Bassa"]
STATI_LEAD = ["Nuovo", "Contattato", "In trattativa", "Qualificato", "Perso"]

FIERE_SETTORE = [
    "K Fair - Düsseldorf (DE)", "Plast - Milano (IT)",
    "Fakuma - Friedrichshafen (DE)", "NPE - Orlando (USA)",
    "Chinaplas - Shenzhen (CN)", "Interplastica - Mosca (RU)",
    "Plastpol - Kielce (PL)", "Feiplastic - San Paolo (BR)",
]

TECNOLOGIE_FRIUL_FILIERE = [
    "Linee di estrusione PVC per profili finestra",
    "Linee di coestrusione multistrato",
    "Sistemi di calibrazione e raffreddamento sottovuoto",
    "Linee di estrusione tubi corrugati e lisci",
    "Impianti per compositi legno-plastica (WPC)",
    "Linee monofilamento e reti estruse",
    "Sistemi downstream (taglio, impilamento, imballo automatico)",
    "Automazione e retrofit Industry 4.0 per linee di estrusione",
    "Teste e stampi per profili tecnici complessi",
]

MAPPA_TECNOLOGIA_SETTORE = {
    "Automotive": "Linee di coestrusione multistrato",
    "Medicale": "Linee monofilamento e reti estruse",
    "Edilizia": "Linee di estrusione PVC per profili finestra",
    "Packaging alimentare": "Sistemi downstream (taglio, impilamento, imballo automatico)",
    "Arredamento": "Impianti per compositi legno-plastica (WPC)",
    "Elettrodomestici": "Teste e stampi per profili tecnici complessi",
    "Serramenti": "Linee di estrusione PVC per profili finestra",
    "Agricoltura": "Linee di estrusione tubi corrugati e lisci",
    "Cavi e condotte": "Linee di estrusione tubi corrugati e lisci",
    "Water management": "Sistemi di calibrazione e raffreddamento sottovuoto",
    "Arredo urbano": "Impianti per compositi legno-plastica (WPC)",
    "Nautica": "Automazione e retrofit Industry 4.0 per linee di estrusione",
}

SETTORE_QUERY_PLACES = {
    "Automotive": "plastic injection molding automotive supplier",
    "Medicale": "medical plastic components manufacturer",
    "Edilizia": "PVC profile extrusion manufacturer",
    "Packaging alimentare": "plastic packaging manufacturer food",
    "Arredamento": "plastic furniture components manufacturer",
    "Elettrodomestici": "plastic components manufacturer appliances",
    "Serramenti": "PVC window profile manufacturer",
    "Agricoltura": "plastic pipe manufacturer irrigation",
    "Cavi e condotte": "plastic pipe extrusion manufacturer",
    "Water management": "HDPE pipe manufacturer water",
    "Arredo urbano": "wood plastic composite manufacturer",
    "Nautica": "plastic composite manufacturer marine",
}

PREFISSI_AZIENDA = ["Euro", "Plast", "Poly", "Nord", "Tecno", "Global", "Alpha", "Master"]
SUFFISSI_AZIENDA = ["Plastics", "Profili", "Extrusion", "Kunststoff", "S.r.l.", "S.p.A."]
NOMI_CONTATTO = ["Marco Bianchi", "Julia Weber", "Pierre Dubois", "Elena Rossi", "John Smith"]
FONTI_NOTIZIA = ["Ampliamento stabilimento", "Nuova linea produttiva", "Aumento organico"]


# =========================================================================
# STATO DI SESSIONE
# =========================================================================

def init_session_state():
    if "leads" not in st.session_state:
        st.session_state.leads = []
    if "next_id" not in st.session_state:
        st.session_state.next_id = 1
    if "gemini_api_key" not in st.session_state:
        st.session_state.gemini_api_key = ""
    if "places_api_key" not in st.session_state:
        st.session_state.places_api_key = ""
    if "dossier_cache" not in st.session_state:
        st.session_state.dossier_cache = {}
    if "email_cache" not in st.session_state:
        st.session_state.email_cache = {}
    if "lotto_corrente" not in st.session_state:
        st.session_state.lotto_corrente = 1
    if "pagina" not in st.session_state:
        st.session_state.pagina = "Dashboard"

    # Credenziali e stato Abbrevia X
    if "abbrevia_env" not in st.session_state:
        st.session_state.abbrevia_env = "production"
    if "abbrevia_username" not in st.session_state:
        st.session_state.abbrevia_username = "e7875aee-98d6-4dec-ae2a-0bd1d6485150"
    if "abbrevia_password" not in st.session_state:
        st.session_state.abbrevia_password = "YmW8Q~xkPM6fBQViiN6ZT0SwvImSUnNp_F6wEb58"
    if "abbrevia_scope" not in st.session_state:
        st.session_state.abbrevia_scope = "api://api-internal.abbrevia.it/31b5b2be-eed3-4285-8ee8-497bc4e13f96"
    if "abbrevia_token" not in st.session_state:
        st.session_state.abbrevia_token = ""
    if "abbrevia_token_expires_at" not in st.session_state:
        st.session_state.abbrevia_token_expires_at = datetime.min
    if "infocheck_cache" not in st.session_state:
        st.session_state.infocheck_cache = {}


init_session_state()


# =========================================================================
# CLIENT API: ABBREVIA X (Registro Imprese & InfoCheck)
# =========================================================================

ABBREVIA_BASE_URL = "https://api.abbrevia.it"


def abbrevia_get_token():
    """Recupera o rinnova il JWT token per Abbrevia X."""
    now = datetime.now()
    if st.session_state.abbrevia_token and now < st.session_state.abbrevia_token_expires_at:
        return st.session_state.abbrevia_token, None

    url = f"{ABBREVIA_BASE_URL}/auth/token"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Environment": st.session_state.abbrevia_env,
    }
    payload = {
        "grant_type": "client_credentials",
        "username": st.session_state.abbrevia_username.strip(),
        "password": st.session_state.abbrevia_password.strip(),
        "scope": st.session_state.abbrevia_scope.strip(),
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        if resp.status_code != 200:
            return None, f"Errore Auth ({resp.status_code}): {resp.text}"
        data = resp.json().get("data", {})
        token = data.get("access_token")
        expires_in = int(data.get("expires_in", 3600))
        if not token:
            return None, "Token non presente nella risposta del server"

        st.session_state.abbrevia_token = token
        st.session_state.abbrevia_token_expires_at = now + timedelta(seconds=expires_in - 60)
        return token, None
    except Exception as exc:
        return None, f"Errore connessione ad Abbrevia: {exc}"


def abbrevia_search_company(ragione_sociale="", piva="", cf="", provincia="", rea=""):
    """Cerca aziende nel Registro Imprese ufficiale tramite Abbrevia X."""
    token, err = abbrevia_get_token()
    if err:
        return [], err

    url = f"{ABBREVIA_BASE_URL}/abbx/search-company-basic"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Environment": st.session_state.abbrevia_env,
        "Authorization": f"Bearer {token}",
    }

    body = {
        "page": {"pageNumber": 0, "pageSize": 25}
    }
    if piva.strip():
        body["partitaIVA"] = piva.strip()
    if cf.strip():
        body["codiceFiscale"] = cf.strip()
    if ragione_sociale.strip():
        body["ragioneSociale"] = ragione_sociale.strip()
    if provincia.strip() and rea.strip():
        body["provinciaCCIAA"] = provincia.strip().upper()
        body["numeroREA"] = rea.strip()

    try:
        resp = requests.post(url, json=body, headers=headers, timeout=20)
        if resp.status_code == 404:
            return [], "Nessuna azienda trovata con i parametri forniti."
        if resp.status_code != 200:
            return [], f"Errore {resp.status_code}: {resp.text}"

        risposta = resp.json()
        dati = risposta.get("data", {})
        content = dati.get("content", [])
        return content, None
    except Exception as exc:
        return [], f"Errore di rete durante la ricerca: {exc}"


def abbrevia_get_infocheck(piva_or_cf):
    """Richiede la scheda InfoCheck completa (bilanci, esponenti, dati occupazionali)."""
    piva_or_cf = piva_or_cf.strip()
    if piva_or_cf in st.session_state.infocheck_cache:
        return st.session_state.infocheck_cache[piva_or_cf], None

    token, err = abbrevia_get_token()
    if err:
        return None, err

    url = f"{ABBREVIA_BASE_URL}/abbx/info-check"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Environment": st.session_state.abbrevia_env,
        "Authorization": f"Bearer {token}",
    }

    # Accetta partitaIva o codiceFiscale
    body = {"partitaIva": piva_or_cf} if len(piva_or_cf) == 11 and piva_or_cf.isdigit() else {"codiceFiscale": piva_or_cf}

    try:
        resp = requests.post(url, json=body, headers=headers, timeout=30)
        if resp.status_code == 404:
            return None, "Scheda InfoCheck non trovata per questo identificativo."
        if resp.status_code == 402:
            return None, "Credito Abbrevia X insufficiente (402 Payment Required)."
        if resp.status_code != 200:
            return None, f"Errore InfoCheck ({resp.status_code}): {resp.text}"

        dati = resp.json().get("data", {})
        st.session_state.infocheck_cache[piva_or_cf] = dati
        return dati, None
    except Exception as exc:
        return None, f"Errore chiamata InfoCheck: {exc}"


# =========================================================================
# GEMINI REST API
# =========================================================================

def call_gemini_api(prompt, temperature=0.7, max_tokens=1500):
    api_key = st.session_state.gemini_api_key.strip()
    if not api_key:
        return None, "no_key"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        return text, "ok"
    except Exception as exc:
        return None, f"errore: {exc}"


# =========================================================================
# GOOGLE PLACES API
# =========================================================================

def google_places_text_search(query, api_key, max_results=10):
    if not api_key:
        return [], "no_key"
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    try:
        resp = requests.get(url, params={"query": query, "key": api_key}, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") not in ("OK", "ZERO_RESULTS"):
            return [], f"errore Places: {data.get('status')}"
        return data.get("results", [])[:max_results], None
    except Exception as exc:
        return [], f"errore rete: {exc}"


def google_places_details(place_id, api_key):
    if not api_key or not place_id:
        return {}
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,formatted_phone_number,international_phone_number,website,rating,user_ratings_total",
        "key": api_key,
    }
    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        return resp.json().get("result", {})
    except Exception:
        return {}


def lead_da_risultato_places(r, settore, paese, fonte, api_key):
    lead_id = st.session_state.next_id
    st.session_state.next_id += 1
    d = google_places_details(r.get("place_id", ""), api_key)

    nome = d.get("name") or r.get("name", "Azienda")
    sito = d.get("website", "")
    telefono = d.get("formatted_phone_number") or d.get("international_phone_number", "")
    rating = d.get("rating") or r.get("rating")
    score = int(min(99, max(35, (rating or 3.5) * 20)))

    return {
        "id": lead_id,
        "azienda": nome,
        "paese": paese,
        "settore": settore,
        "dimensione": "Da verificare",
        "tecnologia_target": MAPPA_TECNOLOGIA_SETTORE.get(settore, "Linee di estrusione PVC"),
        "urgenza": random.choice(LIVELLI_URGENZA),
        "stato": "Nuovo",
        "contatto": "Da individuare",
        "email": f"info@{sito.replace('http://','').replace('https://','').split('/')[0]}" if sito else "Non disponibile",
        "telefono": telefono or "Non disponibile",
        "sito_web": sito or "Non disponibile",
        "fonte": fonte,
        "punteggio": score,
        "note": f"Indirizzo: {d.get('formatted_address', '')}",
        "lotto": st.session_state.lotto_corrente,
        "data_inserimento": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "dati_reali": True,
        "piva": "",
    }


def cerca_aziende_reali(settore, paese, fonte, n_lead=10, query_extra=""):
    api_key = st.session_state.places_api_key.strip()
    query = SETTORE_QUERY_PLACES.get(settore, "plastic processing") + f" in {paese}"
    if query_extra:
        query += f" {query_extra}"
    risultati, err = google_places_text_search(query, api_key, max_results=n_lead)
    if err:
        return [], err
    return [lead_da_risultato_places(r, settore, paese, fonte, api_key) for r in risultati], None


# =========================================================================
# LEAD MOCK
# =========================================================================

def genera_lead_mock(settore, paese, fonte, dimensione=None, urgenza=None, tecnologia=None, nota_extra=""):
    lead_id = st.session_state.next_id
    st.session_state.next_id += 1
    azienda = random.choice(PREFISSI_AZIENDA) + random.choice(SUFFISSI_AZIENDA)
    dominio = azienda.lower().replace(" ", "").replace(".", "")[:12]
    return {
        "id": lead_id,
        "azienda": azienda,
        "paese": paese,
        "settore": settore,
        "dimensione": dimensione or random.choice(DIMENSIONI_AZIENDA),
        "tecnologia_target": tecnologia or MAPPA_TECNOLOGIA_SETTORE.get(settore, random.choice(TECNOLOGIE_FRIUL_FILIERE)),
        "urgenza": urgenza or random.choice(LIVELLI_URGENZA),
        "stato": "Nuovo",
        "contatto": random.choice(NOMI_CONTATTO),
        "email": f"direzione@{dominio}.com",
        "telefono": f"+39 0432 {random.randint(100000, 999999)}",
        "sito_web": f"www.{dominio}.com",
        "fonte": fonte,
        "punteggio": random.randint(45, 95),
        "note": nota_extra,
        "lotto": st.session_state.lotto_corrente,
        "data_inserimento": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "dati_reali": False,
        "piva": f"IT{random.randint(10000000000, 99999999999)}",
    }


def aggiungi_leads(nuovi):
    st.session_state.leads.extend(nuovi)


def df_leads():
    return pd.DataFrame(st.session_state.leads) if st.session_state.leads else pd.DataFrame()


# =========================================================================
# EXPORT HELPERS (PDF / CSV)
# =========================================================================

def export_csv_bytes(df):
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


def _pdf_safe(t):
    return str(t).encode("latin-1", "replace").decode("latin-1")


def export_pdf_dossier(lead, dossier_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(14, 31, 61)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 12, _pdf_safe("Friul Filiere - Dossier Tecnico Commerciale"), ln=True, fill=True)
    pdf.ln(3)
    pdf.set_text_color(200, 16, 46)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, _pdf_safe(lead["azienda"]), ln=True)
    pdf.set_text_color(60, 60, 60)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, _pdf_safe(f"{lead['paese']} | {lead['settore']} | P.IVA: {lead.get('piva', 'N/D')}"), ln=True)
    pdf.ln(4)
    pdf.set_text_color(20, 20, 20)
    for p in dossier_text.split("\n"):
        pdf.multi_cell(0, 5, _pdf_safe(p))
    return bytes(pdf.output(dest="S"))


def export_pdf_lista_lead(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(14, 31, 61)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 12, _pdf_safe("Friul Filiere Lead Engine - Elenco Lead"), ln=True, fill=True)
    pdf.ln(3)
    pdf.set_fill_color(200, 16, 46)
    pdf.set_font("Helvetica", "B", 8)
    cols = ["azienda", "paese", "settore", "urgenza", "punteggio", "telefono"]
    w = [45, 25, 35, 20, 20, 45]
    for c, larg in zip(cols, w):
        pdf.cell(larg, 7, _pdf_safe(c.upper()), border=1, fill=True)
    pdf.ln()
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(20, 20, 20)
    for _, r in df.iterrows():
        for c, larg in zip(cols, w):
            pdf.cell(larg, 6, _pdf_safe(str(r.get(c, ""))[:25]), border=1)
        pdf.ln()
    return bytes(pdf.output(dest="S"))


# =========================================================================
# DOSSIER & OUTREACH ENGINE
# =========================================================================

def ottieni_dossier(lead, lingua):
    chiave = f"{lead['id']}_{lingua}"
    if chiave in st.session_state.dossier_cache:
        return st.session_state.dossier_cache[chiave]

    prompt = f"""
    Agisci come senior sales engineer per Friul Filiere (estrusione materie plastiche).
    Lingua: {lingua}.
    Prepara un Dossier Tecnico-Commerciale sintetico per il cliente:
    - Azienda: {lead['azienda']}
    - Settore: {lead['settore']}
    - Tecnologia target: {lead['tecnologia_target']}
    - Dati noti: {lead.get('note', '')}
    Struttura: 1) Profilo & esigenza 2) Soluzione Friul Filiere 3) Benefici (scarti, energia) 4) Next step commerciale.
    """
    testo, st_call = call_gemini_api(prompt)
    if not testo:
        testo = f"[Dossier sintetico Friul Filiere]\nProposta per {lead['azienda']} ({lead['settore']}): adozione di {lead['tecnologia_target']}. Soluzione ad elevata efficienza con riduzione scarti fino al 12%."
    st.session_state.dossier_cache[chiave] = testo
    return testo


def genera_sequenza_email(lead, lingua):
    return [
        {"step": 1, "giorno_invio": "Giorno 0", "oggetto": f"Efficienza di linea per {lead['azienda']}", "corpo": f"Gentile team di {lead['azienda']},\nnotiamo la vostra presenza nel settore {lead['settore']}. Friul Filiere offre impianti specializzati in {lead['tecnologia_target']}."},
        {"step": 2, "giorno_invio": "Giorno 4", "oggetto": f"Riduzione scarti per {lead['azienda']}", "corpo": f"Gentile referente,\nle nostre soluzioni consentono fino al 10% di risparmio sui consumi energetici su linee simili alle vostre."},
        {"step": 3, "giorno_invio": "Giorno 9", "oggetto": f"Ultimo spunto tecnico per {lead['azienda']}", "corpo": f"Restiamo a disposizione per una demo o un layout personalizzato. Cordiali saluti,\nFriul Filiere"},
    ]


# =========================================================================
# SIDEBAR
# =========================================================================

def sidebar():
    with st.sidebar:
        st.markdown("## 🏭 FRIUL FILIERE")
        st.markdown("##### Lead Engine & Abbrevia X")
        st.markdown("---")

        pagine = [
            "Dashboard",
            "🏢 Dati Ufficiali Imprese (Abbrevia X)",
            "🔎 Ricerca per Settore",
            "🎪 Ricerca Fiere",
            "📈 Progetti di Investimento",
            "👥 Analisi Lookalike",
            "🛰️ Radar Espansione & Organico",
            "🎯 Sales Twin Verticale",
            "📄 Dossier Tecnico AI",
            "✉️ Sequenze Outreach",
            "🗂️ CRM & Database Lead",
        ]
        st.session_state.pagina = st.radio("Modulo", pagine, label_visibility="collapsed")

        st.markdown("---")
        with st.expander("🏢 Connessione Abbrevia X", expanded=True):
            st.session_state.abbrevia_env = st.selectbox(
                "Ambiente", ["production", "pre-production"],
                index=0 if st.session_state.abbrevia_env == "production" else 1
            )
            st.session_state.abbrevia_username = st.text_input("Username / Client ID", value=st.session_state.abbrevia_username)
            st.session_state.abbrevia_password = st.text_input("Password / Secret", value=st.session_state.abbrevia_password, type="password")

            if st.button("🔌 Verifica Token Abbrevia"):
                token, err = abbrevia_get_token()
                if err:
                    st.error(err)
                else:
                    st.success("✅ Connessione riuscita (Token attivo)")

        with st.expander("🌍 Google Places & Gemini"):
            st.session_state.places_api_key = st.text_input("Google Places Key", value=st.session_state.places_api_key, type="password")
            st.session_state.gemini_api_key = st.text_input("Gemini API Key", value=st.session_state.gemini_api_key, type="password")

        st.markdown("---")
        st.metric("Lead nel CRM", len(st.session_state.leads))
        st.metric("Lotto di ricerca", st.session_state.lotto_corrente)


# =========================================================================
# PAGINA: MODULO ABBREVIA X
# =========================================================================

def pagina_abbrevia():
    st.markdown('<div class="ffe-header"><h1>🏢 Dati Ufficiali Imprese (Abbrevia X)</h1><p>Interroga direttamente il Registro Imprese italiano e genera schede InfoCheck per verificare solvibilità, fatturati e compagini sociali</p></div>', unsafe_allow_html=True)

    tab_ricerca, tab_infocheck = st.tabs(["🔎 Ricerca Ufficiale Registro Imprese", "📊 Scheda Approfondita InfoCheck"])

    with tab_ricerca:
        st.markdown("#### Ricerca Aziende nel Database Camerale")
        with st.form("form_cerca_abbrevia"):
            c1, c2 = st.columns(2)
            with c1:
                r_sociale = st.text_input("Ragione Sociale (es. Extrusion, Plast...)")
                piva = st.text_input("Partita IVA (11 cifre)")
            with c2:
                cf = st.text_input("Codice Fiscale")
                col_pr, col_rea = st.columns(2)
                with col_pr:
                    provincia = st.text_input("Provincia CCIAA (es. UD, MI)")
                with col_rea:
                    rea = st.text_input("Numero REA")

            submit = st.form_submit_button("🔎 Interroga Abbrevia X")

        if submit:
            if not any([r_sociale, piva, cf, (provincia and rea)]):
                st.warning("Inserisci almeno un criterio (Ragione Sociale, Partita IVA, CF oppure Provincia + REA).")
            else:
                with st.spinner("Interrogazione Registro Imprese in corso..."):
                    risultati, err = abbrevia_search_company(
                        ragione_sociale=r_sociale, piva=piva, cf=cf, provincia=provincia, rea=rea
                    )
                if err:
                    st.error(err)
                elif not risultati:
                    st.info("Nessuna azienda trovata con i parametri indicati.")
                else:
                    st.success(f"Trovate {len(risultati)} aziende corrispondenti.")
                    for item in risultati:
                        piva_item = item.get("partitaIva") or item.get("partitaIVA") or item.get("codiceFiscale", "")
                        with st.container():
                            st.markdown(f"""
                            <div class="ffe-card">
                                <span class="ffe-badge ffe-badge-abbrevia">DATI UFFICIALI CCIAA</span>
                                <span class="ffe-badge ffe-badge-info">Stato: {item.get('descrizioneStatoAttivita', 'N/D')}</span>
                                <h3>{item.get('denominazione', 'Azienda')}</h3>
                                <b>P.IVA / CF:</b> {piva_item} | <b>Natura:</b> {item.get('naturaGiuridica', 'N/D')}<br>
                                <b>Sede:</b> {item.get('indirizzo', '')} {item.get('cap', '')} {item.get('comune', '')} ({item.get('siglaProvincia', '')})<br>
                                <b>ATECO:</b> {item.get('codiceAteco', '')} - {item.get('descrizioneCodiceAteco', '')}<br>
                                <b>REA:</b> {item.get('cciaa', '')} {item.get('nrea', '')}
                            </div>
                            """, unsafe_allow_html=True)

                            col_btn1, col_btn2 = st.columns([1, 3])
                            with col_btn1:
                                if st.button(f"📥 Importa Lead #{piva_item}", key=f"imp_{piva_item}"):
                                    lead_id = st.session_state.next_id
                                    st.session_state.next_id += 1
                                    st.session_state.leads.append({
                                        "id": lead_id,
                                        "azienda": item.get("denominazione", "Azienda"),
                                        "paese": "Italia",
                                        "settore": "Estrusione / Plastica",
                                        "dimensione": item.get("naturaGiuridica", "Piccola/Media"),
                                        "tecnologia_target": "Linee di estrusione personalizzate",
                                        "urgenza": "Media",
                                        "stato": "Qualificato",
                                        "contatto": "Legale Rappresentante (CCIAA)",
                                        "email": "Verificare tramite InfoCheck",
                                        "telefono": "Da verificare",
                                        "sito_web": "Non presente in anagrafica base",
                                        "fonte": "Abbrevia X (Ufficiale)",
                                        "punteggio": 90,
                                        "note": f"ATECO: {item.get('codiceAteco')} | REA: {item.get('cciaa')}-{item.get('nrea')}",
                                        "lotto": st.session_state.lotto_corrente,
                                        "data_inserimento": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                        "dati_reali": True,
                                        "piva": piva_item,
                                    })
                                    st.success(f"Azienda {item.get('denominazione')} aggiunta ai lead!")

    with tab_infocheck:
        st.markdown("#### Richiesta Scheda di Profondità (InfoCheck)")
        st.caption("Fornisce informazioni complete su bilanci, dipendenti, esponenti, negatività e gruppo societario.")
        c_piva, c_btn = st.columns([2, 1])
        with c_piva:
            input_check = st.text_input("Partita IVA o Codice Fiscale dell'azienda", placeholder="Es. 01234567890")
        with c_btn:
            st.write("")
            st.write("")
            esegui_infocheck = st.button("📊 Scarica InfoCheck")

        if esegui_infocheck:
            if not input_check:
                st.warning("Inserisci una Partita IVA o un Codice Fiscale valido.")
            else:
                with st.spinner("Recupero scheda InfoCheck da Abbrevia X..."):
                    dati_info, err = abbrevia_get_infocheck(input_check)
                if err:
                    st.error(err)
                elif dati_info:
                    st.success("Scheda InfoCheck scaricata con successo!")
                    
                    # Sezione Anagrafica & Sintesi
                    anagrafica = dati_info.get("anagrafica", {})
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("##### 🏢 Dati Anagrafici")
                        st.json(anagrafica if anagrafica else {"messaggio": "Dati base non dettagliati"})
                    with col_b:
                        st.markdown("##### 👥 Dati Occupazionali & Dipendenti")
                        st.json(dati_info.get("datiOccupazionali", []))

                    st.markdown("---")
                    col_c, col_d = st.columns(2)
                    with col_c:
                        st.markdown("##### 📈 Bilanci & Performance")
                        st.json(dati_info.get("bilanci", []))
                    with col_d:
                        st.markdown("##### ⚠️ Negatività & Eventi Pregiudizievoli")
                        st.json(dati_info.get("negativita", {}))


# =========================================================================
# ALTRE PAGINE OPERATIVE
# =========================================================================

def pagina_dashboard():
    st.markdown('<div class="ffe-header"><h1>Dashboard Operativa</h1><p>Panoramica lead pipeline e copertura geografica</p></div>', unsafe_allow_html=True)
    df = df_leads()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="ffe-metric"><div class="val">{len(df)}</div><div class="lbl">Lead Totali</div></div>', unsafe_allow_html=True)
    with c2:
        alta = len(df[df["urgenza"] == "Alta"]) if not df.empty else 0
        st.markdown(f'<div class="ffe-metric"><div class="val">{alta}</div><div class="lbl">Urgenza Alta</div></div>', unsafe_allow_html=True)
    with c3:
        paesi = df["paese"].nunique() if not df.empty else 0
        st.markdown(f'<div class="ffe-metric"><div class="val">{paesi}</div><div class="lbl">Paesi Target</div></div>', unsafe_allow_html=True)
    with c4:
        score = round(df["punteggio"].mean(), 1) if not df.empty else 0
        st.markdown(f'<div class="ffe-metric"><div class="val">{score}</div><div class="lbl">Score Medio</div></div>', unsafe_allow_html=True)

    if not df.empty:
        st.markdown("<div class='ffe-divider'></div>", unsafe_allow_html=True)
        st.dataframe(df[["id", "azienda", "paese", "settore", "urgenza", "punteggio", "fonte"]], use_container_width=True)


def pagina_ricerca_settore():
    st.markdown('<div class="ffe-header"><h1>Ricerca Lead per Settore</h1><p>Scansione per trasformatori plastici tramite Google Places o motore generativo</p></div>', unsafe_allow_html=True)
    with st.form("form_sett"):
        c1, c2 = st.columns(2)
        with c1:
            sett = st.selectbox("Settore", SETTORI)
        with c2:
            paese = st.selectbox("Paese", PAESI)
        n = st.slider("Numero lead", 3, 20, 5)
        sub = st.form_submit_button("🔎 Avvia ricerca")
    if sub:
        usa_reali = bool(st.session_state.places_api_key.strip())
        if usa_reali:
            leads, err = cerca_aziende_reali(sett, paese, "Ricerca Settore (Places)", n)
            if err:
                st.error(err)
            else:
                aggiungi_leads(leads)
                st.success(f"Aggiunti {len(leads)} lead da Google Places.")
        else:
            mock = [genera_lead_mock(sett, paese, "Ricerca Settore (Mock)") for _ in range(n)]
            aggiungi_leads(mock)
            st.success(f"Generati {len(mock)} lead dimostrativi.")


def pagina_dossier():
    st.markdown('<div class="ffe-header"><h1>📄 Dossier Tecnico Commerciale</h1><p>Generazione personalizzata con focus tecnologico Friul Filiere</p></div>', unsafe_allow_html=True)
    df = df_leads()
    if df.empty:
        st.warning("Genera o importa prima dei lead nel CRM.")
        return
    idx = st.selectbox("Seleziona Azienda", df["id"].tolist(), format_func=lambda x: f"#{x} - {df[df['id']==x]['azienda'].values[0]}")
    lead = next(l for l in st.session_state.leads if l["id"] == idx)
    lingua = st.selectbox("Lingua", ["Italiano", "Inglese", "Tedesco", "Francese"])
    if st.button("Genera Dossier"):
        testo = ottieni_dossier(lead, lingua)
        st.text_area("Dossier", testo, height=300)
        st.download_button("⬇️ Scarica PDF", export_pdf_dossier(lead, testo), file_name=f"dossier_{lead['azienda']}.pdf", mime="application/pdf")


def pagina_outreach():
    st.markdown('<div class="ffe-header"><h1>✉️ Sequenze Outreach Email</h1><p>Pianificazione messaggi di contatto commerciale</p></div>', unsafe_allow_html=True)
    df = df_leads()
    if df.empty:
        st.warning("Genera o importa prima dei lead.")
        return
    idx = st.selectbox("Seleziona Lead", df["id"].tolist(), format_func=lambda x: f"#{x} - {df[df['id']==x]['azienda'].values[0]}")
    lead = next(l for l in st.session_state.leads if l["id"] == idx)
    lingua = st.selectbox("Lingua", ["Italiano", "Inglese", "Tedesco", "Francese"])
    if st.button("Crea sequenza 3 email"):
        seq = genera_sequenza_email(lead, lingua)
        for s in seq:
            st.markdown(f"**Step {s['step']} ({s['giorno_invio']})** - Oggetto: *{s['oggetto']}*")
            st.text_area(f"Testo Step {s['step']}", s["corpo"], height=100)


def pagina_crm():
    st.markdown('<div class="ffe-header"><h1>🗂️ CRM & Database Lead</h1><p>Gestione lead salvati ed export</p></div>', unsafe_allow_html=True)
    df = df_leads()
    if df.empty:
        st.info("Nessun lead presente nel database.")
        return

    st.dataframe(df, use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("⬇️ Esporta CSV", export_csv_bytes(df), "lead_friul_filiere.csv", "text/csv")
    with c2:
        st.download_button("⬇️ Esporta PDF", export_pdf_lista_lead(df), "lead_friul_filiere.pdf", "application/pdf")

    if st.button("🗑️ Svuota CRM"):
        st.session_state.leads = []
        st.rerun()


# =========================================================================
# ROUTING
# =========================================================================

def main():
    sidebar()
    p = st.session_state.pagina
    if p == "Dashboard":
        pagina_dashboard()
    elif p == "🏢 Dati Ufficiali Imprese (Abbrevia X)":
        pagina_abbrevia()
    elif p == "🔎 Ricerca per Settore":
        pagina_ricerca_settore()
    elif p == "📄 Dossier Tecnico AI":
        pagina_dossier()
    elif p == "✉️ Sequenze Outreach":
        pagina_outreach()
    elif p == "🗂️ CRM & Database Lead":
        pagina_crm()
    else:
        pagina_ricerca_settore()


if __name__ == "__main__":
    main()