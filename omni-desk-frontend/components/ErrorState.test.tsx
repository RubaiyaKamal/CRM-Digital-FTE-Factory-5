import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ErrorState from './ErrorState';

describe('ErrorState Component', () => {
  it('should render error message', () => {
    render(
      <ErrorState
        message="Failed to load data"
        onRetry={vi.fn()}
        retrying={false}
      />
    );

    expect(screen.getByText('Failed to load data')).toBeInTheDocument();
  });

  it('should call onRetry when retry button is clicked', () => {
    const onRetry = vi.fn();
    render(
      <ErrorState
        message="Network error"
        onRetry={onRetry}
        retrying={false}
      />
    );

    const retryButton = screen.getByText('Try Again');
    fireEvent.click(retryButton);

    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it('should show loading state when retrying', () => {
    render(
      <ErrorState
        message="Failed to fetch"
        onRetry={vi.fn()}
        retrying={true}
      />
    );

    expect(screen.getByText('Retrying...')).toBeInTheDocument();
  });

  it('should disable retry button when retrying', () => {
    render(
      <ErrorState
        message="Error occurred"
        onRetry={vi.fn()}
        retrying={true}
      />
    );

    const retryButton = screen.getByRole('button');
    expect(retryButton).toBeDisabled();
  });

  it('should not disable retry button when not retrying', () => {
    render(
      <ErrorState
        message="Error occurred"
        onRetry={vi.fn()}
        retrying={false}
      />
    );

    const retryButton = screen.getByRole('button');
    expect(retryButton).not.toBeDisabled();
  });
});
