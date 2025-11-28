# src/controller/main_controller.py
import threading
import time
from src.services.speech_service import SpeechRecognizer
from src.services.nlp_service import IntentInterpreter
from src.services.action_service import CommandExecutor
from src.services.audio_service import AudioFeedback
from src.model.config_manager import ConfigManager

class AssistantController:
    def __init__(self, ui_callback_log, app_close_callback=None):
        self.log_callback = ui_callback_log 
        self.close_callback = app_close_callback # Callback para fechar a janela
        
        self.config = ConfigManager()
        self.nlp = IntentInterpreter(self.config)
        self.speech = SpeechRecognizer() 
        self.executor = CommandExecutor(self.config)
        self.feedback = AudioFeedback()
        
        self.is_running = False
        self.listen_thread = None

        # Carrega estado inicial do feedback de voz
        voz_ativa = self.config.get_preference("feedback_voz")
        self.feedback.set_ativo(voz_ativa if voz_ativa is not None else True)

    def reload_model(self):
        """Re-treina o modelo NLP com os novos comandos salvos."""
        self.log_callback("Atualizando modelo de linguagem...")
        self.nlp.train_or_load_model(force_retrain=True)
        self.log_callback("Modelo atualizado! Novo comando pronto para uso.")
        self.feedback.falar("Configuração atualizada.")

    def start_listening(self):
        if self.is_running: return

        self.is_running = True
        self.listen_thread = threading.Thread(target=self._loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        
        self.log_callback("Sistema iniciado.")
        # Feedback de áudio restaurado (RF-1)
        self.feedback.falar("Sistema iniciado. Aguardando comandos.")

    def stop_listening(self):
        self.is_running = False
        self.log_callback("Sistema pausado.")

    def _loop(self):
        while self.is_running:
            # Tenta ouvir. Se não tiver mic, retorna "ERRO_MIC"
            audio_text = self.speech.ouvir_comando()
            
            # --- Lógica de Espera do Microfone (Loop Resiliente) ---
            if audio_text == "ERRO_MIC":
                self.log_callback("AVISO: Microfone desconectado. Aguardando conexão...")
                time.sleep(3) # Espera 3 segundos antes de tentar de novo
                # Tenta reconectar o hardware
                self.speech.verificar_status()
                continue # Volta para o início do while sem parar o programa

            if audio_text:
                self.log_callback(f"Ouvi: {audio_text}")
                intent, score = self.nlp.predict(audio_text)
                
                if intent:
                    # --- Lógica de Encerramento (RF-4) ---
                    if intent == "ENCERRAR":
                        self.log_callback(f"Intenção: {intent} - Encerrando...")
                        self.feedback.falar("Encerrando aplicação. Até logo.")
                        self.is_running = False
                        time.sleep(1) # Dá tempo de terminar a fala
                        if self.close_callback:
                            self.close_callback() # Fecha a janela gráfica
                        return # Sai da thread

                    # Lógica Normal
                    self.log_callback(f"Intenção: {intent} ({score:.2f})")
                    self.feedback.falar("Entendido")
                    self.executor.executar(intent, audio_text)
                else:
                    self.log_callback("Comando não entendido.")