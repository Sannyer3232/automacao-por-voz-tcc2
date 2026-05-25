import sys
import os
import numpy as np
import json
from sklearn.metrics import accuracy_score, f1_score

# --- CONFIGURAÇÃO DE CAMINHO ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from src.services.nlp_service import IntentInterpreter
    from src.model.config_manager import ConfigManager
except ImportError as e:
    print("ERRO: Execute este script a partir da pasta raiz do projeto.")
    sys.exit(1)

# --- FUNÇÕES DE MÉTRICA (SEM DEPENDÊNCIAS EXTERNAS) ---

def levenshtein_distance(s1, s2):
    """Calcula a distância de edição (caracteres) entre duas strings."""
    if len(s1) < len(s2): return levenshtein_distance(s2, s1)
    if len(s2) == 0: return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def calcular_wer_relativo(frase_falada, lista_frases_treino):
    """
    Calcula o WER comparando a frase falada com a frase de treino MAIS PARECIDA.
    Isso mede o quão 'distante' a fala do usuário estava do comando ideal.
    """
    if not lista_frases_treino: return 1.0 # Erro total se não houver referência
    
    melhor_wer = float('inf')
    
    falada_norm = frase_falada.lower().split()
    
    for referencia in lista_frases_treino:
        ref_norm = referencia.lower().split()
        
        # Reconstrói strings para Levenshtein de caracteres (aproximação robusta)
        s1 = " ".join(falada_norm)
        s2 = " ".join(ref_norm)
        
        dist = levenshtein_distance(s1, s2)
        comprimento_ref = len(s2)
        
        # WER = Distância / Comprimento da Referência
        wer_atual = dist / comprimento_ref if comprimento_ref > 0 else 0
        
        if wer_atual < melhor_wer:
            melhor_wer = wer_atual
            
    return melhor_wer

# --- DATASET DE TESTE ---
def get_test_data():
    return [
        # --- NAVEGAÇÃO WEB (18 Comandos) ---
        ("abrir o navegador", "ABRIR_NAVEGADOR"),
        ("iniciar o google chrome", "ABRIR_NAVEGADOR"),
        ("quero acessar a internet", "ABRIR_NAVEGADOR"),
        ("fechar navegador", "FECHAR_NAVEGADOR"),
        ("sair do google chrome", "FECHAR_NAVEGADOR"),
        ("nova aba por favor", "NOVA_GUIA"),
        ("abrir mais uma guia", "NOVA_GUIA"),
        ("fechar esta aba", "FECHAR_GUIA"),
        ("encerrar guia atual", "FECHAR_GUIA"),
        ("ir para a proxima aba", "ALTERNAR_GUIA_PROXIMA"),
        ("avancar guia", "ALTERNAR_GUIA_PROXIMA"),
        ("voltar para a aba anterior", "ALTERNAR_GUIA_ANTERIOR"),
        ("guia da esquerda", "ALTERNAR_GUIA_ANTERIOR"),
        ("atualizar a pagina", "ATUALIZAR_PAGINA"),
        ("pesquisar sobre inteligência artificial", "PESQUISAR_GOOGLE"),
        ("buscar no google por python", "PESQUISAR_GOOGLE"),
        ("procurar na pagina", "PESQUISAR_PAGINA"),
        ("localizar palavra", "PESQUISAR_PAGINA"),

        # --- NAVEGAÇÃO NA PÁGINA (8 Comandos) ---
        ("rolar para baixo", "ROLAR_BAIXO"),
        ("descer a tela", "ROLAR_BAIXO"),
        ("rolar para cima", "ROLAR_CIMA"),
        ("subir a pagina", "ROLAR_CIMA"),
        ("ir para o topo", "TOPO_PAGINA"),
        ("voltar ao inicio", "TOPO_PAGINA"),
        ("ir para o final", "FINAL_PAGINA"),
        ("descer tudo", "FINAL_PAGINA"),

        # --- SISTEMA E ARQUIVOS (12 Comandos) ---
        ("abrir meus documentos", "ABRIR_DOCUMENTOS"),
        ("pasta documentos", "ABRIR_DOCUMENTOS"),
        ("abrir pasta de downloads", "ABRIR_DOWNLOADS_PASTA"),
        ("mostrar minhas imagens", "ABRIR_IMAGENS"),
        ("abrir pasta de musicas", "ABRIR_MUSICAS"),
        ("abrir o explorador", "ABRIR_EXPLORADOR"),
        ("explorador de arquivos", "ABRIR_EXPLORADOR"),
        ("acessar disco c", "ABRIR_DISCO"),
        ("quero criar uma pasta", "CRIAR_PASTA"),
        ("nova pasta", "CRIAR_PASTA"),
        ("abrir area de trabalho", "ABRIR_DESKTOP"),
        ("listar arquivos", "LISTAR_ARQUIVOS"),

        # --- CONTROLE DE TEXTO (12 Comandos) ---
        ("digitar ola mundo", "DIGITAR"),
        ("escrever texto", "DIGITAR"),
        ("copiar texto", "COPIAR"),
        ("copiar selecao", "COPIAR"),
        ("colar aqui", "COLAR"),
        ("colar texto", "COLAR"),
        ("recortar arquivo", "RECORTAR"),
        ("mover selecao", "RECORTAR"),
        ("selecionar tudo", "SELECIONAR_TUDO"),
        ("marcar todo o texto", "SELECIONAR_TUDO"),
        ("apagar isso", "APAGAR"),
        ("confirmar envio", "CONFIRMAR_ENVIO"),

        # --- PROGRAMAS (10 Comandos) ---
        ("abrir bloco de notas", "ABRIR_BLOCO_DE_NOTAS"),
        ("iniciar notepad", "ABRIR_BLOCO_DE_NOTAS"),
        ("abrir calculadora", "ABRIR_CALCULADORA"),
        ("fazer contas", "ABRIR_CALCULADORA"),
        ("abrir word", "ABRIR_WORD"),
        ("iniciar microsoft word", "ABRIR_WORD"),
        ("abrir excel", "ABRIR_EXCEL"),
        ("abrir planilhas", "ABRIR_EXCEL"),
        ("abrir spotify", "ABRIR_SPOTIFY"),
        ("iniciar o spotify", "ABRIR_SPOTIFY"),

        # --- MÍDIA E VOLUME (15 Comandos) ---
        ("tocar musica", "TOCAR_PAUSAR_MUSICA"),
        ("pausar som", "TOCAR_PAUSAR_MUSICA"),
        ("proxima musica", "PROXIMA_MUSICA"),
        ("pular faixa", "PROXIMA_MUSICA"),
        ("musica anterior", "MUSICA_ANTERIOR"),
        ("voltar faixa", "MUSICA_ANTERIOR"),
        ("aumentar o volume", "AUMENTAR_VOLUME"),
        ("subir o som", "AUMENTAR_VOLUME"),
        ("mais alto por favor", "AUMENTAR_VOLUME"),
        ("diminuir volume", "DIMINUIR_VOLUME"),
        ("baixar o som", "DIMINUIR_VOLUME"),
        ("falar mais baixo", "DIMINUIR_VOLUME"),
        ("ficar mudo", "MUTAR_DESMUTAR"),
        ("silenciar tudo", "MUTAR_DESMUTAR"),
        ("ativar o som", "MUTAR_DESMUTAR"),

        # --- NOVOS COMANDOS CUSTOMIZADOS (10 Comandos) ---
        ("abrir emulador ps2", "ABRIR_EMULADOR_PS2"),
        ("iniciar pcsx2", "ABRIR_EMULADOR_PS2"),
        ("quero jogar play station 2", "ABRIR_EMULADOR_PS2"),
        ("quero jogar cuphead", "ABRIR_CUP_HEAD"),
        ("abrir o jogo cup head", "ABRIR_CUP_HEAD"),
        ("iniciar cuphead", "ABRIR_CUP_HEAD"),
        ("abrir sql server", "ABRI_SQL_SERVER_STUDIO"),
        ("iniciar sql server", "ABRI_SQL_SERVER_STUDIO"),
        ("executar management studio", "ABRI_SQL_SERVER_STUDIO"),
        ("abrir o ssms", "ABRI_SQL_SERVER_STUDIO"),

        # --- GERENCIAMENTO DE JANELAS (10 Comandos) ---
        ("minimizar janela", "MINIMIZAR_JANELA"),
        ("esconder essa tela", "MINIMIZAR_JANELA"),
        ("maximizar tela", "MAXIMIZAR_JANELA"),
        ("tela cheia", "MAXIMIZAR_JANELA"),
        ("restaurar tamanho", "RESTAURAR_JANELA"),
        ("mostrar area de trabalho", "MOSTRAR_DESKTOP"),
        ("colocar janela na esquerda", "JANELA_ESQUERDA"),
        ("janela direita", "JANELA_DIREITA"),
        ("fechar janela atual", "FECHAR_JANELA_ATUAL"),
        ("alternar janela", "ALTERNAR_JANELA"),

        # --- ENCERRAMENTO (5 Comandos) ---
        ("encerrar aplicação", "ENCERRAR"),
        ("sair do sistema", "ENCERRAR"),
        ("fechar assistente", "ENCERRAR"),
        ("parar execução", "ENCERRAR"),
        ("deletar arquivo", "DELETAR_ARQUIVO")
    ]

# --- EXECUÇÃO ---
def run_benchmark():
    print("--- INICIANDO BENCHMARK (TCC 2) ---\n")
    
    config = ConfigManager()
    nlp = IntentInterpreter(config)
    # Pega todos os comandos de treino para comparar o WER
    todos_comandos_treino = config.get_commands() 
    
    dataset = get_test_data()
    y_true, y_pred, scores, wers = [], [], [], []
    acertos = 0
    
    print(f"{'FRASE FALADA':<35} | {'PREDITO':<25} | {'CONF.(%)'} | {'WER'}")
    print("-" * 85)

    for frase, esperado in dataset:
        # 1. Predição
        predito, score = nlp.predict(frase, threshold=0.0)
        label_predito = predito if predito else "NÃO_RECONHECIDO"
        
        # 2. Cálculo do WER (Input vs Treino da Intenção ESPERADA)
        # Comparar com o treino da intenção correta mostra o quão robusto o modelo foi
        frases_referencia = todos_comandos_treino.get(esperado, [])
        wer = calcular_wer_relativo(frase, frases_referencia)
        
        # Coleta dados
        y_true.append(esperado)
        y_pred.append(label_predito)
        scores.append(score)
        wers.append(wer)
        
        if label_predito == esperado: acertos += 1
        icon = "✅" if label_predito == esperado else "❌"
        
        print(f"{frase:<35} | {label_predito:<25} | {score*100:.1f}%    | {wer:.2f} {icon}")

    # 3. Resultados Consolidados
    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average='weighted')
    avg_wer = np.mean(wers)
    avg_sim = np.mean(scores)
    
    print("-" * 85)
    print(f"Total: {len(dataset)} | Acertos: {acertos}")
    print(f"\n>>> MÉTRICAS FINAIS PARA O TCC <<<")
    print(f"Acurácia:           {acc:.4f} ({acc*100:.1f}%)")
    print(f"F1-Score:           {f1:.4f}")
    print(f"WER Médio (Texto):  {avg_wer:.4f}")
    print(f"Similaridade Média: {avg_sim:.4f}")

if __name__ == "__main__":
    run_benchmark()