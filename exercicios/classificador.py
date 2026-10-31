# classificador.py — TF-IDF + similaridade do cosseno (núcleo do TCC)
import json
import os

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from preprocessamento import normalizar

PASTA = os.path.dirname(os.path.abspath(__file__))
CAMINHO_COMANDOS = os.path.join(PASTA, "comandos.json")
CAMINHO_MODELO = os.path.join(PASTA, "modelo.joblib")


class ClassificadorIntencoes:
    def __init__(self, limiar=0.5):
        self.limiar = limiar
        self.vetorizador = None
        self.matriz = None   # uma linha por frase de exemplo
        self.rotulos = []    # a intenção de cada linha

    def treinar(self, comandos):
        frases = []
        self.rotulos = []
        for intencao, dados in comandos["intencoes"].items():
            for frase in dados["frases"]:
                frases.append(frase)
                self.rotulos.append(intencao)
        self.vetorizador = TfidfVectorizer(analyzer=normalizar)
        self.matriz = self.vetorizador.fit_transform(frases)

    def prever(self, texto):
        """Devolve (intencao, score); intencao é None se o score ficar abaixo do limiar."""
        # TODO 4:
        #   1. vetorize o texto: self.vetorizador.transform([texto])
        #   2. compare com todas as frases: cosine_similarity(vetor, self.matriz)[0]
        #   3. pegue a posição da maior similaridade (.argmax()) e o score dela
        #   4. se o score for menor que self.limiar, devolva (None, score)
        #   5. senão, devolva (self.rotulos[posicao], score)
        # Confira rodando: python classificador.py
        raise NotImplementedError("TODO 4: implemente prever() em classificador.py")

    def salvar(self, caminho=CAMINHO_MODELO):
        joblib.dump((self.vetorizador, self.matriz, self.rotulos), caminho)

    def carregar(self, caminho=CAMINHO_MODELO):
        self.vetorizador, self.matriz, self.rotulos = joblib.load(caminho)


def carregar_comandos(caminho=CAMINHO_COMANDOS):
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def obter_classificador(comandos, limiar=0.5):
    """Carrega o modelo salvo ou retreina se o comandos.json for mais novo (RF-5)."""
    classificador = ClassificadorIntencoes(limiar)
    desatualizado = (not os.path.exists(CAMINHO_MODELO)
                     or os.path.getmtime(CAMINHO_COMANDOS) > os.path.getmtime(CAMINHO_MODELO))
    if desatualizado:
        print("Treinando o modelo com o comandos.json...")
        classificador.treinar(comandos)
        classificador.salvar()
    else:
        classificador.carregar()
    return classificador


if __name__ == "__main__":
    comandos = carregar_comandos()
    classificador = obter_classificador(comandos, comandos["limiar"])
    print("Digite frases para testar (Enter vazio para sair).")
    while frase := input("> ").strip():
        intencao, score = classificador.prever(frase)
        print(f"  intenção: {intencao or 'não compreendido'} (score {score:.2f})")
