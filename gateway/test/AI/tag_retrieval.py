from sklearn.feature_extraction.text import TfidfVectorizer
import os
from time import time
import pickle
from scipy.sparse import vstack
import scipy.sparse as sp
import numpy as np
import atexit

class TagRetrieval:
    def __init__(self, root_dir
                 ):

        self.tag_contexts = None
        self.tag_corpus = None

        self.transform_file = os.path.join(root_dir, "services", "retrieval", "contexts", "tfidf_transform.pkl")
        self.contexts_file = os.path.join(root_dir, "services", "retrieval", "contexts", "tag_contexts.npz")

        if os.path.exists(self.transform_file) and os.path.exists(self.contexts_file):
            self._load_transform_and_contexts()
        else:
            self.tfidf_transform = TfidfVectorizer(input='content', ngram_range=(1, 1),
                                                   token_pattern=r"(?u)\b[\w\d]+\b")

        atexit.register(self._save_transform_and_contexts)

    def add_contexts(self, tag_contexts):
        """Update tag contexts"""
        if self.tag_contexts is None:
            tag_contexts = self.tfidf_transform.fit_transform(tag_contexts).tocsr()
            self.tag_contexts = tag_contexts
        else:
            tag_contexts = self.tfidf_transform.transform(tag_contexts).tocsr()
            self.tag_contexts = vstack([self.tag_contexts, tag_contexts])
        self.tag_corpus = self.tfidf_transform.get_feature_names_out()

    def search(self, query: str, k=10):
        if isinstance(query, str):
            query = query.split(" ")

        query_vector = self.tfidf_transform.transform(query)
        score = self.tag_contexts.dot(query_vector.T).toarray()
        score = np.array([sum(s)/len(s) for s in score])

        top_k_indices = np.argsort(score)[::-1][:k]
        score = np.take_along_axis(score, top_k_indices, axis=0)

        return score.tolist(), top_k_indices.tolist()

    def _load_transform_and_contexts(self):
        """Load TFIDF transform and tag contexts from disk if available"""
        try:
            with open(self.transform_file, 'rb') as f:
                self.tfidf_transform = pickle.load(f)
            self.tag_contexts = sp.load_npz(self.contexts_file)
            self.tag_corpus = self.tfidf_transform.get_feature_names_out()

        except Exception as e:
            print(f"Error loading transform or contexts: {e}")

    def _save_transform_and_contexts(self):
        """Save TFIDF transform and tag contexts to disk"""
        if self.tfidf_transform is not None:
            with open(self.transform_file, 'wb') as f:
                pickle.dump(self.tfidf_transform, f)

        if self.tag_contexts is not None:
            sp.save_npz(self.contexts_file, self.tag_contexts)
