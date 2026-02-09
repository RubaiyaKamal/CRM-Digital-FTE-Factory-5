'use client';

import { useState } from 'react';
import { Search, Mail, MessageSquare } from 'lucide-react';

const customers = [
  { name: 'John Doe', email: 'john@example.com', phone: '+1234567890', totalTickets: 8, lastContact: '2026-02-09', channels: ['Email', 'Web'] },
  { name: 'Jane Smith', email: 'jane@example.com', phone: '+1234567891', totalTickets: 12, lastContact: '2026-02-09', channels: ['WhatsApp', 'Email'] },
  { name: 'Bob Johnson', email: 'bob@example.com', phone: '+1234567892', totalTickets: 5, lastContact: '2026-02-08', channels: ['Web'] },
  { name: 'Alice Brown', email: 'alice@example.com', phone: '+1234567893', totalTickets: 15, lastContact: '2026-02-09', channels: ['Email', 'WhatsApp', 'Web'] },
  { name: 'Charlie Wilson', email: 'charlie@example.com', phone: '+1234567894', totalTickets: 7, lastContact: '2026-02-08', channels: ['WhatsApp'] },
  { name: 'Diana Prince', email: 'diana@example.com', phone: '+1234567895', totalTickets: 10, lastContact: '2026-02-09', channels: ['Email', 'Web'] },
];

export default function CustomersPage() {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredCustomers = customers.filter((customer) =>
    customer.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    customer.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-darkest mb-2">Customers</h1>
        <p className="text-gray-medium">View and manage your customer database</p>
      </div>

      {/* Search */}
      <div className="bg-white rounded-xl border-2 border-gray-light p-6 mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-medium" />
          <input
            type="text"
            placeholder="Search by name or email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-light focus:border-primary-purple focus:outline-none"
          />
        </div>
      </div>

      {/* Customers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCustomers.map((customer, index) => (
          <div
            key={index}
            className="bg-white rounded-xl border-2 border-gray-light p-6 hover:border-primary-purple hover:shadow-lg transition-all cursor-pointer"
          >
            {/* Avatar */}
            <div className="flex items-start gap-4 mb-4">
              <div
                className="w-14 h-14 rounded-full flex items-center justify-center text-white font-bold text-xl flex-shrink-0"
                style={{ background: 'linear-gradient(135deg, #E91E63 0%, #9C27B0 100%)' }}
              >
                {customer.name.split(' ').map(n => n[0]).join('')}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-bold text-gray-darkest truncate">{customer.name}</h3>
                <p className="text-sm text-gray-medium truncate">{customer.email}</p>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-2xl font-bold text-primary-purple">{customer.totalTickets}</p>
                <p className="text-xs text-gray-medium">Total Tickets</p>
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-darkest">{customer.lastContact}</p>
                <p className="text-xs text-gray-medium">Last Contact</p>
              </div>
            </div>

            {/* Channels */}
            <div className="mb-4">
              <p className="text-xs text-gray-medium mb-2">Channels Used</p>
              <div className="flex gap-2 flex-wrap">
                {customer.channels.map((channel, i) => (
                  <span
                    key={i}
                    className="px-2 py-1 rounded-full text-xs font-semibold bg-purple-100 text-primary-purple"
                  >
                    {channel}
                  </span>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <button className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-purple-50 text-primary-purple hover:bg-primary-purple hover:text-white transition-all">
                <Mail className="w-4 h-4" />
                <span className="text-sm font-semibold">Email</span>
              </button>
              <button className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-purple-50 text-primary-purple hover:bg-primary-purple hover:text-white transition-all">
                <MessageSquare className="w-4 h-4" />
                <span className="text-sm font-semibold">Chat</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredCustomers.length === 0 && (
        <div className="text-center py-12 text-gray-medium">
          No customers found matching your search
        </div>
      )}
    </div>
  );
}
