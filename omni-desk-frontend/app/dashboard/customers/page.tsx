'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Search, Mail, MessageSquare, ExternalLink } from 'lucide-react';
import toast from 'react-hot-toast';
import ErrorState from '@/components/ErrorState';
import LoadingSpinner from '@/components/LoadingSpinner';

interface Customer {
  id?: string;
  name: string;
  email: string;
  phone: string;
  totalTickets: number;
  lastContact: string;
  channels: string[];
}

const demoCustomers: Customer[] = [
  { name: 'John Doe', email: 'john@example.com', phone: '+1234567890', totalTickets: 8, lastContact: '2026-02-09', channels: ['Email', 'Web'] },
  { name: 'Jane Smith', email: 'jane@example.com', phone: '+1234567891', totalTickets: 12, lastContact: '2026-02-09', channels: ['WhatsApp', 'Email'] },
  { name: 'Bob Johnson', email: 'bob@example.com', phone: '+1234567892', totalTickets: 5, lastContact: '2026-02-08', channels: ['Web'] },
  { name: 'Alice Brown', email: 'alice@example.com', phone: '+1234567893', totalTickets: 15, lastContact: '2026-02-09', channels: ['Email', 'WhatsApp', 'Web'] },
  { name: 'Charlie Wilson', email: 'charlie@example.com', phone: '+1234567894', totalTickets: 7, lastContact: '2026-02-08', channels: ['WhatsApp'] },
  { name: 'Diana Prince', email: 'diana@example.com', phone: '+1234567895', totalTickets: 10, lastContact: '2026-02-09', channels: ['Email', 'Web'] },
];

export default function CustomersPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [realCustomers, setRealCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(12);

  const fetchCustomers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/customers');
      if (!res.ok) {
        throw new Error(`Failed to fetch customers: ${res.statusText}`);
      }
      const data = await res.json();
      setRealCustomers(Array.isArray(data) ? data : []);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch customers';
      console.error('Failed to fetch customers:', err);
      setError(errorMessage);
      toast.error(errorMessage);
      setRealCustomers([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, []);

  // Combine real and demo customers
  const allCustomers = [...realCustomers, ...demoCustomers];

  const filteredCustomers = allCustomers.filter((customer) => {
    const query = searchQuery.toLowerCase();
    const name = customer.name || customer.phone || 'Unknown';
    const email = customer.email || '';
    return name.toLowerCase().includes(query) || email.toLowerCase().includes(query);
  });

  // Pagination calculations
  const totalPages = Math.ceil(filteredCustomers.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedCustomers = filteredCustomers.slice(startIndex, endIndex);

  // Reset to page 1 when search changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, pageSize]);

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-darkest mb-2">Customers</h1>
        <p className="text-gray-medium">
          View and manage your customer database
          {realCustomers.length > 0 && (
            <span className="ml-2 px-3 py-1 rounded-full bg-green-100 text-green-600 text-sm font-semibold">
              {realCustomers.length} Real
            </span>
          )}
          <span className="ml-2 px-3 py-1 rounded-full bg-purple-100 text-primary-purple text-sm font-semibold">
            {demoCustomers.length} Demo
          </span>
        </p>
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

      {/* Loading */}
      {loading && <LoadingSpinner message="Loading customers..." />}

      {/* Error State */}
      {!loading && error && (
        <ErrorState
          message={error}
          onRetry={fetchCustomers}
          retrying={loading}
        />
      )}

      {/* Customers Grid */}
      {!loading && !error && (
        <>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
          {paginatedCustomers.map((customer, index) => {
            const isReal = allCustomers.indexOf(customer) < realCustomers.length;
            const conversationId = customer.email === 'kh0102267@gmail.com'
              ? '2251c0bb-65a9-4ae3-8b5e-6085453f26fd'
              : null;

            return (
              <div
                key={index}
                className={`bg-white rounded-xl border-2 border-gray-light p-6 hover:border-primary-purple hover:shadow-lg transition-all cursor-pointer ${
                  isReal ? 'ring-2 ring-green-200' : ''
                }`}
              >
                {/* Avatar */}
                <div className="flex items-start gap-4 mb-4">
                  <div
                    className="w-14 h-14 rounded-full flex items-center justify-center text-white font-bold text-xl flex-shrink-0"
                    style={{
                      background: isReal
                        ? 'linear-gradient(135deg, #66BB6A 0%, #4CAF50 100%)'
                        : 'linear-gradient(135deg, #E91E63 0%, #9C27B0 100%)'
                    }}
                  >
                    {(customer.name || customer.phone || 'U').split(' ').map(n => n[0]).join('').substring(0, 2)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-lg font-bold text-gray-darkest truncate">{customer.name || customer.phone || 'Unknown'}</h3>
                      {isReal && (
                        <span className="px-2 py-0.5 rounded-full bg-green-500 text-white text-xs font-semibold">
                          REAL
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-medium truncate">{customer.email || customer.phone || 'No contact info'}</p>
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
                  {customer.id ? (
                    <>
                      <Link
                        href={`/dashboard/conversations?customer=${customer.id}`}
                        className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-green-500 text-white hover:bg-green-600 transition-all font-semibold"
                      >
                        <MessageSquare className="w-4 h-4" />
                        <span className="text-sm">View Chat</span>
                      </Link>
                      <a
                        href={`mailto:${customer.email}`}
                        className="flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white transition-all"
                      >
                        <Mail className="w-4 h-4" />
                      </a>
                    </>
                  ) : (
                    <>
                      <button className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-purple-50 text-primary-purple hover:bg-primary-purple hover:text-white transition-all">
                        <Mail className="w-4 h-4" />
                        <span className="text-sm font-semibold">Email</span>
                      </button>
                      <button className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-purple-50 text-primary-purple hover:bg-primary-purple hover:text-white transition-all">
                        <MessageSquare className="w-4 h-4" />
                        <span className="text-sm font-semibold">Chat</span>
                      </button>
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Pagination */}
        {filteredCustomers.length > 0 && (
          <div className="bg-white rounded-xl border-2 border-gray-light p-6">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              {/* Results Info & Page Size */}
              <div className="flex items-center gap-4 text-sm">
                <p className="text-gray-medium">
                  Showing {startIndex + 1}-{Math.min(endIndex, filteredCustomers.length)} of {filteredCustomers.length} customers
                </p>
                <select
                  value={pageSize}
                  onChange={(e) => setPageSize(Number(e.target.value))}
                  className="px-3 py-1 rounded-lg border-2 border-gray-light focus:border-primary-purple focus:outline-none text-gray-darkest"
                >
                  <option value={6}>6 per page</option>
                  <option value={12}>12 per page</option>
                  <option value={24}>24 per page</option>
                  <option value={48}>48 per page</option>
                </select>
              </div>

              {/* Page Navigation */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="px-4 py-2 rounded-lg border-2 border-gray-light text-gray-dark hover:border-primary-purple hover:text-primary-purple transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>

                {/* Page Numbers */}
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (currentPage <= 3) {
                    pageNum = i + 1;
                  } else if (currentPage >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = currentPage - 2 + i;
                  }

                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                        currentPage === pageNum
                          ? 'bg-primary-purple text-white'
                          : 'border-2 border-gray-light text-gray-dark hover:border-primary-purple hover:text-primary-purple'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}

                <button
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 rounded-lg border-2 border-gray-light text-gray-dark hover:border-primary-purple hover:text-primary-purple transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        )}
        </>
      )}

      {!loading && filteredCustomers.length === 0 && (
        <div className="text-center py-12 text-gray-medium">
          No customers found matching your search
        </div>
      )}
    </div>
  );
}
