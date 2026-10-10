# Bab 1 — Business Understanding

## 1.1 Latar belakang

Informasi penutup lahan membantu memahami distribusi fisik permukaan, seperti
vegetasi, kawasan terbangun, dan badan air. Citra Sentinel-2A menyediakan
pengamatan multispektral yang dapat digunakan untuk membuat klasifikasi awal
secara konsisten pada wilayah luas. Peta hasil klasifikasi perlu dibaca bersama
konteks skala, kualitas data, waktu akuisisi, dan ketidakpastian label.

Dalam UTS ini, cakupan analisis adalah **Provinsi Jawa Timur** dengan enam
kelas target: sawah, bangunan, mangrove, lahan hijau, perairan terbuka, serta
danau/ranu. Karena sampel lapangan enam kelas belum tersedia, data label awal
menggunakan crosswalk ESA WorldCover 2021 dan poligon danau OpenStreetMap (OSM).
Dengan demikian, produk saat ini dirancang sebagai eksperimen dan demonstrasi
SIG, bukan peta tematik resmi.

## 1.2 Tujuan dan pertanyaan analisis

1. Menyusun alur pengumpulan, pemeriksaan, dan prapemrosesan Sentinel-2A serta
   label referensi untuk Jawa Timur.
2. Membentuk fitur spektral dan indeks untuk membedakan enam kelas.
3. Membandingkan model klasifikasi pada data uji yang dipisahkan secara spasial.
4. Menampilkan jumlah sampel aktual, metrik per kelas, confusion matrix, dan
   peta pratinjau di atas basemap satelit.
5. Menyediakan bahan eksplorasi untuk membahas kawasan terbangun, pertanian,
   mangrove pesisir, vegetasi, dan badan air dalam konteks kebijakan tata ruang.

**Pertanyaan:** seberapa konsisten model membedakan enam label proksi dari
fitur Sentinel-2A pada wilayah yang tidak digunakan untuk training, dan model
mana yang memberi Macro-F1 tertinggi pada pembagian spasial yang sama?

## 1.3 Penggunaan hasil dan batas kebijakan

Peta dapat membantu memilih lokasi untuk pemeriksaan lanjutan terhadap RTRW,
RDTR, kawasan mangrove, area resapan, dan badan air. Peta klasifikasi citra
tidak menetapkan hak kepemilikan atau legalitas lahan, tidak mengubah zonasi,
dan bukan pengganti peta resmi maupun verifikasi lapangan. Keputusan tata
ruang harus merujuk pada dokumen berwenang yang berlaku.

## 1.4 Definisi kelas studi

| Kelas | Makna operasional dalam eksperimen |
|---|---|
| Sawah* | WorldCover 40 (cropland), yang juga dapat mencakup kebun dan pertanian lain |
| Bangunan | WorldCover 50 (built-up) |
| Mangrove | WorldCover 95 (mangroves) |
| Lahan hijau | Gabungan WorldCover 10, 20, dan 30 |
| Perairan terbuka | WorldCover 80 di luar poligon danau/ranu OSM |
| Danau/Ranu* | WorldCover 80 yang bertumpang-susun dengan poligon danau/ranu OSM |

`*` berarti proksi, bukan label lapangan yang diverifikasi satu per satu.
Terminologi penutup lahan nasional mengacu pada SNI 7645-1:2014 sebagai
referensi konseptual; crosswalk enam kelas ini disederhanakan untuk tujuan
eksperimen dan tidak menyatakan kepatuhan penuh terhadap legenda nasional.
