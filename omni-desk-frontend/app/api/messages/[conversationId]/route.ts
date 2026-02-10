import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ conversationId: string }> }
) {
  try {
    const { conversationId } = await params;

    // Fetch real messages from backend API
    const response = await fetch(`http://localhost:8000/api/v1/conversations/${conversationId}/messages`);

    if (!response.ok) {
      console.error(`Failed to fetch messages for conversation ${conversationId}: ${response.status}`);
      return NextResponse.json([]);
    }

    const messages = await response.json();

    // Transform backend format to frontend format
    const transformedMessages = messages.map((msg: any) => ({
      id: msg.id || `msg-${Date.now()}`,
      role: msg.role || 'customer',
      content: msg.content || msg.message || '',
      timestamp: msg.created_at || msg.timestamp || new Date().toISOString(),
    }));

    return NextResponse.json(transformedMessages);
  } catch (error) {
    console.error('Error fetching messages:', error);
    return NextResponse.json([]);
  }
}
