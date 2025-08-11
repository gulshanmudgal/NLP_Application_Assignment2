"""
Model loader and manager for ML translation models.
"""
import os
import asyncio
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Union, Type
import logging
from urllib.parse import urlparse

import httpx
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from .base_model import BaseMLModel

logger = logging.getLogger(__name__)


class ModelLoader:
    """Manages loading and caching of ML models."""
    
    def __init__(self, cache_dir: str = "./model_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.loaded_models: Dict[str, BaseMLModel] = {}
        self.model_configs = {
            "indictrans": {
                "model_name": "ai4bharat/indictrans2-en-indic-1B",
                "supported_languages": ["en", "hi", "ta", "te", "bn", "mr"],
                "size_estimate_mb": 2048
            },
            "m2m100": {
                "model_name": "facebook/m2m100_418M", 
                "supported_languages": ["en", "hi", "ta", "te", "bn", "mr"],
                "size_estimate_mb": 1600
            },
            "mbart": {
                "model_name": "facebook/mbart-large-50-many-to-many-mmt",
                "supported_languages": ["en", "hi", "ta", "te", "bn", "mr"],
                "size_estimate_mb": 2400
            }
        }
    
    async def load_model(
        self, 
        model_type: str, 
        model_class: Type[BaseMLModel],
        force_reload: bool = False
    ) -> Optional[BaseMLModel]:
        """
        Load a model of the specified type.
        
        Args:
            model_type: Type of model (indictrans, m2m100, mbart)
            model_class: Class to instantiate for the model
            force_reload: Whether to force reload if already loaded
            
        Returns:
            Loaded model instance or None if failed
        """
        if model_type in self.loaded_models and not force_reload:
            return self.loaded_models[model_type]
        
        if model_type not in self.model_configs:
            logger.error(f"Unknown model type: {model_type}")
            return None
        
        config = self.model_configs[model_type]
        model_path = await self._ensure_model_cached(
            model_type, 
            config["model_name"]
        )
        
        if not model_path:
            logger.error(f"Failed to cache model {model_type}")
            return None
        
        try:
            # Create model instance
            model = model_class(
                model_name=config["model_name"],
                model_path=str(model_path)
            )
            
            # Set supported languages
            model.supported_languages = set(config["supported_languages"])
            model.model_size_mb = config["size_estimate_mb"]
            
            # Load the model
            success = await model.load_model()
            if success:
                self.loaded_models[model_type] = model
                logger.info(f"Successfully loaded model {model_type}")
                return model
            else:
                logger.error(f"Failed to load model {model_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating model {model_type}: {e}")
            return None
    
    async def _ensure_model_cached(
        self, 
        model_type: str, 
        model_name: str
    ) -> Optional[Path]:
        """
        Ensure model is cached locally.
        
        Args:
            model_type: Type of model
            model_name: HuggingFace model name
            
        Returns:
            Path to cached model or None if failed
        """
        model_cache_dir = self.cache_dir / model_type
        model_cache_dir.mkdir(exist_ok=True)
        
        # Check if model is already cached
        if self._is_model_cached(model_cache_dir):
            logger.info(f"Model {model_type} found in cache")
            return model_cache_dir
        
        # Download model from HuggingFace
        logger.info(f"Downloading model {model_name} to cache...")
        try:
            # Use transformers to download and cache model
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=str(model_cache_dir)
            )
            model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                cache_dir=str(model_cache_dir),
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            
            # Save to our cache structure
            tokenizer.save_pretrained(str(model_cache_dir))
            model.save_pretrained(str(model_cache_dir))
            
            logger.info(f"Model {model_type} downloaded and cached successfully")
            return model_cache_dir
            
        except Exception as e:
            logger.error(f"Failed to download model {model_type}: {e}")
            return None
    
    def _is_model_cached(self, model_dir: Path) -> bool:
        """Check if model is properly cached."""
        required_files = ["config.json", "tokenizer.json"]
        return all((model_dir / file).exists() for file in required_files)
    
    async def get_model(self, model_type: str) -> Optional[BaseMLModel]:
        """Get a loaded model by type."""
        return self.loaded_models.get(model_type)
    
    async def unload_model(self, model_type: str) -> bool:
        """Unload a model to free memory."""
        if model_type in self.loaded_models:
            model = self.loaded_models[model_type]
            await model.unload_model()
            del self.loaded_models[model_type]
            logger.info(f"Unloaded model {model_type}")
            return True
        return False
    
    async def unload_all_models(self):
        """Unload all models."""
        for model_type in list(self.loaded_models.keys()):
            await self.unload_model(model_type)
    
    def get_cache_stats(self) -> Dict[str, any]:
        """Get cache statistics."""
        stats = {
            "cache_dir": str(self.cache_dir),
            "loaded_models": list(self.loaded_models.keys()),
            "cache_size_mb": self._get_cache_size_mb(),
            "available_models": list(self.model_configs.keys())
        }
        return stats
    
    def _get_cache_size_mb(self) -> float:
        """Calculate total cache size in MB."""
        total_size = 0
        for root, dirs, files in os.walk(self.cache_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                except OSError:
                    pass
        return total_size / (1024 * 1024)  # Convert to MB
