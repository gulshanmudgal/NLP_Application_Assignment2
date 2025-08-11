#!/usr/bin/env python3
"""
Demo script to showcase the data models and validation
Run with: python demo_models.py
"""

from app.models import (
    TranslationRequest, 
    TranslationResult,
    TranslationResponse,
    get_supported_languages,
    get_language_by_code,
    is_language_pair_supported,
    SupportedLanguage,
    ModelType
)
from app.utils import (
    validate_text_content,
    validate_language_pair,
    sanitize_text,
    detect_script_type,
    has_mixed_scripts,
    estimate_translation_difficulty
)
from pydantic import ValidationError
import json
from datetime import datetime

def demo_language_models():
    """Demonstrate language model functionality"""
    print("=== Language Models Demo ===\n")
    
    # Show supported languages
    print("Supported Languages:")
    languages = get_supported_languages()
    for lang in languages:
        print(f"  {lang.code}: {lang.name} ({lang.native_name}) - {lang.script_type}")
    
    print("\nLanguage lookup examples:")
    hindi = get_language_by_code("hi")
    if hindi:
        print(f"Hindi: {hindi.name} - {hindi.native_name}")
    
    # Test language pair validation
    print(f"\nLanguage pair validation:")
    print(f"en -> hi: {is_language_pair_supported('en', 'hi')}")
    print(f"en -> en: {is_language_pair_supported('en', 'en')}")
    print(f"en -> xyz: {is_language_pair_supported('en', 'xyz')}")

def demo_translation_models():
    """Demonstrate translation model functionality"""
    print("\n=== Translation Models Demo ===\n")
    
    # Valid translation request
    try:
        request = TranslationRequest(
            text="Hello, how are you?",
            source_language=SupportedLanguage.ENGLISH,
            target_language=SupportedLanguage.HINDI,
            model=ModelType.INDICTRANS
        )
        print("✓ Valid translation request created:")
        print(f"  Text: {request.text}")
        print(f"  {request.source_language} -> {request.target_language}")
        print(f"  Model: {request.model}")
        
    except ValidationError as e:
        print(f"✗ Validation error: {e}")
    
    # Translation result
    result = TranslationResult(
        translated_text="नमस्ते, आप कैसे हैं?",
        source_language=SupportedLanguage.ENGLISH,
        target_language=SupportedLanguage.HINDI,
        confidence=0.95,
        model="indictrans",
        processing_time=0.245,
        from_cache=False,
        alternatives=["हैलो, आप कैसे हैं?"]
    )
    
    print(f"\n✓ Translation result:")
    print(f"  Original: Hello, how are you?")
    print(f"  Translated: {result.translated_text}")
    print(f"  Confidence: {result.confidence}")
    print(f"  Processing time: {result.processing_time}s")
    
    # API Response
    response = TranslationResponse(
        success=True,
        data=result,
        message="Translation completed successfully"
    )
    
    print(f"\n✓ API Response structure:")
    print(f"  Success: {response.success}")
    print(f"  Message: {response.message}")
    print(f"  Timestamp: {response.timestamp}")

def demo_validation_errors():
    """Demonstrate validation error handling"""
    print("\n=== Validation Error Demo ===\n")
    
    # Test various validation errors
    test_cases = [
        {
            "description": "Empty text",
            "request": {"text": "", "source_language": "en", "target_language": "hi"}
        },
        {
            "description": "Same source and target",
            "request": {"text": "Hello", "source_language": "en", "target_language": "en"}
        },
        {
            "description": "Text too long",
            "request": {"text": "a" * 1001, "source_language": "en", "target_language": "hi"}
        }
    ]
    
    for case in test_cases:
        try:
            TranslationRequest(**case["request"])
            print(f"✗ Expected validation error for: {case['description']}")
        except ValidationError as e:
            print(f"✓ Caught expected error for {case['description']}:")
            for error in e.errors():
                print(f"  - {error['msg']}")

def demo_validation_utils():
    """Demonstrate validation utility functions"""
    print("\n=== Validation Utils Demo ===\n")
    
    # Text validation
    texts = [
        "Hello world",
        "",
        "   ",
        "a" * 1001,
        "नमस्ते दुनिया",
        "Hello नमस्ते"
    ]
    
    print("Text validation:")
    for text in texts:
        result = validate_text_content(text)
        display_text = repr(text[:20] + "..." if len(text) > 20 else text)
        print(f"  {display_text}: {'✓' if result.is_valid else '✗'}")
        if not result.is_valid:
            for error in result.errors:
                print(f"    - {error}")
    
    # Language pair validation
    print("\nLanguage pair validation:")
    pairs = [("en", "hi"), ("en", "en"), ("en", "xyz"), ("", "hi")]
    for source, target in pairs:
        result = validate_language_pair(source, target)
        print(f"  {source} -> {target}: {'✓' if result.is_valid else '✗'}")
        if not result.is_valid:
            for error in result.errors:
                print(f"    - {error}")
    
    # Script detection
    print("\nScript detection:")
    test_texts = [
        "Hello world",
        "नमस्ते दुनिया", 
        "வணக்கம் உலகம்",
        "Hello नमस्ते",
        "123 !@#"
    ]
    
    for text in test_texts:
        script = detect_script_type(text)
        mixed = has_mixed_scripts(text)
        print(f"  '{text}': {script} script, mixed: {mixed}")
    
    # Translation difficulty estimation
    print("\nTranslation difficulty estimation:")
    difficulty_tests = [
        ("Hello", "en", "hi"),
        ("This is a very long sentence with many complex words and technical terminology", "en", "hi"),
        ("Hello नमस्ते", "en", "hi"),
        ("नमस्ते", "hi", "en")
    ]
    
    for text, source, target in difficulty_tests:
        difficulty = estimate_translation_difficulty(text, source, target)
        display_text = text[:30] + "..." if len(text) > 30 else text
        print(f"  '{display_text}' ({source}->{target}): {difficulty:.2f}")

def demo_json_serialization():
    """Demonstrate JSON serialization of models"""
    print("\n=== JSON Serialization Demo ===\n")
    
    # Create a translation request
    request = TranslationRequest(
        text="Hello world",
        source_language=SupportedLanguage.ENGLISH,
        target_language=SupportedLanguage.HINDI
    )
    
    # Serialize to JSON
    request_json = request.model_dump_json(indent=2)
    print("Translation Request JSON:")
    print(request_json)
    
    # Create a translation result
    result = TranslationResult(
        translated_text="नमस्ते संसार",
        source_language=SupportedLanguage.ENGLISH,
        target_language=SupportedLanguage.HINDI,
        model="indictrans",
        processing_time=0.5,
        from_cache=False
    )
    
    result_json = result.model_dump_json(indent=2)
    print(f"\nTranslation Result JSON:")
    print(result_json)

if __name__ == "__main__":
    print("🚀 NLP Translation Models Demo\n")
    
    try:
        demo_language_models()
        demo_translation_models()
        demo_validation_errors()
        demo_validation_utils()
        demo_json_serialization()
        
        print("\n✅ All demos completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        raise
