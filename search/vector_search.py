"""
Scene Search Engine - ChromaDB-based semantic search for video scenes
Uses Sentence Transformers for text embeddings of Gemini scene descriptions
"""

import numpy as np
from typing import List, Dict, Optional, Any, Union
from pathlib import Path
import logging
import json
import os
import chromadb
from chromadb.config import Settings

# Suppress progress bars from sentence-transformers (works with all versions)
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
# Disable tqdm progress bars globally
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

logger = logging.getLogger(__name__)


class SceneSearchEngine:
    """
    ChromaDB-based search engine for video scenes.
    Uses text embeddings from scene descriptions for semantic search.
    """
    
    def __init__(
        self,
        persist_dir: str = "./chroma_db",
        collection_name: str = "takeone_scenes",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the scene search engine.
        
        Args:
            persist_dir: Directory for ChromaDB storage
            collection_name: Name of the collection
            embedding_model: Sentence transformer model for embeddings
        """
        import chromadb
        from chromadb.config import Settings
        
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize embedding model
        self._init_embedder(embedding_model)
        
        logger.info(
            f"SceneSearchEngine initialized. "
            f"Collection '{collection_name}' has {self.collection.count()} scenes."
        )
    
    def _init_embedder(self, model_name: str):
        """Initialize the sentence transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            # Suppress progress bars from sentence-transformers
            # Note: show_progress_bar parameter only available in newer versions
            self.embedder = SentenceTransformer(model_name)
            self.embedding_dim = self.embedder.get_sentence_embedding_dimension()
            logger.info(f"Loaded embedding model: {model_name} (dim={self.embedding_dim})")
        except ImportError:
            logger.error("sentence-transformers not installed. Run: pip install sentence-transformers")
            raise
        
        # Initialize Gemini for query expansion (lazy load)
        self._gemini_model = None
    
    def _get_gemini(self):
        """Lazy load Gemini for query expansion (ONLY used during search, NOT during indexing)."""
        if self._gemini_model is None:
            try:
                import google.generativeai as genai
                import os
                api_key = os.environ.get("GEMINI_API_KEY")
                if api_key:
                    genai.configure(api_key=api_key)
                    self._gemini_model = genai.GenerativeModel("gemini-2.5-flash")  # Fixed model name
                    logger.info("Gemini query expansion enabled with gemini-2.5-flash (for search only)")
                else:
                    logger.warning("GEMINI_API_KEY not set - query expansion disabled")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini for query expansion: {e}")
        return self._gemini_model
    
    def expand_query(self, query: str) -> List[str]:
        """
        Use AI to expand search query with synonyms and variations.
        
        Args:
            query: Original search query
            
        Returns:
            List of query variations (including original)
        """
        gemini = self._get_gemini()
        if not gemini:
            return [query]  # Return original if Gemini not available
        
        try:
            prompt = f"""Generate 4 alternative phrasings for this video search query: "{query}"

Requirements:
- Use synonyms and related terms
- Keep the same meaning and intent
- Make them natural and searchable
- Focus on visual and action descriptions

Format: Return ONLY the 4 alternatives, one per line, no numbering or explanation.

Example:
Query: "person walking past a car"
Alternatives:
pedestrian strolling near vehicle
individual passing by automobile
human walking beside parked car
person moving past stationary vehicle"""

            response = gemini.generate_content(
                prompt,
                generation_config={"temperature": 0.7, "max_output_tokens": 200}
            )
            
            # Parse response
            alternatives = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
            alternatives = [alt for alt in alternatives if len(alt) > 3][:4]  # Max 4 alternatives
            
            logger.info(f"Query expansion: '{query}' → {len(alternatives)} variations")
            return [query] + alternatives
            
        except Exception as e:
            logger.warning(f"Query expansion failed: {e}")
            return [query]
    
    def expand_query_comprehensive(self, query: str) -> List[str]:
        """
        Use AI to comprehensively expand search query to handle all possible cases in the database.
        Generates multiple variations covering different aspects, synonyms, related concepts, and edge cases.
        
        Args:
            query: Original search query
            
        Returns:
            List of comprehensive query variations (including original)
        """
        gemini = self._get_gemini()
        if not gemini:
            return [query]  # Return original if Gemini not available
        
        try:
            prompt = f"""You are a video search query expansion AI. Generate comprehensive search variations for: "{query}"

Your goal is to generate queries that will match ALL relevant scenes in a video database, covering:
1. Direct synonyms and alternative phrasings
2. Related actions, objects, and concepts
3. Different perspectives and descriptions
4. Visual elements and cinematography terms
5. Emotional and contextual variations
6. Technical and casual descriptions
7. Specific and general versions
8. Edge cases and partial matches

Generate 10-12 diverse query variations that comprehensively cover all possible ways this scene might be described in the database.

Requirements:
- Each variation should be natural and searchable
- Cover different aspects (visual, emotional, technical, contextual)
- Include both specific and general terms
- Think about how the scene might be tagged or described
- Consider camera angles, lighting, mood, actions, objects, people, setting
- Include variations that might catch edge cases

Format: Return ONLY the variations, one per line, no numbering, no explanation.

Example:
Query: "person looking worried"
Variations:
individual with concerned expression
human showing anxiety on face
worried facial expression close-up
person with tense worried look
anxious individual portrait shot
close-up of concerned person
someone displaying worry and stress
nervous person with fearful expression
tense individual showing concern
worried face emotional moment
person with troubled anxious expression
human expressing worry and fear"""

            response = gemini.generate_content(
                prompt,
                generation_config={"temperature": 0.8, "max_output_tokens": 500}
            )
            
            # Parse response
            variations = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
            variations = [v for v in variations if len(v) > 5][:12]  # Max 12 variations
            
            # Always include original query first
            all_queries = [query] + variations
            
            logger.info(f"Comprehensive query expansion: '{query}' → {len(all_queries)} total variations")
            logger.debug(f"Generated queries: {all_queries[:3]}... (showing first 3)")
            
            return all_queries
            
        except Exception as e:
            logger.warning(f"Comprehensive query expansion failed: {e}")
            # Fallback to simple expansion
            return self.expand_query(query)
    
    def _create_search_text(self, analysis: Dict) -> str:
        """
        Create comprehensive searchable text from enhanced scene analysis.
        Combines all fields including NER entities, detailed descriptions, and metadata.
        """
        parts = []
        
        # Main descriptions
        if analysis.get('description'):
            parts.append(analysis['description'])
        
        if analysis.get('detailed_description'):
            parts.append(analysis['detailed_description'])
        
        # Scene metadata
        if analysis.get('scene_type'):
            parts.append(f"Scene type: {analysis['scene_type']}")
        
        if analysis.get('mood'):
            parts.append(f"Mood: {analysis['mood']}")
        
        if analysis.get('secondary_moods'):
            moods = analysis['secondary_moods']
            if isinstance(moods, list):
                parts.append(f"Secondary moods: {', '.join(moods)}")
        
        # Entities (NER)
        entities = analysis.get('entities', {})
        if entities:
            if entities.get('people'):
                parts.append(f"People: {', '.join(entities['people'])}")
            if entities.get('locations'):
                parts.append(f"Locations: {', '.join(entities['locations'])}")
            if entities.get('objects'):
                parts.append(f"Objects: {', '.join(entities['objects'])}")
            if entities.get('vehicles'):
                parts.append(f"Vehicles: {', '.join(entities['vehicles'])}")
            if entities.get('text_visible'):
                parts.append(f"Visible text: {', '.join(entities['text_visible'])}")
        
        # Visual details
        visual = analysis.get('visual_details', {})
        if visual:
            for key, value in visual.items():
                if value:
                    parts.append(f"{key.replace('_', ' ').title()}: {value}")
        
        # Setting details
        setting = analysis.get('setting', {})
        if isinstance(setting, dict):
            if setting.get('specific_location'):
                parts.append(f"Location: {setting['specific_location']}")
            if setting.get('time_of_day'):
                parts.append(f"Time: {setting['time_of_day']}")
        elif isinstance(setting, str):
            parts.append(f"Setting: {setting}")
        
        # People analysis
        people_analysis = analysis.get('people_analysis', [])
        if people_analysis:
            for person in people_analysis:
                if isinstance(person, dict):
                    desc_parts = []
                    if person.get('description'):
                        desc_parts.append(person['description'])
                    if person.get('clothing'):
                        desc_parts.append(f"wearing {person['clothing']}")
                    if person.get('action'):
                        desc_parts.append(f"doing: {person['action']}")
                    if person.get('expression'):
                        desc_parts.append(f"expression: {person['expression']}")
                    if desc_parts:
                        parts.append(f"Person: {' | '.join(desc_parts)}")
        
        # Actions and interactions
        if analysis.get('actions'):
            actions = analysis['actions']
            if isinstance(actions, list):
                parts.append(f"Actions: {', '.join(actions)}")
        
        if analysis.get('interactions'):
            interactions = analysis['interactions']
            if isinstance(interactions, list):
                parts.append(f"Interactions: {', '.join(interactions)}")
        
        # Lighting and camera
        lighting = analysis.get('lighting', {})
        if isinstance(lighting, dict):
            light_desc = []
            for key, value in lighting.items():
                if value:
                    light_desc.append(f"{key}: {value}")
            if light_desc:
                parts.append(f"Lighting: {', '.join(light_desc)}")
        elif isinstance(lighting, str):
            parts.append(f"Lighting: {lighting}")
        
        camera = analysis.get('camera_work', {})
        if isinstance(camera, dict):
            cam_desc = []
            for key, value in camera.items():
                if value:
                    cam_desc.append(f"{key}: {value}")
            if cam_desc:
                parts.append(f"Camera: {', '.join(cam_desc)}")
        elif isinstance(camera, str):
            parts.append(f"Camera: {camera}")
        
        # Colors
        colors = analysis.get('colors', {})
        if isinstance(colors, dict):
            if colors.get('dominant'):
                parts.append(f"Colors: {', '.join(colors['dominant'])}")
        elif isinstance(colors, list):
            parts.append(f"Colors: {', '.join(colors)}")
        
        # All keywords and tags
        if analysis.get('search_keywords'):
            keywords = analysis['search_keywords']
            if isinstance(keywords, list):
                parts.append(f"Keywords: {', '.join(keywords)}")
        
        if analysis.get('semantic_tags'):
            tags = analysis['semantic_tags']
            if isinstance(tags, list):
                parts.append(f"Semantic: {', '.join(tags)}")
        
        if analysis.get('technical_tags'):
            tags = analysis['technical_tags']
            if isinstance(tags, list):
                parts.append(f"Technical: {', '.join(tags)}")
        
        if analysis.get('searchable_phrases'):
            phrases = analysis['searchable_phrases']
            if isinstance(phrases, list):
                parts.append(f"Phrases: {', '.join(phrases)}")
        
        # Legacy tags field
        if analysis.get('tags'):
            tags = analysis['tags']
            if isinstance(tags, list):
                parts.append(f"Tags: {', '.join(tags)}")
        
        # Context clues
        if analysis.get('context_clues'):
            clues = analysis['context_clues']
            if isinstance(clues, list):
                parts.append(f"Context: {', '.join(clues)}")
        
        return " | ".join(parts)
    
    def _embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for text."""
        return self.embedder.encode(text, convert_to_numpy=True, show_progress_bar=False)
    
    def index_scene(
        self,
        scene_id: str,
        clip_info: Dict,
        analysis: Dict
    ) -> bool:
        """
        Index a single scene.
        
        Args:
            scene_id: Unique identifier for the scene
            clip_info: Clip metadata (path, timestamps, etc.)
            analysis: Gemini analysis result
            
        Returns:
            True if successful
        """
        try:
            # Create searchable text
            search_text = self._create_search_text(analysis)
            
            # Generate embedding (NO AI query expansion during indexing)
            embedding = self._embed_text(search_text)
            
            # Prepare metadata (ChromaDB only supports primitive types)
            metadata = {
                'video_id': str(clip_info.get('video_id', '')),
                'clip_path': str(clip_info.get('clip_path', '')),
                'thumbnail_path': str(clip_info.get('thumbnail_path', '')),
                'start_time': float(clip_info.get('start_time', 0)),
                'end_time': float(clip_info.get('end_time', 0)),
                'duration': float(clip_info.get('duration', 0)),
                'clip_index': int(clip_info.get('clip_index', 0)),
                'scene_type': str(analysis.get('scene_type', '')),
                'mood': str(analysis.get('mood', '')),
                'description': str(analysis.get('description', ''))[:500],  # Truncate
                'tags': ','.join(analysis.get('tags', [])) if isinstance(analysis.get('tags'), list) else '',
                'search_text': search_text[:1000]  # Store for debugging
            }
            
            # Add to collection (direct embedding, no AI involved)
            self.collection.add(
                ids=[scene_id],
                embeddings=[embedding.tolist()],
                metadatas=[metadata],
                documents=[search_text]
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error indexing scene {scene_id}: {e}")
            return False
    
    def index_scenes(self, results: List[Dict]) -> int:
        """
        Index multiple scenes from Gemini analysis results.
        
        Args:
            results: List of analysis results from GeminiAnalyzer.analyze_clips_batch()
            
        Returns:
            Number of scenes successfully indexed
        """
        indexed = 0
        
        for result in results:
            if result.get('status') != 'success':
                continue
            
            clip_info = result.get('clip_info', {})
            analysis = result.get('analysis', {})
            
            # Generate scene ID
            video_id = clip_info.get('video_id', 'unknown')
            clip_index = clip_info.get('clip_index', 0)
            scene_id = f"{video_id}_scene_{clip_index:04d}"
            
            if self.index_scene(scene_id, clip_info, analysis):
                indexed += 1
        
        logger.info(f"Indexed {indexed}/{len(results)} scenes")
        return indexed
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict] = None,
        use_query_expansion: bool = True
    ) -> List[Dict]:
        """
        Search for scenes matching a query with AI-powered comprehensive query generation.
        
        Args:
            query: Natural language search query
            top_k: Number of results to return
            filters: Optional metadata filters (e.g., {"mood": "tense"})
            use_query_expansion: Use AI to expand query comprehensively (default: True)
            
        Returns:
            List of matching scenes with scores
        """
        # Expand query with AI if enabled - generates comprehensive variations
        if use_query_expansion:
            queries = self.expand_query_comprehensive(query)
            logger.info(f"AI generated {len(queries)} comprehensive query variations")
        else:
            queries = [query]
        
        # Search with all query variations
        all_results = {}  # Use dict to deduplicate by scene_id
        
        for q in queries:
            # Generate query embedding
            query_embedding = self._embed_text(q)
            
            # Build where clause for filters
            where_clause = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append({key: {"$eq": value}})
                
                if len(conditions) == 1:
                    where_clause = conditions[0]
                elif len(conditions) > 1:
                    where_clause = {"$and": conditions}
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k * 3,  # Get more results for better merging
                where=where_clause,
                include=["metadatas", "documents", "distances"]
            )
            
            # Merge results (keep best score for each scene)
            for i in range(len(results["ids"][0])):
                scene_id = results["ids"][0][i]
                score = float(1 - results["distances"][0][i])
                
                if scene_id not in all_results or score > all_results[scene_id]["score"]:
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    
                    # Parse tags back to list
                    tags = metadata.get('tags', '')
                    if isinstance(tags, str) and tags:
                        tags = tags.split(',')
                    else:
                        tags = []
                    
                    all_results[scene_id] = {
                        "id": scene_id,
                        "score": score,
                        "clip_path": metadata.get('clip_path', ''),
                        "thumbnail_path": metadata.get('thumbnail_path', ''),
                        "video_id": metadata.get('video_id', ''),
                        "start_time": metadata.get('start_time', 0),
                        "end_time": metadata.get('end_time', 0),
                        "duration": metadata.get('duration', 0),
                        "scene_type": metadata.get('scene_type', ''),
                        "mood": metadata.get('mood', ''),
                        "description": metadata.get('description', ''),
                        "tags": tags
                    }
        
        # Sort by score and return top_k
        formatted = sorted(all_results.values(), key=lambda x: x["score"], reverse=True)[:top_k]
        
        logger.info(f"Search complete: {len(formatted)} results (from {len(all_results)} unique scenes)")
        return formatted
    
    def search_by_tags(
        self,
        tags: List[str],
        top_k: int = 10
    ) -> List[Dict]:
        """
        Search for scenes containing specific tags.
        
        Args:
            tags: List of tags to search for
            top_k: Number of results
            
        Returns:
            List of matching scenes
        """
        # Create query from tags
        query = " ".join(tags)
        return self.search(query, top_k=top_k)
    
    def get_scene(self, scene_id: str) -> Optional[Dict]:
        """
        Get a specific scene by ID.
        
        Args:
            scene_id: Scene identifier
            
        Returns:
            Scene data or None if not found
        """
        try:
            result = self.collection.get(
                ids=[scene_id],
                include=["metadatas", "documents"]
            )
            
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "metadata": result["metadatas"][0] if result["metadatas"] else {},
                    "document": result["documents"][0] if result["documents"] else ""
                }
            return None
        except Exception:
            return None
    
    def delete_video(self, video_id: str) -> int:
        """
        Delete all scenes from a specific video.
        
        Args:
            video_id: Video identifier
            
        Returns:
            Number of scenes deleted
        """
        try:
            # Find all scenes for this video
            results = self.collection.get(
                where={"video_id": {"$eq": video_id}},
                include=["metadatas"]
            )
            
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                logger.info(f"Deleted {len(results['ids'])} scenes for video: {video_id}")
                return len(results["ids"])
            
            return 0
        except Exception as e:
            logger.error(f"Error deleting video scenes: {e}")
            return 0
    
    def get_stats(self) -> Dict:
        """
        Get collection statistics.
        
        Returns:
            Dict with stats
        """
        total = self.collection.count()
        
        # Try to get unique video count
        try:
            all_data = self.collection.get(include=["metadatas"])
            video_ids = set()
            for meta in all_data.get("metadatas", []):
                if meta and meta.get("video_id"):
                    video_ids.add(meta["video_id"])
            unique_videos = len(video_ids)
        except:
            unique_videos = 0
        
        return {
            "total_scenes": total,
            "unique_videos": unique_videos
        }
    
    def archive_and_create_new(self) -> str:
        """
        Archive current database and create a new empty one.
        Archives are timestamped for easy recovery.
        
        Returns:
            Path to archived database
        """
        from datetime import datetime
        import shutil
        
        # Create archives directory
        archives_dir = self.persist_dir.parent / "chroma_db_archives"
        archives_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate archive name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"chroma_db_archive_{timestamp}"
        archive_path = archives_dir / archive_name
        
        # Copy current database to archive
        if self.persist_dir.exists():
            shutil.copytree(self.persist_dir, archive_path)
            logger.info(f"Archived database to: {archive_path}")
        
        # Clear current collection
        all_data = self.collection.get()
        if all_data["ids"]:
            self.collection.delete(ids=all_data["ids"])
        
        logger.info("Created new empty database")
        
        return str(archive_path)
    
    def list_archives(self) -> List[Dict]:
        """
        List all archived databases.
        
        Returns:
            List of archive info dicts
        """
        archives_dir = self.persist_dir.parent / "chroma_db_archives"
        
        if not archives_dir.exists():
            return []
        
        archives = []
        for archive_path in sorted(archives_dir.iterdir(), reverse=True):
            if archive_path.is_dir() and archive_path.name.startswith("chroma_db_archive_"):
                # Extract timestamp from name
                timestamp_str = archive_path.name.replace("chroma_db_archive_", "")
                try:
                    from datetime import datetime
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    
                    # Get archive stats
                    archive_client = chromadb.PersistentClient(path=str(archive_path))
                    try:
                        archive_collection = archive_client.get_collection(name="takeone_scenes")
                        scene_count = archive_collection.count()
                    except:
                        scene_count = 0
                    
                    archives.append({
                        'name': archive_path.name,
                        'path': str(archive_path),
                        'timestamp': timestamp,
                        'timestamp_str': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        'scene_count': scene_count
                    })
                except:
                    pass
        
        return archives
    
    def restore_from_archive(self, archive_path: str) -> bool:
        """
        Restore database from an archive.
        Current database is archived before restoration.
        
        Args:
            archive_path: Path to archive to restore
            
        Returns:
            True if successful
        """
        import shutil
        from datetime import datetime
        
        archive_path = Path(archive_path)
        
        if not archive_path.exists():
            logger.error(f"Archive not found: {archive_path}")
            return False
        
        try:
            # Archive current database first
            self.archive_and_create_new()
            
            # Clear current database directory
            if self.persist_dir.exists():
                shutil.rmtree(self.persist_dir)
            
            # Copy archive to current location
            shutil.copytree(archive_path, self.persist_dir)
            
            # Reinitialize client and collection
            import chromadb
            from chromadb.config import Settings
            
            self.client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=Settings(anonymized_telemetry=False)
            )
            
            self.collection = self.client.get_collection(name="takeone_scenes")
            
            logger.info(f"Restored database from: {archive_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore archive: {e}")
            return False


# Legacy VectorSearch class for backwards compatibility
class VectorSearch:
    """ChromaDB-based vector search for video clip embeddings (legacy)."""
    
    def __init__(self, persist_dir: str = "./chroma_db", collection_name: str = "footage"):
        import chromadb
        from chromadb.config import Settings
        
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize embedder for legacy mode
        try:
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        except:
            self.embedder = None
        
        print(f"ChromaDB initialized. Collection '{collection_name}' has {self.collection.count()} items.")
    
    def add_clip(self, clip_id: str, embedding: np.ndarray, metadata: Dict[str, Any]) -> None:
        self.collection.add(
            ids=[clip_id],
            embeddings=[embedding.tolist()],
            metadatas=[metadata]
        )
    
    def add_clips(self, clip_ids: List[str], embeddings: np.ndarray, metadatas: List[Dict[str, Any]]) -> None:
        self.collection.add(
            ids=clip_ids,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )
    
    def search(self, query_embedding: np.ndarray, top_k: int = 10, filter_metadata: Optional[Dict] = None) -> List[Dict]:
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=filter_metadata
        )
        
        formatted = []
        for i in range(len(results["ids"][0])):
            formatted.append({
                "id": results["ids"][0][i],
                "score": 1 - results["distances"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
            })
        
        return formatted
    
    def count(self) -> int:
        return self.collection.count()
    
    def clear(self) -> None:
        """
        Clear all scenes from the collection.
        Note: Use archive_and_create_new() to preserve data before clearing.
        """
        all_data = self.collection.get()
        if all_data["ids"]:
            self.collection.delete(ids=all_data["ids"])
        logger.info("Cleared all scenes from collection")


# Global instances
_scene_engine: Optional[SceneSearchEngine] = None
_legacy_search: Optional[VectorSearch] = None


def get_scene_engine(persist_dir: str = "./chroma_db") -> SceneSearchEngine:
    """Get or create global scene search engine."""
    global _scene_engine
    if _scene_engine is None:
        _scene_engine = SceneSearchEngine(persist_dir=persist_dir)
    return _scene_engine


def get_search(persist_dir: str = "./chroma_db") -> VectorSearch:
    """Get or create global legacy search instance."""
    global _legacy_search
    if _legacy_search is None:
        _legacy_search = VectorSearch(persist_dir=persist_dir)
    return _legacy_search


if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    # Demo usage
    engine = SceneSearchEngine()
    
    print(f"\nCollection stats: {engine.get_stats()}")
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\nSearching for: '{query}'")
        
        results = engine.search(query, top_k=5)
        
        if results:
            print(f"\nFound {len(results)} results:")
            for r in results:
                print(f"\n  [{r['score']:.2f}] {r['id']}")
                print(f"       {r['description'][:100]}...")
                print(f"       Mood: {r['mood']} | Type: {r['scene_type']}")
        else:
            print("No results found.")
    else:
        print("\nUsage: python vector_search.py <search query>")
        print("Example: python vector_search.py romantic sunset beach")
