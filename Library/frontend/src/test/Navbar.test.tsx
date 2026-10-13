import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { Navbar } from '../components/Navbar';

describe('Navbar Component', () => {
  it('renders brand name and tags', () => {
    render(
      <Navbar
        darkMode={false}
        onToggleTheme={vi.fn()}
        isAdminView={false}
        onToggleAdmin={vi.fn()}
        onOpenChat={vi.fn()}
      />
    );

    expect(screen.getByText('Athenaeum')).toBeInTheDocument();
    expect(screen.getByText('Library Agent')).toBeInTheDocument();
  });

  it('triggers onToggleTheme when clicking theme button', () => {
    const onToggleTheme = vi.fn();
    render(
      <Navbar
        darkMode={false}
        onToggleTheme={onToggleTheme}
        isAdminView={false}
        onToggleAdmin={vi.fn()}
        onOpenChat={vi.fn()}
      />
    );

    const themeBtn = screen.getByLabelText(/toggle theme/i);
    fireEvent.click(themeBtn);

    expect(onToggleTheme).toHaveBeenCalledTimes(1);
  });

  it('triggers onToggleAdmin when clicking Admin Portal button', () => {
    const onToggleAdmin = vi.fn();
    render(
      <Navbar
        darkMode={false}
        onToggleTheme={vi.fn()}
        isAdminView={false}
        onToggleAdmin={onToggleAdmin}
        onOpenChat={vi.fn()}
      />
    );

    const adminBtn = screen.getByTitle(/administrator portal/i);
    fireEvent.click(adminBtn);

    expect(onToggleAdmin).toHaveBeenCalledTimes(1);
  });

  it('triggers onOpenChat when clicking Ask AI Assistant', () => {
    const onOpenChat = vi.fn();
    render(
      <Navbar
        darkMode={false}
        onToggleTheme={vi.fn()}
        isAdminView={false}
        onToggleAdmin={vi.fn()}
        onOpenChat={onOpenChat}
      />
    );

    const chatBtn = screen.getByTitle(/ask ai assistant/i);
    fireEvent.click(chatBtn);

    expect(onOpenChat).toHaveBeenCalledTimes(1);
  });
});
