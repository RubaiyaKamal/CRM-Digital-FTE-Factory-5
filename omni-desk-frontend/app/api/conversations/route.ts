import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Fetch conversations and customers in parallel
    const [convsResponse, customersResponse] = await Promise.all([
      fetch('http://localhost:8000/api/v1/conversations?limit=100'),
      fetch('http://localhost:8000/api/v1/customers?limit=100'),
    ]);

    if (!convsResponse.ok) {
      throw new Error(`Backend API returned ${convsResponse.status}`);
    }

    const conversations = await convsResponse.json();
    const customers = customersResponse.ok ? await customersResponse.json() : [];

    // Create customer lookup map
    const customerMap = new Map(customers.map((c: any) => [c.id, c]));

    // Transform backend format to frontend format with customer data
    const transformedConversations = conversations.map((conv: any) => {
      const customer = customerMap.get(conv.customer_id);
      const customerName = customer?.name || customer?.email || customer?.phone || 'Unknown Customer';

      return {
        conversation_id: conv.id,
        customer_name: customerName,
        email: customer?.email || customer?.phone || '',
        last_message: conv.subject || 'New conversation',
        message: conv.subject || 'New conversation',
        channel: conv.channel === 'web_form' ? 'web_form' : conv.channel,
        created_at: conv.created_at,
        timestamp: conv.created_at,
        message_count: conv.message_count || 0,
      };
    });

    return NextResponse.json(transformedConversations);
  } catch (error) {
    console.error('Error fetching conversations:', error);
    return NextResponse.json([]);
  }
}
