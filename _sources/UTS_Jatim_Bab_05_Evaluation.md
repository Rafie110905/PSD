# Bab 5 — Evaluation

## 5.1 Jumlah kelas dan data

Ada **6 kelas target**. Jumlah sampel harus dibaca dari hasil aktual aplikasi
setelah input tersedia.

| Kelas | Total | Training | Testing |
|---|---:|---:|---:|
| Sawah* | Belum dihitung | Belum dihitung | Belum dihitung |
| Bangunan | Belum dihitung | Belum dihitung | Belum dihitung |
| Mangrove | Belum dihitung | Belum dihitung | Belum dihitung |
| Lahan hijau | Belum dihitung | Belum dihitung | Belum dihitung |
| Perairan terbuka | Belum dihitung | Belum dihitung | Belum dihitung |
| Danau/Ranu* | Belum dihitung | Belum dihitung | Belum dihitung |
| **Total** | **Belum dihitung** | **Belum dihitung** | **Belum dihitung** |

Angka tersebut belum dapat dihitung saat ini karena raster Sentinel-2A,
WorldCover, batas Jawa Timur, dan poligon danau/ranu belum tersedia di
repository. Jumlah maksimum sampel di aplikasi adalah batas sampling, bukan
angka aktual.

## 5.2 Metrik yang dilaporkan

- **Accuracy**: proporsi seluruh prediksi benar.
- **Balanced accuracy**: rerata recall tiap kelas, agar kelas kecil tetap
  diperhitungkan.
- **Macro-F1**: rerata F1 antar kelas tanpa bobot jumlah piksel; menjadi
  kriteria pemilihan model.
- **Cohen's κ**: kesepakatan prediksi dengan label setelah mengoreksi peluang
  kesepakatan acak.
- **Confusion matrix** dan precision/recall/F1 tiap kelas: menunjukkan jenis
  kelas yang tertukar.

Skor baru dihasilkan setelah eksperimen berjalan. Jangan menyalin angka,
confusion matrix, jumlah sampel, atau luas dari repository referensi; data dan
label sumbernya berbeda.

## 5.3 Validitas dan ketidakpastian

Holdout blok spasial lebih ketat daripada random split piksel karena
mengurangi kemiripan lokal antara training dan testing. Meskipun demikian,
metrik hanya mengukur kesesuaian terhadap WorldCover/OSM, bukan akurasi
lapangan independen. Untuk klaim tematik, kumpulkan sampel validasi lapangan
atau interpretasi visual independen dengan rancangan sampling terdokumentasi.

Sumber ketidakpastian utama adalah cropland yang tidak khusus sawah,
penggabungan tiga tipe vegetasi menjadi Lahan hijau, kelas air permanen yang
tidak memisahkan laut dengan seluruh fitur air lain, kualitas poligon danau
OSM, piksel campuran, awan/bayangan, serta ketidakcocokan waktu antar sumber.
Cantumkan tanggal, resolusi, CRS, seed, dan jumlah sampel ketika melaporkan
hasil final.
