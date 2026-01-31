"""
Query Expander - Uses LLM to expand abstract queries into visual/audio search terms
"""
import os
import json
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


EXPANSION_PROMPT = """You are a film editor's assistant. Given a search query for finding video footage, 
expand it into specific visual and audio terms that would help match the right clips.

User Query: "{query}"

Return a JSON object with these keys:
- visual_terms: list of 3-5 visual descriptions (objects, actions, expressions, camera angles)
- audio_terms: list of 2-3 audio/dialogue descriptions (sounds, speech patterns, tone)
- emotions: list of 1-3 emotional tones (happy, tense, sad, neutral, angry, fearful)
- colors: list of 1-2 dominant color tones (warm, cool, dark, bright)

Be specific and cinematic. Focus on observable elements, not abstract concepts.

Return ONLY valid JSON, no markdown or explanation."""


class QueryExpander:
    """Expands natural language queries into searchable visual/audio terms."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize with OpenAI API key.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("Warning: No OpenAI API key found. Query expansion will be disabled.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
    
    def expand(self, query: str) -> Dict[str, List[str]]:
        """
        Expand a natural language query into visual/audio search terms.
        
        Args:
            query: Natural language search query
            
        Returns:
            Dictionary with visual_terms, audio_terms, emotions, colors
        """
        # Fallback if no API key
        if not self.client:
            return self._fallback_expand(query)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fallback to OpenAI if available
                messages=[
                    {"role": "system", "content": "You are a helpful film production assistant."},
                    {"role": "user", "content": EXPANSION_PROMPT.format(query=query)}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON response
            result = json.loads(content)
            return {
                "visual_terms": result.get("visual_terms", []),
                "audio_terms": result.get("audio_terms", []),
                "emotions": result.get("emotions", []),
                "colors": result.get("colors", []),
                "original_query": query
            }
            
        except Exception as e:
            print(f"Query expansion error: {e}")
            return self._fallback_expand(query)
    
    def _fallback_expand(self, query: str) -> Dict[str, List[str]]:
        """Simple fallback when API is unavailable."""
        # Extract basic terms from query
        words = query.lower().split()
        return {
            "visual_terms": words[:5],
            "audio_terms": [],
            "emotions": ["neutral"],
            "colors": [],
            "original_query": query
        }
    
    def get_search_texts(self, expansion: Dict[str, List[str]]) -> List[str]:
        """
        Convert expansion dict into list of search texts for embedding.
        
        Args:
            expansion: Output from expand()
            
        Returns:
            List of text strings to embed and search
        """
        texts = [expansion["original_query"]]
        texts.extend(expansion.get("visual_terms", []))
        texts.extend(expansion.get("emotions", []))
        
        # Combine terms for richer queries
        if expansion.get("visual_terms"):
            combined = " ".join(expansion["visual_terms"][:3])
            texts.append(combined)
        
        return texts


# Global instance
_expander = None


def get_expander() -> QueryExpander:
    """Get or create global expander instance."""
    global _expander
    if _expander is None:
        _expander = QueryExpander()
    return _expander
