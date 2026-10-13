import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { EmptyState } from '../components/EmptyState';

describe('EmptyState Component', () => {
  it('renders truthful not-found message mentioning searched query', () => {
    const handleReset = vi.fn();
    render(<EmptyState query="Unknown Fantasy Book" onReset={handleReset} />);

    expect(screen.getByText(/Not Listed in Library Catalogue/i)).toBeInTheDocument();
    expect(screen.getByText(/"Unknown Fantasy Book"/i)).toBeInTheDocument();
  });

  it('triggers onReset when clicking Clear Search & Filters', () => {
    const handleReset = vi.fn();
    render(<EmptyState query="Some Missing Title" onReset={handleReset} />);

    const button = screen.getByRole('button', { name: /clear search & filters/i });
    fireEvent.click(button);

    expect(handleReset).toHaveBeenCalledTimes(1);
  });

  it('triggers onBrowseAll when clicking Browse Full Catalogue', () => {
    const handleBrowseAll = vi.fn();
    render(<EmptyState query="Missing" onReset={vi.fn()} onBrowseAll={handleBrowseAll} />);

    const button = screen.getByRole('button', { name: /browse full catalogue/i });
    fireEvent.click(button);

    expect(handleBrowseAll).toHaveBeenCalledTimes(1);
  });
});
