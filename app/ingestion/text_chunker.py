import logging
import re

logger = logging.getLogger(__name__)

def chunk_text(
    text: str,
    max_tokens: int = 700,
    overlap_tokens: int = 50
) -> list[dict]:
    """
    Split long text into ordered, overlapping chunks suitable for LLM context.
    
    Note: Since we are running in a lightweight environment without the specific 
    LLM tokenizer loaded in this process, we use whitespace/word splitting as 
    a proxy for tokenization. 1 "token" here is approximately 1 word.
    
    Args:
        text (str): The full input text to chunk.
        max_tokens (int): Approximate maximum words per chunk.
        overlap_tokens (int): Approximate number of words to overlap between chunks.
        
    Returns:
        list[dict]: A list of chunks, e.g., [{"id": 0, "text": "...", "token_est": 500}, ...]
    """
    if not text:
        return []

    # Clean up excessive whitespace to ensure consistent word counting
    # This collapses multiple spaces/newlines into single spaces
    clean_text = re.sub(r'\s+', ' ', text).strip()
    words = clean_text.split()
    
    chunks = []
    total_words = len(words)
    chunk_id = 0
    start_index = 0
    
    while start_index < total_words:
        end_index = min(start_index + max_tokens, total_words)
        
        chunk_words = words[start_index:end_index]
        chunk_str = " ".join(chunk_words)
        
        chunks.append({
            "chunk_id": chunk_id,
            "text": chunk_str,
            "token_est": len(chunk_words),
            "start_word_idx": start_index,
            "end_word_idx": end_index
        })
        
        chunk_id += 1
        
        # If we reached the end, break
        if end_index == total_words:
            break
            
        # Move the start index forward, subtracting overlap
        # Ensure we always move forward by at least 1 word to prevent infinite loops
        step = max_tokens - overlap_tokens
        if step < 1:
            step = 1
            
        start_index += step

    logger.info(f"Chunked text into {len(chunks)} parts (Total words: {total_words})")
    return chunks
