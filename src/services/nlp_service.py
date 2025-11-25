# src/services/nlp_service.py
import joblib
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
from nltk.stem import RSLPStemmer
from nltk.corpus import stopwords
import nltk

class IntentInterpreter:
    def __init__(self, config_manager):
        self.config = config_manager
        self.model_path = "data/tfidf_model.joblib"
        self.vectorizer = None
        self.intents_map = {} # Cache dos comandos
        
        # Configura dependências do NLTK
        self.setup_nltk()
        
        # Carrega ou treina o modelo
        self.train_or_load_model()

    def setup_nltk(self):
        """
        Verifica e baixa todos os recursos necessários do NLTK.
        Inclui 'punkt_tab' que é exigido em versões recentes.
        """
        required_packages = ['punkt', 'punkt_tab', 'stopwords', 'rslp']
        
        for package in required_packages:
            try:
                # Tenta encontrar ou baixar silenciosamente
                nltk.download(package, quiet=True)
            except Exception as e:
                print(f"Aviso: Não foi possível verificar/baixar {package}: {e}")

    def preprocess(self, text):
        stop_words = set(stopwords.words("portuguese"))
        stemmer = RSLPStemmer()
        
        # Tokenização (agora com punkt_tab garantido)
        # Forçamos o idioma portuguese se disponível, mas o default costuma funcionar
        try:
            tokens = word_tokenize(text.lower(), language='portuguese')
        except LookupError:
            # Fallback caso o modelo portuguese específico falhe
            tokens = word_tokenize(text.lower())
            
        return " ".join([stemmer.stem(w) for w in tokens if w.isalnum() and w not in stop_words])

    def train_or_load_model(self, force_retrain=False):
        self.intents_map = self.config.get_commands()
        
        # Prepara dados
        corpus = []
        for intent, phrases in self.intents_map.items():
            for phrase in phrases:
                corpus.append(self.preprocess(phrase))

        if os.path.exists(self.model_path) and not force_retrain:
            self.vectorizer = joblib.load(self.model_path)
        else:
            os.makedirs("data", exist_ok=True)
            self.vectorizer = TfidfVectorizer()
            if corpus: # Garante que há dados para treinar
                self.vectorizer.fit(corpus)
                joblib.dump(self.vectorizer, self.model_path)
            else:
                print("ERRO: Corpus vazio. Verifique o arquivo comandos.json")

    def predict(self, command_text, threshold=0.5):
        if not command_text or not self.vectorizer: 
            return None, 0.0

        processed_input = self.preprocess(command_text)
        
        # Proteção caso o vocabulário do modelo não conheça nenhuma palavra da entrada
        try:
            input_vec = self.vectorizer.transform([processed_input])
        except Exception:
            return None, 0.0

        best_intent = None
        best_score = 0.0

        # Lógica de similaridade do cosseno
        for intent, phrases in self.intents_map.items():
            # Otimização: idealmente pré-calcularíamos isso no treino, 
            # mas para TCC manter assim é didático e funcional para listas pequenas
            phrase_vecs = self.vectorizer.transform([self.preprocess(p) for p in phrases])
            similarities = cosine_similarity(input_vec, phrase_vecs)
            max_sim = np.max(similarities)

            if max_sim > best_score:
                best_score = max_sim
                best_intent = intent

        # Usa o limiar configurado pelo usuário se disponível
        user_threshold = self.config.get_preference("limiar_confianca")
        if user_threshold is not None:
            threshold = user_threshold

        if best_score >= threshold:
            return best_intent, best_score
        return None, best_score