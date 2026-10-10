# Bab 4 — Modeling

## 4.1 Target dan rancangan model

Target terdiri atas enam label proksi: Sawah*, Bangunan, Mangrove, Lahan hijau,
Perairan terbuka, dan Danau/Ranu*. Setiap sampel memiliki sepuluh reflektansi
Sentinel-2A dan delapan indeks spektral dari Bab 3. Seluruh estimator menerima
sampel training yang sama dan dievaluasi pada holdout blok spasial yang sama.

Empat model dibandingkan:

1. **Random Forest** — ansambel pohon bagging untuk pola nonlinier dan interaksi.
2. **Extra Trees** — ansambel pohon dengan pemilihan split lebih acak.
3. **HistGradientBoosting** — boosting pohon dengan binning fitur histogram.
4. **SVM RBF** — pemisah berbasis kernel radial; fitur distandardisasi terlebih
   dahulu.

Model dipilih berdasarkan Macro-F1 tertinggi. Jika nilainya sama, balanced
accuracy menjadi pemecah seri. Pemilihan dilakukan dari evaluasi yang sama
untuk semua model; hasil bukan angka yang di-hardcode.

## 4.2 Training dan inferensi

1. Bentuk matriks fitur dari piksel referensi yang lolos AOI dan pemeriksaan
   validitas.
2. Ambil jumlah sampel seimbang per kelas sampai maksimum yang ditentukan.
3. Bagi data menjadi training dan testing dengan group blok spasial.
4. Latih empat model pada indeks training.
5. Hitung prediksi testing dan metrik tanpa mengganti split di antara model.
6. Gunakan estimator terpilih untuk mengklasifikasikan piksel valid pada
   pratinjau citra.

SVM memakai `StandardScaler` dalam pipeline agar skala tiap fitur
distandardisasi tanpa menghitung parameter dari data uji. Model lain
menggunakan konfigurasi yang ditetapkan di source aplikasi.

## 4.3 Batas klaim

Pembagian berdasarkan blok spasial dirancang mengurangi kebocoran dari
ketetanggaan piksel, tetapi tidak menjadikan label sumber independen dari
WorldCover. Model yang menang pada eksperimen ini adalah yang paling sesuai
dengan label proksi pada split tersebut; hasil tidak otomatis berlaku untuk
seluruh variasi musim, tahun, atau kondisi lapangan.

Jumlah model berbeda dari repository referensi. UTS ini membandingkan empat
estimator yang terpasang pada pipeline sumbernya sendiri; tidak memakai
perbandingan pixel-vs-mean-poligon ataupun skor model dari proyek tersebut.
