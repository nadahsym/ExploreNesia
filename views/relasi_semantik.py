import streamlit as st
import random
import json
from utils.icons import get_hero_style, get_svg_icon
from utils.helpers import format_price

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
    
    # TIER 0: Central node (destinasi utama)
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
    
    # TIER 1: Kota, Kategori, Paket Wisata
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
    
    # TIER 2: Wisata terkait melalui Tier 1
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

def render_relasi_semantik(df_tourism, _g_shared, graph_filter_mode, graph_sort_by, graph_max_nodes):
    img_style = get_hero_style("public/relasi.png", bg_position="right top", overlay_opacity=0.35)
    st.markdown(f"""
    <div class="hero-banner" style="{img_style} padding:2rem 2.5rem;">
        <div class="hero-title" style="font-size:1.8rem;">{get_svg_icon("semantic")} Visualisasi Graf Relasi Semantik</div>
        <div class="hero-subtitle">Menganalisis hubungan semantik antar konsep, kategori, kota, dan paket wisata dalam Knowledge Graph</div>
    </div>
    """, unsafe_allow_html=True)

    g_ontology = _g_shared

    if df_tourism.empty:
        st.warning("Data wisata tidak tersedia.")
        return

    all_places = sorted(df_tourism["Place_Name"].unique().tolist())

    st.markdown('<div class="search-section">', unsafe_allow_html=True)
    selected_place = st.selectbox(
        "Pilih Tempat Wisata untuk Dianalisis:",
        all_places,
        index=0
    )
    st.markdown('</div>', unsafe_allow_html=True)

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
