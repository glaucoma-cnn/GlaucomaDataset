from pathlib import Path

import numpy as np
import pandas as pd

from readers.Readers import PillowImageReader
from config.Settings import GLAUCOMA_DISCREPANCY_THRESHOLD_PCT


reader = PillowImageReader()


def count_pixels(path: Path) -> int:
    """Conta pixels não-pretos (qualquer canal > 0) em uma imagem."""
    array = reader.read(path)

    if array.ndim == 3:
        mask = (array[:, :, 0] > 0) | (array[:, :, 1] > 0) | (array[:, :, 2] > 0)
    else:
        mask = array > 0

    return int(np.sum(mask))


class OpticPairAnalyzer:

    def analyze(self, pairs: dict[str, dict[str, Path]]) -> pd.DataFrame:
        rows = []

        for image_id, paths in pairs.items():
            ap = count_pixels(paths["optic_disc"])
            vp = count_pixels(paths["optic_cup"])

            abs_diff    = abs(vp - ap)
            disc_pct    = abs_diff / max(vp, ap) * 100
            glaucoma_flag = disc_pct > GLAUCOMA_DISCREPANCY_THRESHOLD_PCT if GLAUCOMA_DISCREPANCY_THRESHOLD_PCT else False

            rows.append({
                "image_id":            image_id,
                "optic_disk_pixels":       ap,
                "optic_cup_pixels":         vp,
                "ratio_optic_cup_optic_disk":   vp / ap,
                "absolute_difference": abs_diff,
                "discrepancy_pct":     disc_pct,
                "predominance":        "OpticCup" if vp > ap else "OpticDisk",
                "glaucoma_flag":       glaucoma_flag,
            })

        return pd.DataFrame(rows)