# src/services/input_service.py
import os
import shutil
import subprocess
import time

# Códigos de tecla do kernel Linux (linux/input-event-codes.h), usados pelo ydotool
KEYCODES = {
    "esc": 1, "backspace": 14, "tab": 15, "enter": 28, "space": 57,
    "ctrl": 29, "shift": 42, "alt": 56, "super": 125,
    "up": 103, "down": 108, "left": 105, "right": 106,
    "home": 102, "end": 107, "pageup": 104, "pagedown": 109,
    "insert": 110, "delete": 111,
    "volumemute": 113, "volumedown": 114, "volumeup": 115,
    "nexttrack": 163, "playpause": 164, "prevtrack": 165,
    "a": 30, "b": 48, "c": 46, "d": 32, "e": 18, "f": 33, "g": 34, "h": 35,
    "i": 23, "j": 36, "k": 37, "l": 38, "m": 50, "n": 49, "o": 24, "p": 25,
    "q": 16, "r": 19, "s": 31, "t": 20, "u": 22, "v": 47, "w": 17, "x": 45,
    "y": 21, "z": 44,
    "1": 2, "2": 3, "3": 4, "4": 5, "5": 6, "6": 7, "7": 8, "8": 9, "9": 10, "0": 11,
    "f1": 59, "f2": 60, "f3": 61, "f4": 62, "f5": 63, "f6": 64,
    "f7": 65, "f8": 66, "f9": 67, "f10": 68, "f11": 87, "f12": 88,
}

# Nomes alternativos (inclui os nomes do Windows/pyautogui usados em macros antigas)
ALIASES = {
    "win": "super", "windows": "super", "meta": "super", "cmd": "super",
    "control": "ctrl", "return": "enter", "del": "delete", "escape": "esc",
    "pgup": "pageup", "pgdn": "pagedown",
}


class KeyboardController:
    """
    Simula teclado no Linux.
    - Wayland: usa o ydotool (o pyautogui não consegue enviar teclas ao GNOME/Wayland).
    - X11: usa o pyautogui.
    """

    def __init__(self):
        sessao = os.environ.get("XDG_SESSION_TYPE", "").lower()
        if sessao == "wayland" and shutil.which("ydotool"):
            self.backend = "ydotool"
        else:
            self.backend = "pyautogui"
            if sessao == "wayland":
                print("AVISO: Sessão Wayland sem ydotool. Atalhos de teclado podem não funcionar. "
                      "Instale o ydotool ou use a sessão 'Ubuntu on Xorg'.")
            import pyautogui
            self._pyautogui = pyautogui
        print(f"Backend de teclado: {self.backend}")

    def _normalizar(self, tecla):
        tecla = tecla.strip().lower()
        return ALIASES.get(tecla, tecla)

    def hotkey(self, *teclas):
        teclas = [self._normalizar(t) for t in teclas]
        if self.backend == "pyautogui":
            # O pyautogui chama a tecla super de "win"
            self._pyautogui.hotkey(*["win" if t == "super" else t for t in teclas])
            return

        codigos = [KEYCODES[t] for t in teclas]
        # Pressiona todas em ordem e solta na ordem inversa
        eventos = [f"{c}:1" for c in codigos] + [f"{c}:0" for c in reversed(codigos)]
        subprocess.run(["ydotool", "key", *eventos], check=False)

    def press(self, tecla):
        self.hotkey(tecla)

    def write(self, texto):
        if not texto:
            return
        # ydotool e pyautogui só digitam ASCII: textos com acento (á, ç, õ...) são colados
        if not texto.isascii() and self._colar(texto):
            return
        if self.backend == "pyautogui":
            self._pyautogui.write(texto)
        else:
            subprocess.run(["ydotool", "type", "--", texto], check=False)

    def _colar(self, texto):
        """
        Insere o texto via área de transferência (Ctrl+V) e depois restaura
        o conteúdo anterior. Requer wl-clipboard (Wayland) ou xclip/xsel (X11).
        """
        try:
            import pyperclip
            try:
                anterior = pyperclip.paste()
            except Exception:
                anterior = None

            pyperclip.copy(texto)
            time.sleep(0.1)
            self.hotkey("ctrl", "v")
            # Espera o aplicativo ler a área de transferência antes de restaurar
            time.sleep(0.3)

            if anterior is not None:
                pyperclip.copy(anterior)
            return True
        except Exception as e:
            print(f"AVISO: Não foi possível colar texto acentuado ({e}). "
                  "Instale o wl-clipboard (Wayland) ou xclip (X11).")
            return False
