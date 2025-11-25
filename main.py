import sys
import os

# Adiciona o diretório atual ao path do Python para garantir que
# ele encontre o pacote 'src' corretamente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.view.main_window import MainWindow

if __name__ == "__main__":
    # Cria a aplicação e inicia o loop da interface gráfica
    app = MainWindow()
    app.mainloop()