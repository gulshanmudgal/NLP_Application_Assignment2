"""
Translation API endpoints for the NLP Translation service.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from pydantic import BaseModel, Field
import time
import asyncio

from app.models.translation import (
    TranslationRequest,
    TranslationResponse,
    BatchTranslationRequest,
    BatchTranslationResponse,
    TranslationStats,
    ModelInfo
)
from app.services.translation_service import TranslationService, get_translation_service
from app.core.logging import get_translation_logger, get_logger

router = APIRouter()
translation_logger = get_translation_logger()
logger = get_logger("translation.api")


def get_cache_service(request: Request):
    """Dependency to get cache service from app state."""
    if hasattr(request.app.state, 'cache_service'):
        return request.app.state.cache_service
    return None


@router.post("/", response_model=TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    translation_service: TranslationService = Depends(get_translation_service),
    cache_service = Depends(get_cache_service),
    http_request: Request = None
):
    """
    Translate text from source language to target language.
    
    Args:
        request: Translation request containing text and language parameters
        translation_service: Translation service dependency
        cache_service: Cache service dependency
        http_request: HTTP request object for logging
    
    Returns:
        TranslationResponse: Contains translated text and metadata
    """
    start_time = time.time()
    
    # Log translation request
    translation_logger.log_translation_request(
        source_text=request.text,
        source_lang=request.source_language,
        target_lang=request.target_language,
        model=request.model or "auto"
    )
    
    try:
        # Check cache first
        cache_key = None
        if cache_service:
            cache_key = cache_service.generate_cache_key(
                text=request.text,
                source_lang=request.source_language,
                target_lang=request.target_language,
                model=request.model or "auto"
            )
            
            cached_result = await cache_service.get(cache_key)
            if cached_result:
                translation_logger.log_cache_hit(
                    cache_key=cache_key,
                    source_lang=request.source_language,
                    target_lang=request.target_language
                )
                
                # Add processing time to cached result
                cached_result["processing_time"] = time.time() - start_time
                return TranslationResponse(**cached_result)
            else:
                translation_logger.log_cache_miss(
                    cache_key=cache_key,
                    source_lang=request.source_language,
                    target_lang=request.target_language
                )
        
        # Perform translation
        result = await translation_service.translate(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
            model=request.model
        )
        
        processing_time = time.time() - start_time
        
        # Prepare response
        response = TranslationResponse(
            translated_text=result.translated_text,
            source_language=request.source_language,
            target_language=request.target_language,
            confidence_score=result.confidence,
            model_used=result.model_used,
            processing_time=processing_time,
            cached=False,
            detected_language=result.detected_language
        )
        
        # Cache the result
        if cache_service and cache_key:
            await cache_service.set(cache_key, response.dict())
        
        # Log successful translation
        translation_logger.log_translation_response(
            source_text=request.text,
            translated_text=result.translated_text,
            source_lang=request.source_language,
            target_lang=request.target_language,
            model=result.model_used,
            confidence=result.confidence,
            processing_time=processing_time
        )
        
        return response
        
    except Exception as e:
        # Log translation error
        translation_logger.log_translation_error(
            source_text=request.text,
            source_lang=request.source_language,
            target_lang=request.target_language,
            model=request.model or "auto",
            error=str(e)
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )


@router.post(
    "/batch",
    response_model=List[TranslationResponse],
    summary="Batch translate multiple texts",
    description="Translate multiple texts in a single request for better efficiency"
)
async def batch_translate(
    requests: List[TranslationRequest],
    background_tasks: BackgroundTasks
) -> List[TranslationResponse]:
    """
    Batch translate multiple texts.
    
    Processes up to 10 translation requests in parallel for better efficiency.
    Each request follows the same format as the single translation endpoint.
    """
    if len(requests) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 translation requests allowed per batch"
        )
    
    if not requests:
        raise HTTPException(
            status_code=400,
            detail="At least one translation request is required"
        )
    
    try:
        logger.info("Batch translation request", batch_size=len(requests))
        
        # Process translations concurrently
        tasks = []
        for request in requests:
            task = translate_text(request, background_tasks)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions in the batch
        responses = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch item {i} failed", error=str(result))
                # Return error response for failed items
                error_response = TranslationResponse(
                    translated_text="",
                    confidence=0.0,
                    model_used="error",
                    processing_time_ms=0,
                    alternatives=[],
                    cached=False
                )
                responses.append(error_response)
            else:
                responses.append(result)
        
        logger.info("Batch translation completed", batch_size=len(responses))
        return responses
        
    except Exception as e:
        logger.error("Batch translation error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during batch translation"
        )


@router.get("/models", response_model=List[ModelInfo])
async def get_available_models(
    translation_service: TranslationService = Depends(get_translation_service)
):
    """
    Get information about available translation models.
    
    Returns:
        List[ModelInfo]: List of available models with their capabilities
    """
    try:
        models = await translation_service.get_available_models()
        return [
            ModelInfo(
                name=model["name"],
                source_languages=model["source_languages"],
                target_languages=model["target_languages"],
                description=model["description"],
                timestamp=datetime.utcnow()
            )
            for model in models
        ]
    except Exception as e:
        logger.error("Error retrieving models", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve models: {str(e)}"
        )


@router.get(
    "/stats",
    summary="Get translation statistics",
    description="Get usage statistics for the translation service"
)
async def get_translation_stats(
    translation_service: TranslationService = Depends(get_translation_service),
    cache_service = Depends(get_cache_service)
):
    """
    Get translation service statistics.
    
    Returns metrics including:
    - Total translations processed
    - Cache hit/miss ratios
    - Average processing times
    - Usage by language and model
    """
    try:
        stats = await translation_service.get_stats()
        cache_stats = {}
        if cache_service:
            cache_stats = await cache_service.get_stats()
        
        return {
            "translation_stats": stats,
            "cache_stats": cache_stats,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error("Error retrieving stats", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Error retrieving statistics"
        )
