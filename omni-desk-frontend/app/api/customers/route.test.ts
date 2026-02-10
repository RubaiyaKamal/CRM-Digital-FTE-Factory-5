import { describe, it, expect, beforeEach, vi } from 'vitest';
import { GET } from './route';

describe('Customers API Route', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch and transform customers successfully', async () => {
    const mockCustomers = [
      {
        id: '123',
        name: 'John Doe',
        email: 'john@example.com',
        phone: null,
        ticket_count: 5,
        created_at: '2026-02-10T12:00:00Z',
      },
      {
        id: '456',
        name: 'Unknown',
        email: null,
        phone: '+1234567890',
        ticket_count: 3,
        created_at: '2026-02-09T12:00:00Z',
      },
    ];

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockCustomers,
    });

    const response = await GET();
    const data = await response.json();

    expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/customers?limit=100');
    expect(data).toHaveLength(2);

    // Customer with email should have Email channel
    expect(data[0]).toMatchObject({
      id: '123',
      name: 'John Doe',
      email: 'john@example.com',
      phone: '',
      totalTickets: 5,
      lastContact: '2026-02-10',
      channels: ['Email'],
    });

    // Customer with phone should have WhatsApp channel
    expect(data[1]).toMatchObject({
      id: '456',
      name: 'Unknown',
      email: '',
      phone: '+1234567890',
      totalTickets: 3,
      lastContact: '2026-02-09',
      channels: ['WhatsApp'],
    });
  });

  it('should handle customers with both email and phone', async () => {
    const mockCustomers = [
      {
        id: '789',
        name: 'Jane Smith',
        email: 'jane@example.com',
        phone: '+9876543210',
        ticket_count: 10,
        created_at: '2026-02-10T12:00:00Z',
      },
    ];

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockCustomers,
    });

    const response = await GET();
    const data = await response.json();

    expect(data[0].channels).toEqual(['Email', 'WhatsApp']);
  });

  it('should handle API errors gracefully', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
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

  it('should use default channel when no email or phone', async () => {
    const mockCustomers = [
      {
        id: '999',
        name: 'Unknown Customer',
        email: null,
        phone: null,
        ticket_count: 0,
        created_at: '2026-02-10T12:00:00Z',
      },
    ];

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockCustomers,
    });

    const response = await GET();
    const data = await response.json();

    expect(data[0].channels).toEqual(['Email']); // Default fallback
  });
});
