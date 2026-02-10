import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Fetch real conversations from backend API
    const response = await fetch('http://localhost:8000/api/v1/conversations?limit=100');

    if (!response.ok) {
      throw new Error(`Backend API returned ${response.status}`);
    }

    const conversations = await response.json();

    // Transform backend format to frontend format
    const transformedConversations = conversations.map((conv: any) => ({
      conversation_id: conv.id,
      customer_name: conv.email || conv.customer_id || 'Unknown Customer',
      email: conv.email || '',
      last_message: conv.subject || 'New conversation',
      message: conv.subject || 'New conversation',
      channel: conv.channel === 'web_form' ? 'web_form' : conv.channel,
      created_at: conv.created_at,
      timestamp: conv.created_at,
      message_count: conv.message_count || 0,
    }));

    return NextResponse.json(transformedConversations);
  } catch (error) {
    console.error('Error fetching conversations:', error);
    return NextResponse.json([]);
  }
}
