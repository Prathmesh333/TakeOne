"""
Script-to-Sequence Search - Sequential scene matching for film production
Breaks down scripts into ordered actions and returns matching footage in sequence
"""

import re
import logging
from typing import List, Dict, Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ScriptSequenceSearch:
    """
    Intelligent script parser that breaks down scripts into sequential actions
    and returns matching footage in the correct order for video editing.
    """
    
    def __init__(self, search_engine):
        """
        Initialize script sequence search.
        
        Args:
            search_engine: SceneSearchEngine instance for searching footage
        """
        self.search_engine = search_engine
        
        # Initialize Gemini for script parsing and translation
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
            logger.info("Script parser initialized with Gemini (multilingual support enabled)")
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not set - script parsing will use fallback")
    
    def translate_script_to_english(self, script: str) -> str:
        """
        Translate script from any language to English using AI.
        Handles transliteration and translation automatically.
        
        Args:
            script: Script text in any language
            
        Returns:
            English translation of the script
        """
        if not self.model:
            logger.warning("Translation unavailable - using original script")
            return script
        
        try:
            prompt = f"""Translate this film script to English. If it's already in English, return it as-is.

Script:
{script}

Requirements:
- Translate to natural, readable English
- Preserve the visual actions and scene descriptions
- Handle transliteration if needed (e.g., Hindi/Marathi/Tamil/Telugu/Kannada script to English)
- Keep the sequential structure intact
- Focus on visual elements and actions that can be found in video footage
- Maintain line breaks and formatting

Return ONLY the English translation, no explanation or additional text.
"""

            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.3, "max_output_tokens": 2048}
            )
            
            translated = response.text.strip()
            
            # Log translation if different from original
            if translated.lower() != script.lower():
                logger.info(f"Translated script from source language to English ({len(script)} → {len(translated)} chars)")
            
            return translated
            
        except Exception as e:
            logger.warning(f"Script translation failed: {e} - using original script")
            return script
    
    def parse_script_to_actions(self, script: str) -> List[Dict]:
        """
        Parse a script into sequential actions using AI.
        
        Args:
            script: Full script text with multiple scenes/actions
            
        Returns:
            List of action dicts with sequence number and search query
        """
        if not self.model:
            # Fallback: Simple line-by-line parsing
            return self._fallback_parse(script)
        
        try:
            prompt = f"""You are a film production assistant. Parse this script into sequential actions for finding matching footage.

Script:
{script}

Break this down into a numbered sequence of specific, searchable actions. Each action should be:
1. A clear visual description
2. Searchable in a video database
3. In the order they appear in the script
4. Specific enough to find matching footage

Return ONLY a JSON array with this format:
[
  {{"sequence": 1, "action": "person walking down a street", "description": "establishing shot"}},
  {{"sequence": 2, "action": "close-up of worried face", "description": "emotional reaction"}},
  ...
]

Focus on visual elements, actions, settings, and emotions that can be found in video footage.
Return ONLY the JSON array, no explanation."""

            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 2048,
                    "response_mime_type": "application/json"
                }
            )
            
            # Parse JSON response
            import json
            json_text = response.text.strip()
            
            # Clean up markdown if present
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.startswith("```"):
                json_text = json_text[3:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            json_text = json_text.strip()
            
            actions = json.loads(json_text)
            
            logger.info(f"Parsed script into {len(actions)} sequential actions")
            return actions
            
        except Exception as e:
            logger.error(f"Script parsing failed: {e}")
            return self._fallback_parse(script)
    
    def _fallback_parse(self, script: str) -> List[Dict]:
        """
        Fallback parser when AI is unavailable.
        Simple line-by-line parsing.
        """
        lines = [line.strip() for line in script.split('\n') if line.strip()]
        
        actions = []
        for i, line in enumerate(lines, 1):
            # Skip very short lines or stage directions in parentheses
            if len(line) < 10 or (line.startswith('(') and line.endswith(')')):
                continue
            
            actions.append({
                "sequence": i,
                "action": line,
                "description": f"Action {i}"
            })
        
        logger.info(f"Fallback parser: {len(actions)} actions")
        return actions
    
    def search_script_sequence(
        self,
        script: str,
        results_per_action: int = 3,
        use_query_expansion: bool = True,
        auto_translate: bool = True
    ) -> Dict:
        """
        Search for footage matching a script in sequential order.
        Supports multilingual scripts with automatic translation.
        
        Processing Pipeline:
        1. Script Translation/Transliteration (any language → English)
        2. AI Script Parsing (break into sequential actions)
        3. AI Query Enhancement (for each action)
        4. Semantic Search (find matching footage for each action)
        
        Args:
            script: Full script text (in any language)
            results_per_action: Number of footage options per action
            use_query_expansion: Use AI query expansion for better matches (default: True)
            auto_translate: Automatically translate non-English scripts to English (default: True)
            
        Returns:
            Dict with parsed actions and sequential results
        """
        logger.info("Starting script-to-sequence search with multilingual support")
        
        # STEP 1: Translation/Transliteration (any language → English)
        if auto_translate:
            english_script = self.translate_script_to_english(script)
            logger.info(f"Script translation complete: {len(script)} → {len(english_script)} chars")
        else:
            english_script = script
        
        # STEP 2: AI Script Parsing (break into sequential actions)
        actions = self.parse_script_to_actions(english_script)
        
        if not actions:
            return {
                "status": "error",
                "error": "Could not parse script into actions",
                "actions": [],
                "results": []
            }
        
        logger.info(f"Script parsed into {len(actions)} sequential actions")
        
        # STEP 3 & 4: For each action, do AI Query Enhancement + Semantic Search
        sequential_results = []
        
        for action in actions:
            sequence_num = action["sequence"]
            search_query = action["action"]
            
            logger.info(f"Processing action {sequence_num}/{len(actions)}: '{search_query}'")
            
            # Search with AI query enhancement enabled
            # The search engine will:
            # - Take the English action query
            # - Generate comprehensive variations (AI enhancement)
            # - Search with all variations
            matches = self.search_engine.search(
                query=search_query,
                top_k=results_per_action,
                use_query_expansion=use_query_expansion,  # AI enhancement happens here
                auto_translate=False  # Already translated at script level
            )
            
            sequential_results.append({
                "sequence": sequence_num,
                "action": action,
                "matches": matches,
                "match_count": len(matches)
            })
        
        logger.info(f"Script search complete: {len(actions)} actions, {sum(r['match_count'] for r in sequential_results)} total matches")
        
        return {
            "status": "success",
            "original_script": script,
            "translated_script": english_script if auto_translate and english_script != script else None,
            "total_actions": len(actions),
            "actions": actions,
            "results": sequential_results,
            "total_matches": sum(r['match_count'] for r in sequential_results)
        }
    
    def export_edit_sequence(self, search_results: Dict, format: str = "text") -> str:
        """
        Export search results as an edit sequence for video editors.
        
        Args:
            search_results: Results from search_script_sequence()
            format: Export format - "text", "csv", or "json"
            
        Returns:
            Formatted string ready for export
        """
        if format == "json":
            import json
            return json.dumps(search_results, indent=2)
        
        elif format == "csv":
            lines = ["Sequence,Action,Clip Path,Score,Duration,Description"]
            
            for result in search_results.get("results", []):
                seq = result["sequence"]
                action = result["action"]["action"]
                
                for match in result["matches"]:
                    lines.append(
                        f'{seq},"{action}","{match["clip_path"]}",{match["score"]:.3f},'
                        f'{match["duration"]:.1f},"{match.get("description", "")}"'
                    )
            
            return "\n".join(lines)
        
        else:  # text format
            lines = ["=" * 80]
            lines.append("SCRIPT-TO-SEQUENCE EDIT LIST")
            lines.append("=" * 80)
            lines.append(f"Total Actions: {search_results['total_actions']}")
            lines.append(f"Total Matches: {search_results['total_matches']}")
            lines.append("=" * 80)
            lines.append("")
            
            for result in search_results.get("results", []):
                seq = result["sequence"]
                action = result["action"]
                matches = result["matches"]
                
                lines.append(f"[{seq}] {action['action']}")
                lines.append(f"    Description: {action.get('description', 'N/A')}")
                lines.append(f"    Matches: {len(matches)}")
                lines.append("")
                
                for i, match in enumerate(matches, 1):
                    lines.append(f"    Option {i}:")
                    lines.append(f"      File: {match['clip_path']}")
                    lines.append(f"      Score: {match['score']:.1%}")
                    lines.append(f"      Duration: {match['duration']:.1f}s")
                    if match.get('description'):
                        lines.append(f"      Description: {match['description']}")
                    lines.append("")
                
                lines.append("-" * 80)
                lines.append("")
            
            return "\n".join(lines)


def main():
    """Test script sequence search."""
    from search.vector_search import SceneSearchEngine
    
    # Initialize
    search_engine = SceneSearchEngine()
    script_search = ScriptSequenceSearch(search_engine)
    
    # Example script
    test_script = """
    A person walks down a busy city street, looking worried.
    They stop and check their phone with a concerned expression.
    Cut to a close-up of the phone screen showing a message.
    The person starts running through the crowd.
    They arrive at a building and rush inside.
    """
    
    print("Testing Script-to-Sequence Search")
    print("=" * 60)
    print(f"Script:\n{test_script}")
    print("=" * 60)
    
    # Search
    results = script_search.search_script_sequence(test_script, results_per_action=2)
    
    # Export
    edit_list = script_search.export_edit_sequence(results, format="text")
    print(edit_list)


if __name__ == "__main__":
    main()
