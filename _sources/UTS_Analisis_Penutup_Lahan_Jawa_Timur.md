# UTS SIG: Analisis Spasial Penutup Lahan dan Kebijakan di Jawa Timur

**Klasifikasi multikelas berbasis Sentinel-2A, label referensi terbuka, dan validasi spasial**

> **Status eksperimen.** Repository saat ini belum berisi citra Sentinel-2 seluruh Jawa Timur, raster referensi ESA WorldCover 2021 untuk AOI, maupun poligon danau/ranu. Karena itu, metrik dan jumlah sampel aktual belum dapat dihitung di halaman ini. Jalankan aplikasi Streamlit setelah menyediakan data untuk menghasilkan angka train/test, metrik, dan peta tanpa mengarang hasil.

## 1. Ringkasan

Studi ini merancang alur SIG untuk memetakan enam kategori penutup lahan di Provinsi Jawa Timur: **sawah, bangunan, mangrove, lahan hijau, perairan terbuka (laut/air terbuka), serta danau/ranu**. Data spektral Sentinel-2A L2A diolah menjadi fitur reflektansi dan indeks; Random Forest, Extra Trees, HistGradientBoosting, dan Support Vector Machine (RBF) dibandingkan dengan satu holdout spasial yang sama. Model dengan Macro-F1 tertinggi dipilih dan divisualisasikan pada citra satelit melalui Folium.

Label awal diperoleh melalui *crosswalk* ESA WorldCover 2021 dan poligon danau OpenStreetMap (OSM). Ini adalah **label proksi untuk eksperimen**, bukan sampel validasi lapangan dan bukan peta tematik resmi Indonesia. Khususnya, kelas cropland ESA tidak identik dengan sawah, dan kelas air permanen ESA tidak membedakan laut dari danau. Interpretasi hasil harus mempertimbangkan perbedaan tersebut.

## 2. Tujuan analisis

1. Menghasilkan peta awal enam kelas penutup lahan pada wilayah administrasi Jawa Timur.
2. Menjelaskan pola spasial sawah, kawasan terbangun, mangrove, vegetasi, dan perairan sebagai bahan eksplorasi SIG.
3. Mengukur dan membandingkan empat model menggunakan training/testing yang dipisah secara spasial.
4. Menyajikan jumlah sampel per kelas, fitur, confusion matrix, metrik per kelas, dan peta pada basemap satelit.
5. Menyediakan bukti awal yang dapat membantu diskusi tata ruang, perlindungan mangrove, kawasan resapan, dan sempadan air; bukan menggantikan peta resmi, penetapan zonasi, atau survei lapangan.

## 3. Data understanding

### 3.1 Data yang tersedia dan yang masih diperlukan

Pemeriksaan repository menemukan AOI GeoJSON dan sampel shapefile sawah/bukan-sawah untuk Bangkalan. **Tidak ditemukan** GeoTIFF Sentinel-2, mosaik ESA WorldCover untuk Jawa Timur, batas provinsi Jawa Timur, atau poligon danau/ranu. Sampel Bangkalan dua kelas tidak cukup untuk mengklaim eksperimen enam kelas seluruh provinsi.

| Dataset | Peran | Status |
|---|---|---|
| Sentinel-2A Level-2A | Fitur reflektansi dan indeks vegetasi/air | Belum tersedia; input GeoTIFF 10-band diperlukan |
| ESA WorldCover 2021 v200 | Label kelas awal 10 m | Belum tersedia di repository; perlu raster/tile yang menutupi AOI |
| Batas administrasi Provinsi Jawa Timur | Masking dan cakupan studi | Perlu GeoJSON dengan CRS |
| Poligon danau/ranu OSM | Membantu memisahkan piksel air danau dari air terbuka | Perlu GeoJSON; sifat dan kelengkapan OSM bervariasi |
| Data sampel sawah/bukan-sawah Bangkalan | Contoh data lokal dua kelas | Tersedia, tetapi tidak menjadi sampel enam kelas Jawa Timur |

### 3.2 Data collecting

**Sentinel-2A.** Gunakan produk Level-2A (*Bottom-of-Atmosphere surface reflectance*) pada satu periode yang relevan, mask awan/bayangan awan, lalu bentuk komposit multi-temporal untuk mengurangi awan dan variasi satu tanggal. Ekspor GeoTIFF yang mencakup AOI dengan band berurutan **B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12** pada satu grid yang sama. Band B11/B12 asli 20 m; resampling ke 10 m menyamakan grid tetapi tidak meningkatkan resolusi informasinya. Simpan tanggal/rentang komposit, resolusi, CRS, skala/offset, dan sumber unduhan. Untuk ekspor provinsi yang masih mudah diunggah, contoh ini dapat disiapkan pada grid 100 m; resolusi akhir harus dicantumkan dan hasil tidak ditafsirkan sebagai peta 10 m.

**ESA WorldCover.** Unduh produk kelas **2021 v200** yang menutupi AOI. Dataset global 10 m tersebut merupakan gabungan analisis Sentinel-1 dan Sentinel-2 dengan sistem kelas FAO LCCS. Pertahankan kode asli sebelum melakukan crosswalk. Beri atribusi peta “© ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data 2021 processed by ESA WorldCover consortium” dan sitasi produk.

**Batas dan air daratan.** Siapkan batas resmi Provinsi Jawa Timur sebagai GeoJSON dan poligon danau/ranu dari OSM. Pastikan kedua data vektor memiliki CRS yang diketahui. Catat tanggal unduh OSM karena peta ini diperbarui oleh kontributor dan objek yang belum dipetakan tidak akan muncul.

**Pemeriksaan sebelum klasifikasi.** Verifikasi CRS, transform, rentang nilai, resolusi dan overlap raster; buat RGB komposit; pastikan WorldCover dan Sentinel-2 benar-benar menutup AOI. Tinjau poligon danau di atas citra satelit. Wilayah berawan/tanpa data tidak boleh dihitung sebagai suatu kelas.

#### Contoh pengumpulan komposit melalui Google Earth Engine

Unggah batas administrasi Jawa Timur ke Earth Engine Assets, lalu ganti nama asset pada `roi`. Kode berikut mengekspor stack Sentinel-2 10-band tahun 2021 pada skala 100 m serta peta WorldCover yang diringkas ke moda kelas 100 m. Skala ini dimaksudkan untuk contoh provinsi dan batas upload aplikasi, bukan pemetaan rinci.

```javascript
var roi = ee.FeatureCollection('projects/PROJECT_ANDA/assets/jawa_timur').geometry();

function maskClouds(image) {
  var scl = image.select('SCL');
  var clear = scl.neq(0).and(scl.neq(1)).and(scl.neq(3))
    .and(scl.neq(8)).and(scl.neq(9)).and(scl.neq(10)).and(scl.neq(11));
  return image.updateMask(clear);
}

var bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12'];
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(roi)
  .filterDate('2021-01-01', '2022-01-01')
  .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', 70))
  .map(maskClouds)
  .select(bands)
  .median()
  .clip(roi)
  .toInt16();  // Nilai DN 0–10000; aplikasi mengubahnya ke reflektansi.

var wc10 = ee.ImageCollection('ESA/WorldCover/v200').first().select('Map');
var wc100 = wc10
  .reduceResolution({reducer: ee.Reducer.mode(), maxPixels: 1024})
  .reproject({crs: 'EPSG:6933', scale: 100})
  .clip(roi);

Export.image.toDrive({
  image: s2, description: 'JawaTimur_Sentinel2_2021_100m',
  region: roi, crs: 'EPSG:6933', scale: 100, maxPixels: 1e13,
  fileFormat: 'GeoTIFF', formatOptions: {cloudOptimized: true}
});
Export.image.toDrive({
  image: wc100, description: 'JawaTimur_WorldCover_2021_100m',
  region: roi, crs: 'EPSG:6933', scale: 100, maxPixels: 1e13,
  fileFormat: 'GeoTIFF', formatOptions: {cloudOptimized: true}
});
```

Ekspor dibuat **dua kali** dalam satu grid. Unduh GeoTIFF dari Google Drive lalu unggah ke aplikasi. Untuk danau, cari poligon `natural=water`/`water=lake` di Jawa Timur melalui Overpass Turbo, ekspor GeoJSON, periksa hasilnya terhadap citra, dan catat tanggal pengambilan. Jangan menyamakan seluruh air kelas ESA 80 sebagai laut.

### 3.3 Catatan kualitas label dan batas interpretasi

Crosswalk yang dipakai dalam aplikasi:

| Kelas keluaran | Sumber label awal | Interpretasi/keterbatasan |
|---|---|---|
| Sawah* | ESA WorldCover 40 — Cropland | Cropland juga mencakup kebun dan lahan pertanian lain; bukan inventaris sawah |
| Bangunan | ESA WorldCover 50 — Built-up | Kelas terbangun, bukan fungsi bangunan |
| Mangrove | ESA WorldCover 95 — Mangroves | Kelas referensi mangrove global |
| Lahan hijau | ESA WorldCover 10/20/30 — Tree cover, Shrubland, Grassland | Gabungan hutan/tutupan pohon, semak, dan padang rumput; bukan satu tipe vegetasi homogen |
| Perairan terbuka* | ESA WorldCover 80 — Permanent water bodies, di luar poligon danau OSM | Berpotensi mencampurkan laut, sungai, tambak, waduk, dan air permanen lain |
| Danau/Ranu* | ESA WorldCover 80 yang tumpang-susun poligon danau/ranu OSM | Sangat bergantung pada kelengkapan dan geometri OSM |

`*` Menandai proksi. Ketidakcocokan tanggal, piksel campuran di batas poligon, salah klasifikasi WorldCover, dan kelengkapan OSM dapat menimbulkan kesalahan. Untuk pernyataan akurasi tematik diperlukan titik referensi independen, interpretasi visual citra resolusi tinggi, atau survei lapangan dengan desain sampling yang dapat dipertanggungjawabkan.

## 4. Acuan klasifikasi penutup lahan Indonesia

Gunakan **SNI 7645-1:2014, Klasifikasi penutup lahan — Bagian 1: Skala kecil dan menengah**, sebagai acuan terminologi/struktur penutup lahan nasional. Cocokkan definisi kelas dan tingkat hirarki dengan metadata dan skala peta yang digunakan; jangan menyamakan satu kelas spektral ESA dengan semua subkelas SNI.

Produk peta penutup lahan Kementerian Lingkungan Hidup dan Kehutanan (KLHK) juga relevan sebagai pembanding nasional dan konteks pemetaan. Sebelum mengklaim kepatuhan, periksa edisi standar, petunjuk teknis KLHK/BIG yang berlaku, skala, nomenklatur dan metadata resmi terbaru. Crosswalk eksperimen enam kelas ini disederhanakan untuk tujuan UTS dan **bukan** pengganti legenda nasional yang lengkap.

| Kelompok studi | Hubungan umum dengan nomenklatur penutup lahan nasional |
|---|---|
| Sawah | Pertanian lahan basah/sawah; proksi WorldCover cropland perlu diverifikasi |
| Bangunan | Lahan terbangun/permukiman dan infrastruktur |
| Mangrove | Hutan mangrove/vegetasi pantai; pertahankan kelas khusus |
| Lahan hijau | Disederhanakan dari beberapa tutupan bervegetasi, bukan satu subkelas |
| Perairan terbuka | Badan air terbuka; bedakan laut, sungai, tambak, dan waduk bila datanya memungkinkan |
| Danau/Ranu | Badan air danau; dibedakan memakai batas poligon OSM |

Peta ini cocok untuk latihan metode, inventarisasi awal, serta prioritas pemeriksaan. Peta klasifikasi citra tidak dengan sendirinya menetapkan hak lahan atau mengubah RTRW/RDTR. Keputusan tata ruang harus memakai dokumen resmi berwenang, skala dan proses partisipatif yang berlaku.

## 5. Band Sentinel-2A dan resolusi spasial

Instrumen MSI Sentinel-2 merekam 13 band pada resolusi asli 10 m, 20 m, atau 60 m. Aplikasi menerima 10 band reflektansi yang diperlukan, dengan band 20 m sudah diregistrasikan ke satu grid bersama.

| Band | Nama umum | Panjang gelombang tengah (≈ µm) | Resolusi asli | Kegunaan utama |
|---|---|---:|---:|---|
| B1 | Coastal aerosol | 0.443 | 60 m | Aerosol pesisir, koreksi atmosfer |
| B2 | Blue | 0.490 | 10 m | Komposit warna tampak, air dangkal |
| B3 | Green | 0.560 | 10 m | Warna vegetasi dan respons air |
| B4 | Red | 0.665 | 10 m | Serapan klorofil dan batas vegetasi |
| B5 | Red Edge 1 | 0.705 | 20 m | Kondisi vegetasi/klorofil |
| B6 | Red Edge 2 | 0.740 | 20 m | Gradien red-edge vegetasi |
| B7 | Red Edge 3 | 0.783 | 20 m | Vegetasi dan biomassa |
| B8 | Near Infrared (NIR) | 0.842 | 10 m | Vegetasi sehat dan pemisahan air |
| B8A | Narrow NIR | 0.865 | 20 m | Red-edge/NIR sempit |
| B9 | Water vapour | 0.945 | 60 m | Koreksi atmosfer/uap air |
| B10 | Cirrus | 1.375 | 60 m | Deteksi awan cirrus |
| B11 | SWIR 1 | 1.610 | 20 m | Kelembapan, tanah, lahan terbangun |
| B12 | SWIR 2 | 2.190 | 20 m | Kelembapan vegetasi, tanah dan kebakaran |

Rentang/panjang gelombang merupakan nilai nominal instrumen, bukan pengukuran kelas langsung. Indeks yang menggunakan band 20 m mewarisi resolusi efektif tersebut meskipun grid disimpan pada 10 m.

## 6. Fitur model dan rumus

Sepuluh reflektansi band B2–B12 (tidak termasuk B9 dan B10) menjadi fitur spektral langsung. Delapan indeks berikut dihitung per piksel. Semua pembagian dengan penyebut mendekati nol dijaga agar menghasilkan nilai terdefinisi.

| Fitur | Rumus | Interpretasi |
|---|---|---|
| `B2_blue`, `B3_green`, `B4_red` | Reflektansi band | Warna tampak, atmosfer, air, vegetasi |
| `B5_rededge1`, `B6_rededge2`, `B7_rededge3` | Reflektansi band | Gradien red-edge/struktur vegetasi |
| `B8_nir`, `B8A_rededge4` | Reflektansi band | Respons vegetasi; pemisahan vegetasi dan air |
| `B11_swir1`, `B12_swir2` | Reflektansi band | Kelembapan/tanah/permukaan terbangun |
| NDVI | `(B8 - B4) / (B8 + B4)` | Kehijauan/aktivitas vegetasi |
| NDWI | `(B3 - B8) / (B3 + B8)` | Indeks air berbasis Green–NIR |
| MNDWI | `(B3 - B11) / (B3 + B11)` | Mempertegas air dibanding beberapa permukaan terbangun |
| NDMI | `(B8 - B11) / (B8 + B11)` | Kelembapan kanopi/vegetasi |
| NDBI | `(B11 - B8) / (B11 + B8)` | Respons relatif permukaan terbangun |
| NDRE | `(B8A - B5) / (B8A + B5)` | Respons vegetasi red-edge |
| SAVI | `1.5 × (B8 - B4) / (B8 + B4 + 0.5)` | Vegetasi dengan koreksi pengaruh tanah |
| BSI | `((B11 + B4) - (B8 + B2)) / ((B11 + B4) + (B8 + B2))` | Tanah terbuka/permukaan cerah relatif |

Indeks merupakan fitur, bukan aturan keputusan tunggal. Awan/bayangan harus dimask sebelum penghitungan; nilai indeks dan reflektansi yang salah skala akan merusak model.

## 7. Koleksi sampel dan eksperimen

### 7.1 Jumlah kelas, training dan testing

Kelas target berjumlah **6**. Aplikasi mengambil sampel piksel seimbang hingga maksimum yang dipilih pengguna untuk masing-masing kelas. Pemisahan dilakukan berdasarkan blok spasial pada raster pratinjau agar piksel berdekatan tidak tersebar acak ke training dan testing.

**Jumlah aktual belum tersedia** karena raster 10-band Sentinel-2, label WorldCover seluruh AOI, batas provinsi, dan poligon danau belum ada di repository. Setelah data diunggah dan eksperimen dijalankan, catat tabel aktual dari aplikasi:

| Kelas | Total sampel | Training | Testing |
|---|---:|---:|---:|
| Sawah* | Diisi dari hasil aplikasi | Diisi dari hasil aplikasi | Diisi dari hasil aplikasi |
| Bangunan | Diisi dari hasil aplikasi | Diisi dari hasil aplikasi | Diisi dari hasil aplikasi |
| Mangrove | Diisi dari hasil aplikasi | Diisi dari hasil aplikasi | Diisi dari hasil aplikasi |
| Lahan hijau | Diisi dari hasil aplikasi | Diisi dari hasil aplikasi | Diisi dari hasil aplikasi |
| Perairan terbuka* | Diisi dari hasil aplikasi | Diisi dari hasil aplikasi | Diisi dari hasil aplikasi |
| Danau/Ranu* | Diisi dari hasil aplikasi | Diisi dari hasil aplikasi | Diisi dari hasil aplikasi |
| **Total** | **Diisi dari hasil aplikasi** | **Diisi dari hasil aplikasi** | **Diisi dari hasil aplikasi** |

Jangan menyalin jumlah yang disetel sebagai jumlah aktual: beberapa kelas mungkin tidak memiliki cukup piksel valid di wilayah/tile yang diunggah. Jika kelas tidak ada, eksperimen akan meminta perbaikan data alih-alih diam-diam melatih model lima kelas.

### 7.2 Model dan kriteria pemilihan

Aplikasi membandingkan:

1. **Random Forest** — ansambel pohon bagging; menangani hubungan nonlinier dan interaksi fitur.
2. **Extra Trees** — ansambel pohon dengan pemilihan ambang yang lebih acak.
3. **HistGradientBoosting** — boosting pohon histogram.
4. **SVM RBF** — pemisah margin dengan kernel radial dan fitur yang diskalakan.

Semua model memakai sampel dan spatial holdout yang sama. Model dipilih dengan **Macro-F1 tertinggi** (pemecah seri: balanced accuracy), bukan memilih skor tertinggi setelah melihat ulang data uji. Akurasi keseluruhan, balanced accuracy, Macro-F1, Cohen’s κ, confusion matrix, dan metrik per kelas ditampilkan. Untuk model final seluruh AOI, lakukan validasi independen lain; holdout proksi ini bukan estimasi kinerja lapangan.

> Nilai eksperimen tidak ditampilkan sebelum data aktual diproses. Masukkan tabel dan skor aplikasi ke laporan akhir bersama seed, tanggal komposit, resolusi, blok spasial, dan sumber label.

## 8. Peta, kebijakan dan pemanfaatan

Aplikasi menampilkan komposit RGB B4/B3/B2, layer klasifikasi pratinjau, dan legenda pada **Google Satellite** / Google Satellite Hybrid melalui Folium. Google Satellite adalah layanan tile XYZ, **bukan WMS**; Folium/Leaflet dapat menambahkan WMS bila endpoint WMS pihak ketiga tersedia. Patuhi ketentuan layanan dan atribusi penyedia peta.

Peta penutup lahan dapat digunakan untuk mendiskusikan lokasi yang perlu diverifikasi terhadap RTRW/RDTR, sebaran kawasan terbangun, area mangrove dan pesisir, badan air, serta potensi konflik penggunaan lahan. Peta klasifikasi tidak membuktikan legalitas penggunaan lahan, status kepemilikan, zonasi, atau kesesuaian izin. Kebijakan harus merujuk pada dokumen tata ruang dan peta resmi yang berlaku serta verifikasi lapangan.

## 9. Menjalankan sistem informasi

Source aplikasi berada pada [`gis_uts/app.py`](https://github.com/Rafie110905/PSD/blob/main/PSD/gis_uts/app.py), fungsi eksperimen pada [`gis_uts/classifier.py`](https://github.com/Rafie110905/PSD/blob/main/PSD/gis_uts/classifier.py), serta paket pada [`gis_uts/requirements.txt`](https://github.com/Rafie110905/PSD/blob/main/PSD/gis_uts/requirements.txt). Ikuti petunjuk instalasi/deploy di [`gis_uts/README.md`](https://github.com/Rafie110905/PSD/blob/main/PSD/gis_uts/README.md).

GitHub Pages hanya menyajikan dokumentasi statis. Aplikasi interaktif perlu dijalankan terpisah melalui Streamlit Community Cloud. Deploy mengharuskan pemilik repository masuk ke akun Streamlit dan memilih main file `PSD/gis_uts/app.py`; belum ada URL instance Streamlit sampai proses itu disetujui/dijalankan.

## 10. Referensi

1. Badan Standardisasi Nasional. **SNI 7645-1:2014, Klasifikasi penutup lahan — Bagian 1: Skala kecil dan menengah.** Periksa katalog BSN untuk status/edisi terkini sebelum mengutip definisi normatif.
2. European Space Agency / Copernicus. [Sentinel-2 Level-2A — band, panjang gelombang, dan resolusi](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a).
3. ESA WorldCover. [Akses data dan ukuran/format produk](https://esa-worldcover.org/en/data-access).
4. ESA WorldCover Consortium. [ESA WorldCover 2021 v200 Product/User documentation dan data citation](https://github.com/ESA-WorldCover/esa-worldcover-datasets); DOI: [10.5281/zenodo.7254221](https://doi.org/10.5281/zenodo.7254221).
5. ESA WorldCover. [Daftar kode dan arti kelas WorldCover di STAC](https://planetarycomputer.microsoft.com/api/stac/v1/collections/esa-worldcover).
6. OpenStreetMap contributors. [OpenStreetMap copyright and attribution](https://www.openstreetmap.org/copyright).
