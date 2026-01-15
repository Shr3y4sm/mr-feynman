import re
from collections import Counter

class ContextSelector:
    @staticmethod
    def select_context(query_text: str, chunks: list[dict], top_k: int = 3) -> list[dict]:
        """
        Selects top_k chunks based on rudimentary term frequency overlap.
        """
        if not chunks:
            return []
            
        # Tokenize query
        stop_words = {"the", "a", "an", "is", "of", "to", "in", "and", "it", "that", "for", "on", "with", "this", "be", "as"}
        
        def get_tokens(text):
            words = re.findall(r'\w+', text.lower())
            return set(w for w in words if w not in stop_words and len(w) > 2)
            
        query_tokens = get_tokens(query_text)
        
        scored_chunks = []
        for chunk in chunks:
            chunk_tokens = get_tokens(chunk['text'])
            # Jaccard-ish or just Intersection Count
            intersection = query_tokens.intersection(chunk_tokens)
            score = len(intersection)
            if score > 0:
                scored_chunks.append((score, chunk))
                
        # Sort desc
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        # Take top K
        result = [item[1] for item in scored_chunks[:top_k]]
        return result
