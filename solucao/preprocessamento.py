# preprocessamento.py — normaliza o texto como no TCC
import re
import unicodedata

import nltk
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from nltk.tokenize import wordpunct_tokenize


def _garantir_dados_nltk():
    """Baixa os dados do NLTK na primeira execução (precisa de internet só uma vez)."""
    for pacote, caminho in [("stopwords", "corpora/stopwords"), ("rslp", "stemmers/rslp")]:
        try:
            nltk.data.find(caminho)
        except LookupError:
            nltk.download(pacote, quiet=True)


_garantir_dados_nltk()

# Lista do NLTK, menos o que muda o sentido, mais o "ruído" típico de comandos
MANTER = {"não", "mais"}
RUIDO = {"por", "favor", "agora", "pra", "aí", "né", "então", "ei", "oi"}
STOPWORDS = (set(stopwords.words("portuguese")) - MANTER) | RUIDO

stemmer = RSLPStemmer()


def sem_acentos(palavra):
    """'próx' -> 'prox', para quem digita sem acento chegar ao mesmo radical."""
    decomposta = unicodedata.normalize("NFD", palavra)
    return "".join(c for c in decomposta if unicodedata.category(c) != "Mn")


def limpar(texto):
    """Minúsculas, sem pontuação e separado em tokens."""
    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", " ", texto)
    return wordpunct_tokenize(texto)


def remover_stopwords(tokens):
    """Remove as palavras que não ajudam a identificar a intenção."""
    return [t for t in tokens if t not in STOPWORDS]


def radicalizar(tokens):
    """Reduz cada palavra ao radical: 'abrir', 'abre', 'abrindo' -> 'abr'."""
    return [stemmer.stem(t) for t in tokens]


def normalizar(texto):
    """Pipeline completo: limpar -> remover stopwords -> radicalizar."""
    tokens = radicalizar(remover_stopwords(limpar(texto)))
    return [sem_acentos(t) for t in tokens]


if __name__ == "__main__":
    for frase in ["Abre a ABA!", "por favor abre aba agora", "abrir, abre e abrindo"]:
        print(f"{frase!r:30} -> {normalizar(frase)}")
