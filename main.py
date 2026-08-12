import sys
from pathlib import Path
import os
import pandas as pd
from sklearn.linear_model import LogisticRegression
sys.path.insert(0, str(Path(__file__).parent))

from readers.Readers     import GlaucomaBenchmarkReader
from analyzers.optic_Analysis import OpticPairAnalyzer
from reporters.Reporters import CsvReporter, TxtReporter
from utils.Utils         import get_optic_folders
from LogisticRegression.Analysis_cup_disc import *
 
 # aqui são montados os pares e processados todas as análises das  imagens cup-disc
def analyze_optic_pairs():
    disc_folder, cup_folder = get_optic_folders()
 
    pairs = GlaucomaBenchmarkReader(disc_folder, cup_folder).load_pairs()
    print(f"  {len(pairs)} pares encontrados.")
 
    df = OpticPairAnalyzer().analyze(pairs)
    print(f"  {len(df)} imagens processadas.")
 
    CsvReporter().save(df)
    TxtReporter().save(df)
 
    print("  ✓ Concluído.")

# aqui está rodando a pipeline com o sklearn importando o linear_model de regresão logística, utilizamos o csv criado do def acima mergiado com os dados do metadata
def run_glaucoma_pipeline():
    features = ['disc_pixels', 'cup_pixels', 'ratio_cup_disc']
    target = 'glaucoma_flag'

    fileCSV = load_data(r'C:\Users\Giovana\Desktop\GlaucomaDataset\Optic_Analysis\output\optic_analysis_results.csv')
    metadata = load_metadata(r"C:\Users\Giovana\.cache\kagglehub\datasets\deathtrooper\multichannel-glaucoma-benchmark-dataset\versions\10\metadata - standardized.csv")

    fileCSV = merge_features_with_labels(fileCSV, metadata)


# aqui está a analise de acurácia do modelo treinado ( as imagens de treino e teste já são pre-classificadas dentro do metadata original, segue o arquivo LogisticRegression/Analysis_cup_disc )
    #df_train, df_test = split_train_test(fileCSV)
    #model = train_model(df_train, features, target)
    #result = predict(model, df_test, features)
    #accuracy = evaluate_accuracy(df_test, result, target)
    #print(f"Acurácia: {accuracy:.2%}")
    
    save_result(result, 'results', 'glaucoma_predictions.csv')
     

   
if __name__ == "__main__":
    analyze_optic_pairs()
    run_glaucoma_pipeline()
 