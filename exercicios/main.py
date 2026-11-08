# main.py — laço principal do assistente
import argparse
import os

from acoes import WAYLAND, executar, extrair_termo
from classificador import carregar_comandos, obter_classificador
import voz


def ler_argumentos(limiar_padrao):
    parser = argparse.ArgumentParser(description="Assistente de comandos (versão oficina)")
    parser.add_argument("--simular", action="store_true", help="descreve as ações sem executá-las")
    parser.add_argument("--voz", action="store_true", help="fala as respostas")
    parser.add_argument("--audio", help="arquivo .wav ou pasta com áudios gravados (dispensa o microfone)")
    parser.add_argument("--microfone", action="store_true", help="ouve os comandos pelo microfone")
    parser.add_argument("--mic", type=int, default=None, help="índice do microfone (veja testar_microfone.py)")
    parser.add_argument("--reconhecedor", choices=["auto", "vosk", "google"], default="auto",
                        help="auto: Vosk (offline) e, se ele faltar, Google")
    parser.add_argument("--limiar", type=float, default=limiar_padrao, help="score mínimo para aceitar")
    return parser.parse_args()


def listar_audios(caminho):
    """Devolve os .wav de uma pasta (em ordem alfabética) ou o próprio arquivo."""
    if os.path.isdir(caminho):
        nomes = sorted(n for n in os.listdir(caminho) if n.lower().endswith(".wav"))
        return [os.path.join(caminho, n) for n in nomes]
    if os.path.isfile(caminho):
        return [caminho]
    print(f"Áudio não encontrado: {caminho}")
    return []


def transcrever_audio(caminho, args):
    print(f"\n🔊 Áudio: {os.path.basename(caminho)}")
    try:
        texto = voz.ouvir_arquivo(caminho, args.reconhecedor)
    except NotImplementedError as erro:
        print(f"  ({erro})")
        return None
    if texto:
        print(f"Você disse: {texto}")
    else:
        print("  (não entendi o áudio)")
    return texto


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


def processar(texto, classificador, comandos, args):
    """Classifica o texto e executa a ação. Devolve False quando é para encerrar."""
    intencoes = comandos["intencoes"]
    intencao, score = classificador.prever(texto)
    print(f"  [intenção: {intencao or '-'} | score: {score:.2f}]")  # modo didático (RF-2)
    if intencao is None:
        responder("Desculpe, comando não compreendido.", args.voz)
        return True

    dados = intencoes[intencao]
    acao = dados["acao"]
    termo = None
    if acao["tipo"] == "interno":
        if acao["nome"] == "sair":
            responder(dados["resposta"], args.voz)
            return False
        print(texto_ajuda(intencoes))
    else:
        if acao["tipo"] == "pesquisa":
            termo = extrair_termo(texto, acao["gatilhos"])
            if not termo:
                responder("O que você quer pesquisar? Ex: 'pesquisar receita de bolo'.", args.voz)
                return True
        try:
            print(f"  {executar(acao, termo, args.simular, comandos['url_busca'])}")
        except NotImplementedError as erro:
            print(f"  ({erro})")
            return True
    responder(dados["resposta"].format(termo=termo or ""), args.voz)
    return True


def main():
    comandos = carregar_comandos()
    args = ler_argumentos(comandos["limiar"])
    classificador = obter_classificador(comandos, args.limiar)

    if WAYLAND and not args.simular:
        print("Aviso: sessão Wayland detectada. Os atalhos de teclado serão simulados.")

    # Áudios gravados: transcreve e executa cada um, sem precisar de microfone
    if args.audio:
        for caminho in listar_audios(args.audio):
            texto = transcrever_audio(caminho, args)
            if texto and not processar(texto, classificador, comandos, args):
                break
        return

    if args.microfone and not voz.microfone_disponivel(args.mic):
        print("Seguindo com o teclado.")
        args.microfone = False
    print("Assistente pronto! Digite 'ajuda' para ver os comandos ou 'sair' para encerrar.")

    while True:
        try:
            texto = obter_entrada(args)
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if texto and not processar(texto, classificador, comandos, args):
            break


if __name__ == "__main__":
    main()
