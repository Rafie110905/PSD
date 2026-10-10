# SIG Jawa Timur — Klasifikasi Penutup Lahan

Streamlit dashboard tujuh halaman untuk eksperimen enam kelas berbasis citra
Sentinel-2A dan label proksi ESA WorldCover 2021. Aplikasi melakukan pembagian
train/test berbasis blok spasial, membandingkan empat model, menampilkan peta
Folium, evaluasi, dan unduhan hasil pratinjau.

## Data proyek dan keterbatasan yang harus diketahui

Repository saat ini hanya memiliki batas AOI dan dua berkas sampel Sawah/Bukan
Sawah untuk Bangkalan. Belum tersedia citra Sentinel-2 seluruh Jawa Timur,
label danau/ranu, ataupun data lapangan enam kelas. Karena itu, aplikasi
memerlukan input GeoTIFF dan GeoJSON sebelum metrik eksperimen dapat dihitung;
tidak ada angka akurasi atau jumlah sampel yang dibuat-buat di laporan.

Label ESA WorldCover bukan label lapangan:

- Cropland (40) dipakai sebagai **proksi Sawah***; kelas ini juga memuat jenis
  pertanian lain.
- Built-up (50) menjadi Bangunan.
- Mangroves (95) menjadi Mangrove.
- Tree cover (10), Shrubland (20), dan Grassland (30) digabung menjadi Lahan
  hijau.
- Permanent water bodies (80) dipisahkan menjadi Perairan terbuka dan
  Danau/Ranu* menggunakan poligon danau OpenStreetMap.

Nama kelas bertanda bintang berarti label proksi. Pengukuran hanya menguji
kesesuaian model terhadap peta referensi proksi dan tidak boleh dilaporkan
sebagai akurasi lapangan atau peta resmi Indonesia.

## Berkas input

1. **Sentinel-2 L2A multiband GeoTIFF**, minimal 10 band dalam urutan:
   B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12. Seluruh band harus sudah
   diregistrasi pada grid/CRS yang sama. B11 dan B12 asli beresolusi 20 m;
   resampling tidak menambah informasi spasial. Untuk uji coba satu provinsi
   dan batas ukuran upload Cloud, siapkan komposit 100 m; hasil aplikasi berupa
   pratinjau yang diturunkan skalanya, bukan produk operasional 10 m.
2. **ESA WorldCover 2021 v200** GeoTIFF kelas 10 m yang menutupi AOI, kode kelas
   sesuai dokumentasi aplikasi.
3. **Batas Provinsi Jawa Timur** GeoJSON.
4. **Poligon danau/ranu** GeoJSON ber-CRS jelas, misalnya hasil unduh
   OpenStreetMap dengan tag `natural=water` dan `water=lake`.

Jika menggunakan beberapa tile ESA, gabungkan dahulu menjadi satu mosaic yang
proyeksi dan cakupannya cocok. Gunakan citra Sentinel-2 dan referensi tahun
2021 atau catat jeda tahun dan potensi perubahan tutupan lahan. Untuk awan,
gunakan komposit multi-temporal yang sudah dimask awan.

## Menjalankan lokal

```powershell
cd C:\PSD\PSD\gis_uts
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Unggah empat masukan di sidebar, buka **Alur Data → Model**, atur batas sampel
seimbang per kelas, lalu klik **Jalankan eksperimen**. Hasil tersimpan selama
sesi dashboard agar dapat dibuka pada halaman lain tanpa melatih ulang.

Halaman dashboard: **Ringkasan**, **Alur Data → Model**, **Peta Klasifikasi**,
**Luas per Kelas**, **Evaluasi Model**, **Data & Unduhan**, dan **Metodologi**.
Hasil mencakup jumlah aktual training/testing, confusion matrix, accuracy,
balanced accuracy, Macro-F1, Cohen's kappa, perbandingan model, peta, dan
unduhan GeoTIFF/CSV. Holdout dibagi berdasarkan blok spasial 100 piksel pada
raster pratinjau.

Susunan laporan mengikuti enam tahap CRISP-DM seperti repository referensi.
Susunan bab tersebut tidak berarti data, angka, atau hasil model referensi
dipakai kembali; semua hasil dashboard dihitung dari input eksperimen ini.

## Deploy Streamlit Community Cloud

1. Buka <https://share.streamlit.io/> dan masuk dengan GitHub.
2. Pilih repository `Rafie110905/PSD`, branch `main`.
3. Pilih main file `PSD/gis_uts/app.py`.
4. Atur Advanced settings → Python version ke 3.12, deploy, lalu unggah berkas
   data dari sidebar aplikasi.

Hanya folder `PSD/gis_uts` berisi source dan dependency; berkas citra dan label
besar tidak disimpan di repository. Deploy ke Streamlit Community Cloud perlu
diinisiasi dan dikaitkan dengan akun pemilik repository.
