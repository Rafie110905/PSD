# UTS SIG: Analisis Spasial Penutup Lahan dan Kebijakan di Jawa Timur

**Dari citra Sentinel-2 ke enam kelas tutupan lahan, evaluasi model, dan WebGIS**

![Alur eksperimen klasifikasi enam kelas](../_static/uts-workflow.svg)

> **Asal hasil yang ditampilkan.** Notebook, tabel evaluasi, raster, dan gambar
> hasil yang tersedia berasal dari eksperimen repository
> [PSD-Klasifikasi-Lahan](https://github.com/Rahardian-Ananta/PSD-Klasifikasi-Lahan),
> yang menjadi acuan tugas. Berkas raster Sentinel-2 mentah untuk menjalankan
> ulang seluruh proses tidak tersedia di folder `data` repository tersebut.
> Karena itu, hasil berikut ditandai sebagai **hasil eksperimen referensi**,
> bukan hasil run ulang dari input lokal.

Laporan mengikuti enam bab dengan potongan kode, tabel output, visualisasi, dan
peta seperti alur proyek referensi. Data serta hasil eksperimen yang ditampilkan
dirujuk secara terbuka ke sumbernya.

## Hasil eksperimen singkat

Eksperimen referensi memilih **SVM RBF berbasis fitur per piksel** berdasarkan
CV Macro-F1 (0,521); Macro-F1 test poligonnya 0,474. Raster seluruh wilayah
dibuat dengan Random Forest karena lebih cepat untuk inferensi.

| Kelas | Luas referensi (ha) | Proporsi |
|---|---:|---:|
| Sawah | 526.207,7 | 36,72% |
| Lahan hijau | 473.514,6 | 33,05% |
| Bangunan/Permukiman | 257.855,1 | 18,00% |
| Mangrove | 134.223,7 | 9,37% |
| Danau | 26.823,5 | 1,87% |
| Laut | 14.256,4 | 0,99% |

![Grafik luas tiap kelas](../_static/uts-class-areas.svg)

Lihat juga [gambar peta RGB dan klasifikasi](https://github.com/Rahardian-Ananta/PSD-Klasifikasi-Lahan/blob/main/outputs/figures/rgb_vs_klasifikasi.png)
dan [overlay hasil pada batas Jawa Timur](https://github.com/Rahardian-Ananta/PSD-Klasifikasi-Lahan/blob/main/outputs/figures/klasifikasi_overlay.png)
di repository sumber.

Angka, tabel, dan peta di atas adalah keluaran eksperimen referensi. Jangan
mengutipnya sebagai hasil pengukuran baru tanpa menjalankan ulang notebook
menggunakan raster sumber yang sesuai.

## Navigasi bab

Pilih bab untuk melompat ke bagian yang diperlukan. Semua bab berada di
halaman yang sama; daftar isi di sisi halaman juga menyediakan navigasi
bercabang ke subbagian.

<ol>
<li><a href="#bab-1">UTS SIG — Bab 1: Business Understanding</a></li>
<li><a href="#bab-2">UTS SIG — Bab 2: Data Understanding</a></li>
<li><a href="#bab-3">UTS SIG — Bab 3: Data Preprocessing</a></li>
<li><a href="#bab-4">UTS SIG — Bab 4: Modeling</a></li>
<li><a href="#bab-5">UTS SIG — Bab 5: Evaluation</a></li>
<li><a href="#bab-6">UTS SIG — Bab 6: WebGIS & Deployment</a></li>
</ol>

```{include} UTS_Jatim_Bab_01_Business_Understanding.inc
```

```{include} UTS_Jatim_Bab_02_Data_Understanding.inc
```

```{include} UTS_Jatim_Bab_03_Data_Preprocessing.inc
```

```{include} UTS_Jatim_Bab_04_Modeling.inc
```

```{include} UTS_Jatim_Bab_05_Evaluation.inc
```

```{include} UTS_Jatim_Bab_06_WebGIS_Deployment.inc
```
