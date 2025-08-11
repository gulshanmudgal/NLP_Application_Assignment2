import React, { useState, useCallback } from 'react';
import styled from 'styled-components';
import { TranslationRequest, TranslationResult, ValidationResult } from '../types';
import { validateTranslationRequest, sanitizeTextInput, MAX_TEXT_LENGTH } from '../utils';
import LanguageSelector from './LanguageSelector';
import LoadingIndicator from './LoadingIndicator';
// import LanguageSelector from './LanguageSelector';
// import LoadingIndicator from './LoadingIndicator';

interface TranslationInterfaceProps {
  onTranslate: (request: TranslationRequest) => Promise<TranslationResult>;
  isLoading?: boolean;
  className?: string;
}

const TranslationInterface: React.FC<TranslationInterfaceProps> = ({
  onTranslate,
  isLoading = false,
  className
}) => {
  const [inputText, setInputText] = useState('');
  const [sourceLanguage, setSourceLanguage] = useState('en');
  const [targetLanguage, setTargetLanguage] = useState('hi');
  const [translationResult, setTranslationResult] = useState<TranslationResult | null>(null);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [isTranslating, setIsTranslating] = useState(false);

  const handleTextChange = useCallback((event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = event.target.value;
    const sanitizedText = sanitizeTextInput(text);
    setInputText(sanitizedText);
    
    // Clear previous validation errors when user types
    if (validationErrors.length > 0) {
      setValidationErrors([]);
    }
  }, [validationErrors.length]);

  const handleSourceLanguageChange = useCallback((languageCode: string) => {
    setSourceLanguage(languageCode);
    // Swap languages if source becomes same as target
    if (languageCode === targetLanguage) {
      setTargetLanguage(sourceLanguage);
    }
  }, [sourceLanguage, targetLanguage]);

  const handleTargetLanguageChange = useCallback((languageCode: string) => {
    setTargetLanguage(languageCode);
    // Swap languages if target becomes same as source
    if (languageCode === sourceLanguage) {
      setSourceLanguage(targetLanguage);
    }
  }, [sourceLanguage, targetLanguage]);

  const handleSwapLanguages = useCallback(() => {
    setSourceLanguage(targetLanguage);
    setTargetLanguage(sourceLanguage);
  }, [sourceLanguage, targetLanguage]);

  const handleTranslate = useCallback(async () => {
    // Create translation request
    const request: TranslationRequest = {
      text: inputText || '',
      sourceLanguage: sourceLanguage,
      targetLanguage: targetLanguage,
      enableCache: true,
      model: 'auto'
    };

    // Validate request
    const validation: ValidationResult = validateTranslationRequest(request);
    
    if (!validation.isValid) {
      setValidationErrors(validation.errors);
      return;
    }

    setIsTranslating(true);
    setValidationErrors([]);

    try {
      const result = await onTranslate(request);
      setTranslationResult(result);
    } catch (error) {
      setValidationErrors([error instanceof Error ? error.message : 'Translation failed']);
    } finally {
      setIsTranslating(false);
    }
  }, [inputText, sourceLanguage, targetLanguage, onTranslate]);

  const handleClearText = useCallback(() => {
    setInputText('');
    setTranslationResult(null);
    setValidationErrors([]);
  }, []);

  const canTranslate = (inputText || '').trim().length > 0 && !isTranslating && !isLoading;
  const remainingChars = MAX_TEXT_LENGTH - (inputText || '').length;

  return (
    <Container className={className}>
      <Title>Multi-Language Translation</Title>
      
      <TranslationPanel>
        {/* Input Section */}
        <InputSection>
          <SectionHeader>
            <LanguageSelector
              selectedLanguage={sourceLanguage}
              onLanguageChange={handleSourceLanguageChange}
              label="From"
            />
            <SwapButton 
              onClick={handleSwapLanguages}
              disabled={isTranslating || isLoading}
              title="Swap languages"
            >
              ⇄
            </SwapButton>
            <LanguageSelector
              selectedLanguage={targetLanguage}
              onLanguageChange={handleTargetLanguageChange}
              label="To"
            />
          </SectionHeader>
          
          <InputTextArea
            value={inputText || ''}
            onChange={handleTextChange}
            placeholder="Enter text to translate..."
            disabled={isTranslating || isLoading}
            maxLength={MAX_TEXT_LENGTH}
          />
          
          <InputFooter>
            <CharacterCount isNearLimit={remainingChars < 100}>
              {remainingChars} characters remaining
            </CharacterCount>
            <ButtonGroup>
              <ClearButton 
                onClick={handleClearText}
                disabled={!(inputText || '') || isTranslating || isLoading}
              >
                Clear
              </ClearButton>
              <TranslateButton 
                onClick={handleTranslate}
                disabled={!canTranslate}
              >
                {isTranslating ? <LoadingIndicator size="small" /> : 'Translate'}
              </TranslateButton>
            </ButtonGroup>
          </InputFooter>
        </InputSection>

        {/* Output Section */}
        <OutputSection>
          <SectionHeader>
            <SectionTitle>Translation Result</SectionTitle>
          </SectionHeader>
          
          <OutputArea>
            {isTranslating || isLoading ? (
              <LoadingContainer>
                <LoadingIndicator />
                <LoadingText>Translating...</LoadingText>
              </LoadingContainer>
            ) : translationResult ? (
              <TranslationOutput>
                <TranslatedText>{translationResult.translatedText}</TranslatedText>
                <TranslationMeta>
                  <MetaItem>
                    Model: {translationResult.model}
                  </MetaItem>
                  <MetaItem>
                    Time: {translationResult.processingTime.toFixed(2)}s
                  </MetaItem>
                  {translationResult.confidence && (
                    <MetaItem>
                      Confidence: {(translationResult.confidence * 100).toFixed(1)}%
                    </MetaItem>
                  )}
                  {translationResult.fromCache && (
                    <MetaItem>
                      <CacheIndicator>Cached</CacheIndicator>
                    </MetaItem>
                  )}
                </TranslationMeta>
                
                {translationResult.alternatives && translationResult.alternatives.length > 0 && (
                  <AlternativesSection>
                    <AlternativesTitle>Alternative translations:</AlternativesTitle>
                    <AlternativesList>
                      {translationResult.alternatives.map((alt, index) => (
                        <AlternativeItem key={index}>{alt}</AlternativeItem>
                      ))}
                    </AlternativesList>
                  </AlternativesSection>
                )}
              </TranslationOutput>
            ) : (
              <PlaceholderText>
                Your translation will appear here
              </PlaceholderText>
            )}
          </OutputArea>
        </OutputSection>
      </TranslationPanel>

      {/* Error Display */}
      {validationErrors.length > 0 && (
        <ErrorContainer>
          <ErrorTitle>Please fix the following issues:</ErrorTitle>
          <ErrorList>
            {validationErrors.map((error, index) => (
              <ErrorItem key={index}>{error}</ErrorItem>
            ))}
          </ErrorList>
        </ErrorContainer>
      )}
    </Container>
  );
};

// Styled Components
const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
`;

const Title = styled.h1`
  text-align: center;
  color: #333;
  margin-bottom: 2rem;
  font-size: 2.5rem;
  font-weight: 600;
`;

const TranslationPanel = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  padding: 2rem;
  border: 1px solid #e5e7eb;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    padding: 1rem;
  }
`;

const InputSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const OutputSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const SectionHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #f3f4f6;
`;

const SectionTitle = styled.h3`
  margin: 0;
  color: #374151;
  font-size: 1.1rem;
  font-weight: 500;
`;

const SwapButton = styled.button`
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 0.5rem;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.2s;

  &:hover:not(:disabled) {
    background: #e5e7eb;
    transform: scale(1.05);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const InputTextArea = styled.textarea`
  width: 100%;
  min-height: 200px;
  padding: 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  line-height: 1.5;
  resize: vertical;
  font-family: inherit;

  &:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  &:disabled {
    background: #f9fafb;
    cursor: not-allowed;
  }
`;

const InputFooter = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const CharacterCount = styled.span.withConfig({
  shouldForwardProp: (prop) => prop !== 'isNearLimit'
})<{ isNearLimit: boolean }>`
  font-size: 0.875rem;
  color: ${props => props.isNearLimit ? '#ef4444' : '#6b7280'};
  font-weight: ${props => props.isNearLimit ? '500' : '400'};
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 0.5rem;
`;

const ClearButton = styled.button`
  padding: 0.75rem 1.5rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;

  &:hover:not(:disabled) {
    background: #f9fafb;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const TranslateButton = styled.button`
  padding: 0.75rem 1.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  &:hover:not(:disabled) {
    background: #2563eb;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const OutputArea = styled.div`
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
`;

const LoadingText = styled.p`
  color: #6b7280;
  margin: 0;
`;

const TranslationOutput = styled.div`
  width: 100%;
`;

const TranslatedText = styled.div`
  padding: 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 1rem;
  white-space: pre-wrap;
`;

const TranslationMeta = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
`;

const MetaItem = styled.span`
  font-size: 0.875rem;
  color: #6b7280;
`;

const CacheIndicator = styled.span`
  background: #10b981;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
`;

const AlternativesSection = styled.div`
  margin-top: 1rem;
`;

const AlternativesTitle = styled.h4`
  margin: 0 0 0.5rem 0;
  color: #374151;
  font-size: 0.875rem;
  font-weight: 500;
`;

const AlternativesList = styled.ul`
  margin: 0;
  padding-left: 1rem;
`;

const AlternativeItem = styled.li`
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
`;

const PlaceholderText = styled.div`
  color: #9ca3af;
  font-style: italic;
  text-align: center;
`;

const ErrorContainer = styled.div`
  margin-top: 1rem;
  padding: 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
`;

const ErrorTitle = styled.h4`
  margin: 0 0 0.5rem 0;
  color: #dc2626;
  font-size: 0.875rem;
  font-weight: 500;
`;

const ErrorList = styled.ul`
  margin: 0;
  padding-left: 1rem;
`;

const ErrorItem = styled.li`
  color: #dc2626;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
`;

export default TranslationInterface;
