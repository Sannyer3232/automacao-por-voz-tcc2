# src/services/speech_service.py
import speech_recognition as sr

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
        # Tenta conectar silenciosamente ao iniciar. 
        # Se falhar, o programa continua rodando, mas sem microfone.
        self._conectar_hardware()

    def _conectar_hardware(self):
        """Tenta inicializar o objeto Microfone."""
        try:
            self.microphone = sr.Microphone()
            return True
        except OSError:
            self.microphone = None
            return False

    def verificar_status(self):
        """Retorna True se o microfone estiver pronto, False caso contrário."""
        if self.microphone:
            return True
        # Se não tiver microfone, tenta conectar agora (caso o usuário tenha plugado depois)
        return self._conectar_hardware()

    def ouvir_comando(self):
        """
        Ouve o microfone e retorna o texto transcrito ou None.
        Retorna uma string especial "ERRO_MIC" se não houver hardware.
        """
        # Verifica hardware antes de tentar ouvir
        if not self.verificar_status():
            return "ERRO_MIC"

        with self.microphone as source:
            try:
                # Ajuste rápido de ruído
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Ouve o áudio (timeout curto para a interface não congelar muito tempo)
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
                
                # Transcreve usando Google API
                comando = self.recognizer.recognize_google(audio, language="pt-BR")
                return comando.lower()
                
            except sr.WaitTimeoutError:
                return None # Silêncio
            except sr.UnknownValueError:
                return None # Não entendeu
            except sr.RequestError as e:
                print(f"Erro na API de voz: {e}")
                return None
            except Exception as e:
                print(f"Erro genérico no reconhecimento: {e}")
                return None

    def ouvir_confirmacao(self):
        if not self.verificar_status():
            return False

        with self.microphone as source:
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=4, phrase_time_limit=3)
                resposta = self.recognizer.recognize_google(audio, language="pt-BR").lower()
                
                if "sim" in resposta or "confirmar" in resposta:
                    return True
                return False
            except:
                return False