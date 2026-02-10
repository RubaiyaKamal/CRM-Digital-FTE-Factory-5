import { describe, it, expect, beforeEach, vi } from 'vitest';
import { GET } from './route';

describe('Tickets API Route', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch and transform tickets successfully', async () => {
    const mockTickets = [
      {
        id: 'ticket-1',
        customer_id: 'cust-1',
        raw_message: 'Help me with my account',
        channel: 'email',
        status: 'open',
        priority: 'high',
        created_at: '2026-02-10T12:00:00Z',
        category: 'technical',
      },
      {
        id: 'ticket-2',
        customer_id: 'cust-2',
        raw_message: 'Billing question',
        channel: 'whatsapp',
        status: 'resolved',
        priority: 'medium',
        created_at: '2026-02-09T12:00:00Z',
        category: 'billing',
      },
    ];

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockTickets,
    });

    const response = await GET();
    const data = await response.json();

    expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/tickets?limit=100');
    expect(data).toHaveLength(2);

    expect(data[0]).toMatchObject({
      id: 'ticket-1',
      customer: 'cust-1',
      email: '',
      subject: 'Help me with my account',
      channel: 'Email',
      status: 'Open',
      priority: 'High',
      date: '2026-02-10',
      category: 'technical',
    });

    expect(data[1]).toMatchObject({
      id: 'ticket-2',
      customer: 'cust-2',
      email: '',
      subject: 'Billing question',
      channel: 'Whatsapp',
      status: 'Resolved',
      priority: 'Medium',
      date: '2026-02-09',
      category: 'billing',
    });
  });

  it('should capitalize channel names correctly', async () => {
    const mockTickets = [
      {
        id: 'ticket-1',
        customer_id: 'cust-1',
        raw_message: 'Test',
        channel: 'web_form',
        status: 'open',
        priority: 'low',
        created_at: '2026-02-10T12:00:00Z',
        category: 'general',
      },
    ];

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockTickets,
    });

    const response = await GET();
    const data = await response.json();

    expect(data[0].channel).toBe('Web_form');
  });

  it('should handle empty raw_message', async () => {
    const mockTickets = [
      {
        id: 'ticket-1',
        customer_id: 'cust-1',
        raw_message: '',
        channel: 'email',
        status: 'open',
        priority: 'medium',
        created_at: '2026-02-10T12:00:00Z',
        category: 'general',
      },
    ];

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockTickets,
    });

    const response = await GET();
    const data = await response.json();

    expect(data[0].subject).toBe('No subject');
  });

  it('should handle API errors gracefully', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
    });

    const response = await GET();
    const data = await response.json();

    expect(data).toEqual([]);
  });

  it('should handle network errors', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

    const response = await GET();
    const data = await response.json();

    expect(data).toEqual([]);
  });
});
