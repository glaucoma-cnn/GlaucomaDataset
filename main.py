import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from readers.Readers     import GlaucomaBenchmarkReader
from analyzers.optic_Analysis import OpticPairAnalyzer
from reporters.Reporters import CsvReporter, TxtReporter
from utils.Utils         import get_optic_folders
 
 
def run():
    disc_folder, cup_folder = get_optic_folders()
 
    pairs = GlaucomaBenchmarkReader(disc_folder, cup_folder).load_pairs()
    print(f"  {len(pairs)} pares encontrados.")
 
    df = OpticPairAnalyzer().analyze(pairs)
    print(f"  {len(df)} imagens processadas.")
 
    CsvReporter().save(df)
    TxtReporter().save(df)
 
    print("  ✓ Concluído.")
 
 
if __name__ == "__main__":
    run()
 