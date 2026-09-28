import os
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError

from config.Settings import SUPPORTED_EXTENSIONS


class ImageReadError(Exception):
    pass


class PillowImageReader:

    def read(self, path: Path) -> np.ndarray:
        try:
            return np.array(Image.open(path))
        except (UnidentifiedImageError, OSError) as e:
            raise ImageReadError(f"Não foi possível abrir a imagem '{path.name}': {e}") from e


@dataclass
class PairingResult:
    pairs: dict[str, dict[str, Path]] = field(default_factory=dict)
    missing_cup: list[str] = field(default_factory=list)
    missing_disc: list[str] = field(default_factory=list)
    duplicated_disc: list[str] = field(default_factory=list)
    duplicated_cup: list[str] = field(default_factory=list)


class GlaucomaBenchmarkReader:

    def __init__(self, optic_disk_folder: Path, optic_cup_folder: Path) -> None:
        self._optic_disk_folder = Path(optic_disk_folder)
        self._optic_cup_folder = Path(optic_cup_folder)

    def load_pairs(self) -> PairingResult:
        disc_images, duplicated_disc = self._index_images(self._optic_disk_folder)
        cup_images, duplicated_cup = self._index_images(self._optic_cup_folder)

        pairs = {}
        for name in disc_images:
            if name in cup_images:
                image_id = Path(name).stem
                pairs[image_id] = {
                    "optic_disc": disc_images[name],
                    "optic_cup": cup_images[name],
                }

        return PairingResult(
            pairs=pairs,
            missing_cup=sorted(disc_images.keys() - cup_images.keys()),
            missing_disc=sorted(cup_images.keys() - disc_images.keys()),
            duplicated_disc=duplicated_disc,
            duplicated_cup=duplicated_cup,
        )

    def _index_images(self, folder: Path) -> tuple[dict[str, Path], list[str]]:
        if not folder.is_dir():
            raise FileNotFoundError(
                f"Pasta de imagens não encontrada: '{folder}'. "
                "Confira o caminho do dataset em config/Settings.py (DATASET_ROOT)."
            )

        images: dict[str, Path] = {}
        duplicated: list[str] = []

        for path in self._iter_images(folder):
            if path.name in images:
                duplicated.append(path.name)
            images[path.name] = path

        return images, duplicated

    @staticmethod
    def _iter_images(folder: Path):
        for entry in os.scandir(folder):
            if Path(entry.path).suffix.lower() in SUPPORTED_EXTENSIONS:
                yield Path(entry.path)