# voz.py — opcional: falar (pyttsx3 + espeak-ng) e ouvir (SpeechRecognition + Vosk offline ou Google)
import json
import os

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import vosk
    vosk.SetLogLevel(-1)  # silencia o log do Kaldi
except ImportError:
    vosk = None

# Modelo Vosk em português, baixado com: python baixar_modelo_vosk.py
PASTA_MODELO_VOSK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modelo-vosk")

_motor = None
_voz_indisponivel = False
_reconhecedor = None
_modelo_vosk = None
_avisou_google = False


def _iniciar_motor():
    """Cria o motor de voz uma vez e escolhe uma voz em português."""
    global _motor
    if _motor is None:
        _motor = pyttsx3.init()
        vozes = {f"{v.id} {v.name}".lower(): v.id for v in _motor.getProperty("voices")}
        # Prefere português do Brasil; senão, qualquer português
        for trecho in ("pt-br", "brazil", "portug"):
            escolhida = next((vid for nome, vid in vozes.items() if trecho in nome), None)
            if escolhida:
                _motor.setProperty("voice", escolhida)
                break
    return _motor


def falar(texto):
    """Fala o texto. Devolve False (e segue só com texto) se não houver voz disponível."""
    global _voz_indisponivel
    if _voz_indisponivel:
        return False
    if pyttsx3 is None:
        print("  (voz indisponível: instale o pyttsx3. Seguindo só com texto.)")
        _voz_indisponivel = True
        return False
    try:
        motor = _iniciar_motor()
        motor.say(texto)
        motor.runAndWait()
        return True
    except Exception as erro:
        print(f"  (voz indisponível: {erro}. Instale o espeak-ng. Seguindo só com texto.)")
        _voz_indisponivel = True
        return False


def _obter_reconhecedor(mic):
    """Cria o reconhecedor e calibra o ruído ambiente uma única vez."""
    global _reconhecedor
    if _reconhecedor is None:
        _reconhecedor = sr.Recognizer()
        with sr.Microphone(device_index=mic) as fonte:
            print("  (calibrando o microfone: fique em silêncio por 1 segundo...)")
            _reconhecedor.adjust_for_ambient_noise(fonte, duration=1)
    return _reconhecedor


def microfone_disponivel(mic=None):
    """Testa se o microfone abre; se não, explica o motivo."""
    if sr is None:
        print("  (microfone indisponível: instale SpeechRecognition e PyAudio)")
        return False
    try:
        with sr.Microphone(device_index=mic):
            return True
    except Exception as erro:
        print(f"  (microfone indisponível: {erro})")
        return False


def ouvir(mic=None, motor="auto"):
    """Ouve uma frase no microfone e devolve o texto, ou None se falhar."""
    if sr is None:
        print("  (microfone indisponível: instale SpeechRecognition e PyAudio)")
        return None
    try:
        reconhecedor = _obter_reconhecedor(mic)
        with sr.Microphone(device_index=mic) as fonte:
            print("  🎤 Pode falar...")
            audio = reconhecedor.listen(fonte, timeout=5, phrase_time_limit=6)
    except sr.WaitTimeoutError:
        print("  (não ouvi nada)")
        return None
    except Exception as erro:
        print(f"  (microfone indisponível: {erro})")
        return None
    return reconhecer(audio, motor)


def vosk_disponivel():
    return vosk is not None and os.path.isdir(PASTA_MODELO_VOSK)


def reconhecer(audio, motor="auto"):
    """Transcreve um áudio. motor: 'vosk', 'google' ou 'auto' (Vosk e, se faltar, Google)."""
    global _avisou_google
    if motor == "vosk" or (motor == "auto" and vosk_disponivel()):
        return reconhecer_vosk(audio)
    if motor == "auto" and not _avisou_google:
        print("  (Vosk ou modelo ausente: usando o Google, que precisa de internet)")
        _avisou_google = True
    try:
        return reconhecer_google(audio)
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        print("  (sem internet: o reconhecimento do Google não está disponível)")
        return None


def reconhecer_google(audio):
    """Google Web Speech: gratuito e sem chave, mas precisa de internet."""
    return sr.Recognizer().recognize_google(audio, language="pt-BR")


def reconhecer_vosk(audio):
    """Vosk: roda offline, com o modelo em português da pasta modelo-vosk/."""
    global _modelo_vosk
    if vosk is None:
        print("  (Vosk indisponível: pip install vosk)")
        return None
    if not os.path.isdir(PASTA_MODELO_VOSK):
        print("  (modelo Vosk não encontrado: rode python baixar_modelo_vosk.py)")
        return None
    if _modelo_vosk is None:
        _modelo_vosk = vosk.Model(PASTA_MODELO_VOSK)
    reconhecedor = vosk.KaldiRecognizer(_modelo_vosk, 16000)
    reconhecedor.AcceptWaveform(audio.get_raw_data(convert_rate=16000, convert_width=2))
    return json.loads(reconhecedor.FinalResult()).get("text") or None
