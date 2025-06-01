import os
import pickle
import numpy as np
from typing import List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import vstack, save_npz, load_npz
import scipy.sparse as sp
from loguru import logger


class TagRetrieval:
    """Tag-based retrieval using TF-IDF vectorization"""
    
    def __init__(self, data_dir: str = "data/ai"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.tag_contexts = None
        self.tag_corpus = None
        
        self.transform_file = os.path.join(data_dir, "tfidf_transform.pkl")
        self.contexts_file = os.path.join(data_dir, "tag_contexts.npz")
        
        # Load existing model or create new
        if os.path.exists(self.transform_file) and os.path.exists(self.contexts_file):
            self._load_transform_and_contexts()
        else:
            self.tfidf_transform = TfidfVectorizer(
                input='content',
                ngram_range=(1, 2),  # Use both unigrams and bigrams
                token_pattern=r"(?u)\b[\w\d]+\b",
                max_features=5000
            )
            logger.info("Created new TF-IDF vectorizer")
    
    def add_contexts(self, tag_contexts: List[str]):
        """Add new tag contexts to the retrieval system"""
        if not tag_contexts:
            return
            
        try:
            if self.tag_contexts is None:
                # First time: fit and transform
                contexts_sparse = self.tfidf_transform.fit_transform(tag_contexts).tocsr()
                self.tag_contexts = contexts_sparse
            else:
                # Add new contexts: transform only
                contexts_sparse = self.tfidf_transform.transform(tag_contexts).tocsr()
                self.tag_contexts = vstack([self.tag_contexts, contexts_sparse])
            
            self.tag_corpus = self.tfidf_transform.get_feature_names_out()
            logger.debug(f"Added {len(tag_contexts)} tag contexts to retrieval system")
            
        except Exception as e:
            logger.error(f"Error adding tag contexts: {e}")
    
    def search(self, query: str, k: int = 10) -> Tuple[List[float], List[int]]:
        """Search for similar images based on tag query"""
        if self.tag_contexts is None:
            logger.warning("No tag contexts available for search")
            return [], []
            
        try:
            # Handle query as list of tags or single string
            if isinstance(query, str):
                query_list = [query]
            else:
                query_list = query
            
            # Transform query to vector
            query_vector = self.tfidf_transform.transform(query_list)
            
            # Calculate cosine similarity
            scores = self.tag_contexts.dot(query_vector.T).toarray()
            scores = scores.flatten()
            
            # Get top-k indices
            top_k_indices = np.argsort(scores)[::-1][:k]
            top_k_scores = scores[top_k_indices]
            
            # Filter out zero scores
            non_zero_mask = top_k_scores > 0
            top_k_indices = top_k_indices[non_zero_mask]
            top_k_scores = top_k_scores[non_zero_mask]
            
            return top_k_scores.tolist(), top_k_indices.tolist()
            
        except Exception as e:
            logger.error(f"Error in tag search: {e}")
            return [], []
    
    def save_contexts(self):
        """Save TF-IDF transform and contexts to disk"""
        try:
            if self.tfidf_transform is not None:
                with open(self.transform_file, 'wb') as f:
                    pickle.dump(self.tfidf_transform, f)
                logger.debug(f"Saved TF-IDF transform to {self.transform_file}")
            
            if self.tag_contexts is not None:
                save_npz(self.contexts_file, self.tag_contexts)
                logger.debug(f"Saved tag contexts to {self.contexts_file}")
                
        except Exception as e:
            logger.error(f"Error saving tag retrieval data: {e}")
    
    def _load_transform_and_contexts(self):
        """Load saved TF-IDF transform and contexts from disk"""
        try:
            with open(self.transform_file, 'rb') as f:
                self.tfidf_transform = pickle.load(f)
            
            self.tag_contexts = load_npz(self.contexts_file)
            self.tag_corpus = self.tfidf_transform.get_feature_names_out()
            
            logger.info(f"Loaded tag retrieval data with {self.tag_contexts.shape[0]} contexts")
            
        except Exception as e:
            logger.error(f"Error loading tag retrieval data: {e}") 