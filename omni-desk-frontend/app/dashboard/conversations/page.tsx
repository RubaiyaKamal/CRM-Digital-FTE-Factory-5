'use client';

import { useEffect, useState } from 'react';
import { Mail, MessageSquare, Globe } from 'lucide-react';

interface Conversation {
  id: string;
  customer: string;
  lastMessage: string;
  channel: string;
  time: string;
  unread: number;
}

const demoConversations: Conversation[] = [
  {
    id: 'CONV-001',
    customer: 'John Doe',
    lastMessage: 'Thanks for the help! Issue resolved.',
    channel: 'Email',
    time: '2 min ago',
    unread: 0,
  },
  {
    id: 'CONV-002',
    customer: 'Jane Smith',
    lastMessage: 'Can you explain the billing cycle?',
    channel: 'WhatsApp',
    time: '15 min ago',
    unread: 2,
  },
  {
    id: 'CONV-003',
    customer: 'Bob Johnson',
    lastMessage: 'I submitted a feature request.',
    channel: 'Web',
    time: '1 hour ago',
    unread: 0,
  },
  {
    id: 'CONV-004',
    customer: 'Alice Brown',
    lastMessage: 'The app is crashing when I try to export data.',
    channel: 'Email',
    time: '3 hours ago',
    unread: 1,
  },
  {
    id: 'CONV-005',
    customer: 'Charlie Wilson',
    lastMessage: 'Perfect, my account is working now!',
    channel: 'WhatsApp',
    time: 'Yesterday',
    unread: 0,
  },
];

const getChannelIcon = (channel: string) => {
  switch (channel) {
    case 'Email':
      return <Mail className="w-5 h-5" />;
    case 'WhatsApp':
      return <MessageSquare className="w-5 h-5" />;
    case 'Web':
      return <Globe className="w-5 h-5" />;
    default:
      return <MessageSquare className="w-5 h-5" />;
  }
};

export default function ConversationsPage() {
  const [realConversations, setRealConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch real conversations from API
    fetch('/api/conversations')
      .then((res) => res.json())
      .then((data) => {
        // Transform API data to match our format
        const transformed = Array.isArray(data) ? data.map((conv: any) => ({
          id: conv.conversation_id || conv.id,
          customer: conv.customer_name || conv.email || 'Unknown Customer',
          lastMessage: conv.last_message || conv.message || 'New conversation',
          channel: conv.channel === 'web_form' ? 'Web' : conv.channel || 'Web',
          time: formatTime(conv.created_at || conv.timestamp),
          unread: 0,
        })) : [];
        setRealConversations(transformed);
      })
      .catch((error) => {
        console.error('Failed to fetch conversations:', error);
        setRealConversations([]);
      })
      .finally(() => setLoading(false));
  }, []);

  const formatTime = (timestamp: string) => {
    if (!timestamp) return 'Just now';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    return 'Yesterday';
  };

  // Combine real and demo conversations (real first)
  const allConversations = [...realConversations, ...demoConversations];

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-darkest mb-2">Conversations</h1>
        <p className="text-gray-medium">
          View all customer conversations across channels
          {realConversations.length > 0 && (
            <span className="ml-2 px-3 py-1 rounded-full bg-green-100 text-green-600 text-sm font-semibold">
              {realConversations.length} Real
            </span>
          )}
          <span className="ml-2 px-3 py-1 rounded-full bg-purple-100 text-primary-purple text-sm font-semibold">
            {demoConversations.length} Demo
          </span>
        </p>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-purple mx-auto"></div>
          <p className="text-gray-medium mt-4">Loading conversations...</p>
        </div>
      )}

      {/* Conversations List */}
      {!loading && (
        <div className="bg-white rounded-xl border-2 border-gray-light overflow-hidden">
          {allConversations.map((conv, index) => {
            const isReal = index < realConversations.length;
            return (
              <div
                key={conv.id}
                className={`p-6 border-b border-gray-light hover:bg-purple-50 transition-colors cursor-pointer ${
                  index === allConversations.length - 1 ? 'border-b-0' : ''
                } ${isReal ? 'bg-green-50' : ''}`}
              >
                <div className="flex items-start gap-4">
                  {/* Avatar + Channel */}
                  <div className="relative flex-shrink-0">
                    <div
                      className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg"
                      style={{ background: isReal ? 'linear-gradient(135deg, #66BB6A 0%, #4CAF50 100%)' : 'linear-gradient(135deg, #E91E63 0%, #9C27B0 100%)' }}
                    >
                      {conv.customer.split(' ').map(n => n[0]).join('')}
                    </div>
                    {/* Channel Badge */}
                    <div
                      className="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-white flex items-center justify-center border-2 border-white"
                      style={{ color: '#9C27B0' }}
                    >
                      {getChannelIcon(conv.channel)}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-bold text-gray-darkest">{conv.customer}</h3>
                        {isReal && (
                          <span className="px-2 py-0.5 rounded-full bg-green-500 text-white text-xs font-semibold">
                            REAL
                          </span>
                        )}
                      </div>
                      <span className="text-sm text-gray-medium">{conv.time}</span>
                    </div>
                    <p className="text-sm text-gray-dark truncate mb-2">{conv.lastMessage}</p>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono text-gray-medium">{conv.id}</span>
                      <span className="text-xs px-2 py-1 rounded-full bg-purple-100 text-primary-purple font-semibold">
                        {conv.channel}
                      </span>
                      {conv.unread > 0 && (
                        <span className="text-xs px-2 py-1 rounded-full bg-red-500 text-white font-semibold">
                          {conv.unread} new
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Empty State */}
      {!loading && allConversations.length === 0 && (
        <div className="bg-white rounded-xl border-2 border-gray-light p-12 text-center">
          <MessageSquare className="w-16 h-16 mx-auto mb-4 text-gray-light" />
          <h3 className="text-xl font-bold text-gray-darkest mb-2">No conversations yet</h3>
          <p className="text-gray-medium">
            Conversations will appear here when customers contact support
          </p>
        </div>
      )}
    </div>
  );
}
