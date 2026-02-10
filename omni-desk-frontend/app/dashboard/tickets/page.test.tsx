import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TicketsPage from './page';

vi.mock('react-hot-toast', () => ({
  default: {
    error: vi.fn(),
    success: vi.fn(),
  },
}));

describe('TicketsPage', () => {
  const mockTickets = [
    {
      id: 'ticket-1',
      customer: 'cust-1',
      email: 'john@example.com',
      subject: 'Help with account',
      channel: 'Email',
      status: 'Open',
      priority: 'High',
      date: '2026-02-10',
      category: 'technical',
    },
    {
      id: 'ticket-2',
      customer: 'cust-2',
      email: '',
      subject: 'WhatsApp message',
      channel: 'Whatsapp',
      status: 'Resolved',
      priority: 'Medium',
      date: '2026-02-09',
      category: 'general',
    },
    {
      id: 'ticket-3',
      customer: 'cust-3',
      email: 'jane@example.com',
      subject: 'Billing question',
      channel: 'Web_form',
      status: 'Open',
      priority: 'Urgent',
      date: '2026-02-08',
      category: 'billing',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockTickets,
    });
  });

  it('should render page title', async () => {
    render(<TicketsPage />);

    await waitFor(() => {
      expect(screen.getByText('Tickets')).toBeInTheDocument();
    });
  });

  it('should fetch and display tickets', async () => {
    render(<TicketsPage />);

    await waitFor(() => {
      expect(screen.getByText('Help with account')).toBeInTheDocument();
      expect(screen.getByText('WhatsApp message')).toBeInTheDocument();
      expect(screen.getByText('Billing question')).toBeInTheDocument();
    });
  });

  it('should show loading state initially', () => {
    render(<TicketsPage />);

    expect(screen.getByText('Loading tickets...')).toBeInTheDocument();
  });

  it('should filter tickets by status', async () => {
    render(<TicketsPage />);

    await waitFor(() => screen.getByText('Help with account'));

    const statusFilter = screen.getByDisplayValue('All Statuses') as HTMLSelectElement;
    fireEvent.change(statusFilter, { target: { value: 'Open' } });

    await waitFor(() => {
      expect(screen.getByText('Help with account')).toBeInTheDocument();
      expect(screen.getByText('Billing question')).toBeInTheDocument();
      expect(screen.queryByText('WhatsApp message')).not.toBeInTheDocument();
    });
  });

  it('should filter tickets by channel', async () => {
    render(<TicketsPage />);

    await waitFor(() => screen.getByText('Help with account'));

    const channelFilter = screen.getByDisplayValue('All Channels') as HTMLSelectElement;
    fireEvent.change(channelFilter, { target: { value: 'Email' } });

    await waitFor(() => {
      expect(screen.getByText('Help with account')).toBeInTheDocument();
      expect(screen.queryByText('WhatsApp message')).not.toBeInTheDocument();
    });
  });

  it('should filter tickets by priority', async () => {
    render(<TicketsPage />);

    await waitFor(() => screen.getByText('Help with account'));

    const priorityFilter = screen.getByDisplayValue('All Priorities') as HTMLSelectElement;
    fireEvent.change(priorityFilter, { target: { value: 'Urgent' } });

    await waitFor(() => {
      expect(screen.getByText('Billing question')).toBeInTheDocument();
      expect(screen.queryByText('Help with account')).not.toBeInTheDocument();
    });
  });

  it('should search tickets by subject', async () => {
    const user = userEvent.setup();
    render(<TicketsPage />);

    await waitFor(() => screen.getByText('Help with account'));

    const searchInput = screen.getByPlaceholderText('Search tickets...');
    await user.type(searchInput, 'billing');

    await waitFor(() => {
      expect(screen.getByText('Billing question')).toBeInTheDocument();
      expect(screen.queryByText('Help with account')).not.toBeInTheDocument();
    });
  });

  it('should display correct status badges', async () => {
    render(<TicketsPage />);

    await waitFor(() => {
      const openBadges = screen.getAllByText('Open');
      const resolvedBadges = screen.getAllByText('Resolved');

      expect(openBadges.length).toBeGreaterThan(0);
      expect(resolvedBadges.length).toBeGreaterThan(0);
    });
  });

  it('should display correct priority badges', async () => {
    render(<TicketsPage />);

    await waitFor(() => {
      expect(screen.getByText('High')).toBeInTheDocument();
      expect(screen.getByText('Medium')).toBeInTheDocument();
      expect(screen.getByText('Urgent')).toBeInTheDocument();
    });
  });

  it('should handle API errors', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

    render(<TicketsPage />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to fetch tickets/i)).toBeInTheDocument();
    });
  });

  it('should allow retrying after error', async () => {
    global.fetch = vi.fn().mockRejectedValueOnce(new Error('Network error'));

    render(<TicketsPage />);

    await waitFor(() => screen.getByText(/Failed to fetch tickets/i));

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockTickets,
    });

    const retryButton = screen.getByText('Try Again');
    fireEvent.click(retryButton);

    await waitFor(() => {
      expect(screen.getByText('Help with account')).toBeInTheDocument();
    });
  });

  it('should show pagination controls', async () => {
    render(<TicketsPage />);

    await waitFor(() => {
      expect(screen.getByText('Previous')).toBeInTheDocument();
      expect(screen.getByText('Next')).toBeInTheDocument();
    });
  });

  it('should show "no tickets" message when search returns empty', async () => {
    const user = userEvent.setup();
    render(<TicketsPage />);

    await waitFor(() => screen.getByText('Help with account'));

    const searchInput = screen.getByPlaceholderText('Search tickets...');
    await user.type(searchInput, 'nonexistent-ticket');

    await waitFor(() => {
      expect(screen.getByText(/No tickets found/i)).toBeInTheDocument();
    });
  });

  it('should display channel badges correctly', async () => {
    render(<TicketsPage />);

    await waitFor(() => {
      expect(screen.getByText('Email')).toBeInTheDocument();
      expect(screen.getByText('Whatsapp')).toBeInTheDocument();
      expect(screen.getByText('Web_form')).toBeInTheDocument();
    });
  });
});
