# GlaucomaDataset

Pipeline preliminar para análise de máscaras de segmentação do **disco óptico** (*optic disc*) e do **copo óptico** (*optic cup*) em imagens retinianas do dataset **SMDG-19**.

Nesta etapa do projeto, o objetivo é utilizar as máscaras disponíveis no dataset para extrair medidas morfológicas simples, especialmente a **Area-based Cup-to-Disc Ratio (Area CDR)**, e gerar relatórios exploratórios sobre os dados.

O código também permite realizar uma **triagem preliminar e experimental** baseada em um limiar configurável de Area CDR.

> **Importante:** a sinalização produzida pelo código é apenas uma ferramenta exploratória e didática. Ela **não representa diagnóstico clínico de glaucoma**.

teste

---

# Estrutura do projeto

```text
GlaucomaDataset/
├── analyzers/
│   └── optic_Analysis.py
├── config/
│   └── Settings.py
├── readers/
│   └── Readers.py
├── reporters/
│   └── Reporters.py
├── support_Code/
├── utils/
│   └── Utils.py
├── main.py
└── README.md
```

## `main.py`

Ponto de entrada da aplicação.

É responsável por executar a pipeline completa:

1. Montar os caminhos das pastas do dataset.
2. Localizar e parear as máscaras de disco óptico e copo óptico.
3. Executar a análise das máscaras.
4. Gerar um `DataFrame` com os resultados.
5. Salvar os resultados em CSV e TXT.

---

## `config/Settings.py`

Centraliza as configurações utilizadas pela pipeline, como:

* Caminho local do dataset.
* Nome das pastas contendo as máscaras.
* Diretório de saída.
* Nome dos arquivos de relatório.
* Extensões de imagem suportadas.
* Limiar opcional de Area CDR utilizado na triagem experimental.

---

## `readers/Readers.py`

Responsável pela leitura das imagens e organização dos pares de máscaras.

A classe `GlaucomaBenchmarkReader` procura imagens com o mesmo nome nas pastas de:

* `optic-disc`;
* `optic-cup`.

Por exemplo:

```text
optic-disc/PAPILA-10.png
optic-cup/PAPILA-10.png
```

formam um par correspondente à mesma imagem.

A classe `PillowImageReader` utiliza a biblioteca Pillow para abrir a imagem e convertê-la para um array NumPy.

`GlaucomaBenchmarkReader.load_pairs()` retorna um `PairingResult`, contendo não só os pares válidos, mas também os arquivos sem par e os nomes duplicados encontrados em cada pasta (detalhado em **Pareamento de máscaras e relatório de consistência**).

---

## `analyzers/optic_Analysis.py`

É o núcleo da análise implementada nesta etapa do projeto.

Para cada par de máscaras de disco e copo óptico, o módulo:

1. Abre as imagens.
2. Conta os pixels pertencentes ao disco óptico.
3. Conta os pixels pertencentes ao copo óptico.
4. Calcula a Area CDR.
5. Calcula medidas exploratórias auxiliares.
6. Verifica uma condição simples de consistência anatômica.
7. Opcionalmente aplica um limiar de Area CDR para triagem preliminar.
8. Extrai features morfológicas de forma (perímetro, excentricidade, razão de aspecto e circularidade) tanto do disco quanto do copo.

Imagens que não puderem ser abertas (arquivo corrompido ou formato inválido) são ignoradas individualmente, sem interromper o processamento das demais — ver **Tratamento de erros**.

O resultado é armazenado em um `DataFrame` do Pandas.

---

## `reporters/Reporters.py`

Responsável por armazenar e apresentar os resultados produzidos pela análise.

São gerados três tipos de arquivo:

* **CSV:** contém os resultados individuais de cada imagem.
* **TXT (análise):** contém um resumo estatístico da execução.
* **TXT (consistência):** contém o relatório de pareamento — ver **Pareamento de máscaras e relatório de consistência**.

O relatório textual apresenta informações como:

* quantidade de imagens analisadas;
* média, mediana, desvio-padrão, mínimo e máximo da Area CDR;
* estatísticas da discrepância entre as áreas;
* quantidade de máscaras anatomicamente consistentes;
* quantidade de imagens sinalizadas pela triagem, quando um limiar estiver configurado;
* imagens com maiores valores de Area CDR.

---

## `utils/Utils.py`

Responsável por montar os caminhos utilizados pela pipeline a partir das configurações presentes em `config/Settings.py`.

Por exemplo, combina:

```text
DATASET_ROOT
```

com:

```text
OPTIC_DISC_FOLDER_NAME
```

para obter o caminho completo da pasta contendo as máscaras de disco óptico.

---

## `support_Code/`

Pasta destinada a códigos auxiliares utilizados na preparação ou aquisição do dataset.

---

# Instalação

Instale as dependências utilizadas nesta etapa:

```bash
pip install pillow numpy pandas scikit-image
```

`scikit-image` foi adicionada para o cálculo das features morfológicas (ver seção **Features morfológicas do disco e do copo**).

---

# Configuração do dataset

O dataset utilizado pelo projeto é o **SMDG-19**.

O dataset não precisa estar armazenado dentro do repositório. Basta informar no código onde ele está localizado na máquina.

Abra:

```text
config/Settings.py
```

e configure:

```python
DATASET_ROOT = Path(r"C:\caminho\para\SMDG-19")
```

Por exemplo:

```python
DATASET_ROOT = Path(r"D:\datasets\SMDG-19")
```

## Estrutura das pastas

Dependendo da forma como o SMDG-19 foi baixado, pode existir uma duplicação nos diretórios:

```text
SMDG-19/
├── optic-disc/
│   └── optic-disc/
│       └── imagens...
│
└── optic-cup/
    └── optic-cup/
        └── imagens...
```

Nesse caso, mantenha:

```python
OPTIC_DISC_FOLDER_NAME = "optic-disc/optic-disc"
OPTIC_CUP_FOLDER_NAME = "optic-cup/optic-cup"
```

Caso sua instalação tenha a estrutura:

```text
SMDG-19/
├── optic-disc/
│   └── imagens...
│
└── optic-cup/
    └── imagens...
```

utilize:

```python
OPTIC_DISC_FOLDER_NAME = "optic-disc"
OPTIC_CUP_FOLDER_NAME = "optic-cup"
```

Não é necessário reorganizar fisicamente as pastas do dataset apenas para executar a pipeline.

---

# Configurações principais

## `DATASET_ROOT`

Caminho para a pasta raiz onde o dataset está armazenado.

Exemplo:

```python
DATASET_ROOT = Path(r"D:\datasets\SMDG-19")
```

---

## `OPTIC_DISC_FOLDER_NAME`

Caminho relativo, a partir de `DATASET_ROOT`, para as máscaras do disco óptico.

---

## `OPTIC_CUP_FOLDER_NAME`

Caminho relativo, a partir de `DATASET_ROOT`, para as máscaras do copo óptico.

---

## `OUTPUT_DIR`

Diretório onde serão armazenados automaticamente os arquivos CSV e TXT produzidos pela pipeline.

---

## `GLAUCOMA_AREA_CDR_THRESHOLD`

Limiar opcional utilizado para realizar uma **triagem preliminar baseada na Area CDR**.

Exemplo:

```python
GLAUCOMA_AREA_CDR_THRESHOLD: float | None = None
```

Quando configurado como:

```python
None
```

a sinalização automática permanece desativada.

Quando um valor for configurado, a lógica utilizada será:

```python
glaucoma_flag = area_cdr > GLAUCOMA_AREA_CDR_THRESHOLD
```

Essa flag deve ser interpretada apenas como uma **sinalização experimental para estudo da característica**, e não como diagnóstico clínico.

---

# Execução

A partir do diretório adequado, execute:

```bash
python GlaucomaDataset/main.py
```

ou, caso o terminal já esteja dentro da pasta do projeto:

```bash
python main.py
```

---

# Fluxo da pipeline

```text
main.py
│
├── utils
│   └── monta os caminhos das pastas de disco e copo óptico
│
├── GlaucomaBenchmarkReader.load_pairs()
│   │
│   ├── localiza as máscaras de disco óptico
│   ├── localiza as máscaras de copo óptico
│   └── pareia arquivos que possuem o mesmo nome
│
├── OpticPairAnalyzer.analyze(pairs)
│   │
│   ├── count_pixels()
│   │   └── conta os pixels não-pretos de cada máscara
│   │
│   ├── calcula a área do disco óptico
│   ├── calcula a área do copo óptico
│   ├── calcula a Area CDR
│   ├── calcula medidas exploratórias auxiliares
│   ├── verifica consistência anatômica
│   └── realiza triagem opcional por Area CDR
│
└── reporters
    ├── gera CSV
    └── gera relatório TXT
```

---

# Contagem das áreas

As máscaras são convertidas para arrays NumPy.

Um pixel é considerado pertencente à estrutura quando possui algum valor diferente de zero.

Para imagens com três canais:

```python
mask = (
    (array[:, :, 0] > 0)
    | (array[:, :, 1] > 0)
    | (array[:, :, 2] > 0)
)
```

Para máscaras com apenas um canal:

```python
mask = array > 0
```

A área é então aproximada pela quantidade de pixels pertencentes à máscara:

```python
area = np.sum(mask)
```

Assim são obtidas:

```text
disc_area = número de pixels do disco óptico
cup_area  = número de pixels do copo óptico
```

---

# Area CDR

A principal medida explorada atualmente é a **Area-based Cup-to-Disc Ratio (Area CDR)**.

Ela é calculada por:

```text
Area CDR = área do copo óptico / área do disco óptico
```

ou:

```python
area_cdr = cup_area / disc_area
```

Por exemplo:

```text
Área do disco = 10.000 pixels
Área do copo  = 4.000 pixels
```

resulta em:

```text
Area CDR = 4.000 / 10.000
Area CDR = 0.40
```

Isso significa que a área do copo corresponde a aproximadamente 40% da área do disco.

A medida é chamada explicitamente de **Area CDR** para distingui-la da definição clínica clássica de CDR baseada nos diâmetros das estruturas.

---

# Diferença absoluta

Também é calculada a diferença absoluta entre as áreas:

```python
absolute_difference = abs(cup_area - disc_area)
```

Por exemplo:

```text
Disco = 10.000 pixels
Copo  = 4.000 pixels
```

resulta em:

```text
Diferença absoluta = 6.000 pixels
```

Essa medida é mantida principalmente para exploração e compreensão dos dados.

---

# Discrepância percentual

Também é calculada uma medida exploratória de discrepância entre as áreas:

```text
discrepancy_pct =
    |cup_area - disc_area|
    -------------------------------- × 100
       max(cup_area, disc_area)
```

Em código:

```python
discrepancy_pct = (
    abs(cup_area - disc_area)
    / max(cup_area, disc_area)
    * 100
)
```

Por exemplo:

```text
Disco = 10.000 pixels
Copo  = 4.000 pixels
```

temos:

```text
Diferença = 6.000
Maior área = 10.000
```

portanto:

```text
discrepancy_pct = 60%
```

Essa variável é mantida como uma **estatística exploratória**.

Ela **não é mais utilizada como critério para a triagem de glaucoma**.

---

# Consistência anatômica

Em condições normais, espera-se que o copo óptico esteja contido no disco óptico.

Consequentemente, espera-se:

```text
cup_area <= disc_area
```

O código registra essa verificação em:

```python
anatomical_consistency = cup_area <= disc_area
```

Casos em que:

```text
cup_area > disc_area
```

podem indicar uma amostra que merece inspeção mais detalhada.

Essa verificação funciona como uma análise preliminar de qualidade dos dados, e não como característica diagnóstica.

---

# Proteção contra máscaras de disco vazias

A Area CDR depende da divisão:

```python
cup_area / disc_area
```

Portanto, uma máscara de disco com área igual a zero impediria o cálculo.

O código verifica essa situação:

```python
if disc_area == 0:
    raise ValueError(...)
```

Isso permite detectar explicitamente máscaras potencialmente inválidas em vez de gerar uma divisão por zero.

---

# Pareamento de máscaras e relatório de consistência

`GlaucomaBenchmarkReader.load_pairs()` pareia as máscaras de disco e copo óptico pelo nome do arquivo. Além dos pares válidos, o método agora também identifica:

* **discos sem copo correspondente**;
* **copos sem disco correspondente**;
* **nomes de arquivo duplicados** dentro da pasta de disco ou de copo.

Esse resultado é representado por `PairingResult`:

```python
@dataclass
class PairingResult:
    pairs: dict[str, dict[str, Path]]
    missing_cup: list[str]
    missing_disc: list[str]
    duplicated_disc: list[str]
    duplicated_cup: list[str]
```

A classe `ConsistencyReporter` grava esse resultado em um arquivo de texto próprio, com um resumo em números e a lista de cada inconsistência encontrada:

```text
Optic_Analysis/output/dataset_consistency_report.txt
```

Esse relatório é útil para conferir a integridade do dataset antes de confiar nos resultados da análise — por exemplo, para perceber que uma pasta está incompleta ou que algum arquivo foi salvo com nome repetido.

---

# Features morfológicas do disco e do copo

Além da Area CDR, o pipeline agora calcula medidas de **forma** — não só de tamanho — para o disco e para o copo ópticos, usando `skimage.measure.label` e `regionprops`:

* **Perímetro** (`disc_perimeter`, `cup_perimeter`) — contorno da estrutura, em pixels.
* **Excentricidade** (`disc_eccentricity`, `cup_eccentricity`) — o quanto a forma se aproxima de um círculo (0) ou de uma elipse alongada (perto de 1).
* **Razão de aspecto** (`disc_aspect_ratio`, `cup_aspect_ratio`) — eixo maior dividido pelo eixo menor da elipse ajustada à forma.
* **Circularidade** (`disc_circularity`, `cup_circularity`) — calculada como `4π × área / perímetro²`; vale `1` para um círculo perfeito e menos que `1` para formas irregulares.

A extração é feita a partir da mesma máscara binária já usada para contar pixels (`disc_pixels`/`cup_pixels`), sem reler o arquivo de imagem. Quando a máscara tem mais de uma região conectada (ruído), apenas a maior é considerada. Quando a máscara está vazia, as quatro medidas são retornadas como `0.0` em vez de gerar erro.

---

# Tratamento de erros

O pipeline foi ajustado para não travar por completo diante de problemas pontuais nos dados:

* **Pasta do dataset não encontrada** — `GlaucomaBenchmarkReader` verifica se a pasta de disco/copo existe antes de tentar listá-la, e informa que o caminho deve ser conferido em `config/Settings.py`.
* **Imagem corrompida ou em formato inválido** — `PillowImageReader.read()` relança o erro como `ImageReadError`; `OpticPairAnalyzer.analyze()` captura essa exceção, imprime um aviso com o `image_id` afetado e segue para a próxima imagem, em vez de interromper todo o processamento.
* **CSV de features ou metadata não encontrados** — mensagens específicas orientam rodar a etapa de análise antes, ou conferir o caminho configurado.
* **Split de treino/teste vazio** — se nenhum (ou todos os) `image_id` contiver `'train'`, o erro é sinalizado explicitamente em vez de falhar mais adiante, de forma confusa, durante o treino.

Qualquer um desses erros, quando não tratado localmente, é capturado no bloco principal de `main.py` e exibido como uma mensagem curta, sem traceback.

---

# Resultados armazenados

Para cada par de máscaras processado, o `DataFrame` contém atualmente:

```text
image_id
disc_pixels
cup_pixels
area_cdr
absolute_difference
discrepancy_pct
anatomical_consistency
area_cdr_flag
disc_perimeter
disc_eccentricity
disc_aspect_ratio
disc_circularity
cup_perimeter
cup_eccentricity
cup_aspect_ratio
cup_circularity
```

A sinalização preliminar por limiar de Area CDR foi renomeada de `glaucoma_flag` para **`area_cdr_flag`**. Isso evita ambiguidade com o `glaucoma_flag` real do dataset (o rótulo clínico, usado como alvo do treino do classificador em uma etapa posterior do projeto) — os dois deixam de ter o mesmo nome quando o CSV gerado aqui é combinado com o metadata do dataset.

Esses dados constituem uma primeira etapa da extração de características morfológicas do projeto.

---

# Alterações Lucas

As seguintes alterações foram realizadas após revisão do código inicial:

* **Renomeado o conceito principal para `Area CDR`.**

  * A razão `cup_area / disc_area` passou a ser explicitamente identificada como uma razão baseada em áreas.
  * Isso evita confusão com outras definições de Cup-to-Disc Ratio.

* **Criada explicitamente a variável `area_cdr`.**

  * Antes, o cálculo aparecia diretamente durante a construção do `DataFrame`.
  * Agora o valor é calculado e nomeado antes de ser utilizado.

* **Renomeado o parâmetro de configuração para `GLAUCOMA_AREA_CDR_THRESHOLD`.**

  * O nome anterior fazia referência à discrepância percentual.
  * O novo nome deixa claro que o limiar é aplicado sobre a Area CDR.

* **Corrigida a lógica da triagem.**

  * A versão anterior comparava `discrepancy_pct` com o limiar.
  * Agora a comparação é realizada corretamente com:

```python
area_cdr > GLAUCOMA_AREA_CDR_THRESHOLD
```

* **Alterada a verificação do threshold para `is not None`.**

  * Em vez de:

```python
if GLAUCOMA_AREA_CDR_THRESHOLD
```

* utiliza-se:

```python
if GLAUCOMA_AREA_CDR_THRESHOLD is not None
```

* Isso diferencia corretamente um parâmetro não configurado de um valor numérico válido.

* **Adicionada proteção contra máscaras de disco vazias.**

  * Uma máscara com `disc_area == 0` impossibilita o cálculo da Area CDR.
  * O código agora gera um erro explícito nesse caso.

* **Adicionada a variável `anatomical_consistency`.**

  * Ela verifica se:

```text
cup_area <= disc_area
```

* Casos que não atendem a essa condição podem ser inspecionados como possíveis inconsistências das máscaras.

* **A discrepância percentual deixou de controlar a triagem.**

  * `discrepancy_pct` continua disponível como estatística exploratória.
  * Ela não é utilizada para definir `glaucoma_flag`.

* **A diferença absoluta foi mantida como medida exploratória.**

  * `absolute_difference` continua sendo registrada para facilitar a análise e compreensão das relações entre as áreas das máscaras.

* **Atualizado o relatório TXT.**

  * O relatório passa a apresentar estatísticas da `area_cdr`.
  * Inclui a quantidade de casos anatomicamente consistentes e inconsistentes.
  * A seção de triagem passa a informar o limiar de Area CDR.
  * A documentação deixa explícito que a flag representa somente triagem preliminar.

* **Alterado o ranking principal do relatório.**

  * Em vez de apresentar apenas as maiores discrepâncias, o relatório passa a destacar os maiores valores de **Area CDR**, mais diretamente relacionados ao objetivo atual do exercício.

* **Corrigidas referências antigas a “veia” e “artéria”.**

  * O projeto atual trabalha com **disco óptico e copo óptico**, não com estruturas vasculares.

* **Corrigida a descrição do papel de `utils`.**

  * O módulo monta os caminhos das pastas de disco e copo óptico a partir das configurações.

* **Atualizada a descrição do núcleo científico do projeto.**

  * A versão atual deve ser entendida principalmente como uma etapa de:

    * leitura das máscaras;
    * extração de áreas;
    * cálculo da Area CDR;
    * análise exploratória;
    * auditoria preliminar;
    * triagem didática opcional.

---

# Alterações recentes

As seguintes alterações foram realizadas após a versão anterior deste README:

* **Pareamento passou a reportar o que não bate.**

  * `load_pairs()` agora retorna um `PairingResult`, não só os pares válidos.
  * Discos sem copo, copos sem disco e nomes duplicados passam a ser identificados explicitamente.
  * Um relatório próprio (`dataset_consistency_report.txt`) é gerado com esse resumo.

* **Adicionadas features morfológicas de forma.**

  * Perímetro, excentricidade, razão de aspecto e circularidade, calculadas via `skimage.measure.regionprops`.
  * Calculadas tanto para o disco quanto para o copo, reaproveitando a mesma máscara já usada na contagem de pixels.

* **A sinalização por limiar de Area CDR foi renomeada.**

  * De `glaucoma_flag` para `area_cdr_flag`, para não colidir com o rótulo clínico real do dataset em etapas posteriores do projeto.

* **Adicionado tratamento de erros pontuais.**

  * Pasta do dataset ausente, imagem corrompida, CSV/metadata não encontrados e split de treino/teste vazio agora geram mensagens específicas em vez de interromper a execução de forma abrupta.
  * Uma imagem com problema de leitura é ignorada individualmente; o restante do processamento continua.

---

# Próximas extensões possíveis

Esta etapa representa apenas a primeira parte do pipeline planejado.

Do que estava listado aqui, já foram implementados: **perímetro**, **circularidade**, **excentricidade**, **razão de aspecto** e o uso de **propriedades de elipses ajustadas** às máscaras (ver **Features morfológicas do disco e do copo**).

Futuramente ainda poderão ser adicionadas outras características morfológicas, como:

* diâmetros horizontal e vertical;
* Vertical Cup-to-Disc Ratio;
* características do neuroretinal rim.

Também poderão ser incorporadas informações das imagens originais de fundo de olho, como:

* intensidade;
* cor;
* histogramas;
* textura.

Posteriormente, essas características poderão ser associadas aos **rótulos reais do SMDG-19** para construção de um dataset tabular destinado ao treinamento e avaliação de classificadores de aprendizado de máquina.

---

# Observação sobre organização futura

À medida que novas análises forem incorporadas, é recomendável manter a separação de responsabilidades já utilizada no projeto:

```text
readers/
    leitura e organização dos dados

analyzers/
    extração de características e análises

reporters/
    geração dos resultados

config/
    parâmetros e caminhos

utils/
    funções auxiliares
```

Caso sejam necessários novos tipos de análise, novos módulos podem ser adicionados em `analyzers/`, evitando concentrar funcionalidades diferentes em um único arquivo.

---

# Alterações: seleção de features, validação cruzada e registro dos folds 13-10-2026

> Histórico da implementação de 13/10/2026. O protocolo descrito nesta seção foi substituído pelas alterações de 30/10/2026, documentadas ao final deste README.
 
Este documento descreve as mudanças feitas na pipeline de classificação de glaucoma (regressão logística sobre as features extraídas das máscaras de disco e copo ópticos).
 
## Resumo
 
1. **Seleção de features pelo terminal** com `argparse`.
2. **Validação cruzada estratificada** com 5 folds, aplicada no conjunto de treino.
3. **CSV com o resultado de cada fold** (acertos, erros, porcentagem de acerto) e com a média e o desvio padrão.

---
## 1. Seleção de features com `argparse`
 
Antes, as features do modelo ficavam fixas no `main.py`:
 
```python
features = ['disc_pixels', 'cup_pixels', 'area_cdr']
```
 
Agora elas são escolhidas ao rodar o programa. Como o `OpticPairAnalyzer` já calcula todas as colunas de uma vez e salva no CSV de features, escolher features é apenas escolher colunas do DataFrame. Não é preciso `if` para cada feature.
 
### Arquivos alterados
 
**`config/Settings.py`**
 
- `AVAILABLE_FEATURES`: lista de todas as features que podem ser escolhidas.
- `DEFAULT_FEATURES`: features usadas quando nada é informado (`disc_pixels`, `cup_pixels`, `area_cdr`).
- `METADATA_PATH`: caminho padrão do `metadata - standardized.csv`.
Ficaram de fora `anatomical_consistency` e `area_cdr_flag`, porque são constantes nos dados atuais e não ajudam o modelo.
 
**`main.py`**
 
- Nova função `parse_args()` com as opções abaixo.
- `run_glaucoma_pipeline(features, metadata_path)` passou a receber os parâmetros em vez de usar valores fixos e caminhos da máquina.
- O CSV de features é lido com `OUTPUT_DIR / CSV_FILENAME`, o mesmo caminho em que o `CsvReporter` grava.
### Opções disponíveis
 
| Opção | O que faz | Padrão |
|---|---|---|
| `--features F1 F2 ...` | Features usadas no modelo | `DEFAULT_FEATURES` |
| `--skip-analysis` | Pula a extração das imagens e reutiliza o CSV já gerado | desligado |
| `--metadata CAMINHO` | Caminho do `metadata - standardized.csv` | `METADATA_PATH` |
 
### Features disponíveis
 
```
disc_pixels  cup_pixels  area_cdr  absolute_difference  discrepancy_pct
disc_perimeter  disc_eccentricity  disc_aspect_ratio  disc_circularity
cup_perimeter  cup_eccentricity  cup_aspect_ratio  cup_circularity
```
 
Qualquer outro nome gera o erro `invalid choice`.
 
### Exemplos de uso
 
```bash
# usa tudo no padrão
python main.py
 
# escolhe as features
python main.py --features area_cdr cup_circularity disc_eccentricity
```

Os parâmetros só têm efeito quando digitados no terminal, na mesma linha do comando.
 
---
 ## 2. Validação cruzada estratificada (5 folds)
 
**Arquivo alterado:** `LogisticRegression/Analysis_cup_disc.py` (função `cross_validate_model`).
 
### Como funciona
 
O conjunto de **treino** é dividido em 5 pedaços (folds). O processo se repete 5 vezes: em cada rodada, o modelo treina com 4 pedaços e é avaliado no pedaço restante. Ao final há 5 notas de acurácia, resumidas pela média e pelo desvio padrão.
 
| Rodada | Treina com | Avalia em |
|---|---|---|
| 1 | folds 2, 3, 4, 5 | fold 1 |
| 2 | folds 1, 3, 4, 5 | fold 2 |
| 3 | folds 1, 2, 4, 5 | fold 3 |
| 4 | folds 1, 2, 3, 5 | fold 4 |
| 5 | folds 1, 2, 3, 4 | fold 5 |
 
### Por que estratificada
 
Com `StratifiedKFold`, cada fold mantém a mesma proporção de casos com e sem glaucoma do conjunto de treino. Sem isso, um fold poderia ficar com poucos casos positivos e a nota daquela rodada deixaria de ser confiável.
 
### Parâmetros
 
Vêm de `config/Settings.py`:
 
- `CROSS_VALIDATION_FOLDS = 5`: número de folds.
- `RANDOM_STATE = 42`: fixa o embaralhamento, então os folds e os resultados são os mesmos a cada execução.
- `shuffle=True`: embaralha os dados antes de dividir.
### Duas avaliações diferentes
 
| | Validação cruzada | Avaliação no teste |
|---|---|---|
| Onde | Dentro do treino | No conjunto de teste, separado desde o início |
| Como | 5 rodadas, cada uma com um fold de validação | Treina uma vez e testa uma vez |
| Resultado | Média ± desvio padrão | Uma acurácia |
O `± X%` impresso na saída é o desvio padrão das 5 notas da validação cruzada. Ele mede a estabilidade dentro do treino e não se aplica à acurácia do teste.
 
### Observação sobre o split
 
A divisão treino/teste vem do metadata original e é feita pelo texto `train` no `image_id`. O treino tem bem menos imagens que o teste e parece vir de poucas bases, enquanto o teste mistura várias. Por isso é normal a acurácia da validação cruzada ficar acima da acurácia do teste: elas medem coisas diferentes (dados do mesmo grupo do treino versus dados de outras fontes).
 
---
 ## 3. CSV com os resultados dos folds
 
**Arquivo gerado:** `results/cv_folds.csv`
 
A cada execução, a função grava as linhas dos 5 folds e as linhas de resumo no mesmo arquivo, sempre **adicionando ao final** (`mode='a'`). O cabeçalho só é escrito na primeira vez. Assim, rodar com parâmetros diferentes acumula as execuções em um único arquivo.
## Dependências
 
```bash
pip install scikit-learn pandas numpy pillow scikit-image
```
 
O pacote se chama `scikit-learn`, mas é importado como `sklearn`.
 
## Arquivos modificados
 
| Arquivo | Mudança |
|---|---|
| `config/Settings.py` | `AVAILABLE_FEATURES`, `DEFAULT_FEATURES`, `METADATA_PATH` |
| `main.py` | `parse_args()`, `run_glaucoma_pipeline(features, metadata_path)`, chamada da validação cruzada |
| `LogisticRegression/Analysis_cup_disc.py` | `cross_validate_model` com `StratifiedKFold` e gravação do CSV dos folds |

---

# Atualização das folds de validação— preparação dos grupos e avaliação entre datasets

Esta atualização altera a preparação dos dados e os protocolos de avaliação da regressão logística. A extração de características das máscaras e o modelo utilizado foram mantidos.

## Por que foi necessário alterar a avaliação

As seis bases utilizadas — CRFO, DRISHTI, G1020, ORIGA, PAPILA e REFUGE1 — não possuem uma organização única de identificação de pacientes, nomes de imagens e divisão de treino e teste. Por isso, não é adequado interpretar os nomes dos arquivos como uma separação padronizada de todo o benchmark.

Na implementação anterior, a função `split_train_test` colocava no treino qualquer imagem cujo `image_id` contivesse `train`. Todas as outras eram colocadas no teste. Essa regra selecionava imagens de treino da REFUGE1 e da DRISHTI, enquanto as outras bases ficavam inteiramente no teste. Imagens de validação também eram tratadas como teste quando seus nomes não continham `train`.

A validação cruzada anterior era aplicada somente ao conjunto formado por essa regra, e não às seis bases reunidas. O problema estava na falta de uma convenção comum de separação: o nome do arquivo, isoladamente, não garantia um protocolo uniforme entre as bases.

Mesmo quando as seis bases são reunidas em uma validação cruzada estratificada, a estratificação equilibra os rótulos, mas não padroniza as bases nem garante independência entre pacientes. Treino e validação podem conter imagens das mesmas origens e, sem agrupamento, até do mesmo paciente ou fotografias duplicadas. Assim, uma acurácia nessa mistura, isoladamente, não sustenta uma conclusão confiável de generalização para outra base. Isso não invalida automaticamente a validação cruzada: limita a conclusão que pode ser tirada dela.

Para separar essas perguntas, foram implementados dois experimentos complementares e uma preparação comum dos grupos.

## 1. Preservação das informações do metadata

**Alteração:** `load_metadata` passou a preservar `patient_id`, `original_name` e o caminho da fotografia, além do identificador e do rótulo. Também identifica a base de origem pelo prefixo do `image_id`.

**Por que foi necessária:** essas informações eram descartadas, mas são necessárias para reconhecer pacientes, verificar duplicatas e reservar uma base inteira no LODO. Elas controlam a separação dos dados e não são utilizadas como características da regressão logística. A união das tabelas também passou a exigir um registro por `image_id`, evitando multiplicação silenciosa de amostras por IDs repetidos.

## 2. Identificação dos pacientes — `get_patient_id`

**Alteração:** utiliza o paciente informado no metadata, quando disponível. Na CRFO, extrai a identificação do nome original e mantém os dois olhos do mesmo paciente juntos. O identificador é associado à base de origem.

**Por que foi necessária:** a identificação de paciente não é padronizada. A PAPILA informa esse campo; na CRFO ele pode ser recuperado pelo nome. Separar imagens de um mesmo paciente entre treino e teste comprometeria a independência da avaliação. Nas demais bases, IDs sequenciais de imagens não foram considerados IDs de paciente sem evidência dessa relação.

## 3. Verificação de fotografias idênticas — `get_image_hash`

**Alteração:** calcula um hash SHA-256 a partir das dimensões e dos pixels da fotografia convertida para RGB.

**Por que foi necessária:** nomes diferentes não garantem fotografias diferentes. Essa comparação permite reconhecer cópias exatas, inclusive entre bases. O hash não é um embedding e não entra como característica do modelo. Ele não detecta necessariamente versões recortadas, redimensionadas ou com pixels alterados.

## 4. Criação e preparação dos grupos — `create_groups` e `prepare_experiment_groups`

**Alteração:** imagens ligadas pelo paciente, pelo nome original repetido dentro da mesma base ou por pixels idênticos recebem o mesmo `group_id`. Relações transitivas também são respeitadas: se A está ligada a B e B a C, as três ficam juntas. A tabela de grupos é salva para conferência.

**Por que foi necessária:** a unidade de separação precisa ser o grupo relacionado, e não apenas cada linha da tabela. Onde não há paciente identificável, cada imagem começa independente, podendo ainda ser ligada a outras pelas verificações de nome e de pixels. Essa medida reduz o risco de vazamento, mas não comprova independência por paciente quando a informação não existe.

## 5. Experimento A — validação cruzada estratificada com grupos

**Alteração:** `cross_validate_model` passou a utilizar `StratifiedGroupKFold` com cinco folds, semente 42 e todas as imagens elegíveis das seis bases. As antigas marcações de treino, teste e validação deixam de determinar a divisão. Em cada rodada, quatro folds treinam e um valida.

**Por que foi necessária:** permite avaliar o modelo na mistura das seis bases, tentando preservar a proporção das classes e mantendo cada grupo inteiro no mesmo fold. Diferentemente do `StratifiedKFold` anterior, considera a dependência identificada entre imagens. Os tamanhos e as proporções dos folds podem variar para respeitar os grupos.

**Interpretação:** esse experimento mede o desempenho dentro do conjunto combinado. Como as mesmas bases podem estar representadas no treino e na validação, ele não demonstra, sozinho, desempenho em uma base desconhecida.

## 6. Experimento B — Leave-One-Dataset-Out (LODO)

**Alteração:** `leave_one_dataset_out` cria seis folds. A cada rodada, uma base inteira é teste e as outras cinco são candidatas ao treino. Por exemplo: CRFO no teste e DRISHTI, G1020, ORIGA, PAPILA e REFUGE1 no treino. Se um grupo do teste aparecer em outra base, suas imagens são retiradas do treino, mantendo o teste inteiro.

**Por que foi necessária:** a validação da mistura não isola a influência da origem dos dados. O LODO avalia como o modelo treinado nas outras bases se comporta ao receber uma origem que ficou fora daquele treinamento. Isso permite observar diferenças de generalização entre bases, sem depender das marcações inconsistentes de treino e teste dos arquivos.

No LODO, a origem define a divisão; não se utiliza `StratifiedGroupKFold`, pois isso repartiria as bases em vez de reservar uma delas inteira.

## 7. Treinamento e avaliação por fold — `evaluate_folds`

**Alteração:** os dois experimentos compartilham a mesma rotina, reutilizando `train_model`, `predict` e `evaluate_accuracy`. Um novo modelo é treinado em cada fold. Antes disso, são verificados conjuntos vazios, treino com apenas uma classe e grupos presentes simultaneamente no treino e na avaliação.

**Por que foi necessária:** os protocolos devem mudar a divisão dos dados, mantendo o mesmo procedimento de treinamento e cálculo das métricas. As verificações impedem que uma divisão inválida seja avaliada silenciosamente. São registrados tamanhos, exclusões do treino, acertos, erros, acurácia e composição de cada fold.

## 8. Registro dos resultados — `save_fold_results`

**Alteração:** salva as métricas, a média simples das acurácias, o desvio padrão populacional (`ddof=0`), as características utilizadas e a data da execução. Salva também quais imagens participaram de cada conjunto.

**Por que foi necessária:** uma única acurácia esconde diferenças entre folds e bases. O registro permite conferir a composição das divisões e comparar a variação dos resultados. No LODO, cada base tem o mesmo peso na média, independentemente de seu tamanho. O desvio padrão descreve essa variação; não é um intervalo de confiança.

| Arquivo | Conteúdo |
|---|---|
| `results/experiment_groups.csv` | Identificação dos pacientes disponíveis, hashes e grupos por imagem. |
| `results/cv_folds.csv` | Métricas dos cinco folds do experimento A e resumo. |
| `results/lodo_folds.csv` | Métricas dos seis folds do experimento B e resumo. |
| `results/cv_folds_assignments.csv` | Composição dos conjuntos por fold do A. |
| `results/lodo_folds_assignments.csv` | Composição dos conjuntos por fold do B. |

Os CSVs atuais são substituídos a cada execução, em vez de acrescentar linhas ao histórico do protocolo antigo. Para preservar uma execução, seus arquivos devem ser copiados antes da próxima.

## 9. Atualização do `main.py`

**Alteração:** após carregar e unir características e metadata, o fluxo passou a preparar os grupos e executar os experimentos A e B. A chamada à divisão antiga baseada em `train` foi retirada desse fluxo; a função antiga permanece no arquivo, mas não é utilizada pelos novos experimentos.

**Por que foi necessária:** a avaliação passa a seguir os dois protocolos explicitamente definidos, em vez de depender da convenção de nomes de cada base. A pipeline atual também deixa de gerar uma nova versão do antigo `glaucoma_predictions.csv`.

```python
fileCSV = merge_features_with_labels(fileCSV, metadata)
fileCSV = prepare_experiment_groups(fileCSV)

# Experimento A: cinco folds com grupos.
cross_validate_model(fileCSV, features, target)

# Experimento B: uma base inteira no teste por rodada.
leave_one_dataset_out(fileCSV, features, target)
```

Os comandos de execução e de seleção de características continuam os mesmos. `--skip-analysis` reutiliza o CSV de características, mas continua executando a preparação dos grupos e os dois experimentos.

## Problemas encontrados e limitações

### Identificação incompleta de pacientes

Nem todas as bases fornecem um identificador de paciente utilizável. O agrupamento usa essa informação quando ela existe e recupera a identificação da CRFO pelo nome original. Sem essa informação, não é possível garantir que imagens diferentes pertencem a pessoas diferentes. Os identificadores sequenciais de imagens não são interpretados como pacientes sem evidência dessa relação.

### Duplicatas e diferenças de representação

O hash identifica fotografias com dimensões e pixels RGB idênticos, mas uma versão recortada, redimensionada ou com pixels alterados pode receber outra assinatura. Portanto, a verificação de duplicatas exatas não elimina toda possibilidade de imagens relacionadas sem identificação comum.

### Diferenças entre bases

A estratificação organiza a proporção das classes, mas não padroniza a origem das imagens. O experimento A avalia o conjunto combinado; o experimento B reserva uma origem inteira para avaliar a generalização entre bases. Esses protocolos respondem a perguntas diferentes e devem ser interpretados separadamente.

### Limite de iterações da regressão logística

O uso conjunto de características em escalas diferentes pode dificultar o ajuste da regressão logística. O modelo permanece configurado como `LogisticRegression()`, com limite padrão de 100 iterações. Quando o algoritmo atinge esse limite antes de satisfazer o critério de convergência, emite um aviso de que o ajuste pode estar incompleto.

As iterações são etapas de ajuste dos coeficientes dentro de cada treinamento, não imagens ou folds. Aumentar `max_iter` e avaliar padronização com uma `Pipeline` são possibilidades futuras; essas mudanças não foram implementadas. Se houver padronização, ela deve ser ajustada somente no treino de cada fold para evitar vazamento de informação.

### Arquivos gerados e dependências locais

Os arquivos de execução em `results/` e as dependências locais em `.glaucoma/` não fazem parte desta atualização versionada. As dependências necessárias ao projeto estão descritas na seção de instalação. A descrição dos CSVs neste README documenta o comportamento do código, sem incluir esses arquivos no repositório.
