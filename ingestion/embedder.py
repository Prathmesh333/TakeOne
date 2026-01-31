"""
Embedder - Generates CLIP embeddings for frames and text
"""
import torch
import numpy as np
from PIL import Image
from typing import List, Union
from transformers import CLIPProcessor, CLIPModel


class CLIPEmbedder:
    """CLIP-based embedding generator for images and text."""
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        """
        Initialize CLIP model.
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading CLIP model on {self.device}...")
        
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model.eval()
        
        print("CLIP model loaded successfully!")
    
    def embed_image(self, image: Image.Image) -> np.ndarray:
        """
        Generate embedding for a single image.
        
        Args:
            image: PIL Image
            
        Returns:
            Normalized embedding as numpy array
        """
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            embedding = self.model.get_image_features(**inputs)
        
        # Normalize embedding
        embedding = embedding / embedding.norm(dim=-1, keepdim=True)
        return embedding.cpu().numpy().flatten()
    
    def embed_images(self, images: List[Image.Image], batch_size: int = 8) -> np.ndarray:
        """
        Generate embeddings for multiple images.
        
        Args:
            images: List of PIL Images
            batch_size: Batch size for processing
            
        Returns:
            Array of embeddings, shape (n_images, embedding_dim)
        """
        all_embeddings = []
        
        for i in range(0, len(images), batch_size):
            batch = images[i:i + batch_size]
            inputs = self.processor(images=batch, return_tensors="pt", padding=True).to(self.device)
            
            with torch.no_grad():
                embeddings = self.model.get_image_features(**inputs)
            
            embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)
            all_embeddings.append(embeddings.cpu().numpy())
        
        return np.vstack(all_embeddings)
    
    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embedding for text query.
        
        Args:
            text: Single string or list of strings
            
        Returns:
            Normalized embedding(s) as numpy array
        """
        if isinstance(text, str):
            text = [text]
        
        inputs = self.processor(text=text, return_tensors="pt", padding=True).to(self.device)
        
        with torch.no_grad():
            embeddings = self.model.get_text_features(**inputs)
        
        embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)
        result = embeddings.cpu().numpy()
        
        return result.flatten() if len(text) == 1 else result
    
    def compute_similarity(self, image_embedding: np.ndarray, text_embedding: np.ndarray) -> float:
        """Compute cosine similarity between image and text embeddings."""
        return float(np.dot(image_embedding, text_embedding))


# Global instance for convenience
_embedder = None


def get_embedder() -> CLIPEmbedder:
    """Get or create global embedder instance."""
    global _embedder
    if _embedder is None:
        _embedder = CLIPEmbedder()
    return _embedder
