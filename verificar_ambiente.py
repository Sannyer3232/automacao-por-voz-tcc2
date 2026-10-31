# verificar_ambiente.py — checklist da máquina (TODO 0: rode no início da aula)
import importlib
import json
import os
import shutil
import socket
import sys

VERDE, AMARELO, VERMELHO, FIM = "\033[92m", "\033[93m", "\033[91m", "\033[0m"
erros_essenciais = 0


def ok(msg):
    print(f"{VERDE}  ✔ {msg}{FIM}")


def aviso(msg):
    print(f"{AMARELO}  ⚠ {msg}{FIM}")


def erro(msg):
    global erros_essenciais
    erros_essenciais += 1
    print(f"{VERMELHO}  ✘ {msg}{FIM}")


def modulo_existe(nome):
    try:
        importlib.import_module(nome)
        return True
    except Exception:
        return False


print("Essencial")
if sys.version_info >= (3, 10):
    ok(f"Python {sys.version.split()[0]}")
else:
    erro(f"Python {sys.version.split()[0]}: é preciso 3.10 ou superior")

for modulo, pacote in [("nltk", "nltk"), ("sklearn", "scikit-learn"), ("joblib", "joblib")]:
    if modulo_existe(modulo):
        ok(f"{pacote} instalado")
    else:
        erro(f"{pacote} não instalado: pip install -r requirements.txt")

if modulo_existe("nltk"):
    import nltk
    for pacote, caminho in [("stopwords", "corpora/stopwords"), ("rslp", "stemmers/rslp")]:
        try:
            nltk.data.find(caminho)
            ok(f"dados do NLTK: {pacote}")
        except LookupError:
            erro(f"dados do NLTK '{pacote}' ausentes: python -m nltk.downloader {pacote}")

print("\nAções no computador")
sessao = os.environ.get("XDG_SESSION_TYPE", "desconhecida").lower()
if sessao == "x11":
    ok("sessão gráfica X11 (atalhos de teclado funcionam)")
else:
    aviso(f"sessão '{sessao}': atalhos serão simulados. Para usá-los, entre na sessão 'Ubuntu on Xorg'")

if modulo_existe("pyautogui"):
    ok("pyautogui instalado")
else:
    aviso("pyautogui indisponível: atalhos serão simulados")

pasta = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(pasta, "exercicios", "comandos.json"), encoding="utf-8") as arquivo:
    intencoes = json.load(arquivo)["intencoes"]
for nome, dados in intencoes.items():
    comando = dados["acao"].get("comando")
    if comando:
        if shutil.which(comando[0]):
            ok(f"{nome}: '{comando[0]}' encontrado")
        else:
            aviso(f"{nome}: '{comando[0]}' não encontrado (ajuste no comandos.json)")

try:
    socket.create_connection(("duckduckgo.com", 443), timeout=3).close()
    ok("internet disponível (pesquisa web)")
except OSError:
    aviso("sem internet: a pesquisa web e o reconhecimento do Google não vão funcionar")

print("\nOpcional (voz)")
try:
    import pyttsx3
    pyttsx3.init()  # falha se não houver o eSpeak no sistema
    ok("pyttsx3 + eSpeak (--voz)")
except Exception:
    aviso("--voz indisponível: pip install pyttsx3 e sudo apt install espeak-ng")

if modulo_existe("speech_recognition") and modulo_existe("pyaudio"):
    import speech_recognition as sr
    try:
        microfones = sr.Microphone.list_microphone_names()
        ok(f"--microfone: {len(microfones)} dispositivo(s) de áudio encontrado(s)")
    except Exception as e:
        aviso(f"--microfone: não foi possível listar microfones ({e})")
else:
    aviso("--microfone indisponível: pip install -r requirements.txt (e sudo apt install portaudio19-dev python3-dev build-essential)")

if not modulo_existe("vosk"):
    aviso("vosk não instalado (só faz falta sem internet)")
elif os.path.isdir(os.path.join(pasta, "modelo-vosk")):
    ok("vosk + modelo em português (reconhecimento offline)")
else:
    aviso("vosk instalado, mas sem modelo: python baixar_modelo_vosk.py")

print()
if erros_essenciais:
    print(f"{VERMELHO}{erros_essenciais} problema(s) no essencial. Chame o instrutor.{FIM}")
    sys.exit(1)
print(f"{VERDE}Tudo pronto para a oficina!{FIM}")
