<div align="center">

# Crawling & Analisis Data Polutan Udara Kabupaten Bangkalan

**Academic Project · Pengantar Sains Data**

[![Live Documentation](https://img.shields.io/badge/Live_Documentation-GitHub_Pages-222222?style=flat-square&logo=github)](https://Rafie110905.github.io/PSD/)
![Python](https://img.shields.io/badge/Python-Data_Analysis-3776AB?style=flat-square&logo=python&logoColor=white)
![Jupyter Book](https://img.shields.io/badge/Jupyter_Book-Documentation-F37626?style=flat-square&logo=jupyter&logoColor=white)

</div>

## Tentang Project

Repository ini berisi project akademik Mata Kuliah **Pengantar Sains Data** pada Program Studi Teknik Informatika, Universitas Trunojoyo Madura.

Project berfokus pada proses **crawling data polutan udara** (CO, NO2, HCHO, O3, SO2, dan CH4) untuk wilayah **Kabupaten Bangkalan** menggunakan data satelit Sentinel-5P melalui Copernicus Data Space Ecosystem (openEO). Wilayah kajian dibatasi menggunakan berkas GeoJSON, data hasil crawling disimpan dalam format CSV, kemudian dianalisis dan divisualisasikan dalam bentuk time series untuk mengetahui kondisi kualitas udara di wilayah tersebut.

Dokumentasi materi, proses crawling, data understanding, serta hasil analisis disusun menggunakan Jupyter Book agar proses pengerjaan dapat dibaca secara runtut melalui website.

## Tujuan Project

- Mengetahui kondisi/kualitas udara di Kabupaten Bangkalan berdasarkan data polutan terkini.
- Melakukan crawling data polutan udara dari citra satelit Sentinel-5P.
- Membatasi wilayah pengambilan data menggunakan GeoJSON/AOI (Area of Interest).
- Melakukan eksplorasi dan pemahaman data (data understanding) untuk setiap fitur polutan.
- Menyajikan hasil akhir dalam bentuk visualisasi time series.

## Kontribusi Saya

- Menentukan wilayah kajian (AOI) Kabupaten Bangkalan menggunakan GeoJSON.
- Melakukan crawling data polutan (CO, NO2, HCHO, O3, SO2, CH4) menggunakan openEO/Copernicus Data Space.
- Membersihkan dan menggabungkan data hasil crawling ke dalam satu berkas CSV.
- Melakukan eksplorasi data (data understanding), termasuk pengecekan missing value dan outlier.
- Membuat visualisasi time series untuk setiap polutan.
- Menyusun dokumentasi project menggunakan Jupyter Book.
- Mempublikasikan dokumentasi melalui GitHub Pages.

## Teknologi dan Tools

| Kategori | Teknologi |
|---|---|
| Bahasa | Python |
| Sumber Data | Sentinel-5P (Copernicus Data Space Ecosystem) |
| Akses Data | openEO |
| Analisis Data | Pandas, NumPy |
| Visualisasi | Matplotlib |
| Notebook | Jupyter Notebook (Google Colab) |
| Dokumentasi | Jupyter Book |
| Deployment | GitHub Pages |

## Dokumentasi Online

Dokumentasi project dapat dibaca melalui:

**https://Rafie110905.github.io/PSD/**

## Menjalankan Dokumentasi Secara Lokal

### 1. Aktifkan environment

```powershell
..\.venv\Scripts\Activate.ps1
```

Apabila PowerShell membatasi eksekusi script:

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
```

### 2. Instal dependensi dokumentasi

```bash
pip install jupyter-book==1.0.3
```

### 3. Buat struktur project Jupyter Book (sekali saja)

```bash
jupyter-book create PSD
```

Perintah ini membuat folder `PSD` berisi skeleton dokumentasi (`_config.yml`, `_toc.yml`, dan contoh notebook). Notebook crawling data polutan (`Crawling_Polutan_Bangkalan.ipynb`) diletakkan di dalam folder ini dan didaftarkan pada `_toc.yml`.

### 4. Build Jupyter Book

```bash
jupyter-book build PSD
```

Hasil build tersedia di:

```text
PSD/_build/html/index.html
```

## Deployment GitHub Pages

```bash
cd PSD/_build/html/

git init
git branch -m main
git config --global user.email "email-github-kamu@gmail.com"
git config --global user.name "Rafie110905"

git add .
git remote add origin https://github.com/Rafie110905/PSD.git
git commit -m "Upload Materi PSD"
git push origin main --force
```

Keterangan:

- Pastikan ada file `.nojekyll` (kosong) di dalam folder `_build/html/` sebelum push, supaya GitHub Pages tidak salah memproses folder yang diawali underscore (`_static`, `_sources`, dll).
- `--force` menimpa isi branch `main` dengan hasil build terbaru.
- Setelah push, aktifkan GitHub Pages di **Settings > Pages**, pilih branch `main`, folder `/ (root)`.
- Untuk update berikutnya: build ulang dari folder source `PSD` (di luar `_build`), lalu ulangi `git add .`, `git commit`, `git push origin main --force` dari dalam `_build/html`.

> **Catatan:** karena hanya folder `_build/html` yang di-push, source notebook (`.ipynb`, `_config.yml`, `_toc.yml`) sebaiknya juga dibackup terpisah (repo lain, Google Drive, atau branch lain) agar tidak hilang.

## Konteks Akademik

- **Mata Kuliah:** Pengantar Sains Data
- **Program Studi:** Teknik Informatika
- **Universitas:** Universitas Trunojoyo Madura
- **Pengembang:** Moh Rafie Nazar J (240411100003)

## Catatan

Repository ini dibuat untuk kebutuhan pembelajaran dan evaluasi akademik. Data polutan yang digunakan bersumber dari citra satelit Sentinel-5P dan digunakan sebagai bahan analisis kualitas udara, bukan sebagai data resmi/pengganti pengukuran instansi terkait.
