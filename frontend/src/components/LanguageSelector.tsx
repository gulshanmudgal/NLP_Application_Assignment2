import React from 'react';
import styled from 'styled-components';
import { SUPPORTED_LANGUAGES, getLanguageByCode } from '../types/language';

interface LanguageSelectorProps {
  selectedLanguage: string;
  onLanguageChange: (languageCode: string) => void;
  label?: string;
  disabled?: boolean;
  className?: string;
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  selectedLanguage,
  onLanguageChange,
  label,
  disabled = false,
  className
}) => {
  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    onLanguageChange(event.target.value);
  };

  const selectedLang = getLanguageByCode(selectedLanguage);

  return (
    <Container className={className}>
      {label && <Label>{label}</Label>}
      <SelectWrapper>
        <Select
          value={selectedLanguage}
          onChange={handleChange}
          disabled={disabled}
        >
          {SUPPORTED_LANGUAGES.map((language) => (
            <option key={language.code} value={language.code}>
              {language.name} ({language.nativeName})
            </option>
          ))}
        </Select>
        <SelectIcon>
          <svg 
            width="12" 
            height="12" 
            viewBox="0 0 12 12" 
            fill="none" 
            xmlns="http://www.w3.org/2000/svg"
          >
            <path 
              d="M3 4.5L6 7.5L9 4.5" 
              stroke="currentColor" 
              strokeWidth="1.5" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            />
          </svg>
        </SelectIcon>
      </SelectWrapper>
      {selectedLang && (
        <LanguageInfo>
          <LanguageCode>{selectedLang.code.toUpperCase()}</LanguageCode>
          <ScriptType>{selectedLang.scriptType}</ScriptType>
        </LanguageInfo>
      )}
    </Container>
  );
};

// Styled Components
const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const Label = styled.label`
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
`;

const SelectWrapper = styled.div`
  position: relative;
  display: inline-block;
`;

const Select = styled.select`
  appearance: none;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 0.75rem 2.5rem 0.75rem 0.75rem;
  font-size: 0.875rem;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 180px;

  &:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  &:hover:not(:disabled) {
    border-color: #9ca3af;
  }

  &:disabled {
    background: #f9fafb;
    color: #9ca3af;
    cursor: not-allowed;
  }

  option {
    padding: 0.5rem;
    background: white;
    color: #374151;
  }
`;

const SelectIcon = styled.div`
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: #6b7280;
`;

const LanguageInfo = styled.div`
  display: flex;
  gap: 0.5rem;
  align-items: center;
`;

const LanguageCode = styled.span`
  font-size: 0.75rem;
  font-weight: 500;
  color: #3b82f6;
  background: #eff6ff;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
`;

const ScriptType = styled.span`
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: capitalize;
`;

export default LanguageSelector;
