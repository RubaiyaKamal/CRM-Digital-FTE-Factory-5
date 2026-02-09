'use client';

import { useState } from 'react';
import { Search, Filter } from 'lucide-react';
import { colors } from '@/lib/colors';

const allTickets = [
  { id: 'TKT-001', customer: 'John Doe', email: 'john@example.com', subject: 'Password reset issue', channel: 'Email', status: 'Open', priority: 'High', date: '2026-02-09' },
  { id: 'TKT-002', customer: 'Jane Smith', email: 'jane@example.com', subject: 'Billing question', channel: 'WhatsApp', status: 'In Progress', priority: 'Medium', date: '2026-02-09' },
  { id: 'TKT-003', customer: 'Bob Johnson', email: 'bob@example.com', subject: 'Feature request', channel: 'Web', status: 'Resolved', priority: 'Low', date: '2026-02-08' },
  { id: 'TKT-004', customer: 'Alice Brown', email: 'alice@example.com', subject: 'Bug report - app crashing', channel: 'Email', status: 'Open', priority: 'Urgent', date: '2026-02-09' },
  { id: 'TKT-005', customer: 'Charlie Wilson', email: 'charlie@example.com', subject: 'Account access problem', channel: 'WhatsApp', status: 'Resolved', priority: 'High', date: '2026-02-08' },
  { id: 'TKT-006', customer: 'Diana Prince', email: 'diana@example.com', subject: 'Integration help needed', channel: 'Web', status: 'In Progress', priority: 'Medium', date: '2026-02-09' },
  { id: 'TKT-007', customer: 'Ethan Hunt', email: 'ethan@example.com', subject: 'API documentation request', channel: 'Email', status: 'Open', priority: 'Low', date: '2026-02-09' },
  { id: 'TKT-008', customer: 'Fiona Gallagher', email: 'fiona@example.com', subject: 'Payment failed', channel: 'WhatsApp', status: 'Escalated', priority: 'Urgent', date: '2026-02-09' },
];

export default function TicketsPage() {
  const [filter, setFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredTickets = allTickets.filter((ticket) => {
    const matchesFilter = filter === 'All' || ticket.status === filter;
    const matchesSearch =
      ticket.customer.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ticket.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ticket.id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-darkest mb-2">Tickets</h1>
        <p className="text-gray-medium">Manage and track all customer support tickets</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border-2 border-gray-light p-6 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-medium" />
            <input
              type="text"
              placeholder="Search by customer, subject, or ticket ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-light focus:border-primary-purple focus:outline-none"
            />
          </div>

          {/* Status Filter Tabs */}
          <div className="flex gap-2 flex-wrap">
            {['All', 'Open', 'In Progress', 'Resolved', 'Escalated'].map((status) => (
              <button
                key={status}
                onClick={() => setFilter(status)}
                className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                  filter === status
                    ? 'bg-primary-purple text-white'
                    : 'bg-gray-lightest text-gray-dark hover:bg-purple-50'
                }`}
              >
                {status}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Tickets Table */}
      <div className="bg-white rounded-xl border-2 border-gray-light overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-lightest border-b-2 border-gray-light">
                <th className="text-left py-4 px-6 text-gray-darkest font-bold">Ticket ID</th>
                <th className="text-left py-4 px-6 text-gray-darkest font-bold">Customer</th>
                <th className="text-left py-4 px-6 text-gray-darkest font-bold">Subject</th>
                <th className="text-left py-4 px-6 text-gray-darkest font-bold">Channel</th>
                <th className="text-left py-4 px-6 text-gray-darkest font-bold">Priority</th>
                <th className="text-left py-4 px-6 text-gray-darkest font-bold">Status</th>
                <th className="text-left py-4 px-6 text-gray-darkest font-bold">Date</th>
              </tr>
            </thead>
            <tbody>
              {filteredTickets.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-gray-medium">
                    No tickets found matching your criteria
                  </td>
                </tr>
              ) : (
                filteredTickets.map((ticket) => (
                  <tr key={ticket.id} className="border-b border-gray-light hover:bg-purple-50 transition-colors cursor-pointer">
                    <td className="py-4 px-6 font-mono text-sm text-primary-purple font-bold">
                      {ticket.id}
                    </td>
                    <td className="py-4 px-6">
                      <div>
                        <p className="font-semibold text-gray-darkest">{ticket.customer}</p>
                        <p className="text-sm text-gray-medium">{ticket.email}</p>
                      </div>
                    </td>
                    <td className="py-4 px-6 text-gray-dark max-w-xs truncate">
                      {ticket.subject}
                    </td>
                    <td className="py-4 px-6">
                      <span className="px-3 py-1 rounded-full text-xs font-semibold bg-purple-100 text-primary-purple">
                        {ticket.channel}
                      </span>
                    </td>
                    <td className="py-4 px-6">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          ticket.priority === 'Urgent'
                            ? 'bg-red-100 text-red-600'
                            : ticket.priority === 'High'
                            ? 'bg-orange-100 text-orange-600'
                            : ticket.priority === 'Medium'
                            ? 'bg-blue-100 text-blue-600'
                            : 'bg-gray-200 text-gray-700'
                        }`}
                      >
                        {ticket.priority}
                      </span>
                    </td>
                    <td className="py-4 px-6">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          ticket.status === 'Resolved'
                            ? 'bg-green-100 text-green-600'
                            : ticket.status === 'In Progress'
                            ? 'bg-blue-100 text-blue-600'
                            : ticket.status === 'Escalated'
                            ? 'bg-red-100 text-red-600'
                            : 'bg-yellow-100 text-yellow-600'
                        }`}
                      >
                        {ticket.status}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-gray-medium text-sm">{ticket.date}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="px-6 py-4 border-t border-gray-light flex items-center justify-between">
          <p className="text-gray-medium text-sm">
            Showing {filteredTickets.length} of {allTickets.length} tickets
          </p>
          <div className="flex gap-2">
            <button className="px-4 py-2 rounded-lg border-2 border-gray-light text-gray-dark hover:border-primary-purple hover:text-primary-purple transition-all">
              Previous
            </button>
            <button className="px-4 py-2 rounded-lg bg-primary-purple text-white font-semibold">
              1
            </button>
            <button className="px-4 py-2 rounded-lg border-2 border-gray-light text-gray-dark hover:border-primary-purple hover:text-primary-purple transition-all">
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
