<a id="bab-6"></a>

## BAB 6 — WebGIS

### Peta untuk publik: notebook + Streamlit + Book

**Alur narasi seluruh project:** masalah klasifikasi lahan Jawa Timur (Bab 1)
→ Sentinel-2 enam band selama dua hari dan 2.823 poligon sumber sekunder
(Bab 2) → saringan validitas V1–V6 menyisakan 768 poligon berpiksel valid
(Bab 2) → pemilihan 256 poligon (50 untuk lima kelas dan 6 kelas Laut)
(Bab 3) → sampel pixel 40.076/11.432 dan mean 204/52, dengan split poligon
204/52 (Bab 3) → CV sepuluh kombinasi, pemenang pixel-SVM 0,537 ± 0,072
(Bab 4) → test sekali, Macro-F1 0,474 dengan CI [0,366, 0,565] (Bab 5) →
peta pixel-RF untuk inferensi dan WebGIS (bab ini).

Nilai 0,537 ± 0,072 adalah hasil terbaik pencarian parameter di notebook
modeling. Tabel ringkasan konfigurasi akhir `test_vs_cv.csv` yang dirujuk pada
Bab 5 mencatat CV pixel-SVM 0,521 ± 0,071.

Notebook bersifat statis: tidak memakai `ipywidgets`; overlay kategorikal
di-decimate dan direproyeksikan dengan nearest-neighbor; basemap hanya
konteks visual. Kode dan output di bawah ini adalah cuplikan dari notebook
[06_webgis.ipynb](https://github.com/Rahardian-Ananta/PSD-Klasifikasi-Lahan/blob/main/notebooks/06_webgis.ipynb).

### 6.1 WebGIS di dalam notebook

#### 6.1a Membuat overlay PNG

Raster kategori diturunkan skalanya 1/20, diproyeksikan ke EPSG:4326 dengan
nearest-neighbor, lalu diubah menjadi RGBA. Metode nearest mempertahankan ID
kelas dan tidak menciptakan kelas interpolasi.

```python
import numpy as np
import json
import os
import rasterio
from PIL import Image
from rasterio.warp import Resampling, calculate_default_transform, reproject

os.makedirs("../outputs/figures", exist_ok=True)
LUT = {
    0: (0, 0, 0, 0), 1: (255, 255, 0, 255),
    2: (255, 0, 0, 255), 3: (0, 255, 0, 255),
    4: (255, 0, 255, 255), 5: (0, 0, 255, 255),
    6: (0, 255, 255, 255),
}
with rasterio.open("../outputs/raster/klasifikasi_jawa_timur.tif") as src:
    print(f"DATA AKTUAL PROJECT: sumber {src.width}x{src.height} {src.crs}")
    h, w = src.height // 20, src.width // 20
    small = src.read(1, out_shape=(h, w), resampling=Resampling.nearest)
    transform = src.transform * src.transform.scale(
        src.width / w, src.height / h
    )
    dst_transform, dst_width, dst_height = calculate_default_transform(
        src.crs, "EPSG:4326", w, h,
        left=src.bounds.left, bottom=src.bounds.bottom,
        right=src.bounds.right, top=src.bounds.top,
    )
    classes = np.zeros((dst_height, dst_width), dtype=np.uint8)
    reproject(
        small, classes,
        src_transform=transform, src_crs=src.crs,
        dst_transform=dst_transform, dst_crs="EPSG:4326",
        resampling=Resampling.nearest,
    )
    rgba = np.zeros((*classes.shape, 4), dtype=np.uint8)
    for class_id, color in LUT.items():
        rgba[classes == class_id] = color
    Image.fromarray(rgba).save("../outputs/figures/klasifikasi_overlay.png")
    size = os.path.getsize("../outputs/figures/klasifikasi_overlay.png")
    print(f"DATA AKTUAL PROJECT: PNG {dst_width}x{dst_height} = {size:,} byte")
    bounds4326 = [
        dst_transform.c,
        dst_transform.f + dst_transform.e * dst_height,
        dst_transform.c + dst_transform.a * dst_width,
        dst_transform.f,
    ]
    with open("../outputs/figures/overlay_bounds.json", "w", encoding="utf-8") as f:
        json.dump({"bounds4326": bounds4326}, f)
    print(f"DATA AKTUAL PROJECT: bounds4326 = {[round(x, 4) for x in bounds4326]}")
```

```text
DATA AKTUAL PROJECT: sumber 59412x41323 EPSG:32749
DATA AKTUAL PROJECT: PNG 2984x2079 = 281,571 byte
DATA AKTUAL PROJECT: bounds4326 = [110.8986, -8.7966, 116.2938, -5.0377]
```

#### 6.1b Peta Folium: basemap, overlay, batas, legenda, dan slider opacity

Peta menggunakan Esri World Imagery sebagai layer awal, Google Satellite
sebagai opsi, batas provinsi, overlay enam kelas, kontrol layer, legenda, dan
slider opacity JavaScript. Basemap adalah tile XYZ, bukan layanan WMS.

```python
import geopandas as gpd
import folium
from folium.elements import MacroElement
from jinja2 import Template
import json

CLASS_NAMES = {
    1: "Sawah", 2: "Bangunan / Permukiman", 3: "Mangrove",
    4: "Lahan hijau", 5: "Laut", 6: "Danau",
}
CLASS_COLORS = {
    1: "#FFFF00", 2: "#FF0000", 3: "#00FF00",
    4: "#FF00FF", 5: "#0000FF", 6: "#00FFFF",
}

class OpacitySlider(MacroElement):
    def __init__(self, layer_name, label="Opacity klasifikasi"):
        super().__init__()
        self.layer_name = layer_name
        self.label = label
        self._template = Template("""
        {% macro html(this, kwargs) %}
        <div style="position:fixed;top:10px;right:10px;z-index:9999;
                    background:white;padding:6px 10px;border:2px solid grey;">
          {{ this.label }}<br>
          <input id="opacity-slider" type="range" min="0" max="1"
                 step="0.05" value="0.7" style="width:140px;">
        </div>
        {% endmacro %}
        {% macro script(this, kwargs) %}
        {{ this.layer_name }}.setOpacity(0.7);
        document.getElementById("opacity-slider").addEventListener(
            "input", function(e) {
                {{ this.layer_name }}.setOpacity(parseFloat(e.target.value));
            }
        );
        {% endmacro %}
        """)

boundary = gpd.read_file("../data/boundary_jatim.geojson").to_crs("EPSG:4326")
vertices_before = sum(
    len(part.exterior.coords) for part in boundary.geometry.values[0].geoms
)
boundary_simplified = boundary.simplify(0.005)
vertices_after = sum(
    len(part.exterior.coords) for part in boundary_simplified.values[0].geoms
)
print(
    f"DATA AKTUAL PROJECT: boundary vertex {vertices_before} -> "
    f"{vertices_after} (toleransi 0.005 derajat)"
)
with open("../outputs/figures/overlay_bounds.json", encoding="utf-8") as f:
    bounds = json.load(f)["bounds4326"]

map_jatim = folium.Map(
    location=[(boundary.total_bounds[1] + boundary.total_bounds[3]) / 2,
              (boundary.total_bounds[0] + boundary.total_bounds[2]) / 2],
    zoom_start=7,
    tiles=None,
)
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
          "World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri World Imagery", name="Esri World Imagery",
    overlay=False, control=True,
).add_to(map_jatim)
folium.TileLayer(
    tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
    attr="Google Satellite", name="Google Satellite",
    overlay=False, control=True,
).add_to(map_jatim)
overlay = folium.raster_layers.ImageOverlay(
    name="Klasifikasi (6 kelas)",
    image="../outputs/figures/klasifikasi_overlay.png",
    bounds=[[bounds[1], bounds[0]], [bounds[3], bounds[2]]],
    opacity=0.7,
).add_to(map_jatim)
folium.GeoJson(
    boundary_simplified.__geo_interface__,
    name="Batas Jatim",
    style_function=lambda feature: {
        "color": "black", "weight": 2.5, "fill": False
    },
).add_to(map_jatim)
map_jatim.add_child(OpacitySlider(overlay.get_name()))
folium.LayerControl(collapsed=False).add_to(map_jatim)
legend = (
    "<div style='position:fixed;bottom:20px;left:10px;z-index:9999;"
    "background:white;padding:8px;border:2px solid grey;'>"
    "<b>Legenda</b><br>"
    + "<br>".join(
        f"<span style='background:{color};display:inline-block;"
        f"width:12px;height:12px;'></span> {class_id} {name}"
        for class_id, name in CLASS_NAMES.items()
        for color in [CLASS_COLORS[class_id]]
    )
    + "</div>"
)
map_jatim.get_root().html.add_child(folium.Element(legend))
map_jatim.save("../outputs/figures/webgis.html")
print("DATA AKTUAL PROJECT: webgis tersimpan, overlay+border+legenda+slider")
```

```text
DATA AKTUAL PROJECT: boundary vertex 6496 -> 2664
DATA AKTUAL PROJECT: webgis tersimpan, overlay+border+legenda+slider
```

Peta interaktif hasil notebook. Esri World Imagery dan Google Satellite
tersedia sebagai pilihan basemap di kontrol layer:

<iframe title="WebGIS referensi Jawa Timur dengan basemap dan overlay klasifikasi" src="../_static/uts-ref-webgis.html" width="100%" height="800" loading="lazy"></iframe>

File HTML peta besarnya sekitar 443 KB. Peta tetap interaktif pada Jupyter
Book statis; tile basemap memerlukan koneksi internet. Overlay dan garis batas
bisa diatur melalui kontrol layer, dan slider mengubah opacity overlay.

#### Luas hasil klasifikasi

```python
import pandas as pd

luas = pd.read_csv("../outputs/tables/luas_per_kelas.csv")
print(luas.to_string(index=False))
print(f"Total luas = {luas['luas_ha'].sum():,.1f} ha")
```

```text
DATA AKTUAL PROJECT: luas per kelas (ha) =
class_id  class_name             pixel_count  luas_ha   persen
1         Sawah                  52620770     526207.7  36.72
2         Bangunan / Permukiman  25785506     257855.1  18.00
3         Mangrove               13422371     134223.7   9.37
4         Lahan hijau            47351462     473514.6  33.05
5         Laut                    1425642      14256.4   0.99
6         Danau                   2682354      26823.5   1.87
DATA AKTUAL PROJECT: total = 1,432,881.0 ha
```

Tabel hasil:

| ID | Kelas | Piksel | Luas (ha) | Persen |
|---:|---|---:|---:|---:|
| 1 | Sawah | 52.620.770 | 526.207,7 | 36,72 |
| 2 | Bangunan / Permukiman | 25.785.506 | 257.855,1 | 18,00 |
| 3 | Mangrove | 13.422.371 | 134.223,7 | 9,37 |
| 4 | Lahan hijau | 47.351.462 | 473.514,6 | 33,05 |
| 5 | Laut | 1.425.642 | 14.256,4 | 0,99 |
| 6 | Danau | 2.682.354 | 26.823,5 | 1,87 |
| | **Total** | | **1.432.881,0** | **100,00** |

**Interpretasi 6.1:** overlay berukuran 2.984 × 2.079 piksel, sekitar 20 kali
lebih kecil pada tiap dimensi (sekitar 396 kali lebih sedikit piksel) daripada
raster sumber 59.412 × 41.323. Nearest-neighbor menjaga label kelas, tetapi
blok piksel menjadi lebih kasar dan detail kecil dapat hilang. Penyederhanaan
garis batas mengurangi verteks 6.496 menjadi 2.664 dengan toleransi 0,005°.
Jumlah luas berasal dari CSV keluaran Tahap 5.

### 6.2 Analisis kebijakan (dibatasi data)

- Luas hasil (ha): Sawah 526.208; Lahan hijau 473.515; Bangunan 257.855;
  Mangrove 134.224; Danau 26.824; Laut 14.256.
- Luas per kabupaten/kota **tidak tersedia**: data batas yang dipakai adalah
  satu fitur provinsi; batas kabupaten/kota tidak diunduh untuk analisis ini.
- Sawah (36,7%) dan bangunan (18,0%) dapat menjadi bahan pertimbangan untuk
  pemeriksaan perlindungan lahan pertanian. Mangrove (9,4%) relevan untuk
  pengelolaan pesisir, sementara danau/waduk (1,9%) luasnya kecil tetapi
  penting bagi sumber daya air. Ini bukan kesimpulan sebab-akibat.
- Satu snapshot 1–2 September 2025 tidak menunjukkan perubahan dari waktu ke
  waktu. Akurasi mengikuti label sumber sekunder (test Macro-F1 0,47); enam
  kelas merupakan penyederhanaan legenda, dan awan/tambak yang tidak berkelas
  dapat menyebabkan piksel salah klasifikasi.

### Checkpoint Tahap 6

- Output notebook menampilkan peta Folium dengan Esri sebagai basemap awal,
  Google Satellite sebagai opsi, kontrol layer, legenda enam kelas, slider
  opacity JavaScript, dan batas provinsi.
- Notebook enam berukuran 459.907 byte, jauh di bawah batas berkas GitHub
  sebesar 100 MB.
- Repository referensi menyediakan
  [`app.py`](https://github.com/Rahardian-Ananta/PSD-Klasifikasi-Lahan/blob/main/app.py)
  (empat halaman: peta, luas, evaluasi, metodologi),
  [`requirements.txt`](https://github.com/Rahardian-Ananta/PSD-Klasifikasi-Lahan/blob/main/requirements.txt),
  dan [panduan deployment](https://github.com/Rahardian-Ananta/PSD-Klasifikasi-Lahan/blob/main/deployment.md).
  Aplikasi Streamlit tersebut belum di-deploy.
- Book menggunakan `_toc.yml`; notebook tidak dijalankan ulang otomatis
  (`execute_notebooks: off`) dan data/raster/model mentah dikecualikan dari
  build.

Sumber: [notebook asli 06_webgis](https://rahardian-ananta.github.io/PSD-Klasifikasi-Lahan/notebooks/06_webgis.html)
dan [repository PSD-Klasifikasi-Lahan](https://github.com/Rahardian-Ananta/PSD-Klasifikasi-Lahan).
