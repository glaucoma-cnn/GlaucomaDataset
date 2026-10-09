import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.Settings import (
    AVAILABLE_FEATURES,
    DEFAULT_FEATURES,
    METADATA_PATH,
    OUTPUT_DIR,
    CSV_FILENAME,
)
from readers.Readers import GlaucomaBenchmarkReader
from analyzers.optic_Analysis import OpticPairAnalyzer
from reporters.Reporters import CsvReporter, TxtReporter, ConsistencyReporter
from utils.Utils import get_optic_folders
from LogisticRegression.Analysis_cup_disc import *


# aqui são montados os pares e processados todas as análises das imagens cup-disc
def analyze_optic_pairs():
    disc_folder, cup_folder = get_optic_folders()

    pairing = GlaucomaBenchmarkReader(disc_folder, cup_folder).load_pairs()
    print(f"  {len(pairing.pairs)} pares encontrados.")

    ConsistencyReporter().save(pairing)

    df = OpticPairAnalyzer().analyze(pairing.pairs)
    print(f"  {len(df)} imagens processadas.")

    CsvReporter().save(df)
    TxtReporter().save(df)

    print("  ✓ Concluído.")


def parse_args():
    p = argparse.ArgumentParser(description="Pipeline de detecção de glaucoma")
    p.add_argument(
        "--features", nargs="+",
        choices=AVAILABLE_FEATURES, default=DEFAULT_FEATURES,
        metavar="FEATURE",
        help=f"Features do modelo. Disponíveis: {', '.join(AVAILABLE_FEATURES)}",
    )
    p.add_argument("--skip-analysis", action="store_true",
                   help="Pula a extração e reutiliza o CSV já gerado")
    p.add_argument("--metadata", type=Path, default=METADATA_PATH,
                   help="Caminho do 'metadata - standardized.csv' (padrão: Settings.METADATA_PATH)")
    return p.parse_args()


# aqui está rodando a pipeline com o sklearn importando o linear_model de regresão logística,
# utilizamos o csv criado do def acima mergiado com os dados do metadata
def run_glaucoma_pipeline(features, metadata_path):
    target = 'glaucoma_flag'

    fileCSV = load_data(OUTPUT_DIR / CSV_FILENAME)
    metadata = load_metadata(metadata_path)

    fileCSV = merge_features_with_labels(fileCSV, metadata)

    # aqui está a analise de acurácia do modelo treinado (as imagens de treino e teste já são
    # pre-classificadas dentro do metadata original, segue o arquivo LogisticRegression/Analysis_cup_disc)
    df_train, df_test = split_train_test(fileCSV)
    cross_validate_model(df_train, features, target)
    model = train_model(df_train, features, target)
    result = predict(model, df_test, features)
    accuracy = evaluate_accuracy(df_test, result, target)
    print(f"  Acurácia: {accuracy:.2%}")

    save_result(result, 'results', 'glaucoma_predictions.csv')


if __name__ == "__main__":
    args = parse_args()
    try:
        if not args.skip_analysis:
            analyze_optic_pairs()
        run_glaucoma_pipeline(args.features, args.metadata)
    except FileNotFoundError as e:
        print(f"\n  ✗ Arquivo ou pasta não encontrado: {e}")
    except ValueError as e:
        print(f"\n  ✗ Dados inválidos para rodar a pipeline: {e}")