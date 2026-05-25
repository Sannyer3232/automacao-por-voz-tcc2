import matplotlib.pyplot as plt
import numpy as np

# --- Graph 1: Performance Metrics ---
# Data from your benchmark results
metrics = ['Acurácia', 'F1-Score', 'Similaridade', 'WER (Erro)']
values = [0.8400, 0.8362, 0.8743, 0.2387]
colors = ['#4CAF50', '#2196F3', '#FFC107', '#F44336'] # Green, Blue, Amber, Red

plt.figure(figsize=(10, 6))
bars = plt.bar(metrics, values, color=colors)

# Add title and labels
plt.title('Métricas de Desempenho do Modelo (TCC 2)', fontsize=14)
plt.ylabel('Valor (0-1)', fontsize=12)
plt.ylim(0, 1.1) # Set y-axis limit to accommodate labels

# Add value labels on top of bars
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.02, f'{yval:.4f}', ha='center', va='bottom', fontsize=11)

plt.tight_layout()
plt.savefig('grafico_metricas.png', dpi=300)
print("Graph 1 saved: grafico_metricas.png")

# --- Graph 2: Test Command Distribution ---
# Updated counts based on the 100-command test set categories
categories = [
    'Navegação Web', 'Naveg. Página', 'Sistema/Arquivos', 'Controle Texto',
    'Programas', 'Mídia/Volume', 'Customizados', 'Janelas', 'Encerramento'
]
# Counts corresponding to: 18, 8, 12, 12, 10, 15, 10, 10, 5
counts = [18, 8, 12, 12, 10, 15, 10, 10, 5]

plt.figure(figsize=(12, 6))
bars2 = plt.barh(categories, counts, color='skyblue')

# Add title and labels
plt.title('Distribuição dos Comandos de Teste por Categoria', fontsize=14)
plt.xlabel('Quantidade de Comandos', fontsize=12)
plt.xlim(0, max(counts) + 2) # Extend x-axis slightly

# Add value labels to the right of bars
plt.bar_label(bars2, padding=3, fontsize=11)

plt.tight_layout()
plt.savefig('grafico_distribuicao.png', dpi=300)
print("Graph 2 saved: grafico_distribuicao.png")