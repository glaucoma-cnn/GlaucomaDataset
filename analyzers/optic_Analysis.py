from pathlib import Path

import numpy as np
import pandas as pd

from readers.Readers import PillowImageReader
from config.Settings import GLAUCOMA_AREA_CDR_THRESHOLD


reader = PillowImageReader()


def count_pixels(path: Path) -> int:
    """Conta pixels não-pretos (qualquer canal > 0) em uma imagem."""
    array = reader.read(path)

    if array.ndim == 3:
        mask = (
            (array[:, :, 0] > 0)
            | (array[:, :, 1] > 0)
            | (array[:, :, 2] > 0)
        )
    else:
        mask = array > 0

    return int(np.sum(mask))


class OpticPairAnalyzer:

    def analyze(self, pairs: dict[str, dict[str, Path]]) -> pd.DataFrame:
        rows = []

        for image_id, paths in pairs.items():
            disc_area = count_pixels(paths["optic_disc"])
            cup_area = count_pixels(paths["optic_cup"])

            # Uma máscara de disco vazia torna impossível calcular a Area CDR.
            if disc_area == 0:
                raise ValueError(
                    f"Máscara de disco óptico vazia para a imagem '{image_id}'."
                )

            # Area-based Cup-to-Disc Ratio:
            # proporção da área do disco ocupada pelo copo.
            area_cdr = cup_area / disc_area

            # Medidas exploratórias auxiliares.
            absolute_difference = abs(cup_area - disc_area)
            discrepancy_pct = (
                absolute_difference / max(cup_area, disc_area) * 100
            )

            # Triagem preliminar baseada exclusivamente na Area CDR.
            # Não representa diagnóstico clínico.
            glaucoma_flag = (
                area_cdr > GLAUCOMA_AREA_CDR_THRESHOLD
                if GLAUCOMA_AREA_CDR_THRESHOLD is not None
                else False
            )

            # Em condições normais, espera-se que o copo esteja contido
            # no disco e, portanto, sua área não seja maior.
            anatomical_consistency = cup_area <= disc_area

            rows.append({
                "image_id": image_id,
                "disc_pixels": disc_area,
                "cup_pixels": cup_area,
                "area_cdr": area_cdr,
                "absolute_difference": absolute_difference,
                "discrepancy_pct": discrepancy_pct,
                "anatomical_consistency": anatomical_consistency,
                "glaucoma_flag": glaucoma_flag,
            })

        return pd.DataFrame(rows)