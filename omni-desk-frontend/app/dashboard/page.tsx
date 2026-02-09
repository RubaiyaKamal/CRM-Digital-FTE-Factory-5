'use client';

import { TrendingUp, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { colors, gradients } from '@/lib/colors';

const stats = [
  {
    label: 'Total Tickets',
    value: '1,234',
    change: '+12%',
    trend: 'up',
    icon: TrendingUp,
    color: colors.primary.purple,
  },
  {
    label: 'Open Tickets',
    value: '156',
    change: '+8',
    trend: 'up',
    icon: AlertCircle,
    color: colors.warning,
  },
  {
    label: 'Resolved Today',
    value: '89',
    change: '+15%',
    trend: 'up',
    icon: CheckCircle,
    color: colors.success,
  },
  {
    label: 'Avg Response Time',
    value: '1.8s',
    change: '-0.3s',
    trend: 'down',
    icon: Clock,
    color: colors.primary.pink,
  },
];

const recentTickets = [
  { id: 'TKT-001', customer: 'John Doe', subject: 'Password reset issue', channel: 'Email', status: 'Open', priority: 'High' },
  { id: 'TKT-002', customer: 'Jane Smith', subject: 'Billing question', channel: 'WhatsApp', status: 'In Progress', priority: 'Medium' },
  { id: 'TKT-003', customer: 'Bob Johnson', subject: 'Feature request', channel: 'Web', status: 'Resolved', priority: 'Low' },
  { id: 'TKT-004', customer: 'Alice Brown', subject: 'Bug report', channel: 'Email', status: 'Open', priority: 'Urgent' },
  { id: 'TKT-005', customer: 'Charlie Wilson', subject: 'Account access', channel: 'WhatsApp', status: 'Resolved', priority: 'High' },
];

export default function DashboardPage() {
  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-darkest mb-2">Dashboard</h1>
        <p className="text-gray-medium">Welcome back! Here's what's happening today.</p>
      </div>

      {/* Stats Cards */}
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
                <tr key={ticket.id} className="border-b border-gray-light hover:bg-purple-50 transition-colors">
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
