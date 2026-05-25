import sys
import os
import numpy as np
from sklearn.metrics import accuracy_score, f1_score

# --- CONFIGURAÇÃO DE CAMINHO ---
# Garante que o script encontre a pasta 'src' mesmo rodando de dentro de 'tests'
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from src.services.nlp_service import IntentInterpreter
    from src.model.config_manager import ConfigManager
except ImportError as e:
    print("ERRO DE IMPORTAÇÃO: Verifique se a estrutura de pastas está correta.")
    print(f"Detalhe: {e}")
    sys.exit(1)

# --- FUNÇÕES DE MÉTRICA (Levenshtein manual para não depender de libs externas) ---
def levenshtein(s1, s2):
    if len(s1) < len(s2): return levenshtein(s2, s1)
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

def calcular_wer_robusto(frase_falada, lista_frases_treino):
    """
    Calcula o quão diferente a frase falada é da frase de treino mais próxima.
    WER = Distância / Comprimento da Referência
    """
    if not lista_frases_treino: return 1.0
    
    melhor_wer = float('inf')
    falada_norm = frase_falada.lower().split()
    
    for referencia in lista_frases_treino:
        ref_norm = referencia.lower().split()
        s1, s2 = " ".join(falada_norm), " ".join(ref_norm)
        dist = levenshtein(s1, s2)
        comp = len(s2)
        wer = dist / comp if comp > 0 else 0
        if wer < melhor_wer: melhor_wer = wer
            
    return melhor_wer

# --- DATASET "SUJO" (100 FRASES COM VARIAÇÕES NATURAIS) ---
def get_dirty_dataset():
    return [
        # Navegação (20) - Adicionando "quero", "por favor", "agora"
        ("eu quero abrir o navegador", "ABRIR_NAVEGADOR"),
        ("iniciar o google chrome por favor", "ABRIR_NAVEGADOR"),
        ("abre a internet ai", "ABRIR_NAVEGADOR"),
        ("acessar o navegador", "ABRIR_NAVEGADOR"),
        ("fechar esse navegador", "FECHAR_NAVEGADOR"),
        ("sair do chrome agora", "FECHAR_NAVEGADOR"),
        ("encerrar a internet", "FECHAR_NAVEGADOR"),
        ("cria uma nova aba", "NOVA_GUIA"),
        ("abrir mais uma guia no navegador", "NOVA_GUIA"),
        ("fecha essa aba", "FECHAR_GUIA"),
        ("sair da guia atual", "FECHAR_GUIA"),
        ("vai para a proxima aba", "ALTERNAR_GUIA_PROXIMA"),
        ("avancar para guia da direita", "ALTERNAR_GUIA_PROXIMA"),
        ("volta para a aba anterior", "ALTERNAR_GUIA_ANTERIOR"),
        ("guia da esquerda", "ALTERNAR_GUIA_ANTERIOR"),
        ("atualiza essa pagina", "ATUALIZAR_PAGINA"),
        ("recarregar o site", "ATUALIZAR_PAGINA"),
        ("pesquisar no google sobre python", "PESQUISAR_GOOGLE"),
        ("busca por inteligencia artificial", "PESQUISAR_GOOGLE"),
        ("procurar termo na pagina", "PESQUISAR_PAGINA"),

        # Sistema e Arquivos (15) - Trocando termos ("meus docs", "pasta")
        ("abrir a pasta meus documentos", "ABRIR_DOCUMENTOS"),
        ("quero ver meus documentos", "ABRIR_DOCUMENTOS"),
        ("abrir pasta de downloads agora", "ABRIR_DOWNLOADS_PASTA"),
        ("ver meus downloads", "ABRIR_DOWNLOADS_PASTA"),
        ("mostrar minhas fotos", "ABRIR_IMAGENS"),
        ("abrir diretorio de imagens", "ABRIR_IMAGENS"),
        ("tocar minhas musicas", "ABRIR_MUSICAS"),
        ("abrir pasta de videos", "ABRIR_VIDEOS"),
        ("iniciar o explorador de arquivos", "ABRIR_EXPLORADOR"),
        ("abrir meu computador", "ABRIR_EXPLORADOR"),
        ("acessar o disco local c", "ABRIR_DISCO"),
        ("cria uma nova pasta aqui", "CRIAR_PASTA"),
        ("fazer um novo diretorio", "CRIAR_PASTA"),
        ("mudar o nome do arquivo", "RENOMEAR_SELECIONADO"),
        ("renomear isso", "RENOMEAR_SELECIONADO"),

        # Texto e Edição (15) - Verbos conjugados
        ("quero digitar um texto", "DIGITAR"),
        ("escreve ola mundo", "DIGITAR"),
        ("copia isso", "COPIAR"),
        ("fazer uma copia do texto", "COPIAR"),
        ("cola aqui", "COLAR"),
        ("colar o conteudo", "COLAR"),
        ("recorta esse arquivo", "RECORTAR"),
        ("mover seleção", "RECORTAR"),
        ("seleciona tudo por favor", "SELECIONAR_TUDO"),
        ("marcar o texto todo", "SELECIONAR_TUDO"),
        ("apaga isso", "APAGAR"),
        ("deletar texto", "APAGAR"),
        ("confirma o envio", "CONFIRMAR_ENVIO"),
        ("apertar enter", "CONFIRMAR_ENVIO"),
        ("pode enviar", "CONFIRMAR_ENVIO"),

        # Apps e Produtividade (15)
        ("abrir o bloco de notas rapido", "ABRIR_BLOCO_DE_NOTAS"),
        ("anotar alguma coisa", "ABRIR_BLOCO_DE_NOTAS"),
        ("preciso da calculadora", "ABRIR_CALCULADORA"),
        ("fazer um calculo", "ABRIR_CALCULADORA"),
        ("iniciar o microsoft word", "ABRIR_WORD"),
        ("escrever um documento no word", "ABRIR_WORD"),
        ("abrir o excel agora", "ABRIR_EXCEL"),
        ("fazer uma planilha", "ABRIR_EXCEL"),
        ("abrir o aplicativo do spotify", "ABRIR_SPOTIFY"),
        ("quero escutar spotify", "ABRIR_SPOTIFY"),
        ("iniciar app de musica", "ABRIR_SPOTIFY"),
        ("minimizar janela do spotify", "MINIMIZAR_JANELA"), # Teste cruzado
        ("maximizar o word", "MAXIMIZAR_JANELA"), # Teste cruzado
        ("fechar o excel", "FECHAR_JANELA_ATUAL"), # Intenção genérica
        ("sair do bloco de notas", "FECHAR_JANELA_ATUAL"),

        # Mídia e Volume (15)
        ("solta o som", "TOCAR_PAUSAR_MUSICA"),
        ("pausa a musica ai", "TOCAR_PAUSAR_MUSICA"),
        ("passar para a proxima", "PROXIMA_MUSICA"),
        ("pula essa musica", "PROXIMA_MUSICA"),
        ("volta a musica", "MUSICA_ANTERIOR"),
        ("toca a anterior", "MUSICA_ANTERIOR"),
        ("aumenta esse volume", "AUMENTAR_VOLUME"),
        ("som mais alto", "AUMENTAR_VOLUME"),
        ("abaixa o som", "DIMINUIR_VOLUME"),
        ("volume mais baixo por favor", "DIMINUIR_VOLUME"),
        ("fica em silencio", "MUTAR_DESMUTAR"),
        ("cortar o som", "MUTAR_DESMUTAR"),
        ("volta o som", "MUTAR_DESMUTAR"),
        ("quero ouvir musica alta", "AUMENTAR_VOLUME"),
        ("parar o barulho", "MUTAR_DESMUTAR"),

        # Customizados e Janelas (20) - Os mais difíceis
        ("abrir emulador de ps2", "ABRIR_EMULADOR_PS2"),
        ("iniciar o pcsx2 agora", "ABRIR_EMULADOR_PS2"),
        ("quero jogar playstation", "ABRIR_EMULADOR_PS2"),
        ("jogar cuphead agora", "ABRIR_CUP_HEAD"),
        ("iniciar o jogo do xicrinho", "ABRIR_CUP_HEAD"), # Variação difícil (pode falhar, bom pro teste)
        ("abrir banco de dados sql", "ABRI_SQL_SERVER_STUDIO"),
        ("rodar o management studio", "ABRI_SQL_SERVER_STUDIO"),
        ("minimizar essa tela", "MINIMIZAR_JANELA"),
        ("esconde a janela", "MINIMIZAR_JANELA"),
        ("deixa em tela cheia", "MAXIMIZAR_JANELA"),
        ("aumenta a janela", "MAXIMIZAR_JANELA"),
        ("volta ao tamanho normal", "RESTAURAR_JANELA"),
        ("restaurar janela", "RESTAURAR_JANELA"),
        ("mostra meu desktop", "MOSTRAR_DESKTOP"),
        ("ir para area de trabalho", "MOSTRAR_DESKTOP"),
        ("coloca a janela na esquerda", "JANELA_ESQUERDA"),
        ("joga pra esquerda", "JANELA_ESQUERDA"),
        ("janela na direita", "JANELA_DIREITA"),
        ("divide a tela na direita", "JANELA_DIREITA"),
        ("fechar o programa atual", "FECHAR_JANELA_ATUAL")
    ]

# --- EXECUÇÃO DO BENCHMARK ---
def run():
    print("--- INICIANDO TESTE DE ROBUSTEZ (100 FRASES VARIADAS) ---\n")
    
    # 1. Carrega o sistema real
    config = ConfigManager()
    nlp = IntentInterpreter(config)
    
    # Treina com os dados do JSON (Dados Limpos)
    # Isso é importante: o modelo treina com "Abrir navegador", mas vamos testar com "Eu quero abrir..."
    nlp.train_or_load_model(force_retrain=True)
    todos_comandos_treino = config.get_commands()
    
    dataset = get_dirty_dataset()
    
    # Variáveis de métrica
    y_true = []
    y_pred = []
    similarities = []
    wers = []
    
    print(f"{'FRASE (INPUT)':<40} | {'PREDITO':<25} | {'SIMIL.'} | {'WER'}")
    print("-" * 90)
    
    for frase, esperado in dataset:
        # Predição
        predito, score = nlp.predict(frase, threshold=0.0) # Threshold 0 para pegar o melhor palpite
        label = predito if predito else "NÃO_RECONHECIDO"
        
        # Métricas
        y_true.append(esperado)
        y_pred.append(label)
        similarities.append(score)
        
        # WER: Compara a frase falada ("eu quero abrir...") com a melhor frase de treino ("abrir...")
        # Isso mostra o quanto o usuário "errou" em relação ao comando padrão
        frases_ref = todos_comandos_treino.get(esperado, [])
        wer = calcular_wer_robusto(frase, frases_ref)
        wers.append(wer)
        
        # Visualização (apenas os primeiros 10 e erros para não poluir)
        match = "✅" if label == esperado else "❌"
        print(f"{frase[:40]:<40} | {label[:25]:<25} | {score:.2f}   | {wer:.2f} {match}")

    # --- CÁLCULO FINAL ---
    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average='weighted')
    avg_sim = np.mean(similarities)
    avg_wer = np.mean(wers)
    
    print("-" * 90)
    print("\n>>> RESULTADOS CONSOLIDADOS (TCC 2) <<<")
    print(f"Total de Testes:    {len(dataset)}")
    print(f"Acurácia:           {acc:.4f} ({acc*100:.1f}%)")
    print(f"F1-Score:           {f1:.4f}")
    print(f"Similaridade Média: {avg_sim:.4f} (Não deve ser 1.0)")
    print(f"WER Médio:          {avg_wer:.4f} (Indica variação textual)")
    
    # Salvar em arquivo para você copiar pro TCC
    with open("resultado_metricas_final.txt", "w") as f:
        f.write(f"Acurácia: {acc:.4f}\nF1-Score: {f1:.4f}\nSimilaridade: {avg_sim:.4f}\nWER: {avg_wer:.4f}")

if __name__ == "__main__":
    run()