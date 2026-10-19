---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Klasifikasi Spasial Tutupan Lahan Jawa Timur (6 Kelas)

## Business Understanding

### 1. Latar Belakang & Urgensi Masalah
Provinsi Jawa Timur merupakan salah satu wilayah strategis nasional dengan luas daratan mencapai ±47.800 km² serta karakteristik bentang alam yang sangat beragam. Wilayah ini memegang peranan krusial sebagai **lumbung pangan nasional** (sektor persawahan), pusat pertumbuhan industri dan permukiman perkotaan, serta penyangga ekologis penting berupa kawasan hutan dataran tinggi dan sabuk hijau mangrove pesisir.

Seiring pesatnya laju pembangunan infrastruktur, industrialisasi, dan pertumbuhan populasi, dinamika perubahan tutupan dan penggunaan lahan (*Land Use / Land Cover - LULC*) berlangsung dengan sangat cepat. Pemantauan berkala menggunakan metode survei lapangan konvensional (terestrial) menghadapi berbagai kendala:
- **Biaya dan Waktu Tinggi:** Survei terestrial pada cakupan regional 38 kabupaten/kota membutuhkan alokasi logistik, personel, dan anggaran yang sangat besar.
- **Keterlambatan Informasi (*Time-Lag*):** Proses pembaruan peta konvensional memerlukan waktu bulanan hingga tahunan sehingga data acuan cepat usang (*outdated*).
- **Keterbatasan Aksesibilitas Geografis:** Kesulitan menjangkau area dengan medan berat, seperti hutan lindung lereng gunung dan rawa mangrove pesisir.

Oleh karena itu, pemanfaatan teknologi **Penginderaan Jauh (*Remote Sensing*)** satelit optik (**Sentinel-2A**) yang dipadukan dengan **Machine Learning** menjadi solusi mutakhir untuk mengotomatisasi pemetaan tutupan lahan berskala regional secara objektif, berbiaya hemat, dan memiliki resolusi spasial tinggi.

### 2. Rumusan Masalah
1. Bagaimana mengidentifikasi dan mengklasifikasikan 6 tipe tutupan lahan utama (*Sawah, Bangunan, Danau, Hutan, Mangrove, dan Laut*) di Jawa Timur secara akurat dari nilai reflektansi pita spektral Sentinel-2A?
2. Bagaimana mengatasi kerentanan tumpang-tindih spektral (*spectral confusion*), khususnya antara sesama vegetasi kanopi lebat (*Hutan* vs *Mangrove*) serta sesama badan air (*Danau* vs *Laut*)?
3. Algoritma pembelajaran mesin manakah di antara **Random Forest**, **XGBoost**, dan **Support Vector Machine (SVM)** yang menghasilkan performa akurasi, sensitivitas, dan stabilitas terbaik?
4. Bagaimana menerapkan model optimal tersebut pada seluruh piksel citra satelit (*pixel-wise inference*) secara efisien dan menyajikannya dalam bentuk visualisasi peta web interaktif bagi pemangku kepentingan?

### 3. Tujuan Analisis
- **Tujuan Bisnis & Perencanaan Wilayah:**
  - Menyediakan basis data spasial aktual untuk mendukung perumusan Rencana Tata Ruang Wilayah (RTRW) Provinsi Jawa Timur.
  - Memantau perlindungan Lahan Pertanian Pangan Berkelanjutan (LP2B) guna menjaga ketahanan pangan daerah dan nasional.
  - Mendukung upaya mitigasi bencana pesisir (abrasi/rob) dan konservasi ekosistem mangrove serta hutan lindung.
- **Tujuan Teknis & *Data Science*:**
  - Mengekstraksi 5 pita spektral multispektral (`B02, B03, B04, B08, B11`) dan mengombinasikannya dengan 3 indeks biofisik kunci (`NDVI, NDWI, NDBI`).
  - Mengembangkan dan membandingkan performa model klasifikasi multi-kelas (*Random Forest*, *XGBoost*, dan *SVM*) berbasis evaluasi metrik berbobot (*Precision*, *Recall*, *F1-Score*, dan *Overall Accuracy*).
  - Melakukan inferensi skala penuh jutaan piksel menggunakan model terbaik (**XGBoost**) dengan teknik *spatial masking* batas daratan teroptimasi.
  - Membangun peta interaktif berbasis Web GIS (**Folium ImageOverlay**) yang dilengkapi kontrol lapisan (*Layer Control*) dan legenda LULC tematik.

### 4. Kriteria Keberhasilan (*Success Criteria*)
| Kategori | Parameter Keberhasilan | Target yang Ditetapkan |
| :--- | :--- | :--- |
| **Kinerja Model** | Akurasi Keseluruhan (*Overall Accuracy*) | Mencapai $\ge 90\%$ pada subset data uji (*test set*). |
| **Keseimbangan Kelas** | *Recall* & *F1-Score* per Kelas | Nilai $\ge 0.85$ pada kelas-kelas rawan misklasifikasi (*Mangrove* dan *Danau*). |
| **Efisiensi Komputasi** | Waktu Inferensi Spasial Penuh | Mampu mengklasifikasikan jutaan piksel citra satelit secara cepat melalui paralelisasi komputasi (`n_jobs=-1`) dan *raster masking*. |
| **Penyajian Produk** | *Interactive Web Map* | Menghasilkan peta mandiri berbasis Folium yang dapat dibuka di peramban web tanpa memerlukan instalasi perangkat lunak GIS khusus. |

### 5. Deployment Aplikasi Web (Streamlit Cloud)

Sebagai implementasi produk akhir (*data product delivery*) yang siap digunakan oleh pengambil kebijakan maupun publik, sistem klasifikasi tutupan lahan ini telah di-*deploy* secara terbuka ke platform **Streamlit Cloud**.

Dashboard interaktif ini menyajikan visualisasi peta tutupan lahan resolusi tinggi, statistik luas wilayah per kelas, evaluasi matriks model, serta simulasi prediksi manual secara *on-the-fly*. Aplikasi dapat diakses melalui tautan berikut:

- **URL Aplikasi Web:** [https://24-209-klasifikasijawatimur.streamlit.app/](https://24-209-klasifikasijawatimur.streamlit.app/)

Fitur utama yang tersedia pada aplikasi web:
1. **Peta Interaktif:** Tampilan *overlay* hasil klasifikasi XGBoost di atas citra satelit resolusi tinggi dengan pengaturan transparansi (*opacity*) serta visualisasi titik sampel *ground truth*.
2. **Statistik Luas LULC:** Tabel kalkulasi luas wilayah (km²) dan proporsi persentase tiap kelas tutupan lahan yang dilengkapi fitur unduh data (CSV).
3. **Evaluasi Performa Model:** Laporan klasifikasi (*Classification Report*) dan matriks konfusi (*Confusion Matrix*) komprehensif pada subset data uji.
4. **Prediksi Manual:** Pengujian tebakan kelas secara instan berdasarkan input nilai reflektansi spektral pita Sentinel-2A.

---

Bagian berikut mendokumentasikan keseluruhan alur kerja teknis, mulai dari perancangan sampel *ground truth*, ekstraksi fitur piksel citra Sentinel-2A (Level-2A), komparasi algoritma, pelatihan model XGBoost, hingga visualisasi peta interaktif per-piksel.

## Instalasi Library Yang Digunakan

```bash
pip install geopandas openeo pandas scikit-learn xgboost folium joblib rasterio rasterstats matplotlib seaborn
```

## 1. Desain Pengamatan (Ground Truth) 6 Kelas

Pengambilan sampel dilakukan secara spasial menggunakan data vektor (`Shapefile` / `GeoJSON` zip) yang mencakup wilayah Jawa Timur. Terdapat 6 kelas tutupan lahan yang diklasifikasikan:

| Kelas Target | Kode Label | Karakteristik Objek |
| :--- | :---: | :--- |
| **Sawah** | `0` | Petak lahan pertanian padi aktif. |
| **Bangunan** | `1` | Permukiman, infrastruktur jalan, dan kawasan terbangun perkotaan. |
| **Danau** | `2` | Badan air darat tawar, seperti danau atau waduk. |
| **Hutan** | `3` | Area dengan tutupan pohon rapat di daratan (hutan primer/sekunder). |
| **Mangrove** | `4` | Hutan bakau/vegetasi pesisir pantai. |
| **Laut** | `5` | Perairan laut lepas atau wilayah perairan pesisir. |

```bash
import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
from rasterstats import zonal_stats

print("Membaca dan menggabungkan sampel poligon...")
gdf_sawah = gpd.read_file("sawah.zip").to_crs("EPSG:4326")
gdf_bangunan = gpd.read_file("bangunan.zip").to_crs("EPSG:4326")
gdf_danau = gpd.read_file("danau.zip").to_crs("EPSG:4326")
gdf_hutan = gpd.read_file("hutan.zip").to_crs("EPSG:4326")
gdf_mangrove = gpd.read_file("mangrove.zip").to_crs("EPSG:4326")
gdf_laut = gpd.read_file("laut.zip").to_crs("EPSG:4326")

# Beri label teks dan angka
gdf_sawah["label_teks"], gdf_sawah["label"] = "sawah", 0
gdf_bangunan["label_teks"], gdf_bangunan["label"] = "bangunan", 1
gdf_danau["label_teks"], gdf_danau["label"] = "danau", 2
gdf_hutan["label_teks"], gdf_hutan["label"] = "hutan", 3
gdf_mangrove["label_teks"], gdf_mangrove["label"] = "mangrove", 4
gdf_laut["label_teks"], gdf_laut["label"] = "laut", 5

# Gabungkan menjadi 1 variabel: gdf_sampel
gdf_sampel = gpd.GeoDataFrame(
    pd.concat([gdf_sawah, gdf_bangunan, gdf_danau, gdf_hutan, gdf_mangrove, gdf_laut], ignore_index=True),
    crs="EPSG:4326"
)

# Hapus baris jika ada geometri yang kosong (mencegah error saat ekstraksi)
gdf_sampel = gdf_sampel.dropna(subset=["geometry"]).reset_index(drop=True)

# Tentukan nama file TIF hasil unduhan Anda
file_tif = "sentinel2_6kelas_visual_full.tif"
```

## 2. Akuisisi & Ekstraksi Nilai Piksel Cloud via openEO

Berbeda dengan akuisisi lokasi sempit yang seringkali mengunduh citra utuh `.tif` berukuran besar, pada pemetaan skala regional (Provinsi Jawa Timur), kita dapat memanfaatkan metode **Spatial Aggregation**. 

Melalui fungsi `aggregate_spatial`, ekstraksi nilai pantulan (*reflectance*) Sentinel-2A dihitung langsung oleh *server cloud* (Data Space Copernicus). Model mengekstrak nilai spektral 5 band (*Blue, Green, Red, NIR, SWIR*) di titik-titik lokasi (poligon) tanpa perlu mengunduh file mentahnya, menghemat ratusan Gigabyte memori.

Selain menggunakan ke-5 Pita Utama (`B02, B03, B04, B08, B11`), proses diskriminasi *Multiclass* (6 Kelas) sangat memerlukan penekanan terhadap jenis objek tertentu dengan kalkulasi Indeks Spektral:

1. **NDVI (Normalized Difference Vegetation Index):** `(B08 - B04) / (B08 + B04)` 
   Sangat ideal dalam membedakan kerapatan *Vegetasi* seperti Sawah, Hutan, dan Mangrove dibandingkan non-vegetasi.
2. **NDWI (Normalized Difference Water Index):** `(B03 - B08) / (B03 + B08)` 
   Berguna mendeteksi pantulan air (*Badan Air*), sehingga mudah membedakan Danau dan Laut dengan daratan.
3. **NDBI (Normalized Difference Built-up Index):** `(B11 - B08) / (B11 + B08)` 
   Sangat peka terhadap pantulan dari bangunan dan lahan terbuka. Kunci bagi model mengenali Bangunan secara spesifik.


```bash
with rasterio.open(file_tif) as src:
    crs_tif = src.crs

if gdf_sampel.crs != crs_tif:
    gdf_sampel = gdf_sampel.to_crs(crs_tif)

# Asumsi urutan band di file TIF persis seperti saat diunduh: B02, B03, B04, B08, B11
band_names = ["B02", "B03", "B04", "B08", "B11"]

print("Mengekstrak nilai band...")
for i, band in enumerate(band_names, start=1): # rasterio membaca band mulai dari indeks 1
    # Ekstrak nilai rata-rata (mean) piksel yang berada di dalam tiap poligon
    stats = zonal_stats(
        vectors=gdf_sampel,
        raster=file_tif,
        band=i,
        stats="mean",
        nodata=np.nan
    )
    # Masukkan hasil ekstraksi ke kolom baru di GeoDataFrame
    gdf_sampel[band] = [s['mean'] for s in stats]

print("Menghitung indeks NDVI, NDWI, NDBI...")

# NDVI = (NIR - Red) / (NIR + Red)
gdf_sampel['NDVI'] = (gdf_sampel['B08'] - gdf_sampel['B04']) / (gdf_sampel['B08'] + gdf_sampel['B04'])

# NDWI = (Green - NIR) / (Green + NIR)
gdf_sampel['NDWI'] = (gdf_sampel['B03'] - gdf_sampel['B08']) / (gdf_sampel['B03'] + gdf_sampel['B08'])

# NDBI = (SWIR - NIR) / (SWIR + NIR)
gdf_sampel['NDBI'] = (gdf_sampel['B11'] - gdf_sampel['B08']) / (gdf_sampel['B11'] + gdf_sampel['B08'])

df_final = pd.DataFrame(gdf_sampel.drop(columns='geometry'))

# Ganti nilai tak terhingga (infinity) jika ada pembagian dengan nol menjadi NaN
df_final.replace([np.inf, -np.inf], np.nan, inplace=True)

# Hapus baris yang nilai band-nya kosong (misal poligon berada di luar area gambar TIF)
df_final.dropna(subset=['B02', 'NDVI'], inplace=True)

# Simpan ke CSV
nama_csv = "dataset_ekstraksi_tif_lengkap.csv"
df_final.to_csv(nama_csv, index=False)
print(f"Ekstraksi selesai! File dataset telah disimpan sebagai: {nama_csv}")
```

## 3. Perbandingan Model Klasifikasi (Random Forest, XGBoost, dan SVM)

Setelah dataset hasil ekstraksi nilai piksel dan indeks spektral (`dataset_ekstraksi_tif_lengkap.csv`) siap, tahap selanjutnya adalah melakukan pengujian dan komparasi performa algoritma *Machine Learning*. Tiga algoritma populer untuk klasifikasi spasial multi-kelas dievaluasi:

1. **Random Forest (RF):**
   Algoritma *ensemble* berbasis *bagging* (*Bootstrap Aggregating*) yang membangun ratusan pohon keputusan (*decision trees*) independen. Model ini sangat stabil, tidak mudah mengalami *overfitting*, dan *scale-invariant* (tidak terpengaruh oleh perbedaan skala antar fitur).

2. **XGBoost (Extreme Gradient Boosting):**
   Algoritma *ensemble* berbasis *boosting* yang membangun pohon secara bertahap (sekuensial) untuk meminimalkan *residual error* dari pohon sebelumnya. XGBoost dilengkapi regularisasi ($L_1$ dan $L_2$) untuk mencegah overfitting serta komputasi yang dioptimalkan secara paralel.

3. **Support Vector Machine (SVM):**
   Algoritma yang memetakan data ke ruang dimensi lebih tinggi menggunakan kernel (RBF / *Radial Basis Function*) untuk menemukan bidang pemisah (*hyperplane*) dengan margin terbesar. Karena sensitif terhadap rentang skala nilai input, model SVM dibungkus dalam *pipeline* bersama `StandardScaler` agar fitur ternormalisasi dengan baik.

### Alur Kode Perbandingan Model:
- **Pemisahan Data (*Stratified Split*):** Dataset dibagi menjadi 80% data latih dan 20% data uji. Parameter `stratify=y` menjamin proporsi ke-6 kelas (Sawah, Bangunan, Danau, Hutan, Mangrove, Laut) tetap seimbang pada data latih dan uji.
- **Pelatihan & Pengujian:** Ketiga model dilatih menggunakan fitur `['B02', 'B03', 'B04', 'B08', 'B11', 'NDVI', 'NDWI', 'NDBI']` lalu diuji pada subset data uji yang sama.
- **Evaluasi Komparatif:** Menghitung *Classification Report* (Precision, Recall, F1-Score) dan merangkum peringkat akurasi keseluruhan (*overall accuracy*) untuk menentukan model terbaik.

```{code-cell} ipython3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report, accuracy_score

# ==========================================
# 1. BACA DATASET & PERSIAPAN
# ==========================================
# Sesuaikan nama file CSV dengan hasil ekstraksi terakhir Anda
df_final = pd.read_csv("./source/klasifikasi_jatim/data/dataset_ekstraksi_tif_lengkap.csv")

fitur_kolom = ['B02', 'B03', 'B04', 'B08', 'B11', 'NDVI', 'NDWI', 'NDBI']
X = df_final[fitur_kolom]
y = df_final['label']
nama_kelas = ['Sawah', 'Bangunan', 'Danau', 'Hutan', 'Mangrove', 'Laut']

# Pemisahan dataset (80% Latih, 20% Uji)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Data Pelatihan: {len(X_train)} Sampel")
print(f"Data Pengujian: {len(X_test)} Sampel\n")

# Dictionary untuk menyimpan skor akurasi
skor_akurasi = {}

# ==========================================
# 2. MODEL RANDOM FOREST
# ==========================================
print("Melatih Model Random Forest...")
model_rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model_rf.fit(X_train, y_train)
y_pred_rf = model_rf.predict(X_test)
skor_akurasi['Random Forest'] = accuracy_score(y_test, y_pred_rf)

print("\n--- Evaluasi Random Forest ---")
print(classification_report(y_test, y_pred_rf, target_names=nama_kelas))

# ==========================================
# 3. MODEL XGBOOST
# ==========================================
print("Melatih Model XGBoost...")
model_xgb = XGBClassifier(n_estimators=100, learning_rate=0.1, random_state=42, n_jobs=-1)
model_xgb.fit(X_train, y_train)
y_pred_xgb = model_xgb.predict(X_test)
skor_akurasi['XGBoost'] = accuracy_score(y_test, y_pred_xgb)

print("\n--- Evaluasi XGBoost ---")
print(classification_report(y_test, y_pred_xgb, target_names=nama_kelas))

# ==========================================
# 4. MODEL SUPPORT VECTOR MACHINE (SVM)
# ==========================================
print("Melatih Model SVM...")
# SVM menggunakan StandardScaler agar performanya maksimal
model_svm = make_pipeline(StandardScaler(), SVC(kernel='rbf', C=1.0, random_state=42))
model_svm.fit(X_train, y_train)
y_pred_svm = model_svm.predict(X_test)
skor_akurasi['SVM'] = accuracy_score(y_test, y_pred_svm)

print("\n--- Evaluasi SVM ---")
print(classification_report(y_test, y_pred_svm, target_names=nama_kelas))

# ==========================================
# 5. KESIMPULAN PERBANDINGAN AKURASI
# ==========================================
print("\n==========================================")
print("   PERBANDINGAN AKURASI KETIGA MODEL")
print("==========================================")
for model, skor in sorted(skor_akurasi.items(), key=lambda item: item[1], reverse=True):
    print(f"{model:<15}: {skor * 100:.2f}%")
print("==========================================")
```

### Penjelasan Metrik dan Analisis Hasil Evaluasi:
- **Accuracy (Akurasi Keseluruhan):** Rasio total prediksi benar terhadap keseluruhan sampel uji. Metrik ini memberikan gambaran umum efektivitas model secara makro.
- **Precision:** Mengukur ketepatan model saat memprediksi suatu kelas (berapa persen dari prediksi kelas tersebut yang benar-benar akurat). Menghindari *false positive* (misal: area Bangunan salah terprediksi sebagai Sawah).
- **Recall (Sensitivitas):** Mengukur kemampuan model mendeteksi seluruh data riil dari kelas tersebut (berapa persen dari data asli yang berhasil dikenali). Kritis untuk kelas dengan karakteristik mirip seperti Mangrove dan Hutan.
- **F1-Score:** Rata-rata harmonik antara *precision* dan *recall*, menjadi rujukan utama untuk menilai performa model pada klasifikasi multi-kelas.

## 4. Pelatihan Model XGBoost dan Evaluasi Confusion Matrix

Berdasarkan hasil perbandingan model pada bagian sebelumnya, algoritma **XGBoost (Extreme Gradient Boosting)** dipilih untuk dievaluasi secara lebih mendalam karena keunggulannya dalam menangani batas keputusan non-linear yang kompleks pada data spektral citra satelit, dilengkapi mekanisme regularisasi untuk meminimalkan *overfitting*, serta efisiensi komputasi yang tinggi.

Pada tahap ini, model XGBoost dikonfigurasi dengan hyperparameter spesifik (`n_estimators=100`, `learning_rate=0.1`, `max_depth=6`), dilatih menggunakan 80% data latih, dan dievaluasi secara rinci melalui **Classification Report** serta visualisasi **Confusion Matrix**.

### Penjelasan Konfigurasi & Hyperparameter:
- **`n_estimators=100`:** Menentukan jumlah pohon keputusan (*boosting trees*) yang dilatih secara bertahap untuk meminimalkan nilai *loss function*.
- **`learning_rate=0.1` (eta):** Mengatur laju pembelajaran (penyusutan kontribusi tiap pohon), menjaga keseimbangan antara kecepatan konvergensi dan pencegahan *overfitting*.
- **`max_depth=6`:** Membatasi kedalaman maksimum setiap pohon keputusan agar pohon cukup fleksibel memisahkan 6 kelas tutupan lahan tanpa menjadi terlalu spesifik (*overfit* terhadap noise).
- **`random_state=42` & `n_jobs=-1`:** Memastikan reproduktifitas hasil pengujian dan mengoptimalkan kecepatan komputasi dengan memanfaatkan seluruh inti prosesor (*multi-threading*).

```{code-cell} ipython3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

# ==========================================
# 1. BACA DATASET & PREPROCESSING
# ==========================================
# Ganti dengan nama file CSV terakhir Anda (contoh: dataset_ekstraksi_tif_lengkap.csv)
df_final = pd.read_csv("./source/klasifikasi_jatim/data/dataset_ekstraksi_tif_lengkap.csv")

# Preprocessing: Pastikan tidak ada nilai infinity (tak terhingga) atau NaN yang tersisa
# df_final.replace([np.inf, -np.inf], np.nan, inplace=True)
# df_final.dropna(inplace=True)

# Tentukan Fitur (X) dan Target (y)
fitur_kolom = ['B02', 'B03', 'B04', 'B08', 'B11', 'NDVI', 'NDWI', 'NDBI']
X = df_final[fitur_kolom]
y = df_final['label']
nama_kelas = ['Sawah', 'Bangunan', 'Danau', 'Hutan', 'Mangrove', 'Laut']

# ==========================================
# 2. PEMISAHAN DATA (TRAIN & TEST)
# ==========================================
# Memisahkan 80% data untuk pelatihan dan 20% untuk pengujian (stratify agar proporsional)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ==========================================
# 3. PELATIHAN MODEL XGBOOST
# ==========================================
print("Melatih Model XGBoost...")
# Konfigurasi parameter dasar XGBoost
model_xgb = XGBClassifier(
    n_estimators=100,      # Jumlah pohon keputusan
    learning_rate=0.1,     # Kecepatan belajar model
    max_depth=6,           # Kedalaman maksimal pohon
    random_state=42,
    n_jobs=-1              # Gunakan semua core CPU
)

# Proses Training
model_xgb.fit(X_train, y_train)

# ==========================================
# 4. PREDIKSI & EVALUASI
# ==========================================
# Melakukan prediksi pada data pengujian
y_pred = model_xgb.predict(X_test)

print("\n==========================================")
print("          CLASSIFICATION REPORT           ")
print("==========================================")
print(classification_report(y_test, y_pred, target_names=nama_kelas))

# ==========================================
# 5. VISUALISASI CONFUSION MATRIX
# ==========================================
# Hitung matrix kebingungan (Confusion Matrix)
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=nama_kelas)

# Tampilkan grafik
fig, ax = plt.subplots(figsize=(8, 6))
disp.plot(cmap=plt.cm.Blues, ax=ax, values_format='d')
plt.title("Confusion Matrix - Klasifikasi XGBoost")
plt.xlabel("Kelas Prediksi")
plt.ylabel("Kelas Aktual")
plt.grid(False) # Mematikan grid agar matrix terlihat bersih
plt.show()
```

### Penjelasan dan Interpretasi Confusion Matrix:
- **Diagonal Utama (Kiri Atas ke Kanan Bawah):** Menunjukkan jumlah piksel/sampel yang berhasil diprediksi secara benar (*True Positive*) untuk setiap kelas (Sawah, Bangunan, Danau, Hutan, Mangrove, dan Laut). Semakin gelap warna biru pada kotak diagonal, semakin tinggi jumlah prediksi benar.
- **Elemen Luar Diagonal (*Off-Diagonal Elements*):** Mengindikasikan terjadinya misklasifikasi (*Classification Error*):
  - **Sumbu Y (Kelas Aktual):** Merupakan label acuan lapangan (*Ground Truth*).
  - **Sumbu X (Kelas Prediksi):** Merupakan hasil klasifikasi yang dikeluarkan oleh XGBoost.
  - Sebagai contoh, apabila terdapat nilai di luar diagonal pada baris *Hutan* tetapi kolom *Mangrove*, berarti ada sampel vegetasi darat yang terprediksi sebagai bakau karena adanya kemiripan nilai kehijauan (*NDVI*) dan pantulan spektral kanopi.
- **Kesimpulan Visualisasi:** Confusion Matrix ini memberikan visualisasi mendetail mengenai kelas mana yang sudah terpisah sempurna (misalnya *Laut* dan *Danau* yang terdeteksi tajam lewat nilai *NDWI*) serta kelas mana yang masih memiliki kerentanan tumpang-tindih spektral (*spectral confusion*).

## 5. Visualisasi Spasial Klasifikasi Per-Piksel Interaktif (Folium ImageOverlay)

Tahap akhir dari alur pemrosesan ini adalah melakukan inferensi spasial presisi tinggi secara *per-pixel* (piksel demi piksel) pada keseluruhan citra satelit Sentinel-2A (`sentinel2_6kelas_visual_full.tif`). Hasil klasifikasi kemudian dipetakan ke dalam format warna kanvas RGBA dan disajikan sebagai peta web interaktif berbasis **Folium** menggunakan *layer* `ImageOverlay`.

### Tahapan Utama Implementasi:
1. **Pemuatan Artefak Model & Data Sampel:**
   - Membaca model XGBoost yang telah diekspor (`model_xgb.joblib`) bersama konfigurasi urutan fitur dan label encoder.
   - Membaca koordinat centroid poligon sampel lapangan (`centroid_poligon.csv`) untuk penandaan titik validasi.
2. **Pembacaan Raster & Ekstraksi Indeks Spektral *On-the-Fly*:**
   - Membaca 5 pita spektral (`B02, B03, B04, B08, B11`) menggunakan `rasterio`.
   - Mengkalkulasi indeks turunan NDVI, NDWI, dan NDBI untuk seluruh matriks piksel citra secara simultan dengan penanganan division-by-zero (`np.nan_to_num`).
   - Melakukan transformasi batas koordinat (*bounds*) raster ke sistem koordinat geografis WGS84 (`EPSG:4326`) untuk overlay Folium.
3. **Masking Batas Daratan Jawa Timur:**
   - Melakukan rasterisasi poligon batas administratif Jawa Timur (`jawa_timur_provinsi.geojson`) menjadi masker biner berdimensi $(H, W)$.
   - Area bernilai 1 menandakan daratan (objek prediksi XGBoost), sedangkan nilai 0 menandakan laut lepas yang langsung diwarnai biru laut tanpa membebani komputasi model.
4. **Inferensi Prediksi Skala Besar & Pewarnaan RGBA:**
   - Matriks piksel diratakan (*flatten*) menjadi tabel fitur 1D untuk diproses secara paralel oleh XGBoost.
   - Hasil prediksi kelas dipetakan ke matriks warna RGBA (Red, Green, Blue, Alpha):
     - **Sawah:** Kuning (`#FFD92F`)
     - **Bangunan:** Merah (`#E41A1C`)
     - **Danau:** Biru Muda (`#4FC3F7`)
     - **Hutan:** Hijau Tua (`#2E7D32`)
     - **Mangrove:** Ungu (`#8E44AD`)
     - **Laut:** Biru Tua (`#0D47A1`)
   - Lapisan warna disusun dengan tingkat opasitas (*alpha* = 225 / ~88%) agar kontur dan tekstur dasar satelit tetap tampak serasi.
5. **Penyusunan Peta Web Interaktif (Folium):**
   - Menambahkan basemap resolusi tinggi *Esri World Imagery* dan *Google Hybrid*.
   - Menempelkan kanvas warna RGBA dengan `ImageOverlay` (opasitas 0.65).
   - Menambahkan *CircleMarker* untuk titik-titik sampel ground truth per kelas tutupan lahan.
   - Menyematkan legenda tematik LULC (*Land Use / Land Cover*) melayang berbasis HTML/CSS.
   - Menyimpan seluruh visualisasi ke file web mandiri `hasil_klasifikasi_xgboost_asli.html`.

```{code-cell} ipython3
:tags: [hide-input]

"""
Klasifikasi Presisi Per Piksel (Folium ImageOverlay) - XGBoost & Rasterio TIF
"""

import os
import folium
from folium.raster_layers import ImageOverlay
import geopandas as gpd
import joblib
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize
from rasterio.warp import transform_bounds

# =======================================================
# 1. KONFIGURASI WARNA & FOLDER
# =======================================================
DIR_XGB = "./source/klasifikasi_jatim/data" 

WARNA_KELAS = {
    "Sawah": "#FFD92F",
    "Bangunan": "#E41A1C",
    "Mangrove": "#8E44AD",
    "Hutan": "#2E7D32",         
    "Laut": "#0D47A1",          
    "Danau": "#4FC3F7",
}

def hex_ke_rgb(h):
    h = h.lstrip("#")
    return [int(h[i : i + 2], 16) for i in (0, 2, 4)]

# =======================================================
# 2. MUAT MODEL XGBOOST & TITIK SAMPEL
# =======================================================
paket = joblib.load(f"{DIR_XGB}/model_xgb.joblib")
model_xgb = paket["model"]
fitur = paket["fitur"] # ['B02', 'B03', 'B04', 'B08', 'B11', 'NDVI', 'NDWI', 'NDBI']
encoder = paket["encoder"] 
cen = pd.read_csv(f"{DIR_XGB}/centroid_poligon.csv")

# =======================================================
# 3. BACA DATA SATELIT ASLI (.TIF) & HITUNG INDEKS
# =======================================================
FILE_TIF = f"{DIR_XGB}/sentinel2_6kelas_visual_full.tif"

with rasterio.open(FILE_TIF) as src:
    # Mengambil resolusi gambar
    H, W = src.height, src.width
    
    # Membaca kelima band (B02, B03, B04, B08, B11)
    B02 = src.read(1).astype(np.float32)
    B03 = src.read(2).astype(np.float32)
    B04 = src.read(3).astype(np.float32)
    B08 = src.read(4).astype(np.float32)
    B11 = src.read(5).astype(np.float32)
    
    # Ambil batas peta dan ubah ke koordinat GPS (Lat/Lon) untuk Folium
    bounds_latlon = transform_bounds(src.crs, "EPSG:4326", *src.bounds)
    lon_w, lat_s, lon_e, lat_n = bounds_latlon
    
    transform_tif = src.transform
    crs_tif = src.crs

# Hindari error pembagian dengan nol
np.seterr(divide='ignore', invalid='ignore')

# Hitung Indeks
NDVI = (B08 - B04) / (B08 + B04)
NDWI = (B03 - B08) / (B03 + B08)
NDBI = (B11 - B08) / (B11 + B08)

# Bersihkan nilai tak terhingga (infinity/NaN) menjadi 0
NDVI = np.nan_to_num(NDVI, nan=0.0, posinf=0.0, neginf=0.0)
NDWI = np.nan_to_num(NDWI, nan=0.0, posinf=0.0, neginf=0.0)
NDBI = np.nan_to_num(NDBI, nan=0.0, posinf=0.0, neginf=0.0)

# =======================================================
# 4. MASKING DARATAN JAWA TIMUR
# =======================================================
prov = gpd.read_file(f"{DIR_XGB}/jawa_timur_provinsi.geojson")

# Pastikan koordinat shapefile Jatim sama dengan koordinat TIF
if prov.crs != crs_tif:
    prov = prov.to_crs(crs_tif)

# Ubah poligon menjadi piksel (1 untuk daratan, 0 untuk laut)
mask_daratan = rasterize(
    [(geom, 1) for geom in prov.geometry],
    out_shape=(H, W),
    transform=transform_tif,
    fill=0,
    dtype=np.uint8,
)

# =======================================================
# 5. PREDIKSI KELAS DENGAN XGBOOST
# =======================================================
# Flatten (ratakan) matriks 2D menjadi 1D untuk dimasukkan ke model
df_pred = pd.DataFrame({
    'B02': B02.flatten(), 'B03': B03.flatten(), 'B04': B04.flatten(),
    'B08': B08.flatten(), 'B11': B11.flatten(),
    'NDVI': NDVI.flatten(), 'NDWI': NDWI.flatten(), 'NDBI': NDBI.flatten()
})

mask_flat = mask_daratan.flatten()
# Cari area yang datanya valid (tidak kosong)
valid_data = B02.flatten() > 0 

# Kita hanya memprediksi area yang Valid DAN merupakan Daratan
idx_daratan_valid = (mask_flat == 1) & valid_data

# Lakukan prediksi
preds_num = model_xgb.predict(df_pred[idx_daratan_valid][fitur])
preds_teks = encoder.inverse_transform(preds_num)
preds_teks_title = np.array([str(p).title() for p in preds_teks]) # Pastikan Title Case

# =======================================================
# 6. PEMBUATAN LAPISAN WARNA (RGBA)
# =======================================================
# Buat kanvas kosong transparan (Alpha = 0)
rgba_flat = np.zeros((H * W, 4), dtype=np.uint8)

# 1. Warnai Laut (Valid data TIF, tapi di luar mask daratan)
idx_laut_valid = (mask_flat == 0) & valid_data
rgba_flat[idx_laut_valid, :3] = hex_ke_rgb(WARNA_KELAS["Laut"])
rgba_flat[idx_laut_valid, 3] = 225  # Alpha (Opasitas)

# 2. Warnai Daratan sesuai tebakan XGBoost
for k, col in WARNA_KELAS.items():
    if k == "Laut": continue
    # Cari posisi piksel daratan yang tebakannya adalah kelas 'k'
    idx_kelas = np.zeros(len(preds_teks_title), dtype=bool)
    idx_kelas[preds_teks_title == k] = True
    
    # Petakan kembali indeks kelas ke indeks array global (rgba_flat)
    posisi_global = np.where(idx_daratan_valid)[0][idx_kelas]
    
    rgba_flat[posisi_global, :3] = hex_ke_rgb(col)
    rgba_flat[posisi_global, 3] = 225 # Alpha

# Kembalikan bentuk array ke format 2D gambar
rgba_img = rgba_flat.reshape((H, W, 4))

# =======================================================
# 7. BANGUN PETA FOLIUM
# =======================================================
pusat = [(lat_s + lat_n) / 2, (lon_w + lon_e) / 2]
peta = folium.Map(location=pusat, zoom_start=8, tiles=None, control_scale=True)

folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Tiles &copy; Esri", name="Esri Satellite", max_zoom=19, overlay=False,
).add_to(peta)

folium.TileLayer(
    tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    attr="Google Hybrid", name="Google Hybrid", max_zoom=20, overlay=False, show=False,
).add_to(peta)

# Pasang gambar RGBA di atas peta
batas_peta = [[lat_s, lon_w], [lat_n, lon_e]]
ImageOverlay(
    image=rgba_img,
    bounds=batas_peta,
    opacity=0.65,
    name="Hasil Klasifikasi XGBoost (TIF Asli)",
    zindex=5,
).add_to(peta)

# Tambahkan Titik Sampel
for nama in WARNA_KELAS.keys():
    grup = folium.FeatureGroup(name=f"Titik Sampel: {nama}", show=False)
    for _, r in cen[cen['label_teks'] == nama].iterrows():
        folium.CircleMarker(
            [r["lat_centroid"], r["lon_centroid"]],
            radius=4, color="white", weight=1, fill=True,
            fill_color=WARNA_KELAS[nama], fill_opacity=1,
            popup=f"{nama}",
        ).add_to(grup)
    grup.add_to(peta)

# Legenda
item_legenda = "".join(
    f'<div style="margin:2px 0"><span'
    f' style="display:inline-block;width:14px;height:14px;background:{WARNA_KELAS[k]};border:1px'
    f' solid #333;margin-right:6px;vertical-align:middle"></span>{k}</div>'
    for k in WARNA_KELAS.keys()
)
legenda_html = (
    f'<div style="position:fixed;bottom:30px;left:30px;z-index:9999;background:rgba(255,255,255,0.95);'
    f'padding:10px 14px;border:1px solid #888;border-radius:6px;font:12px sans-serif;">'
    f'<b>Legenda LULC</b><hr style="margin:5px 0">{item_legenda}</div>'
)
peta.get_root().html.add_child(folium.Element(legenda_html))

folium.LayerControl(collapsed=False).add_to(peta)
peta.save(f"{DIR_XGB}/hasil_klasifikasi_xgboost_asli.html")

# Tampilkan di notebook
peta
```

### Penjelasan Hasil Visualisasi Peta Interaktif:
- **Ketepatan Spasial (*Pixel-wise Classification*):** Pendekatan klasifikasi per piksel mampu menangkap variasi spasial mikro di bentang alam Jawa Timur, seperti sempadan sungai, tambak/pesisir mangrove di pantai utara/selatan, serta sebaran perkotaan dan kawasan sawah.
- **Efisiensi Komputasi Melalui Masking:** Dengan memanfaatkan poligon `jawa_timur_provinsi.geojson` untuk melakukan masking daratan, waktu komputasi inferensi XGBoost berkurang drastis karena jutaan piksel laut lepas tidak perlu melalui proses prediksi model pohon, melainkan langsung diberi kelas `Laut`.
- **Interaktivitas Lapisan (*Layer Control* & *ImageOverlay*):** Pengguna dapat mengubah mode basemap antara citra satelit murni (*Esri*) atau beranotasi jalan (*Google Hybrid*), menyalakan/mematikan titik-titik sampel verifikasi lapangan, serta mengatur tingkat transparansi lapisan klasifikasi untuk memvalidasi batas tutupan lahan terhadap kondisi riil di permukaan bumi.


