import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import LoadingSpinner from './LoadingSpinner';

describe('LoadingSpinner Component', () => {
  it('should render with default message', () => {
    render(<LoadingSpinner />);

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('should render with custom message', () => {
    render(<LoadingSpinner message="Fetching customers..." />);

    expect(screen.getByText('Fetching customers...')).toBeInTheDocument();
  });

  it('should render spinner icon', () => {
    const { container } = render(<LoadingSpinner />);

    // Check for svg element (Loader2 icon)
    const spinner = container.querySelector('svg');
    expect(spinner).toBeInTheDocument();
  });

  it('should have animate-spin class on spinner', () => {
    const { container } = render(<LoadingSpinner />);

    const spinner = container.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });
});
