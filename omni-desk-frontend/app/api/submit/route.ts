import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { channel, ...data } = body;

    // Determine backend endpoint based on channel
    let backendEndpoint = 'http://localhost:8000/webhooks/web_form';

    if (channel === 'email') {
      backendEndpoint = 'http://localhost:8000/webhooks/email';
    } else if (channel === 'whatsapp') {
      backendEndpoint = 'http://localhost:8000/webhooks/whatsapp';
    } else if (channel === 'web_form') {
      backendEndpoint = 'http://localhost:8000/webhooks/web_form';
    }

    // Proxy request to backend API
    const response = await fetch(backendEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Backend API error' },
        { status: response.status }
      );
    }

    const responseData = await response.json();
    return NextResponse.json(responseData);
  } catch (error) {
    console.error('API proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to submit form' },
      { status: 500 }
    );
  }
}
