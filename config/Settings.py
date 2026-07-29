from pathlib import Path

DATASET_ROOT = Path( r"C:\Users\Giovana\.cache\kagglehub\datasets\deathtrooper\multichannel-glaucoma-benchmark-dataset\versions\10" )
CUP_FOLDER_NAME = "optic-cup"
DISC_FOLDER_NAME   = "opctic-disc"


OUTPUT_DIR      = Path("vessel_Analysis/output")
CSV_FILENAME    = "vessel_analysis_results.csv"
REPORT_FILENAME = "vessel_analysis_report.txt"


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}


GLAUCOMA_DISCREPANCY_THRESHOLD_PCT: float | None = None