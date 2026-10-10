from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.features import rasterize
from rasterio.transform import Affine
from rasterio.warp import reproject, transform_bounds
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


CLASS_NAMES = {
    1: "Sawah*",
    2: "Bangunan",
    3: "Mangrove",
    4: "Lahan hijau",
    5: "Perairan terbuka",
    6: "Danau/Ranu*",
}
CLASS_COLORS = {
    1: "#f1c40f",
    2: "#e74c3c",
    3: "#16a085",
    4: "#27ae60",
    5: "#3498db",
    6: "#2c3e50",
}
FEATURE_NAMES = [
    "B2_blue",
    "B3_green",
    "B4_red",
    "B5_rededge1",
    "B6_rededge2",
    "B7_rededge3",
    "B8_nir",
    "B8A_rededge4",
    "B11_swir1",
    "B12_swir2",
    "NDVI",
    "NDWI",
    "MNDWI",
    "NDMI",
    "NDBI",
    "NDRE",
    "SAVI",
    "BSI",
]
SAMPLE_CAP_PER_CLASS = 1200
PREVIEW_MAX_DIMENSION = 1200


@dataclass
class Experiment:
    models: list[dict]
    selected: object
    x: np.ndarray
    y: np.ndarray
    groups: np.ndarray
    train_indices: np.ndarray
    test_indices: np.ndarray
    class_counts: dict[str, dict[str, int]]


def safe_normalized_difference(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    denominator = a + b
    return np.divide(
        a - b,
        denominator,
        out=np.zeros_like(a, dtype=np.float32),
        where=np.abs(denominator) > 1e-6,
    )


def calculate_features(bands: np.ndarray) -> np.ndarray:
    """Return the ten harmonized S2 reflectance bands and eight indices."""
    if bands.ndim != 3 or bands.shape[0] < 10:
        raise ValueError(
            "Citra harus memiliki minimal 10 band berurutan: "
            "B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12."
        )
    values = bands[:10].astype(np.float32, copy=False)
    if np.nanpercentile(values, 99) > 2:
        values = values / 10000.0

    b2, b3, b4, b5, b6, b7, b8, b8a, b11, b12 = values
    ndvi = safe_normalized_difference(b8, b4)
    ndwi = safe_normalized_difference(b3, b8)
    mndwi = safe_normalized_difference(b3, b11)
    ndmi = safe_normalized_difference(b8, b11)
    ndbi = safe_normalized_difference(b11, b8)
    ndre = safe_normalized_difference(b8a, b5)
    savi = np.divide(
        1.5 * (b8 - b4),
        b8 + b4 + 0.5,
        out=np.zeros_like(b8, dtype=np.float32),
        where=np.abs(b8 + b4 + 0.5) > 1e-6,
    )
    bsi = safe_normalized_difference(b11 + b4, b8 + b2)
    return np.stack(
        [
            b2, b3, b4, b5, b6, b7, b8, b8a, b11, b12,
            ndvi, ndwi, mndwi, ndmi, ndbi, ndre, savi, bsi,
        ]
    ).astype(np.float32, copy=False)


def scale_for_preview(
    width: int, height: int, max_dimension: int = PREVIEW_MAX_DIMENSION
) -> tuple[int, int]:
    scale = min(1.0, max_dimension / max(width, height))
    return max(1, round(width * scale)), max(1, round(height * scale))


def read_preview_stack(dataset: rasterio.io.DatasetReader) -> tuple[np.ndarray, Affine]:
    width, height = scale_for_preview(dataset.width, dataset.height)
    stack = dataset.read(
        indexes=list(range(1, 11)),
        out_shape=(10, height, width),
        resampling=Resampling.bilinear,
        masked=True,
    ).astype(np.float32).filled(np.nan)
    scale = Affine.scale(dataset.width / width, dataset.height / height)
    return stack, dataset.transform * scale


def read_reference_labels(
    worldcover: rasterio.io.DatasetReader,
    shape: tuple[int, int],
    transform: Affine,
    crs: rasterio.crs.CRS,
) -> np.ndarray:
    result = np.zeros(shape, dtype=np.uint8)
    reproject(
        source=rasterio.band(worldcover, 1),
        destination=result,
        src_transform=worldcover.transform,
        src_crs=worldcover.crs,
        src_nodata=worldcover.nodata or 0,
        dst_transform=transform,
        dst_crs=crs,
        dst_nodata=0,
        resampling=Resampling.nearest,
    )
    labels = np.zeros_like(result)
    labels[result == 40] = 1
    labels[result == 50] = 2
    labels[result == 95] = 3
    labels[np.isin(result, (10, 20, 30))] = 4
    labels[result == 80] = 5
    return labels


def rasterize_aoi(
    geometries: list[dict], shape: tuple[int, int], transform: Affine
) -> np.ndarray:
    if not geometries:
        return np.ones(shape, dtype=bool)
    return rasterize(
        ((geometry, 1) for geometry in geometries),
        out_shape=shape,
        transform=transform,
        fill=0,
        dtype="uint8",
        all_touched=True,
    ).astype(bool)


def assign_lake_reference(
    labels: np.ndarray,
    lake_geometries: list[dict],
    transform: Affine,
) -> np.ndarray:
    if not lake_geometries:
        raise ValueError(
            "Unggah GeoJSON poligon danau/ranu dari OpenStreetMap. "
            "WorldCover hanya menyediakan kelas air permanen dan tidak "
            "membedakan laut dengan danau."
        )
    lakes = rasterize(
        ((geometry, 1) for geometry in lake_geometries),
        out_shape=labels.shape,
        transform=transform,
        fill=0,
        dtype="uint8",
        all_touched=True,
    ).astype(bool)
    result = labels.copy()
    result[(labels == 5) & lakes] = 6
    return result


def build_experiment(
    feature_stack: np.ndarray,
    labels: np.ndarray,
    aoi_mask: np.ndarray,
    seed: int = 42,
    max_samples_per_class: int = SAMPLE_CAP_PER_CLASS,
) -> Experiment:
    valid = aoi_mask & (labels > 0) & np.isfinite(feature_stack).all(axis=0)
    rng = np.random.default_rng(seed)
    samples_x: list[np.ndarray] = []
    samples_y: list[np.ndarray] = []
    samples_groups: list[np.ndarray] = []

    for class_id in CLASS_NAMES:
        positions = np.flatnonzero(valid & (labels == class_id))
        if not positions.size:
            raise ValueError(
                f"Tidak ada piksel referensi untuk kelas {CLASS_NAMES[class_id]}. "
                "Periksa cakupan AOI, raster WorldCover, dan poligon danau."
            )
        rows, cols = np.divmod(positions, labels.shape[1])
        groups = (rows // 100) * int(np.ceil(labels.shape[1] / 100)) + cols // 100
        unique_groups = np.unique(groups)
        if unique_groups.size < 2:
            raise ValueError(
                f"Kelas {CLASS_NAMES[class_id]} hanya ditemukan pada "
                f"{unique_groups.size} blok spasial. Dibutuhkan minimal 2."
            )
        sample_count = min(max_samples_per_class, positions.size)
        sampled_groups = rng.choice(
            unique_groups, size=min(unique_groups.size, sample_count), replace=False
        )
        per_group = max(1, sample_count // sampled_groups.size)
        selected: list[np.ndarray] = []
        for group in sampled_groups:
            group_positions = positions[groups == group]
            rng.shuffle(group_positions)
            selected.append(group_positions[:per_group])
        indexes = np.concatenate(selected)
        if indexes.size < sample_count:
            remaining = positions[~np.isin(positions, indexes)]
            rng.shuffle(remaining)
            indexes = np.concatenate((indexes, remaining[:sample_count - indexes.size]))
        if indexes.size > sample_count:
            rng.shuffle(indexes)
            indexes = indexes[:sample_count]
        samples_x.append(feature_stack.reshape(feature_stack.shape[0], -1)[:, indexes].T)
        samples_y.append(np.full(indexes.size, class_id, dtype=np.uint8))
        rows, cols = np.divmod(indexes, labels.shape[1])
        groups = (rows // 100) * int(np.ceil(labels.shape[1] / 100)) + cols // 100
        samples_groups.append(groups)

    x = np.concatenate(samples_x)
    y = np.concatenate(samples_y)
    spatial_groups = np.concatenate(samples_groups)
    splitter = GroupShuffleSplit(n_splits=100, test_size=0.35, random_state=seed)
    expected_classes = np.asarray(list(CLASS_NAMES), dtype=np.uint8)
    split = next(
        (
            (train, test)
            for train, test in splitter.split(x, y, spatial_groups)
            if np.array_equal(np.unique(y[train]), expected_classes)
            and np.array_equal(np.unique(y[test]), expected_classes)
        ),
        None,
    )
    if split is None:
        raise ValueError(
            "Pembagian blok spasial tidak dapat menempatkan seluruh enam kelas "
            "di data latih dan uji. Tambahkan sampel yang tersebar pada lebih "
            "banyak blok atau periksa poligon danau."
        )
    train_indices, test_indices = split

    estimators = {
        "Random Forest": RandomForestClassifier(
            n_estimators=250, class_weight="balanced", n_jobs=-1, random_state=seed
        ),
        "Extra Trees": ExtraTreesClassifier(
            n_estimators=250, class_weight="balanced", n_jobs=-1, random_state=seed
        ),
        "HistGradientBoosting": HistGradientBoostingClassifier(
            max_iter=150, l2_regularization=1.0, random_state=seed
        ),
        "SVM RBF": make_pipeline(
            StandardScaler(),
            SVC(C=2.0, kernel="rbf", class_weight="balanced"),
        ),
    }
    trained: list[dict] = []
    for name, estimator in estimators.items():
        estimator.fit(x[train_indices], y[train_indices])
        predicted = estimator.predict(x[test_indices])
        trained.append(
            {
                "model": name,
                "estimator": estimator,
                "accuracy": accuracy_score(y[test_indices], predicted),
                "balanced_accuracy": balanced_accuracy_score(
                    y[test_indices], predicted
                ),
                "macro_f1": f1_score(
                    y[test_indices],
                    predicted,
                    labels=list(CLASS_NAMES),
                    average="macro",
                    zero_division=0,
                ),
                "kappa": cohen_kappa_score(y[test_indices], predicted),
                "confusion_matrix": confusion_matrix(
                    y[test_indices], predicted, labels=list(CLASS_NAMES)
                ),
                "classification_report": classification_report(
                    y[test_indices],
                    predicted,
                    labels=list(CLASS_NAMES),
                    target_names=list(CLASS_NAMES.values()),
                    zero_division=0,
                    output_dict=True,
                ),
            }
        )
    trained.sort(key=lambda result: (result["macro_f1"], result["balanced_accuracy"]), reverse=True)
    counts = {
        CLASS_NAMES[class_id]: {
            "total": int(np.count_nonzero(y == class_id)),
            "training": int(np.count_nonzero(y[train_indices] == class_id)),
            "testing": int(np.count_nonzero(y[test_indices] == class_id)),
        }
        for class_id in CLASS_NAMES
    }
    return Experiment(
        models=trained,
        selected=trained[0]["estimator"],
        x=x,
        y=y,
        groups=spatial_groups,
        train_indices=train_indices,
        test_indices=test_indices,
        class_counts=counts,
    )


def classify_preview(
    estimator: object,
    bands: np.ndarray,
    aoi_mask: np.ndarray,
    batch_size: int = 50_000,
    progress: Callable[[float], None] | None = None,
) -> np.ndarray:
    features = calculate_features(bands)
    valid = aoi_mask & np.isfinite(features).all(axis=0)
    rows, cols = np.where(valid)
    classes = np.zeros(aoi_mask.shape, dtype=np.uint8)
    flattened = features.reshape(features.shape[0], -1)
    flat_classes = classes.ravel()
    flat_indexes = np.ravel_multi_index((rows, cols), aoi_mask.shape)
    for start in range(0, flat_indexes.size, batch_size):
        current = flat_indexes[start : start + batch_size]
        flat_classes[current] = estimator.predict(flattened[:, current].T)
        if progress is not None:
            progress(min(1.0, (start + current.size) / max(1, flat_indexes.size)))
    return classes


def geographic_bounds(dataset: rasterio.io.DatasetReader) -> list[list[float]]:
    west, south, east, north = transform_bounds(
        dataset.crs, "EPSG:4326", *dataset.bounds, densify_pts=21
    )
    return [[south, west], [north, east]]


def classification_rgb(classes: np.ndarray) -> np.ndarray:
    from matplotlib.colors import to_rgb

    image = np.zeros((*classes.shape, 4), dtype=np.uint8)
    for class_id, color in CLASS_COLORS.items():
        rgba = np.array([*to_rgb(color), 0.68])
        image[classes == class_id] = (rgba * 255).astype(np.uint8)
    return image
