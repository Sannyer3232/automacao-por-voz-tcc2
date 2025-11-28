# src/services/action_service.py
import os
import webbrowser
import pyautogui
import time

class CommandExecutor:
    def __init__(self, config_manager):
        self.config = config_manager
        
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
                pyautogui.hotkey("alt", "f4")
            elif intencao == "NOVA_GUIA":
                pyautogui.hotkey("ctrl", "t")
            elif intencao == "FECHAR_GUIA":
                pyautogui.hotkey("ctrl", "w")
            elif intencao == "ALTERNAR_GUIA_PROXIMA":
                pyautogui.hotkey("ctrl", "tab")
            elif intencao == "PESQUISAR_GOOGLE":
                termo = comando_original.replace("pesquisar sobre", "").replace("buscar por", "").strip()
                pyautogui.hotkey("ctrl", "l")
                time.sleep(0.1)
                pyautogui.write(termo)
                pyautogui.press("enter")
            
            # --- CONTROLE DE TEXTO ---
            elif intencao == "DIGITAR":
                texto = comando_original.replace("digitar", "").replace("escrever", "").strip()
                pyautogui.write(texto)
            elif intencao == "COPIAR":
                pyautogui.hotkey("ctrl", "c")
            elif intencao == "COLAR":
                pyautogui.hotkey("ctrl", "v")
            elif intencao == "SELECIONAR_TUDO":
                pyautogui.hotkey("ctrl", "a")
            elif intencao == "APAGAR":
                pyautogui.press("backspace")
            elif intencao == "CONFIRMAR_ENVIO":
                pyautogui.press("enter")

            # --- AÇÕES DE SISTEMA / ARQUIVOS ---
            elif intencao == "ABRIR_EXPLORADOR":
                os.system("explorer.exe")
            elif intencao == "DELETAR_ARQUIVO":
                pyautogui.press("delete")
            elif intencao == "CRIAR_PASTA":
                pyautogui.hotkey("ctrl", "shift", "n")

            # --- PASTAS DE USUÁRIO ---
            elif intencao == "ABRIR_DOCUMENTOS":
                os.startfile(os.path.expanduser("~/Documents"))
            elif intencao == "ABRIR_DOWNLOADS_PASTA":
                os.startfile(os.path.expanduser("~/Downloads"))
            elif intencao == "ABRIR_IMAGENS":
                os.startfile(os.path.expanduser("~/Pictures"))
            elif intencao == "ABRIR_DESKTOP":
                os.startfile(os.path.expanduser("~/Desktop"))

            # --- AÇÕES DE MÍDIA / VOLUME ---
            elif intencao == "AUMENTAR_VOLUME":
                pyautogui.press("volumeup")
            elif intencao == "DIMINUIR_VOLUME":
                pyautogui.press("volumedown")
            elif intencao == "MUTAR_DESMUTAR":
                pyautogui.press("volumemute")
            elif intencao == "TOCAR_PAUSAR_MUSICA":
                pyautogui.press("playpause")
            elif intencao == "PROXIMA_MUSICA":
                pyautogui.press("nexttrack")
            elif intencao == "MUSICA_ANTERIOR":
                pyautogui.press("prevtrack")

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
                try:
                    os.system("start spotify:") 
                except:
                    self._abrir_programa_caminho("spotify")
            
            # --- GERENCIAMENTO DE JANELAS (NOVO) ---
            elif intencao == "FECHAR_JANELA_ATUAL":
                pyautogui.hotkey("alt", "f4")
            
            elif intencao == "ALTERNAR_JANELA":
                pyautogui.hotkey("alt", "tab")
            elif intencao == "MINIMIZAR_JANELA":
                # Pressionar 'win + down' duas vezes garante que minimize 
                # mesmo se estiver maximizada
                pyautogui.hotkey("win", "down")
                time.sleep(0.1)
                pyautogui.hotkey("win", "down")
                
            elif intencao == "MAXIMIZAR_JANELA":
                pyautogui.hotkey("win", "up")
                
            elif intencao == "RESTAURAR_JANELA":
                # Restaura tamanho original se estiver maximizada ou minimizada
                pyautogui.hotkey("win", "down") 
                # As vezes precisa de win+shift+m dependendo de como foi minimizado, 
                # mas win+down costuma funcionar para 'desmaximizar'
                
            elif intencao == "MOSTRAR_DESKTOP":
                pyautogui.hotkey("win", "d")

            elif intencao == "JANELA_ESQUERDA":
                # Encaixa a janela na metade esquerda da tela
                pyautogui.hotkey("win", "left")
                
            elif intencao == "JANELA_DIREITA":
                # Encaixa a janela na metade direita da tela
                pyautogui.hotkey("win", "right")

            # --- AÇÕES PERSONALIZADAS (CUSTOM) ---
            elif intencao in self.custom_actions:
                acao = self.custom_actions[intencao]
                tipo = acao.get("type")
                valor = acao.get("value")

                print(f"DEBUG: Tentando Custom Action -> Tipo: {tipo} | Valor: {valor}")

                if tipo == "macro":
                    teclas = valor.lower().split("+")
                    pyautogui.hotkey(*teclas)
                
                elif tipo == "programa":
                    # Normaliza barras (converte / para \ no Windows)
                    caminho_exe = os.path.normpath(valor)
                    
                    if os.path.exists(caminho_exe):
                        pasta_do_programa = os.path.dirname(caminho_exe)
                        nome_exe = os.path.basename(caminho_exe)
                        
                        print(f"DEBUG: Arquivo encontrado. Entrando em: {pasta_do_programa}")
                        try:
                            # Muda o diretório para a pasta do jogo/app (Crucial para emuladores e jogos)
                            original_cwd = os.getcwd() 
                            os.chdir(pasta_do_programa) 
                            os.startfile(nome_exe)
                            # Restaura o diretório original do Python (rápido, para não afetar o resto)
                            time.sleep(0.1) 
                            os.chdir(original_cwd) 
                            print("DEBUG: Executado com sucesso.")
                        except Exception as e:
                            print(f"ERRO ao tentar abrir com chdir: {e}")
                            # Fallback: Tenta abrir direto
                            os.startfile(caminho_exe)
                    else:
                        print(f"ERRO: O Python não encontrou o arquivo neste caminho: {caminho_exe}")
                        print("DICA: Verifique se o caminho está escrito corretamente e se o arquivo .exe existe.")

        except Exception as e:
            print(f"Erro CRÍTICO ao executar comando {intencao}: {e}")

    def _abrir_programa_caminho(self, nome_chave):
        self.comandos_programas = self.config.get_paths()
        caminho = self.comandos_programas.get(nome_chave)
        
        if caminho and os.path.exists(caminho):
            os.startfile(caminho)
        else:
            try:
                cmd = caminho if caminho else f"{nome_chave}.exe"
                os.startfile(cmd)
            except Exception as e:
                print(f"Falha ao abrir programa '{nome_chave}': {e}")