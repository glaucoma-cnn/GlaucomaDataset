import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from readers.Readers     import GlaucomaBenchmarkReader
from analyzers.optic_Analysis import OpticPairAnalyzer