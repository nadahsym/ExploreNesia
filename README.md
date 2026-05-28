# 🗺️ Semantic Tourism Search System

Aplikasi pencarian wisata Indonesia berbasis **Semantic Web** menggunakan Streamlit + Pandas.

---

## 📁 Struktur Project

```
semantic_tourism/
├── app.py                  ← Aplikasi utama Streamlit
├── requirements.txt        ← Dependensi Python
├── README.md               ← Dokumentasi ini
└── data/
    ├── tourism_with_id.csv ← Dataset 437 tempat wisata
    └── package_tourism.csv ← Dataset paket wisata
```

---

## 🚀 Cara Menjalankan

### 1. Install dependensi
```bash
pip install -r requirements.txt
```

### 2. Jalankan aplikasi
```bash
streamlit run app.py
```

### 3. Buka di browser
```
http://localhost:8501
```

---

## ✨ Fitur Saat Ini

| Halaman         | Fitur                                                         |
|-----------------|---------------------------------------------------------------|
| 🏠 Beranda       | Hero banner, statistik, pencarian cepat, wisata unggulan      |
| 🔍 Cari Wisata   | Filter nama/kota/kategori/rating, sorting, pagination         |
| 📦 Paket Wisata  | Paket terkurasi dari package_tourism.csv, filter per kota     |
| 📊 Statistik     | Grafik distribusi, tabel preview dataset                      |

---

## 🗓️ Roadmap Integrasi Semantic Web

- [ ] Konversi dataset ke format **RDF/Turtle** (.ttl)
- [ ] SPARQL endpoint dengan **Apache Jena Fuseki**
- [ ] Query pencarian via **SPARQLWrapper**
- [ ] **Knowledge Graph** wisata Indonesia
- [ ] Recommendation System berbasis **linked data**

---

## 📦 Dataset

- **tourism_with_id.csv** — 437 tempat wisata (Jakarta, Yogyakarta, Bandung, Semarang, Surabaya)
- **package_tourism.csv** — Paket wisata terkurasi per kota
