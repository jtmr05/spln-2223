# SPLN TP2 - WHISPER

No âmbito da UC de Scripting no Processamento de Linguágem Natural do
perfil de Engenharia de Linguagens, integrado no Mestrado em Engenharia
Informática da Universidade do Minho, é-nos proposto desenvolver um
programa, com o auxílio de um conjunto de ferramentas disponibilizadas,
permita utilizar conhecimento adquirido nas aulas, ou extenda o mesmo.
Desse modo, a nossa escolha consistiu no sistema remoto de transcrição
de áudio, o Whisper, da OpenAI, seguindo as orientações dos docentes. O
programa é capaz de receber pedidos do cliente, coloca-los numa fila de
espera, e posteriormente o resultado será enviado ao cliente. A
biblioteca *noisereduce* de Python é utilizada de modo a reduzir o ruído
de áudio, de modo a puder ser usado com muitos mais ficheiros de áudio
reais, e não apenas ficheiros limpos gravados em estudios . O programa
provê ainda a utilização de um instalador, de modo a facilitar todo o
processo de utilização, sob a forma de *Docker container*.

Tendo em conta os pontos enunciados anteriormente, o presente documento
visa focar-se na explicação do trabalho desenvolvido, demonstrando as
funcionalidades e recursos extra disponíveis.

# Bibliotecas Usadas

## whisper

O [Whisper](https://pypi.org/project/openai-whisper/#description) é um
modelo de reconhecimento de áudio *speech to text* de propósito geral. É
treinado num grande conjunto de dados de áudio diversificado e também é
um modelo multi-tarefa capaz de realizar reconhecimento de áudio
multilingue, tradução de fala e identificação de idioma.

Um modelo de sequência para sequência Transformer é treinado em várias
tarefas de processamento de fala, incluindo reconhecimento de fala
multilingue, tradução de fala, identificação de idioma falado e deteção
de atividade de voz. Essas tarefas são representadas conjuntamente como
uma sequência de tokens a serem previstos pelo descodificador,
permitindo que um único modelo substitua muitas etapas de um pipeline de
processamento de fala tradicional. O formato de treino multi-tarefa usa
um conjunto de *tokens* especiais que atuam como especificadores de
tarefa ou alvos de classificação.

## noisereduce

A biblioteca [noisereduce](https://pypi.org/project/noisereduce) é uma
ferramenta em Python usada para reduzir o ruído em sinais de áudio,
melhorando a sua qualidade para o processamento de linguagem. As
ferramentas desta biblioteca utilizam técnicas avançadas de
processamento de sinais para modelar e estimar o ruído presente no
áudio, permitindo a sua supressão de forma precisa. Ao remover o ruído
indesejado, a biblioteca contribui para transcrições mais precisas,
melhor eficácia em modelos de *machine learning*. A redução de ruído
proporciona clareza à fala, eliminando distrações e facilitando um
processamento de áudio mais eficiente e confiável. A biblioteca
*noisereduce* desempenha um papel importante na preparação e
pré-processamento de sinais de áudio para tarefas de processamento de
linguagem, melhorando a qualidade e a utilidade dos resultados obtidos,
de modo a puder ser usada com melhor exatidão nos resultados
provenientes da utilização do Whisper.

## argparse

O [argparse](https://pypi.org/project/argparse/) é uma biblioteca muito
utilizada em Python para análise de linha de comando. Permite aos
programadores definir facilmente argumentos e opções que podem ser
passados quando o programa é executado via linha de comandos. Durante as
aulas, o *argparse* foi utilizado para simplificar a interação com o
código Python.

Com o *argparse*, é possível adicionar argumentos personalizados, como a
especificação da linguagem, para tornar o programa mais flexível e
adaptável a diferentes situações. Deste modo, o *script* correspondente
ao cliente pode especificar uma série de opções, nomeadamente a opção de
reduzir o ruído com recurso ao módulo *noisereduce*, a linguagem do
áudio a ser enviado (se omitido, será detetado automaticamente), o
*sample rate* a usar, e o nome do ficheiro de saída, para além dos
argumentos obrigatórios (o endereço do servidor e o nome do ficheiro de
entrada).

Ao utilizar o argparse em conjunto com as opções de especificação de
linguagem, redução de ruído com *noisereduce* e taxa de amostragem, é
possível criar uma interface mais intuitiva e personalizável para
programas Python, permitindo que os utilizadores definam configurações e
comportamentos do programa de forma flexível e conveniente.

## pickle

O módulo *pickle* da *standard library* do Python permite a serialização
e desserialização de objetos Python, possibilitando salvar e recuperar
objetos complexos em um formato binário persistente. É comummente
utilizada para armazenar dados de forma reutilizável e eficiente.

Na solução final, o áudio passa por tratamento e processamento,
incluindo a possível aplicação de técnicas como redução de ruído
utilizando a biblioteca *noisereduce*. Em seguida, o áudio tratado é
convertido num formato adequado para uso com o Whisper.

Uma abordagem comum é representar o áudio tratado como um *numpy array*,
permitindo a sua manipulação eficiente. Esse *array* é então serializado
utilizando o *pickle* para ser armazenado em formato binário
persistente.

Dessa forma, o áudio tratado e serializado pode ser posteriormente
utilizado pelo Whisper, um sistema de reconhecimento automático de fala
(ASR), que converte a fala em texto de forma precisa e automática.

# Solução Desenvolvida

O programa está estruturado em classes e métodos que são responsáveis
por diferentes funcionalidades. A classe principal, denominada
WhisperServer, é responsável por gerir a conexão com os clientes e
processar as suas solicitações de transcrição de áudio, através de
*sockets* TCP.

A solução desenvolvida possui um conjunto de constantes que definem o
tamanho do *buffer* de leitura/gravação, o caminho do arquivo
temporário, o tamanho inteiro em *bytes* (para efeitos protocolares) e o
tempo limite para conexões. Essas constantes foram configuradas de
acordo com as necessidades do servidor e podem ser ajustadas conforme a
aplicação.

Além disso, foram implementadas funções auxiliares num arquivo de
utilitários (utils.py), que fornecem funcionalidades adicionais para o
servidor, como a escrita e leitura confiável de dados de/para os
clientes, sendo estas funções igualmente úteis ao *script* do cliente.

## Cliente

O programa cliente é responsável por se conectar ao servidor Whisper e
transcrever um arquivo de áudio. O *argparse* é utilizado para analisar
os argumentos fornecidos na linha de comando. O *pickle* é utilizado
para serializar o áudio fornecido pelo utilizador, enviado através de
uma instância de um *socket*, que estabelece a comunicação com o
servidor.

Após a análise dos argumentos e a obtenção do nome final do arquivo com
a ajuda da função *change_file_ext*, a conexão com o servidor Whisper é
iniciada. Um socket é criado para se conectar ao servidor utilizando o o
nome do *host* e a porta fornecidos na linha de comando.

O programa cliente lê uma mensagem do servidor, envia as opções
escolhidas (como idioma, tamanho do arquivo, opção de redução de ruído,
etc.) sob a forma de um dicionário, utilizando a serialização *pickle* e
envia o conteúdo do arquivo de áudio em vários fragmentos (*chunks*).

Com base na resposta do servidor, o programa cliente define o caminho do
arquivo de saída, que conterá a transcrição do áudio enviado. O nome do
arquivo pode ser fornecido como argumento ou baseado no nome do arquivo
de entrada. O programa cria as diretorias necessárias e guarda o
resultado num ficheiro de texto.

Após a conclusão da transcrição e receção do arquivo resultante, a
conexão com o servidor é encerrada. Este último irá então tratar do
pedido seguinte, se este existir. O programa cliente também permite
terminar de forma graciosa, tal como o servidor, permitindo ao utlizador
interromper a execução pressionando Ctrl + C, exibindo uma mensagem
adequada.

## Servidor

O servidor é responsável por receber um arquivo de áudio enviado pelo
cliente e processá-lo utilizando a biblioteca Whisper para realizar a
transcrição.

Esse módulo utiliza várias bibliotecas, incluindo o *noisereduce* para
redução de ruído, o *pickle* para serialização de objetos, além dos
módulos *socket* para comunicação de rede e o *threading* para execução
paralela (uma *thread* aceita pedidos e coloca-os na fila de espera, e
outra trata esses pedidos sequencialmente).

A classe WhisperServer contém métodos para inicialização, aguardar novos
pedidos, manipular as pedidos recebidas dos clientes e realizar a
transformação do áudio em texto. Inicialmente, o modelo Whisper é
configurado e uma fila (queue) é criada para armazenar os pedidos em
espera. Em seguida, o servidor é iniciado na porta especificada e,
apenas após isso, a transcrição do áudio é iniciada.

Os métodos *\_listen* e *\_handle_requests* são responsáveis por receber
novas comunicações e manipulá-las. Eles recebem as informações do
cliente, processam o áudio, realizam a transcrição e enviam o resultado
como texto. O recebimento de novos clientes é gerido num outro fio de
execução, evitando esperas e reduzindo a probabilidade de ocorrer um
tempo limite de conexão.

Em resumo, o servidor Whisper recebe solicitações de transcrição de
áudio, processa o áudio utilizando o modelo especificado e retorna a
transcrição aos clientes. Ele pode ser executado na linha de comando,
fornecendo o nome do modelo *Hugging Face*, o *hostname* e a porta como
argumentos.

## Instalador

Com o objetivo de aumentar a produtividade e facilitar a utilização do
programa desenvolvido, foi criado um *Dockerfile*, que permite gerar uma
imagem, e consequentemente correr instâncias dessa imagem, que
correspodem a um servidor Whisper num ambiente Python. O *container*
utiliza a versão 3 do Python e define três variáveis de ambiente:
WHISPER_MODEL, WHISPER_HOSTNAME e WHISPER_PORT, com os valores por
omissão \"small\", \"localhost\" e \"8888\", respetivamente.

Os ficheiros necessários para o servidor são copiados para a pasta
\"/server\", que é definido como a *workdir* dentro do *container*. Essa
diretoria inclui o módulo do servidor e um módulo com funções úteis.

Além disso, a ferramenta *FFmpeg* é instalada no *container* para
permitir a manipulação dos ficheiros de áudio, sendo uma dependência do
Whisper. Através do comando *pip*, que é atualizado no início do
processo, são instaladas as bibliotecas *openai-whisper* e
*noisereduce*, que são necessárias para o funcionamento do servidor.

Em resumo, o *Dockerfile* define o processo de configuração do ambiente
necessário para correr o servidor, isolando todas as dependências
necessárias para executar o mesmo. Ao iniciar o *container*, o servidor
é executado com as configurações fornecidas, proporcionando um ambiente
pré-configurado e fácil de utilizar.

# Guia de Utilização

A mensagem de ajuda gerado pelo módulo *argparse* para o servidor é a
seguinte:

    usage: whisper-server [-h] model hostname port

    Whisper audio transcription server

    positional arguments:
      model       HuggingFace model to be used
      hostname
      port

    options:
      -h, --help  show this help message and exit 

Como se pode observar, para correr o servidor basta especificar os
argumentos posicionais necessários, concretamente o modelo a usar, o
*hostname* e a porta onde o servidor deverá escutar. Como exemplo, o
mesmo podia ser iniciado da seguinte forma:

    $ ./server.py large 0.0.0.0 8888

Por outro lado, correndo $./client.py --help$ obtemos:

    usage: whisper-client [-h] [--language LANGUAGE] 
    [--noise-reduction | --no-noise-reduction | -n] 
    [--sample-rate SAMPLE_RATE] [--output OUTPUT] filename hostname port

    Transcribe an audio file

    positional arguments:
      filename
      hostname              The hostname of the Whisper server instance
      port                  The port on which the server is listening

    options:
      -h, --help            show this help message and exit
      --language LANGUAGE, -l LANGUAGE
                            Define the audio language
      --noise-reduction, --no-noise-reduction, -n
                            Perform a noise reduction on the audio file before
                            transcribing
      --sample-rate SAMPLE_RATE, -s SAMPLE_RATE
      --output OUTPUT, -o OUTPUT
                            Ouput path

Para além dos argumentos obrigatórios, pode se especificar a linguagem
do áudio a enviar, o *sample rate*, o nome do ficheiro de saída, e se se
pretende realizar redução de ruído. Dessa forma, o cliente poderia
submeter um pedido da seguinte forma:

    $ ./client.py o_meu_audio.mp4 0.0.0.0 8888 -o o_meu_texto.txt 
        -l Portuguese -n
    $ ./client.py o_meu_audio.mp3 0.0.0.0 8888
    $ ./client.py o_meu_outro_audio.mp4 0.0.0.0 7345 -s 16000
        --output foo/bar/baz/file.txt

# Conclusão

A implementação do servidor Whisper para transcrição de áudio revelou-se
uma solução altamente eficiente e funcional. O programa foi desenvolvido
com o objetivo de receber arquivos de áudio, processá-los utilizando o
modelo Whisper e retornar transcrições precisas aos clientes. Ao longo
do desenvolvimento, foram utilizadas diversas bibliotecas e módulos,
além de técnicas avançadas de processamento de áudio, consolidando o
conhecimento adquirido na unidade curricular.

O servidor Whisper demonstrou um desempenho notável na transcrição de
arquivos de áudio, lidando com múltiplas solicitações de forma
simultânea. Através do uso de threads, foi possível processar as
solicitações de forma eficiente, garantindo resultados rápidos e
precisos.

Um aspeto importante a destacar é a aplicação de medidas de segurança e
confiabilidade. Foram implementados mecanismos de validação de opções,
tratamento de erros e um *timeout* para evitar bloqueios prolongados.
Isso contribui para a robustez do servidor e assegura uma experiência
confiável aos clientes. Em termos protocolares, há o cuidado de
estabelecer que os tamanhos das estruturas (quer dos ficheiros, que do
dicionário das opções) são propriamente comunicados antes de serem
enviados, sendo por isso necessário estabelecer um tamanho máximo para
estes inteiros, estabelecido em 64 octetos.

A nível de trabalho futuro, o aprimoramento e a otimização do servidor
Whisper devem ser uma prioridade. Isso pode envolver a implementação de
recursos adicionais, como suporte a diferentes modelos de transcrição e
aprimoramentos na redução de ruído, bem como a inclusão de uma
estimativa do tempo necessário para processar um ficheiro. Com essas
melhorias, o servidor Whisper poderá se consolidar como uma ferramenta
ainda mais poderosa e versátil no processamento de transcrições de
áudio. Por outro lado, incluir mais opções do lado cliente também seria
interessante (i.e. escrever o *output* num outro formato).
