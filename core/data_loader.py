import streamlit as st
import pandas as pd
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON
import re

sparql = SPARQLWrapper("http://localhost:3030/tourism/query")

@st.cache_resource
def load_ontology_graph(path: str = "tourism_ontology.ttl") -> rdflib.Graph:
    """Memuat ontologi TTL sebagai fallback jika Fuseki tidak tersedia."""
    g = rdflib.Graph()
    try:
        g.parse(path, format="turtle")
    except Exception as e:
        st.warning(f"Gagal memuat ontologi lokal: {e}")
    return g

def _sparql_query(query_str: str, _g: rdflib.Graph = None) -> list:
    """
    Eksekusi SPARQL query:
    1. Coba ke Apache Jena Fuseki (sumber utama).
    2. Jika gagal atau kosong, fallback ke rdflib (TTL lokal).
    Mengembalikan list of dicts dengan key = nama variabel SPARQL.
    """
    # ── Coba Fuseki ──
    try:
        sparql.setQuery(query_str)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        bindings = results["results"]["bindings"]
        if bindings:  # hanya return jika ada data
            return [{k: v["value"] for k, v in row.items()} for row in bindings]
    except Exception:
        pass  # Fuseki tidak tersedia

    # ── Fallback: rdflib ──
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
    return df

def get_sparql_tourism(search_q, filter_city, filter_cat, filter_rating, _g=None):
    """
    Fungsi untuk memfilter data berdasarkan input user di halaman 'Cari Wisata'.
    Mengambil data dari fungsi load_tourism_data yang sudah dicache untuk efisiensi.
    """
    df = load_tourism_data(_g)
    
    if df.empty:
        return df
        
    if search_q:
        df = df[df['Place_Name'].str.contains(search_q, case=False, na=False)]
    if filter_city != "Semua Kota":
        df = df[df['City'] == filter_city]
    if filter_cat != "Semua Kategori":
        df = df[df['Category'] == filter_cat]
        
    df = df[df['Rating'] >= filter_rating]
    
    return df
