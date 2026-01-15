import json
import logging
import uuid
import asyncio
from datetime import datetime

from app.services.llm_engine import llm_engine
from app.prompts.templates import FEYNMAN_SYSTEM_PROMPT, get_prompt_template, PromptMode
from app.schemas.analysis import AnalysisRequest, AnalysisResponse

# Logic Services
from app.services.text_chunker import TextChunker
from app.services.context_selector import ContextSelector
from app.services.explanation_comparator import ExplanationComparator
from app.memory.attempts_store import save_attempt, load_attempt

logger = logging.getLogger(__name__)

class FeynmanAnalyzer:
    def __init__(self):
        self.llm = llm_engine
        self.chunker = TextChunker()
        self.selector = ContextSelector()
        self.comparator = ExplanationComparator()

    def clean_json_string(self, json_str: str) -> str:
        """Helper to clean LLM output if it includes markdown code blocks."""
        json_str = json_str.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        return json_str.strip()

    def analyze_explanation(self, request: AnalysisRequest) -> AnalysisResponse:
        logger.info(f"Analyzing concept: {request.concept}")
        
        # 1. Handle Source Text (RAG)
        context_str = ""
        used_chunk_ids = []
        
        if request.source_text:
            logger.info("Processing source text for context...")
            try:
                # Chunk it
                chunks = self.chunker.chunk_text(request.source_text)
                # Select relevant chunks
                query = f"{request.concept} {request.explanation}"
                relevant_chunks = self.selector.select_context(query, chunks)
                
                if relevant_chunks:
                    context_str = "\n\nReference Material:\n" + "\n---\n".join([c['text'] for c in relevant_chunks])
                    used_chunk_ids = [c['id'] for c in relevant_chunks]
                    logger.info(f"Found {len(relevant_chunks)} relevant chunks.")
            except Exception as e:
                logger.error(f"RAG processing failed: {e}")
                # Continue without context rather than crashing

        # 2. Prepare Prompt
        system_prompt_to_use = FEYNMAN_SYSTEM_PROMPT
        if context_str:
            system_prompt_to_use += f"\n\n{context_str}\n\nUse the Reference Material above to check the accuracy of the explanation."

        user_prompt = get_prompt_template(
            PromptMode.FEYNMAN_ANALYSIS,
            concept=request.concept,
            target_audience=request.target_audience,
            explanation=request.explanation
        )

        # 3. Call LLM
        raw_response = self.llm.generate(
            system_prompt=system_prompt_to_use,
            user_prompt=user_prompt
        )

        # 4. Parse Response
        analysis_data = {}
        try:
            cleaned_response = self.clean_json_string(raw_response)
            analysis_data = json.loads(cleaned_response)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse JSON response: {raw_response}")
            # Fallback
            analysis_data = {
                "summary": "We couldn't process the AI response correctly.",
                "gaps": ["System Error: Invalid JSON response"],
                "suggestions": ["Please try again."],
                "follow_up_questions": []
            }

        # 5. Handle Comparison (History)
        comparison_result = None
        if request.previous_attempt_id:
            logger.info(f"Comparing with previous attempt {request.previous_attempt_id}")
            try:
                old_attempt = load_attempt(request.previous_attempt_id)
                if old_attempt:
                    old_analysis = old_attempt.get("analysis_result", {})
                    comparison_result = self.comparator.compare_attempts(old_analysis, analysis_data)
            except Exception as e:
                logger.error(f"Comparison failed: {e}")

        # 6. Save Current Attempt
        new_attempt_id = str(uuid.uuid4())
        try:
            attempt_record = {
                "attempt_id": new_attempt_id,
                "timestamp": datetime.utcnow().isoformat(),
                "concept": request.concept,
                "target_audience": request.target_audience,
                "explanation_text": request.explanation,
                "analysis_result": analysis_data,
                "referenced_chunk_ids": used_chunk_ids,
                "comparison": comparison_result
            }
            save_attempt(attempt_record)
        except Exception as e:
            logger.error(f"Failed to save attempt: {e}")

        # 7. construct Response
        return AnalysisResponse(
            analysis=analysis_data,
            comparison=comparison_result,
            attempt_id=new_attempt_id
        )

analyzer_service = FeynmanAnalyzer()
