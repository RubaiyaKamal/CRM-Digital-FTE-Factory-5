import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // In a real app, this would query the database
    // For now, return calculated stats from the tickets API
    const response = await fetch('http://localhost:8000/api/v1/tickets?limit=100', {
      cache: 'no-store',
    });

    if (!response.ok) {
      throw new Error('Failed to fetch tickets');
    }

    const tickets = await response.json();

    // Calculate stats
    const totalTickets = tickets.length;
    const openTickets = tickets.filter(
      (t: any) => t.status === 'open' || t.status === 'pending'
    ).length;

    // Count tickets resolved today
    const today = new Date().toISOString().split('T')[0];
    const resolvedToday = tickets.filter((t: any) => {
      const resolvedDate = t.resolved_at?.split('T')[0];
      return resolvedDate === today && t.status === 'resolved';
    }).length;

    // Calculate average response time (mock for now)
    // In production, this would query actual response times from the database
    const avgResponseTime = tickets.length > 0 ? '1.8s' : '0s';

    // Calculate changes (mock percentages)
    const stats = {
      totalTickets: {
        value: totalTickets.toString(),
        change: '+12%',
        trend: 'up' as const,
      },
      openTickets: {
        value: openTickets.toString(),
        change: '+' + openTickets.toString(),
        trend: 'up' as const,
      },
      resolvedToday: {
        value: resolvedToday.toString(),
        change: '+15%',
        trend: 'up' as const,
      },
      avgResponseTime: {
        value: avgResponseTime,
        change: '-0.3s',
        trend: 'down' as const,
      },
    };

    return NextResponse.json(stats);
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    // Return fallback data on error
    return NextResponse.json({
      totalTickets: {
        value: '0',
        change: '+0%',
        trend: 'up' as const,
      },
      openTickets: {
        value: '0',
        change: '+0',
        trend: 'up' as const,
      },
      resolvedToday: {
        value: '0',
        change: '+0%',
        trend: 'up' as const,
      },
      avgResponseTime: {
        value: '0s',
        change: '0s',
        trend: 'down' as const,
      },
    });
  }
}
