# baixar_modelo_vosk.py — baixa o modelo Vosk pequeno em português (~31 MB) para modelo-vosk/
import os
import shutil
import sys
import tempfile
import urllib.request
import zipfile

URL = "https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip"
DESTINO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelo-vosk")


def mostrar_progresso(blocos, tamanho_bloco, total):
    if total > 0:
        feito = min(blocos * tamanho_bloco, total)
        print(f"\r  {feito / 1e6:5.1f} / {total / 1e6:.1f} MB", end="", flush=True)


def main():
    if os.path.isdir(DESTINO):
        print(f"O modelo já está em {DESTINO}. Apague a pasta para baixar de novo.")
        return

    with tempfile.TemporaryDirectory() as temporaria:
        arquivo_zip = os.path.join(temporaria, "modelo.zip")
        print(f"Baixando {URL}")
        try:
            urllib.request.urlretrieve(URL, arquivo_zip, mostrar_progresso)
        except OSError as erro:
            print(f"\nFalha no download: {erro}")
            sys.exit(1)
        print("\nDescompactando...")
        with zipfile.ZipFile(arquivo_zip) as zip_modelo:
            zip_modelo.extractall(temporaria)
            pasta_extraida = zip_modelo.namelist()[0].split("/")[0]
        shutil.move(os.path.join(temporaria, pasta_extraida), DESTINO)

    print(f"Pronto! Modelo salvo em {DESTINO}")


if __name__ == "__main__":
    main()
