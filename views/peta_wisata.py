import streamlit as st
import json
from utils.icons import get_hero_style, get_svg_icon
from utils.helpers import format_price

def render_peta_wisata(df_tourism, all_cities, all_categories, min_r, max_r):
    img_style = get_hero_style("public/peta.webp",  bg_position="center bottom")
    st.markdown(f"""
    <div class="hero-banner" style="{img_style} padding:2rem 2.5rem;">
        <div class="hero-title" style="font-size:1.8rem;">{get_svg_icon("map")} Peta Sebaran Wisata</div>
        <div class="hero-subtitle">Visualisasi lokasi geografis seluruh destinasi wisata Indonesia</div>
    </div>
    """, unsafe_allow_html=True)

    if df_tourism.empty:
        st.warning("Data wisata tidak tersedia.")
        return

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
