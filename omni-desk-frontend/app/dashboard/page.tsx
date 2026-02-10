'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { TrendingUp, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import toast from 'react-hot-toast';
import { colors, gradients } from '@/lib/colors';

const defaultStats = [
  {
    key: 'totalTickets',
    label: 'Total Tickets',
    value: '0',
    change: '+0%',
    trend: 'up' as const,
    icon: TrendingUp,
    color: colors.primary.purple,
  },
  {
    key: 'openTickets',
    label: 'Open Tickets',
    value: '0',
    change: '+0',
    trend: 'up' as const,
    icon: AlertCircle,
    color: colors.warning,
  },
  {
    key: 'resolvedToday',
    label: 'Resolved Today',
    value: '0',
    change: '+0%',
    trend: 'up' as const,
    icon: CheckCircle,
    color: colors.success,
  },
  {
    key: 'avgResponseTime',
    label: 'Avg Response Time',
    value: '0s',
    change: '0s',
    trend: 'down' as const,
    icon: Clock,
    color: colors.primary.pink,
  },
];

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState(defaultStats);
  const [loading, setLoading] = useState(true);
  const [recentTickets, setRecentTickets] = useState<any[]>([]);

  useEffect(() => {
    // Fetch dashboard stats
    fetch('/api/dashboard/stats')
      .then((res) => res.json())
      .then((data) => {
        const updatedStats = defaultStats.map((stat) => ({
          ...stat,
          value: data[stat.key]?.value || stat.value,
          change: data[stat.key]?.change || stat.change,
          trend: data[stat.key]?.trend || stat.trend,
        }));
        setStats(updatedStats);
      })
      .catch((error) => {
        console.error('Failed to fetch dashboard stats:', error);
        toast.error('Failed to load dashboard stats');
      })
      .finally(() => setLoading(false));

    // Fetch recent tickets
    fetch('/api/tickets')
      .then((res) => res.json())
      .then((tickets) => {
        // Get most recent 5 tickets
        const recent = tickets.slice(0, 5).map((ticket: any) => ({
          id: ticket.id?.substring(0, 8) || 'N/A',
          customer: ticket.customer_name || ticket.email || 'Unknown',
          subject: ticket.subject || ticket.category || 'No subject',
          channel: ticket.channel === 'web_form' ? 'Web' : (ticket.channel || 'Email'),
          status: ticket.status === 'escalated' ? 'Escalated' : (ticket.status || 'Open'),
          priority: ticket.priority || 'Medium',
        }));
        setRecentTickets(recent);
      })
      .catch((error) => {
        console.error('Failed to fetch recent tickets:', error);
      });
  }, []);

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-darkest mb-2">Dashboard</h1>
        <p className="text-gray-medium">Welcome back! Here's what's happening today.</p>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-purple mx-auto"></div>
          <p className="text-gray-medium mt-4">Loading stats...</p>
        </div>
      )}

      {/* Stats Cards */}
      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, index) => (
          <div
            key={index}
            className="bg-white rounded-xl p-6 border-2 border-gray-light hover:border-primary-purple hover:shadow-lg transition-all"
          >
            <div className="flex items-center justify-between mb-4">
              <div
                className="w-12 h-12 rounded-lg flex items-center justify-center"
                style={{ background: `${stat.color}20` }}
              >
                <stat.icon className="w-6 h-6" style={{ color: stat.color }} />
              </div>
              <span
                className={`text-sm font-semibold ${
                  stat.trend === 'up' ? 'text-success' : 'text-primary-pink'
                }`}
              >
                {stat.change}
              </span>
            </div>
            <h3 className="text-3xl font-bold text-gray-darkest mb-1">{stat.value}</h3>
            <p className="text-gray-medium text-sm">{stat.label}</p>
          </div>
        ))}
      </div>
      )}

      {/* Recent Tickets */}
      <div className="bg-white rounded-xl border-2 border-gray-light p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-darkest">Recent Tickets</h2>
          <a
            href="/dashboard/tickets"
            className="text-primary-purple font-semibold hover:underline"
          >
            View All →
          </a>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-gray-light">
                <th className="text-left py-3 px-4 text-gray-dark font-semibold">Ticket ID</th>
                <th className="text-left py-3 px-4 text-gray-dark font-semibold">Customer</th>
                <th className="text-left py-3 px-4 text-gray-dark font-semibold">Subject</th>
                <th className="text-left py-3 px-4 text-gray-dark font-semibold">Channel</th>
                <th className="text-left py-3 px-4 text-gray-dark font-semibold">Priority</th>
                <th className="text-left py-3 px-4 text-gray-dark font-semibold">Status</th>
              </tr>
            </thead>
            <tbody>
              {recentTickets.map((ticket) => (
                <tr
                  key={ticket.id}
                  onClick={() => router.push('/dashboard/tickets')}
                  className="border-b border-gray-light hover:bg-purple-50 transition-colors cursor-pointer"
                >
                  <td className="py-4 px-4 font-mono text-sm text-primary-purple font-semibold">
                    {ticket.id}
                  </td>
                  <td className="py-4 px-4 text-gray-darkest">{ticket.customer}</td>
                  <td className="py-4 px-4 text-gray-dark">{ticket.subject}</td>
                  <td className="py-4 px-4">
                    <span className="px-3 py-1 rounded-full text-xs font-semibold bg-purple-100 text-primary-purple">
                      {ticket.channel}
                    </span>
                  </td>
                  <td className="py-4 px-4">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        ticket.priority === 'Urgent'
                          ? 'bg-red-100 text-red-600'
                          : ticket.priority === 'High'
                          ? 'bg-orange-100 text-orange-600'
                          : ticket.priority === 'Medium'
                          ? 'bg-blue-100 text-blue-600'
                          : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {ticket.priority}
                    </span>
                  </td>
                  <td className="py-4 px-4">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        ticket.status === 'Resolved'
                          ? 'bg-green-100 text-green-600'
                          : ticket.status === 'In Progress'
                          ? 'bg-blue-100 text-blue-600'
                          : 'bg-yellow-100 text-yellow-600'
                      }`}
                    >
                      {ticket.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
