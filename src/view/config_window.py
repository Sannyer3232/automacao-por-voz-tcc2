# src/view/config_window.py
import customtkinter as ctk
from tkinter import messagebox

class ConfigWindow(ctk.CTkToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config_manager = controller.config
        
        self.title("Configurações do Sistema")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # Garante que a janela fique no topo
        self.attributes("-topmost", True)

        self._setup_ui()

    def _setup_ui(self):
        # Criação das Abas
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_geral = self.tabview.add("Geral")
        self.tab_comandos = self.tabview.add("Comandos")

        self._setup_tab_geral()
        self._setup_tab_comandos()

    def _setup_tab_geral(self):
        # --- Switch Feedback de Voz ---
        feedback_val = self.config_manager.get_preference("feedback_voz")
        self.switch_feedback = ctk.CTkSwitch(
            self.tab_geral, 
            text="Feedback de Voz Ativo",
            command=self._toggle_feedback
        )
        if feedback_val: self.switch_feedback.select()
        self.switch_feedback.pack(pady=20, padx=20, anchor="w")

        # --- Switch Iniciar com Windows ---
        startup_val = self.config_manager.get_preference("iniciar_com_windows")
        self.switch_startup = ctk.CTkSwitch(
            self.tab_geral, 
            text="Iniciar com o Windows",
            command=self._toggle_startup
        )
        if startup_val: self.switch_startup.select()
        self.switch_startup.pack(pady=20, padx=20, anchor="w")

        # Nota explicativa
        lbl_info = ctk.CTkLabel(
            self.tab_geral, 
            text="Nota: As alterações são salvas automaticamente.",
            font=("Arial", 10), text_color="gray"
        )
        lbl_info.pack(side="bottom", pady=10)

    def _setup_tab_comandos(self):
        lbl_title = ctk.CTkLabel(self.tab_comandos, text="Adicionar Novo Comando", font=("Arial", 14, "bold"))
        lbl_title.pack(pady=10)

        # Dropdown para escolher a Intenção (Ação)
        self.comandos_existentes = list(self.config_manager.get_commands().keys())
        self.comandos_existentes.sort()
        
        self.option_intent = ctk.CTkOptionMenu(self.tab_comandos, values=self.comandos_existentes)
        self.option_intent.set("Selecione a Ação")
        self.option_intent.pack(pady=5, padx=20, fill="x")

        # Entrada de texto para a nova frase
        self.entry_frase = ctk.CTkEntry(self.tab_comandos, placeholder_text="Digite a nova frase (ex: 'Abrir o navegadorzão')")
        self.entry_frase.pack(pady=10, padx=20, fill="x")

        # Botão Salvar
        self.btn_add = ctk.CTkButton(
            self.tab_comandos, 
            text="Adicionar e Treinar",
            command=self._adicionar_comando,
            fg_color="green"
        )
        self.btn_add.pack(pady=20)

    # --- Callbacks ---
    def _toggle_feedback(self):
        estado = bool(self.switch_feedback.get())
        self.config_manager.set_preference("feedback_voz", estado)
        # Atualiza o serviço de áudio em tempo real
        self.controller.feedback.set_ativo(estado)

    def _toggle_startup(self):
        estado = bool(self.switch_startup.get())
        self.config_manager.set_preference("iniciar_com_windows", estado)

    def _adicionar_comando(self):
        intencao = self.option_intent.get()
        frase = self.entry_frase.get().strip()

        if intencao == "Selecione a Ação" or not frase:
            print("Erro: Selecione uma ação e digite uma frase.")
            return

        # 1. Salva no JSON
        self.config_manager.add_command(intencao, frase)
        
        # 2. Solicita ao Controller para retreinar o modelo TF-IDF
        self.controller.reload_model()
        
        # Feedback visual
        self.entry_frase.delete(0, "end")
        msg = f"Frase '{frase}' adicionada à ação '{intencao}'.\nModelo retreinado com sucesso!"
        print(msg)
        # Em uma aplicação real, usaria messagebox, mas print serve para o log do terminal/interface