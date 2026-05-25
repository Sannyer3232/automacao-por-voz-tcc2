# Assistente de Automação por Voz (TCC)

Este projeto é um assistente virtual desktop desenvolvido em Python para automação de tarefas através de comandos de voz. Ele utiliza técnicas de Processamento de Linguagem Natural (NLP) para interpretar intenções e simular ações no sistema operacional Windows.

## 🚀 Funcionalidades

- **Controle de Navegador:** Abrir/fechar navegador, gerenciar guias (nova, fechar, alternar), pesquisar no Google, atualizar página e navegação por links.
- **Automação do Windows:** Abrir explorador de arquivos, documentos, downloads, imagens, calculadora e bloco de notas.
- **Edição de Texto:** Comandos para copiar, colar, recortar, selecionar tudo, apagar e digitar texto por voz.
- **Controle de Mídia:** Abrir Spotify, play/pause, próxima música, música anterior e controle de volume (aumentar, diminuir, mutar).
- **Gerenciamento de Janelas:** Minimizar, maximizar, restaurar, alternar janelas (Alt+Tab) e organizar janelas nos cantos da tela.
- **Interface Gráfica:** Dashboard moderno construído com `customtkinter` para monitoramento de logs em tempo real e configurações.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** [Python 3.10+](https://www.python.org/)
- **Interface Gráfica:** `customtkinter`
- **Reconhecimento de Voz:** `SpeechRecognition` (Google Web Speech API)
- **Síntese de Voz (TTS):** `pyttsx3`
- **Processamento de Linguagem Natural:** `scikit-learn` (TF-IDF + MultinomialNB), `nltk`
- **Automação de Teclado/Mouse:** `pyautogui`, `pyperclip`

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

2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv .venv
   # No Windows:
   .venv\Scripts\activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute a aplicação:**
   ```bash
   python main.py
   ```

## ⚙️ Como funciona a interpretação?

O sistema não utiliza apenas comparação de strings exatas. Ele passa por um pipeline de NLP:
1. **Captação:** O áudio é convertido em texto.
2. **Processamento:** O texto é limpo e vetorizado.
3. **Classificação:** Um modelo de Machine Learning treinado com as frases em `config/comandos.json` identifica a intenção (`intent`) com maior probabilidade.
4. **Execução:** O serviço de ações executa o comando correspondente à intenção identificada.

## 📊 Métricas

Para avaliar a precisão do modelo, você pode executar os testes de benchmark localizados na pasta `tests/`:
```bash
python tests/benchmark_metrics.py
```

---
*Este projeto foi desenvolvido como parte de um Trabalho de Conclusão de Curso (TCC).*