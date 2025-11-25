import customtkinter as ctk
from src.controller.main_controller import AssistantController
from src.view.config_window import ConfigWindow # <--- Importe a nova classe

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Assistente Virtual TCC - Sannyer")
        self.geometry("600x500")
        
        # Guarda referência da janela de config para não abrir múltiplas
        self.toplevel_window = None 

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        self.label_status = ctk.CTkLabel(self.header_frame, text="Status: Parado", font=("Arial", 16, "bold"))
        self.label_status.pack(pady=10)

        self.btn_toggle = ctk.CTkButton(self.header_frame, text="Iniciar Escuta", command=self.toggle_listening)
        self.btn_toggle.pack(pady=10)

        # Log Area
        self.log_box = ctk.CTkTextbox(self, state="disabled")
        self.log_box.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Footer
        self.btn_config = ctk.CTkButton(self, text="Configurações", command=self.open_config)
        self.btn_config.grid(row=2, column=0, padx=20, pady=20)

        # Controller
        self.controller = AssistantController(self.update_log)

    def update_log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def toggle_listening(self):
        if not self.controller.is_running:
            self.controller.start_listening()
            self.label_status.configure(text="Status: Ouvindo...", text_color="green")
            self.btn_toggle.configure(text="Parar Escuta", fg_color="red")
        else:
            self.controller.stop_listening()
            self.label_status.configure(text="Status: Parado", text_color="white")
            self.btn_toggle.configure(text="Iniciar Escuta", fg_color="blue")

    def open_config(self):
        # Lógica para abrir a janela apenas se ela não estiver aberta
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ConfigWindow(self, self.controller)  # Passa o controller
        else:
            self.toplevel_window.focus()

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()