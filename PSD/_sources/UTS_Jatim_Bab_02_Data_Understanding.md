# Bab 2 — Data Understanding

## 2.1 Inventaris dan status data

| Dataset | Fungsi | Status repository |
|---|---|---|
| Sentinel-2A Level-2A | Fitur reflektansi | GeoTIFF seluruh Jawa Timur belum tersedia |
| ESA WorldCover 2021 v200 | Label awal kelas penutup lahan | Tile/mosaik AOI belum tersedia |
| Batas Provinsi Jawa Timur | AOI dan masking | GeoJSON perlu disediakan |
| Poligon danau/ranu OSM | Memisahkan sebagian kelas air | GeoJSON perlu disediakan dan ditinjau |
| Sawah/bukan-sawah Bangkalan | Contoh sampel lokal | Tersedia untuk dua kelas saja; tidak mewakili enam kelas provinsi |

Karena input tersebut belum lengkap, jumlah sampel aktual dan hasil uji belum
dapat dihitung. Jangan mengisi tabel eksperimen dengan angka contoh atau angka
dari proyek lain.

## 2.2 Pengumpulan data

Gunakan produk Sentinel-2 Level-2A (*Bottom-of-Atmosphere surface reflectance*)
dengan tanggal komposit yang dicatat. Komposit multi-temporal yang telah
dimask awan dan bayangan awan lebih sesuai daripada satu citra berawan.
WorldCover 2021 v200 menyediakan referensi kelas 10 m; pertahankan kode kelas
aslinya sebelum crosswalk. Unduh batas provinsi resmi dan poligon danau/ranu
OSM, lalu catat sumber, tanggal pengambilan, dan CRS.

### Contoh ekspor Google Earth Engine

Unggah batas Jawa Timur ke Earth Engine Assets dan ganti asset path berikut.
Ekspor Sentinel-2 dan WorldCover secara terpisah pada satu grid 100 m untuk
contoh regional dan batas ukuran upload. Skala 100 m tidak mewakili produk
rinci 10 m.

```javascript
var roi = ee.FeatureCollection(
  'projects/PROJECT_ANDA/assets/jawa_timur'
).geometry();

function maskClouds(image) {
  var scl = image.select('SCL');
  var clear = scl.neq(0).and(scl.neq(1)).and(scl.neq(3))
    .and(scl.neq(8)).and(scl.neq(9)).and(scl.neq(10)).and(scl.neq(11));
  return image.updateMask(clear);
}

var bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12'];
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(roi)
  .filterDate('2021-01-01', '2022-01-01')
  .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', 70))
  .map(maskClouds)
  .select(bands)
  .median()
  .clip(roi)
  .toInt16();

var wc100 = ee.ImageCollection('ESA/WorldCover/v200').first()
  .select('Map')
  .reduceResolution({reducer: ee.Reducer.mode(), maxPixels: 1024})
  .reproject({crs: 'EPSG:6933', scale: 100})
  .clip(roi);

Export.image.toDrive({
  image: s2, description: 'JawaTimur_Sentinel2_2021_100m',
  region: roi, crs: 'EPSG:6933', scale: 100, maxPixels: 1e13
});
Export.image.toDrive({
  image: wc100, description: 'JawaTimur_WorldCover_2021_100m',
  region: roi, crs: 'EPSG:6933', scale: 100, maxPixels: 1e13
});
```

## 2.3 Band Sentinel-2A

Instrumen MSI Sentinel-2 mengukur 13 band pada resolusi asli 10 m, 20 m, atau
60 m. Aplikasi memakai sepuluh band untuk fitur, semuanya diregistrasikan ke
satu grid. Resampling band 20 m menyamakan grid, tetapi tidak menambah
informasi spasial.

| Band | Nama | Panjang gelombang tengah (µm) | Resolusi | Kegunaan umum |
|---|---|---:|---:|---|
| B1 | Coastal aerosol | 0.443 | 60 m | Aerosol pesisir/koreksi atmosfer |
| B2 | Blue | 0.490 | 10 m | Warna tampak dan air dangkal |
| B3 | Green | 0.560 | 10 m | Warna vegetasi dan respons air |
| B4 | Red | 0.665 | 10 m | Serapan klorofil dan batas vegetasi |
| B5 | Red Edge 1 | 0.705 | 20 m | Kondisi vegetasi |
| B6 | Red Edge 2 | 0.740 | 20 m | Gradien red-edge |
| B7 | Red Edge 3 | 0.783 | 20 m | Vegetasi dan biomassa |
| B8 | Near Infrared | 0.842 | 10 m | Vegetasi sehat dan pemisahan air |
| B8A | Narrow NIR | 0.865 | 20 m | Respons NIR sempit |
| B9 | Water vapour | 0.945 | 60 m | Uap air atmosfer |
| B10 | Cirrus | 1.375 | 60 m | Deteksi cirrus |
| B11 | SWIR 1 | 1.610 | 20 m | Kelembapan dan lahan terbangun |
| B12 | SWIR 2 | 2.190 | 20 m | Kelembapan, tanah, kebakaran |

## 2.4 Kualitas dan keterbatasan referensi

WorldCover 40 berarti *cropland*, bukan sawah secara eksklusif. WorldCover 80
adalah badan air permanen, bukan kelas laut murni. Pemisahan Danau/Ranu memakai
OSM sehingga bergantung pada kelengkapan geometri; air lain dapat tercampur
dalam kelas Perairan terbuka. Beda tahun citra dan label, piksel campuran,
awan, dan perubahan tutupan lahan juga dapat memengaruhi kesesuaian.
