import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { BookFormModal } from '../components/BookFormModal';

describe('BookFormModal Component', () => {
  it('does not render when isOpen is false', () => {
    const { container } = render(
      <BookFormModal
        isOpen={false}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        isLoading={false}
      />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renders form with empty fields for adding a book', () => {
    render(
      <BookFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        isLoading={false}
      />
    );

    expect(screen.getByText(/Add New Book to Catalogue/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/e.g. Clean Architecture/i)).toBeInTheDocument();
  });

  it('displays validation error if title is empty', async () => {
    const onSubmit = vi.fn();
    render(
      <BookFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={onSubmit}
        isLoading={false}
      />
    );

    const submitBtn = screen.getByRole('button', { name: /add to catalogue/i });
    fireEvent.click(submitBtn);

    // Browser HTML5 or form validation prevents submission
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('validates that available copies cannot exceed total copies', async () => {
    const onSubmit = vi.fn();
    render(
      <BookFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={onSubmit}
        isLoading={false}
      />
    );

    const titleInput = screen.getByPlaceholderText(/e.g. Clean Architecture/i);
    fireEvent.change(titleInput, { target: { value: 'Distributed Systems' } });

    // Total copies = 1, available copies = 5
    const numberInputs = screen.getAllByRole('spinbutton');
    fireEvent.change(numberInputs[0], { target: { value: '1' } });
    fireEvent.change(numberInputs[1], { target: { value: '5' } });

    const submitBtn = screen.getByRole('button', { name: /add to catalogue/i });
    fireEvent.submit(submitBtn.closest('form')!);

    expect(screen.getByText(/cannot exceed total copies/i)).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });
});
