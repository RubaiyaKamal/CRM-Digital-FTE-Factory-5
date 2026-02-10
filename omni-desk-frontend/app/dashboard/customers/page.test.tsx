import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import CustomersPage from './page';

// Mock react-hot-toast
vi.mock('react-hot-toast', () => ({
  default: {
    error: vi.fn(),
    success: vi.fn(),
  },
}));

describe('CustomersPage', () => {
  const mockCustomers = [
    {
      id: 'cust-1',
      name: 'John Doe',
      email: 'john@example.com',
      phone: '+1234567890',
      totalTickets: 8,
      lastContact: '2026-02-09',
      channels: ['Email', 'WhatsApp'],
    },
    {
      id: 'cust-2',
      name: null,
      email: null,
      phone: '+923313494999',
      totalTickets: 3,
      lastContact: '2026-02-10',
      channels: ['WhatsApp'],
    },
    {
      id: 'cust-3',
      name: 'Jane Smith',
      email: 'jane@example.com',
      phone: null,
      totalTickets: 12,
      lastContact: '2026-02-08',
      channels: ['Email'],
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockCustomers,
    });
  });

  it('should render page title and description', async () => {
    render(<CustomersPage />);

    await waitFor(() => {
      expect(screen.getByText('Customers')).toBeInTheDocument();
      expect(screen.getByText(/View and manage your customer database/i)).toBeInTheDocument();
    });
  });

  it('should fetch and display customers', async () => {
    render(<CustomersPage />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
      expect(screen.getByText('+923313494999')).toBeInTheDocument();
    });
  });

  it('should show loading spinner initially', () => {
    render(<CustomersPage />);

    expect(screen.getByText('Loading customers...')).toBeInTheDocument();
  });

  it('should filter customers by name', async () => {
    const user = userEvent.setup();
    render(<CustomersPage />);

    await waitFor(() => screen.getByText('John Doe'));

    const searchInput = screen.getByPlaceholderText('Search by name or email...');
    await user.type(searchInput, 'john');

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.queryByText('Jane Smith')).not.toBeInTheDocument();
    });
  });

  it('should filter customers by email', async () => {
    const user = userEvent.setup();
    render(<CustomersPage />);

    await waitFor(() => screen.getByText('Jane Smith'));

    const searchInput = screen.getByPlaceholderText('Search by name or email...');
    await user.type(searchInput, 'jane@');

    await waitFor(() => {
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
      expect(screen.queryByText('John Doe')).not.toBeInTheDocument();
    });
  });

  it('should handle WhatsApp customers with null names', async () => {
    render(<CustomersPage />);

    await waitFor(() => {
      // Phone number should be used as name
      const phoneElements = screen.getAllByText('+923313494999');
      expect(phoneElements.length).toBeGreaterThan(0);
    });
  });

  it('should display correct channel badges', async () => {
    render(<CustomersPage />);

    await waitFor(() => {
      const emailBadges = screen.getAllByText('Email');
      const whatsappBadges = screen.getAllByText('WhatsApp');

      expect(emailBadges.length).toBeGreaterThan(0);
      expect(whatsappBadges.length).toBeGreaterThan(0);
    });
  });

  it('should show real customer count badge', async () => {
    render(<CustomersPage />);

    await waitFor(() => {
      expect(screen.getByText('3 Real')).toBeInTheDocument();
    });
  });

  it('should handle API errors', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

    render(<CustomersPage />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to fetch customers/i)).toBeInTheDocument();
    });
  });

  it('should allow retrying after error', async () => {
    global.fetch = vi.fn().mockRejectedValueOnce(new Error('Network error'));

    render(<CustomersPage />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to fetch customers/i)).toBeInTheDocument();
    });

    // Mock successful retry
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockCustomers,
    });

    const retryButton = screen.getByText('Try Again');
    fireEvent.click(retryButton);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });

  it('should change page size', async () => {
    render(<CustomersPage />);

    await waitFor(() => screen.getByText('John Doe'));

    const pageSizeSelect = screen.getByDisplayValue('12 per page') as HTMLSelectElement;
    fireEvent.change(pageSizeSelect, { target: { value: '6' } });

    await waitFor(() => {
      expect(pageSizeSelect.value).toBe('6');
    });
  });

  it('should show "no customers" message when search returns empty', async () => {
    const user = userEvent.setup();
    render(<CustomersPage />);

    await waitFor(() => screen.getByText('John Doe'));

    const searchInput = screen.getByPlaceholderText('Search by name or email...');
    await user.type(searchInput, 'nonexistent');

    await waitFor(() => {
      expect(screen.getByText('No customers found matching your search')).toBeInTheDocument();
    });
  });

  it('should display ticket counts correctly', async () => {
    render(<CustomersPage />);

    await waitFor(() => {
      expect(screen.getByText('8')).toBeInTheDocument(); // John's tickets
      expect(screen.getByText('3')).toBeInTheDocument(); // WhatsApp customer tickets
      expect(screen.getByText('12')).toBeInTheDocument(); // Jane's tickets
    });
  });

  it('should render View Chat button for customers with IDs', async () => {
    render(<CustomersPage />);

    await waitFor(() => {
      const viewChatButtons = screen.getAllByText('View Chat');
      expect(viewChatButtons.length).toBeGreaterThan(0);
    });
  });
});
