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
            self._selecionar_voz_portugues(engine)
            engine.say(texto)
            engine.runAndWait()
        except Exception as e:
            print(f"Erro ao sintetizar áudio: {e}")

    def _selecionar_voz_portugues(self, engine):
        """No Linux o pyttsx3 usa o eSpeak, cuja voz padrão é inglês."""
        for voz in engine.getProperty("voices"):
            idiomas = " ".join(
                l.decode(errors="ignore") if isinstance(l, bytes) else str(l)
                for l in (voz.languages or [])
            )
            identificacao = f"{voz.id} {voz.name} {idiomas}".lower()
            if "pt-br" in identificacao or "brazil" in identificacao:
                engine.setProperty("voice", voz.id)
                return