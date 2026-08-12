import os
from pathlib import Path

import numpy as np
from PIL import Image

from config.Settings import SUPPORTED_EXTENSIONS


class PillowImageReader:
    
    def read(self, path: Path) -> np.ndarray:
        return np.array(Image.open(path))


class GlaucomaBenchmarkReader:

    def __init__(self, optic_disk_folder: Path, optic_cup_folder: Path) -> None:
        self._optic_disk_folder = Path(optic_disk_folder)
        self._optic_cup_folder = Path(optic_cup_folder)

    def load_pairs(self) -> dict[str, dict[str, Path]]:
        pairs = {}

        disc_images = {p.name: p for p in self._iter_images(self._optic_disk_folder)}
        cup_images = {p.name: p for p in self._iter_images(self._optic_cup_folder)}

        for name in disc_images:
            if name in cup_images:
                image_id = Path(name).stem
                pairs[image_id] = {
                    "optic_disc": disc_images[name],
                    "optic_cup": cup_images[name],
                }

        return pairs

    @staticmethod
    def _iter_images(folder: Path):
        for entry in os.scandir(folder):
            if Path(entry.path).suffix.lower() in SUPPORTED_EXTENSIONS:
                yield Path(entry.path)