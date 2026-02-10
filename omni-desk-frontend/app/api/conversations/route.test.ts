import { describe, it, expect, beforeEach, vi } from 'vitest';
import { GET } from './route';

describe('Conversations API Route', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch conversations and enrich with customer data', async () => {
    const mockConversations = [
      {
        id: 'conv-1',
        customer_id: 'cust-1',
        channel: 'email',
        subject: 'Help with account',
        created_at: '2026-02-10T12:00:00Z',
        message_count: 3,
      },
      {
        id: 'conv-2',
        customer_id: 'cust-2',
        channel: 'whatsapp',
        subject: null,
        created_at: '2026-02-09T12:00:00Z',
        message_count: 2,
      },
    ];

    const mockCustomers = [
      {
        id: 'cust-1',
        name: 'John Doe',
        email: 'john@example.com',
        phone: null,
      },
      {
        id: 'cust-2',
        name: null,
        email: null,
        phone: '+1234567890',
      },
    ];

    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockConversations,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockCustomers,
      });

    const response = await GET();
    const data = await response.json();

    expect(fetch).toHaveBeenCalledTimes(2);
    expect(data).toHaveLength(2);

    // Email conversation with customer name
    expect(data[0]).toMatchObject({
      conversation_id: 'conv-1',
      customer_name: 'John Doe',
      email: 'john@example.com',
      last_message: 'Help with account',
      channel: 'email',
      message_count: 3,
    });

    // WhatsApp conversation with phone as name
    expect(data[1]).toMatchObject({
      conversation_id: 'conv-2',
      customer_name: '+1234567890',
      email: '+1234567890',
      last_message: 'New conversation',
      channel: 'whatsapp',
      message_count: 2,
    });
  });

  it('should handle web_form channel correctly', async () => {
    const mockConversations = [
      {
        id: 'conv-3',
        customer_id: 'cust-3',
        channel: 'web_form',
        subject: 'Bug report',
        created_at: '2026-02-10T12:00:00Z',
        message_count: 1,
      },
    ];

    const mockCustomers = [
      {
        id: 'cust-3',
        name: 'Jane Smith',
        email: 'jane@example.com',
        phone: null,
      },
    ];

    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockConversations,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockCustomers,
      });

    const response = await GET();
    const data = await response.json();

    expect(data[0].channel).toBe('web_form');
  });

  it('should handle missing customer data gracefully', async () => {
    const mockConversations = [
      {
        id: 'conv-4',
        customer_id: 'missing-customer',
        channel: 'email',
        subject: 'Test',
        created_at: '2026-02-10T12:00:00Z',
        message_count: 1,
      },
    ];

    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockConversations,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

    const response = await GET();
    const data = await response.json();

    expect(data[0].customer_name).toBe('Unknown Customer');
    expect(data[0].email).toBe('');
  });

  it('should handle conversations API error', async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    const response = await GET();
    const data = await response.json();

    expect(data).toEqual([]);
  });

  it('should handle customers API error gracefully', async () => {
    const mockConversations = [
      {
        id: 'conv-5',
        customer_id: 'cust-5',
        channel: 'email',
        subject: 'Test',
        created_at: '2026-02-10T12:00:00Z',
        message_count: 1,
      },
    ];

    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockConversations,
      })
      .mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

    const response = await GET();
    const data = await response.json();

    // Should still return conversations, just without customer data
    expect(data).toHaveLength(1);
    expect(data[0].customer_name).toBe('Unknown Customer');
  });
});
