import json
import os
import sys
import winreg # Necessário para mexer no Registro do Windows

class ConfigManager:
    def __init__(self):
        self.config_path = "config/config_usuario.json"
        self.commands_path = "config/comandos.json"
        self.ensure_files_exist()
        self.user_config = self.load_json(self.config_path)
        self.commands = self.load_json(self.commands_path)

    def ensure_files_exist(self):
        os.makedirs("config", exist_ok=True)
        if not os.path.exists(self.config_path):
            default_config = {
                "feedback_voz": True,
                "tema": "Dark",
                "iniciar_com_windows": False,
                "limiar_confianca": 0.5
            }
            self.save_json(self.config_path, default_config)
        
        if not os.path.exists(self.commands_path):
            self.save_json(self.commands_path, {}) # Cria vazio se não existir

    def load_json(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar {path}: {e}")
            return {}

    def save_json(self, path, data):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar {path}: {e}")

    # --- Gerenciamento de Comandos (RF-2) ---
    def get_commands(self):
        return self.commands

    def add_command(self, intent, phrases):
        """Adiciona novas frases a uma intenção existente."""
        if intent in self.commands:
            # Converte para set para evitar duplicatas e volta para list
            current = set(self.commands[intent])
            if isinstance(phrases, list):
                current.update(phrases)
            else:
                current.add(phrases)
            self.commands[intent] = list(current)
        else:
            # Se a intenção não existe (ex: usuário avançado criando nova lógica), cria nova
            self.commands[intent] = phrases if isinstance(phrases, list) else [phrases]
            
        self.save_json(self.commands_path, self.commands)

    # --- Gerenciamento de Preferências (RF-1) ---
    def get_preference(self, key):
        return self.user_config.get("preferences", {}).get(key)

    def set_preference(self, key, value):
        if "preferences" not in self.user_config:
            self.user_config["preferences"] = {}
        
        self.user_config["preferences"][key] = value
        self.save_json(self.config_path, self.user_config)

        # Lógica especial para inicialização do Windows (RF-3)
        if key == "iniciar_com_windows":
            self._set_windows_startup(value)
    def get_paths(self):
        """Retorna o dicionário de caminhos dos programas."""
        # Retorna o que está no JSON ou um dicionário vazio se não existir
        return self.user_config.get("paths", {})

    # --- Lógica de Registro do Windows (RF-3) ---
    def _set_windows_startup(self, enable):
        """Adiciona ou remove o script da chave Run do Registro do Windows."""
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "TCC_Sannyer_VoiceAssist"
        
        # Caminho para o executável do Python atual e o script main.py
        # Nota: Isso funciona enquanto você roda o código fonte. 
        # Se criar um .exe depois, o caminho muda para o próprio .exe.
        python_exe = sys.executable
        script_path = os.path.abspath("main.py")
        command = f'"{python_exe}" "{script_path}"'

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            if enable:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command)
                print("Adicionado à inicialização do Windows.")
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                    print("Removido da inicialização do Windows.")
                except FileNotFoundError:
                    pass # Já não existia
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Erro ao manipular registro do Windows: {e}")
    def get_custom_actions(self):
        """Retorna o dicionário de ações customizadas (macros/programas)."""
        return self.user_config.get("custom_actions", {})

    def add_custom_action(self, intent_name, action_type, action_value):
        """
        Salva a lógica da nova ação.
        type: 'macro' ou 'program'
        value: 'ctrl+c' ou 'C:/caminho/app.exe'
        """
        if "custom_actions" not in self.user_config:
            self.user_config["custom_actions"] = {}
        
        self.user_config["custom_actions"][intent_name] = {
            "type": action_type,
            "value": action_value
        }
        self.save_json(self.config_path, self.user_config)