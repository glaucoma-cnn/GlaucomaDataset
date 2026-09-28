import math
from pathlib import Path

import numpy as np
import pandas as pd
from skimage.measure import label, regionprops

from readers.Readers import PillowImageReader, ImageReadError
from config.Settings import GLAUCOMA_AREA_CDR_THRESHOLD


reader = PillowImageReader()


def _read_mask(path: Path) -> np.ndarray:
    array = reader.read(path)

    if array.ndim == 3:
        mask = (array[:, :, 0] > 0) | (array[:, :, 1] > 0) | (array[:, :, 2] > 0)
    else:
        mask = array > 0

    return mask


def count_pixels(mask: np.ndarray) -> int:
    return int(np.sum(mask))


def extract_morphological_features(mask: np.ndarray, prefix: str) -> dict:
    regions = regionprops(label(mask))

    if not regions:
        return {
            f"{prefix}_perimeter": 0.0,
            f"{prefix}_eccentricity": 0.0,
            f"{prefix}_aspect_ratio": 0.0,
            f"{prefix}_circularity": 0.0,
        }

    region = max(regions, key=lambda r: r.area)

    perimeter = region.perimeter
    circularity = (4 * math.pi * region.area / perimeter**2) if perimeter > 0 else 0.0
    aspect_ratio = (
        region.axis_major_length / region.axis_minor_length
        if region.axis_minor_length > 0
        else 0.0
    )

    return {
        f"{prefix}_perimeter": perimeter,
        f"{prefix}_eccentricity": region.eccentricity,
        f"{prefix}_aspect_ratio": aspect_ratio,
        f"{prefix}_circularity": circularity,
    }


class OpticPairAnalyzer:

    def analyze(self, pairs: dict[str, dict[str, Path]]) -> pd.DataFrame:
        rows = []
        skipped: list[str] = []

        for image_id, paths in pairs.items():
            try:
                disc_mask = _read_mask(paths["optic_disc"])
                cup_mask = _read_mask(paths["optic_cup"])
            except ImageReadError as e:
                print(f"  ⚠ Ignorando '{image_id}': {e}")
                skipped.append(image_id)
                continue

            disc_area = count_pixels(disc_mask)
            cup_area = count_pixels(cup_mask)

            # Uma máscara de disco vazia torna impossível calcular a Area CDR.
            if disc_area == 0:
                print(f"  ⚠ Ignorando '{image_id}': máscara de disco óptico vazia.")
                skipped.append(image_id)
                continue

            # Area-based Cup-to-Disc Ratio:
            # proporção da área do disco ocupada pelo copo.
            area_cdr = cup_area / disc_area

            # Medidas exploratórias auxiliares.
            absolute_difference = abs(cup_area - disc_area)
            discrepancy_pct = absolute_difference / max(cup_area, disc_area) * 100

            # Triagem preliminar baseada exclusivamente na Area CDR.
            # Não representa diagnóstico clínico.
            area_cdr_flag = (
                area_cdr > GLAUCOMA_AREA_CDR_THRESHOLD
                if GLAUCOMA_AREA_CDR_THRESHOLD is not None
                else False
            )

            # Em condições normais, espera-se que o copo esteja contido
            # no disco e, portanto, sua área não seja maior.
            anatomical_consistency = cup_area <= disc_area

            row = {
                "image_id": image_id,
                "disc_pixels": disc_area,
                "cup_pixels": cup_area,
                "area_cdr": area_cdr,
                "absolute_difference": absolute_difference,
                "discrepancy_pct": discrepancy_pct,
                "anatomical_consistency": anatomical_consistency,
                "area_cdr_flag": area_cdr_flag,
            }
            row.update(extract_morphological_features(disc_mask, "disc"))
            row.update(extract_morphological_features(cup_mask, "cup"))

            rows.append(row)

        if skipped:
            print(f"  {len(skipped)} imagem(ns) ignorada(s) por erro de leitura.")

        return pd.DataFrame(rows)