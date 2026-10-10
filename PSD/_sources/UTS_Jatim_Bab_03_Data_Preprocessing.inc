<a id="bab-3"></a>

## Bab 3 — Data Preprocessing

![Alur pra-pemrosesan dan pembentukan fitur](../_static/uts-workflow.svg)

### 3.1 Pemeriksaan dan penyelarasan

Sebelum eksperimen, periksa jumlah band, CRS, transform, resolusi, rentang
nilai, NoData, dan cakupan tumpang-susun. GeoTIFF referensi berisi enam band
yang digunakan pada grid 10 m EPSG:32749. Batas wilayah dan sampel poligon
diselaraskan dengan CRS raster; komposit citra sudah difilter awan sebelum
ekspor. Profil raster sumber mencatat 59.412 × 41.323 piksel. Raster inferensi
tersedia sebagai GeoTIFF 44 MB pada folder output referensi.

### 3.2 Crosswalk label

Label sampel diseragamkan menjadi enam ID kelas: 1 Sawah, 2
Bangunan/Permukiman, 3 Mangrove, 4 Lahan hijau, 5 Laut, dan 6 Danau. Kelas
asal dipertahankan pada atribut sumber; misalnya Sawah berasal dari Kementan,
vegetasi dan permukiman dari BIG, dan Laut dari Natural Earth.

### 3.3 Fitur model

Eksperimen referensi memakai enam band reflektansi dan tiga indeks, total
sembilan fitur. Berikut deskripsi fitur yang cocok dengan metadata eksperimen:

| Fitur | Rumus | Kegunaan umum |
|---|---|---|
| B02 | Reflektansi biru | Warna tampak/pesisir |
| B03 | Reflektansi hijau | Warna tampak dan air |
| B04 | Reflektansi merah | Serapan klorofil |
| B08 | Reflektansi NIR | Vegetasi sehat dan air |
| B11 | Reflektansi SWIR-1 | Kelembapan/permukaan terbangun |
| B12 | Reflektansi SWIR-2 | Kelembapan/tanah |
| NDVI | `(B8 - B4) / (B8 + B4)` | Kehijauan vegetasi |
| NDWI | `(B3 - B8) / (B3 + B8)` | Indeks air Green–NIR |
| NDBI | `(B11 - B8) / (B11 + B8)` | Respons lahan terbangun |

Contoh perhitungan indeks pada array NumPy:

```python
import numpy as np

# Urutan input: B02, B03, B04, B08, B11, B12
B02, B03, B04, B08, B11, B12 = bands

def normalized_difference(a, b, eps=1e-6):
    denominator = a + b
    return np.divide(
        a - b,
        denominator,
        out=np.zeros_like(a, dtype=np.float32),
        where=np.abs(denominator) > eps,
    )

features = np.stack([
    B02, B03, B04, B08, B11, B12,
    normalized_difference(B08, B04),  # NDVI
    normalized_difference(B03, B08),  # NDWI
    normalized_difference(B11, B08),  # NDBI
])
print(features.shape)
```

```text
(9, tinggi_raster, lebar_raster)
```

Eksperimen referensi memakai sembilan fitur tersebut. Dashboard interaktif
terpisah di repository UTS saat ini memiliki pipeline 18 fitur; skor di Bab 5
adalah hasil notebook referensi, bukan output dashboard tersebut.

### 3.4 Sampel dan pembagian spasial

Split referensi yang tersimpan berisi 204 poligon training dan 52 testing dari
256 poligon. Pembagian dilakukan per poligon/FID, distratifikasi dengan ID
kelas, sehingga FID tidak muncul pada kedua subset:

```python
from sklearn.model_selection import train_test_split

train_polygons, test_polygons = train_test_split(
    polygons,
    test_size=0.20,
    random_state=42,
    stratify=polygons["class_id"],
)
assert set(train_polygons["FID"]).isdisjoint(test_polygons["FID"])
print(len(train_polygons), len(test_polygons))
```

```text
204 52
```

Contoh di atas menjelaskan pemisahan berdasarkan poligon; file split aktual dapat dilihat di
[`polygon_split.csv`](https://github.com/Rahardian-Ananta/PSD-Klasifikasi-Lahan/blob/main/outputs/tables/polygon_split.csv).
Dashboard UTS sendiri memakai sampling dan pembagian spasial yang berbeda;
hasilnya tidak sama dengan split referensi.

![Distribusi nilai piksel pada eksperimen referensi](../_static/uts-ref-pixel-distribution.png)
