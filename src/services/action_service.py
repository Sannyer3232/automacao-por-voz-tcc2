# src/services/action_service.py
import os
import shlex
import shutil
import subprocess
import webbrowser
import time

from src.services.input_service import KeyboardController

class CommandExecutor:
    def __init__(self, config_manager):
        self.config = config_manager
        self.teclado = KeyboardController()

        # Carrega os caminhos do JSON.
        self.comandos_programas = self.config.get_paths()
        self.custom_actions = self.config.get_custom_actions()

    def executar(self, intencao, comando_original):
        """Direciona a intenção para a função específica."""
        print(f"Executando ação: {intencao}")

        # Recarrega configurações (para pegar alterações no JSON em tempo real)
        self.custom_actions = self.config.get_custom_actions()
        self.comandos_programas = self.config.get_paths()

        try:
            # --- NAVEGAÇÃO WEB ---
            if intencao == "ABRIR_NAVEGADOR":
                webbrowser.open("https://www.google.com")
            elif intencao == "FECHAR_NAVEGADOR":
                self.teclado.hotkey("alt", "f4")
            elif intencao == "NOVA_GUIA":
                self.teclado.hotkey("ctrl", "t")
            elif intencao == "FECHAR_GUIA":
                self.teclado.hotkey("ctrl", "w")
            elif intencao == "ALTERNAR_GUIA_PROXIMA":
                self.teclado.hotkey("ctrl", "tab")
            elif intencao == "PESQUISAR_GOOGLE":
                termo = comando_original.replace("pesquisar sobre", "").replace("buscar por", "").strip()
                self.teclado.hotkey("ctrl", "l")
                time.sleep(0.1)
                self.teclado.write(termo)
                self.teclado.press("enter")

            # --- CONTROLE DE TEXTO ---
            elif intencao == "DIGITAR":
                texto = comando_original.replace("digitar", "").replace("escrever", "").strip()
                self.teclado.write(texto)
            elif intencao == "COPIAR":
                self.teclado.hotkey("ctrl", "c")
            elif intencao == "COLAR":
                self.teclado.hotkey("ctrl", "v")
            elif intencao == "SELECIONAR_TUDO":
                self.teclado.hotkey("ctrl", "a")
            elif intencao == "APAGAR":
                self.teclado.press("backspace")
            elif intencao == "CONFIRMAR_ENVIO":
                self.teclado.press("enter")

            # --- AÇÕES DE SISTEMA / ARQUIVOS ---
            elif intencao == "ABRIR_EXPLORADOR":
                self._abrir_com_xdg(os.path.expanduser("~"))
            elif intencao == "DELETAR_ARQUIVO":
                # No Nautilus, Delete move o arquivo para a lixeira
                self.teclado.press("delete")
            elif intencao == "CRIAR_PASTA":
                self.teclado.hotkey("ctrl", "shift", "n")

            # --- PASTAS DE USUÁRIO ---
            # As pastas são localizadas via xdg-user-dir (ex: ~/Documentos em pt-BR)
            elif intencao == "ABRIR_DOCUMENTOS":
                self._abrir_com_xdg(self._pasta_usuario("DOCUMENTS", "~/Documentos"))
            elif intencao == "ABRIR_DOWNLOADS_PASTA":
                self._abrir_com_xdg(self._pasta_usuario("DOWNLOAD", "~/Downloads"))
            elif intencao == "ABRIR_IMAGENS":
                self._abrir_com_xdg(self._pasta_usuario("PICTURES", "~/Imagens"))
            elif intencao == "ABRIR_DESKTOP":
                self._abrir_com_xdg(self._pasta_usuario("DESKTOP", "~/Área de trabalho"))

            # --- AÇÕES DE MÍDIA / VOLUME ---
            elif intencao == "AUMENTAR_VOLUME":
                self._volume(["set-volume", "-l", "1.0", "@DEFAULT_AUDIO_SINK@", "5%+"], "volumeup")
            elif intencao == "DIMINUIR_VOLUME":
                self._volume(["set-volume", "@DEFAULT_AUDIO_SINK@", "5%-"], "volumedown")
            elif intencao == "MUTAR_DESMUTAR":
                self._volume(["set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"], "volumemute")
            elif intencao == "TOCAR_PAUSAR_MUSICA":
                self._midia("play-pause", "playpause")
            elif intencao == "PROXIMA_MUSICA":
                self._midia("next", "nexttrack")
            elif intencao == "MUSICA_ANTERIOR":
                self._midia("previous", "prevtrack")

            # --- ABRIR PROGRAMAS (DINÂMICO) ---
            elif intencao == "ABRIR_BLOCO_DE_NOTAS":
                self._abrir_programa_caminho("bloco de notas")
            elif intencao == "ABRIR_CALCULADORA":
                self._abrir_programa_caminho("calculadora")
            elif intencao == "ABRIR_WORD":
                self._abrir_programa_caminho("word")
            elif intencao == "ABRIR_EXCEL":
                self._abrir_programa_caminho("excel")

            # --- SPOTIFY ---
            elif intencao == "ABRIR_SPOTIFY":
                self._abrir_programa_caminho("spotify")

            # --- GERENCIAMENTO DE JANELAS (atalhos padrão do GNOME) ---
            elif intencao == "FECHAR_JANELA_ATUAL":
                self.teclado.hotkey("alt", "f4")

            elif intencao == "ALTERNAR_JANELA":
                self.teclado.hotkey("alt", "tab")
            elif intencao == "MINIMIZAR_JANELA":
                self.teclado.hotkey("super", "h")

            elif intencao == "MAXIMIZAR_JANELA":
                self.teclado.hotkey("super", "up")

            elif intencao == "RESTAURAR_JANELA":
                # Desfaz a maximização / encaixe lateral
                self.teclado.hotkey("super", "down")

            elif intencao == "MOSTRAR_DESKTOP":
                self.teclado.hotkey("super", "d")

            elif intencao == "JANELA_ESQUERDA":
                # Encaixa a janela na metade esquerda da tela
                self.teclado.hotkey("super", "left")

            elif intencao == "JANELA_DIREITA":
                # Encaixa a janela na metade direita da tela
                self.teclado.hotkey("super", "right")

            # --- AÇÕES PERSONALIZADAS (CUSTOM) ---
            elif intencao in self.custom_actions:
                acao = self.custom_actions[intencao]
                tipo = acao.get("type")
                valor = acao.get("value")

                print(f"DEBUG: Tentando Custom Action -> Tipo: {tipo} | Valor: {valor}")

                if tipo == "macro":
                    teclas = valor.lower().split("+")
                    self.teclado.hotkey(*teclas)

                elif tipo == "programa":
                    self._executar_programa(valor)

        except Exception as e:
            print(f"Erro CRÍTICO ao executar comando {intencao}: {e}")

    def _abrir_programa_caminho(self, nome_chave):
        self.comandos_programas = self.config.get_paths()
        comando = self.comandos_programas.get(nome_chave) or nome_chave
        self._executar_programa(comando)

    def _executar_programa(self, valor):
        """
        Aceita um caminho de executável/AppImage, um arquivo .desktop
        ou um comando do PATH (com argumentos, ex: 'libreoffice --writer').
        """
        caminho = os.path.expanduser(valor)

        if os.path.isfile(caminho):
            if caminho.endswith(".desktop"):
                self._iniciar(["gio", "launch", caminho])
            elif os.access(caminho, os.X_OK):
                # Executa a partir da pasta do programa (crucial para emuladores e jogos)
                self._iniciar([caminho], cwd=os.path.dirname(caminho))
            else:
                # Arquivo comum: abre com o aplicativo padrão
                self._abrir_com_xdg(caminho)
            return

        partes = shlex.split(valor)
        if partes and shutil.which(partes[0]):
            self._iniciar(partes)
        else:
            print(f"ERRO: Programa não encontrado: {valor}")
            print("DICA: Informe um comando do PATH, um arquivo .desktop ou o caminho de um executável.")

    def _iniciar(self, args, cwd=None):
        # Sessão própria para o programa não morrer junto com o assistente
        subprocess.Popen(args, cwd=cwd, start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _abrir_com_xdg(self, alvo):
        self._iniciar(["xdg-open", alvo])

    def _pasta_usuario(self, nome_xdg, padrao):
        try:
            pasta = subprocess.run(["xdg-user-dir", nome_xdg], capture_output=True,
                                   text=True, check=True).stdout.strip()
            if pasta and os.path.isdir(pasta):
                return pasta
        except (OSError, subprocess.CalledProcessError):
            pass
        return os.path.expanduser(padrao)

    def _volume(self, args_wpctl, tecla_fallback):
        """Controla o volume via PipeWire (wpctl); sem ele, usa a tecla multimídia."""
        if shutil.which("wpctl"):
            subprocess.run(["wpctl", *args_wpctl], check=False)
        else:
            self.teclado.press(tecla_fallback)

    def _midia(self, acao_playerctl, tecla_fallback):
        """Controla players via MPRIS (playerctl); sem ele, usa a tecla multimídia."""
        if shutil.which("playerctl"):
            subprocess.run(["playerctl", acao_playerctl], check=False)
        else:
            self.teclado.press(tecla_fallback)
