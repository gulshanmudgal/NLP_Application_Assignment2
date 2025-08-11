import { TranslationRequest, ValidationResult, isLanguagePairSupported } from '../types';

/**
 * Maximum allowed text length for translation
 */
export const MAX_TEXT_LENGTH = 1000;

/**
 * Validate translation request data
 */
export const validateTranslationRequest = (request: Partial<TranslationRequest>): ValidationResult => {
  const errors: string[] = [];

  // Validate text
  if (!request.text) {
    errors.push('Text is required');
  } else {
    const trimmedText = request.text.trim();
    if (trimmedText.length === 0) {
      errors.push('Text cannot be empty or whitespace only');
    } else if (trimmedText.length > MAX_TEXT_LENGTH) {
      errors.push(`Text cannot exceed ${MAX_TEXT_LENGTH} characters`);
    }
  }

  // Validate source language
  if (!request.sourceLanguage) {
    errors.push('Source language is required');
  }

  // Validate target language
  if (!request.targetLanguage) {
    errors.push('Target language is required');
  }

  // Validate language pair
  if (request.sourceLanguage && request.targetLanguage) {
    if (request.sourceLanguage === request.targetLanguage) {
      errors.push('Source and target languages must be different');
    } else if (!isLanguagePairSupported(request.sourceLanguage, request.targetLanguage)) {
      errors.push('Selected language pair is not supported');
    }
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Validate text input
 */
export const validateTextInput = (text: string): ValidationResult => {
  const errors: string[] = [];

  if (!text) {
    errors.push('Text is required');
    return { isValid: false, errors };
  }

  const trimmedText = text.trim();
  
  if (trimmedText.length === 0) {
    errors.push('Text cannot be empty or whitespace only');
  } else if (trimmedText.length > MAX_TEXT_LENGTH) {
    errors.push(`Text cannot exceed ${MAX_TEXT_LENGTH} characters`);
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Sanitize text input by normalizing whitespace while preserving normal spaces
 */
export const sanitizeTextInput = (text: string): string => {
  if (!text) return '';
  
  return text
    .replace(/[\t\r\n]/g, ' ') // Replace tabs, carriage returns, and newlines with spaces
    .replace(/\s{3,}/g, ' ') // Replace 3 or more consecutive spaces with single space
    .slice(0, MAX_TEXT_LENGTH); // Ensure max length
};

/**
 * Check if text contains mixed scripts (useful for Indian languages)
 */
export const hasMixedScripts = (text: string): boolean => {
  const latinRegex = /[a-zA-Z]/;
  const devanagariRegex = /[\u0900-\u097F]/;
  const tamilRegex = /[\u0B80-\u0BFF]/;
  const teluguRegex = /[\u0C00-\u0C7F]/;
  const bengaliRegex = /[\u0980-\u09FF]/;

  const scripts = [
    latinRegex.test(text),
    devanagariRegex.test(text),
    tamilRegex.test(text),
    teluguRegex.test(text),
    bengaliRegex.test(text)
  ];

  return scripts.filter(Boolean).length > 1;
};

/**
 * Detect primary script in text
 */
export const detectPrimaryScript = (text: string): string => {
  const latinCount = (text.match(/[a-zA-Z]/g) || []).length;
  const devanagariCount = (text.match(/[\u0900-\u097F]/g) || []).length;
  const tamilCount = (text.match(/[\u0B80-\u0BFF]/g) || []).length;
  const teluguCount = (text.match(/[\u0C00-\u0C7F]/g) || []).length;
  const bengaliCount = (text.match(/[\u0980-\u09FF]/g) || []).length;

  const scriptCounts = [
    { script: 'latin', count: latinCount },
    { script: 'devanagari', count: devanagariCount },
    { script: 'tamil', count: tamilCount },
    { script: 'telugu', count: teluguCount },
    { script: 'bengali', count: bengaliCount }
  ];

  const primaryScript = scriptCounts.reduce((max, current) => 
    current.count > max.count ? current : max
  );

  return primaryScript.script;
};
