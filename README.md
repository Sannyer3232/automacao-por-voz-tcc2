# Assistente de Comandos — versão oficina

Assistente de comandos por voz em Python para o terminal do Linux. Ele recebe um comando falado (de um áudio gravado ou do microfone) ou digitado, transcreve a fala com o Vosk, identifica a intenção com NLTK + TF-IDF e executa a ação correspondente no computador.

É o mesmo núcleo de interpretação do TCC *Assistente de Automação por Voz*, sem a interface gráfica. A pasta `audios/` traz um comando gravado para cada intenção, então o reconhecimento de voz funciona mesmo em máquinas sem microfone. A versão completa do TCC está nas branches `main` (Windows) e `linux`.

- **Formato:** 1 encontro de 4 h, hands-on. O instrutor programa no projetor e a turma acompanha, completando as lacunas (`TODO`) do código junto com ele. Todos saem com o assistente funcionando.
- **Requisitos:** Linux (Ubuntu 22.04 ou 24.04), Python 3.10 a 3.14, noções básicas de Python. Não precisa de GPU, modelo de IA pré-treinado nem chave de API.
- **Dependências:** versões fixadas em `requirements.txt` (testadas com Python 3.10, 3.12 e 3.14).

## Instalação

```bash
# IMPORTANTE: rode este comando ANTES do pip install. Ele instala pacotes do Ubuntu
# (não do Python) e exige sudo, ou seja, senha de administrador. Sem eles, o venv não
# é criado, o PyAudio não compila e o pip install -r requirements.txt falha inteiro.
# Em laboratório, peça para a equipe de TI rodar este comando antes da aula.
sudo apt install python3-venv espeak-ng mbrola mbrola-br4 portaudio19-dev python3-dev build-essential

git clone -b oficina <url-do-repositorio> assistente-oficina
cd assistente-oficina
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python baixar_modelo_vosk.py        # modelo de voz offline em português (~31 MB)
python verificar_ambiente.py        # tudo verde ou só avisos nos opcionais
```

### Pacotes do sistema (`sudo apt install`)

Esses pacotes são do Ubuntu, não do Python: o `pip` não consegue instalá-los, e o `apt` exige senha de administrador. **Em laboratório, peça para a equipe de TI instalá-los antes da aula.** Sem eles, o `pip install -r requirements.txt` falha por inteiro.

| Pacote | Por que é necessário |
| --- | --- |
| `python3-venv` | O Python do Ubuntu não vem com o módulo de ambiente virtual; sem ele, `python3 -m venv .venv` falha |
| `portaudio19-dev` | O PyAudio (microfone) não tem versão pronta para Linux e é compilado na instalação, usando a PortAudio, biblioteca de áudio do sistema |
| `python3-dev` | Arquivos de cabeçalho do Python, também usados na compilação do PyAudio |
| `build-essential` | Compilador `gcc`, necessário para compilar o PyAudio |
| `espeak-ng` | Motor de síntese de voz, que transforma as respostas do assistente em fala |
| `mbrola`, `mbrola-br4` | Voz feminina brasileira, mais natural que a do eSpeak. Sem ela, o assistente usa a variante feminina do eSpeak |

Na primeira execução, o NLTK baixa os dados `stopwords` e `rslp`, o que precisa de internet uma única vez. Sem internet, rode antes `python -m nltk.downloader stopwords rslp` numa máquina conectada.

## Estrutura

```text
├── verificar_ambiente.py   # checklist da máquina
├── testar_microfone.py     # teste do reconhecimento de voz (microfone -> texto -> intenção)
├── baixar_modelo_vosk.py   # baixa o modelo offline em português (~31 MB)
├── audios/                 # um comando gravado (.wav) por intenção, para testar a voz sem microfone
├── exercicios/             # código com as lacunas TODO: é aqui que você trabalha
└── solucao/                # mesmo código, completo
```

As duas pastas têm os mesmos arquivos:

| Arquivo | O que faz |
| --- | --- |
| `comandos.json` | Intenções, frases de exemplo, ação e resposta |
| `preprocessamento.py` | Minúsculas, tokenização, stopwords e stemming (RSLP) |
| `classificador.py` | TF-IDF + similaridade do cosseno, com limiar de confiança |
| `acoes.py` | Executa a ação no Linux (programa, atalho, pesquisa, sistema) |
| `voz.py` | Falar (eSpeak + MBROLA) e ouvir um áudio gravado ou o microfone (SpeechRecognition + Vosk) |
| `avaliar.py` | Acurácia, F1 macro e matriz de confusão em `testes.csv` |
| `main.py` | Laço principal |

Rode sempre de dentro da pasta em que está trabalhando:

```bash
cd exercicios
python main.py --simular     # mostra as ações em vez de executá-las
python main.py               # executa de verdade
python main.py --voz         # fala as respostas
python main.py --audio ../audios --simular   # ouve todos os comandos gravados, em ordem
python main.py --audio ../audios/03_pesquisar.wav   # ouve um comando gravado
python main.py --microfone   # ouve pelo microfone (volta para o teclado se falhar)
python main.py --microfone --mic 3 --reconhecedor google   # escolhe o microfone e o reconhecedor
python main.py --limiar 0.3  # muda o score mínimo para aceitar um comando
python avaliar.py            # mede o classificador
```

## Roteiro (4 h, programando juntos)

Cada TODO segue o mesmo ritmo: o instrutor explica o conceito, escreve o código no projetor, a turma digita junto e todos conferem o resultado antes de seguir.

| Horário | Etapa | Arquivo | O que fazer | Como conferir |
| --- | --- | --- | --- | --- |
| 0:00 – 0:15 | Abertura | `verificar_ambiente.py` | Apresentação e diagnóstico da máquina | tudo verde ou só avisos nos opcionais |
| 0:15 – 0:30 | Demonstração | `solucao/` | Ver o assistente completo funcionando e entender o fluxo frase → intenção → ação | — |
| 0:30 – 1:10 | TODO 1 | `preprocessamento.py` | Minúsculas, remoção de pontuação e tokenização | `python preprocessamento.py` |
| | TODO 2 | `preprocessamento.py` | Remoção de stopwords | "por favor abre aba agora" vira `['abr', 'aba']` |
| | TODO 3 | `preprocessamento.py` | Stemming com `RSLPStemmer` | "abrir", "abre" e "abrindo" viram `abr` |
| 1:10 – 1:40 | TODO 4 | `classificador.py` | `prever()`: vetorizar, calcular o cosseno, aplicar o limiar | `python classificador.py` mostra intenção e score |
| 1:40 – 2:00 | TODO 5 | `avaliar.py` | Calcular as métricas e testar os limiares 0,3 / 0,5 / 0,7 | comparar com o 0,94 do TCC |
| 2:00 – 2:15 | Intervalo | | | |
| 2:15 – 2:45 | TODO 6 | `acoes.py` | Implementar os tipos `programa` e `atalho` | `nova aba` abre uma aba no Firefox (ou mostra a simulação) |
| 2:45 – 3:20 | TODO 7 | `comandos.json` | Criar uma intenção nova juntos e, em seguida, cada um cria a sua | `ajuda` lista as novas e `avaliar.py` continua passando |
| 3:20 – 3:45 | TODO 8 | `voz.py` | 8a: falar (`--voz`). 8b: transcrever os áudios gravados (`--audio ../audios`). 8c (extra): microfone | o assistente fala e entende os 14 áudios |
| 3:45 – 4:00 | Fechamento | — | Discutir os limites do TF-IDF (veja "Para discutir em aula") | — |

**Ficou para trás?** Copie o arquivo correspondente de `solucao/` para `exercicios/` e siga com a turma.

**Se o tempo apertar:** no TODO 7, faça só a intenção em conjunto. No TODO 8, faça o 8a e o 8b e mostre o microfone no projetor.

## Criando comandos (TODO 7)

Cada intenção do `comandos.json` tem frases de exemplo, uma ação e uma resposta:

```json
"abrir_terminal": {
    "frases": ["abrir o terminal", "abre o console", "quero a linha de comando"],
    "acao": {"tipo": "programa", "comando": ["gnome-terminal"]},
    "resposta": "Abrindo o terminal."
}
```

Tipos de ação:

| Tipo | Campos | Exemplo |
| --- | --- | --- |
| `programa` | `comando`: lista de argumentos | `["gnome-calculator"]`, `["xdg-open", "~"]` |
| `atalho` | `teclas`: teclas do PyAutoGUI | `["ctrl", "t"]` |
| `pesquisa` | `gatilhos`: o termo é o texto depois do último gatilho | "pesquisar **receita de bolo**" |
| `sistema` | `comando`: comando fixo | `["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+10%"]` |
| `interno` | `nome`: `ajuda` ou `sair` | tratado no `main.py` |

O modelo é retreinado sozinho na próxima execução sempre que o `comandos.json` for alterado. Para ver se as frases novas não confundiram as antigas, rode `python avaliar.py` de novo.

**Segurança:** nenhuma ação monta um comando a partir do texto digitado. O termo de pesquisa só entra na URL, e sempre escapado.

## Reconhecimento de voz

O microfone é capturado com a biblioteca **SpeechRecognition**, e a fala é transcrita por um de dois motores:

| Motor | Internet | Chave de API | Download | Observação |
| --- | --- | --- | --- | --- |
| `vosk` (principal) | não | não | modelo pequeno em português (~31 MB) | Roda na CPU, offline |
| `google` | sim | não | nada | Google Web Speech, gratuito. Um pouco mais preciso |
| `auto` (padrão) | — | — | — | Usa o Vosk e, se ele ou o modelo não estiverem instalados, o Google |

Não há Whisper nem outro modelo pesado: tudo roda em CPU comum.

Baixe o modelo do Vosk uma vez, com internet (na raiz do projeto):

```bash
python baixar_modelo_vosk.py
```

### Áudios gravados (sem microfone)

A pasta `audios/` tem um comando gravado para cada intenção (WAV, 16 kHz, mono), numerado na ordem da demonstração. O `13_fora_do_dominio.wav` deve ser rejeitado, e o `14_sair.wav` encerra o assistente.

```bash
cd solucao
python main.py --audio ../audios --simular                 # todos os áudios, em ordem
python main.py --audio ../audios/02_nova_aba.wav --voz     # um áudio, com resposta falada
python main.py --audio ../audios --reconhecedor google     # compara com o Google (precisa de internet)
```

Com o Vosk, os 14 áudios caem na intenção certa. Alguns saem com pequenos erros de transcrição ("abri a calculadora", "a baixa o volume"), e mesmo assim o classificador acerta. Isso rende uma boa discussão em aula.

Os áudios da pasta foram gerados por síntese de voz. Para trocar por gravações suas (ou da turma), grave em WAV 16 kHz mono e mantenha o número no início do nome:

```bash
arecord -f S16_LE -r 16000 -c 1 -d 4 audios/15_minha_frase.wav
```

### Testando o microfone

O `testar_microfone.py` mostra cada etapa: calibração do ruído, gravação, transcrição pelos dois motores (com o tempo de cada um) e a intenção identificada.

```bash
python testar_microfone.py --listar          # lista os microfones e seus índices
python testar_microfone.py                   # grava com o microfone padrão
python testar_microfone.py --mic 3           # grava com o microfone de índice 3
python testar_microfone.py --arquivo x.wav   # testa com um áudio gravado, sem microfone
```

A gravação fica salva em `gravacao.wav` (ouça com `aplay gravacao.wav`), o que ajuda a descobrir se o problema é o microfone ou o reconhecimento.

### Roteiro do teste no laboratório

1. `python verificar_ambiente.py`: confira a sessão (X11 ou Wayland), a internet e os programas.
2. Confira se a instalação do `requirements.txt` e o `python baixar_modelo_vosk.py` rodaram sem erro.
3. `python testar_microfone.py --listar` e anote o índice do fone com microfone.
4. `python testar_microfone.py --mic <índice>` com alguns comandos: compare Google e Vosk.
5. Desligue a internet e repita: o Vosk deve continuar funcionando (o Google vai mostrar erro de conexão).
6. `cd solucao && python main.py --microfone --voz --mic <índice>`: teste o assistente completo.

## Problemas comuns

- **Os atalhos não funcionam:** o PyAutoGUI só envia teclas numa sessão **X11**. No Wayland, padrão do Ubuntu, o assistente avisa e simula os atalhos. Para usá-los de verdade, saia da sessão e escolha "Ubuntu on Xorg" na tela de login.
- **"Programa não encontrado":** ajuste o `comando` da intenção no `comandos.json` para um programa instalado (ex: `gedit` no lugar de `gnome-text-editor`).
- **O volume não muda ("'pactl' não encontrado"):** instale com `sudo apt install pulseaudio-utils` ou troque, no `comandos.json`, para o `wpctl` do PipeWire: `["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "10%+"]` (e `"10%-"` para diminuir).
- **`--voz` não fala:** instale o `espeak-ng`. Sem ele, o assistente avisa e segue só com texto.
- **A voz saiu robótica/masculina:** falta a voz MBROLA (`sudo apt install mbrola mbrola-br4`). Teste com `espeak-ng -v mb-br4 -s 150 "Abrindo o navegador."`. Para mudar a velocidade, altere `VELOCIDADE` no `voz.py`.
- **O Vosk erra muitas palavras:** compare com `python testar_microfone.py`, que mostra também o resultado do Google. Se houver internet, `--reconhecedor google` é um pouco mais preciso.
- **`--microfone` não ouve:** rode `python testar_microfone.py --listar` e passe o índice certo com `--mic`. Confira também o volume de entrada nas configurações de som do Ubuntu.
- **"Não ouvi nada" o tempo todo ou cortes no meio da frase:** o ambiente pode estar barulhento. O `testar_microfone.py` mostra o limiar de energia calibrado; acima de ~4000, use fone com microfone ou reduza o ganho.
- **Falha ao instalar o PyAudio:** faltam pacotes do sistema (`sudo apt install portaudio19-dev python3-dev build-essential`).

## Para discutir em aula

O classificador da `solucao/` atinge 0,93 de acurácia e 0,92 de F1 macro em `testes.csv` com limiar 0,5. Os erros que sobram mostram os limites do TF-IDF:

- **"me conta uma piada" vira `abrir_calculadora`:** a palavra "conta" aparece em "preciso fazer uma conta". O TF-IDF compara palavras, não sentido.
- **"mais uma guia" é confundido com `fechar_aba`:** sobra pouca informação depois de remover as stopwords. Por isso "mais" foi retirada da lista de stopwords do NLTK, junto com "não": sem ela, "mais volume" e "menos volume" ficariam quase iguais.
- **O stemmer não é perfeito:** o RSLP reduz "procura" a `proc`, mas "procurar" a `procur`, e "comandos" a `com`.
- **O Vosk não conhece todas as palavras:** o modelo pequeno não tem "aba" no vocabulário. "Próxima aba" vira só "próxima", e o assistente acerta pelas outras palavras. Já "próxima guia" é transcrito inteiro. Bom exemplo de como o reconhecimento de fala e o classificador se complementam, e de por que vale ter sinônimos nas frases de exemplo.
- **O limiar é uma troca:** abaixo de 0,5 o assistente aceita mais frases, inclusive erradas. Acima, prefere dizer que não entendeu. Compare `--limiar 0.3`, `0.5` e `0.7` no `avaliar.py`.
