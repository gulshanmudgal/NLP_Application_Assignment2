import { Language } from './language';

// Translation request interface
export interface TranslationRequest {
  text: string;
  sourceLanguage: string;
  targetLanguage: string;
  enableCache?: boolean;
  model?: 'indictrans' | 'mt5' | 'auto';
}

// Translation result interface
export interface TranslationResult {
  translatedText: string;
  sourceLanguage: string;
  targetLanguage: string;
  confidence?: number;
  model: string;
  processingTime: number;
  fromCache: boolean;
  alternatives?: string[];
}

// API response wrapper
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

// Translation API response
export type TranslationResponse = ApiResponse<TranslationResult>;

// Languages API response
export type LanguagesResponse = ApiResponse<Language[]>;

// Error response interface
export interface ErrorResponse {
  error: string;
  details?: string;
  code?: string;
  timestamp: string;
}

// Translation history item
export interface TranslationHistoryItem {
  id: string;
  request: TranslationRequest;
  result: TranslationResult;
  timestamp: string;
}

// Validation result interface
export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

// Translation metrics interface
export interface TranslationMetrics {
  totalTranslations: number;
  averageProcessingTime: number;
  cacheHitRate: number;
  popularLanguagePairs: { source: string; target: string; count: number }[];
}
