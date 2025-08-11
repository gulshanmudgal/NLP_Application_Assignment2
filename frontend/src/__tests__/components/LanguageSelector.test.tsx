import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import LanguageSelector from '../../components/LanguageSelector';

describe('LanguageSelector', () => {
  const mockOnLanguageChange = jest.fn();

  beforeEach(() => {
    mockOnLanguageChange.mockClear();
  });

  test('renders language selector with English as default', () => {
    render(
      <LanguageSelector
        selectedLanguage="en"
        onLanguageChange={mockOnLanguageChange}
        label="Select language"
      />
    );

    const select = screen.getByRole('combobox');
    expect(select).toHaveValue('en');
  });

  test('calls onLanguageChange when language is selected', () => {
    render(
      <LanguageSelector
        selectedLanguage="en"
        onLanguageChange={mockOnLanguageChange}
        label="Select language"
      />
    );

    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'hi' } });

    expect(mockOnLanguageChange).toHaveBeenCalledWith('hi');
  });

  test('renders with pre-selected value', () => {
    render(
      <LanguageSelector
        selectedLanguage="hi"
        onLanguageChange={mockOnLanguageChange}
        label="Select language"
      />
    );

    const select = screen.getByRole('combobox');
    expect(select).toHaveValue('hi');
  });

  test('can be disabled', () => {
    render(
      <LanguageSelector
        selectedLanguage="en"
        onLanguageChange={mockOnLanguageChange}
        label="Select language"
        disabled={true}
      />
    );

    const select = screen.getByRole('combobox');
    expect(select).toBeDisabled();
  });

  test('shows all available languages', () => {
    render(
      <LanguageSelector
        selectedLanguage="en"
        onLanguageChange={mockOnLanguageChange}
        label="Select language"
      />
    );

    // Check that main languages are available as options
    expect(screen.getByText('English (English)')).toBeInTheDocument();
    expect(screen.getByText('Hindi (हिन्दी)')).toBeInTheDocument();
    expect(screen.getByText('Tamil (தமிழ்)')).toBeInTheDocument();
  });

  test('displays label when provided', () => {
    render(
      <LanguageSelector
        selectedLanguage="en"
        onLanguageChange={mockOnLanguageChange}
        label="Choose language"
      />
    );

    expect(screen.getByText('Choose language')).toBeInTheDocument();
  });
});