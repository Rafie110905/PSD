<div align="center">

# Crawling & Analisis Data Polutan Udara Kabupaten Bangkalan

**Academic Project · Pengantar Sains Data**

[![Live Documentation](https://img.shields.io/badge/Live_Documentation-GitHub_Pages-222222?style=flat-square&logo=github)](https://Rafie110905.github.io/PSD/)
![Python](https://img.shields.io/badge/Python-Data_Analysis-3776AB?style=flat-square&logo=python&logoColor=white)
![Jupyter Book](https://img.shields.io/badge/Jupyter_Book-Documentation-F37626?style=flat-square&logo=jupyter&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-K--Means_&_PCA-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)

</div>

## Tentang Project

Repository ini berisi project akademik Mata Kuliah **Pengantar Sains Data** pada Program Studi Teknik Informatika, Universitas Trunojoyo Madura.

Project berfokus pada proses **crawling data polutan udara** (CO, NO2, HCHO, O3, SO2, dan CH4) untuk wilayah **Kabupaten Bangkalan** menggunakan data satelit Sentinel-5P melalui Copernicus Data Space Ecosystem (openEO). Wilayah kajian dibatasi menggunakan berkas GeoJSON, data hasil crawling disimpan dalam format CSV, kemudian dianalisis dan divisualisasikan dalam bentuk time series untuk mengetahui kondisi kualitas udara di wilayah tersebut.

Pada tahap lanjutan, data deret waktu polutan (NO2, CO, dan SO2) diubah menjadi fitur menggunakan **TSFEL**, lalu dikelompokkan dengan **K-Means Clustering** untuk menemukan daerah-daerah yang memiliki karakteristik dan pola polusi yang serupa. Hasilnya dibandingkan dengan alur kerja yang sama di **KNIME**.

Dokumentasi materi, proses crawling, data understanding, ekstraksi fitur, serta hasil analisis disusun menggunakan Jupyter Book agar proses pengerjaan dapat dibaca secara runtut melalui website.

## Tujuan Project

- Mengetahui kondisi/kualitas udara di Kabupaten Bangkalan berdasarkan data polutan terkini.
- Melakukan crawling data polutan udara dari citra satelit Sentinel-5P.
- Membatasi wilayah pengambilan data menggunakan GeoJSON/AOI (Area of Interest).
- Melakukan eksplorasi dan pemahaman data (data understanding) untuk setiap fitur polutan.
- Menyajikan hasil akhir dalam bentuk visualisasi time series.
- Mengekstrak fitur dari data deret waktu dan mengelompokkan daerah berdasarkan karakteristik polutannya (K-Means).
- Membandingkan hasil clustering pada data hasil PCA dengan data fitur asli.

## Isi Dokumentasi

| No | Materi | Deskripsi |
|---|---|---|
| 1 | Crawling & Analisis Data Polutan Udara di Kabupaten Bangkalan | Crawling data Sentinel-5P, data understanding, visualisasi time series |
| 2 | Crawling & Analisis Data Polutan Udara di Kecamatan Bangkalan | Analisis pada cakupan wilayah kecamatan |
| 3 | K-Means Clustering Polutan | Elbow Method, Hopkins Statistic, PCA, Silhouette Score, profiling klaster |
| 4 | Alur Kerja (Workflow) Clustering KNIME | Implementasi clustering menggunakan KNIME |
| 5 | Deskripsi Fitur & Perhitungan Manual | Penjelasan fitur hasil ekstraksi dan perhitungan manualnya |

## Kontribusi Saya

- Menentukan wilayah kajian (AOI) Kabupaten Bangkalan menggunakan GeoJSON.
- Melakukan crawling data polutan (CO, NO2, HCHO, O3, SO2, CH4) menggunakan openEO/Copernicus Data Space.
- Membersihkan dan menggabungkan data hasil crawling ke dalam satu berkas CSV.
- Melakukan eksplorasi data (data understanding), termasuk pengecekan missing value dan outlier.
- Membuat visualisasi time series untuk setiap polutan.
- Mengekstrak fitur time series menggunakan TSFEL dan melakukan preprocessing (imputasi, pembuangan fitur konstan, standardisasi).
- Menjalankan K-Means Clustering dengan evaluasi Elbow Method, Silhouette Score, dan Hopkins Statistic, serta membandingkan PCA (37 komponen) dengan fitur asli.
- Menyusun alur kerja clustering di KNIME.
- Menyusun dokumentasi project menggunakan Jupyter Book.
- Mempublikasikan dokumentasi melalui GitHub Pages.

## Teknologi dan Tools

| Kategori | Teknologi |
|---|---|
| Bahasa | Python |
| Sumber Data | Sentinel-5P (Copernicus Data Space Ecosystem) |
| Akses Data | openEO |
| Analisis Data | Pandas, NumPy |
| Ekstraksi Fitur | TSFEL |
| Machine Learning | scikit-learn (StandardScaler, PCA, K-Means, Silhouette Score) |
| Visualisasi | Matplotlib, Seaborn |
| Workflow Clustering | KNIME |
| Notebook | Jupyter Notebook (Google Colab) |
| Dokumentasi | Jupyter Book |
| Deployment | GitHub Pages |

## Dokumentasi Online

Dokumentasi project dapat dibaca melalui:

**https://Rafie110905.github.io/PSD/**

## Struktur Repository

Repository ini menyimpan **hasil build** (yang disajikan GitHub Pages) di root, dan **source Jupyter Book** di dalam subfolder `PSD/`.

```text
C:\PSD\                     <- root repository (folder yang memiliki .git)
├── .git
├── .nojekyll               <- wajib ada, supaya folder berawalan "_" tidak diabaikan
├── index.html, *.html      <- hasil build (disajikan GitHub Pages)
├── _images\, _static\, _sources\, ...
└── PSD\                    <- source Jupyter Book
    ├── _config.yml
    ├── _toc.yml
    ├── *.ipynb, *.md       <- materi
    ├── *.csv               <- data
    └── _build\html\        <- output build sementara (hasil jupyter-book build)
```

> **Penting:** semua perintah `git` dijalankan dari root repository (`C:\PSD`), sedangkan `jupyter-book build` dijalankan dari folder source (`C:\PSD\PSD`).

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

Perintah ini membuat folder `PSD` berisi skeleton dokumentasi (`_config.yml`, `_toc.yml`, dan contoh notebook). Notebook materi diletakkan di dalam folder ini dan didaftarkan pada `_toc.yml`.

### 4. Build Jupyter Book

Jalankan dari folder source (`C:\PSD\PSD`):

```bash
jupyter-book build .
```

Hasil build tersedia di:

```text
PSD/_build/html/index.html
```

Sebelum build, pastikan semua cell notebook sudah dijalankan (Run All) dan disimpan, supaya gambar dan output grafik ikut tersimpan di file `.ipynb`.

## Menambah Materi Baru

1. Letakkan notebook/markdown baru di folder `C:\PSD\PSD`.
2. Daftarkan di `_toc.yml`:
   ```yaml
   - file: nama_file_baru    # tanpa ekstensi
   ```
3. Build ulang, salin hasilnya ke root, lalu push (lihat bagian berikut).

## Deployment GitHub Pages

### Pengaturan sekali saja

Di **Settings > Pages**, pilih **Deploy from a branch**, branch `main`, folder `/ (root)`. Pastikan file kosong `.nojekyll` ada di root repository.

### Langkah update

```powershell
# 1. Build dari folder source
cd C:\PSD\PSD
jupyter-book build .

# 2. Salin hasil build ke ROOT repository (satu level di atas, bukan ke folder ini)
Copy-Item -Path "_build/html/*" -Destination ".." -Recurse -Force

# 3. Commit & push dari root repository
cd C:\PSD
git add .
git commit -m "update materi"
git push
```

Tunggu workflow **pages build and deployment** di tab **Actions** selesai (centang hijau), lalu buka situs dengan `Ctrl+Shift+R`.

### Script otomatis (opsional)

Simpan sebagai `C:\PSD\PSD\deploy.ps1`:

```powershell
param([string]$msg = "update materi")
Set-Location C:\PSD\PSD
jupyter-book build .
Copy-Item -Path "_build/html/*" -Destination ".." -Recurse -Force
Set-Location C:\PSD
git add .
git commit -m $msg
git push
```

Cara pakai:

```powershell
.\deploy.ps1 "tambah materi baru"
```

### Troubleshooting

| Gejala | Kemungkinan penyebab | Solusi |
|---|---|---|
| Gambar tidak muncul (404), halaman lain normal | Hasil build disalin ke folder yang salah (`C:\PSD\PSD`, bukan `C:\PSD`) | Salin ke `..` lalu commit dari `C:\PSD` |
| Semua folder berawalan `_` (`_images`, `_static`) 404 | File `.nojekyll` tidak ada di root | Buat file kosong `.nojekyll` di root, commit, push |
| Gambar tidak ada di hasil build | Notebook belum di-Run All sebelum disimpan | Jalankan semua cell, simpan, build ulang |
| Perubahan sudah di-push tapi belum tampil | Deploy belum selesai atau cache | Cek tab Actions, lalu `Ctrl+Shift+R` / jendela incognito |
| `git status` bersih padahal file baru ada | Menjalankan git dari folder yang berbeda | Pastikan `git rev-parse --show-toplevel` menunjuk ke `C:/PSD` |

## Konteks Akademik

- **Mata Kuliah:** Pengantar Sains Data
- **Program Studi:** Teknik Informatika
- **Universitas:** Universitas Trunojoyo Madura
- **Pengembang:** Moh Rafie Nazar J (240411100003)

## Catatan

Repository ini dibuat untuk kebutuhan pembelajaran dan evaluasi akademik. Data polutan yang digunakan bersumber dari citra satelit Sentinel-5P dan digunakan sebagai bahan analisis kualitas udara, bukan sebagai data resmi/pengganti pengukuran instansi terkait.
