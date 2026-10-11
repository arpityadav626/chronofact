"""
CHRONOFACT Production RAG Engine
================================
Uses Sentence Transformers for semantic understanding of evidence.
Removes hardcoded keywords/city/IP assumptions.
"""

import logging
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Semantic Search Engine using Sentence Transformers.
    Runs entirely locally (all-MiniLM-L6-v2).
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.indexed_docs: List[Dict[str, Any]] = []

    def _load_model(self):
        """Lazy load model to avoid startup delay."""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading semantic model: {self.model_name}...")
                self.model = SentenceTransformer(self.model_name)
                logger.info("Semantic model loaded.")
            except ImportError:
                logger.warning("sentence-transformers not installed. Install with 'pip install sentence-transformers'")
                self.model = None
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                self.model = None

    def index_documents(self, documents: List[Dict[str, Any]]):
        """
        Index a list of evidence chunks.
        Each doc must have: {'id': str, 'text': str, 'metadata': dict}
        """
        if not documents:
            return

        self._load_model()
        if self.model is None:
            # Fallback: just store text without embeddings
            self.indexed_docs = documents
            return

        try:
            texts = [d.get("text", "") for d in documents]
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            
            self.indexed_docs = []
            for i, doc in enumerate(documents):
                doc_copy = doc.copy()
                doc_copy["embedding"] = embeddings[i]
                self.indexed_docs.append(doc_copy)
            
            logger.info(f"Indexed {len(documents)} evidence chunks.")
        except Exception as e:
            logger.error(f"Failed to embed documents: {e}")
            # Fallback to raw storage
            self.indexed_docs = documents

    def search(self, query: str, top_k: int = 5, min_similarity: float = 0.25) -> List[Dict[str, Any]]:
        """
        Search indexed documents semantically.
        Returns results sorted by cosine similarity.
        """
        self._load_model()
        
        if not self.indexed_docs:
            return []

        # If using pure storage (model failed) or simple text match
        if self.model is None:
            results = []
            query_lower = query.lower()
            for doc in self.indexed_docs:
                text = doc.get("text", "").lower()
                if any(w in text for w in query_lower.split()):
                    doc_copy = doc.copy()
                    doc_copy["similarity"] = 0.5  # Default score
                    results.append(doc_copy)
            return results[:top_k]

        try:
            query_embedding = self.model.encode([query], convert_to_numpy=True)[0]
            
            # Calculate cosine similarity
            import numpy as np
            
            # Filter to docs with embeddings
            docs_with_embed = [d for d in self.indexed_docs if "embedding" in d]
            if not docs_with_embed:
                return []
            
            doc_embeds = np.array([d["embedding"] for d in docs_with_embed])
            
            # Cosine similarity
            norm_q = np.linalg.norm(query_embedding)
            norm_d = np.linalg.norm(doc_embeds, axis=1)
            
            if norm_q == 0 or np.all(norm_d == 0):
                return []
            
            similarities = np.dot(doc_embeds, query_embedding) / (norm_d * norm_q)
            
            # Get top indices
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                score = float(similarities[idx])
                if score >= min_similarity:
                    doc = docs_with_embed[idx].copy()
                    doc["similarity"] = score
                    results.append(doc)
            
            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
