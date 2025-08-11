"""
Languages API endpoints.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime

from app.models.language import (
    get_supported_languages,
    get_language_by_code
)
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get(
    "/",
    summary="Get supported languages",
    description="Get list of all supported languages with their metadata"
)
async def get_languages():
    """
    Get all supported languages.
    
    Returns detailed information about each supported language including:
    - Language code (ISO 639-1)
    - English and native names
    - Writing script and direction
    - Language family
    - Supported translation models
    """
    try:
        languages = get_supported_languages()
        
        language_list = []
        for lang in languages:
            language_info = {
                "code": lang.code,
                "name": lang.name,
                "native_name": lang.native_name,
                "script": lang.script_type,
                "direction": lang.direction,
                "family": "unknown",  # Not available in current model
                "region": "unknown",  # Not available in current model
                "supported_models": [],  # Not available in current model
                "is_rtl": lang.direction == "rtl"
            }
            language_list.append(language_info)
        
        return {
            "languages": language_list,
            "total": len(language_list),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving languages: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving supported languages"
        )


@router.get(
    "/{language_code}",
    summary="Get language details",
    description="Get detailed information about a specific language"
)
async def get_language_details(language_code: str):
    """
    Get details for a specific language by its code.
    
    - **language_code**: Two-letter language code (en, hi, ta, te, bn, mr)
    """
    try:
        language = get_language_by_code(language_code)
        if not language:
            raise HTTPException(
                status_code=404,
                detail=f"Language with code '{language_code}' not found"
            )
        
        return {
            "code": language.code,
            "name": language.name,
            "native_name": language.native_name,
            "script": language.script_type,
            "direction": language.direction,
            "family": "unknown",  # Not available in current model
            "region": "unknown",  # Not available in current model
            "supported_models": [],  # Not available in current model
            "is_rtl": language.direction == "rtl",
            "character_set": "unknown",  # Not available in current model
            "writing_system": "unknown",  # Not available in current model
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving language details for {language_code}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving language details"
        )


@router.get(
    "/pairs/supported",
    summary="Get supported language pairs",
    description="Get all supported source-target language pairs"
)
async def get_supported_pairs():
    """
    Get all supported language pairs for translation.
    
    Returns a list of all valid source-target language combinations
    along with the models that support each pair.
    """
    try:
        languages = get_supported_languages()
        language_codes = [lang.code for lang in languages]
        
        pairs = []
        for source in language_codes:
            for target in language_codes:
                if source != target:  # Can't translate to same language
                    source_lang = get_language_by_code(source)
                    target_lang = get_language_by_code(target)
                    
                    # For now, all language pairs are supported by mock translator
                    pairs.append({
                        "source": source,
                        "target": target,
                        "source_name": source_lang.name if source_lang else source,
                        "target_name": target_lang.name if target_lang else target,
                        "supported_models": ["mock"],  # Mock translator supports all pairs
                        "bidirectional": True  # All pairs are bidirectional
                    })
        
        return {
            "language_pairs": pairs,
            "total": len(pairs),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving language pairs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving supported language pairs"
        )


@router.get(
    "/detect/{text}",
    summary="Detect language of text",
    description="Auto-detect the language of provided text"
)
async def detect_language(text: str):
    """
    Detect the language of provided text.
    
    - **text**: Text to analyze for language detection
    
    Returns the most likely language code along with confidence scores
    for all detected languages.
    """
    if not text or len(text.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )
    
    if len(text) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Text too long for language detection (max 1000 characters)"
        )
    
    try:
        # Language detection service not implemented yet
        # Return a mock response for now
        return {
            "text": text[:100] + "..." if len(text) > 100 else text,
            "detected_language": "en",  # Default to English
            "confidence": 0.5,  # Low confidence since it's mocked
            "all_predictions": [{"language": "en", "confidence": 0.5}],
            "is_supported": True,
            "timestamp": datetime.utcnow()
        }
        raise HTTPException(
            status_code=503,
            detail="Language detection service temporarily unavailable"
        )
    except Exception as e:
        logger.error(f"Error in language detection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error detecting language"
        )
