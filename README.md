vessel_Analysis

Pipeline de análise de segmentação do disco optico e copo optico retinianos para triagem de glaucoma.

Calcula a discrepância de pixels entre as máscaras do disc e cup e sinaliza os casos que ultrapassam um limiar configurável como possível glaucoma.



Estrutura

Main.py - Roda a pipeline, chama todas as pastas (ponto de entrada)

config/Settings.py - Monta todos os caminhos e qualquer parâmetro de análise - se é possível indicativo de glaucoma ou não - é configurado nessa parte

readers/Readers.py - Abre as pastas - Dataset baixado localmente, código no support_Code- e monta os pares do cup - disc utilizando o ip presente na frente de cada imagem.

analyzers/optic_Analysis.py - o Coração principal da primeira parte do projeto, aqui que calcula a discrepância entre os pixels brancos do par disc/cup.

reporters/Reporters.py - Armazena todos os resultados em CSV e TXT.

utils/Utils.py - Monta o caminho de cada pasta aqui.


Para Iniciar 

Precisa instalar todas as dependências

pip install pillow numpy pandas

precisa configurar o caminho do dataset dependendo da sua máquina 
Abra o config/Settings e em DATASET_ROOT ajuste de acordo com a sua pasta.

Para executar - python GlaucomaDataset/main.py

ATENÇÃO *** ao baixar o Dataset do kaggleHub ele normalmente duplica cada pasta de imagens e não é interressante mudar a estrutura no qual foi baixada para não dar conflito no proprio site da kaggle, por cauda disso, em Settings eu coloquei para acessar as pastas como "optic-cup/optic-cup" (ex) para conseguir acessar corretamente. Se o seu dataset instalado não possuir essa duplicata, desconsidere e apague para teste em seu computador.


Destrinchando as configurações - 
DATASET_ROOT - Caminho das pastas de onde o DATASET está armazenado.

OPTIC_DISC_FOLDER_NAME - O nome da subpasta com as imagens do optic_disc (desconsidere se você baixou o dataset localmente-ja configurado)

OPTIC_CUP_FOLDER_NAME - O nome da subpasta com as imagens do optic_cup (Desconsidere se você baixou localmente - já configurado)

OUTPUT_DIR  - pasta executada automaticamente quando rodar o código - para armazenar os arquivos CSV e/ou TXT.

GLAUCOMA_DISCREPANCY_THRESHOLD_PCT - Porcentagem de discrepância para sinalizar de possivel glaucoma (ATENÇÃO -Desativado- conversar esse parametro com o Lucas)


Fluxo da pipeline - 


main
|
|
|--utils - Responsável por montar os caminhos da veia e artéria a partir do settings.py.
|
|
|-- GlaucomaBenchmarkReader.load_pairs() - no Readers.py
    -- Pareia as imagens do optic_disc e optic_cup pelo seu nome
|
|
|-- OpticPairAnalyzer.analyze(pairs) - no analyzers
|   --agora, depois de montar o pares essa função é responsável, em cada par: 
|       --count_pixels() -abrir a imagem, jogar em um array numpy e contar os pixels ( todos que não são pretos)  e 
|       calcular o ratio, abs_diff, disc_pct, predominance, glaucoma_flag
|        esperado retornar um Dataframe
|-- reporters - salva os resultados em CSV e TXT

formula usada para calcular a divisão é a
disc_pct = |optic_cup_pixels - optic_disc_pixels| / max(optic_cup_pixels,optic_disc_pixels) × 100

Na pratica,oque essa fórmula faz? 

1- ela pega a diferença de pixels não-pretos entre artéria e a veia (|optic_cup_pixels- optic_disc_pixels|)

2- pega o maior valor de pixels entre o cup e disc ( max(ptic_cup_pixels,optic_disc_pixels)) - porque? se pegassémos uma imagem só, ou o cup ou o disc, pode ser dividido por um numero muito pequeno em comparação, que aumentaria o resultado de uma forma que não é conveniente para a conta,por isso sempre dividimos pelo maior para ter uma porcentagem entre 0% e 100%

3- Divide a diferença entre a quantidade de pixels da diferença dividido pelo maior numero de pixels

4- multiplica por 100% para oferecer uma porcentagem de desbalanceamento.

5- Armazena no disc_pct que será sinalizado quando a sua porcentagem for > GLAUCOMA_DISCREPANCY_THRESHOLD_PCT


Para adicionar um Script futuro - razão do copo óptico e disco optico, analíse do full-fundus, etc.

se precisar de um novo cálculo, o nome da pasta deve ser imagem_analizada_Analysis (igual o optic_Analysis)

se precisar abrir mais pastas (oque claramente vamos precisar), renomeie o Readers.py para o nome_da_pasta_Readers.py

caso precisemos de um novo ponto de entrada da pipeline nomeie os mains de acordo com a sua entrada de dados.

        

    "# GlaucomaDataset" 
"# GlaucomaDataset" 
