import re
import logging

logger = logging.getLogger(__name__)

def normalize_text(text: str) -> set[str]:
    """
    Normalize text into a set of unique lowercase words, removing punctuation.
    """
    # Simple regex to find words (alphanumeric)
    words = re.findall(r'\b\w+\b', text.lower())
    # Filter out common English stopwords (hardcoded to avoid huge dependencies)
    stopwords = {
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", 
        "it", "for", "not", "on", "with", "he", "as", "you", "do", "at", 
        "this", "but", "his", "by", "from", "they", "we", "say", "her", 
        "she", "or", "an", "will", "my", "one", "all", "would", "there", 
        "their", "what", "so", "up", "out", "if", "about", "who", "get", 
        "which", "go", "me", "is", "are", "was", "were"
    }
    return {w for w in words if w not in stopwords and len(w) > 2}

def select_relevant_chunks(
    explanation: str,
    chunks: list[dict],
    max_chunks: int = 3
) -> list[dict]:
    """
    Select the most relevant chunks for grounding the explanation analysis using accurate keyword overlap.
    
    Strategy:
    1. Normalize user explanation into a set of unique keywords.
    2. Normalize each chunk into a set of unique keywords.
    3. Calculate score based on keyword intersection count.
    4. Return top `max_chunks` sorted by relevance.
    
    Args:
        explanation (str): The user's explanation of the concept.
        chunks (list[dict]): List of chunk dictionaries from the text chunker.
        max_chunks (int): Maximum number of chunks to return.
        
    Returns:
        list[dict]: The top N most relevant chunks, with an added 'relevance_score' key.
    """
    if not chunks:
        return []
        
    if not explanation or not explanation.strip():
        # If no explanation provided (edge case), return first N chunks
        return chunks[:max_chunks]

    user_keywords = normalize_text(explanation)
    
    scored_chunks = []
    
    for chunk in chunks:
        # Create a shallow copy to avoid mutating the original input list
        chunk_data = chunk.copy()
        
        chunk_text = chunk_data.get("text", "")
        chunk_keywords = normalize_text(chunk_text)
        
        # Calculate intersection
        intersection = user_keywords.intersection(chunk_keywords)
        score = len(intersection)
        
        chunk_data["relevance_score"] = score
        scored_chunks.append(chunk_data)
    
    # Sort by score descending
    scored_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    # Select top N
    selected = scored_chunks[:max_chunks]
    
    logger.info(f"Selected {len(selected)} chunks from pool of {len(chunks)}. Top score: {selected[0]['relevance_score'] if selected else 0}")
    
    return selected
