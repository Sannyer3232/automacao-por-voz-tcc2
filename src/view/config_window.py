# src/view/config_window.py
import customtkinter as ctk
from tkinter import filedialog # Para abrir seletor de arquivos

class ConfigWindow(ctk.CTkToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config_manager = controller.config
        
        self.title("Configurações do Sistema")
        self.geometry("600x500")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        self._setup_ui()

    def _setup_ui(self):
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
        # --- Seleção de Modo ---
        self.modo_var = ctk.StringVar(value="existente")

        lbl_modo = ctk.CTkLabel(self.tab_comandos, text="O que você deseja fazer?", font=("Arial", 12, "bold"))
        lbl_modo.pack(pady=(10, 5))

        frame_radios = ctk.CTkFrame(self.tab_comandos, fg_color="transparent")
        frame_radios.pack()
        
        rad_existente = ctk.CTkRadioButton(frame_radios, text="Adicionar frase a comando existente", 
                                         variable=self.modo_var, value="existente", command=self._atualizar_form)
        rad_existente.pack(side="left", padx=10)
        
        rad_novo = ctk.CTkRadioButton(frame_radios, text="Criar NOVO comando (Macro/App)", 
                                    variable=self.modo_var, value="novo", command=self._atualizar_form)
        rad_novo.pack(side="left", padx=10)

        # --- Frame Dinâmico (Muda conforme seleção) ---
        self.frame_form = ctk.CTkFrame(self.tab_comandos)
        self.frame_form.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._atualizar_form()

    def _atualizar_form(self):
        # Limpa o frame
        for widget in self.frame_form.winfo_children():
            widget.destroy()

        modo = self.modo_var.get()

        if modo == "existente":
            self._form_existente()
        else:
            self._form_novo()

    def _form_existente(self):
        lbl = ctk.CTkLabel(self.frame_form, text="Selecione a Ação:")
        lbl.pack(pady=5)
        
        cmds = list(self.config_manager.get_commands().keys())
        cmds.sort()
        self.option_intent = ctk.CTkOptionMenu(self.frame_form, values=cmds)
        self.option_intent.pack(pady=5)

        lbl2 = ctk.CTkLabel(self.frame_form, text="Nova Frase de Voz:")
        lbl2.pack(pady=5)
        self.entry_frase = ctk.CTkEntry(self.frame_form, placeholder_text="Ex: 'Abrir o navegadorzão'")
        self.entry_frase.pack(pady=5, fill="x", padx=20)

        btn = ctk.CTkButton(self.frame_form, text="Salvar e Treinar", command=self._salvar_existente, fg_color="green")
        btn.pack(pady=20)

    def _form_novo(self):
        # Nome da intenção interna
        lbl_id = ctk.CTkLabel(self.frame_form, text="Nome do Comando (ID interno):")
        lbl_id.pack(pady=2)
        self.entry_id = ctk.CTkEntry(self.frame_form, placeholder_text="Ex: ABRIR_MEU_JOGO")
        self.entry_id.pack(pady=2, fill="x", padx=20)

        # Frase
        lbl_frase = ctk.CTkLabel(self.frame_form, text="Frase de Voz:")
        lbl_frase.pack(pady=2)
        self.entry_frase_nova = ctk.CTkEntry(self.frame_form, placeholder_text="Ex: 'Iniciar meu jogo'")
        self.entry_frase_nova.pack(pady=2, fill="x", padx=20)

        # Tipo de Ação
        lbl_tipo = ctk.CTkLabel(self.frame_form, text="Tipo de Ação:")
        lbl_tipo.pack(pady=5)
        
        self.tipo_acao_var = ctk.StringVar(value="programa")
        frm_tipo = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        frm_tipo.pack()
        
        ctk.CTkRadioButton(frm_tipo, text="Abrir Programa", variable=self.tipo_acao_var, value="programa", command=self._toggle_input_valor).pack(side="left", padx=10)
        ctk.CTkRadioButton(frm_tipo, text="Macro de Teclas", variable=self.tipo_acao_var, value="macro", command=self._toggle_input_valor).pack(side="left", padx=10)

        # Input do Valor (Dinâmico)
        self.frame_valor = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        self.frame_valor.pack(fill="x", pady=10)
        self._toggle_input_valor()

        btn = ctk.CTkButton(self.frame_form, text="Criar Comando e Treinar", command=self._salvar_novo, fg_color="blue")
        btn.pack(pady=10)

    def _toggle_input_valor(self):
        for w in self.frame_valor.winfo_children(): w.destroy()
        
        tipo = self.tipo_acao_var.get()
        if tipo == "programa":
            self.entry_valor = ctk.CTkEntry(self.frame_valor, placeholder_text="Caminho do .exe")
            self.entry_valor.pack(side="left", fill="x", expand=True, padx=(20, 5))
            btn_busca = ctk.CTkButton(self.frame_valor, text="Buscar...", width=60, command=self._buscar_arquivo)
            btn_busca.pack(side="right", padx=(5, 20))
        else: # macro
            self.entry_valor = ctk.CTkEntry(self.frame_valor, placeholder_text="Ex: ctrl+c, alt+tab, win+d")
            self.entry_valor.pack(fill="x", padx=20)

    def _buscar_arquivo(self):
        path = filedialog.askopenfilename(filetypes=[("Executáveis", "*.exe"), ("Todos", "*.*")])
        if path:
            self.entry_valor.delete(0, "end")
            self.entry_valor.insert(0, path)

    # --- Callbacks dos Switches (FALTAVAM ESTES MÉTODOS) ---
    def _toggle_feedback(self):
        estado = bool(self.switch_feedback.get())
        self.config_manager.set_preference("feedback_voz", estado)
        # Atualiza o serviço de áudio em tempo real
        self.controller.feedback.set_ativo(estado)

    def _toggle_startup(self):
        estado = bool(self.switch_startup.get())
        self.config_manager.set_preference("iniciar_com_windows", estado)

    # --- Processamento Auxiliar ---
    def _processar_frases(self, texto_bruto):
        """
        Converte 'Frase 1, Frase 2' em ['Frase 1', 'Frase 2'].
        Remove aspas extras caso o usuário tenha digitado.
        """
        texto_limpo = texto_bruto.replace("'", "").replace('"', "")
        lista_frases = [p.strip() for p in texto_limpo.split(',') if p.strip()]
        return lista_frases

    # --- Salvamento ---
    def _salvar_existente(self):
        intent = self.option_intent.get()
        texto_bruto = self.entry_frase.get()
        
        if not texto_bruto.strip(): return
        
        frases = self._processar_frases(texto_bruto)
        
        self.config_manager.add_command(intent, frases)
        self.controller.reload_model()
        
        self.entry_frase.delete(0, "end")
        print(f"Adicionadas {len(frases)} frases a {intent}")

    def _salvar_novo(self):
        intent_id = self.entry_id.get().upper().strip().replace(" ", "_")
        texto_bruto = self.entry_frase_nova.get()
        tipo = self.tipo_acao_var.get()
        valor = self.entry_valor.get().strip()

        if not intent_id or not texto_bruto or not valor:
            print("Preencha todos os campos!")
            return

        frases = self._processar_frases(texto_bruto)

        # 1. Salva a lógica
        self.config_manager.add_custom_action(intent_id, tipo, valor)
        
        # 2. Salva as frases
        self.config_manager.add_command(intent_id, frases)
        
        # 3. Retreina
        self.controller.reload_model()
        
        # Limpa
        self.entry_id.delete(0, "end")
        self.entry_frase_nova.delete(0, "end")
        self.entry_valor.delete(0, "end")
        print(f"Novo comando {intent_id} criado com {len(frases)} frases!")