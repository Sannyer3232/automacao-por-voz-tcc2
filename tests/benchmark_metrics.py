import sys
import os
import json
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import Levenshtein # pip install python-Levenshtein

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.nlp_service import IntentInterpreter
from src.model.config_manager import ConfigManager

def calcular_wer(referencia, hipotese):
    """Calcula o Word Error Rate entre duas strings"""
    ref_words = referencia.lower().split()
    hyp_words = hipotese.lower().split()
    # Usando distância de Levenshtein nas palavras
    dist = Levenshtein.distance(referencia.lower(), hipotese.lower())
    # Aproximação simples de WER baseada em caracteres/palavras para o contexto
    # Para WER real de ASR, precisaríamos dos áudios originais. 
    # Aqui calculamos a taxa de erro textual.
    return dist / len(referencia) if len(referencia) > 0 else 0

def run_benchmark():
    # 1. Setup
    config = ConfigManager()
    nlp = IntentInterpreter(config)
    
    # 2. Carregar Dataset de Teste (Exemplo hardcoded ou carregar de arquivo)
    # No seu TCC use o arquivo completo
    dataset_teste = [
        ("abrir o google", "ABRIR_NAVEGADOR"),
        ("iniciar navegador", "ABRIR_NAVEGADOR"),
        ("tocar musica", "TOCAR_PAUSAR_MUSICA"),
        ("parar som", "PAUSAR_MUSICA"), # Supondo erro intencional ou variação
        ("quero criar uma pasta", "CRIAR_PASTA"),
        # ... adicione seus 100 comandos aqui
    ]

    y_true = []
    y_pred = []
    similarities = []
    wers = []

    print(f"Iniciando benchmark com {len(dataset_teste)} amostras...")
    print("-" * 60)
    print(f"{'Comando':<30} | {'Esperado':<20} | {'Predito':<20} | {'Simil.':<5}")
    print("-" * 60)

    for comando, intencao_real in dataset_teste:
        # Predição
        intencao_predita, score = nlp.predict(comando, threshold=0.0) # Threshold 0 para forçar uma escolha
        
        y_true.append(intencao_real)
        y_pred.append(intencao_predita if intencao_predita else "NAO_RECONHECIDO")
        similarities.append(score)
        
        # WER (Aqui comparamos o texto de entrada com a frase "canônica" do comando se houvesse reconversão, 
        # mas como estamos testando classificação, o WER se aplica à transcrição do ASR.
        # Se você tiver o áudio e o texto transcrito pelo SpeechRecognition, você compara os dois.)
        
        print(f"{comando:<30} | {intencao_real:<20} | {str(intencao_predita):<20} | {score:.3f}")

    print("-" * 60)
    
    # 3. Cálculo das Métricas [cite: 17, 707]
    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average='weighted')
    avg_sim = np.mean(similarities)
    
    print("\nRESULTADOS DO BENCHMARK (TF-IDF + NLTK):")
    print(f"Acurácia: {acc*100:.2f}%")
    print(f"F1-Score: {f1*100:.2f}%")
    print(f"Similaridade Média do Cosseno: {avg_sim:.4f}")
    
    # Salvar relatório
    with open("tests/resultado_benchmark.txt", "w") as f:
        f.write(f"Acurácia: {acc}\nF1: {f1}\nSimilaridade Média: {avg_sim}")

if __name__ == "__main__":
    run_benchmark()