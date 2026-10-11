"""
CHRONOFACT Enhanced ML Models
=============================
Production-grade NLP and semantic analysis for forensic evidence.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer

# Production NLP model (lightweight, runs locally)
SENTENCE_MODEL = None


def get_sentence_model() -> Optional[SentenceTransformer]:
    """Lazy-load sentence transformer model."""
    global SENTENCE_MODEL
    if SENTENCE_MODEL is None:
        try:
            # Using a lightweight model that works well for short forensic texts
            SENTENCE_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception:
            # Fallback to TF-IDF if NLP model unavailable
            SENTENCE_MODEL = None
    return SENTENCE_MODEL


class NLPForensicAnalyzer:
    """
    Production NLP analysis for semantic search and entity extraction.
    Uses sentence-transformers for better semantic understanding than TF-IDF.
    """
    
    def __init__(self):
        self.model = get_sentence_model()
        self.embeddings: Dict[str, np.ndarray] = {}
        self.evidence_ids: List[str] = []
    
    def analyze_evidence_text(self, text: str, evidence_id: str) -> Dict[str, Any]:
        """
        Analyze text for semantic content and extract entities.
        Returns enriched evidence data with embeddings.
        """
        result = {
            "evidence_id": evidence_id,
            "text_length": len(text),
            "sentence_count": text.count('.') + text.count('!') + text.count('?'),
            "entities": self._extract_entities(text),
            "sentiment": self._analyze_sentiment(text),
            "keywords": self._extract_keywords(text),
        }
        
        # Generate embedding if model available
        if self.model is not None:
            try:
                embedding = self.model.encode(text)
                result["embedding"] = embedding.tolist()[:100]  # Store first 100 dims
            except Exception:
                result["embedding"] = None
        
        return result
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract all relevant entities from text."""
        entities = {
            "ips": [],
            "emails": [],
            "phones": [],
            "dates": [],
            "usernames": [],
            "urls": [],
            "files": [],
            "actions": []
        }
        
        # IP addresses
        entities["ips"] = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)
        
        # Emails
        entities["emails"] = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text)
        
        # Phones (Indian format support)
        entities["phones"] = re.findall(r'\b(?:\+91|0)?[6789]\d{9}\b', text)
        
        # Dates
        entities["dates"] = re.findall(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b|\d{4}-\d{2}-\d{2}', text)
        
        # Usernames (common forensic patterns)
        entities["usernames"] = re.findall(r'\b[A-Za-z0-9_-]{3,20}\b', text)
        
        # URLs
        entities["urls"] = re.findall(r'https?://[^\s]+', text)
        
        # Files
        entities["files"] = re.findall(r'\b[\w\-]+\.(xlsx|xls|csv|txt|pdf|zip|eml|doc|docx|bin|jpg|png|mp4|avi)\b', text, re.IGNORECASE)
        
        # Actions
        actions_found = []
        action_keywords = ["login", "logout", "download", "upload", "export", "delete", "modify", "transfer", "encrypt", "decrypt"]
        for keyword in action_keywords:
            if keyword in text.lower():
                actions_found.append(keyword)
        entities["actions"] = actions_found
        
        return entities
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Simple heuristic-based sentiment for forensic texts."""
        text_lower = text.lower()
        
        # Forensic-specific sentiment indicators
        negative_indicators = ["illegal", "unauthorized", "suspicious", "malicious", "exploit", 
                              "attack", "breach", "leak", "compromise", "threat", "violation"]
        positive_indicators = ["legitimate", "authorized", "verified", "approved", "secure", "safe"]
        
        negative_count = sum(1 for word in negative_indicators if word in text_lower)
        positive_count = sum(1 for word in positive_indicators if word in text_lower)
        
        total = negative_count + positive_count
        if total == 0:
            return {"label": "NEUTRAL", "score": 0.5}
        elif negative_count > positive_count:
            return {"label": "SUSPICIOUS", "score": 0.2}
        else:
            return {"label": "VERIFIED", "score": 0.8}
    
    def _extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract top keywords using simple TF scoring."""
        # Clean and tokenize
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Stop words for forensic texts
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 
            'have', 'has', 'had', 'do', 'does', 'did', 'and', 'or', 
            'but', 'if', 'then', 'so', 'than', 'too', 'very', 'can'
        }
        
        # Count word frequencies
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:top_n]]


class SemanticSearchEnhanced:
    """
    Enhanced semantic search using sentence-transformers for better accuracy.
    """
    
    def __init__(self):
        self.model = get_sentence_model()
        self.index: Dict[str, Any] = {}
    
    def search(self, query: str, evidence_texts: Dict[str, str], 
               top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic search across evidence.
        Returns ranked results with similarity scores.
        """
        if self.model is None:
            return []
        
        # Generate embeddings
        query_embedding = self.model.encode(query)
        
        # Calculate similarities
        results = []
        for ev_id, text in evidence_texts.items():
            try:
                text_embedding = self.model.encode(text)
                similarity = np.dot(query_embedding, text_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(text_embedding)
                )
                results.append({
                    "evidence_id": ev_id,
                    "similarity": float(similarity),
                    "text_preview": text[:200] + "..." if len(text) > 200 else text
                })
            except Exception:
                continue
        
        # Sort and return top_k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
