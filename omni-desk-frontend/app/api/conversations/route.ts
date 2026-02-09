import { NextResponse } from 'next/server';

export async function GET() {
  // Real conversations from database (hardcoded for now - will be dynamic later)
  const realConversations = [
    {
      id: '2251c0bb-65a9-4ae3-8b5e-6085453f26fd',
      customer: 'kh0102267@gmail.com',
      email: 'kh0102267@gmail.com',
      lastMessage: 'Tell me the billing and contact issue',
      channel: 'Web',
      created_at: '2026-02-09T09:27:59Z',
    },
    {
      id: '04efac40-2d3c-4296-bd90-b89772ef4e40',
      customer: 'livetest@example.com',
      email: 'livetest@example.com',
      lastMessage: 'Billing issue inquiry',
      channel: 'Web',
      created_at: '2026-02-08T13:17:40Z',
    },
    {
      id: 'bf19e90f-b965-440a-a273-a0adf645c052',
      customer: 'demo@test.com',
      email: 'demo@test.com',
      lastMessage: 'Data export request',
      channel: 'Web',
      created_at: '2026-02-08T13:14:04Z',
    },
  ];

  return NextResponse.json(realConversations);
}
