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
    CLASS_NAMES,
    FEATURE_NAMES,
    assign_lake_reference,
    build_experiment,
    calculate_features,
    classify_preview,
    classification_rgb,
    geographic_bounds,
    rasterize_aoi,
    read_preview_stack,
    read_reference_labels,
)


st.set_page_config(
    page_title="SIG Jawa Timur | Klasifikasi Penutup Lahan",
    page_icon="🛰️",
    layout="wide",
)

st.title("Klasifikasi Penutup Lahan Jawa Timur")
st.caption(
    "Eksperimen multikelas Sentinel-2A dengan label referensi ESA WorldCover 2021, "
    "validasi spasial, dan peta Folium."
)

st.warning(
    "Sawah* memakai proksi ESA WorldCover kelas cropland (40), bukan label sawah "
    "yang diverifikasi satu per satu. Danau/Ranu* ditentukan dari tumpang-susun "
    "poligon danau OSM dengan piksel air WorldCover (80). Skor di bawah mengukur "
    "kesesuaian terhadap proksi, bukan akurasi lapangan independen."
)


def read_geojson(uploaded_file) -> tuple[list[dict], list[dict]]:
    try:
        document = json.loads(uploaded_file.getvalue())
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError(f"{uploaded_file.name} bukan GeoJSON yang valid.") from error
    features = document.get("features", [])
    geometries = []
    for feature in features:
        geometry = feature.get("geometry")
        if geometry:
            geometries.append(shape(geometry))
    if not geometries:
        raise ValueError(f"Tidak ada geometri yang dapat dibaca di {uploaded_file.name}.")
    source_crs = (document.get("crs") or {}).get("properties", {}).get("name", "EPSG:4326")
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
        low, high = np.percentile(valid, [2, 98])
        image.append(np.clip((band - low) / max(high - low, 1e-6), 0, 1))
    return np.dstack(image)


@st.cache_data(show_spinner=False)
def make_rgb_png(rgba: np.ndarray) -> bytes:
    output = BytesIO()
    plt.imsave(output, rgba)
    return output.getvalue()


with st.sidebar:
    st.header("Data masukan")
    sentinel_upload = st.file_uploader(
        "Citra Sentinel-2A harmonisasi GeoTIFF (10 band)",
        type=("tif", "tiff"),
        key="s2",
        help=(
            "Urutan band wajib: B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12. "
            "Band harus sudah disejajarkan ke satu grid dan CRS."
        ),
    )
    worldcover_upload = st.file_uploader(
        "ESA WorldCover 2021 v200 GeoTIFF",
        type=("tif", "tiff"),
        key="worldcover",
    )
    aoi_upload = st.file_uploader(
        "Batas Provinsi Jawa Timur (GeoJSON)",
        type=("geojson", "json"),
        key="aoi",
    )
    lake_upload = st.file_uploader(
        "Poligon danau/ranu dari OpenStreetMap (GeoJSON)",
        type=("geojson", "json"),
        key="lakes",
    )
    samples_per_class = st.slider(
        "Maksimum piksel sampel per kelas", min_value=100, max_value=1200, value=600, step=100
    )
    random_seed = st.number_input("Random seed", min_value=0, max_value=99999, value=42)
    run_experiment = st.button(
        "Jalankan eksperimen", type="primary", use_container_width=True
    )

with st.expander("Panduan data dan kode kelas acuan", expanded=not all(
    (sentinel_upload, worldcover_upload, aoi_upload, lake_upload)
)):
    st.markdown(
        """
1. Ekspor satu GeoTIFF Sentinel-2 L2A yang mencakup AOI dan memiliki minimal 10 band pada satu grid.
   Nilai boleh berupa reflektansi 0–1 atau DN 0–10000; band 20 m perlu di-*resample* ke grid bersama.
2. Unduh ESA WorldCover 2021 v200, kelas 10 m, lalu unggah tile/mosaik yang mencakup AOI.
3. Unggah batas administrasi Jawa Timur dalam GeoJSON dan poligon `natural=water` danau/ranu
   dari OpenStreetMap dalam GeoJSON. CRS poligon harus dicantumkan atau EPSG:4326.
4. Proksi kelas otomatis: ESA 40 → Sawah* (sebenarnya seluruh lahan budidaya); 50 → Bangunan;
   95 → Mangrove; 10/20/30 → Lahan hijau; 80 → air. Piksel air yang tumpang-susun dengan
   poligon danau OSM menjadi Danau/Ranu*; sisa piksel 80 menjadi Perairan terbuka.
5. Sistem mengambil sampel berimbang, membagi data dengan blok spasial, membandingkan
   Random Forest, Extra Trees, HistGradientBoosting, dan SVM RBF, lalu memilih Macro-F1 tertinggi.

**Penting:** gunakan wilayah dan waktu citra yang konsisten. Label WorldCover 2021 dan citra
Sentinel-2 dengan tahun berbeda dapat menimbulkan ketidakcocokan perubahan lahan.
"""
    )

if run_experiment:
    required = {
        "GeoTIFF Sentinel-2A": sentinel_upload,
        "GeoTIFF ESA WorldCover": worldcover_upload,
        "GeoJSON batas provinsi": aoi_upload,
        "GeoJSON danau/ranu": lake_upload,
    }
    missing = [name for name, file in required.items() if file is None]
    if missing:
        st.error("Lengkapi data berikut sebelum menjalankan eksperimen: " + ", ".join(missing))
    else:
        try:
            with st.spinner("Membaca citra, membentuk sampel spasial, dan melatih model..."):
                aoi_geometries, aoi_crs = read_geojson(aoi_upload)
                lake_geometries, lake_crs = read_geojson(lake_upload)
                aoi_json = json.loads(aoi_upload.getvalue())
                lake_json = json.loads(lake_upload.getvalue())
                aoi_crs = aoi_json.get("crs", {}).get("properties", {}).get("name", aoi_crs)
                lake_crs = lake_json.get("crs", {}).get("properties", {}).get("name", lake_crs)

                with MemoryFile(sentinel_upload.getvalue()) as sentinel_memory, \
                        MemoryFile(worldcover_upload.getvalue()) as worldcover_memory:
                    with sentinel_memory.open() as sentinel, worldcover_memory.open() as worldcover:
                        if sentinel.count < 10:
                            raise ValueError(
                                f"Citra Sentinel-2 memiliki {sentinel.count} band; dibutuhkan 10."
                            )
                        bands, preview_transform = read_preview_stack(sentinel)
                        target_crs = sentinel.crs
                        if target_crs is None or worldcover.crs is None:
                            raise ValueError("Kedua GeoTIFF harus memiliki metadata CRS.")

                        projected_aoi = project_geometries(aoi_geometries, aoi_crs, target_crs)
                        projected_lakes = project_geometries(lake_geometries, lake_crs, target_crs)
                        labels = read_reference_labels(
                            worldcover, bands.shape[1:], preview_transform, target_crs
                        )
                        labels = assign_lake_reference(
                            labels, projected_lakes, preview_transform
                        )
                        aoi_mask = rasterize_aoi(
                            projected_aoi, bands.shape[1:], preview_transform
                        )
                        features = calculate_features(bands)
                        experiment = build_experiment(
                            features,
                            labels,
                            aoi_mask,
                            seed=int(random_seed),
                            max_samples_per_class=samples_per_class,
                        )
                        selected = experiment.selected
                        class_map = classify_preview(selected, bands, aoi_mask)
                        bounds = geographic_bounds(sentinel)
                        center_lat = (bounds[0][0] + bounds[1][0]) / 2
                        center_lon = (bounds[0][1] + bounds[1][1]) / 2
                        rgb = preview_band_rgb(bands)
                        mask = ~aoi_mask
                        rgb[mask] = 0.0
                        classification_overlay = classification_rgb(class_map)
                        classification_overlay[~aoi_mask, 3] = 0
                        profile = {
                            "driver": "GTiff",
                            "height": class_map.shape[0],
                            "width": class_map.shape[1],
                            "count": 1,
                            "dtype": "uint8",
                            "crs": target_crs,
                            "transform": preview_transform,
                            "nodata": 0,
                            "compress": "deflate",
                        }
                        with MemoryFile() as result_memory:
                            with result_memory.open(**profile) as result_dataset:
                                result_dataset.write(class_map, 1)
                            prediction_tif = result_memory.read()

            st.success("Eksperimen selesai. Peta adalah pratinjau pada resolusi yang diturunkan.")
            st.caption(
                f"Ukuran citra: {sentinel.width:,} × {sentinel.height:,} piksel; "
                f"ukuran peta klasifikasi: {bands.shape[2]:,} × {bands.shape[1]:,} piksel. "
                f"Jumlah fitur: {len(FEATURE_NAMES)}."
            )
            st.download_button(
                "Unduh GeoTIFF pratinjau klasifikasi",
                data=prediction_tif,
                file_name="klasifikasi_penutup_lahan_jawa_timur_pratinjau.tif",
                mime="image/tiff",
            )

            class_columns = st.columns(6)
            for column, class_id in zip(class_columns, CLASS_NAMES):
                values = experiment.class_counts[CLASS_NAMES[class_id]]
                column.metric(
                    CLASS_NAMES[class_id],
                    f"{values['total']:,}",
                    f"latih {values['training']:,} · uji {values['testing']:,}",
                )

            st.subheader("Perbandingan model — data uji spasial")
            comparison = pd.DataFrame(
                [
                    {
                        "Model": result["model"],
                        "Accuracy": result["accuracy"],
                        "Balanced accuracy": result["balanced_accuracy"],
                        "Macro-F1": result["macro_f1"],
                        "Kappa": result["kappa"],
                    }
                    for result in experiment.models
                ]
            )
            st.dataframe(
                comparison.style.format(
                    {
                        "Accuracy": "{:.3f}",
                        "Balanced accuracy": "{:.3f}",
                        "Macro-F1": "{:.3f}",
                        "Kappa": "{:.3f}",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
            best_result = experiment.models[0]
            st.info(
                f"Model dengan Macro-F1 tertinggi pada holdout spasial: **{best_result['model']}**. "
                "Nilai ini berlaku untuk label proksi yang digunakan."
            )

            left, right = st.columns(2)
            left.subheader("Sentinel-2A RGB (B4/B3/B2)")
            left.image(rgb, use_container_width=True)
            right.subheader(f"Peta prediksi — {best_result['model']}")
            right.image(classification_overlay, use_container_width=True)

            st.subheader("Peta interaktif di atas citra satelit")
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
                image=make_rgb_png(classification_overlay),
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
                'box-shadow:0 1px 5px #666">'
                '<b>Prediksi penutup lahan</b><br>'
            )
            for class_id, class_name in CLASS_NAMES.items():
                color = {
                    1: "#f1c40f",
                    2: "#e74c3c",
                    3: "#16a085",
                    4: "#27ae60",
                    5: "#3498db",
                    6: "#2c3e50",
                }[class_id]
                legend += (
                    f'<span style="color:{color}">■</span> {class_name} '
                    f'({int((class_map == class_id).sum()):,} piksel)<br>'
                )
            legend += "</div>"
            map_view.get_root().html.add_child(folium.Element(legend))
            folium.LayerControl(collapsed=False).add_to(map_view)
            st.components.v1.html(map_view.get_root().render(), height=650, scrolling=False)

            st.subheader("Metrik per kelas pada data uji")
            report = pd.DataFrame(best_result["classification_report"]).T
            st.dataframe(report.round(3), use_container_width=True)
            confusion = pd.DataFrame(
                best_result["confusion_matrix"],
                index=[f"Aktual: {name}" for name in CLASS_NAMES.values()],
                columns=[f"Prediksi: {name}" for name in CLASS_NAMES.values()],
            )
            st.subheader("Confusion matrix")
            st.dataframe(confusion, use_container_width=True)
            st.caption(
                f"Accuracy {best_result['accuracy']:.3f} · "
                f"Balanced accuracy {best_result['balanced_accuracy']:.3f} · "
                f"Macro-F1 {best_result['macro_f1']:.3f} · "
                f"Cohen's κ {best_result['kappa']:.3f}."
            )
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

st.divider()
st.caption(
    "Acuan label: ESA WorldCover 2021 v200 (CC BY 4.0). Basemap satelit Google adalah "
    "XYZ tiles, bukan WMS; label kelas dan hasil model bukan peta resmi penutup lahan Indonesia."
)
