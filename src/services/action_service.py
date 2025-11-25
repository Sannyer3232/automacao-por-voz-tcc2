# src/services/action_service.py
import os
import webbrowser
import pyautogui
import time
import pyperclip

class CommandExecutor:
    def __init__(self):
        # Mapeamento simples de programas. 
        # Idealmente isso viria do ConfigManager, mas pode manter hardcoded por enquanto.
        self.comandos_programas = {
            "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
            "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
            "bloco de notas": "notepad.exe",
            "calculadora": "calc.exe",
            "spotify": "spotify.exe" 
        }

    def executar(self, intencao, comando_original):
        """Direciona a intenção para a função específica."""
        print(f"Executando ação: {intencao}")
        
        try:
            # Navegação Web
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
                # Remove gatilhos comuns para pegar só o termo
                termo = comando_original.replace("pesquisar sobre", "").replace("buscar por", "").strip()
                pyautogui.hotkey("ctrl", "l")
                pyautogui.write(termo)
                pyautogui.press("enter")
            
            # Controle de Texto
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

            # Ações de Sistema / Arquivos
            elif intencao == "ABRIR_EXPLORADOR":
                os.system("explorer.exe")
            elif intencao == "DELETAR_ARQUIVO":
                pyautogui.press("delete")
            elif intencao == "CRIAR_PASTA":
                pyautogui.hotkey("ctrl", "shift", "n")

            # Ações de Mídia / Volume
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

            # Abrir Programas
            elif intencao == "ABRIR_BLOCO_DE_NOTAS":
                os.startfile("notepad.exe")
            elif intencao == "ABRIR_CALCULADORA":
                os.startfile("calc.exe")
            elif intencao == "ABRIR_WORD":
                self._abrir_programa_caminho("word")
            elif intencao == "ABRIR_EXCEL":
                self._abrir_programa_caminho("excel")

        except Exception as e:
            print(f"Erro ao executar comando {intencao}: {e}")

    def _abrir_programa_caminho(self, nome_chave):
        caminho = self.comandos_programas.get(nome_chave)
        if caminho and os.path.exists(caminho):
            os.startfile(caminho)
        else:
            print(f"Programa {nome_chave} não encontrado no caminho configurado.")