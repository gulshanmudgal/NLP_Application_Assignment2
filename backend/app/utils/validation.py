import re
from typing import List, Tuple
from app.models.language import SupportedLanguage, get_language_by_code
from app.models.translation import ValidationResult

def validate_text_content(text: str, max_length: int = 1000) -> ValidationResult:
    """
    Validate text content for translation
    
    Args:
        text: Text to validate
        max_length: Maximum allowed length
        
    Returns:
        ValidationResult with validation status and errors
    """
    errors = []
    
    if not text:
        errors.append("Text is required")
        return ValidationResult(is_valid=False, errors=errors)
    
    trimmed_text = text.strip()
    
    if not trimmed_text:
        errors.append("Text cannot be empty or whitespace only")
    elif len(trimmed_text) > max_length:
        errors.append(f"Text cannot exceed {max_length} characters")
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)

def validate_language_pair(source: str, target: str) -> ValidationResult:
    """
    Validate language pair for translation
    
    Args:
        source: Source language code
        target: Target language code
        
    Returns:
        ValidationResult with validation status and errors
    """
    errors = []
    
    if not source:
        errors.append("Source language is required")
    
    if not target:
        errors.append("Target language is required")
    
    if source and target:
        if source == target:
            errors.append("Source and target languages must be different")
        else:
            # Check if languages are supported
            source_lang = get_language_by_code(source)
            target_lang = get_language_by_code(target)
            
            if not source_lang:
                errors.append(f"Source language '{source}' is not supported")
            
            if not target_lang:
                errors.append(f"Target language '{target}' is not supported")
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)

def sanitize_text(text: str) -> str:
    """
    Sanitize text input by normalizing whitespace and trimming
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Normalize whitespace
    sanitized = re.sub(r'\s+', ' ', text.strip())
    
    # Remove control characters except newlines and tabs
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', sanitized)
    
    return sanitized

def detect_script_type(text: str) -> str:
    """
    Detect the primary script type in text
    
    Args:
        text: Text to analyze
        
    Returns:
        Primary script type
    """
    if not text:
        return "latin"
    
    # Script detection patterns
    patterns = {
        "latin": r'[a-zA-Z]',
        "devanagari": r'[\u0900-\u097F]',
        "tamil": r'[\u0B80-\u0BFF]',
        "telugu": r'[\u0C00-\u0C7F]',
        "bengali": r'[\u0980-\u09FF]'
    }
    
    script_counts = {}
    for script, pattern in patterns.items():
        matches = re.findall(pattern, text)
        script_counts[script] = len(matches)
    
    # Return script with highest count
    primary_script = max(script_counts, key=script_counts.get)
    return primary_script if script_counts[primary_script] > 0 else "latin"

def has_mixed_scripts(text: str) -> bool:
    """
    Check if text contains mixed scripts
    
    Args:
        text: Text to analyze
        
    Returns:
        True if text contains multiple scripts
    """
    if not text:
        return False
    
    patterns = {
        "latin": r'[a-zA-Z]',
        "devanagari": r'[\u0900-\u097F]',
        "tamil": r'[\u0B80-\u0BFF]',
        "telugu": r'[\u0C00-\u0C7F]',
        "bengali": r'[\u0980-\u09FF]'
    }
    
    script_found = []
    for script, pattern in patterns.items():
        if re.search(pattern, text):
            script_found.append(script)
    
    return len(script_found) > 1

def estimate_translation_difficulty(text: str, source_lang: str, target_lang: str) -> float:
    """
    Estimate translation difficulty based on text characteristics
    
    Args:
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code
        
    Returns:
        Difficulty score between 0.0 (easy) and 1.0 (difficult)
    """
    difficulty = 0.0
    
    # Base difficulty for script differences
    source_config = get_language_by_code(source_lang)
    target_config = get_language_by_code(target_lang)
    
    if source_config and target_config:
        if source_config.script_type != target_config.script_type:
            difficulty += 0.3
    
    # Difficulty based on text characteristics
    if len(text) > 500:
        difficulty += 0.2
    
    if has_mixed_scripts(text):
        difficulty += 0.3
    
    # Special characters and numbers
    special_chars = len(re.findall(r'[^\w\s]', text))
    if special_chars > len(text) * 0.1:
        difficulty += 0.2
    
    return min(difficulty, 1.0)

def get_supported_language_pairs() -> List[Tuple[str, str]]:
    """
    Get all supported language pairs
    
    Returns:
        List of (source, target) language code tuples
    """
    languages = list(SupportedLanguage)
    pairs = []
    
    for source in languages:
        for target in languages:
            if source != target:
                pairs.append((source.value, target.value))
    
    return pairs

def is_transliteration_candidate(text: str, source_lang: str) -> bool:
    """
    Check if text might need transliteration
    
    Args:
        text: Text to check
        source_lang: Source language code
        
    Returns:
        True if transliteration might be needed
    """
    if not text or not source_lang:
        return False
    
    # Check for Latin script in non-Latin source languages
    if source_lang in ['hi', 'ta', 'te', 'bn', 'mr']:
        latin_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(re.findall(r'[a-zA-Z\u0900-\u097F\u0B80-\u0BFF\u0C00-\u0C7F\u0980-\u09FF]', text))
        
        if total_chars > 0 and latin_chars / total_chars > 0.5:
            return True
    
    return False
