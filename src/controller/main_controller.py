import threading
from src.services.speech_service import SpeechRecognizer
from src.services.nlp_service import IntentInterpreter
from src.services.action_service import CommandExecutor
from src.services.audio_service import AudioFeedback
from src.model.config_manager import ConfigManager

class AssistantController:
    def __init__(self, ui_callback_log):
        self.log_callback = ui_callback_log 
        self.config = ConfigManager()
        self.nlp = IntentInterpreter(self.config)
        self.speech = SpeechRecognizer() 
        self.executor = CommandExecutor()
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
        # ... (MANTER O CÓDIGO EXISTENTE AQUI) ...
        # Copie o código do start_listening da resposta anterior
        if self.is_running: return
        if not self.speech.verificar_status():
            self.log_callback("ERRO: Microfone não detectado!")
            return

        self.is_running = True
        self.listen_thread = threading.Thread(target=self._loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        self.log_callback("Sistema iniciado.")

    def stop_listening(self):
        self.is_running = False
        self.log_callback("Sistema pausado.")

    def _loop(self):
        # ... (MANTER O CÓDIGO EXISTENTE AQUI) ...
        while self.is_running:
            audio_text = self.speech.ouvir_comando()
            
            if audio_text == "ERRO_MIC":
                self.log_callback("ALERTA: Microfone desconectado!")
                self.is_running = False
                break

            if audio_text:
                self.log_callback(f"Ouvi: {audio_text}")
                intent, score = self.nlp.predict(audio_text)
                
                if intent:
                    self.log_callback(f"Intenção: {intent} ({score:.2f})")
                    self.feedback.falar("Entendido")
                    self.executor.executar(intent, audio_text)
                else:
                    self.log_callback("Comando não entendido.")