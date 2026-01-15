import re

class TextChunker:
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 200) -> list[dict]:
        """
        Splits text into chunks of roughly `chunk_size` characters.
        Returns list of dicts with 'id' and 'text'.
        """
        # Clean text basic
        text = text.replace('\r\n', '\n')
        
        # Split by paragraphs
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_length = 0
        
        chunk_counter = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            para_len = len(para)
            
            # If adding this paragraph exceeds size and we have content, emit current chunk
            if current_length + para_len > chunk_size and current_chunk:
                # Join current buffer
                chunk_text = "\n\n".join(current_chunk)
                chunks.append({
                    "id": f"chunk_{chunk_counter}",
                    "text": chunk_text
                })
                chunk_counter += 1
                
                # Handling overlap is tricky with simple lists, so we just reset for now 
                # or keep the last paragraph if small enough.
                # For simplicity in this Phase: Strict tumbling windows usually fine.
                # But let's keep the last paragraph if it's less than overlap size to start next chunk
                if len(current_chunk[-1]) < overlap:
                     current_chunk = [current_chunk[-1]]
                     current_length = len(current_chunk[-1])
                else:
                    current_chunk = []
                    current_length = 0
            
            current_chunk.append(para)
            current_length += para_len
            
        # Add remaining
        if current_chunk:
            chunks.append({
                "id": f"chunk_{chunk_counter}",
                "text": "\n\n".join(current_chunk)
            })
            
        return chunks
