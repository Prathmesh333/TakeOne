"""
CineSearch AI - Production-Ready Gradio Interface
Complete UI with video clips, descriptions, and all features
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
            
            return f"Pipeline initialized. GPU: {gpu_name if gpu_available else 'CPU only'}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    return "Pipeline already initialized"

def get_stats() -> Dict:
    """Get library statistics"""
    if search_engine:
        return search_engine.get_stats()
    return {"total_scenes": 0, "unique_videos": 0}

def process_video_file(video_file, progress=gr.Progress()) -> str:
    """Process uploaded video file"""
    if not video_file:
        return "No video file provided"
    
    if not pipeline:
        return "Pipeline not initialized"
    
    try:
        progress(0, desc="Starting...")
        video_path = video_file.name if hasattr(video_file, 'name') else video_file
        
        def update_progress(stage, current, total):
            pct = current / total if total > 0 else 0
            progress(pct, desc=f"{stage}: {current}/{total}")
        
        result = pipeline.process_video(
            video_path,
            progress_callback=update_progress,
            use_yolo=True,
            yolo_scene_detection=True
        )
        
        if result["status"] == "complete":
            stats = get_stats()
            msg = f"✅ Video processed successfully!\n\n"
            msg += f"📊 Scenes: {result['stages']['scene_detection']['optimized_scenes']}\n"
            msg += f"🎬 Clips: {result['stages']['clip_extraction']['clips_created']}\n"
            msg += f"🖼️ Thumbnails: {result['stages']['thumbnails']['created']}\n"
            msg += f"🤖 Analyzed: {result['stages']['analysis']['successful']}/{result['stages']['analysis']['total']}\n"
            msg += f"💾 Indexed: {result['stages']['indexing']['indexed']}\n\n"
            msg += f"📚 Library: {stats['total_scenes']} scenes from {stats.get('unique_videos', 0)} videos"
            return msg
        else:
            return f"❌ Failed: {result.get('error', 'Unknown error')}"
            
    except Exception as e:
        return f"❌ Error: {str(e)}"

def process_video_url(url: str, custom_name: str, cleanup: bool, progress=gr.Progress()) -> str:
    """Process video from URL"""
    if not url:
        return "No URL provided"
    
    if not pipeline:
        return "Pipeline not initialized"
    
    try:
        progress(0, desc="Downloading...")
        
        def update_progress(stage, current, total):
            pct = current / total if total > 0 else 0
            progress(pct, desc=f"{stage}: {current}/{total}")
        
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
            msg = f"✅ Video processed successfully!\n\n"
            msg += f"🔗 Source: {result.get('original_url', url)}\n"
            msg += f"📊 Scenes: {result['stages']['scene_detection']['optimized_scenes']}\n"
            msg += f"🎬 Clips: {result['stages']['clip_extraction']['clips_created']}\n"
            msg += f"🖼️ Thumbnails: {result['stages']['thumbnails']['created']}\n"
            msg += f"🤖 Analyzed: {result['stages']['analysis']['successful']}/{result['stages']['analysis']['total']}\n"
            msg += f"💾 Indexed: {result['stages']['indexing']['indexed']}\n\n"
            msg += f"📚 Library: {stats['total_scenes']} scenes from {stats.get('unique_videos', 0)} videos"
            return msg
        else:
            return f"❌ Failed: {result.get('error', 'Unknown error')}"
            
    except Exception as e:
        return f"❌ Error: {str(e)}"

def search_scenes(query: str, top_k: int) -> Tuple[str, str, str, str, str, str, str]:
    """Search for scenes and return formatted HTML results with video paths"""
    if not query:
        return "<p>Please enter a search query</p>", None, None, None, None, None, None
    
    if not search_engine:
        return "<p>Search engine not initialized</p>", None, None, None, None, None, None
    
    try:
        results = search_engine.search(query, top_k=top_k)
        
        if not results:
            return "<p>No results found</p>", None, None, None, None, None, None
        
        # Build HTML with descriptions
        html = f"<h2>Found {len(results)} Results</h2>"
        video_paths = [None, None, None, None, None, None]
        
        for i, res in enumerate(results[:6]):  # Show first 6 videos
            metadata = res.get("metadata", {})
            
            video_id = metadata.get('video_id', 'Unknown')
            start_time = metadata.get('start_time', 0)
            end_time = metadata.get('end_time', 0)
            scene_type = metadata.get('scene_type', 'Unknown')
            description = metadata.get('description', 'No description')
            mood = metadata.get('mood', '')
            setting = metadata.get('setting', '')
            lighting = metadata.get('lighting', '')
            camera_work = metadata.get('camera_work', '')
            colors = metadata.get('colors', '')
            people = metadata.get('people', '')
            objects = metadata.get('objects', '')
            actions = metadata.get('actions', '')
            tags = metadata.get('tags', '')
            clip_path = metadata.get('clip_path', '')
            score = res.get('distance', 0)
            
            # Convert to absolute path
            if clip_path and not os.path.isabs(clip_path):
                clip_path = os.path.abspath(clip_path)
            
            # Add to video paths
            if clip_path and os.path.exists(clip_path):
                video_paths[i] = clip_path
            
            html += f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 20px 0; background: white;">
                <h3 style="margin: 0 0 10px 0; color: #333;">Result {i+1}</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div>
                        <p style="margin: 5px 0;"><strong>Video:</strong> {video_id}</p>
                        <p style="margin: 5px 0;"><strong>Time:</strong> {start_time:.1f}s - {end_time:.1f}s ({end_time - start_time:.1f}s)</p>
                        <p style="margin: 5px 0;"><strong>Type:</strong> <span style="background: #667eea; color: white; padding: 2px 8px; border-radius: 4px;">{scene_type}</span></p>
                        <p style="margin: 5px 0;"><strong>Relevance Score:</strong> {score:.3f}</p>
                    </div>
                    <div>
                        {f'<p style="margin: 5px 0;"><strong>Mood:</strong> {mood}</p>' if mood else ''}
                        {f'<p style="margin: 5px 0;"><strong>Setting:</strong> {setting}</p>' if setting else ''}
                        {f'<p style="margin: 5px 0;"><strong>Lighting:</strong> {lighting}</p>' if lighting else ''}
                        {f'<p style="margin: 5px 0;"><strong>Camera:</strong> {camera_work}</p>' if camera_work else ''}
                    </div>
                </div>
                
                <div style="margin-top: 15px;">
                    <p style="margin: 5px 0 10px 0;"><strong>Description:</strong></p>
                    <p style="margin: 5px 0; line-height: 1.6; background: #f8f9fa; padding: 10px; border-radius: 4px;">{description}</p>
                </div>
                
                {f'<p style="margin: 10px 0 5px 0;"><strong>Colors:</strong> {colors}</p>' if colors else ''}
                {f'<p style="margin: 5px 0;"><strong>People:</strong> {people}</p>' if people else ''}
                {f'<p style="margin: 5px 0;"><strong>Objects:</strong> {objects}</p>' if objects else ''}
                {f'<p style="margin: 5px 0;"><strong>Actions:</strong> {actions}</p>' if actions else ''}
            """
            
            # Add tags separately to avoid f-string backslash issue
            if tags:
                tag_html = '<p style="margin: 10px 0 5px 0;"><strong>Tags:</strong> '
                for tag in tags.split(", "):
                    tag_html += f'<span style="background: #e9ecef; padding: 2px 6px; border-radius: 3px; margin: 2px; display: inline-block;">{tag}</span> '
                tag_html += '</p>'
                html += tag_html
            
            html += "</div>"
        
        return html, video_paths[0], video_paths[1], video_paths[2], video_paths[3], video_paths[4], video_paths[5]
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return f"<p>Search error: {str(e)}</p>", None, None, None, None, None, None

def get_library_info() -> Tuple[str, str, str, str, str, str, str, str, str, str, str, str, str]:
    """Get library information as HTML with video paths"""
    if not search_engine:
        return "<p>Search engine not initialized</p>", None, None, None, None, None, None, None, None, None, None, None, None
    
    try:
        stats = get_stats()
        all_data = search_engine.collection.get(include=["metadatas"])
        
        if not all_data or not all_data.get("ids"):
            return "<p>No scenes in library</p>", None, None, None, None, None, None, None, None, None, None, None, None
        
        # Group by video
        videos = {}
        for i, scene_id in enumerate(all_data["ids"]):
            metadata = all_data["metadatas"][i] if all_data.get("metadatas") else {}
            video_id = metadata.get("video_id", "unknown")
            if video_id not in videos:
                videos[video_id] = []
            videos[video_id].append(metadata)
        
        html = f"""
        <h2>Library Statistics</h2>
        <p><strong>Total Scenes:</strong> {stats['total_scenes']}</p>
        <p><strong>Unique Videos:</strong> {stats.get('unique_videos', 0)}</p>
        <hr>
        <h2>Videos in Library</h2>
        """
        
        video_paths = [None] * 12
        video_idx = 0
        
        for video_id, scenes in videos.items():
            html += f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 15px 0; background: white;">
                <h3 style="color: #333;">{video_id}</h3>
                <p><strong>Total Scenes:</strong> {len(scenes)}</p>
                <p style="font-size: 12px; color: #666;">Showing first clips in video player grid below</p>
            </div>
            """
            
            # Add clips to video paths
            for scene in scenes:
                if video_idx >= 12:
                    break
                    
                clip_path = scene.get('clip_path', '')
                if clip_path and not os.path.isabs(clip_path):
                    clip_path = os.path.abspath(clip_path)
                
                if clip_path and os.path.exists(clip_path):
                    video_paths[video_idx] = clip_path
                    video_idx += 1
        
        return (html, video_paths[0], video_paths[1], video_paths[2], video_paths[3], 
                video_paths[4], video_paths[5], video_paths[6], video_paths[7],
                video_paths[8], video_paths[9], video_paths[10], video_paths[11])
        
    except Exception as e:
        return f"<p>Error: {str(e)}</p>", None, None, None, None, None, None, None, None, None, None, None, None

def archive_library() -> str:
    """Archive current library"""
    if not search_engine:
        return "Search engine not initialized"
    
    try:
        archive_path = search_engine.archive_and_create_new()
        return f"✅ Library archived to:\n{archive_path}\n\nNew empty library created."
    except Exception as e:
        return f"❌ Error: {str(e)}"

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
            result += f"📦 {archive['name']}\n"
            result += f"   Created: {archive['created']}\n"
            result += f"   Path: {archive['path']}\n\n"
        
        return result
    except Exception as e:
        return f"Error: {str(e)}"

def restore_archive(archive_name: str) -> str:
    """Restore from archive"""
    if not archive_name:
        return "Please enter archive name"
    
    if not search_engine:
        return "Search engine not initialized"
    
    try:
        search_engine.restore_from_archive(archive_name)
        stats = get_stats()
        return f"✅ Restored!\n\nLibrary now has:\n{stats['total_scenes']} scenes from {stats.get('unique_videos', 0)} videos"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def delete_video(video_id: str) -> str:
    """Delete video from library"""
    if not video_id:
        return "Please enter video ID"
    
    if not search_engine:
        return "Search engine not initialized"
    
    try:
        search_engine.delete_video(video_id)
        stats = get_stats()
        return f"✅ Deleted '{video_id}'\n\nLibrary now has:\n{stats['total_scenes']} scenes from {stats.get('unique_videos', 0)} videos"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Build Interface
def build_interface():
    """Build production-ready Gradio interface"""
    
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
    """
    
    with gr.Blocks(css=custom_css, title="CineSearch AI Pro", theme=gr.themes.Soft()) as app:
        
        gr.Markdown("# CineSearch AI")
        gr.Markdown("AI-Powered Video Scene Search Engine")
        
        with gr.Row():
            init_status = gr.Textbox(label="System Status", value="Initializing...", interactive=False)
        
        with gr.Tabs():
            
            # Search Tab
            with gr.Tab("🔍 Search"):
                gr.Markdown("### Search Your Video Library")
                
                with gr.Row():
                    search_query = gr.Textbox(
                        label="Search Query",
                        placeholder="e.g., 'person speaking', 'sunset scene', 'action sequence'",
                        scale=4
                    )
                    top_k = gr.Slider(label="Results", minimum=1, maximum=50, value=10, step=1, scale=1)
                
                search_btn = gr.Button("Search", variant="primary", size="lg")
                search_results = gr.HTML(label="Results Details")
                
                gr.Markdown("### Video Clips")
                with gr.Row():
                    search_video_1 = gr.Video(label="Clip 1", interactive=False)
                    search_video_2 = gr.Video(label="Clip 2", interactive=False)
                    search_video_3 = gr.Video(label="Clip 3", interactive=False)
                
                with gr.Row():
                    search_video_4 = gr.Video(label="Clip 4", interactive=False)
                    search_video_5 = gr.Video(label="Clip 5", interactive=False)
                    search_video_6 = gr.Video(label="Clip 6", interactive=False)
                
                search_btn.click(
                    fn=search_scenes,
                    inputs=[search_query, top_k],
                    outputs=[search_results, search_video_1, search_video_2, search_video_3, 
                            search_video_4, search_video_5, search_video_6]
                )
            
            # Upload Tab
            with gr.Tab("📤 Upload"):
                with gr.Tabs():
                    with gr.Tab("Upload File"):
                        video_file = gr.File(label="Select Video", file_types=["video"])
                        upload_btn = gr.Button("Process Video", variant="primary", size="lg")
                        upload_status = gr.Textbox(label="Status", lines=10, interactive=False)
                        
                        upload_btn.click(fn=process_video_file, inputs=[video_file], outputs=[upload_status])
                    
                    with gr.Tab("From URL"):
                        gr.Markdown("Supported: YouTube, Google Drive, Vimeo, direct links")
                        url_input = gr.Textbox(label="Video URL", placeholder="https://...")
                        with gr.Row():
                            custom_name = gr.Textbox(label="Custom Name (optional)", scale=3)
                            cleanup = gr.Checkbox(label="Auto-cleanup", value=True, scale=1)
                        url_btn = gr.Button("Process from URL", variant="primary", size="lg")
                        url_status = gr.Textbox(label="Status", lines=10, interactive=False)
                        
                        url_btn.click(fn=process_video_url, inputs=[url_input, custom_name, cleanup], outputs=[url_status])
            
            # Library Tab
            with gr.Tab("📚 Library"):
                gr.Markdown("### Your Video Library")
                refresh_btn = gr.Button("Refresh Library", variant="secondary")
                library_display = gr.HTML(label="Library Info")
                
                gr.Markdown("### Video Clips")
                with gr.Row():
                    lib_video_1 = gr.Video(label="Clip 1", interactive=False)
                    lib_video_2 = gr.Video(label="Clip 2", interactive=False)
                    lib_video_3 = gr.Video(label="Clip 3", interactive=False)
                    lib_video_4 = gr.Video(label="Clip 4", interactive=False)
                
                with gr.Row():
                    lib_video_5 = gr.Video(label="Clip 5", interactive=False)
                    lib_video_6 = gr.Video(label="Clip 6", interactive=False)
                    lib_video_7 = gr.Video(label="Clip 7", interactive=False)
                    lib_video_8 = gr.Video(label="Clip 8", interactive=False)
                
                with gr.Row():
                    lib_video_9 = gr.Video(label="Clip 9", interactive=False)
                    lib_video_10 = gr.Video(label="Clip 10", interactive=False)
                    lib_video_11 = gr.Video(label="Clip 11", interactive=False)
                    lib_video_12 = gr.Video(label="Clip 12", interactive=False)
                
                refresh_btn.click(
                    fn=get_library_info, 
                    outputs=[library_display, lib_video_1, lib_video_2, lib_video_3, lib_video_4,
                            lib_video_5, lib_video_6, lib_video_7, lib_video_8,
                            lib_video_9, lib_video_10, lib_video_11, lib_video_12]
                )
                
                with gr.Accordion("Delete Video", open=False):
                    video_id_input = gr.Textbox(label="Video ID")
                    delete_btn = gr.Button("Delete", variant="stop")
                    delete_status = gr.Textbox(label="Status", interactive=False)
                    delete_btn.click(fn=delete_video, inputs=[video_id_input], outputs=[delete_status])
            
            # Archives Tab
            with gr.Tab("💾 Archives"):
                gr.Markdown("### Library Archive Management")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### Create Archive")
                        archive_btn = gr.Button("Archive Current Library", variant="primary")
                        archive_status = gr.Textbox(label="Status", lines=5, interactive=False)
                        archive_btn.click(fn=archive_library, outputs=[archive_status])
                    
                    with gr.Column():
                        gr.Markdown("#### Restore Archive")
                        list_btn = gr.Button("List Archives", variant="secondary")
                        archives_list = gr.Textbox(label="Available Archives", lines=10, interactive=False)
                        archive_name_input = gr.Textbox(label="Archive Name")
                        restore_btn = gr.Button("Restore", variant="primary")
                        restore_status = gr.Textbox(label="Status", lines=3, interactive=False)
                        
                        list_btn.click(fn=list_archives, outputs=[archives_list])
                        restore_btn.click(fn=restore_archive, inputs=[archive_name_input], outputs=[restore_status])
        
        gr.Markdown("---")
        gr.Markdown("CineSearch AI | Powered by Gemini 2.5 Flash & YOLO")
        
        app.load(fn=initialize_pipeline, outputs=[init_status])
    
    return app

if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY not set")
    
    app = build_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
