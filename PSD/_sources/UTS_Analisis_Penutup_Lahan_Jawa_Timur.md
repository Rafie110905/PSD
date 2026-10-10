# UTS SIG: Analisis Spasial Penutup Lahan dan Kebijakan di Jawa Timur

**Klasifikasi enam kelas dari Sentinel-2A, referensi terbuka, dan WebGIS**

> **Status data dan hasil.** Repository ini belum berisi raster Sentinel-2A,
> label ESA WorldCover untuk seluruh Jawa Timur, batas provinsi, atau poligon
> danau/ranu. Angka sampel dan skor eksperimen aktual karena itu belum dihitung.
> Tidak ada angka dari repository referensi yang dipindahkan ke laporan ini.

Laporan disusun mengikuti enam tahap kerja yang digunakan pada referensi:
**Business Understanding → Data Understanding → Data Preprocessing → Modeling
→ Evaluation → WebGIS & Deployment**. Susunan ini menjadi panduan narasi dan
dashboard saja. Cakupan data, label proksi, metode eksperimen, serta semua hasil
tetap spesifik untuk UTS ini.

## Enam bab

1. [Business Understanding — tujuan dan pertanyaan analisis](https://rafie110905.github.io/PSD/UTS_Jatim_Bab_01_Business_Understanding.html)
2. [Data Understanding — data, band Sentinel-2A, dan label](https://rafie110905.github.io/PSD/UTS_Jatim_Bab_02_Data_Understanding.html)
3. [Data Preprocessing — penyelarasan, fitur, dan sampel](https://rafie110905.github.io/PSD/UTS_Jatim_Bab_03_Data_Preprocessing.html)
4. [Modeling — perbandingan model klasifikasi](https://rafie110905.github.io/PSD/UTS_Jatim_Bab_04_Modeling.html)
5. [Evaluation — pembagian training/testing dan evaluasi](https://rafie110905.github.io/PSD/UTS_Jatim_Bab_05_Evaluation.html)
6. [WebGIS & Deployment — peta, dashboard, dan kebijakan](https://rafie110905.github.io/PSD/UTS_Jatim_Bab_06_WebGIS_Deployment.html)

## Aplikasi dan data

Aplikasi Streamlit menyediakan tujuh halaman dashboard: **Ringkasan, Alur Data
→ Model, Peta Klasifikasi, Luas per Kelas, Evaluasi Model, Data & Unduhan,** dan
**Metodologi**. Source ada di [`app.py`](https://github.com/Rafie110905/PSD/blob/main/PSD/gis_uts/app.py),
algoritma di [`classifier.py`](https://github.com/Rafie110905/PSD/blob/main/PSD/gis_uts/classifier.py),
dan petunjuk menjalankan/deploy ada di [`README.md`](https://github.com/Rafie110905/PSD/blob/main/PSD/gis_uts/README.md).

Enam kelas keluaran adalah **Sawah***, **Bangunan**, **Mangrove**, **Lahan
hijau**, **Perairan terbuka**, dan **Danau/Ranu***. Tanda bintang menandai label
proksi: WorldCover cropland tidak khusus sawah, dan pemisahan air danau
bergantung pada kelengkapan poligon OpenStreetMap. Hasil peta merupakan
pratinjau eksperimen, bukan peta resmi atau hasil survei lapangan.

Untuk memahami metodologi, batasan label, serta keluaran yang masih menunggu
data, lanjutkan dari Bab 1 sampai Bab 6 menggunakan daftar isi.
