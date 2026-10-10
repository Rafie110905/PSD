from __future__ import annotations

import json
from io import BytesIO

import folium
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
import streamlit as st
from rasterio.io import MemoryFile
from rasterio.warp import transform_geom
from shapely.geometry import shape

from classifier import (
    CLASS_COLORS,
    CLASS_NAMES,
    FEATURE_NAMES,
    Experiment,
    assign_lake_reference,
    build_experiment,
    calculate_features,
    classification_rgb,
    classify_preview,
    geographic_bounds,
    rasterize_aoi,
    read_preview_stack,
    read_reference_labels,
)


PAGES = (
    "Ringkasan",
    "Alur Data → Model",
    "Peta Klasifikasi",
    "Luas per Kelas",
    "Evaluasi Model",
    "Data & Unduhan",
    "Metodologi",
)
RESULT_KEY = "classification_result"

st.set_page_config(
    page_title="SIG Jawa Timur | Klasifikasi Penutup Lahan",
    page_icon="🛰️",
    layout="wide",
)


def read_geojson(uploaded_file) -> tuple[list[dict], str]:
    try:
        document = json.loads(uploaded_file.getvalue())
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError(f"{uploaded_file.name} bukan GeoJSON yang valid.") from error
    geometries = [
        shape(feature["geometry"])
        for feature in document.get("features", [])
        if feature.get("geometry")
    ]
    if not geometries:
        raise ValueError(f"Tidak ada geometri yang dapat dibaca di {uploaded_file.name}.")
    source_crs = (document.get("crs") or {}).get("properties", {}).get(
        "name", "EPSG:4326"
    )
    return geometries, source_crs


def project_geometries(geometries, source_crs, target_crs) -> list[dict]:
    return [
        transform_geom(source_crs, target_crs, geometry.__geo_interface__)
        for geometry in geometries
    ]


def preview_band_rgb(bands: np.ndarray) -> np.ndarray:
    red, green, blue = bands[2], bands[1], bands[0]
    image = []
    for band in (red, green, blue):
        valid = band[np.isfinite(band)]
        if not valid.size:
            raise ValueError("Band RGB tidak memiliki piksel valid untuk ditampilkan.")
        low, high = np.percentile(valid, [2, 98])
        image.append(np.clip((band - low) / max(high - low, 1e-6), 0, 1))
    return np.dstack(image)


def make_rgb_png(rgba: np.ndarray) -> bytes:
    output = BytesIO()
    plt.imsave(output, rgba)
    return output.getvalue()


def execute_experiment(
    sentinel_upload,
    worldcover_upload,
    aoi_upload,
    lake_upload,
    sample_limit: int,
    seed: int,
) -> dict:
    aoi_geometries, aoi_crs = read_geojson(aoi_upload)
    lake_geometries, lake_crs = read_geojson(lake_upload)

    with MemoryFile(sentinel_upload.getvalue()) as sentinel_memory, MemoryFile(
        worldcover_upload.getvalue()
    ) as worldcover_memory:
        with sentinel_memory.open() as sentinel, worldcover_memory.open() as worldcover:
            if sentinel.count < 10:
                raise ValueError(
                    f"Citra Sentinel-2 memiliki {sentinel.count} band; dibutuhkan 10."
                )
            if sentinel.crs is None or worldcover.crs is None:
                raise ValueError("Kedua GeoTIFF harus memiliki metadata CRS.")

            bands, preview_transform = read_preview_stack(sentinel)
            target_crs = sentinel.crs
            projected_aoi = project_geometries(aoi_geometries, aoi_crs, target_crs)
            projected_lakes = project_geometries(lake_geometries, lake_crs, target_crs)
            labels = read_reference_labels(
                worldcover, bands.shape[1:], preview_transform, target_crs
            )
            labels = assign_lake_reference(labels, projected_lakes, preview_transform)
            aoi_mask = rasterize_aoi(
                projected_aoi, bands.shape[1:], preview_transform
            )
            features = calculate_features(bands)
            experiment = build_experiment(
                features,
                labels,
                aoi_mask,
                seed=seed,
                max_samples_per_class=sample_limit,
            )
            class_map = classify_preview(experiment.selected, bands, aoi_mask)
            bounds = geographic_bounds(sentinel)
            source_dimensions = (sentinel.width, sentinel.height)
            source_crs = sentinel.crs

        rgb = preview_band_rgb(bands)
        rgb[~aoi_mask] = 0.0
        classification_overlay = classification_rgb(class_map)
        classification_overlay[~aoi_mask, 3] = 0
        profile = {
            "driver": "GTiff",
            "height": class_map.shape[0],
            "width": class_map.shape[1],
            "count": 1,
            "dtype": "uint8",
            "crs": source_crs,
            "transform": preview_transform,
            "nodata": 0,
            "compress": "deflate",
        }
        with MemoryFile() as output_memory:
            with output_memory.open(**profile) as output_dataset:
                output_dataset.write(class_map, 1)
            prediction_tif = output_memory.read()

    return {
        "experiment": experiment,
        "class_map": class_map,
        "rgb": rgb,
        "overlay": classification_overlay,
        "bounds": bounds,
        "source_dimensions": source_dimensions,
        "preview_dimensions": (bands.shape[2], bands.shape[1]),
        "crs": source_crs,
        "transform": preview_transform,
        "prediction_tif": prediction_tif,
        "input_names": (
            sentinel_upload.name,
            worldcover_upload.name,
            aoi_upload.name,
            lake_upload.name,
        ),
    }


def render_map(result: dict) -> None:
    bounds = result["bounds"]
    center_lat = (bounds[0][0] + bounds[1][0]) / 2
    center_lon = (bounds[0][1] + bounds[1][1]) / 2
    class_map = result["class_map"]
    map_view = folium.Map(location=[center_lat, center_lon], zoom_start=7, tiles=None)
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google Satellite",
        name="Google Satellite",
        overlay=False,
        control=True,
    ).add_to(map_view)
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attr="Google Satellite Hybrid",
        name="Google Satellite Hybrid",
        overlay=False,
        control=True,
    ).add_to(map_view)
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(map_view)
    folium.raster_layers.ImageOverlay(
        image=make_rgb_png(result["overlay"]),
        bounds=bounds,
        opacity=0.85,
        name="Prediksi klasifikasi",
        interactive=True,
        cross_origin=False,
        zindex=2,
    ).add_to(map_view)
    legend = (
        '<div style="position:fixed;bottom:35px;left:35px;z-index:9999;'
        'background:white;color:#222;padding:10px 12px;border-radius:5px;'
        'box-shadow:0 1px 5px #666"><b>Prediksi penutup lahan</b><br>'
    )
    for class_id, class_name in CLASS_NAMES.items():
        pixels = int(np.count_nonzero(class_map == class_id))
        legend += (
            f'<span style="color:{CLASS_COLORS[class_id]}">■</span> '
            f"{class_name} ({pixels:,} piksel)<br>"
        )
    legend += "</div>"
    map_view.get_root().html.add_child(folium.Element(legend))
    folium.LayerControl(collapsed=False).add_to(map_view)
    st.components.v1.html(map_view.get_root().render(), height=650, scrolling=False)


def model_table(experiment: Experiment) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Model": item["model"],
                "Accuracy": item["accuracy"],
                "Balanced accuracy": item["balanced_accuracy"],
                "Macro-F1": item["macro_f1"],
                "Cohen's κ": item["kappa"],
            }
            for item in experiment.models
        ]
    )


def render_summary(result: dict | None) -> None:
    st.title("Ringkasan")
    if result is None:
        st.info("Jalankan eksperimen pada halaman **Alur Data → Model** untuk melihat hasil.")
        st.markdown(
            "Dashboard ini mengikuti pola navigasi proyek referensi. "
            "Data, label proksi, dan hasil yang muncul tetap berasal dari masukan eksperimen ini."
        )
        return

    experiment = result["experiment"]
    winner = experiment.models[0]
    metrics = st.columns(4)
    metrics[0].metric("Jumlah kelas", len(CLASS_NAMES))
    metrics[1].metric("Sampel training", f"{len(experiment.train_indices):,}")
    metrics[2].metric("Sampel testing", f"{len(experiment.test_indices):,}")
    metrics[3].metric("Model terpilih", winner["model"])
    st.caption(
        f"Macro-F1 holdout spasial: {winner['macro_f1']:.3f}. "
        "Skor menunjukkan kesesuaian terhadap label proksi ESA/OSM, bukan akurasi lapangan."
    )
    st.subheader("Macro-F1 pada holdout spasial")
    chart = model_table(experiment).set_index("Model")[["Macro-F1"]]
    st.bar_chart(chart)
    st.subheader("Perbandingan model")
    st.dataframe(
        model_table(experiment).style.format(
            {
                "Accuracy": "{:.3f}",
                "Balanced accuracy": "{:.3f}",
                "Macro-F1": "{:.3f}",
                "Cohen's κ": "{:.3f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def render_workflow(result: dict | None, input_files: dict) -> None:
    st.title("Alur Data → Model")
    st.markdown(
        """
**Alur kerja:** masukan Sentinel-2 L2A + label WorldCover/OSM → cek CRS dan cakupan
→ samakan grid → hitung fitur → sampling seimbang → holdout blok spasial → bandingkan
model → klasifikasi pratinjau → peta dan tabel evaluasi.

Unggah data melalui panel kiri, pilih batas sampel, lalu jalankan eksperimen di bawah.
"""
    )
    for label, uploaded in input_files.items():
        st.write(f"{'✅' if uploaded else '⬜'} **{label}:** {uploaded.name if uploaded else 'belum diunggah'}")
    if result is not None:
        st.success("Eksperimen sudah tersedia. Pindah ke halaman dashboard tanpa melatih ulang.")
        st.write("Berkas yang digunakan:", ", ".join(result["input_names"]))
        source_width, source_height = result["source_dimensions"]
        preview_width, preview_height = result["preview_dimensions"]
        st.write(
            f"Citra asal: **{source_width:,} × {source_height:,}** piksel; "
            f"pratinjau: **{preview_width:,} × {preview_height:,}** piksel."
        )


def render_map_page(result: dict | None) -> None:
    st.title("Peta Klasifikasi")
    if result is None:
        st.info("Jalankan eksperimen terlebih dahulu pada halaman **Alur Data → Model**.")
        return
    winner = result["experiment"].models[0]["model"]
    left, right = st.columns(2)
    left.subheader("Citra Sentinel-2A RGB (B4/B3/B2)")
    left.image(result["rgb"], use_container_width=True)
    right.subheader(f"Hasil klasifikasi — {winner}")
    right.image(result["overlay"], use_container_width=True)
    st.subheader("Peta interaktif")
    render_map(result)
    st.caption(
        "Basemap Google ditambahkan sebagai XYZ tiles, bukan WMS. "
        "Peta klasifikasi ini merupakan pratinjau dengan resolusi yang diturunkan."
    )


def render_area_page(result: dict | None) -> None:
    st.title("Luas per Kelas")
    if result is None:
        st.info("Jalankan eksperimen terlebih dahulu untuk menghitung keluaran per kelas.")
        return
    class_map = result["class_map"]
    pixel_counts = {
        CLASS_NAMES[class_id]: int(np.count_nonzero(class_map == class_id))
        for class_id in CLASS_NAMES
    }
    area_ha = None
    crs = result["crs"]
    if crs and crs.is_projected:
        _, unit_to_metre = crs.linear_units_factor
        transform = result["transform"]
        pixel_area_m2 = abs(
            transform.a * transform.e - transform.b * transform.d
        ) * unit_to_metre**2
        area_ha = {
            class_name: pixels * pixel_area_m2 / 10_000
            for class_name, pixels in pixel_counts.items()
        }
    rows = []
    for class_name, pixels in pixel_counts.items():
        row = {"Kelas": class_name, "Piksel": pixels}
        if area_ha is not None:
            row["Luas pratinjau (ha)"] = area_ha[class_name]
        rows.append(row)
    area_table = pd.DataFrame(rows)
    st.dataframe(
        area_table.style.format({"Luas pratinjau (ha)": "{:,.2f}"}),
        use_container_width=True,
        hide_index=True,
    )
    if area_ha is None:
        st.warning(
            "Luas hektare tidak dihitung karena CRS raster bukan proyeksi dengan unit linear. "
            "Tabel hanya melaporkan jumlah piksel pratinjau."
        )
    else:
        st.bar_chart(area_table.set_index("Kelas")[["Luas pratinjau (ha)"]])
        st.caption("Estimasi luas berasal dari piksel pratinjau, bukan luas produk resolusi penuh.")


def render_evaluation(result: dict | None) -> None:
    st.title("Evaluasi Model")
    if result is None:
        st.info("Jalankan eksperimen terlebih dahulu untuk melihat evaluasi.")
        return
    experiment = result["experiment"]
    st.subheader("Perbandingan pada holdout blok spasial")
    st.dataframe(
        model_table(experiment).style.format(
            {
                "Accuracy": "{:.3f}",
                "Balanced accuracy": "{:.3f}",
                "Macro-F1": "{:.3f}",
                "Cohen's κ": "{:.3f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
    best = experiment.models[0]
    st.info(
        f"Macro-F1 tertinggi: **{best['model']}** ({best['macro_f1']:.3f}). "
        "Semua angka mengevaluasi kesesuaian dengan label proksi."
    )
    st.subheader("Metrik per kelas")
    report = pd.DataFrame(best["classification_report"]).T
    st.dataframe(report.round(3), use_container_width=True)
    st.subheader("Confusion matrix")
    confusion = pd.DataFrame(
        best["confusion_matrix"],
        index=[f"Aktual: {name}" for name in CLASS_NAMES.values()],
        columns=[f"Prediksi: {name}" for name in CLASS_NAMES.values()],
    )
    st.dataframe(confusion, use_container_width=True)
    st.caption(
        f"Accuracy {best['accuracy']:.3f} · Balanced accuracy {best['balanced_accuracy']:.3f} · "
        f"Macro-F1 {best['macro_f1']:.3f} · Cohen's κ {best['kappa']:.3f}."
    )


def render_downloads(result: dict | None) -> None:
    st.title("Data & Unduhan")
    if result is None:
        st.info("Hasil unduhan tersedia setelah eksperimen selesai.")
        return
    experiment = result["experiment"]
    st.download_button(
        "Unduh GeoTIFF klasifikasi pratinjau",
        data=result["prediction_tif"],
        file_name="klasifikasi_penutup_lahan_jawa_timur_pratinjau.tif",
        mime="image/tiff",
        use_container_width=True,
    )
    counts = pd.DataFrame.from_dict(experiment.class_counts, orient="index")
    counts.index.name = "Kelas"
    st.download_button(
        "Unduh jumlah sampel CSV",
        data=counts.to_csv().encode("utf-8"),
        file_name="jumlah_sampel_train_test.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.download_button(
        "Unduh metrik model CSV",
        data=model_table(experiment).to_csv(index=False).encode("utf-8"),
        file_name="perbandingan_model.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.warning(
        "GeoTIFF adalah peta pratinjau beresolusi lebih rendah dari raster masukan. "
        "Jangan gunakan sebagai peta operasional atau produk resmi."
    )


def render_methodology() -> None:
    st.title("Metodologi")
    st.caption(f"Jumlah fitur model: {len(FEATURE_NAMES)} (10 band reflektansi + 8 indeks)")
    st.markdown(
        """
### Kelas dan label proksi

| Kelas keluaran | Label referensi |
|---|---|
| Sawah* | WorldCover 40 (cropland; tidak eksklusif sawah) |
| Bangunan | WorldCover 50 |
| Mangrove | WorldCover 95 |
| Lahan hijau | Gabungan WorldCover 10/20/30 |
| Perairan terbuka | WorldCover 80 di luar poligon danau |
| Danau/Ranu* | Piksel WorldCover 80 di dalam poligon danau OSM |

### Fitur

Model memakai 10 reflektansi Sentinel-2 **B2, B3, B4, B5, B6, B7, B8, B8A, B11,
B12** dan delapan indeks: NDVI, NDWI, MNDWI, NDMI, NDBI, NDRE, SAVI, BSI.
Rumus lengkap, deskripsi 13 band, sumber data, dan batas interpretasi disajikan
di laporan UTS pada web statis.

### Training, testing, dan batas klaim

Sampel diseimbangkan per kelas hingga batas yang dipilih pengguna. Data uji
dipisahkan berdasarkan blok spasial, bukan pembagian piksel acak. Empat model
dibandingkan pada split yang sama; model dengan Macro-F1 tertinggi dipakai untuk
pratinjau klasifikasi. ESA/OSM adalah label proksi, sehingga skor bukan akurasi
lapangan. Cropland tidak sama dengan sawah, dan kualitas poligon OSM bervariasi.

Struktur dashboard mengikuti pola proyek referensi; data masukan, metode label,
dan hasil eksperimen di halaman ini tetap berasal dari proyek ini. Angka,
confusion matrix, atau luas dari repository referensi tidak digunakan.
"""
    )
    st.caption(
        "Acuan terminologi nasional: SNI 7645-1:2014; verifikasi status katalog BSN "
        "dan metadata peta resmi sebelum dipakai untuk keputusan tata ruang."
    )


st.title("Klasifikasi Penutup Lahan Jawa Timur")
st.caption(
    "Dashboard 6 kelas berbasis Sentinel-2A, label proksi ESA WorldCover/OSM, "
    "dan validasi blok spasial."
)
st.warning(
    "Sawah* memakai proksi WorldCover cropland, bukan label sawah terverifikasi. "
    "Danau/Ranu* dibentuk dari poligon OSM di area air WorldCover. Skor bukan akurasi lapangan."
)

with st.sidebar:
    st.header("Data masukan")
    sentinel_upload = st.file_uploader(
        "Sentinel-2A GeoTIFF (10 band)",
        type=("tif", "tiff"),
        key="s2",
        help="Urutan: B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12; satu grid/CRS.",
    )
    worldcover_upload = st.file_uploader(
        "ESA WorldCover GeoTIFF", type=("tif", "tiff"), key="worldcover"
    )
    aoi_upload = st.file_uploader(
        "Batas Provinsi Jawa Timur (GeoJSON)", type=("geojson", "json"), key="aoi"
    )
    lake_upload = st.file_uploader(
        "Poligon danau/ranu OSM (GeoJSON)", type=("geojson", "json"), key="lakes"
    )
    samples_per_class = st.slider(
        "Maksimum sampel per kelas", 100, 1200, 600, 100
    )
    random_seed = st.number_input("Random seed", 0, 99999, 42)
    page = st.radio("Halaman dashboard", PAGES)

result = st.session_state.get(RESULT_KEY)
if page == "Alur Data → Model":
    render_workflow(
        result,
        {
            "Sentinel-2A": sentinel_upload,
            "ESA WorldCover": worldcover_upload,
            "Batas provinsi": aoi_upload,
            "Poligon danau/ranu": lake_upload,
        },
    )
    run_experiment = st.button(
        "Jalankan eksperimen", type="primary", use_container_width=True
    )
    if run_experiment:
        required = {
            "GeoTIFF Sentinel-2A": sentinel_upload,
            "GeoTIFF ESA WorldCover": worldcover_upload,
            "GeoJSON batas provinsi": aoi_upload,
            "GeoJSON danau/ranu": lake_upload,
        }
        missing = [label for label, uploaded in required.items() if uploaded is None]
        if missing:
            st.error("Lengkapi data berikut sebelum eksperimen: " + ", ".join(missing))
        else:
            try:
                with st.spinner("Menyelaraskan data, melatih model, dan membuat peta..."):
                    result = execute_experiment(
                        sentinel_upload,
                        worldcover_upload,
                        aoi_upload,
                        lake_upload,
                        samples_per_class,
                        int(random_seed),
                    )
                st.session_state[RESULT_KEY] = result
                st.success("Eksperimen selesai; hasil tersimpan selama sesi dashboard ini.")
                st.rerun()
            except (
                ValueError,
                TypeError,
                KeyError,
                json.JSONDecodeError,
                UnicodeDecodeError,
                rasterio.errors.RasterioError,
                OSError,
            ) as error:
                st.error(f"Eksperimen tidak dapat dijalankan: {error}")
elif page == "Ringkasan":
    render_summary(result)
elif page == "Peta Klasifikasi":
    render_map_page(result)
elif page == "Luas per Kelas":
    render_area_page(result)
elif page == "Evaluasi Model":
    render_evaluation(result)
elif page == "Data & Unduhan":
    render_downloads(result)
elif page == "Metodologi":
    render_methodology()

st.divider()
st.caption(
    "Acuan label: ESA WorldCover 2021 v200 (CC BY 4.0). Google Satellite adalah "
    "XYZ tiles, bukan WMS. Hasil bukan peta resmi penutup lahan Indonesia."
)
