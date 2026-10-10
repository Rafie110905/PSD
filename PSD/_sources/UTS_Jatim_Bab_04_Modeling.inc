<a id="bab-4"></a>

## Bab 4 — Modeling

![Perbandingan CV Macro-F1 sepuluh kombinasi model](../_static/uts-ref-cv-scores.png)

### 4.1 Target dan rancangan model

Target terdiri atas enam kelas: Sawah, Bangunan/Permukiman, Mangrove, Lahan
hijau, Laut, dan Danau. Setiap sampel memiliki sembilan fitur Sentinel-2 dari
Bab 3. Eksperimen membandingkan dua representasi (fitur per-pixel dan
rata-rata fitur per-poligon); seluruh model pada representasi yang sama
menggunakan split yang sama.

Pada eksperimen referensi, dua representasi fitur (*pixel* dan rata-rata
poligon/`mean`) dibandingkan dengan lima model: Random Forest, Extra Trees,
LightGBM, SVM RBF, dan Logistic Regression. Total ada sepuluh kombinasi.

Contoh kode CV berkelompok berdasarkan FID:

```python
from sklearn.model_selection import StratifiedGroupKFold, cross_val_score

cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(
    estimator,
    X_train,
    y_train,
    groups=fid_train,
    cv=cv,
    scoring="f1_macro",
    n_jobs=-1,
)
print(scores.mean(), scores.std())
```

```text
Pixel SVM: CV Macro-F1 = 0.521 (rerata fold; tabel test lengkap ada di Bab 5)
```

Satu group FID diperlakukan sebagai satu poligon saat validasi agar piksel dari
poligon yang sama tidak tersebar ke fold training dan validasi.

Variabel `estimator`, `X_train`, `y_train`, dan `fid_train` diisi dari tahap
preprocessing notebook. Kode tersebut menghasilkan skor per fold; nilai
ringkas eksperimen tersimpan pada tabel Bab 5.

### 4.2 Training dan inferensi

1. Bentuk fitur pixel dan ringkasan rata-rata fitur per poligon.
2. Pilih 256 poligon dengan distribusi kelas yang dicatat di Bab 2.
3. Pisahkan 204 poligon training dan 52 testing berdasarkan FID.
4. Bandingkan lima estimator pada dua representasi fitur.
5. Pilih SVM pixel berdasarkan CV Macro-F1; ukur juga performa pada test.
6. Jalankan Random Forest pixel untuk membuat raster seluruh wilayah karena
   inferensinya lebih cepat.

SVM dan Logistic Regression memerlukan standardisasi fitur. Seluruh langkah
preprocessing model harus di-fit pada data training saja.

### 4.3 Batas klaim

Split berdasarkan FID mengurangi kebocoran antar piksel dalam poligon yang
sama, tetapi tidak menjadikan sumber label independen atau menggantikan
validasi lapangan. Model yang menang adalah yang paling sesuai pada data dan
protokol eksperimen tersebut; hasil tidak otomatis berlaku pada musim/tahun
lain atau seluruh kondisi lapangan.

Dashboard UTS di repository ini masih membandingkan empat model pada fitur
berbeda dan split blok piksel. Tabel pada Bab 5 berasal dari hasil run
referensi; jangan menyebutnya sebagai metrik dashboard UTS.

![Pentingnya fitur pada model referensi](../_static/uts-ref-feature-importance.png)
