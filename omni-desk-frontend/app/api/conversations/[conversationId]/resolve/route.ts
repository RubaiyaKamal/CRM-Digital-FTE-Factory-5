import { NextRequest, NextResponse } from 'next/server';

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ conversationId: string }> }
) {
  try {
    const { conversationId } = await params;

    // Update conversation status to resolved in backend
    const response = await fetch(
      `http://localhost:8000/api/v1/conversations/${conversationId}/resolve`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to resolve conversation' },
        { status: response.status }
      );
    }

    return NextResponse.json({ success: true, conversationId });
  } catch (error) {
    console.error('Error resolving conversation:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
