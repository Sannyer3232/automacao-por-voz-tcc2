# testar_microfone.py — teste do reconhecimento de voz, do microfone até a intenção
#
#   python testar_microfone.py --listar        # lista os microfones e seus índices
#   python testar_microfone.py                 # grava uma frase com o microfone padrão
#   python testar_microfone.py --mic 3         # grava com o microfone de índice 3
#   python testar_microfone.py --arquivo x.wav # testa com um áudio gravado (sem microfone)
import argparse
import os
import sys
import time

PASTA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PASTA, "solucao"))

try:
    import speech_recognition as sr
except ImportError:
    print("Instale primeiro: pip install -r requirements.txt")
    sys.exit(1)

import voz


def listar_microfones():
    try:
        nomes = sr.Microphone.list_microphone_names()
    except Exception as erro:
        print(f"Não foi possível listar os microfones ({erro}). O PyAudio está instalado?")
        return
    print("Dispositivos de áudio (use o índice com --mic):")
    for indice, nome in enumerate(nomes):
        print(f"  {indice:>2}: {nome}")


def gravar(mic, segundos):
    reconhecedor = sr.Recognizer()
    with sr.Microphone(device_index=mic) as fonte:
        print("1. Calibrando: fique em silêncio por 1 segundo...")
        reconhecedor.adjust_for_ambient_noise(fonte, duration=1)
        print(f"   Limiar de energia: {reconhecedor.energy_threshold:.0f} "
              "(acima de ~4000 indica ambiente muito barulhento ou ganho alto demais)")
        print(f"2. 🎤 Fale um comando (até {segundos} s)...")
        audio = reconhecedor.listen(fonte, timeout=5, phrase_time_limit=segundos)
    caminho = os.path.join(PASTA, "gravacao.wav")
    with open(caminho, "wb") as arquivo:
        arquivo.write(audio.get_wav_data())
    print(f"   Gravado em {caminho} (ouça com: aplay gravacao.wav)")
    return audio


def transcrever(nome, funcao, audio):
    inicio = time.perf_counter()
    try:
        texto = funcao(audio)
    except sr.UnknownValueError:
        texto = None
    except sr.RequestError as erro:
        print(f"   {nome:<7} erro de conexão: {erro}")
        return None
    print(f"   {nome:<7} {texto!r} ({time.perf_counter() - inicio:.1f} s)")
    return texto


def main():
    parser = argparse.ArgumentParser(description="Teste do reconhecimento de voz")
    parser.add_argument("--listar", action="store_true", help="lista os microfones e sai")
    parser.add_argument("--mic", type=int, default=None, help="índice do microfone")
    parser.add_argument("--arquivo", help="arquivo .wav para testar sem microfone")
    parser.add_argument("--segundos", type=int, default=6, help="duração máxima da frase")
    args = parser.parse_args()

    if args.listar:
        listar_microfones()
        return

    if args.arquivo:
        if not os.path.isfile(args.arquivo):
            print(f"Arquivo não encontrado: {args.arquivo}")
            return
        with sr.AudioFile(args.arquivo) as fonte:
            audio = sr.Recognizer().record(fonte)
    else:
        try:
            audio = gravar(args.mic, args.segundos)
        except sr.WaitTimeoutError:
            print("   Não ouvi nada. Confira o microfone com --listar e o volume de entrada.")
            return
        except Exception as erro:
            print(f"Erro ao abrir o microfone: {erro}")
            listar_microfones()
            return

    print("3. Transcrevendo:")
    textos = [transcrever("Vosk", voz.reconhecer_vosk, audio),
              transcrever("Google", voz.reconhecer_google, audio)]

    from classificador import carregar_comandos, obter_classificador
    comandos = carregar_comandos()
    classificador = obter_classificador(comandos, comandos["limiar"])
    print("4. Intenção identificada:")
    for nome, texto in zip(["Vosk", "Google"], textos):
        if texto:
            intencao, score = classificador.prever(texto)
            print(f"   {nome:<7} {intencao or 'não compreendido'} (score {score:.2f})")


if __name__ == "__main__":
    main()
