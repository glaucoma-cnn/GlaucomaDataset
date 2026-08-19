from pathlib import Path

DATASET_ROOT = Path( r"datasets/SMDG-19" )
OPTIC_CUP_FOLDER_NAME = "optic-cup/optic-cup"
OPTIC_DISC_FOLDER_NAME   = "optic-disc/optic-disc"


OUTPUT_DIR      = Path("Optic_Analysis/output")
CSV_FILENAME    = "optic_analysis_results.csv"
REPORT_FILENAME = "optic_analysis_report.txt"


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}


GLAUCOMA_AREA_CDR_THRESHOLD: float | None = None
