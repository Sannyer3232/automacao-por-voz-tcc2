# main.py — laço principal do assistente
import argparse

from acoes import WAYLAND, executar, extrair_termo
from classificador import carregar_comandos, obter_classificador
import voz


def ler_argumentos(limiar_padrao):
    parser = argparse.ArgumentParser(description="Assistente de comandos (versão oficina)")
    parser.add_argument("--simular", action="store_true", help="descreve as ações sem executá-las")
    parser.add_argument("--voz", action="store_true", help="fala as respostas")
    parser.add_argument("--microfone", action="store_true", help="ouve os comandos pelo microfone")
    parser.add_argument("--mic", type=int, default=None, help="índice do microfone (veja testar_microfone.py)")
    parser.add_argument("--reconhecedor", choices=["auto", "vosk", "google"], default="auto",
                        help="auto: Vosk (offline) e, se ele faltar, Google")
    parser.add_argument("--limiar", type=float, default=limiar_padrao, help="score mínimo para aceitar")
    return parser.parse_args()


def obter_entrada(args):
    if args.microfone:
        try:
            texto = voz.ouvir(args.mic, args.reconhecedor)
        except NotImplementedError as erro:
            print(f"  ({erro})")
            texto = None
        if texto:
            print(f"Você disse: {texto}")
            return texto
        print("Não ouvi direito, digite o comando:")
    return input("Você: ").strip()


def texto_ajuda(intencoes):
    linhas = [f"  - {nome}: \"{dados['frases'][0]}\"" for nome, dados in intencoes.items()]
    return "\n".join(linhas)


def responder(texto, usar_voz):
    print(f"Assistente: {texto}")
    if usar_voz:
        try:
            voz.falar(texto)
        except NotImplementedError as erro:
            print(f"  ({erro})")


def main():
    comandos = carregar_comandos()
    args = ler_argumentos(comandos["limiar"])
    classificador = obter_classificador(comandos, args.limiar)
    intencoes = comandos["intencoes"]

    if args.microfone and not voz.microfone_disponivel(args.mic):
        print("Seguindo com o teclado.")
        args.microfone = False
    if WAYLAND and not args.simular:
        print("Aviso: sessão Wayland detectada. Os atalhos de teclado serão simulados.")
    print("Assistente pronto! Digite 'ajuda' para ver os comandos ou 'sair' para encerrar.")

    while True:
        try:
            texto = obter_entrada(args)
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not texto:
            continue

        intencao, score = classificador.prever(texto)
        print(f"  [intenção: {intencao or '-'} | score: {score:.2f}]")  # modo didático (RF-2)
        if intencao is None:
            responder("Desculpe, comando não compreendido.", args.voz)
            continue

        dados = intencoes[intencao]
        acao = dados["acao"]
        termo = None
        if acao["tipo"] == "interno":
            if acao["nome"] == "sair":
                responder(dados["resposta"], args.voz)
                break
            print(texto_ajuda(intencoes))
        else:
            if acao["tipo"] == "pesquisa":
                termo = extrair_termo(texto, acao["gatilhos"])
                if not termo:
                    responder("O que você quer pesquisar? Ex: 'pesquisar receita de bolo'.", args.voz)
                    continue
            try:
                print(f"  {executar(acao, termo, args.simular, comandos['url_busca'])}")
            except NotImplementedError as erro:
                print(f"  ({erro})")
                continue
        responder(dados["resposta"].format(termo=termo or ""), args.voz)


if __name__ == "__main__":
    main()
