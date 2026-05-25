import torch
import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import RSLPStemmer
from nltk.corpus import stopwords

# --- 1. SETUP INICIAL ---

print(">>> Iniciando Setup...")

# Baixar recursos NLTK
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('stemmers/rslp')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('rslp')

# SEUS COMANDOS DE TREINO (A "Verdade Absoluta" do sistema)
intents_treino = {
    # Navegação
    "ABRIR_NAVEGADOR": ["Abrir navegador", "Abrir o Google", "Iniciar navegador", "Quero navegar na internet"],
    "FECHAR_NAVEGADOR": ["Fechar navegador", "Sair do Google", "Encerrar internet"],
    "NOVA_GUIA": ["Abrir nova guia", "Nova aba", "Mais uma aba", "Ctrl T"],
    "FECHAR_GUIA": ["Fechar esta guia", "Fechar aba", "Sair desta aba", "Ctrl W"],
    "ALTERNAR_GUIA_PROXIMA": ["Próxima guia", "Avançar aba", "Ctrl Tab"],
    "PESQUISAR_GOOGLE": ["Pesquisar sobre", "Buscar por", "O que é", "Quem é"],
    "PESQUISAR_PAGINA": ["Procurar por", "Buscar na página", "Encontrar na página"],
    
    # Sistema
    "ABRIR_EXPLORADOR": ["Abrir explorador de arquivos", "Abrir pastas", "Meus arquivos"],
    "ABRIR_DOCUMENTOS": ["Abrir documentos", "Pasta documentos"],
    "ABRIR_DESKTOP": ["Abrir área de trabalho", "Mostrar desktop"],
    "CRIAR_PASTA": ["Criar pasta", "Nova pasta", "Criar diretório"],
    
    # Texto
    "DIGITAR": ["Digitar", "Escrever", "Quero escrever"],
    "COPIAR": ["Copiar", "Copiar texto", "Ctrl C"],
    "COLAR": ["Colar", "Colar texto", "Ctrl V"],
    "SELECIONAR_TUDO": ["Selecionar tudo", "Marcar tudo"],
    
    # Mídia
    "ABRIR_SPOTIFY": ["Abrir Spotify", "Tocar música", "Iniciar Spotify"],
    "TOCAR_PAUSAR_MUSICA": ["Tocar música", "Pausar", "Play", "Pause"],
    "PROXIMA_MUSICA": ["Próxima música", "Pular faixa", "Avançar"],
    "AUMENTAR_VOLUME": ["Aumentar volume", "Subir o som", "Mais volume"],
    "DIMINUIR_VOLUME": ["Diminuir volume", "Baixar o som", "Menos volume"],
    "MUTAR_DESMUTAR": ["Mutar", "Silenciar", "Mudo"],
    
    # Customizados
    "ABRIR_EMULADOR_PS2": ["Abrir PS 2", "Abrir Play Station 2", "Abrir Emulador de PS 2", "Abrir PCSX 2"],
    "ABRIR_CUP_HEAD": ["Abrir CupHead", "Abra Cup Head", "Jogar Cup Head"],
    "ABRI_SQL_SERVER_STUDIO": ["Abri SQL Server", "Abrir SQL Server", "Executar SQL Server"],
    
    # Janelas
    "MINIMIZAR_JANELA": ["Minimizar janela", "Esconder janela", "Abaixar janela"],
    "MAXIMIZAR_JANELA": ["Maximizar janela", "Tela cheia", "Expandir janela"],
    "MOSTRAR_DESKTOP": ["Mostrar área de trabalho", "Minimizar tudo", "Win D"],
    "JANELA_ESQUERDA": ["Janela à esquerda", "Dividir tela esquerda"],
    "JANELA_DIREITA": ["Janela à direita", "Dividir tela direita"],
    "FECHAR_JANELA_ATUAL": ["Fechar janela", "Fechar programa", "Alt F4"],
    
    # Encerramento
    "ENCERRAR": ["Encerrar aplicação", "Sair", "Parar assistente"]
}

# 100 FRASES DE TESTE "SUJAS" (O que o usuário fala na vida real)
dataset_teste_100 = [
    # Navegação (15)
    ("eu quero abrir o navegador", "ABRIR_NAVEGADOR"),
    ("iniciar o google chrome por favor", "ABRIR_NAVEGADOR"),
    ("abre a internet ai", "ABRIR_NAVEGADOR"),
    ("fechar esse navegador", "FECHAR_NAVEGADOR"),
    ("sair do chrome agora", "FECHAR_NAVEGADOR"),
    ("encerrar a internet", "FECHAR_NAVEGADOR"),
    ("cria uma nova aba", "NOVA_GUIA"),
    ("abrir mais uma guia no navegador", "NOVA_GUIA"),
    ("fecha essa aba", "FECHAR_GUIA"),
    ("sair da guia atual", "FECHAR_GUIA"),
    ("vai para a proxima aba", "ALTERNAR_GUIA_PROXIMA"),
    ("avancar para guia da direita", "ALTERNAR_GUIA_PROXIMA"),
    ("pesquisar no google sobre python", "PESQUISAR_GOOGLE"),
    ("busca por inteligencia artificial", "PESQUISAR_GOOGLE"),
    ("procurar termo na pagina", "PESQUISAR_PAGINA"),

    # Sistema e Arquivos (15)
    ("abrir a pasta meus documentos", "ABRIR_DOCUMENTOS"),
    ("quero ver meus documentos", "ABRIR_DOCUMENTOS"),
    ("iniciar o explorador de arquivos", "ABRIR_EXPLORADOR"),
    ("abrir meu computador", "ABRIR_EXPLORADOR"),
    ("cria uma nova pasta aqui", "CRIAR_PASTA"),
    ("fazer um novo diretorio", "CRIAR_PASTA"),
    ("abrir area de trabalho", "ABRIR_DESKTOP"),
    ("ver meus icones", "ABRIR_DESKTOP"),
    ("mostrar desktop agora", "MOSTRAR_DESKTOP"),
    ("ir para o desktop", "MOSTRAR_DESKTOP"),
    ("esconder tudo", "MOSTRAR_DESKTOP"),
    ("minimizar todas as janelas", "MOSTRAR_DESKTOP"),
    ("win d", "MOSTRAR_DESKTOP"),
    ("abrir pasta de documentos", "ABRIR_DOCUMENTOS"),
    ("acessar arquivos", "ABRIR_EXPLORADOR"),

    # Texto (15)
    ("quero digitar um texto", "DIGITAR"),
    ("escreve ola mundo", "DIGITAR"),
    ("copia isso", "COPIAR"),
    ("fazer uma copia do texto", "COPIAR"),
    ("cola aqui", "COLAR"),
    ("colar o conteudo", "COLAR"),
    ("seleciona tudo por favor", "SELECIONAR_TUDO"),
    ("marcar o texto todo", "SELECIONAR_TUDO"),
    ("quero escrever uma carta", "DIGITAR"),
    ("digite para mim", "DIGITAR"),
    ("ctrl c", "COPIAR"),
    ("copiar selecao", "COPIAR"),
    ("colar agora", "COLAR"),
    ("ctrl v", "COLAR"),
    ("selecionar a pagina toda", "SELECIONAR_TUDO"),

    # Mídia (20)
    ("abrir o aplicativo do spotify", "ABRIR_SPOTIFY"),
    ("quero escutar spotify", "ABRIR_SPOTIFY"),
    ("iniciar app de musica", "ABRIR_SPOTIFY"),
    ("solta o som", "TOCAR_PAUSAR_MUSICA"),
    ("pausa a musica ai", "TOCAR_PAUSAR_MUSICA"),
    ("dar play na musica", "TOCAR_PAUSAR_MUSICA"),
    ("passar para a proxima", "PROXIMA_MUSICA"),
    ("pula essa musica", "PROXIMA_MUSICA"),
    ("aumenta esse volume", "AUMENTAR_VOLUME"),
    ("som mais alto", "AUMENTAR_VOLUME"),
    ("abaixa o som", "DIMINUIR_VOLUME"),
    ("volume mais baixo por favor", "DIMINUIR_VOLUME"),
    ("fica em silencio", "MUTAR_DESMUTAR"),
    ("cortar o som", "MUTAR_DESMUTAR"),
    ("volta o som", "MUTAR_DESMUTAR"),
    ("quero ouvir musica alta", "AUMENTAR_VOLUME"),
    ("parar o barulho", "MUTAR_DESMUTAR"),
    ("tocar", "TOCAR_PAUSAR_MUSICA"),
    ("proxima faixa", "PROXIMA_MUSICA"),
    ("volume maximo", "AUMENTAR_VOLUME"),

    # Customizados e Janelas (20)
    ("abrir emulador de ps2", "ABRIR_EMULADOR_PS2"),
    ("iniciar o pcsx2 agora", "ABRIR_EMULADOR_PS2"),
    ("quero jogar playstation", "ABRIR_EMULADOR_PS2"),
    ("jogar cuphead agora", "ABRIR_CUP_HEAD"),
    ("iniciar o jogo do xicrinho", "ABRIR_CUP_HEAD"),
    ("abrir banco de dados sql", "ABRI_SQL_SERVER_STUDIO"),
    ("rodar o management studio", "ABRI_SQL_SERVER_STUDIO"),
    ("minimizar essa tela", "MINIMIZAR_JANELA"),
    ("esconde a janela", "MINIMIZAR_JANELA"),
    ("deixa em tela cheia", "MAXIMIZAR_JANELA"),
    ("aumenta a janela", "MAXIMIZAR_JANELA"),
    ("coloca a janela na esquerda", "JANELA_ESQUERDA"),
    ("joga pra esquerda", "JANELA_ESQUERDA"),
    ("janela na direita", "JANELA_DIREITA"),
    ("divide a tela na direita", "JANELA_DIREITA"),
    ("fechar o programa atual", "FECHAR_JANELA_ATUAL"),
    ("sair dessa janela", "FECHAR_JANELA_ATUAL"),
    ("abrir o ssms", "ABRI_SQL_SERVER_STUDIO"),
    ("jogar cup head", "ABRIR_CUP_HEAD"),
    ("abrir emulador", "ABRIR_EMULADOR_PS2"),

    # Encerramento (15)
    ("encerrar aplicação", "ENCERRAR"),
    ("sair do sistema", "ENCERRAR"),
    ("fechar assistente", "ENCERRAR"),
    ("desligar assistente", "ENCERRAR"),
    ("parar execução", "ENCERRAR"),
    ("tchau", "ENCERRAR"),
    ("até logo", "ENCERRAR"),
    ("finalizar programa", "ENCERRAR"),
    ("encerrar tudo", "ENCERRAR"),
    ("sair agora", "ENCERRAR"),
    ("fechar o bot", "ENCERRAR"),
    ("parar de ouvir", "ENCERRAR"),
    ("desligar tudo", "ENCERRAR"),
    ("encerrar o assistente", "ENCERRAR"),
    ("fechar aplicativo", "ENCERRAR")
]

# --- 2. CONFIGURAÇÃO DOS MODELOS ---

# NLTK Setup
def preprocess_nltk(texto):
    stop_words = set(stopwords.words("portuguese"))
    stemmer = RSLPStemmer()
    try: tokens = word_tokenize(texto.lower(), language='portuguese')
    except: tokens = texto.lower().split()
    return " ".join([stemmer.stem(w) for w in tokens if w.isalnum() and w not in stop_words])

corpus_nltk = []
for frases in intents_treino.values():
    for f in frases: corpus_nltk.append(preprocess_nltk(f))

vectorizer = TfidfVectorizer()
X_nltk_treino = vectorizer.fit_transform(corpus_nltk)

def get_similarity_nltk(frase, intent_esperada):
    entrada = preprocess_nltk(frase)
    vec_entrada = vectorizer.transform([entrada])
    # Compara com as frases da intenção correta para ver o "match"
    frases_alvo = intents_treino.get(intent_esperada, [])
    if not frases_alvo: return 0.0
    vec_alvo = vectorizer.transform([preprocess_nltk(f) for f in frases_alvo])
    sims = cosine_similarity(vec_entrada, vec_alvo)
    return np.max(sims) if sims.size > 0 else 0.0

# BERT Setup (BERTugues)
print(">>> Carregando BERTugues (Isso pode demorar)...")
try:
    NOME_MODELO = 'lpedotti/bertugues-cased'
    tokenizer_bert = AutoTokenizer.from_pretrained(NOME_MODELO)
    model_bert = AutoModel.from_pretrained(NOME_MODELO)
except Exception as e:
    print(f"Erro ao carregar BERTugues: {e}. Usando 'neuralmind/bert-base-portuguese-cased' como fallback.")
    NOME_MODELO = 'neuralmind/bert-base-portuguese-cased'
    tokenizer_bert = AutoTokenizer.from_pretrained(NOME_MODELO)
    model_bert = AutoModel.from_pretrained(NOME_MODELO)

def get_bert_embedding(text):
    inputs = tokenizer_bert(text, return_tensors="pt", padding=True, truncation=True, max_length=64)
    with torch.no_grad(): outputs = model_bert(**inputs)
    return outputs.last_hidden_state.mean(dim=1).numpy()

print(">>> Gerando embeddings de treino BERT...")
embeddings_treino_map = {}
for intent, frases in intents_treino.items():
    embeddings_treino_map[intent] = np.vstack([get_bert_embedding(f) for f in frases])

def get_similarity_bert(frase, intent_esperada):
    if intent_esperada not in embeddings_treino_map: return 0.0
    emb_entrada = get_bert_embedding(frase)
    emb_alvos = embeddings_treino_map[intent_esperada]
    sims = cosine_similarity(emb_entrada, emb_alvos)
    return np.max(sims)

# --- 3. EXECUÇÃO DO BENCHMARK ---

resultados = []
print(f"\n>>> Processando {len(dataset_teste_100)} frases de teste...\n")
print(f"{'COMANDO FALADO':<40} | {'BERT':<6} | {'NLTK':<6}")
print("-" * 60)

for comando, intent_real in dataset_teste_100:
    sim_nltk = get_similarity_nltk(comando, intent_real)
    sim_bert = get_similarity_bert(comando, intent_real)
    
    # Formatação para tabela
    resultados.append({
        "Comando Falado": comando,
        "Intenção Esperada": intent_real,
        "Simil. BERTugues": f"{sim_bert:.4f}".replace('.', ','),
        "Simil. NLTK": f"{sim_nltk:.4f}".replace('.', ',')
    })
    
    print(f"{comando[:40]:<40} | {sim_bert:.3f}  | {sim_nltk:.3f}")

# --- 4. SALVAR CSV ---
df = pd.DataFrame(resultados)
nome_arquivo = "tabela_comparativa_full_100.csv"
df.to_csv(nome_arquivo, index=False, sep=';', encoding='utf-8-sig')

print("-" * 60)
print(f"Sucesso! Arquivo '{nome_arquivo}' gerado.")
print("Copie o conteúdo do CSV para o seu TCC.")