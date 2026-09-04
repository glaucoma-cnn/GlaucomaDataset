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

O resultado é armazenado em um `DataFrame` do Pandas.

---

## `reporters/Reporters.py`

Responsável por armazenar e apresentar os resultados produzidos pela análise.

São gerados dois tipos de arquivo:

* **CSV:** contém os resultados individuais de cada imagem.
* **TXT:** contém um resumo estatístico da execução.

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
pip install pillow numpy pandas
```

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
glaucoma_flag
```

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

# Próximas extensões possíveis

Esta etapa representa apenas a primeira parte do pipeline planejado.

Futuramente poderão ser adicionadas outras características morfológicas, como:

* perímetro do disco e do copo;
* circularidade;
* excentricidade;
* razão de aspecto;
* diâmetros horizontal e vertical;
* Vertical Cup-to-Disc Ratio;
* características do neuroretinal rim;
* propriedades de elipses ajustadas às máscaras.

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

# GlaucomaDataset
