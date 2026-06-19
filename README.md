# ExploreNesia - Semantic Tourism Search System

ExploreNesia adalah aplikasi pencarian dan eksplorasi wisata Indonesia berbasis Semantic Web. Aplikasi ini dibangun menggunakan Streamlit, RDF/OWL Ontology, SPARQL, dan Knowledge Graph untuk menghubungkan 437 destinasi wisata di 5 kota besar (Jakarta, Yogyakarta, Bandung, Semarang, dan Surabaya).

---

## Panduan Instalasi

### Prasyarat Sistem
Sebelum memulai instalasi, pastikan sistem Anda telah memenuhi persyaratan berikut:
* Python versi 3.9 atau yang lebih baru.
* Java JDK atau JRE versi 11 atau yang lebih baru (diperlukan hanya jika ingin menjalankan Apache Jena Fuseki).
* Koneksi internet untuk memuat visualisasi graf interaktif (Vis-Network) dan font web.

### Langkah Instalasi

1. **Unduh Kode Sumber**
   Ekstrak file project ke dalam direktori kerja Anda, kemudian buka terminal/command prompt pada direktori tersebut:
   ```bash
   cd ExploreNesia
   ```

2. **Buat Virtual Environment (Opsional)**
   Membuat lingkungan python terisolasi sangat disarankan:
   ```bash
   python -m venv venv
   
   # Untuk Windows (PowerShell / CMD)
   venv\Scripts\activate
   
   # Untuk macOS / Linux
   source venv/bin/activate
   ```

3. **Instal Dependensi Python**
   Pasang semua pustaka yang dibutuhkan menggunakan pip:
   ```bash
   pip install -r requirements.txt
   ```
   Pustaka utama yang diinstal meliputi:
   * `streamlit`: Framework untuk antarmuka pengguna web.
   * `pandas`: Manipulasi dataset dalam format tabel.
   * `rdflib`: Parsing dan manipulasi RDF lokal (Graph).
   * `SPARQLWrapper`: Antarmuka koneksi ke SPARQL endpoint Fuseki.
   * `scikit-learn`: Komputasi TF-IDF dan Cosine Similarity untuk sistem rekomendasi.

4. **Konfigurasi Apache Jena Fuseki (Opsional untuk Cari Wisata)**
   Halaman Cari Wisata menggunakan Apache Jena Fuseki sebagai server SPARQL query. Jika Fuseki tidak dijalankan, aplikasi akan otomatis menggunakan fallback database RDF lokal (`rdflib`).
   
   Untuk menjalankan Fuseki:
   * Unduh Apache Jena Fuseki dari situs resmi Apache Jena.
   * Jalankan server melalui terminal di folder Fuseki Anda:
     ```bash
     # Windows
     fuseki-server.bat --update --mem /tourism
     
     # macOS / Linux
     ./fuseki-server --update --mem /tourism
     ```
   * Buka browser dan akses `http://localhost:3030`.
   * Pilih dataset `tourism`, buka tab "Upload data", lalu unggah file `tourism_ontology.ttl`.

5. **Menjalankan Aplikasi**
   Jalankan Streamlit dari folder project utama:
   ```bash
   streamlit run app.py
   ```
   Aplikasi akan otomatis terbuka pada browser default di alamat `http://localhost:8501`.

---

## Panduan Pengguna

Aplikasi ini dibagi menjadi beberapa menu navigasi utama yang dapat diakses melalui sidebar kiri:

### 1. Beranda
* **Statistik Cepat**: Menampilkan ringkasan jumlah tempat wisata, kota, kategori, dan rata-rata rating.
* **Pencarian Cepat**: Ketik sebagian atau seluruh nama tempat wisata pada kolom pencarian untuk melihat ringkasan deskripsi tempat tersebut secara langsung.
* **Wisata Unggulan**: Menampilkan destinasi dengan rating tertinggi di Indonesia.

### 2. Cari Wisata
Halaman utama untuk mencari tempat wisata secara detail menggunakan query SPARQL.
* **Filter Pencarian**: Anda dapat menyaring data berdasarkan nama wisata, pilihan kota, kategori wisata, dan rating minimum.
* **Pagination**: Gunakan tombol "Sebelumnya" dan "Berikutnya" di bagian atas atau bawah daftar untuk melihat halaman data selanjutnya.
* **Rekomendasi AI**: Klik tombol "Lihat Rekomendasi" pada kartu tempat wisata untuk menampilkan 3 rekomendasi tempat wisata serupa yang dihitung berdasarkan metode TF-IDF Vectorizer dan Cosine Similarity.

### 3. Paket Wisata
Menampilkan daftar paket perjalanan wisata terkurasi.
* **Pilih Kota**: Pilih kota yang diinginkan untuk melihat paket perjalanan khusus di kota tersebut.
* **Destinasi Paket**: Setiap paket menampilkan rute perjalanan berisi tempat-tempat wisata yang direkomendasikan untuk dikunjungi secara berurutan.

### 4. Statistik
Menampilkan analisis grafis dari dataset yang ada.
* **Grafik Batang**: Distribusi jumlah tempat wisata berdasarkan kota dan kategori.
* **Distribusi Rating**: Histogram sebaran nilai rating tempat wisata.
* **Tabel Data**: Menampilkan pratinjau data mentah dari file CSV.

### 5. Peta Wisata
Menampilkan koordinat tempat wisata secara visual di peta interaktif.
* **Filter Peta**: Saring lokasi berdasarkan kota, kategori, dan rating untuk memplot titik koordinat wisata yang relevan di peta.

### 6. Relasi Semantik
Menampilkan visualisasi Graph interaktif (Knowledge Graph) yang merepresentasikan hubungan semantik antar entitas di ontologi.
* **Pilih Wisata**: Tentukan tempat wisata yang ingin dianalisis hubungannya.
* **Pengaturan Graf**: Anda dapat memfilter jenis relasi (misalnya hanya relasi satu kota, satu kategori, atau satu paket) dan mengatur jumlah maksimal node tetangga yang ditampilkan.
* **Visualisasi Interaktif**: Tarik (drag) node untuk memindahkan posisinya, gunakan scroll mouse untuk memperbesar/memperkecil (zoom), dan arahkan kursor ke node untuk melihat keterangan lebih detail.

---

## Contoh Hasil

Berikut adalah beberapa contoh representasi data dan hasil keluaran dari aplikasi:

### 1. Contoh Data Tempat Wisata (Hasil Query SPARQL)

| Nama Wisata | Kota | Kategori | Harga Tiket | Rating |
| :--- | :--- | :--- | :--- | :--- |
| Monumen Nasional | Jakarta | Budaya | Rp 15.000 | 4.6 |
| Taman Pintar Yogyakarta | Yogyakarta | Taman Hiburan | Rp 12.000 | 4.5 |
| Kawah Putih | Bandung | Cagar Alam | Rp 25.000 | 4.4 |
| Lawang Sewu | Semarang | Budaya | Rp 10.000 | 4.5 |

### 2. Contoh Hubungan Relasi Semantik (Ontologi RDF)
Visualisasi graf merepresentasikan entitas dalam bentuk node dan relasi dalam bentuk edge terarah. Contoh representasi triple yang dihasilkan:

```text
[Monumen Nasional] -- (locatedIn) --> [Jakarta]
[Monumen Nasional] -- (hasCategory) --> [Budaya]
[Paket Wisata 1] -- (includes) --> [Monumen Nasional]
```

### 3. Contoh Hasil Rekomendasi Tempat Wisata
Saat menekan tombol "Lihat Rekomendasi" pada **Kawah Putih** (Bandung, Cagar Alam), sistem akan menghitung kemiripan deskripsi dan menghasilkan rekomendasi berikut:

* **Rekomendasi 1**: Tangkuban Perahu (Bandung, Cagar Alam) - Skor Kemiripan: 0.85
* **Rekomendasi 2**: Tebing Keraton (Bandung, Cagar Alam) - Skor Kemiripan: 0.76
* **Rekomendasi 3**: Kawah Rengganis Cibuni (Bandung, Cagar Alam) - Skor Kemiripan: 0.72
