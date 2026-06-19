import streamlit as st

def inject_custom_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ══════════════════════════════════════
   CSS Variables — Light Mode (default)
   Rasio Kontras Tinggi & Warna Harmonik
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
    --accent-blue:       #2563eb;
    --accent-green:      #10b981;
    --accent-orange:     #f59e0b;
    --accent-purple:     #8b5cf6;
    
    --shadow-sm:         0 1px 3px rgba(15,23,42,0.08);
    --shadow-md:         0 4px 6px -1px rgba(15,23,42,0.1), 0 2px 4px -1px rgba(15,23,42,0.06);
    --shadow-hover:      0 12px 20px -3px rgba(37,99,235,0.12), 0 4px 6px -2px rgba(15,23,42,0.05);
    
    --badge-city-bg:     #eff6ff;
    --badge-city-fg:     #1e40af;
    --badge-cat-bg:      #fffbeb;
    --badge-cat-fg:      #92400e;
    --badge-rating-bg:   #ecfdf5;
    --badge-rating-fg:   #065f46;
    --badge-price-bg:    #fdf2f8;
    --badge-price-fg:    #9d174d;
    --icon-color:        #64748b;
}

/* ══════════════════════════════════════
   CSS Variables — Dark Mode
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
    --accent-blue:       #2563eb;
    --accent-green:      #10b981;
    --accent-orange:     #f59e0b;
    --accent-purple:     #8b5cf6;
    
    --badge-city-bg:     #eff6ff;
    --badge-city-fg:     #1e40af;
    --badge-cat-bg:      #fffbeb;
    --badge-cat-fg:      #92400e;
    --badge-rating-bg:   #ecfdf5;
    --badge-rating-fg:   #065f46;
    --badge-price-bg:    #fdf2f8;
    --badge-price-fg:    #9d174d;
    --icon-color:        #64748b;
}

/* ── Global Styles ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background: var(--bg-primary) !important;
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

/* ── Hero Banner ── */
.hero-banner {
    background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 50%, #115e59 100%);
    border-radius: 20px;
    padding: 2.8rem 2.8rem 2.4rem;
    margin-bottom: 2rem;
    box-shadow: 0 8px 40px rgba(0,0,0,0.15);
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.05);
}
.hero-banner::after {
    content: "";
    position: absolute;
    top: -40px;
    right: -40px;
    width: 220px;
    height: 220px;
    background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
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
}
.hero-title svg {
    color: #3b82f6;
    width: 32px;
    height: 32px;
}
.hero-subtitle {
    color: #93c5fd;
    font-size: 1rem;
    margin: 0 0 1rem;
    font-weight: 400;
    line-height: 1.5;
    max-width: 560px;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(59,130,246,0.15);
    border: 1px solid rgba(59,130,246,0.3);
    color: #93c5fd;
    font-size: 0.75rem;
    padding: 5px 14px;
    border-radius: 100px;
    letter-spacing: 0.4px;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 0.25rem;
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

/* ── Result count text ── */
[style*="color:#666"] {
    color: var(--text-secondary) !important;
}
</style>
""", unsafe_allow_html=True)
