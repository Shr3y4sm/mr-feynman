import json
import logging
import uuid
import asyncio
import re
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

FILLER_WORDS = [
    "um", "uh", "like", "you know", "basically", "actually", 
    "so", "kind of", "sort of", "i mean", "right", "you see"
]

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

    def _analyze_fillers(self, text: str) -> dict:
        """Detect common filler words in the text."""
        if barely_text:= (not text or len(text.split()) < 5):
            return None

        found_fillers = {}
        total_count = 0
        
        # Normalize text slightly for word count, but regex handles matching
        word_count = len(text.split())
        
        for filler in FILLER_WORDS:
            # Pattern for detecting fillers as whole words/phrases
            pattern = r'\b' + re.escape(filler) + r'\b'
            matches = re.findall(pattern, text, re.IGNORECASE)
            count = len(matches)
            if count > 0:
                found_fillers[filler] = count
                total_count += count
        
        if total_count == 0:
            return None

        density = round(total_count / word_count, 3)
        common = sorted(found_fillers.keys(), key=lambda k: found_fillers[k], reverse=True)[:3]
        
        return {
            "total_filler_count": total_count,
            "filler_density": density,
            "common_fillers": common
        }

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

        # 2a. Handle Speaking Metrics & Fillers
        speaking_context = ""
        user_metrics = None
        filler_stats = None
        
        # Calculate Fillers
        try:
            filler_stats = self._analyze_fillers(request.explanation)
            if filler_stats:
                speaking_context += (
                    f"\nFiller Analysis:\n"
                    f"- Total Fillers: {filler_stats['total_filler_count']}\n"
                    f"- Density: {filler_stats['filler_density']}\n"
                    f"- Top Fillers: {', '.join(filler_stats['common_fillers'])}\n"
                    f"Please utilize these stats to provide feedback in the 'filler_analysis' JSON field."
                )
        except Exception as e:
            logger.error(f"Filler analysis failed: {e}")

        if request.speaking_duration:
            try:
                total = request.speaking_duration.get('total_seconds', 0)
                active = request.speaking_duration.get('active_seconds', 0)
                
                if total > 0:
                    pause_ratio = round((total - active) / total, 2)
                    speaking_context = (
                        f"Speaking Metrics:\n"
                        f"- Total Time: {total}s\n"
                        f"- Active Speaking: {active}s\n"
                        f"- Pause Ratio: {pause_ratio}\n"
                        f"Please analyze these metrics in the 'speaking_metrics' JSON field. "
                        f"Provide a specific 'insight' about their pace/hesitation and 'suggestions' to improve fluency."
                    )
                    user_metrics = {
                        "total_time_seconds": total,
                        "active_speaking_seconds": active,
                        "pause_ratio": pause_ratio
                    }
                    logger.info(f"Generated speaking context: {user_metrics}")
            except Exception as e:
                logger.error(f"Error processing speaking metrics: {e}")

        user_prompt = get_prompt_template(
            PromptMode.FEYNMAN_ANALYSIS,
            concept=request.concept,
            target_audience=request.target_audience,
            explanation=request.explanation,
            speaking_context=speaking_context
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
            
            # 4a. Enrich with calculated metrics (ensure accuracy)
            if user_metrics:
                # Get insight/suggestions from LLM or default
                llm_metrics = analysis_data.get("speaking_metrics", {})
                
                # Merge: force calculated numbers, keep LLM insights
                final_metrics = {
                    "total_time_seconds": user_metrics["total_time_seconds"],
                    "active_speaking_seconds": user_metrics["active_speaking_seconds"],
                    "pause_ratio": user_metrics["pause_ratio"],
                    "insight": llm_metrics.get("insight", "Your speaking data has been recorded."),
                    "suggestions": llm_metrics.get("suggestions", ["Practice maintaining a steady pace."])
                }
                analysis_data["speaking_metrics"] = final_metrics
            
            if filler_stats:
                 llm_fillers = analysis_data.get("filler_analysis", {})
                 final_fillers = {
                    "total_filler_count": filler_stats["total_filler_count"],
                    "filler_density": filler_stats["filler_density"],
                    "common_fillers": filler_stats["common_fillers"],
                    "insight": llm_fillers.get("insight", "Detected some filler words."),
                    "suggestions": llm_fillers.get("suggestions", ["Try to pause silently instead of using fillers."])
                 }
                 analysis_data["filler_analysis"] = final_fillers

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse JSON response: {raw_response}")
            # Fallback
            analysis_data = {
                "summary": "We couldn't process the AI response correctly.",
                "gaps": ["System Error: Invalid JSON response"],
                "suggestions": ["Please try again."],
                "follow_up_questions": [],
                "speaking_clarity": {
                    "issues": [],
                    "suggestions": []
                }
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
