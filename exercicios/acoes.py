# acoes.py — traduz uma intenção em ação no Linux
import os
import shutil
import subprocess
import webbrowser
from urllib.parse import quote

# O PyAutoGUI é opcional: sem ele (ou sem sessão gráfica) os atalhos são simulados
try:
    import pyautogui
except Exception:
    pyautogui = None

WAYLAND = os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"
URL_BUSCA_PADRAO = "https://duckduckgo.com/?q={termo}"


def extrair_termo(texto, gatilhos):
    """O termo é o que vem depois da última palavra-gatilho: 'pesquisar [receita de bolo]'."""
    palavras = [p.strip(".,!?;:") for p in texto.lower().split()]
    posicoes = [i for i, palavra in enumerate(palavras) if palavra in gatilhos]
    if not posicoes:
        return None
    return " ".join(palavras[posicoes[-1] + 1:]) or None


def _iniciar_programa(comando):
    comando = [os.path.expanduser(parte) for parte in comando]  # "~" vira a sua pasta pessoal
    # TODO 6a:
    #   1. se shutil.which(comando[0]) for None, devolva uma mensagem de "não encontrado"
    #   2. senão, abra com subprocess.Popen(comando, start_new_session=True)
    #   3. devolva uma mensagem dizendo qual programa foi iniciado
    raise NotImplementedError("TODO 6a: implemente _iniciar_programa() em acoes.py")


def _pressionar_atalho(teclas):
    atalho = "+".join(teclas)
    if pyautogui is None or WAYLAND:
        return f"[simulação] pressionaria {atalho} (atalhos exigem PyAutoGUI numa sessão X11)"
    # TODO 6b: pressione as teclas com pyautogui.hotkey(*teclas) e devolva uma mensagem
    raise NotImplementedError("TODO 6b: implemente _pressionar_atalho() em acoes.py")


def executar(acao, termo=None, simular=False, url_busca=URL_BUSCA_PADRAO):
    """Executa a ação (ou só a descreve, com simular=True) e devolve o que foi feito."""
    tipo = acao["tipo"]

    if tipo == "programa":
        if simular:
            return f"[simulação] abriria: {' '.join(acao['comando'])}"
        return _iniciar_programa(acao["comando"])

    if tipo == "atalho":
        if simular:
            return f"[simulação] pressionaria {'+'.join(acao['teclas'])}"
        return _pressionar_atalho(acao["teclas"])

    if tipo == "pesquisa":
        if not termo:
            return "Não entendi o que pesquisar. Ex: 'pesquisar receita de bolo'."
        # Segurança: o texto do usuário só entra na URL, sempre escapado
        url = url_busca.format(termo=quote(termo))
        if simular:
            return f"[simulação] abriria {url}"
        webbrowser.open(url)
        return f"Pesquisa aberta: {url}"

    if tipo == "sistema":
        # Comando fixo do comandos.json, nunca montado a partir do texto digitado
        if simular:
            return f"[simulação] executaria: {' '.join(acao['comando'])}"
        if not shutil.which(acao["comando"][0]):
            return f"Comando '{acao['comando'][0]}' não encontrado."
        subprocess.run(acao["comando"], check=False)
        return f"Comando executado: {' '.join(acao['comando'])}"

    return f"Tipo de ação desconhecido: {tipo}"
