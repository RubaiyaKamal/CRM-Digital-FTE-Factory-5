import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { conversationId: string } }
) {
  const conversationId = params.conversationId;

  // Real messages from database for conversation 2251c0bb-65a9-4ae3-8b5e-6085453f26fd
  const messagesData: Record<string, any[]> = {
    '2251c0bb-65a9-4ae3-8b5e-6085453f26fd': [
      {
        id: 'msg-1',
        role: 'customer',
        content: 'define me the issues in my submission',
        timestamp: '2026-02-09T08:44:50Z',
      },
      {
        id: 'msg-2',
        role: 'customer',
        content: 'I have a technical issue with this',
        timestamp: '2026-02-09T09:17:18Z',
      },
      {
        id: 'msg-3',
        role: 'agent',
        content: "Hi there!\n\nI'm truly sorry for the frustration you're experiencing with logging into your account. I've escalated your issue to our support team, and they will assist you shortly. Thank you for your patience!\n\nBest,\nCloudFlow Support",
        timestamp: '2026-02-09T09:23:28Z',
      },
      {
        id: 'msg-4',
        role: 'customer',
        content: 'Tell me the billing and contact issue',
        timestamp: '2026-02-09T09:27:59Z',
      },
      {
        id: 'msg-5',
        role: 'agent',
        content: "I understand your concern regarding the billing issue. I've escalated your request to our support team, and they will reach out to you shortly for assistance.\n\nThank you for your patience!",
        timestamp: '2026-02-09T09:28:11Z',
      },
    ],
  };

  const messages = messagesData[conversationId] || [];
  return NextResponse.json(messages);
}
