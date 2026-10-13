import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { SearchHero } from '../components/SearchHero';

describe('SearchHero Component', () => {
  const categories = ['Computer Science', 'Algorithms', 'Fiction'];

  it('renders welcoming prompt and search input', () => {
    const onSearch = vi.fn();
    render(
      <SearchHero
        onSearch={onSearch}
        categories={categories}
        selectedCategory="All"
        onSelectCategory={vi.fn()}
        onlyAvailable={false}
        onToggleOnlyAvailable={vi.fn()}
        isLoading={false}
      />
    );

    expect(screen.getByText(/Welcome to your Library Assistant/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Search by title, author, ISBN/i)).toBeInTheDocument();
  });

  it('submits search query when typing and submitting form', () => {
    const onSearch = vi.fn();
    render(
      <SearchHero
        onSearch={onSearch}
        categories={categories}
        selectedCategory="All"
        onSelectCategory={vi.fn()}
        onlyAvailable={false}
        onToggleOnlyAvailable={vi.fn()}
        isLoading={false}
      />
    );

    const input = screen.getByPlaceholderText(/Search by title, author, ISBN/i);
    fireEvent.change(input, { target: { value: 'Clean Code' } });

    const searchButton = screen.getByRole('button', { name: /^search$/i });
    fireEvent.click(searchButton);

    expect(onSearch).toHaveBeenCalledWith('Clean Code', false, 'All');
  });

  it('clicks on a suggested example query to trigger search', () => {
    const onSearch = vi.fn();
    render(
      <SearchHero
        onSearch={onSearch}
        categories={categories}
        selectedCategory="All"
        onSelectCategory={vi.fn()}
        onlyAvailable={false}
        onToggleOnlyAvailable={vi.fn()}
        isLoading={false}
      />
    );

    const exampleBtn = screen.getByRole('button', { name: /"Find Clean Code by Robert C. Martin"/i });
    fireEvent.click(exampleBtn);

    expect(onSearch).toHaveBeenCalledWith('Find Clean Code by Robert C. Martin', false, 'All');
  });

  it('toggles only available filter', () => {
    const onToggleOnlyAvailable = vi.fn();
    render(
      <SearchHero
        onSearch={vi.fn()}
        categories={categories}
        selectedCategory="All"
        onSelectCategory={vi.fn()}
        onlyAvailable={false}
        onToggleOnlyAvailable={onToggleOnlyAvailable}
        isLoading={false}
      />
    );

    const availBtn = screen.getByRole('button', { name: /available for borrowing only/i });
    fireEvent.click(availBtn);

    expect(onToggleOnlyAvailable).toHaveBeenCalledTimes(1);
  });
});
