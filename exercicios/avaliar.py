# avaliar.py — mede o classificador em frases inéditas (testes.csv)
import argparse
import csv
import os

from sklearn.metrics import accuracy_score, confusion_matrix, f1_score

from classificador import PASTA, carregar_comandos, obter_classificador

ACURACIA_TCC = 0.94


def carregar_testes(caminho=os.path.join(PASTA, "testes.csv")):
    with open(caminho, encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    return [l["frase"] for l in linhas], [l["intencao_esperada"] for l in linhas]


def imprimir_matriz(esperados, previstos):
    rotulos = sorted(set(esperados) | set(previstos))
    matriz = confusion_matrix(esperados, previstos, labels=rotulos)
    print("\nMatriz de confusão (linhas = esperado, colunas = previsto):")
    print(" " * 18 + "".join(f"{i:>3}" for i in range(len(rotulos))))
    for i, (rotulo, linha) in enumerate(zip(rotulos, matriz)):
        celulas = "".join(f"{n:>3}" if n else "  ." for n in linha)
        print(f"{i:>2} {rotulo:<15}{celulas}")


def main():
    comandos = carregar_comandos()
    parser = argparse.ArgumentParser(description="Avalia o classificador em testes.csv")
    parser.add_argument("--limiar", type=float, default=comandos["limiar"])
    args = parser.parse_args()

    classificador = obter_classificador(comandos, args.limiar)
    frases, esperados = carregar_testes()

    # TODO 5:
    #   1. para cada frase, chame classificador.prever(frase) e guarde a intenção
    #      em 'previstos' (use "nenhuma" quando vier None: frase rejeitada pelo limiar)
    #   2. calcule acuracia = accuracy_score(esperados, previstos)
    #   3. calcule f1 = f1_score(esperados, previstos, average="macro", zero_division=0)
    # Depois teste: python avaliar.py --limiar 0.3 / 0.5 / 0.7
    raise NotImplementedError("TODO 5: complete a avaliação em avaliar.py")

    print(f"Limiar: {args.limiar} | {len(frases)} frases de teste")
    print(f"Acurácia: {acuracia:.2f}  (TCC: {ACURACIA_TCC})")
    print(f"F1 macro: {f1:.2f}")
    imprimir_matriz(esperados, previstos)

    erros = [(f, e, p) for f, e, p in zip(frases, esperados, previstos) if e != p]
    if erros:
        print("\nErros:")
        for frase, esperado, previsto in erros:
            print(f"  '{frase}': esperado {esperado}, previsto {previsto}")


if __name__ == "__main__":
    main()
