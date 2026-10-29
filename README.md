# Assistente de Automação por Voz (TCC)

Este projeto é um assistente virtual desktop desenvolvido em Python para automação de tarefas através de comandos de voz. Ele utiliza técnicas de Processamento de Linguagem Natural (NLP) para interpretar intenções e simular ações no sistema operacional.

> **Branch `linux`:** esta versão é adaptada para Linux (testada como alvo no Ubuntu com GNOME, em Wayland ou X11). A versão original para Windows está na branch `main`.

## 🚀 Funcionalidades

- **Controle de Navegador:** Abrir/fechar navegador, gerenciar guias (nova, fechar, alternar), pesquisar no Google, atualizar página e navegação por links.
- **Automação do Sistema:** Abrir o gerenciador de arquivos, documentos, downloads, imagens, calculadora e editor de texto.
- **Edição de Texto:** Comandos para copiar, colar, recortar, selecionar tudo, apagar e digitar texto por voz.
- **Controle de Mídia:** Abrir Spotify, play/pause, próxima música, música anterior e controle de volume (aumentar, diminuir, mutar).
- **Gerenciamento de Janelas:** Minimizar, maximizar, restaurar, alternar janelas (Alt+Tab) e encaixar janelas nas laterais da tela (atalhos padrão do GNOME).
- **Interface Gráfica:** Dashboard moderno construído com `customtkinter` para monitoramento de logs em tempo real e configurações.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** [Python 3.10+](https://www.python.org/)
- **Interface Gráfica:** `customtkinter`
- **Reconhecimento de Voz:** `SpeechRecognition` (Google Web Speech API)
- **Síntese de Voz (TTS):** `pyttsx3`
- **Processamento de Linguagem Natural:** `scikit-learn` (TF-IDF + MultinomialNB), `nltk`
- **Automação de Teclado:** `ydotool` (Wayland) ou `pyautogui` (X11)
- **Integração com o sistema:** `xdg-open`, `wpctl` (PipeWire), `playerctl` (opcional), autostart XDG

## 📂 Estrutura do Projeto

```text
├── main.py                 # Ponto de entrada da aplicação
├── src/
│   ├── view/               # Interfaces gráficas (Janela principal e configurações)
│   ├── controller/         # Lógica de integração entre UI e Serviços
│   ├── services/           # Núcleo de processamento (NLP, Áudio, Ações)
│   └── model/              # Gerenciamento de configurações e dados
├── config/                 # Arquivos JSON de mapeamento de comandos
├── data/                   # Armazenamento do modelo de ML treinado
├── tests/                  # Scripts de benchmark e métricas de desempenho
└── requirements.txt        # Dependências do projeto
```

## 🔧 Instalação e Execução

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/usuario/automacao-por-voz-tcc2.git
   cd automacao-por-voz-tcc2
   ```

2. **Instale as dependências do sistema (Ubuntu/Debian):**
   ```bash
   sudo apt install python3-venv python3-tk portaudio19-dev espeak-ng ydotool wl-clipboard xclip playerctl
   ```
   - `portaudio19-dev`: necessário para compilar o `pyaudio` (microfone).
   - `espeak-ng`: motor de voz usado pelo `pyttsx3` no Linux.
   - `ydotool`: simula o teclado em sessões **Wayland** (padrão do Ubuntu). Em sessões X11 o `pyautogui` é usado automaticamente.
   - `wl-clipboard` / `xclip`: usados para digitar textos com acento (á, ç, õ...), que são inseridos via área de transferência (Ctrl+V) em Wayland / X11.
   - `playerctl` (opcional): controle de mídia via MPRIS; sem ele, são usadas as teclas multimídia.

3. **Configure o ydotool (somente Wayland):**
   O `ydotool` precisa do daemon `ydotoold` rodando e de acesso ao `/dev/uinput`:
   ```bash
   sudo usermod -aG input $USER          # depois faça logout/login
   ydotoold &                            # ou configure como serviço do systemd --user
   ```

4. **Crie e ative um ambiente virtual:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

5. **Instale as dependências Python:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Execute a aplicação (a partir da raiz do projeto):**
   ```bash
   python main.py
   ```

### Programas e ações personalizadas

Os programas abertos por voz ficam em `config/config_usuario.json`, na seção `paths`. Cada valor pode ser um comando do PATH (ex: `gnome-calculator`, `libreoffice --writer`), um arquivo `.desktop` ou o caminho de um executável/AppImage. O mesmo vale para as ações personalizadas do tipo `programa`. Em macros, use `super` (ou `win`) para a tecla do sistema, ex: `super+d`.

## ⚙️ Como funciona a interpretação?

O sistema não utiliza apenas comparação de strings exatas. Ele passa por um pipeline de NLP:
1. **Captação:** O áudio é convertido em texto.
2. **Processamento:** O texto é limpo e vetorizado.
3. **Classificação:** O texto é vetorizado com TF-IDF (treinado com as frases em `config/comandos.json`) e comparado por similaridade do cosseno; a intenção (`intent`) mais similar acima do limiar de confiança é escolhida.
4. **Execução:** O serviço de ações executa o comando correspondente à intenção identificada.

## 📊 Métricas

Para avaliar a precisão do modelo, você pode executar os testes de benchmark localizados na pasta `tests/`:
```bash
python tests/benchmark_metrics.py
```

---
*Este projeto foi desenvolvido como parte de um Trabalho de Conclusão de Curso (TCC).*