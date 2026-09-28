from pathlib import Path

DATASET_ROOT = Path(r"C:\Users\Giovana\.cache\kagglehub\datasets\deathtrooper\multichannel-glaucoma-benchmark-dataset\versions\10")
OPTIC_CUP_FOLDER_NAME = "optic-cup/optic-cup"
OPTIC_DISC_FOLDER_NAME = "optic-disc/optic-disc"


OUTPUT_DIR = Path("Optic_Analysis/output")
CSV_FILENAME = "optic_analysis_results.csv"
REPORT_FILENAME = "optic_analysis_report.txt"
CONSISTENCY_REPORT_FILENAME = "dataset_consistency_report.txt"


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}


GLAUCOMA_AREA_CDR_THRESHOLD: float | None = None


GLAUCOMA_NEGATIVE_LABEL = 0
GLAUCOMA_POSITIVE_LABEL = 1
GLAUCOMA_SUSPECT_LABEL = -1
VALID_GLAUCOMA_LABELS = {GLAUCOMA_NEGATIVE_LABEL, GLAUCOMA_POSITIVE_LABEL}

CROSS_VALIDATION_FOLDS = 5

# necessário fixar um valor para manter a padronização de acurácia
RANDOM_STATE = 42
