# Bab 3 — Data Preprocessing

## 3.1 Pemeriksaan dan penyelarasan

Sebelum eksperimen, periksa jumlah band, CRS, transform, resolusi, rentang
nilai, NoData, dan cakupan tumpang-susun. GeoTIFF Sentinel-2 wajib berisi
minimal sepuluh band pada urutan B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12
dengan grid bersama. Nilai boleh berupa reflektansi 0–1 atau DN 0–10000.
WorldCover diselaraskan ke grid citra memakai nearest-neighbour agar kode kelas
tetap kategori, bukan nilai interpolasi.

Batas AOI dan geometri danau diproyeksikan ke CRS raster sebelum dirasterisasi.
Piksel di luar AOI dan piksel yang memiliki fitur tidak valid dikeluarkan dari
eksperimen. Mask awan harus diterapkan pada proses penyediaan komposit citra.
Raster pratinjau aplikasi dibatasi hingga 1.200 piksel pada sisi terpanjang;
hasilnya tidak setara peta resolusi penuh.

## 3.2 Crosswalk label

| Kode WorldCover | Kelas studi |
|---:|---|
| 40 | Sawah* |
| 50 | Bangunan |
| 95 | Mangrove |
| 10, 20, 30 | Lahan hijau |
| 80 di dalam poligon danau OSM | Danau/Ranu* |
| 80 di luar poligon danau OSM | Perairan terbuka |

Kelas proksi tidak diartikan sebagai label lapangan. Poligon OSM hanya
memisahkan air yang beririsan secara spasial dengan poligon danau yang
diunggah.

## 3.3 Fitur model

Sepuluh fitur pertama adalah reflektansi band. Delapan indeks dihitung per
piksel. Pembagian dengan penyebut mendekati nol dihindari agar tidak
menghasilkan nilai tak terhingga.

| Fitur | Rumus | Kegunaan umum |
|---|---|---|
| `B2_blue`, `B3_green`, `B4_red` | Reflektansi band | Warna tampak, air, vegetasi |
| `B5_rededge1`, `B6_rededge2`, `B7_rededge3` | Reflektansi band | Respons red-edge/vegetasi |
| `B8_nir`, `B8A_rededge4` | Reflektansi band | Vegetasi sehat, pemisahan air |
| `B11_swir1`, `B12_swir2` | Reflektansi band | Kelembapan, tanah, permukaan terbangun |
| NDVI | `(B8 - B4) / (B8 + B4)` | Kehijauan vegetasi |
| NDWI | `(B3 - B8) / (B3 + B8)` | Indeks air Green–NIR |
| MNDWI | `(B3 - B11) / (B3 + B11)` | Air dibanding sebagian permukaan terbangun |
| NDMI | `(B8 - B11) / (B8 + B11)` | Kelembapan vegetasi |
| NDBI | `(B11 - B8) / (B11 + B8)` | Respons lahan terbangun |
| NDRE | `(B8A - B5) / (B8A + B5)` | Respons vegetasi red-edge |
| SAVI | `1.5 × (B8 - B4) / (B8 + B4 + 0.5)` | Vegetasi dengan koreksi tanah |
| BSI | `((B11 + B4) - (B8 + B2)) / ((B11 + B4) + (B8 + B2))` | Tanah terbuka/permukaan cerah |

Delapan belas fitur tersebut merupakan rancangan UTS ini. Jumlah dan rumus
fitur tidak disalin dari eksperimen referensi.

## 3.4 Sampel dan pembagian spasial

Aplikasi mengambil sampel berimbang per kelas sampai batas maksimum yang
dipilih pengguna. Sampel dikelompokkan dalam blok 100 piksel pada raster
pratinjau; satu pembagian holdout berbasis grup digunakan bersama oleh seluruh
model untuk mengurangi kebocoran antarpiksel bertetangga.

**Jumlah aktual belum tersedia** sampai GeoTIFF dan vektor AOI/OSM dimasukkan.
Jumlah yang dipilih di kontrol aplikasi adalah batas, bukan jaminan jumlah
sampel valid. Kelas yang tidak memiliki cakupan valid membuat eksperimen
berhenti dengan pesan kesalahan, bukan menghapus kelas secara diam-diam.
