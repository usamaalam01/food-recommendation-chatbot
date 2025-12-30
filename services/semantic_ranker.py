from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SemanticRanker:
    def __init__(self, documents):
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.doc_vectors = self.vectorizer.fit_transform(documents)

    def rank(self, query, top_k=5):
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.doc_vectors)[0]
        top_indices = scores.argsort()[::-1][:top_k]
        return top_indices, scores[top_indices]


# semantic_ranker = None

# def init_semantic_ranker(documents):
#     global semantic_ranker
#     semantic_ranker = SemanticRanker(documents)