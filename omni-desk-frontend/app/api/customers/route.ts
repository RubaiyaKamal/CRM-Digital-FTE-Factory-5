import { NextResponse } from 'next/server';

export async function GET() {
  // Real customers from database (hardcoded for now - will be dynamic later)
  const realCustomers = [
    {
      id: 'customer-001',
      name: 'Your Submission',
      email: 'kh0102267@gmail.com',
      phone: '+1234567890',
      totalTickets: 5,
      lastContact: '2026-02-09',
      channels: ['Web', 'Email'],
    },
    {
      id: 'customer-002',
      name: 'Live Tester',
      email: 'livetest@example.com',
      phone: '+1234567891',
      totalTickets: 3,
      lastContact: '2026-02-08',
      channels: ['Web'],
    },
    {
      id: 'customer-003',
      name: 'Demo User',
      email: 'demo@test.com',
      phone: '+1234567892',
      totalTickets: 2,
      lastContact: '2026-02-08',
      channels: ['Web'],
    },
  ];

  return NextResponse.json(realCustomers);
}
