"""
CineSearch AI - Professional Gradio Interface
Clean, modern UI for AI-powered video search
"""

import gradio as gr
import os
import logging
import tempfile
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import pipeline components
from ingestion.pipeline import TakeOnePipeline
from search.vector_search import SceneSearchEngine

# Global state
pipeline = None
search_engine = None

def initialize_pipeline():
    """Initialize the processing pipeline"""
    global pipeline, search_engine
    
    if pipeline is None:
        try:
            pipeline = TakeOnePipeline(
                output_dir="./output",
                chroma_dir="./chroma_db",
                gemini_model="gemini-2.5-flash"
            )
            search_engine = pipeline.search_engine
            
            # Check GPU
            gpu_available = torch.cuda.is_available()
            gpu_name = torch.cuda.get_device_name(0) if gpu_available else "None"
            
            return f"Pipeline initialized successfully. GPU: {gpu_name if gpu_available else 'CPU only'}"
        except Exception as e:
            return f"Error initializing pipeline: {str(e)}"
    
    return "Pipeline already initialized"

def get_stats() -> Dict:
    """Get library statistics"""
    if search_engine:
        return search_engine.get_stats()
    return {"total_scenes": 0, "unique_videos": 0}

def process_video_file(video_file, progress=gr.Progress()) -> Tuple[str, str]:
    """Process uploaded video file"""
    if not video_file:
        return "No video file provided", ""
    
    if not pipeline:
        return "Pipeline not initialized. Please check API key.", ""
    
    try:
        progress(0, desc="Starting video processing...")
        
        # Get video path
        video_path = video_file.name if hasattr(video_file, 'name') else video_file
        
        # Progress callback
        def update_progress(stage, current, total):
            pct = current / total if total > 0 else 0
            progress(pct, desc=f"{stage}: {current}/{total}")
        
        # Process video
        result = pipeline.process_video(
            video_path,
            progress_callback=update_progress,
            use_yolo=True,
            yolo_scene_detection=True
        )
        
        if result["status"] == "complete":
            stats = get_stats()
            success_msg = f"Video processed successfully!\n\n"
            success_msg += f"Scenes detected: {result['stages']['scene_detection']['optimized_scenes']}\n"
            success_msg += f"Clips extracted: {result['stages']['clip_extraction']['clips_created']}\n"
            success_msg += f"Thumbnails: {result['stages']['thumbnails']['created']}\n"
            success_msg += f"Analyzed: {result['stages']['analysis']['successful']}/{result['stages']['analysis']['total']}\n"
            success_msg += f"Indexed: {result['stages']['indexing']['indexed']}\n\n"
            success_msg += f"Total library: {stats['total_scenes']} scenes from {stats.get('unique_videos', 0)} videos"
            
            return success_msg, json.dumps(result, indent=2)
        else:
            return f"Processing failed: {result.get('error', 'Unknown error')}", json.dumps(result, indent=2)
            
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        return f"Error: {str(e)}", ""

def process_video_url(url: str, custom_name: str, cleanup: bool, progress=gr.Progress()) -> Tuple[str, str]:
    """Process video from URL"""
    if not url:
        return "No URL provided", ""
    
    if not pipeline:
        return "Pipeline not initialized. Please check API key.", ""
    
    try:
        progress(0, desc="Downloading video...")
        
        # Progress callback
        def update_progress(stage, current, total):
            pct = current / total if total > 0 else 0
            progress(pct, desc=f"{stage}: {current}/{total}")
        
        # Process video from URL
        result = pipeline.process_video(
            url,
            video_id=custom_name if custom_name else None,
            progress_callback=update_progress,
            use_yolo=True,
            yolo_scene_detection=True,
            cleanup_download=cleanup
        )
        
        if result["status"] == "complete":
            stats = get_stats()
            success_msg = f"Video processed successfully!\n\n"
            success_msg += f"Source: {result.get('original_url', url)}\n"
            success_msg += f"Scenes detected: {result['stages']['scene_detection']['optimized_scenes']}\n"
            success_msg += f"Clips extracted: {result['stages']['clip_extraction']['clips_created']}\n"
            success_msg += f"Thumbnails: {result['stages']['thumbnails']['created']}\n"
            success_msg += f"Analyzed: {result['stages']['analysis']['successful']}/{result['stages']['analysis']['total']}\n"
            success_msg += f"Indexed: {result['stages']['indexing']['indexed']}\n\n"
            success_msg += f"Total library: {stats['total_scenes']} scenes from {stats.get('unique_videos', 0)} videos"
            
            return success_msg, json.dumps(result, indent=2)
        else:
            return f"Processing failed: {result.get('error', 'Unknown error')}", json.dumps(result, indent=2)
            
    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        return f"Error: {str(e)}", ""

def search_scenes(query: str, top_k: int) -> Tuple[str, List]:
    """Search for scenes matching query"""
    if not query:
        return "Please enter a search query", []
    
    if not search_engine:
        return "Search engine not initialized", []
    
    try:
        # Perform search
        results = search_engine.search(query, top_k=top_k)
        
        if not results:
            return "No results found", []
        
        # Format results for gallery
        gallery_items = []
        result_text = f"Found {len(results)} results:\n\n"
        
        for i, res in enumerate(results):
            metadata = res.get("metadata", {})
            
            # Add to text results
            result_text += f"Result {i+1}:\n"
            result_text += f"  Video: {metadata.get('video_id', 'Unknown')}\n"
            result_text += f"  Time: {metadata.get('start_time', 0):.1f}s - {metadata.get('end_time', 0):.1f}s\n"
            result_text += f"  Type: {metadata.get('scene_type', 'Unknown')}\n"
            result_text += f"  Description: {metadata.get('description', 'No description')[:100]}...\n"
            result_text += f"  Score: {res.get('distance', 0):.3f}\n\n"
            
            # Add to gallery - use absolute path
            thumbnail = metadata.get('thumbnail_path', '')
            if thumbnail:
                # Convert to absolute path if relative
                if not os.path.isabs(thumbnail):
                    thumbnail = os.path.abspath(thumbnail)
                
                if os.path.exists(thumbnail):
                    caption = f"{metadata.get('video_id', 'Unknown')} | {metadata.get('start_time', 0):.1f}s"
                    gallery_items.append((thumbnail, caption))
                    logger.debug(f"Added thumbnail to gallery: {thumbnail}")
                else:
                    logger.warning(f"Thumbnail not found: {thumbnail}")
        
        logger.info(f"Search returned {len(gallery_items)} thumbnails for gallery")
        return result_text, gallery_items
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return f"Search error: {str(e)}", []

def get_library_info() -> Tuple[str, List]:
    """Get library information and thumbnails"""
    if not search_engine:
        return "Search engine not initialized", []
    
    try:
        stats = get_stats()
        
        info_text = f"Library Statistics:\n\n"
        info_text += f"Total Scenes: {stats['total_scenes']}\n"
        info_text += f"Unique Videos: {stats.get('unique_videos', 0)}\n"
        
        # Get all scenes
        all_data = search_engine.collection.get()
        
        if not all_data or not all_data.get("ids"):
            return info_text + "\nNo scenes in library", []
        
        # Get thumbnails for gallery
        gallery_items = []
        for i, scene_id in enumerate(all_data["ids"][:50]):  # Limit to 50 for performance
            metadata = all_data["metadatas"][i] if all_data.get("metadatas") else {}
            thumbnail = metadata.get('thumbnail_path', '')
            
            if thumbnail and os.path.exists(thumbnail):
                video_id = metadata.get('video_id', 'Unknown')
                start_time = metadata.get('start_time', 0)
                caption = f"{video_id} | {start_time:.1f}s"
                gallery_items.append((thumbnail, caption))
        
        info_text += f"\nShowing {len(gallery_items)} thumbnails"
        
        return info_text, gallery_items
        
    except Exception as e:
        logger.error(f"Error getting library info: {e}")
        return f"Error: {str(e)}", []

def archive_library() -> str:
    """Archive current library and create new one"""
    if not search_engine:
        return "Search engine not initialized"
    
    try:
        archive_path = search_engine.archive_and_create_new()
        return f"Library archived successfully to:\n{archive_path}\n\nNew empty library created."
    except Exception as e:
        return f"Error archiving library: {str(e)}"

def list_archives() -> str:
    """List available archives"""
    if not search_engine:
        return "Search engine not initialized"
    
    try:
        archives = search_engine.list_archives()
        
        if not archives:
            return "No archives found"
        
        result = f"Available Archives ({len(archives)}):\n\n"
        for archive in archives:
            result += f"Name: {archive['name']}\n"
            result += f"Created: {archive['created']}\n"
            result += f"Path: {archive['path']}\n\n"
        
        return result
    except Exception as e:
        return f"Error listing archives: {str(e)}"

def restore_archive(archive_name: str) -> str:
    """Restore library from archive"""
    if not archive_name:
        return "Please enter archive name"
    
    if not search_engine:
        return "Search engine not initialized"
    
    try:
        search_engine.restore_from_archive(archive_name)
        stats = get_stats()
        return f"Archive restored successfully!\n\nLibrary now contains:\n{stats['total_scenes']} scenes from {stats.get('unique_videos', 0)} videos"
    except Exception as e:
        return f"Error restoring archive: {str(e)}"

def delete_video(video_id: str) -> str:
    """Delete all scenes from a video"""
    if not video_id:
        return "Please enter video ID"
    
    if not search_engine:
        return "Search engine not initialized"
    
    try:
        search_engine.delete_video(video_id)
        stats = get_stats()
        return f"Video '{video_id}' deleted successfully.\n\nLibrary now contains:\n{stats['total_scenes']} scenes from {stats.get('unique_videos', 0)} videos"
    except Exception as e:
        return f"Error deleting video: {str(e)}"

# Build Gradio Interface
def build_interface():
    """Build the Gradio interface"""
    
    # Custom CSS for professional look with full width
    custom_css = """
    .gradio-container {
        font-family: 'Inter', sans-serif;
        max-width: 100% !important;
        width: 100% !important;
        padding: 2rem !important;
    }
    .contain {
        max-width: 100% !important;
    }
    .gr-button-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
    }
    .gr-button-secondary {
        background: #f3f4f6;
        color: #374151;
        border: 1px solid #d1d5db;
    }
    h1 {
        text-align: center;
        color: #1f2937;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    """
    
    with gr.Blocks(css=custom_css, title="CineSearch AI", theme=gr.themes.Soft()) as app:
        
        # Header
        gr.Markdown("# CineSearch AI")
        gr.Markdown("<p class='subtitle'>AI-Powered Video Scene Search Engine</p>", elem_classes="subtitle")
        
        # Initialize pipeline on load
        with gr.Row():
            init_status = gr.Textbox(label="System Status", value="Initializing...", interactive=False)
        
        # Main tabs
        with gr.Tabs():
            
            # Search Tab
            with gr.Tab("Search"):
                gr.Markdown("### Search Your Video Library")
                gr.Markdown("Enter natural language queries to find specific scenes")
                
                with gr.Row():
                    with gr.Column(scale=3):
                        search_query = gr.Textbox(
                            label="Search Query",
                            placeholder="e.g., 'person speaking at podium', 'sunset over city', 'car chase scene'",
                            lines=2
                        )
                    with gr.Column(scale=1):
                        top_k = gr.Slider(
                            label="Results",
                            minimum=1,
                            maximum=50,
                            value=10,
                            step=1
                        )
                
                search_btn = gr.Button("Search", variant="primary", size="lg")
                
                with gr.Row():
                    with gr.Column():
                        search_results_text = gr.Textbox(
                            label="Search Results",
                            lines=15,
                            interactive=False
                        )
                    with gr.Column():
                        search_results_gallery = gr.Gallery(
                            label="Matching Scenes",
                            columns=3,
                            height="auto"
                        )
                
                search_btn.click(
                    fn=search_scenes,
                    inputs=[search_query, top_k],
                    outputs=[search_results_text, search_results_gallery]
                )
            
            # Upload Tab
            with gr.Tab("Upload"):
                gr.Markdown("### Add Videos to Library")
                
                with gr.Tabs():
                    # File upload
                    with gr.Tab("Upload File"):
                        video_file = gr.File(
                            label="Select Video File",
                            file_types=["video"],
                            type="filepath"
                        )
                        upload_btn = gr.Button("Process Video", variant="primary", size="lg")
                        
                        upload_status = gr.Textbox(label="Status", lines=10, interactive=False)
                        upload_details = gr.JSON(label="Processing Details", visible=False)
                        
                        upload_btn.click(
                            fn=process_video_file,
                            inputs=[video_file],
                            outputs=[upload_status, upload_details]
                        )
                    
                    # URL input
                    with gr.Tab("From URL"):
                        gr.Markdown("Supported: YouTube, Google Drive, Vimeo, direct links")
                        
                        url_input = gr.Textbox(
                            label="Video URL",
                            placeholder="https://www.youtube.com/watch?v=...",
                            lines=1
                        )
                        
                        with gr.Row():
                            custom_name = gr.Textbox(
                                label="Custom Name (optional)",
                                placeholder="Leave empty to use video title",
                                scale=3
                            )
                            cleanup = gr.Checkbox(
                                label="Auto-cleanup",
                                value=True,
                                scale=1
                            )
                        
                        url_btn = gr.Button("Process from URL", variant="primary", size="lg")
                        
                        url_status = gr.Textbox(label="Status", lines=10, interactive=False)
                        url_details = gr.JSON(label="Processing Details", visible=False)
                        
                        url_btn.click(
                            fn=process_video_url,
                            inputs=[url_input, custom_name, cleanup],
                            outputs=[url_status, url_details]
                        )
            
            # Library Tab
            with gr.Tab("Library"):
                gr.Markdown("### Manage Your Video Library")
                
                with gr.Row():
                    refresh_btn = gr.Button("Refresh Library", variant="secondary")
                    delete_video_btn = gr.Button("Delete Video", variant="secondary")
                
                with gr.Row():
                    library_info = gr.Textbox(label="Library Information", lines=5, interactive=False)
                
                library_gallery = gr.Gallery(
                    label="Library Contents",
                    columns=4,
                    height="auto"
                )
                
                # Delete video section
                with gr.Accordion("Delete Video", open=False):
                    video_id_input = gr.Textbox(
                        label="Video ID",
                        placeholder="Enter video ID to delete"
                    )
                    confirm_delete_btn = gr.Button("Confirm Delete", variant="stop")
                    delete_status = gr.Textbox(label="Status", interactive=False)
                    
                    confirm_delete_btn.click(
                        fn=delete_video,
                        inputs=[video_id_input],
                        outputs=[delete_status]
                    )
                
                refresh_btn.click(
                    fn=get_library_info,
                    outputs=[library_info, library_gallery]
                )
            
            # Archive Tab
            with gr.Tab("Archives"):
                gr.Markdown("### Library Archive Management")
                gr.Markdown("Create backups of your library or restore from previous versions")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### Create New Archive")
                        archive_btn = gr.Button("Archive Current Library", variant="primary")
                        archive_status = gr.Textbox(label="Status", lines=5, interactive=False)
                        
                        archive_btn.click(
                            fn=archive_library,
                            outputs=[archive_status]
                        )
                    
                    with gr.Column():
                        gr.Markdown("#### Restore from Archive")
                        list_archives_btn = gr.Button("List Archives", variant="secondary")
                        archives_list = gr.Textbox(label="Available Archives", lines=10, interactive=False)
                        
                        archive_name_input = gr.Textbox(
                            label="Archive Name",
                            placeholder="e.g., chroma_db_archive_20260131_123456"
                        )
                        restore_btn = gr.Button("Restore Archive", variant="primary")
                        restore_status = gr.Textbox(label="Status", lines=3, interactive=False)
                        
                        list_archives_btn.click(
                            fn=list_archives,
                            outputs=[archives_list]
                        )
                        
                        restore_btn.click(
                            fn=restore_archive,
                            inputs=[archive_name_input],
                            outputs=[restore_status]
                        )
        
        # Footer
        gr.Markdown("---")
        gr.Markdown(
            "<p style='text-align: center; color: #6b7280;'>CineSearch AI | Powered by Gemini 2.5 Flash & YOLO</p>"
        )
        
        # Initialize on load
        app.load(fn=initialize_pipeline, outputs=[init_status])
    
    return app

if __name__ == "__main__":
    # Check for API key
    if not os.environ.get("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY not set. Please set it in your .env file.")
    
    # Build and launch
    app = build_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
