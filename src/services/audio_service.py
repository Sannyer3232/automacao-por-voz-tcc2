# src/services/audio_service.py
import pyttsx3

class AudioFeedback:
    def __init__(self):
        self.ativo = True
    
    def set_ativo(self, estado: bool):
        self.ativo = estado

    def falar(self, texto):
        """
        Sintetiza a voz. Cria uma nova instância a cada chamada
        para evitar travamentos de loop do pyttsx3 em threads.
        """
        if not self.ativo:
            return

        try:
            engine = pyttsx3.init()
            # Configurações opcionais de voz podem vir aqui
            engine.say(texto)
            engine.runAndWait()
        except Exception as e:
            print(f"Erro ao sintetizar áudio: {e}")