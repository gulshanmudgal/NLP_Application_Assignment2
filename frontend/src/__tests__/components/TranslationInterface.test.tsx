import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TranslationInterface from '../../components/TranslationInterface';
import { TranslationResult } from '../../types';

// Mock the utility functions
jest.mock('../../utils/validation', () => ({
  validateTranslationRequest: jest.fn(),
  sanitizeTextInput: jest.fn((text) => text),
  MAX_TEXT_LENGTH: 1000
}));

const mockValidateTranslationRequest = require('../../utils/validation').validateTranslationRequest;

describe('TranslationInterface', () => {
  const mockOnTranslate = jest.fn();

  const mockTranslationResult: TranslationResult = {
    translatedText: 'नमस्ते संसार',
    sourceLanguage: 'en',
    targetLanguage: 'hi',
    confidence: 0.95,
    model: 'indictrans',
    processingTime: 0.5,
    fromCache: false,
    alternatives: ['हैलो वर्ल्ड']
  };

  beforeEach(() => {
    mockOnTranslate.mockClear();
    mockValidateTranslationRequest.mockClear();
  });

  test('renders translation interface with all components', () => {
    render(<TranslationInterface onTranslate={mockOnTranslate} />);

    expect(screen.getByText('Multi-Language Translation')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter text to translate...')).toBeInTheDocument();
    expect(screen.getByText('From')).toBeInTheDocument();
    expect(screen.getByText('To')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /translate/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /clear/i })).toBeInTheDocument();
    expect(screen.getByText('Your translation will appear here')).toBeInTheDocument();
  });

  test('handles text input correctly', async () => {
    const user = userEvent.setup();
    render(<TranslationInterface onTranslate={mockOnTranslate} />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    
    await user.type(textArea, 'Hello world');
    
    expect(textArea).toHaveValue('Hello world');
  });

  test('displays character count correctly', async () => {
    const user = userEvent.setup();
    render(<TranslationInterface onTranslate={mockOnTranslate} />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    
    await user.type(textArea, 'Hello');
    
    expect(screen.getByText('995 characters remaining')).toBeInTheDocument();
  });

  test('shows warning when character limit is near', async () => {
    const user = userEvent.setup();
    render(<TranslationInterface onTranslate={mockOnTranslate} />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    const longText = 'a'.repeat(950);
    
    await user.type(textArea, longText);
    
    const characterCount = screen.getByText('50 characters remaining');
    expect(characterCount).toBeInTheDocument();
  });

  test('handles language selection', async () => {
    const user = userEvent.setup();
    render(<TranslationInterface onTranslate={mockOnTranslate} />);

    const sourceSelector = screen.getAllByRole('combobox')[0];
    const targetSelector = screen.getAllByRole('combobox')[1];

    await user.selectOptions(sourceSelector, 'hi');
    await user.selectOptions(targetSelector, 'ta');

    expect(sourceSelector).toHaveValue('hi');
    expect(targetSelector).toHaveValue('ta');
  });

  test('swaps languages when swap button is clicked', async () => {
    const user = userEvent.setup();
    render(<TranslationInterface onTranslate={mockOnTranslate} />);

    const sourceSelector = screen.getAllByRole('combobox')[0];
    const targetSelector = screen.getAllByRole('combobox')[1];
    const swapButton = screen.getByTitle('Swap languages');

    // Initial state: en -> hi
    expect(sourceSelector).toHaveValue('en');
    expect(targetSelector).toHaveValue('hi');

    await user.click(swapButton);

    // After swap: hi -> en
    expect(sourceSelector).toHaveValue('hi');
    expect(targetSelector).toHaveValue('en');
  });

  test('prevents same source and target language selection', async () => {
    const user = userEvent.setup();
    render(<TranslationInterface onTranslate={mockOnTranslate} />);

    const sourceSelector = screen.getAllByRole('combobox')[0];
    const targetSelector = screen.getAllByRole('combobox')[1];

    // Set source to Hindi
    await user.selectOptions(sourceSelector, 'hi');
    expect(sourceSelector).toHaveValue('hi');
    expect(targetSelector).toHaveValue('en'); // Should auto-swap to prevent same language

    // Set target to Hindi (same as source)
    await user.selectOptions(targetSelector, 'hi');
    expect(targetSelector).toHaveValue('hi');
    expect(sourceSelector).toHaveValue('en'); // Should auto-swap to prevent same language
  });

  test('clears text when clear button is clicked', async () => {
    const user = userEvent.setup();
    render(<TranslationInterface onTranslate={mockOnTranslate} />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    const clearButton = screen.getByRole('button', { name: /clear/i });

    await user.type(textArea, 'Hello world');
    expect(textArea).toHaveValue('Hello world');

    await user.click(clearButton);
    expect(textArea).toHaveValue('');
  });

  test('disables translate button when text is empty', () => {
    render(<TranslationInterface onTranslate={mockOnTranslate} />);

    const translateButton = screen.getByRole('button', { name: /translate/i });
    expect(translateButton).toBeDisabled();
  });

  test('enables translate button when text is entered', async () => {
    const user = userEvent.setup();
    render(<TranslationInterface onTranslate={mockOnTranslate} />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    const translateButton = screen.getByRole('button', { name: /translate/i });

    await user.type(textArea, 'Hello');
    expect(translateButton).toBeEnabled();
  });

  test('calls onTranslate with correct parameters when translate button is clicked', async () => {
    const user = userEvent.setup();
    mockValidateTranslationRequest.mockReturnValue({ isValid: true, errors: [] });
    mockOnTranslate.mockResolvedValue(mockTranslationResult);

    render(<TranslationInterface onTranslate={mockOnTranslate} />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    const translateButton = screen.getByRole('button', { name: /translate/i });

    await user.type(textArea, 'Hello world');
    await user.click(translateButton);

    await waitFor(() => {
      expect(mockOnTranslate).toHaveBeenCalledWith({
        text: 'Hello world',
        sourceLanguage: 'en',
        targetLanguage: 'hi',
        enableCache: true,
        model: 'auto'
      });
    });
  });

  test('displays translation result after successful translation', async () => {
    const user = userEvent.setup();
    mockValidateTranslationRequest.mockReturnValue({ isValid: true, errors: [] });
    mockOnTranslate.mockResolvedValue(mockTranslationResult);

    render(<TranslationInterface onTranslate={mockOnTranslate} />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    const translateButton = screen.getByRole('button', { name: /translate/i });

    await user.type(textArea, 'Hello world');
    await user.click(translateButton);

    await waitFor(() => {
      expect(screen.getByText('नमस्ते संसार')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Model: indictrans')).toBeInTheDocument();
    expect(screen.getByText('Time: 0.50s')).toBeInTheDocument();
    expect(screen.getByText('Confidence: 95.0%')).toBeInTheDocument();
  });

  test('displays alternative translations when available', async () => {
    const user = userEvent.setup();
    mockValidateTranslationRequest.mockReturnValue({ isValid: true, errors: [] });
    mockOnTranslate.mockResolvedValue(mockTranslationResult);

    render(<TranslationInterface onTranslate={mockOnTranslate} />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    const translateButton = screen.getByRole('button', { name: /translate/i });

    await user.type(textArea, 'Hello world');
    await user.click(translateButton);

    await waitFor(() => {
      expect(screen.getByText('Alternative translations:')).toBeInTheDocument();
    });
    
    expect(screen.getByText('हैलो वर्ल्ड')).toBeInTheDocument();
  });

  test('displays cache indicator when result is from cache', async () => {
    const user = userEvent.setup();
    const cachedResult = { ...mockTranslationResult, fromCache: true };
    mockValidateTranslationRequest.mockReturnValue({ isValid: true, errors: [] });
    mockOnTranslate.mockResolvedValue(cachedResult);

    render(<TranslationInterface onTranslate={mockOnTranslate} />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    const translateButton = screen.getByRole('button', { name: /translate/i });

    await user.type(textArea, 'Hello world');
    await user.click(translateButton);

    await waitFor(() => {
      expect(screen.getByText('Cached')).toBeInTheDocument();
    });
  });

  test('displays validation errors when request is invalid', async () => {
    const user = userEvent.setup();
    mockValidateTranslationRequest.mockReturnValue({
      isValid: false,
      errors: ['Text is too long', 'Invalid language pair']
    });

    render(<TranslationInterface onTranslate={mockOnTranslate} />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    const translateButton = screen.getByRole('button', { name: /translate/i });

    await user.type(textArea, 'Some text');
    await user.click(translateButton);

    await waitFor(() => {
      expect(screen.getByText('Please fix the following issues:')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Text is too long')).toBeInTheDocument();
    expect(screen.getByText('Invalid language pair')).toBeInTheDocument();
    expect(mockOnTranslate).not.toHaveBeenCalled();
  });

  test('displays error when translation fails', async () => {
    const user = userEvent.setup();
    mockValidateTranslationRequest.mockReturnValue({ isValid: true, errors: [] });
    mockOnTranslate.mockRejectedValue(new Error('Translation service unavailable'));

    render(<TranslationInterface onTranslate={mockOnTranslate} />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    const translateButton = screen.getByRole('button', { name: /translate/i });

    await user.type(textArea, 'Hello world');
    await user.click(translateButton);

    await waitFor(() => {
      expect(screen.getByText('Please fix the following issues:')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Translation service unavailable')).toBeInTheDocument();
  });

  test('shows loading state during translation', async () => {
    const user = userEvent.setup();
    mockValidateTranslationRequest.mockReturnValue({ isValid: true, errors: [] });
    // Mock a delay in translation
    mockOnTranslate.mockImplementation(() => new Promise(resolve => 
      setTimeout(() => resolve(mockTranslationResult), 100)
    ));

    render(<TranslationInterface onTranslate={mockOnTranslate} />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    const translateButton = screen.getByRole('button', { name: /translate/i });

    await user.type(textArea, 'Hello world');
    await user.click(translateButton);

    // Should show loading state
    expect(screen.getByText('Translating...')).toBeInTheDocument();

    // Wait for translation to complete
    await waitFor(() => {
      expect(screen.getByText('नमस्ते संसार')).toBeInTheDocument();
    });
  });

  test('disables controls when loading prop is true', () => {
    render(<TranslationInterface onTranslate={mockOnTranslate} isLoading={true} />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    const translateButton = screen.getByRole('button', { name: /translate/i });
    const clearButton = screen.getByRole('button', { name: /clear/i });
    const swapButton = screen.getByTitle('Swap languages');

    expect(textArea).toBeDisabled();
    expect(translateButton).toBeDisabled();
    expect(clearButton).toBeDisabled();
    expect(swapButton).toBeDisabled();
  });
});
