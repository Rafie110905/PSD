# Bab 6 — WebGIS & Deployment

## 6.1 Tampilan WebGIS

Dashboard Streamlit menyediakan tujuh halaman:

1. **Ringkasan** — jumlah kelas/sampel, model terpilih, Macro-F1, dan
   perbandingan model.
2. **Alur Data → Model** — status input, uraian proses, dan tombol menjalankan
   eksperimen.
3. **Peta Klasifikasi** — komposit RGB, overlay kelas, legenda, dan basemap
   satelit interaktif melalui Folium/Leaflet.
4. **Luas per Kelas** — jumlah piksel prediksi dan estimasi hektare jika CRS
   raster terproyeksi serta unit luas terdefinisi.
5. **Evaluasi Model** — metrik model, metrik tiap kelas, dan confusion matrix.
6. **Data & Unduhan** — GeoTIFF klasifikasi pratinjau dan tabel CSV.
7. **Metodologi** — kelas, fitur, pembagian spasial, dan batas interpretasi.

Google Satellite pada Folium merupakan **XYZ tile**, bukan WMS. Peta interaktif
dipakai untuk eksplorasi visual; atribusi dan ketentuan layanan penyedia
basemap harus dipatuhi. Hasil GeoTIFF aplikasi diturunkan skalanya untuk
pratinjau, bukan produk klasifikasi resolusi penuh.

## 6.2 Menjalankan aplikasi

Source aplikasi dan petunjuk terbaru:

- [Streamlit `app.py`](https://github.com/Rafie110905/PSD/blob/main/PSD/gis_uts/app.py)
- [Algoritma `classifier.py`](https://github.com/Rafie110905/PSD/blob/main/PSD/gis_uts/classifier.py)
- [Panduan `README.md`](https://github.com/Rafie110905/PSD/blob/main/PSD/gis_uts/README.md)

```powershell
cd C:\PSD\PSD\gis_uts
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Unggah empat input melalui sidebar: GeoTIFF 10-band Sentinel-2A, GeoTIFF
WorldCover yang mencakup AOI, GeoJSON batas provinsi, dan GeoJSON danau/ranu.
Pastikan CRS ada dan sama/tidak ambigu; bila raster sangat luas, siapkan
komposit regional yang ukurannya sesuai sumber daya aplikasi.

## 6.3 Deployment dan web statis

GitHub Pages menampilkan laporan enam bab. Aplikasi interaktif berjalan
terpisah di Streamlit Community Cloud. Pemilik repository perlu membuat app
dari branch `main` dengan main file `PSD/gis_uts/app.py`, kemudian mengunggah
input data melalui aplikasi. Belum ada URL Streamlit sampai deployment
dijalankan dan berhasil.

## 6.4 Implikasi kebijakan dan referensi

Gunakan peta sebagai bahan pemilihan lokasi pemeriksaan RTRW/RDTR, bukan
sebagai penetapan zonasi atau bukti status lahan. Periksa legenda dan skala
nasional sebelum menyatakan pemetaan sesuai standar.

1. Badan Standardisasi Nasional. **SNI 7645-1:2014, Klasifikasi penutup lahan
   — Bagian 1: Skala kecil dan menengah.** Verifikasi status/edisi pada katalog
   BSN sebelum penggunaan normatif.
2. [Sentinel-2 Level-2A, band dan resolusi (Microsoft Planetary Computer)](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a).
3. [ESA WorldCover data access](https://esa-worldcover.org/en/data-access).
4. [ESA WorldCover 2021 v200 documentation](https://github.com/ESA-WorldCover/esa-worldcover-datasets);
   DOI [10.5281/zenodo.7254221](https://doi.org/10.5281/zenodo.7254221).
5. [OpenStreetMap copyright and attribution](https://www.openstreetmap.org/copyright).
