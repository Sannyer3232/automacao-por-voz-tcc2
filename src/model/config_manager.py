import json
import os
import sys

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
                "iniciar_com_sistema": False,
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

        # Lógica especial para inicialização com o sistema (RF-3)
        if key == "iniciar_com_sistema":
            self._set_autostart(value)
    def get_paths(self):
        """Retorna o dicionário de caminhos dos programas."""
        # Retorna o que está no JSON ou um dicionário vazio se não existir
        return self.user_config.get("paths", {})

    # --- Inicialização automática no Linux (RF-3) ---
    def _set_autostart(self, enable):
        """Cria ou remove o atalho .desktop em ~/.config/autostart (padrão XDG)."""
        autostart_dir = os.path.join(
            os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "autostart"
        )
        desktop_path = os.path.join(autostart_dir, "tcc-sannyer-voiceassist.desktop")

        # Caminho para o executável do Python atual e o script main.py
        python_exe = sys.executable
        project_dir = os.path.abspath(".")
        script_path = os.path.join(project_dir, "main.py")

        try:
            if enable:
                os.makedirs(autostart_dir, exist_ok=True)
                with open(desktop_path, "w", encoding="utf-8") as f:
                    f.write(
                        "[Desktop Entry]\n"
                        "Type=Application\n"
                        "Name=Assistente de Automação por Voz\n"
                        f'Exec="{python_exe}" "{script_path}"\n'
                        f"Path={project_dir}\n"
                        "X-GNOME-Autostart-enabled=true\n"
                    )
                print("Adicionado à inicialização do sistema.")
            elif os.path.exists(desktop_path):
                os.remove(desktop_path)
                print("Removido da inicialização do sistema.")
        except Exception as e:
            print(f"Erro ao configurar a inicialização automática: {e}")

    def get_custom_actions(self):
        """Retorna o dicionário de ações customizadas (macros/programas)."""
        return self.user_config.get("custom_actions", {})

    def add_custom_action(self, intent_name, action_type, action_value):
        """
        Salva a lógica da nova ação.
        type: 'macro' ou 'program'
        value: 'ctrl+c' ou '/caminho/para/app' (ou comando do PATH)
        """
        if "custom_actions" not in self.user_config:
            self.user_config["custom_actions"] = {}
        
        self.user_config["custom_actions"][intent_name] = {
            "type": action_type,
            "value": action_value
        }
        self.save_json(self.config_path, self.user_config)