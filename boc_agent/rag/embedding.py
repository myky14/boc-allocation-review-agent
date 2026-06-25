import re
import math
from typing import List, Dict, Set

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", 
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", 
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could", 
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", 
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", 
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", 
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", 
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", 
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", 
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", 
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", 
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", 
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", 
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", 
    "they've", "this", "those", "through", "to", "too", "under", "until", "up", 
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", 
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", 
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", 
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", 
    "yourself", "yourselves"
}

def tokenize(text: str) -> List[str]:
    """Tokenizes a string to lowercase alphanumeric words, filtering out common stopwords."""
    if not text:
        return []
    words = re.findall(r'\b[a-zA-Z0-9_]+\b', text.lower())
    return [w for w in words if w not in STOPWORDS]

class TfidfVectorizer:
    """Lightweight, local-first TF-IDF vectorizer built on pure Python dicts."""
    def __init__(self):
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.num_docs = 0

    def fit(self, texts: List[str]) -> None:
        """Fits vocabulary and term document frequencies over the corpus of texts."""
        self.num_docs = len(texts)
        if self.num_docs == 0:
            return
        
        doc_frequencies: Dict[str, int] = {}
        for text in texts:
            unique_terms = set(tokenize(text))
            for term in unique_terms:
                doc_frequencies[term] = doc_frequencies.get(term, 0) + 1
                
        # Assign indexes to vocab and compute smooth IDF values
        vocab_idx = 0
        for term, doc_freq in doc_frequencies.items():
            self.vocab[term] = vocab_idx
            self.idf[term] = math.log((1 + self.num_docs) / (1 + doc_freq)) + 1.0
            vocab_idx += 1

    def transform(self, text: str) -> Dict[int, float]:
        """Transforms a string into a sparse TF-IDF vector represented as Dict[vocab_idx, tf_idf_weight]."""
        tokens = tokenize(text)
        if not tokens:
            return {}
            
        tf_counts: Dict[str, int] = {}
        for t in tokens:
            tf_counts[t] = tf_counts.get(t, 0) + 1
            
        vector = {}
        for term, count in tf_counts.items():
            if term in self.vocab:
                idx = self.vocab[term]
                # TF-IDF formula: raw count * IDF weight
                vector[idx] = count * self.idf[term]
        return vector

def compute_cosine_similarity(vec1: Dict[int, float], vec2: Dict[int, float]) -> float:
    """Computes cosine similarity between two sparse dict-based vectors."""
    if not vec1 or not vec2:
        return 0.0
        
    dot_product = 0.0
    for idx, val in vec1.items():
        if idx in vec2:
            dot_product += val * vec2[idx]
            
    norm1 = math.sqrt(sum(val ** 2 for val in vec1.values()))
    norm2 = math.sqrt(sum(val ** 2 for val in vec2.values()))
    
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
        
    return dot_product / (norm1 * norm2)
