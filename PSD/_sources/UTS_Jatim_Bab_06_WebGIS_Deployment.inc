<a id="bab-6"></a>

## Bab 6 — WebGIS & Deployment

![Luas hasil klasifikasi per kelas](../_static/uts-class-areas.svg)

### 6.1 Tampilan WebGIS

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

Peta overlay di atas adalah hasil inferensi run referensi. Peta interaktif
Folium, raster GeoTIFF 44 MB, tabel luas, dan grafik evaluasi tersedia di
[folder `outputs` proyek sumber](https://github.com/Rahardian-Ananta/PSD-Klasifikasi-Lahan/tree/main/outputs).
Halaman statis menampilkan hasil yang sudah tersimpan; halaman ini tidak
menjalankan ulang model saat dibuka.

### 6.2 Menjalankan aplikasi

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

Dashboard UTS saat ini menerima GeoTIFF Sentinel-2 10-band, GeoTIFF WorldCover,
GeoJSON batas provinsi, dan GeoJSON danau/ranu. Pipeline ini berbeda dari
eksperimen referensi (enam band dan poligon Kementan/BIG/Natural Earth).
Keluaran dashboard baru dihitung setelah inputnya tersedia; gambar dan skor
statis di bab ini tetap diberi label sebagai hasil run referensi.

### 6.3 Deployment dan web statis

GitHub Pages menampilkan laporan enam bab. Aplikasi interaktif berjalan
terpisah di Streamlit Community Cloud. Pemilik repository perlu membuat app
dari branch `main` dengan main file `PSD/gis_uts/app.py`, kemudian mengunggah
input data melalui aplikasi. Belum ada URL Streamlit sampai deployment
dijalankan dan berhasil.

### 6.4 Implikasi kebijakan dan referensi

Gunakan peta sebagai bahan pemilihan lokasi pemeriksaan RTRW/RDTR, bukan
sebagai penetapan zonasi atau bukti status lahan. Periksa legenda dan skala
nasional sebelum menyatakan pemetaan sesuai standar.

1. Badan Standardisasi Nasional. **SNI 7645-1:2014, Klasifikasi penutup lahan
   — Bagian 1: Skala kecil dan menengah.** Verifikasi status/edisi pada katalog
   BSN sebelum penggunaan normatif.
2. [Sentinel-2 Level-2A, band dan resolusi (Microsoft Planetary Computer)](https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a).
3. [Kementerian Pertanian — sumber sampel sawah yang dicatat pada metadata proyek referensi](https://github.com/Rahardian-Ananta/PSD-Klasifikasi-Lahan/tree/main/data).
4. [Repository sumber, notebook, output tabel dan gambar](https://github.com/Rahardian-Ananta/PSD-Klasifikasi-Lahan).

#### Gambar hasil dan peta interaktif

![Komposit RGB dan hasil klasifikasi](../_static/uts-ref-rgb-vs-classification.png)

![Overlay klasifikasi pada batas Jawa Timur](../_static/uts-ref-classification-overlay.png)

Peta hasil dapat dieksplorasi langsung pada halaman ini. Basemap tile
memerlukan koneksi internet.

<iframe title="Peta Folium klasifikasi poligon Jawa Timur" src="../_static/uts-ref-folium-map.html" width="100%" height="620" loading="lazy"></iframe>

- [Raster klasifikasi GeoTIFF](https://github.com/Rahardian-Ananta/PSD-Klasifikasi-Lahan/blob/main/outputs/raster/klasifikasi_jawa_timur.tif)
- [Dashboard kode sumber](https://github.com/Rahardian-Ananta/PSD-Klasifikasi-Lahan/blob/main/app.py)
