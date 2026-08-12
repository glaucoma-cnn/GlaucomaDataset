from pathlib import Path
 
from config.Settings import DATASET_ROOT, OPTIC_DISC_FOLDER_NAME, OPTIC_CUP_FOLDER_NAME
 
 
def get_optic_folders() -> tuple[Path, Path]:

    disc = DATASET_ROOT / OPTIC_DISC_FOLDER_NAME
    cup  = DATASET_ROOT / OPTIC_CUP_FOLDER_NAME
    return disc, cup
 