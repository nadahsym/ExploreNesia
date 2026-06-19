"""
Semantic Tourism Search System
================================
Aplikasi pencarian wisata Indonesia berbasis Semantic Web
menggunakan Streamlit + Pandas + SPARQL.
"""
import streamlit as st
import pandas as pd
import math
import random
from SPARQLWrapper import SPARQLWrapper, JSON
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import rdflib
import json

# ──────────────────────────────────────────────
# SPARQL ENDPOINT
# ──────────────────────────────────────────────
# Pastikan Apache Jena Fuseki kamu berjalan di port 3030 dan nama datasetnya "tourism"
sparql = SPARQLWrapper("http://localhost:3030/tourism/query")

# ──────────────────────────────────────────────
# SVG VECTOR ICONS SYSTEM
# ──────────────────────────────────────────────
SVG_ICONS = {
    "compass": '<svg class="{clazz}" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon></svg>',
    "home": '<svg class="{clazz}" viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>',
    "search": '<svg class="{clazz}" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>',
    "package": '<svg class="{clazz}" viewBox="0 0 24 24"><line x1="16.5" y1="9.4" x2="7.5" y2="4.21"></line><polygon points="12 22.08 12 12 3 6.92 3 17.08 12 22.08"></polygon><polygon points="12 22.08 21 17.08 21 6.92 12 12 12 22.08"></polygon><polygon points="12 12 21 6.92 12 1.84 3 6.92 12 12"></polygon></svg>',
    "stats": '<svg class="{clazz}" viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>',
    "map": '<svg class="{clazz}" viewBox="0 0 24 24"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"></polygon><line x1="9" y1="3" x2="9" y2="18"></line><line x1="15" y1="6" x2="15" y2="21"></line></svg>',
    "semantic": '<svg class="{clazz}" viewBox="0 0 24 24"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>',
    "city": '<svg class="{clazz}" viewBox="0 0 24 24"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><line x1="9" y1="22" x2="9" y2="16"></line><line x1="15" y1="22" x2="15" y2="16"></line><line x1="9" y1="16" x2="15" y2="16"></line><path d="M8 6h.01M16 6h.01M9 10h.01M15 10h.01M12 6h.01M12 10h.01M8 14h.01M16 14h.01M12 14h.01"></path></svg>',
    "category": '<svg class="{clazz}" viewBox="0 0 24 24"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>',
    "rating": '<svg class="{clazz}" viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>',
    "price": '<svg class="{clazz}" viewBox="0 0 24 24"><rect x="2" y="6" width="20" height="12" rx="2"></rect><circle cx="12" cy="12" r="2"></circle><path d="M6 12h.01M18 12h.01"></path></svg>',
    "info": '<svg class="{clazz}" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>',
    "telescope": '<svg class="{clazz}" style="width:48px;height:48px;stroke-width:1.5" viewBox="0 0 24 24"><path d="M10.01 10.01 4 16v5l5-4 5.99-5.99M16.5 7.5l-3 3M19 5l-3 3M15 3l6 6M12 18v3M9 21h6"></path></svg>',
    "plug": '<svg class="{clazz}" style="width:48px;height:48px;stroke-width:1.5" viewBox="0 0 24 24"><path d="M12 2v6M9 8h6M10 12h4M10 18h4M8 12v3a4 4 0 0 0 8 0v-3M12 22v-3"></path></svg>',
    "arrow-right": '<svg class="{clazz}" viewBox="0 0 24 24"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>'
}

def get_svg_icon(name: str, clazz: str = "svg-icon") -> str:
    svg_template = SVG_ICONS.get(name, "")
    if svg_template:
        return svg_template.replace("{clazz}", clazz)
    return ""

def get_indo_ornament(type_: str = "batik") -> str:
    """Menghasilkan elemen dekoratif bertema Indonesia."""
    if type_ == "batik":
        return '''
        <div style="display:inline-block; width:24px; height:24px; margin:0 4px; opacity:0.6;">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;">
                <circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.5"/>
                <circle cx="12" cy="12" r="5" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3"/>
                <path d="M8 12 Q 12 8 16 12 Q 12 16 8 12" fill="none" stroke="currentColor" stroke-width="0.8" opacity="0.4"/>
            </svg>
        </div>
        '''
    elif type_ == "divider":
        return '<hr style="border:none; height:2px; background:linear-gradient(90deg, transparent, rgba(8,145,178,0.3), transparent); margin:1.5rem 0;">'
    elif type_ == "landmark":
        return '''
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="display:inline-block; width:20px; height:20px; opacity:0.5; margin:0 2px;">
            <path d="M12 2 L8 8 L8 20 L16 20 L16 8 Z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
            <rect x="9" y="9" width="6" height="3" fill="none" stroke="currentColor" stroke-width="1" opacity="0.6"/>
        </svg>
        '''
    return ""

# ──────────────────────────────────────────────
# PAGE CONFIGURATION
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Semantic Tourism Search",
    page_icon="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%232563eb' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolygon points='3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21'%3E%3C/polygon%3E%3Cline x1='9' y1='3' x2='9' y2='18'%3E%3C/line%3E%3Cline x1='15' y1='6' x2='15' y2='21'%3E%3C/line%3E%3C/svg%3E",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CUSTOM CSS — Premium Adaptive Dark/Light Mode
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ══════════════════════════════════════
   CSS Variables — Light Mode (default)
   Indonesia-inspired Color Harmony
   ══════════════════════════════════════ */
:root {
    --bg-primary:        #f4f6fa;
    --bg-surface:        #ffffff;
    --bg-surface-hover:  #f8fafc;
    --bg-subtle:         #edf2f7;
    --border-color:      #cbd5e1;
    --text-primary:      #0f172a;
    --text-secondary:    #334155;
    --text-muted:        #64748b;
    /* Indonesia-inspired accents */
    --accent-blue:       #0891b2;   /* Ocean Coast */
    --accent-green:      #15803d;   /* Forest Green */
    --accent-orange:     #ea580c;   /* Sunset Orange */
    --accent-purple:     #7c3aed;   /* Kept for packages */
    
    --shadow-sm:         0 1px 3px rgba(15,23,42,0.08);
    --shadow-md:         0 4px 6px -1px rgba(15,23,42,0.1), 0 2px 4px -1px rgba(15,23,42,0.06);
    --shadow-hover:      0 12px 20px -3px rgba(8, 145, 178, 0.12), 0 4px 6px -2px rgba(15,23,42,0.05);
    
    /* Badge colors inspired by Indonesian landscapes */
    --badge-city-bg:     #e0f2fe;
    --badge-city-fg:     #0c4a6e;   /* Deep ocean */
    --badge-cat-bg:      #fef3c7;
    --badge-cat-fg:     #78350f;    /* Earth tone */
    --badge-rating-bg:   #dcfce7;
    --badge-rating-fg:   #166534;   /* Forest */
    --badge-price-bg:    #fed7aa;
    --badge-price-fg:    #7c2d12;   /* Spice brown */
    --icon-color:        #64748b;
}

/* ══════════════════════════════════════
   CSS Variables — Dark Mode
   Indonesia-inspired Ocean & Forest
   ══════════════════════════════════════ */
@media (prefers-color-scheme: dark) {
    :root {
        --bg-primary:        #0f172a;
        --bg-surface:        #1e293b;
        --bg-surface-hover:  #334155;
        --bg-subtle:         #1e293b;
        --border-color:      #334155;
        --text-primary:      #f8fafc;
        --text-secondary:    #cbd5e1;
        --text-muted:        #94a3b8;
        /* Indonesia-inspired dark mode */
        --accent-blue:       #06b6d4;   /* Bright ocean */
        --accent-green:      #4ade80;   /* Fresh forest */
        --accent-orange:     #fb923c;   /* Warm sunset */
        --accent-purple:     #a78bfa;
        
        --shadow-sm:         0 1px 3px rgba(0,0,0,0.3);
        --shadow-md:         0 4px 6px -1px rgba(0,0,0,0.4);
        --shadow-hover:      0 12px 20px -3px rgba(6,182,212,0.25);
        
        --badge-city-bg:     #164e63;
        --badge-city-fg:     #67e8f9;
        --badge-cat-bg:      #78350f;
        --badge-cat-fg:      #fcd34d;
        --badge-rating-bg:   #14532d;
        --badge-rating-fg:   #86efac;
        --badge-price-bg:    #7c2d12;
        --badge-price-fg:    #fed7aa;
        --icon-color:        #94a3b8;
    }
}

/* Override Tema Streamlit (Mendukung Dynamic switching) */
[data-theme="dark"] {
    --bg-primary:        #0f172a;
    --bg-surface:        #1e293b;
    --bg-surface-hover:  #334155;
    --bg-subtle:         #1e293b;
    --border-color:      #334155;
    --text-primary:      #f8fafc;
    --text-secondary:    #cbd5e1;
    --text-muted:        #94a3b8;
    --accent-blue:       #3b82f6;
    --accent-green:      #34d399;
    --accent-orange:     #fbbf24;
    --accent-purple:     #a78bfa;
    
    --shadow-sm:         0 1px 3px rgba(0,0,0,0.3);
    --shadow-md:         0 4px 6px -1px rgba(0,0,0,0.4);
    --shadow-hover:      0 12px 20px -3px rgba(59,130,246,0.25);
    
    --badge-city-bg:     #1e3a8a;
    --badge-city-fg:     #93c5fd;
    --badge-cat-bg:      #78350f;
    --badge-cat-fg:      #fcd34d;
    --badge-rating-bg:   #065f46;
    --badge-rating-fg:   #6ee7b7;
    --badge-price-bg:    #831843;
    --badge-price-fg:    #fbcfe8;
    --icon-color:        #94a3b8;
}

[data-theme="light"] {
    --bg-primary:        #f4f6fa;
    --bg-surface:        #ffffff;
    --bg-surface-hover:  #f8fafc;
    --bg-subtle:         #edf2f7;
    --border-color:      #cbd5e1;
    --text-primary:      #0f172a;
    --text-secondary:    #334155;
    --text-muted:        #64748b;
    --accent-blue:       #0891b2;   /* Ocean */
    --accent-green:      #15803d;   /* Forest */
    --accent-orange:     #ea580c;   /* Sunset */
    --accent-purple:     #7c3aed;
    
    --badge-city-bg:     #e0f2fe;
    --badge-city-fg:     #0c4a6e;
    --badge-cat-bg:      #fef3c7;
    --badge-cat-fg:      #78350f;
    --badge-rating-bg:   #dcfce7;
    --badge-rating-fg:   #166534;
    --badge-price-bg:    #fed7aa;
    --badge-price-fg:    #7c2d12;
    --icon-color:        #64748b;
}

/* ══════════════════════════════════════
   Indonesian Cultural Theme Colors
   ══════════════════════════════════════ */
:root {
    /* Indonesia-inspired palette: ocean blue, forest green, sunset orange, volcanic earth */
    --indo-ocean:        #0891b2;   /* Kalimantan Coast */
    --indo-forest:       #15803d;   /* Rainforest Green */
    --indo-sunset:       #ea580c;   /* Sunset Orange */
    --indo-earth:        #92400e;   /* Volcanic Soil */
    --indo-gold:         #d97706;   /* Golden Spice */
    --indo-coral:        #f87171;   /* Coral Red */
}

/* ── Global Styles ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Background Image with Blur & Overlay */
[data-testid="stAppViewContainer"] {
    background: 
        linear-gradient(180deg, 
            rgba(244, 246, 250, 0.92) 0%,
            rgba(244, 246, 250, 0.88) 50%,
            rgba(244, 246, 250, 0.92) 100%
        ),
        url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800"><defs><filter id="blur"><feGaussianBlur in="SourceGraphic" stdDeviation="3"/></filter></defs><g opacity="0.08" filter="url(%23blur)"><path d="M0 300 Q 300 200 600 300 T 1200 300 L 1200 800 L 0 800 Z" fill="%230891b2"/><path d="M0 400 Q 300 350 600 400 T 1200 400 L 1200 800 L 0 800 Z" fill="%2315803d"/><circle cx="150" cy="250" r="120" fill="%23d97706" opacity="0.6"/><circle cx="1050" cy="150" r="150" fill="%23ea580c" opacity="0.5"/></g></svg>') center/cover fixed !important;
    background-attachment: fixed !important;
}

/* Dark Mode Background */
@media (prefers-color-scheme: dark) {
    [data-testid="stAppViewContainer"] {
        background: 
            linear-gradient(180deg, 
                rgba(15, 23, 42, 0.95) 0%,
                rgba(15, 23, 42, 0.92) 50%,
                rgba(15, 23, 42, 0.95) 100%
            ),
            url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800"><defs><filter id="blur"><feGaussianBlur in="SourceGraphic" stdDeviation="3"/></filter></defs><g opacity="0.04" filter="url(%23blur)"><path d="M0 300 Q 300 200 600 300 T 1200 300 L 1200 800 L 0 800 Z" fill="%2338bdf8"/><path d="M0 400 Q 300 350 600 400 T 1200 400 L 1200 800 L 0 800 Z" fill="%2386efac"/><circle cx="150" cy="250" r="120" fill="%23fbbf24" opacity="0.4"/><circle cx="1050" cy="150" r="150" fill="%23fb923c" opacity="0.3"/></g></svg>') center/cover fixed !important;
        background-attachment: fixed !important;
    }
}
[data-testid="stAppViewContainer"] > .main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* ── Streamlit native element fixes for light/dark mode ── */
.stTextInput > div > div > input,
.stSelectbox > div > div > div,
.stNumberInput > div > div > input {
    background: var(--bg-surface) !important;
    border-color: var(--border-color) !important;
    color: var(--text-primary) !important;
}
.stSlider > div { color: var(--text-primary) !important; }
label, .stRadio label, .stCheckbox label {
    color: var(--text-primary) !important;
}
.stDataFrame { border-color: var(--border-color) !important; }
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    color: var(--text-secondary);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0b1329 !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
[data-testid="stSidebar"] .stMarkdown, 
[data-testid="stSidebar"] label, 
[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] span, 
[data-testid="stSidebar"] li {
    color: #cbd5e1 !important;
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {
    color: #ffffff !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px;
    margin-top: 1.2rem;
}
[data-testid="stSidebar"] div.stSelectbox > div > div > div,
[data-testid="stSidebar"] div.stSlider > div,
[data-testid="stSidebar"] div.stTextInput > div > div > input {
    background-color: #172554 !important;
    color: #ffffff !important;
    border-color: #1e3a8a !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.08) !important; }

/* ── SVG Icon Base styling ── */
.svg-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.1em;
    height: 1.1em;
    vertical-align: -0.15em;
    fill: none;
    stroke: currentColor;
    stroke-width: 2.2;
    stroke-linecap: round;
    stroke-linejoin: round;
}
.inline-icon {
    width: 14px !important;
    height: 14px !important;
    vertical-align: middle !important;
    margin-right: 4px !important;
}

/* ── Hero Banner — Indonesian Explorer Theme ── */
.hero-banner {
    background: linear-gradient(135deg, #0891b2 0%, #0f172a 35%, #15803d 70%, #0f172a 100%);
    border-radius: 20px;
    padding: 2.8rem 2.8rem 2.4rem;
    margin-bottom: 2rem;
    box-shadow: 0 8px 40px rgba(0,0,0,0.15);
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.08);
}
.hero-banner::before {
    content: "";
    position: absolute;
    inset: 0;
    background: 
        url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200"><defs><pattern id="batik" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse"><circle cx="20" cy="20" r="8" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="1"/><path d="M10 20 Q 20 10 30 20 Q 20 30 10 20" fill="none" stroke="rgba(255,255,255,0.02)" stroke-width="0.5"/></pattern></defs><rect width="400" height="200" fill="url(%23batik)"/></svg>') repeat;
    opacity: 0.4;
    pointer-events: none;
}
.hero-banner::after {
    content: "";
    position: absolute;
    top: -40px;
    right: -40px;
    width: 220px;
    height: 220px;
    background: radial-gradient(circle, rgba(6,182,212,0.2) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    color: #ffffff;
    font-size: 2.3rem;
    font-weight: 800;
    margin: 0 0 0.5rem;
    letter-spacing: -0.5px;
    line-height: 1.2;
    display: flex;
    align-items: center;
    gap: 10px;
    position: relative;
    z-index: 1;
}
.hero-title svg {
    color: #06b6d4;
    width: 32px;
    height: 32px;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}
.hero-subtitle {
    color: #cffafe;
    font-size: 1rem;
    margin: 0 0 1rem;
    font-weight: 400;
    line-height: 1.5;
    max-width: 560px;
    position: relative;
    z-index: 1;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(6,182,212,0.15);
    border: 1px solid rgba(6,182,212,0.4);
    color: #cffafe;
    font-size: 0.75rem;
    padding: 5px 14px;
    border-radius: 100px;
    letter-spacing: 0.4px;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 0.25rem;
    position: relative;
    z-index: 1;
}

/* ── Stat Cards ── */
.stat-card {
    background: var(--bg-surface);
    border-radius: 16px;
    padding: 1.3rem 1.6rem;
    box-shadow: var(--shadow-sm);
    border-left: 4px solid;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border-top: 1px solid var(--border-color);
    border-right: 1px solid var(--border-color);
    border-bottom: 1px solid var(--border-color);
}
.stat-number {
    font-size: 2rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1;
    letter-spacing: -1px;
}
.stat-label {
    font-size: 0.78rem;
    color: var(--text-muted);
    margin-top: 8px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
}
.stat-label svg { width: 14px; height: 14px; color: var(--text-muted); }

/* ── Search Section ── */
.search-section {
    background: var(--bg-surface);
    border-radius: 18px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color);
}
.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
    letter-spacing: -0.2px;
}
.section-title svg { color: var(--accent-blue); }

/* ── Tourism Card ── */
.tourism-card {
    background: var(--bg-surface);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color);
    border-top: 3px solid var(--accent-blue);
    transition: box-shadow 0.25s ease, transform 0.25s ease, border-color 0.25s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
}
.tourism-card:hover {
    box-shadow: var(--shadow-hover);
    transform: translateY(-3px);
    border-color: rgba(37,99,235,0.3);
}
.card-title {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 0.6rem;
    line-height: 1.35;
    letter-spacing: -0.2px;
}
.card-meta { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 0.75rem; }
.badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.72rem;
    padding: 3px 9px;
    border-radius: 100px;
    font-weight: 600;
    letter-spacing: 0.2px;
    white-space: nowrap;
}
.badge svg { width: 12px; height: 12px; }
.badge-city     { background: var(--badge-city-bg);   color: var(--badge-city-fg); }
.badge-category { background: var(--badge-cat-bg);    color: var(--badge-cat-fg); }
.badge-rating   { background: var(--badge-rating-bg); color: var(--badge-rating-fg); }
.badge-price    { background: var(--badge-price-bg);  color: var(--badge-price-fg); }
.card-desc {
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.6;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    flex-grow: 1;
}

/* ── Package Card ── */
.package-card {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    color: #ffffff;
    height: 100%;
    box-shadow: var(--shadow-md);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border: 1px solid rgba(255,255,255,0.05);
    display: flex;
    flex-direction: column;
}
.package-card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(0,0,0,0.25); }
.package-city {
    font-size: 0.72rem;
    color: #38bdf8;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.4rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    display: flex;
    align-items: center;
    gap: 4px;
}
.package-places { font-size: 0.85rem; color: #cbd5e1; margin-top: 0.6rem; line-height: 1.7; }
.place-item { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }
.place-item svg { color: #38bdf8; flex-shrink: 0; }

/* ── Section Headers ── */
.sec-header { display: flex; align-items: center; gap: 0.75rem; margin: 2.5rem 0 1.2rem; }
.sec-header h2 {
    font-size: 1.2rem;
    font-weight: 800;
    color: var(--text-primary);
    margin: 0;
    white-space: nowrap;
    letter-spacing: -0.3px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.sec-header h2 svg { color: var(--accent-blue); }
.sec-line { flex: 1; height: 1px; background: linear-gradient(90deg, var(--border-color), transparent); }

/* ── Empty State ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: var(--text-muted);
    background: var(--bg-surface);
    border-radius: 18px;
    border: 2px dashed var(--border-color);
    margin-top: 1rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.empty-state svg { color: var(--text-muted); margin-bottom: 0.75rem; }
.empty-state p { font-size: 0.95rem; margin-top: 0.5rem; color: var(--text-secondary); line-height: 1.6; max-width: 400px; margin-inline: auto; }

/* ── Footer ── */
.footer {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.8rem;
    padding: 2rem 0 1.5rem;
    border-top: 1px solid var(--border-color);
    margin-top: 3rem;
    line-height: 1.8;
}

/* ── Info Row & Legends ── */
.info-row {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-bottom: 0.55rem;
    line-height: 1.5;
}
.info-row svg { flex-shrink: 0; margin-top: 1px; color: var(--icon-color); }
.info-row b { color: var(--text-primary); font-weight: 600; }

.legend-box {
    background: var(--bg-subtle);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 0.9rem 1rem;
    font-size: 0.8rem;
    margin-top: 1rem;
}
.legend-title {
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 6px;
}
.legend-title svg { color: var(--accent-blue); }
.legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-secondary);
    margin-bottom: 5px;
    font-size: 0.78rem;
}

/* ── Tourism Card with Indonesia-Inspired Design ── */
.tourism-card {
    background: var(--bg-surface);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color);
    border-top: 3px solid var(--accent-blue);
    border-left: 2px solid var(--accent-green);
    transition: box-shadow 0.25s ease, transform 0.25s ease, border-color 0.25s ease;
    height: 100%;
    position: relative;
    overflow: hidden;
}
.tourism-card::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(8,145,178,0.03) 0%, transparent 60%);
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.25s;
}
.tourism-card:hover {
    box-shadow: var(--shadow-hover);
    transform: translateY(-3px);
    border-color: rgba(8,145,178,0.3);
    border-top-color: var(--accent-orange);
}
.tourism-card:hover::before { opacity: 1; }
.card-title {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 0.6rem;
    line-height: 1.35;
    letter-spacing: -0.2px;
}
.card-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-bottom: 0.75rem;
}
.badge {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    font-size: 0.7rem;
    padding: 3px 9px;
    border-radius: 100px;
    font-weight: 600;
    letter-spacing: 0.2px;
    white-space: nowrap;
}
.badge-city     { background: var(--badge-city-bg);   color: var(--badge-city-fg); }
.badge-category { background: var(--badge-cat-bg);    color: var(--badge-cat-fg); }
.badge-rating   { background: var(--badge-rating-bg); color: var(--badge-rating-fg); }
.badge-price    { background: var(--badge-price-bg);  color: var(--badge-price-fg); }
.card-desc {
    font-size: 0.82rem;
    color: var(--text-secondary);
    line-height: 1.6;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* ── Package Card with Ocean & Forest Gradient ── */
.package-card {
    background: linear-gradient(135deg, #0c4a6e 0%, #064e3b 50%, #1e3a8a 100%);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    color: #fff;
    height: 100%;
    box-shadow: var(--shadow-md);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border: 1px solid rgba(6,182,212,0.2);
    position: relative;
    overflow: hidden;
}
.package-card::after {
    content: "";
    position: absolute;
    top: -30px;
    right: -30px;
    width: 120px;
    height: 120px;
    background: radial-gradient(circle, rgba(6,182,212,0.25) 0%, transparent 70%);
    pointer-events: none;
}
.package-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(6,182,212,0.2);
    border-color: rgba(6,182,212,0.4);
}
.package-city {
    font-size: 0.7rem;
    color: #67e8f9;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.4rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}
.package-places {
    font-size: 0.82rem;
    color: #cffafe;
    margin-top: 0.6rem;
    line-height: 1.7;
}

/* ── Section Headers with Indonesian Ornaments ── */
.sec-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 2.5rem 0 1.2rem;
    position: relative;
}
.sec-header::before {
    content: "";
    position: absolute;
    left: 0;
    top: -12px;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--accent-blue);
    opacity: 0.6;
    box-shadow: 8px 0 0 var(--accent-green), 16px 0 0 var(--accent-orange);
}
.sec-header h2 {
    font-size: 1.2rem;
    font-weight: 800;
    color: var(--text-primary);
    margin: 0;
    white-space: nowrap;
    letter-spacing: -0.3px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.sec-header h2 svg {
    color: var(--accent-blue);
}
.sec-line {
    flex: 1;
    height: 2px;
    background: linear-gradient(90deg, 
        var(--accent-blue) 0%, 
        var(--accent-green) 25%, 
        var(--accent-orange) 50%, 
        var(--accent-green) 75%, 
        transparent 100%);
    border-radius: 2px;
    opacity: 0.4;
}

/* ── Indonesian Ornamental Divider ── */
.indo-divider {
    height: 3px;
    margin: 1.5rem 0;
    background: linear-gradient(90deg, 
        transparent 0%, 
        var(--accent-blue) 15%, 
        var(--accent-green) 35%, 
        var(--accent-orange) 50%, 
        var(--accent-green) 65%, 
        var(--accent-blue) 85%, 
        transparent 100%);
    border-radius: 2px;
    opacity: 0.5;
}

/* ── Batik Pattern Background for Sections ── */
.batik-section {
    position: relative;
}
.batik-section::before {
    content: "";
    position: absolute;
    inset: 0;
    background: 
        url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><defs><pattern id="batik-fine" x="0" y="0" width="50" height="50" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="4" fill="none" stroke="rgba(255,255,255,0.02)" stroke-width="0.5"/><path d="M15 25 Q 25 15 35 25 Q 25 35 15 25" fill="none" stroke="rgba(255,255,255,0.01)" stroke-width="0.3"/></pattern></defs><rect width="200" height="200" fill="url(%23batik-fine)"/></svg>') repeat;
    pointer-events: none;
    opacity: 0.3;
}

/* ── Landmark Silhouettes (decorative) ── */
.landmark-accent {
    position: relative;
    display: inline-block;
}
.landmark-accent::after {
    content: "";
    position: absolute;
    bottom: -8px;
    right: -12px;
    width: 24px;
    height: 24px;
    background: 
        url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g opacity="0.15"><path d="M12 2 L16 8 L20 8 L20 20 L4 20 L4 8 L8 8 Z" fill="currentColor"/></g></svg>') no-repeat center / contain;
    color: var(--accent-blue);
}

/* ── Pagination ── */
.page-info {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.82rem;
    margin-top: 1rem;
    font-weight: 500;
    letter-spacing: 0.2px;
}

/* ── Empty State ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: var(--text-muted);
    background: var(--bg-surface);
    border-radius: 18px;
    border: 1px dashed var(--border-color);
    margin-top: 1rem;
}
.empty-state .icon {
    font-size: 3.5rem;
    margin-bottom: 0.5rem;
    display: block;
}
.empty-state p {
    font-size: 0.95rem;
    margin-top: 0.5rem;
    color: var(--text-secondary);
    line-height: 1.6;
    max-width: 400px;
    margin-inline: auto;
}

/* ── Footer with Indonesian Ornamental Elements ── */
.footer {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.78rem;
    padding: 2.5rem 0 1.5rem;
    border-top: 2px solid transparent;
    border-image: linear-gradient(90deg, 
        transparent 0%, 
        var(--accent-blue) 15%, 
        var(--accent-green) 35%, 
        var(--accent-orange) 50%, 
        var(--accent-green) 65%, 
        var(--accent-blue) 85%, 
        transparent 100%) 1;
    margin-top: 3rem;
    line-height: 1.8;
    position: relative;
}
.footer::before {
    content: "🌴  •  🏔️  •  🌊  •  🎭  •  🌴";
    display: block;
    font-size: 1.2rem;
    margin-bottom: 0.8rem;
    letter-spacing: 4px;
    opacity: 0.4;
}

/* ── Result count text ── */
[style*="color:#666"] {
    color: var(--text-secondary) !important;
}

/* ── Smooth transitions for all interactive elements ── */
button, input, select, textarea, [role="button"] {
    transition: all 0.2s ease !important;
}

/* ── Animation for landscape/cultural theme ── */
@keyframes gentle-float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-2px); }
}

.indo-animated {
    animation: gentle-float 3s ease-in-out infinite;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# DATA LOADING — Apache Jena Fuseki sebagai sumber utama
# Semua halaman menggunakan SPARQL Endpoint (Fuseki) sebagai sumber data.
# Jika Fuseki tidak tersedia, otomatis fallback ke rdflib (TTL lokal).
# ──────────────────────────────────────────────
@st.cache_resource
def load_ontology_graph(path: str = "tourism_ontology.ttl") -> rdflib.Graph:
    """Memuat ontologi TTL sebagai fallback jika Fuseki tidak tersedia."""
    g = rdflib.Graph()
    g.parse(path, format="turtle")
    return g

def _sparql_query(query_str: str, _g: rdflib.Graph = None) -> list:
    # ── Coba Fuseki ──
    try:
        sparql.setQuery(query_str)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        bindings = results["results"]["bindings"]
        if bindings:  
            # Tambahkan notifikasi ini!
            st.toast("🌐 Mengambil data dari Server Apache Jena Fuseki", icon="🚀")
            return [{k: v["value"] for k, v in row.items()} for row in bindings]
    except Exception:
        pass  # Fuseki tidak tersedia

    # ── Fallback: rdflib ──
    # Tambahkan notifikasi ini!
    st.toast("📂 Server mati! Mengambil data dari file TTL lokal", icon="⚠️")
    
    if _g is None:
        _g = load_ontology_graph()
    rows = []
    for r in _g.query(query_str):
        row = {}
        for var in r.labels:
            val = r[var]
            row[str(var)] = str(val).strip() if val is not None else ""
        rows.append(row)
    return rows

@st.cache_data
def load_tourism_data(_g: rdflib.Graph = None) -> pd.DataFrame:
    """Memuat data tempat wisata. Sumber utama: Fuseki. Fallback: rdflib TTL."""
    q = """
    PREFIX : <http://www.semanticweb.org/tourism-ontology#>
    SELECT ?placeId ?placeName ?cityName ?categoryName ?price ?rating ?desc ?lat ?long
    WHERE {
        ?place a :TouristPlace ;
               :hasName ?placeName ;
               :locatedIn ?cityNode ;
               :hasCategory ?categoryNode ;
               :hasPrice ?price ;
               :hasRating ?rating ;
               :hasDescription ?desc .
        ?cityNode :hasName ?cityName .
        ?categoryNode :hasName ?categoryName .
        OPTIONAL { ?place :hasPlaceId ?placeId . }
        OPTIONAL { ?place :hasLat ?lat . }
        OPTIONAL { ?place :hasLong ?long . }
    }
    """
    raw = _sparql_query(q, _g)
    if not raw:
        return pd.DataFrame()
    rows = []
    for r in raw:
        rows.append({
            "Place_Id":    r.get("placeId", ""),
            "Place_Name":  r.get("placeName", "").strip(),
            "City":        r.get("cityName", "").strip(),
            "Category":    r.get("categoryName", "").strip(),
            "Price":       int(float(r["price"]))    if r.get("price")  else 0,
            "Rating":      float(r["rating"])        if r.get("rating") else 0.0,
            "Description": r.get("desc", "").strip(),
            "Lat":         float(r["lat"])           if r.get("lat")    else None,
            "Long":        float(r["long"])          if r.get("long")   else None,
        })
    df = pd.DataFrame(rows)
    df["Price"]  = pd.to_numeric(df["Price"],  errors="coerce").fillna(0).astype(int)
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce").fillna(0.0)
    df["Lat"]    = pd.to_numeric(df["Lat"],    errors="coerce")
    df["Long"]   = pd.to_numeric(df["Long"],   errors="coerce")
    return df

@st.cache_data
def load_package_data(_g: rdflib.Graph = None) -> pd.DataFrame:
    """Memuat data paket wisata. Sumber utama: Fuseki. Fallback: rdflib TTL."""
    import re
    q = """
    PREFIX : <http://www.semanticweb.org/tourism-ontology#>
    SELECT ?packageName ?cityName ?placeName
    WHERE {
        ?package a :TourPackage ;
                 :hasName ?packageName ;
                 :locatedIn ?city ;
                 :includes ?place .
        ?city  :hasName ?cityName .
        ?place :hasName ?placeName .
    }
    ORDER BY ?packageName
    """
    raw = _sparql_query(q, _g)
    grouped = {}
    for r in raw:
        pkg_name  = r.get("packageName", "").strip()
        city_name = r.get("cityName", "").strip()
        place_nm  = r.get("placeName", "").strip()
        m = re.search(r'(\d+)', pkg_name)
        pkg_id = int(m.group(1)) if m else pkg_name
        key = (pkg_id, city_name)
        grouped.setdefault(key, []).append(place_nm)
    rows = []
    for (pkg_id, city_name), places in grouped.items():
        row = {"Package": pkg_id, "City": city_name}
        for idx, p in enumerate(places, start=1):
            row[f"Place_Tourism{idx}"] = p
        rows.append(row)
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("Package").reset_index(drop=True)
    return df

def get_recommendations(target_place_name, df_sparql, top_n=3):
    # Jika data kosong atau tempat tidak ditemukan, kembalikan dataframe kosong
    if df_sparql.empty or target_place_name not in df_sparql['Place_Name'].values:
        return pd.DataFrame()

    # 1. Gabungkan fitur teks yang akan dianalisis oleh AI
    # Kita menggabungkan Kategori, Kota, dan Deskripsi menjadi satu kalimat panjang
    df_sparql['AI_Features'] = df_sparql['Category'] + " " + df_sparql['City'] + " " + df_sparql['Description']

    # 2. Ubah teks menjadi representasi angka (vektor) menggunakan TF-IDF
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df_sparql['AI_Features'])

    # 3. Hitung skor kemiripan (Cosine Similarity) antar semua tempat wisata
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # 4. Cari index dari tempat wisata yang sedang dipilih user
    idx = df_sparql.index[df_sparql['Place_Name'] == target_place_name].tolist()[0]

    # 5. Ambil skor kemiripan tempat tersebut dengan tempat lainnya
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Urutkan dari skor yang paling tinggi ke rendah
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Ambil top N (kita lewati index ke-0 karena itu adalah tempat itu sendiri yang pasti skornya 100%)
    sim_scores = sim_scores[1:top_n+1]
    
    # Dapatkan index tempat-tempat hasil rekomendasi
    place_indices = [i[0] for i in sim_scores]

    # Kembalikan baris data tempat wisata yang direkomendasikan
    return df_sparql.iloc[place_indices]

@st.dialog("Rekomendasi Wisata Serupa")
def show_recommendation_dialog(place_name, df_sparql):
    st.markdown(f"Tempat yang mirip dengan **{place_name}**:")
    
    with st.spinner("Menganalisis kemiripan konten..."):
        # Panggil fungsi AI kita
        rekomendasi = get_recommendations(place_name, df_sparql, top_n=3)
        
    if rekomendasi.empty:
        st.info("Maaf, belum ada rekomendasi yang cukup mirip.")
    else:
        # Tampilkan hasil rekomendasi dengan gaya yang rapi
        for _, row in rekomendasi.iterrows():
            st.markdown(f"### {row['Place_Name']}")
            st.markdown(f"""
            <div style="font-size:0.9rem; font-weight:600; color:var(--text-secondary); margin-bottom:0.5rem; display:flex; align-items:center; gap:12px;">
                <span style="display:flex; align-items:center; gap:4px;">{get_svg_icon("city")} {row['City']}</span>
                <span style="display:flex; align-items:center; gap:4px;">{get_svg_icon("category")} {row['Category']}</span>
                <span style="display:flex; align-items:center; gap:4px;">{get_svg_icon("rating")} {row['Rating']}</span>
            </div>
            """, unsafe_allow_html=True)
            st.caption(row['Description'][:150] + "...")
            st.divider() # Garis pemisah antar rekomendasi

def format_price(price):
    """Mengubah angka harga menjadi format Rupiah atau teks 'Gratis'"""
    if pd.isna(price) or price == 0:
        return "Gratis"
    return f"Rp {int(price):,.0f}".replace(",", ".")

def star_rating(rating):
    """Menghasilkan string bintang berdasarkan nilai float rating"""
    stars = int(round(rating))
    return "⭐" * stars

def category_color(category):
    """Mengembalikan warna hex spesifik berdasarkan kategori wisata"""
    colors = {
        "Budaya": "#ff6b6b",
        "Taman Hiburan": "#ffd93d",
        "Cagar Alam": "#6bcb77",
        "Bahari": "#4d96ff",
        "Pusat Perbelanjaan": "#c77dff",
        "Tempat Ibadah": "#ff9f1c"
    }
    return colors.get(category, "#3a86ff") # Default warna biru

def get_sparql_tourism(search_q, filter_city, filter_cat, filter_rating, _g=None):
    """
    Fungsi untuk memfilter data berdasarkan input user di halaman 'Cari Wisata'.
    Mengambil data dari fungsi load_tourism_data yang sudah dicache untuk efisiensi.
    """
    df = load_tourism_data(_g)
    
    # Return dataframe kosong jika data belum tersedia
    if df.empty:
        return df
        
    # Terapkan filter satu per satu
    if search_q:
        df = df[df['Place_Name'].str.contains(search_q, case=False, na=False)]
    if filter_city != "Semua Kota":
        df = df[df['City'] == filter_city]
    if filter_cat != "Semua Kategori":
        df = df[df['Category'] == filter_cat]
        
    df = df[df['Rating'] >= filter_rating]
    
    return df

# ──────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="font-size:1.3rem; font-weight:800; color:#ffffff; margin-bottom:0.5rem; display:flex; align-items:center; gap:8px;">
        {get_svg_icon("compass")} ExploreNesia
    </div>
    <div style="font-size:0.75rem; color:#06b6d4; letter-spacing:1px; font-family:'JetBrains Mono',monospace; margin-bottom:1rem;">
        🌴 Eksplorasi Kekayaan Wisata Indonesia 🌴
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "Navigasi",
        ["Beranda", "Cari Wisata", "Paket Wisata", "Statistik", "Peta Wisata", "Relasi Semantik"],
        label_visibility="collapsed",
    )

    # ── Graph filter settings (only shown on Relasi Semantik page) ──
    if page == "Relasi Semantik":
        st.markdown("---")
        st.markdown("<div style='font-size:0.8rem; color:#a8c4e0; font-weight:700; letter-spacing:0.5px; margin-bottom:0.5rem;'>⚙️ PENGATURAN GRAF</div>", unsafe_allow_html=True)
        graph_filter_mode = st.selectbox(
            "Tipe Relasi Semantik:",
            ["Semua Relasi", "Lokasi yang Sama", "Kategori yang Sama", "Paket yang Sama"],
            index=0,
            key="graph_filter_mode"
        )
        graph_sort_by = st.selectbox(
            "Urutkan Tetangga:",
            ["Default", "Rating Tertinggi", "Rating Terendah", "Nama A–Z", "Nama Z–A", "Acak"],
            index=0,
            key="graph_sort_by"
        )
        graph_max_nodes = st.slider(
            "Jumlah Node Tetangga:",
            min_value=2,
            max_value=10,
            value=3,
            key="graph_max_nodes"
        )
    else:
        graph_filter_mode = "Semua Relasi"
        graph_sort_by = "Default"
        graph_max_nodes = 3

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.75rem; color:rgba(200,214,232,0.45); text-align:center; font-family:JetBrains Mono,monospace;'>"
        "🌏 ExploreNesia v1.3<br>Semantic Web Tourism Platform<br>"
        "<span style='font-size:0.7rem;'>Discover Indonesia's Wonders</span>"
        "</div>",
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────
# LOAD DATA AWAL — Dari TTL (sumber tunggal)
# ──────────────────────────────────────────────
with st.spinner("Memuat ontologi wisata dari TTL…"):
    _g_shared    = load_ontology_graph()
    df_tourism   = load_tourism_data(_g_shared)
    df_packages  = load_package_data(_g_shared)

all_cities      = sorted(df_tourism["City"].unique().tolist())      if not df_tourism.empty else []
all_categories  = sorted(df_tourism["Category"].unique().tolist())  if not df_tourism.empty else []
min_r = float(df_tourism["Rating"].min()) if not df_tourism.empty else 0.0
max_r = float(df_tourism["Rating"].max()) if not df_tourism.empty else 5.0

# ══════════════════════════════════════════════
# PAGE: BERANDA
# ══════════════════════════════════════════════
if page == "Beranda":

    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-title">{get_svg_icon("compass")} Semantic Tourism Search System</div>
        <div class="hero-subtitle">
            Jelajahi 400+ destinasi wisata Indonesia — Jakarta, Yogyakarta,
            Bandung, Semarang, Surabaya
        </div>
    </div>
    """, unsafe_allow_html=True)

    total_places = len(df_tourism)
    total_cities = df_tourism["City"].nunique()
    total_cats   = df_tourism["Category"].nunique()
    avg_rating   = df_tourism["Rating"].mean()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="stat-card blue">
            <div class="stat-number">{total_places}</div>
            <div class="stat-label">{get_svg_icon("city")} Total Wisata</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card green">
            <div class="stat-number">{total_cities}</div>
            <div class="stat-label">{get_svg_icon("city")} Kota</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-card orange">
            <div class="stat-number">{total_cats}</div>
            <div class="stat-label">{get_svg_icon("category")} Kategori</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="stat-card purple">
            <div class="stat-number">{avg_rating:.1f}</div>
            <div class="stat-label">{get_svg_icon("rating")} Rata-rata Rating</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="indo-divider"></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sec-header">
        <h2>{get_svg_icon("search")} Pencarian Cepat</h2>
        <div class="sec-line"></div>
    </div>
    """, unsafe_allow_html=True)

    quick_q = st.text_input(
        "Cari tempat wisata…",
        placeholder="Contoh: Borobudur, pantai, museum…",
        label_visibility="collapsed",
    )
    if quick_q:
        mask = df_tourism["Place_Name"].str.contains(quick_q, case=False, na=False)
        results = df_tourism[mask].head(6)
        if results.empty:
            st.info("Tidak ada hasil. Coba kata kunci lain.")
        else:
            cols = st.columns(3)
            for i, (_, row) in enumerate(results.iterrows()):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="tourism-card" style="border-color:{category_color(row['Category'])};">
                        <div class="card-title">{row['Place_Name']}</div>
                        <div class="card-meta">
                            <span class="badge badge-city">{get_svg_icon("city")} {row['City']}</span>
                            <span class="badge badge-category">{get_svg_icon("category")} {row['Category']}</span>
                            <span class="badge badge-rating">{get_svg_icon("rating")} {row['Rating']}</span>
                            <span class="badge badge-price">{get_svg_icon("price")} {format_price(row['Price'])}</span>
                        </div>
                        <p class="card-desc">{row['Description']}</p>
                    </div>
                    """, unsafe_allow_html=True)

    CATEGORY_ICON_COLORS = {
        "Budaya":               "#ff6b6b",
        "Taman Hiburan":        "#ffd93d",
        "Cagar Alam":           "#6bcb77",
        "Bahari":               "#4d96ff",
        "Pusat Perbelanjaan":   "#c77dff",
        "Tempat Ibadah":        "#ff9f1c",
    }

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:0.85rem; font-weight:700; color:var(--text-primary); margin-bottom:0.5rem;">{get_svg_icon("info")} Legenda Kategori</div>', unsafe_allow_html=True)
    leg_cols = st.columns(len(CATEGORY_ICON_COLORS))
    for i, (cat_name, cat_color) in enumerate(CATEGORY_ICON_COLORS.items()):
        with leg_cols[i]:
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:6px;font-size:0.78rem;color:var(--text-secondary);'>"
                f"<span style='width:12px;height:12px;border-radius:50%;background:{cat_color};display:inline-block;flex-shrink:0;'></span>"
                f"{cat_name}</div>",
                unsafe_allow_html=True,
            )
    
    st.markdown(f"""
    <div class="sec-header">
        <h2>{get_svg_icon("rating")} Wisata Unggulan</h2>
        <div class="sec-line"></div>
    </div>
    """, unsafe_allow_html=True)

    top_places = df_tourism.nlargest(6, "Rating")
    cols = st.columns(3)
    for i, (_, row) in enumerate(top_places.iterrows()):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="tourism-card" style="border-color:{category_color(row['Category'])};">
                <div class="card-title">{row['Place_Name']}</div>
                <div class="card-meta">
                    <span class="badge badge-city">{get_svg_icon("city")} {row['City']}</span>
                    <span class="badge badge-category">{get_svg_icon("category")} {row['Category']}</span>
                    <span class="badge badge-rating">{get_svg_icon("rating")} {row['Rating']} {star_rating(row['Rating'])}</span>
                    <span class="badge badge-price">{get_svg_icon("price")} {format_price(row['Price'])}</span>
                </div>
                <p class="card-desc">{row['Description']}</p>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# PAGE: CARI WISATA (SUDAH MENGGUNAKAN SPARQL)
# ══════════════════════════════════════════════
elif page == "Cari Wisata":

    st.markdown(f"""
    <div class="hero-banner" style="padding:2rem 2.5rem;">
        <div class="hero-title" style="font-size:1.8rem;">{get_svg_icon("search")} Cari Tempat Wisata</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="search-section">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{get_svg_icon("info")} Filter Pencarian Semantic</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    with col1:
        search_q = st.text_input(
            "Nama Wisata",
            placeholder="Cari nama tempat wisata…",
            label_visibility="visible",
        )
    with col2:
        filter_city = st.selectbox(
            "Kota",
            ["Semua Kota"] + all_cities,
        )
    with col3:
        filter_cat = st.selectbox(
            "Kategori",
            ["Semua Kategori"] + all_categories,
        )
    with col4:
        filter_rating = st.slider(
            "Rating Minimum",
            min_value=min_r,
            max_value=max_r,
            value=min_r,
            step=0.1,
            format="%.1f ⭐",
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Ambil Data dari Semantic Web (Fuseki → rdflib fallback) ──
    with st.spinner("Mengambil data dari Semantic Web (TTL / Fuseki)..."):
        filtered = get_sparql_tourism(search_q, filter_city, filter_cat, filter_rating, _g=_g_shared)

    if not filtered.empty:
        # Sort by rating descending by default
        filtered = filtered.sort_values("Rating", ascending=False).reset_index(drop=True)

        col_res, col_sort = st.columns([5, 2])
        with col_res:
            st.markdown(
                f"<p style='color:var(--text-secondary); font-size:0.9rem; margin:0.5rem 0;'>"
                f"Menampilkan <b>{len(filtered)}</b> tempat wisata</p>",
                unsafe_allow_html=True,
            )
        with col_sort:
            sort_by = st.selectbox(
                "Urutkan",
                ["Rating Tertinggi", "Harga Terendah", "Harga Tertinggi", "A-Z"],
                label_visibility="collapsed",
            )

        if sort_by == "Rating Tertinggi":
            filtered = filtered.sort_values("Rating", ascending=False)
        elif sort_by == "Harga Terendah":
            filtered = filtered.sort_values("Price", ascending=True)
        elif sort_by == "Harga Tertinggi":
            filtered = filtered.sort_values("Price", ascending=False)
        elif sort_by == "A-Z":
            filtered = filtered.sort_values("Place_Name", ascending=True)

        CARDS_PER_PAGE = 12
        total_pages = max(1, math.ceil(len(filtered) / CARDS_PER_PAGE))
        page_num = st.number_input(
            f"Halaman (dari {total_pages})",
            min_value=1,
            max_value=total_pages,
            value=1,
            step=1,
            label_visibility="collapsed",
        )
        start_idx = (page_num - 1) * CARDS_PER_PAGE
        page_data = filtered.iloc[start_idx : start_idx + CARDS_PER_PAGE]

        if page_data.empty:
            st.markdown(f"""
            <div class="empty-state">
                <div class="icon">{get_svg_icon("telescope")}</div>
                <p>Tidak ada wisata yang sesuai dengan filter yang dipilih.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            cols = st.columns(3)
            for i, (_, row) in enumerate(page_data.iterrows()):
                with cols[i % 3]:
                    desc_short = row["Description"][:180] + "…" if len(row["Description"]) > 180 else row["Description"]
                    st.markdown(f"""
                    <div class="tourism-card" style="border-color:{category_color(row['Category'])};">
                        <div class="card-title">{row['Place_Name']}</div>
                        <div class="card-meta">
                            <span class="badge badge-city">{get_svg_icon("city")} {row['City']}</span>
                            <span class="badge badge-category">{get_svg_icon("category")} {row['Category']}</span>
                            <span class="badge badge-rating">{get_svg_icon("rating")} {row['Rating']}</span>
                            <span class="badge badge-price">{get_svg_icon("price")} {format_price(row['Price'])}</span>
                        </div>
                        <p class="card-desc">{desc_short}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("Lihat Rekomendasi", key=f"btn_{row['Place_Name']}", use_container_width=True):
                        show_recommendation_dialog(row['Place_Name'], filtered)

            st.markdown(
                f"<div class='page-info'>Halaman {page_num} dari {total_pages} "
                f"· {len(filtered)} hasil total</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(f"""
        <div class="empty-state">
            <div class="icon">{get_svg_icon("telescope")}</div>
            <p>Tidak ada data ditemukan yang sesuai filter. Coba ubah kriteria pencarian.</p>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# PAGE: PAKET WISATA
# ══════════════════════════════════════════════
elif page == "Paket Wisata":

    st.markdown(f"""
    <div class="hero-banner" style="padding:2rem 2.5rem;">
        <div class="hero-title" style="font-size:1.8rem;">{get_svg_icon("package")} Paket Wisata Rekomendasi</div>
        <div class="hero-subtitle">Kumpulan paket perjalanan wisata terkurasi per kota</div>
    </div>
    """, unsafe_allow_html=True)

    pkg_cities = sorted(df_packages["City"].unique().tolist())
    selected_city = st.selectbox("Filter Kota Paket", ["Semua Kota"] + pkg_cities)

    pkg_filtered = df_packages.copy()
    if selected_city != "Semua Kota":
        pkg_filtered = pkg_filtered[pkg_filtered["City"] == selected_city]

    st.markdown(
        f"<p style='color:var(--text-secondary); font-size:0.9rem; margin:0.5rem 0 1.2rem;'>"
        f"Menampilkan <b>{len(pkg_filtered)}</b> paket wisata</p>",
        unsafe_allow_html=True,
    )

    place_cols = sorted([c for c in df_packages.columns if c.startswith("Place_Tourism")])

    cols = st.columns(3)
    for i, (_, row) in enumerate(pkg_filtered.iterrows()):
        places = [str(row[c]) for c in place_cols if pd.notna(row[c]) and str(row[c]).strip()]
        places_html = "".join(
            f"<div>▸ {p}</div>" for p in places
        ) if places else "<div style='color:rgba(255,255,255,0.35); font-style:italic;'>Tidak ada detail tempat</div>"

        with cols[i % 3]:
            st.markdown(f"""
            <div class="package-card">
                <div class="package-city">{get_svg_icon("city")} {row['City']}</div>
                <div style="font-size:1rem; font-weight:700; color:#e8f0fa; letter-spacing:-0.2px; margin-bottom:0.2rem;">
                    Paket #{int(row['Package'])}
                </div>
                <div class="package-places">{places_html}</div>
            </div>
            """, unsafe_allow_html=True)

    if selected_city != "Semua Kota":
        st.markdown(f"""
        <div class="sec-header">
            <h2>{get_svg_icon("city")} Wisata Populer di Kota Ini</h2>
            <div class="sec-line"></div>
        </div>
        """, unsafe_allow_html=True)

        city_tourism = (
            df_tourism[df_tourism["City"] == selected_city]
            .nlargest(6, "Rating")
        )
        cols2 = st.columns(3)
        for i, (_, row) in enumerate(city_tourism.iterrows()):
            with cols2[i % 3]:
                st.markdown(f"""
                <div class="tourism-card" style="border-color:{category_color(row['Category'])};">
                    <div class="card-title">{row['Place_Name']}</div>
                    <div class="card-meta">
                        <span class="badge badge-category">{get_svg_icon("category")} {row['Category']}</span>
                        <span class="badge badge-rating">{get_svg_icon("rating")} {row['Rating']}</span>
                        <span class="badge badge-price">{get_svg_icon("price")} {format_price(row['Price'])}</span>
                    </div>
                    <p class="card-desc">{row['Description'][:150]}…</p>
                </div>
                """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# PAGE: STATISTIK
# ══════════════════════════════════════════════
elif page == "Statistik":

    st.markdown(f"""
    <div class="hero-banner" style="padding:2rem 2.5rem;">
        <div class="hero-title" style="font-size:1.8rem;">{get_svg_icon("stats")} Statistik Dataset</div>
        <div class="hero-subtitle">Gambaran umum dataset wisata Indonesia</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="stat-card blue">
            <div class="stat-number">{len(df_tourism)}</div>
            <div class="stat-label">{get_svg_icon("city")} Total Wisata</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card green">
            <div class="stat-number">{df_tourism['City'].nunique()}</div>
            <div class="stat-label">{get_svg_icon("city")} Jumlah Kota</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-card orange">
            <div class="stat-number">{df_tourism['Category'].nunique()}</div>
            <div class="stat-label">{get_svg_icon("category")} Kategori</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="stat-card purple">
            <div class="stat-number">{len(df_packages)}</div>
            <div class="stat-label">{get_svg_icon("package")} Paket Wisata</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown(f"#### {get_svg_icon('city', 'svg-icon inline-icon')} Wisata per Kota", unsafe_allow_html=True)
        city_counts = df_tourism["City"].value_counts().reset_index()
        city_counts.columns = ["Kota", "Jumlah Wisata"]
        st.bar_chart(city_counts.set_index("Kota"))

        st.dataframe(
            city_counts,
            use_container_width=True,
            hide_index=True,
        )

    with col_right:
        st.markdown(f"#### {get_svg_icon('category', 'svg-icon inline-icon')} Wisata per Kategori", unsafe_allow_html=True)
        cat_counts = df_tourism["Category"].value_counts().reset_index()
        cat_counts.columns = ["Kategori", "Jumlah Wisata"]
        st.bar_chart(cat_counts.set_index("Kategori"))

        st.dataframe(
            cat_counts,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown(f"#### {get_svg_icon('rating', 'svg-icon inline-icon')} Distribusi Rating", unsafe_allow_html=True)
    rating_dist = df_tourism["Rating"].value_counts().sort_index()
    st.bar_chart(rating_dist)

    st.markdown(f"#### {get_svg_icon('info', 'svg-icon inline-icon')} Data Tempat Wisata (dari tourism_ontology.ttl)", unsafe_allow_html=True)
    display_cols = ["Place_Id", "Place_Name", "City", "Category", "Rating", "Price", "Description"]
    available = [c for c in display_cols if c in df_tourism.columns]
    st.dataframe(
        df_tourism[available].head(50),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(f"#### {get_svg_icon('package', 'svg-icon inline-icon')} Data Paket Wisata (dari tourism_ontology.ttl)", unsafe_allow_html=True)
    st.dataframe(df_packages.head(30), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# PAGE: PETA WISATA
# ══════════════════════════════════════════════
elif page == "Peta Wisata":

    st.markdown(f"""
    <div class="hero-banner" style="padding:2rem 2.5rem;">
        <div class="hero-title" style="font-size:1.8rem;">{get_svg_icon("map")} Peta Sebaran Wisata</div>
        <div class="hero-subtitle">Visualisasi lokasi geografis seluruh destinasi wisata Indonesia</div>
    </div>
    """, unsafe_allow_html=True)

    # Filter controls
    st.markdown('<div class="search-section">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{get_svg_icon("search")} Filter Peta</div>', unsafe_allow_html=True)

    map_col1, map_col2, map_col3 = st.columns([2, 2, 2])
    with map_col1:
        map_city = st.selectbox("Kota", ["Semua Kota"] + all_cities, key="map_city")
    with map_col2:
        map_cat  = st.selectbox("Kategori", ["Semua Kategori"] + all_categories, key="map_cat")
    with map_col3:
        map_rating = st.slider("Rating Minimum", min_value=min_r, max_value=max_r,
                               value=min_r, step=0.1, format="%.1f ★", key="map_rating")
    st.markdown('</div>', unsafe_allow_html=True)

    # Apply filters to df_tourism (which has Lat, Long)
    df_map = df_tourism.copy()
    if map_city != "Semua Kota":
        df_map = df_map[df_map["City"] == map_city]
    if map_cat != "Semua Kategori":
        df_map = df_map[df_map["Category"] == map_cat]
    df_map = df_map[df_map["Rating"] >= map_rating]
    df_map = df_map.dropna(subset=["Lat", "Long"])

    st.markdown(
        f"<p style='color:var(--text-secondary); font-size:0.9rem; margin:0.5rem 0 1rem;'>"
        f"Menampilkan <b>{len(df_map)}</b> destinasi wisata pada peta</p>",
        unsafe_allow_html=True,
    )

    # Build Leaflet markers JSON
    CATEGORY_ICON_COLORS = {
        "Budaya":               "#ff6b6b",
        "Taman Hiburan":        "#ffd93d",
        "Cagar Alam":           "#6bcb77",
        "Bahari":               "#4d96ff",
        "Pusat Perbelanjaan":   "#c77dff",
        "Tempat Ibadah":        "#ff9f1c",
    }

    markers = []
    for _, row in df_map.iterrows():
        color = CATEGORY_ICON_COLORS.get(str(row.get("Category", "")), "#3a86ff")
        price_str = format_price(int(row["Price"])) if "Price" in row else "—"
        markers.append({
            "lat":     float(row["Lat"]),
            "lng":     float(row["Long"]),
            "name":    str(row["Place_Name"]),
            "city":    str(row.get("City", "")),
            "cat":     str(row.get("Category", "")),
            "rating":  float(row["Rating"]),
            "price":   price_str,
            "color":   color,
        })

    markers_js = json.dumps(markers)

    # Compute map center
    if len(df_map) > 0:
        center_lat = df_map["Lat"].mean()
        center_lng = df_map["Long"].mean()
        zoom = 10 if map_city != "Semua Kota" else 6
    else:
        center_lat, center_lng, zoom = -7.0, 110.0, 6

    leaflet_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8"/>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            html, body {{ margin:0; padding:0; height:100%; font-family:'Plus Jakarta Sans',system-ui,sans-serif; }}
            #map {{ width:100%; height:100%; }}
            
            /* Premium Search Container Styling */
            #search-container {{
                position: absolute;
                top: 10px;
                left: 55px;
                z-index: 1000;
                width: 260px;
                transition: all 0.3s ease;
            }}
            
            #search-input {{
                width: 100%;
                padding: 8px 12px 8px 32px;
                font-family: inherit;
                font-size: 13px;
                border: 1px solid var(--border);
                border-radius: 8px;
                outline: none;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                background: var(--bg);
                color: var(--text);
                transition: all 0.3s ease;
            }}
            
            #search-input:focus {{
                border-color: #3b82f6;
                box-shadow: 0 4px 16px rgba(59,130,246,0.3);
            }}
            
            /* Search icon inside search container */
            .search-icon-wrapper {{
                position: absolute;
                left: 10px;
                top: 50%;
                transform: translateY(-50%);
                display: flex;
                align-items: center;
                color: var(--muted);
                pointer-events: none;
            }}
            .search-icon-wrapper svg {{
                width: 14px;
                height: 14px;
                fill: none;
                stroke: currentColor;
                stroke-width: 2.5;
                stroke-linecap: round;
                stroke-linejoin: round;
            }}

            #suggestions {{
                position: absolute;
                top: 40px;
                left: 0;
                width: 100%;
                background: var(--bg);
                border: 1px solid var(--border);
                border-radius: 8px;
                max-height: 200px;
                overflow-y: auto;
                display: none;
                box-shadow: 0 8px 24px rgba(0,0,0,0.2);
                z-index: 999;
            }}
            
            .suggestion-item {{
                padding: 8px 12px;
                font-size: 12px;
                cursor: pointer;
                color: var(--text);
                border-bottom: 1px solid var(--border-subtle);
                transition: background 0.2s ease;
            }}
            
            .suggestion-item:last-child {{
                border-bottom: none;
            }}
            
            .suggestion-item:hover {{
                background: var(--hover-bg);
            }}
            
            /* Tooltip styling matching app's premium cards */
            .leaflet-tooltip.custom-tooltip {{
                background: var(--tooltip-bg) !important;
                color: var(--tooltip-text) !important;
                border-radius: 12px !important;
                border: 1px solid var(--tooltip-border) !important;
                box-shadow: 0 8px 24px rgba(0,0,0,0.25) !important;
                padding: 12px 16px !important;
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                opacity: 1 !important;
            }}
            
            .tooltip-title {{ font-size:13px; font-weight:800; color:var(--tooltip-title-color); margin-bottom:4px; line-height:1.3; }}
            .tooltip-meta  {{ font-size:11px; color:var(--tooltip-muted); line-height:1.7; }}
            .tooltip-meta b {{ color:var(--tooltip-highlight); }}
            .tooltip-rating {{ display:inline-block; background:var(--tooltip-badge-bg); color:var(--tooltip-badge-text);
                             font-size:10px; font-weight:700; padding:2px 8px;
                             border-radius:100px; margin-top:6px; }}

            /* Tooltip arrow overrides */
            .leaflet-tooltip-left:before {{ border-left-color: var(--tooltip-bg) !important; }}
            .leaflet-tooltip-right:before {{ border-right-color: var(--tooltip-bg) !important; }}
            .leaflet-tooltip-top:before {{ border-top-color: var(--tooltip-bg) !important; }}
            .leaflet-tooltip-bottom:before {{ border-bottom-color: var(--tooltip-bg) !important; }}

            /* Light/Dark mode CSS variables for map overlays */
            :root {{
                --bg: #ffffff;
                --text: #1e293b;
                --muted: #64748b;
                --border: #cbd5e1;
                --border-subtle: #f1f5f9;
                --hover-bg: #f8fafc;
                
                --tooltip-bg: #ffffff;
                --tooltip-text: #334155;
                --tooltip-title-color: #0f172a;
                --tooltip-border: #e2e8f0;
                --tooltip-muted: #64748b;
                --tooltip-highlight: #2563eb;
                --tooltip-badge-bg: #ecfdf5;
                --tooltip-badge-text: #065f46;
            }}
            
            @media (prefers-color-scheme: dark) {{
                :root {{
                    --bg: #1e293b;
                    --text: #f8fafc;
                    --muted: #94a3b8;
                    --border: #334155;
                    --border-subtle: #1e293b;
                    --hover-bg: #334155;
                    
                    --tooltip-bg: #0f172a;
                    --tooltip-text: #cbd5e1;
                    --tooltip-title-color: #f8fafc;
                    --tooltip-border: #334155;
                    --tooltip-muted: #94a3b8;
                    --tooltip-highlight: #3b82f6;
                    --tooltip-badge-bg: #065f46;
                    --tooltip-badge-text: #6ee7b7;
                }}
            }}
        </style>
    </head>
    <body>
    <div id="search-container">
        <div class="search-icon-wrapper">
            <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        </div>
        <input type="text" id="search-input" placeholder="Cari nama atau kota wisata..."/>
        <div id="suggestions"></div>
    </div>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([{center_lat}, {center_lng}], {zoom});

        var isDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        var tileUrl = isDarkMode 
            ? 'https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png' 
            : 'https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png';
        
        L.tileLayer(tileUrl, {{
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 19
        }}).addTo(map);

        var markers = {markers_js};
        var markerObjects = {{}};

        function makeIcon(color) {{
            return L.divIcon({{
                html: '<div style="width:14px;height:14px;border-radius:50%;background:' + color +
                      ';border:2px solid #fff;box-shadow:0 0 8px ' + color + '88;"></div>',
                className: '',
                iconSize: [14, 14],
                iconAnchor: [7, 7],
                tooltipAnchor: [0, -10]
            }});
        }}

        markers.forEach(function(m) {{
            var icon = makeIcon(m.color);
            var tooltipContent = 
                '<div class="tooltip-title">' + m.name + '</div>' +
                '<div class="tooltip-meta">' +
                    '<b>Kota:</b> ' + m.city + '<br>' +
                    '<b>Kategori:</b> ' + m.cat + '<br>' +
                    '<b>Harga:</b> ' + m.price +
                '</div>' +
                '<div class="tooltip-rating">⭐ ' + m.rating.toFixed(1) + ' / 5.0</div>';
            
            var marker = L.marker([m.lat, m.lng], {{icon: icon}})
                .bindTooltip(tooltipContent, {{
                    sticky: true,
                    direction: 'auto',
                    className: 'custom-tooltip'
                }})
                .addTo(map);
            
            markerObjects[m.name] = marker;
        }});

        // Search and suggestions implementation
        var searchInput = document.getElementById('search-input');
        var suggestions = document.getElementById('suggestions');
        
        searchInput.addEventListener('input', function(e) {{
            var val = e.target.value.toLowerCase().trim();
            suggestions.innerHTML = '';
            if (!val) {{
                suggestions.style.display = 'none';
                return;
            }}
            
            var matches = markers.filter(function(m) {{
                return m.name.toLowerCase().indexOf(val) > -1 || m.city.toLowerCase().indexOf(val) > -1;
            }});
            
            if (matches.length > 0) {{
                suggestions.style.display = 'block';
                matches.slice(0, 5).forEach(function(m) {{
                    var div = document.createElement('div');
                    div.className = 'suggestion-item';
                    div.innerHTML = '<b>' + m.name + '</b> <span style="font-size:10px; opacity:0.7;">(' + m.city + ')</span>';
                    div.addEventListener('click', function() {{
                        map.setView([m.lat, m.lng], 14);
                        var marker = markerObjects[m.name];
                        if (marker) {{
                            marker.openTooltip();
                        }}
                        searchInput.value = m.name;
                        suggestions.style.display = 'none';
                    }});
                    suggestions.appendChild(div);
                }});
            }} else {{
                suggestions.style.display = 'none';
            }}
        }});
        
        document.addEventListener('click', function(e) {{
            if (e.target !== searchInput && e.target !== suggestions) {{
                suggestions.style.display = 'none';
            }}
        }});
    </script>
    </body>
    </html>
    """

    st.components.v1.html(leaflet_html, height=540)

    # Legend
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:0.85rem; font-weight:700; color:var(--text-primary); margin-bottom:0.5rem;">{get_svg_icon("info")} Legenda Kategori</div>', unsafe_allow_html=True)
    leg_cols = st.columns(len(CATEGORY_ICON_COLORS))
    for i, (cat_name, cat_color) in enumerate(CATEGORY_ICON_COLORS.items()):
        with leg_cols[i]:
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:6px;font-size:0.78rem;color:var(--text-secondary);'>"
                f"<span style='width:12px;height:12px;border-radius:50%;background:{cat_color};display:inline-block;flex-shrink:0;'></span>"
                f"{cat_name}</div>",
                unsafe_allow_html=True,
            )

    # Summary table
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="sec-header"><h2>{get_svg_icon("info")} Daftar Destinasi</h2><div class="sec-line"></div></div>', unsafe_allow_html=True)
    display_cols_map = ["Place_Name", "City", "Category", "Rating", "Price"]
    avail_map = [c for c in display_cols_map if c in df_map.columns]
    st.dataframe(df_map[avail_map].reset_index(drop=True), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# PAGE: RELASI SEMANTIK
# ══════════════════════════════════════════════
elif page == "Relasi Semantik":


    st.markdown(f"""
    <div class="hero-banner" style="padding:2rem 2.5rem;">
        <div class="hero-title" style="font-size:1.8rem;">{get_svg_icon("semantic")} Visualisasi Graf Relasi Semantik</div>
        <div class="hero-subtitle">Menganalisis hubungan semantik antar konsep, kategori, kota, dan paket wisata dalam Knowledge Graph</div>
    </div>
    """, unsafe_allow_html=True)

    # Gunakan graph yang sudah dimuat di awal (sumber tunggal)
    g_ontology = _g_shared

    # Dropdown to select tourism spot
    all_places = sorted(df_tourism["Place_Name"].unique().tolist())

    st.markdown('<div class="search-section">', unsafe_allow_html=True)
    selected_place = st.selectbox(
        "Pilih Tempat Wisata untuk Dianalisis:",
        all_places,
        index=0
    )
    st.markdown('</div>', unsafe_allow_html=True)

    def apply_sorting_to_neighbors(neighbors_list, sort_by="Default"):
        """
        Terapkan sorting pada neighbor list.
        
        sort_by: "Default", "Rating Tertinggi", "Rating Terendah", "Nama A–Z", "Nama Z–A", "Acak"
        neighbors_list: list of tuples (name, rating, ...)
        """
        if sort_by == "Rating Tertinggi":
            return sorted(neighbors_list, key=lambda x: float(x[1]), reverse=True)
        elif sort_by == "Rating Terendah":
            return sorted(neighbors_list, key=lambda x: float(x[1]))
        elif sort_by == "Nama A–Z":
            return sorted(neighbors_list, key=lambda x: str(x[0]))
        elif sort_by == "Nama Z–A":
            return sorted(neighbors_list, key=lambda x: str(x[0]), reverse=True)
        elif sort_by == "Acak":
            shuffled = list(neighbors_list)
            random.shuffle(shuffled)
            return shuffled
        else:  # Default
            return list(neighbors_list)

    def get_vis_graph_data(place_name, g, filter_mode="Lokasi yang Sama", sort_by="Default", max_nodes=3):
        """
        Membangun graf relasi semantik bertingkat (multi-level) untuk place_name.
        
        Tier 0: Destinasi Utama
        Tier 1: Kota, Kategori, Paket Wisata
        Tier 2: Wisata yang terhubung melalui Tier 1
        
        filter_mode: "Lokasi yang Sama", "Kategori yang Sama", "Paket yang Sama", "Semua Relasi"
        sort_by: "Default", "Rating Tertinggi", "Rating Terendah", "Nama A–Z", "Nama Z–A", "Acak"
        max_nodes: jumlah tetangga per kategori relasi
        """
        q_place = """
        PREFIX : <http://www.semanticweb.org/tourism-ontology#>
        SELECT ?cityName ?categoryName ?price ?rating ?desc
        WHERE {
            ?place :hasName ?placeName .
            FILTER(str(?placeName) = "%s")
            ?place :locatedIn ?city ;
                   :hasCategory ?category ;
                   :hasPrice ?price ;
                   :hasRating ?rating ;
                   :hasDescription ?desc .
            ?city :hasName ?cityName .
            ?category :hasName ?categoryName .
        }
        LIMIT 1
        """ % place_name.replace('"', '\\"')
        
        res = list(g.query(q_place))
        if not res:
            return None
        
        city_name, category_name, price, rating, desc = res[0]
        
        nodes = []
        edges = []
        pname_esc = place_name.replace('"', '\\"')
        
        # ══════════════════════════════════════════════
        # TIER 0: Central node (destinasi utama)
        # ══════════════════════════════════════════════
        nodes.append({
            "id": "main",
            "label": place_name,
            "color": {"background": "#3a86ff", "border": "#1a6eef", "highlight": {"background": "#5599ff", "border": "#3a86ff"}},
            "font": {"color": "#ffffff", "size": 15, "bold": True},
            "shadow": {"enabled": True, "color": "rgba(58,134,255,0.4)", "size": 12, "x": 0, "y": 4},
            "title": f"<b>{place_name}</b><br>Rating: {rating} / 5.0<br>Harga: {format_price(int(float(price)))}",
            "size": 28,
            "level": 0
        })
        
        # ══════════════════════════════════════════════
        # TIER 1: Kota, Kategori, Paket Wisata
        # ══════════════════════════════════════════════
        
        show_city = filter_mode in ["Lokasi yang Sama", "Semua Relasi"]
        show_category = filter_mode in ["Kategori yang Sama", "Semua Relasi"]
        show_packages = filter_mode in ["Paket yang Sama", "Semua Relasi"]
        
        # 1.1 City node
        if show_city:
            nodes.append({
                "id": "city",
                "label": str(city_name),
                "color": {"background": "#06d6a0", "border": "#04b386", "highlight": {"background": "#20e8b4", "border": "#06d6a0"}},
                "font": {"color": "#ffffff", "size": 13, "bold": True},
                "shadow": True,
                "title": f"Kota: {city_name}",
                "level": 1
            })
            edges.append({
                "from": "main",
                "to": "city",
                "label": "locatedIn",
                "width": 3
            })
        
        # 1.2 Category node
        if show_category:
            nodes.append({
                "id": "category",
                "label": str(category_name),
                "color": {"background": "#ffb703", "border": "#e0a000", "highlight": {"background": "#ffc933", "border": "#ffb703"}},
                "font": {"color": "#1a1a1a", "size": 13, "bold": True},
                "shadow": True,
                "title": f"Kategori: {category_name}",
                "level": 1
            })
            edges.append({
                "from": "main",
                "to": "category",
                "label": "hasCategory",
                "width": 3
            })
        
        # 1.3 Package nodes
        package_list = []
        if show_packages:
            q_packages = """
            PREFIX : <http://www.semanticweb.org/tourism-ontology#>
            SELECT ?packageName
            WHERE {
                ?place :hasName ?placeName .
                FILTER(str(?placeName) = "%s")
                ?package a :TourPackage ;
                         :includes ?place ;
                         :hasName ?packageName .
            }
            """ % pname_esc
            
            for i, r in enumerate(g.query(q_packages)):
                pkg_name = str(r.packageName)
                node_id = f"package_{i}"
                package_list.append({"id": node_id, "name": pkg_name})
                
                nodes.append({
                    "id": node_id,
                    "label": pkg_name,
                    "color": {"background": "#7c3aed", "border": "#5b21b6",
                              "highlight": {"background": "#9057f0", "border": "#7c3aed"}},
                    "font": {"color": "#ffffff", "size": 11},
                    "shape": "box",
                    "title": "Paket Wisata yang mencakup tempat ini",
                    "level": 1
                })
                edges.append({
                    "from": "main",
                    "to": node_id,
                    "label": "includedIn",
                    "color": {"color": "#a78bfa"},
                    "width": 2
                })
        
        # ══════════════════════════════════════════════
        # TIER 2: Wisata terkait melalui Tier 1
        # ══════════════════════════════════════════════
        
        # 2.1 Wisata di kota yang sama (dari city node)
        if show_city:
            q_city_neighbors = """
            PREFIX : <http://www.semanticweb.org/tourism-ontology#>
            SELECT ?otherName ?otherRating
            WHERE {
                ?place :hasName ?placeName ; :locatedIn ?city .
                FILTER(str(?placeName) = "%s")
                ?otherPlace a :TouristPlace ; :locatedIn ?city ; :hasName ?otherName ; :hasRating ?otherRating .
                FILTER(str(?otherName) != "%s")
            }
            """ % (pname_esc, pname_esc)
            
            city_neighbors = apply_sorting_to_neighbors(list(g.query(q_city_neighbors)), sort_by)
            city_neighbors_sample = city_neighbors[:max_nodes]
            
            for i, r in enumerate(city_neighbors_sample):
                other_name = str(r[0])
                other_rating = float(r[1])
                node_id = f"city_neighbor_{i}"
                
                nodes.append({
                    "id": node_id,
                    "label": other_name,
                    "color": {"background": "#d1fae5", "border": "#6ee7b7",
                              "highlight": {"background": "#d1fae5", "border": "#6ee7b7"}},
                    "font": {"color": "#065f46", "size": 10},
                    "shape": "box",
                    "title": f"Wisata di {city_name}<br>Rating: {other_rating:.1f} / 5.0",
                    "level": 2
                })
                edges.append({
                    "from": "city",
                    "to": node_id,
                    "label": "sameCity",
                    "color": {"color": "#6ee7b7"},
                    "width": 1.5
                })
        
        # 2.2 Wisata dengan kategori yang sama (dari category node)
        if show_category:
            q_category_neighbors = """
            PREFIX : <http://www.semanticweb.org/tourism-ontology#>
            SELECT ?otherName ?otherRating
            WHERE {
                ?place :hasName ?placeName ; :hasCategory ?cat .
                FILTER(str(?placeName) = "%s")
                ?otherPlace a :TouristPlace ; :hasCategory ?cat ; :hasName ?otherName ; :hasRating ?otherRating .
                FILTER(str(?otherName) != "%s")
            }
            """ % (pname_esc, pname_esc)
            
            category_neighbors = apply_sorting_to_neighbors(list(g.query(q_category_neighbors)), sort_by)
            category_neighbors_sample = category_neighbors[:max_nodes]
            
            for i, r in enumerate(category_neighbors_sample):
                other_name = str(r[0])
                other_rating = float(r[1])
                node_id = f"category_neighbor_{i}"
                
                nodes.append({
                    "id": node_id,
                    "label": other_name,
                    "color": {"background": "#fef3c7", "border": "#fcd34d",
                              "highlight": {"background": "#fef3c7", "border": "#fcd34d"}},
                    "font": {"color": "#92400e", "size": 10},
                    "shape": "box",
                    "title": f"Wisata berkategori {category_name}<br>Rating: {other_rating:.1f} / 5.0",
                    "level": 2
                })
                edges.append({
                    "from": "category",
                    "to": node_id,
                    "label": "sameCategory",
                    "color": {"color": "#fcd34d"},
                    "width": 1.5
                })
        
        # 2.3 Wisata dalam paket yang sama (dari setiap package node)
        if show_packages:
            for pkg_info in package_list:
                pkg_node_id = pkg_info["id"]
                pkg_name = pkg_info["name"]
                
                q_package_neighbors = """
                PREFIX : <http://www.semanticweb.org/tourism-ontology#>
                SELECT ?otherName ?otherRating
                WHERE {
                    ?place :hasName ?placeName .
                    FILTER(str(?placeName) = "%s")
                    ?package :hasName ?packageName ; :includes ?place ; :includes ?otherPlace .
                    FILTER(str(?packageName) = "%s")
                    ?otherPlace :hasName ?otherName ; :hasRating ?otherRating .
                    FILTER(str(?otherName) != "%s")
                }
                """ % (pname_esc, pkg_name.replace('"', '\\"'), pname_esc)
                
                pkg_neighbors = apply_sorting_to_neighbors(list(g.query(q_package_neighbors)), sort_by)
                pkg_neighbors_sample = pkg_neighbors[:max_nodes]
                
                for i, r in enumerate(pkg_neighbors_sample):
                    other_name = str(r[0])
                    other_rating = float(r[1])
                    node_id = f"{pkg_node_id}_neighbor_{i}"
                    
                    nodes.append({
                        "id": node_id,
                        "label": other_name,
                        "color": {"background": "#ede9fe", "border": "#c4b5fd",
                                  "highlight": {"background": "#ede9fe", "border": "#c4b5fd"}},
                        "font": {"color": "#5b21b6", "size": 10},
                        "shape": "box",
                        "title": f"Wisata dalam {pkg_name}<br>Rating: {other_rating:.1f} / 5.0",
                        "level": 2
                    })
                    edges.append({
                        "from": pkg_node_id,
                        "to": node_id,
                        "label": "samePackage",
                        "color": {"color": "#c4b5fd"},
                        "width": 1.5
                    })
            
        return {
            "nodes": nodes,
            "edges": edges,
            "details": {
                "city": city_name,
                "category": category_name,
                "price": price,
                "rating": rating,
                "desc": desc
            },
            "filter_mode": filter_mode,
            "sort_by": sort_by,
            "max_nodes": max_nodes
        }

    def draw_vis_network(nodes, edges):
        nodes_js = json.dumps(nodes)
        edges_js = json.dumps(edges)
        
        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
            <style type="text/css">
                html, body {{
                    margin: 0;
                    padding: 0;
                    width: 100%;
                    height: 100%;
                    overflow: hidden;
                    font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
                }}
                #mynetwork {{
                    width: 100%;
                    height: 100%;
                    background-color: transparent;
                }}
                div.vis-tooltip {{
                    background-color: #0f1b2d !important;
                    border: 1px solid #3a86ff !important;
                    color: #e8edf5 !important;
                    border-radius: 8px !important;
                    padding: 8px 12px !important;
                    font-family: 'Plus Jakarta Sans', sans-serif !important;
                    font-size: 11px !important;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
                }}
            </style>
        </head>
        <body>
        <div id="mynetwork"></div>
        <script type="text/javascript">
            var nodes = new vis.DataSet({nodes_js});
            var edges = new vis.DataSet({edges_js});

            var container = document.getElementById('mynetwork');
            var data = {{
                nodes: nodes,
                edges: edges
            }};
            var options = {{
                nodes: {{
                    shape: 'box',
                    margin: 12,
                    borderWidth: 1.5,
                    borderColor: '#2a3349',
                    shapeProperties: {{
                        borderRadius: 10
                    }},
                    font: {{
                        face: 'Plus Jakarta Sans, system-ui, sans-serif',
                        size: 13
                    }}
                }},
                edges: {{
                    arrows: {{
                        to: {{ enabled: true, scaleFactor: 0.8 }}
                    }}
                    ,color: {{
                        color: '#8896ab',
                        highlight: '#3a86ff',
                        hover: '#3a86ff',
                        inherit: false
                    }},
                    font: {{
                        face: 'Plus Jakarta Sans, system-ui, sans-serif',
                        size: 10,
                        align: 'top',
                        color: '#8896ab'
                    }},
                    smooth: {{
                        type: 'cubicBezier',
                        forceDirection: 'none',
                        roundness: 0.5
                    }}
                }},
                interaction: {{
                    hover: true,
                    zoomView: true,
                    dragView: true
                }},
                physics: {{
                    solver: 'forceAtlas2Based',
                    forceAtlas2Based: {{
                        gravitationalConstant: -100,
                        centralGravity: 0.015,
                        springLength: 120,
                        springConstant: 0.08
                    }},
                    stabilization: {{
                        iterations: 120
                    }}
                }}
            }};
            var network = new vis.Network(container, data, options);
        </script>
        </body>
        </html>
        """
        return html_code

    if selected_place:
        with st.spinner("Mengekstrak hubungan semantik..."):
            graph_data = get_vis_graph_data(
                selected_place, g_ontology,
                filter_mode=graph_filter_mode,
                sort_by=graph_sort_by,
                max_nodes=graph_max_nodes
            )
            
        if graph_data:
            col_det, col_gra = st.columns([2, 3])
            
            with col_det:
                details = graph_data["details"]
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#0f3460,#0d6e72);border-radius:14px;padding:1.2rem 1.4rem;color:#fff;margin-bottom:1rem;">
                    <div style="font-size:1.1rem;font-weight:800;margin-bottom:0.6rem;">{selected_place}</div>
                    <div style="font-size:0.85rem;opacity:0.85;line-height:1.8;">
                        {get_svg_icon("city", "svg-icon inline-icon")}
                        <b>{details['city']}</b> &nbsp;|&nbsp;
                        {get_svg_icon("rating", "svg-icon inline-icon")}
                        <b>{details['rating']} / 5.0</b><br>
                        {get_svg_icon("category", "svg-icon inline-icon")}
                        {details['category']} &nbsp;|&nbsp;
                        {get_svg_icon("price", "svg-icon inline-icon")}
                        {format_price(int(float(details['price'])))}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"<div style='font-size:0.85rem;color:var(--text-secondary);line-height:1.65;'>{details['desc']}</div>", unsafe_allow_html=True)
                
                st.markdown("---")
                mode_label = graph_data["filter_mode"]
                sort_label = graph_data["sort_by"]
                
                # Determine relation description for legend
                if mode_label == "Lokasi yang Sama":
                    relation_desc = "Menampilkan wisata-wisata di kota yang sama"
                elif mode_label == "Kategori yang Sama":
                    relation_desc = "Menampilkan wisata-wisata dengan kategori yang sama"
                elif mode_label == "Paket yang Sama":
                    relation_desc = "Menampilkan wisata-wisata dalam paket yang sama"
                else:  # Semua Relasi
                    relation_desc = "Menampilkan seluruh hubungan semantik sekaligus"
                
                st.markdown(f"""
                <div style="background:var(--bg-subtle);border-radius:10px;padding:0.9rem 1rem;font-size:0.8rem;">
                    <div style="font-weight:700;color:var(--text-primary);margin-bottom:0.5rem;">
                        {get_svg_icon("info", "svg-icon inline-icon")}
                        Legenda Graf Bertingkat
                    </div>
                    <div style="line-height:2;color:var(--text-secondary);">
                        <b style="color:var(--text-primary);">Tier 0 — Destinasi Utama:</b><br>
                        <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#3a86ff;margin-right:6px;"></span><b>Node Pusat</b> — Destinasi yang dipilih<br>
                        <br>
                        <b style="color:var(--text-primary);">Tier 1 — Entitas Terkait:</b><br>
                        <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#06d6a0;margin-right:6px;"></span>Kota (locatedIn)<br>
                        <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#ffb703;margin-right:6px;"></span>Kategori (hasCategory)<br>
                        <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#7c3aed;margin-right:6px;"></span>Paket Wisata (includedIn)<br>
                        <br>
                        <b style="color:var(--text-primary);">Tier 2 — Wisata Terkait:</b><br>
                        <span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#d1fae5;border:1px solid #6ee7b7;margin-right:6px;"></span>Wisata di kota yang sama<br>
                        <span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#fef3c7;border:1px solid #fcd34d;margin-right:6px;"></span>Wisata berkategori sama<br>
                        <span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#ede9fe;border:1px solid #c4b5fd;margin-right:6px;"></span>Wisata dalam paket sama
                    </div>
                </div>
                <div style="background:var(--bg-subtle);border-radius:10px;padding:0.9rem 1rem;font-size:0.75rem;margin-top:0.8rem;">
                    <div style="font-weight:700;color:var(--text-primary);margin-bottom:0.5rem;">Pengaturan Aktif</div>
                    <div style="line-height:1.8;color:var(--text-muted);">
                        <b>Tipe Relasi:</b> {mode_label}<br>
                        <b>Urutkan:</b> {sort_label}<br>
                        <b>Node per Relasi:</b> {graph_data["max_nodes"]}<br>
                        <div style="margin-top:0.5rem;padding-top:0.5rem;border-top:1px solid rgba(255,255,255,0.1);font-size:0.7rem;color:var(--text-secondary);">{relation_desc}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_gra:
                st.markdown(f"<div style='font-size:0.9rem;font-weight:600;color:var(--text-primary);margin-bottom:0.5rem;'>Graf Relasi Semantik</div>", unsafe_allow_html=True)
                html_code = draw_vis_network(graph_data["nodes"], graph_data["edges"])
                st.components.v1.html(html_code, height=560)
                st.markdown("<div style='font-size:0.75rem;color:var(--text-muted);margin-top:0.3rem;'>Wisata terkait bercabang dari entitas relasi (Kota/Kategori/Paket), bukan langsung dari destinasi utama, mencerminkan hubungan semantik yang sebenarnya.</div>", unsafe_allow_html=True)
        else:
            st.warning("Gagal menemukan detail hubungan semantik untuk tempat wisata yang dipilih di dalam ontology.")