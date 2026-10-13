import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import React from 'react';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

describe('LoadingSkeleton Component', () => {
  it('renders 6 loading skeleton cards with shimmer effect', () => {
    const { container } = render(<LoadingSkeleton />);
    const shimmerElements = container.querySelectorAll('.skeleton-shimmer');
    expect(shimmerElements.length).toBeGreaterThan(10);
  });
});
