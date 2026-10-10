# Bab 1 — Business Understanding

![Alur eksperimen klasifikasi enam kelas](../_static/uts-workflow.svg)

## 1.1 Latar belakang

Informasi penutup lahan membantu memahami distribusi fisik permukaan, seperti
vegetasi, kawasan terbangun, dan badan air. Citra Sentinel-2A menyediakan
pengamatan multispektral yang dapat digunakan untuk membuat klasifikasi awal
secara konsisten pada wilayah luas. Peta hasil klasifikasi perlu dibaca bersama
konteks skala, kualitas data, waktu akuisisi, dan ketidakpastian label.

Dalam eksperimen referensi, cakupan analisis adalah **Provinsi Jawa Timur**
dengan enam kelas target: sawah, bangunan/permukiman, mangrove, lahan hijau,
laut, serta danau. Data sampelnya berasal dari sumber sekunder Kementan, BIG,
dan Natural Earth. Hasil merupakan eksperimen berdasarkan label sekunder,
bukan peta tematik resmi atau validasi lapangan.

## 1.2 Tujuan dan pertanyaan analisis

1. Menyusun alur pengumpulan, pemeriksaan, dan prapemrosesan Sentinel-2A serta
   label referensi untuk Jawa Timur.
2. Membentuk fitur spektral dan indeks untuk membedakan enam kelas.
3. Membandingkan model klasifikasi pada data uji yang dipisahkan secara spasial.
4. Menampilkan jumlah sampel aktual, metrik per kelas, confusion matrix, dan
   peta pratinjau di atas basemap satelit.
5. Menyediakan bahan eksplorasi untuk membahas kawasan terbangun, pertanian,
   mangrove pesisir, vegetasi, dan badan air dalam konteks kebijakan tata ruang.

**Pertanyaan:** seberapa baik model membedakan enam kelas pada poligon yang
tidak digunakan untuk training, dan model/representasi fitur mana yang memberi
Macro-F1 tertinggi pada validasi silang berbasis poligon?

## 1.3 Penggunaan hasil dan batas kebijakan

Peta dapat membantu memilih lokasi untuk pemeriksaan lanjutan terhadap RTRW,
RDTR, kawasan mangrove, area resapan, dan badan air. Peta klasifikasi citra
tidak menetapkan hak kepemilikan atau legalitas lahan, tidak mengubah zonasi,
dan bukan pengganti peta resmi maupun verifikasi lapangan. Keputusan tata
ruang harus merujuk pada dokumen berwenang yang berlaku.

## 1.4 Definisi kelas studi

| Kelas | Makna operasional dalam eksperimen |
|---|---|
| Sawah | Sampel poligon Kementan |
| Bangunan/Permukiman | Kelas permukiman dari sampel BIG |
| Mangrove | Kelas mangrove dari sampel BIG |
| Lahan hijau | Gabungan kelas vegetasi/tutupan hijau dari sampel BIG |
| Laut | Poligon laut Natural Earth |
| Danau | Waduk/danau dari sampel BIG |

Label merupakan sampel referensi sekunder, bukan validasi lapangan baru.
Terminologi penutup lahan nasional mengacu pada SNI 7645-1:2014 sebagai
referensi konseptual; penggabungan kelas disederhanakan untuk tujuan
eksperimen dan tidak menyatakan kepatuhan penuh terhadap legenda nasional.

## 1.5 Keluaran eksperimen yang menjadi acuan

Repository referensi menyediakan 2.823 poligon sumber dan memilih 256 poligon
untuk eksperimen (50 untuk masing-masing lima kelas pertama dan 6 poligon laut).
Pembagian yang tersimpan menggunakan 204 poligon training dan 52 testing.
Angka ini merujuk pada data dan hasil eksperimen
[PSD-Klasifikasi-Lahan](https://github.com/Rahardian-Ananta/PSD-Klasifikasi-Lahan),
bukan jumlah dari input yang diunggah ke dashboard UTS ini.

![Luas hasil klasifikasi per kelas](../_static/uts-class-areas.svg)

Lihat [peta batas kabupaten/kota](https://github.com/Rahardian-Ananta/PSD-Klasifikasi-Lahan/blob/main/outputs/figures/boundary_jatim_kabkota.png)
dan [grafik sebaran sampel](https://github.com/Rahardian-Ananta/PSD-Klasifikasi-Lahan/blob/main/outputs/figures/sebaran_per_kelas.png)
di repository sumber.
