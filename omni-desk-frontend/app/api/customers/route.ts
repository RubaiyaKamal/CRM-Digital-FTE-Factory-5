import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Fetch real customers from backend API
    const response = await fetch('http://localhost:8000/api/v1/customers?limit=100');

    if (!response.ok) {
      throw new Error(`Backend API returned ${response.status}`);
    }

    const customers = await response.json();

    // Transform backend format to frontend format
    const transformedCustomers = customers.map((customer: any) => {
      // Determine channels based on contact info
      const channels = [];
      if (customer.email) channels.push('Email');
      if (customer.phone) channels.push('WhatsApp');
      if (channels.length === 0) channels.push('Email'); // Default fallback

      return {
        id: customer.id,
        name: customer.name || 'Unknown',
        email: customer.email || '',
        phone: customer.phone || '',
        totalTickets: customer.ticket_count,
        lastContact: customer.created_at.split('T')[0],
        channels: channels,
      };
    });

    return NextResponse.json(transformedCustomers);
  } catch (error) {
    console.error('Error fetching customers:', error);
    return NextResponse.json([]);
  }
}
