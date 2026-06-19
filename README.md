# 🗺️ ExploreNesia — Semantic Tourism Search System

> Aplikasi pencarian dan eksplorasi wisata Indonesia berbasis **Semantic Web**, dibangun menggunakan Streamlit, RDF/OWL Ontology, SPARQL, dan Knowledge Graph.

---

## 📋 Daftar Isi

1. [Tentang Aplikasi](#-tentang-aplikasi)
2. [Fitur Utama](#-fitur-utama)
3. [Prasyarat](#-prasyarat)
4. [Struktur Project](#-struktur-project)
5. [Instalasi](#-instalasi)
6. [Pengaturan Apache Jena Fuseki](#-pengaturan-apache-jena-fuseki-untuk-sparql)
7. [Menjalankan Aplikasi](#-menjalankan-aplikasi)
8. [Panduan Penggunaan](#-panduan-penggunaan)
9. [Arsitektur Semantik](#-arsitektur-semantik)
10. [Dataset](#-dataset)

---

## 🧭 Tentang Aplikasi

**ExploreNesia** adalah aplikasi web berbasis Semantic Web untuk menjelajahi 437 destinasi wisata Indonesia di 5 kota besar: Jakarta, Yogyakarta, Bandung, Semarang, dan Surabaya.

Aplikasi ini mengintegrasikan teknologi:
- **RDF/OWL Ontology** — representasi pengetahuan wisata dalam format `.ttl` (Turtle)
- **SPARQL** — query bahasa semantik via Apache Jena Fuseki endpoint
- **Knowledge Graph** — relasi antar entitas (Tempat → Kota → Kategori → Paket Wisata)
- **TF-IDF + Cosine Similarity** — sistem rekomendasi berbasis kemiripan konten
- **Vis-Network** — visualisasi graf relasi semantik interaktif

---

## ✨ Fitur Utama

| Halaman | Fitur |
|---|---|
| 🏠 **Beranda** | Hero banner, statistik dataset, pencarian cepat nama wisata, wisata unggulan berdasarkan rating |
| 🔍 **Cari Wisata** | Query SPARQL ke Fuseki, filter nama/kota/kategori/rating, sorting, pagination, rekomendasi AI |
| 📦 **Paket Wisata** | Kumpulan paket perjalanan terkurasi per kota, wisata populer per kota |
| 📊 **Statistik** | Grafik distribusi kota & kategori, distribusi rating, preview raw dataset |
| 🌐 **Relasi Semantik** | Graf interaktif hubungan antar entitas wisata (kota, kategori, paket) dari Knowledge Graph |

---

## ⚙️ Prasyarat

Sebelum menjalankan aplikasi, pastikan sudah terinstal:

- **Python** `>= 3.9`
- **pip** (Python package manager)
- **Java JDK/JRE** `>= 11` (diperlukan untuk Apache Jena Fuseki)
- **Apache Jena Fuseki** `>= 4.x` (SPARQL server, opsional — hanya untuk halaman *Cari Wisata*)
- Koneksi internet (untuk memuat font Google Fonts dan library Vis-Network via CDN)

> **Catatan:** Halaman 🌐 *Relasi Semantik* membaca ontologi langsung dari file `tourism_ontology.ttl` lokal menggunakan `rdflib`, sehingga **tidak** memerlukan Fuseki untuk berfungsi.

---

## 📁 Struktur Project

```
ExploreNesia/
├── app.py                    ← Aplikasi utama Streamlit (semua halaman)
├── requirements.txt          ← Daftar dependensi Python
├── tourism_ontology.ttl      ← File ontologi RDF/OWL (Knowledge Graph wisata Indonesia)
├── README.md                 ← Dokumentasi ini
└── data/
    ├── tourism_with_id.csv   ← Dataset 437 tempat wisata (untuk dropdown & beranda)
    └── package_tourism.csv   ← Dataset 100 paket wisata terkurasi per kota
```

---

## 💿 Instalasi

### 1. Clone atau unduh repository

```bash
git clone <url-repository>
cd ExploreNesia
```

### 2. (Opsional) Buat virtual environment

```bash
python -m venv venv

# Aktifkan (Windows)
venv\Scripts\activate

# Aktifkan (macOS/Linux)
source venv/bin/activate
```

### 3. Install semua dependensi Python

```bash
pip install -r requirements.txt
```

Dependensi utama yang akan terinstal:

| Library | Fungsi |
|---|---|
| `streamlit` | Framework web app |
| `pandas` | Manipulasi dan loading dataset CSV |
| `scikit-learn` | TF-IDF vectorizer & cosine similarity (rekomendasi) |
| `SPARQLWrapper` | Koneksi ke SPARQL endpoint (Apache Jena Fuseki) |
| `rdflib` | Parsing & query ontologi RDF lokal (graf relasi semantik) |

---

## 🔥 Pengaturan Apache Jena Fuseki (untuk SPARQL)

> **Lewati bagian ini jika hanya ingin melihat halaman Beranda, Paket Wisata, Statistik, atau Relasi Semantik.** Fuseki hanya diperlukan untuk halaman **🔍 Cari Wisata**.

### Langkah 1 — Unduh Apache Jena Fuseki

1. Buka: https://jena.apache.org/download/
2. Unduh **Apache Jena Fuseki** (file `.zip` atau `.tar.gz`)
3. Ekstrak ke folder yang mudah diakses, misalnya `C:\fuseki\`

### Langkah 2 — Jalankan Fuseki Server

Buka terminal di folder Fuseki, lalu jalankan:

```bash
# Windows
fuseki-server.bat --update --mem /tourism

# macOS / Linux
./fuseki-server --update --mem /tourism
```

Server akan berjalan di: `http://localhost:3030`

> **Penting:** Nama dataset harus **`tourism`** (sesuai konfigurasi di `app.py`).

### Langkah 3 — Upload Ontologi ke Fuseki

1. Buka browser, akses `http://localhost:3030`
2. Klik dataset **`tourism`** → Tab **Upload data**
3. Pilih file `tourism_ontology.ttl` dari folder project
4. Klik **Upload** — tunggu hingga selesai (file ~500KB)
5. Verifikasi: klik tab **Info**, pastikan jumlah triple `> 6000`

### Langkah 4 — Verifikasi Koneksi

Coba query SPARQL sederhana di tab **Query** pada UI Fuseki:

```sparql
PREFIX : <http://www.semanticweb.org/tourism-ontology#>

SELECT (COUNT(?place) AS ?total)
WHERE {
    ?place a :TouristPlace .
}
```

Hasil yang diharapkan: **437 tempat wisata**.

---

## 🚀 Menjalankan Aplikasi

Setelah instalasi selesai:

```bash
streamlit run app.py
```

Aplikasi akan otomatis terbuka di browser pada:

```
http://localhost:8501
```

Untuk menghentikan: tekan `Ctrl + C` di terminal.

---

## 📖 Panduan Penggunaan

### 🏠 Beranda

Halaman utama yang menampilkan ringkasan dataset wisata Indonesia.

- **Statistik** — Total wisata, jumlah kota, kategori, dan rata-rata rating
- **Pencarian Cepat** — Ketik nama tempat wisata pada kotak teks untuk melihat hasil langsung
- **Wisata Unggulan** — 6 destinasi dengan rating tertinggi dari seluruh dataset

### 🔍 Cari Wisata (SPARQL)

Halaman pencarian utama yang mengambil data **langsung dari Knowledge Graph** via SPARQL.

> **Memerlukan Apache Jena Fuseki yang berjalan.**

**Cara menggunakan:**
1. Ketik nama wisata pada kolom **Nama Wisata** (opsional)
2. Pilih **Kota** untuk memfilter berdasarkan lokasi
3. Pilih **Kategori** (Budaya, Cagar Alam, Taman Hiburan, dll.)
4. Geser slider **Rating Minimum** untuk menyaring berdasarkan nilai minimum
5. Klik tombol **💡 Lihat Rekomendasi** pada kartu wisata untuk mendapatkan saran tempat serupa

**Sistem Rekomendasi:**
Menggunakan algoritma **TF-IDF** untuk mengubah teks (kategori + kota + deskripsi) menjadi representasi vektor, kemudian menghitung **Cosine Similarity** antar semua tempat wisata untuk menemukan 3 destinasi paling mirip.

### 📦 Paket Wisata

Menampilkan koleksi 100 paket perjalanan wisata terkurasi yang berisi kombinasi beberapa tempat wisata per paket.

**Cara menggunakan:**
1. Pilih **kota** dari dropdown untuk memfilter paket
2. Setiap kartu menampilkan daftar tempat wisata yang termasuk dalam paket
3. Scroll ke bawah untuk melihat **Wisata Populer** di kota yang dipilih

### 📊 Statistik

Menyajikan gambaran visual dan numerik dari keseluruhan dataset.

- **Grafik Batang** — Distribusi wisata per kota dan per kategori
- **Distribusi Rating** — Sebaran nilai rating di seluruh tempat wisata
- **Preview Dataset** — Tabel interaktif 50 baris pertama dari `tourism_with_id.csv` dan `package_tourism.csv`

### 🌐 Relasi Semantik

Fitur inti Semantic Web — memvisualisasikan **hubungan semantik antar entitas** secara interaktif.

**Cara menggunakan:**
1. Pilih tempat wisata dari dropdown **"Pilih Tempat Wisata untuk Dianalisis"**
2. Panel kiri menampilkan detail lengkap: kota, kategori, rating, harga, dan deskripsi
3. Panel kanan menampilkan **Graf Interaktif** dengan node dan edge berlabel relasi semantik

**Interaksi Graf:**
- 🖱️ **Klik & Drag** node untuk menggeser posisi
- 🔍 **Scroll** untuk zoom in/out
- 🖱️ **Hover** pada node untuk melihat tooltip detail
- Graf menggunakan layout **ForceAtlas2** untuk penempatan otomatis

**Legenda Warna Node:**
| Warna | Jenis Node | Relasi |
|---|---|---|
| 🟦 Biru | Destinasi Pilihan (Pusat) | — |
| 🟩 Hijau | Kota Lokasi | `locatedIn` |
| 🟨 Kuning | Kategori Wisata | `hasCategory` |
| 🟪 Ungu | Paket Wisata | `includes` |
| ⬜ Abu-abu | Wisata Lain di Kota | `locatedIn` (dashed) |
| 🟨 Kuning muda | Wisata Lain se-Kategori | `hasCategory` (dashed) |

---

## 🧠 Arsitektur Semantik

Aplikasi ini mengimplementasikan prinsip **Semantic Web Stack**:

```
┌─────────────────────────────────────────────────┐
│                  Streamlit UI                   │
│  (Beranda · Cari Wisata · Paket · Statistik)    │
├──────────────────┬──────────────────────────────┤
│  SPARQL Query    │     rdflib (lokal)            │
│  (SPARQLWrapper) │     Graf Relasi Semantik      │
├──────────────────┼──────────────────────────────┤
│ Apache Jena      │  tourism_ontology.ttl         │
│ Fuseki Server    │  (RDF/OWL Turtle)             │
│ (port 3030)      │                               │
├──────────────────┴──────────────────────────────┤
│           Knowledge Graph                        │
│  TouristPlace ─── locatedIn ──▶ City             │
│  TouristPlace ─── hasCategory ▶ Category         │
│  TourPackage  ─── includes ───▶ TouristPlace     │
└─────────────────────────────────────────────────┘
```

**Prefix Ontologi:**
```
PREFIX : <http://www.semanticweb.org/tourism-ontology#>
```

**Kelas Utama:**
- `:TouristPlace` — Entitas tempat wisata
- `:TourPackage` — Entitas paket wisata
- `:City` — Entitas kota
- `:Category` — Entitas kategori wisata

**Properties:**
- `:hasName` — Nama entitas
- `:locatedIn` — Relasi tempat wisata ke kota
- `:hasCategory` — Relasi tempat wisata ke kategori
- `:hasPrice` — Harga tiket masuk (integer, dalam rupiah)
- `:hasRating` — Nilai rating (float, 1.0–5.0)
- `:hasDescription` — Deskripsi lengkap tempat wisata
- `:hasLat`, `:hasLong` — Koordinat geografis
- `:includes` — Relasi paket wisata ke tempat wisata
- `:hasTimeMinutes` — Estimasi durasi kunjungan (menit)

---

## 📦 Dataset

| File | Isi | Ukuran |
|---|---|---|
| `data/tourism_with_id.csv` | 437 tempat wisata (ID, nama, deskripsi, kategori, kota, harga, rating, koordinat) | ~356 KB |
| `data/package_tourism.csv` | 100 paket wisata terkurasi (kota, ID paket, daftar tempat wisata) | ~10 KB |
| `tourism_ontology.ttl` | Knowledge Graph dalam format RDF/Turtle (6.974 triple) | ~512 KB |

**Kota yang dicakup:** Jakarta · Yogyakarta · Bandung · Semarang · Surabaya

**Kategori Wisata:**
- 🏛️ Budaya
- 🌿 Cagar Alam
- 🎡 Taman Hiburan
- 🌊 Bahari
- 🛍️ Pusat Perbelanjaan
- 🕌 Tempat Ibadah

---

<div align="center">
  <sub>🗺️ <b>ExploreNesia</b> · Semantic Web Project · Powered by Streamlit, RDFLib, SPARQL & Vis-Network</sub>
</div>
