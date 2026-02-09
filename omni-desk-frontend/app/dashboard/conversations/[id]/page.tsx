'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, User, Bot } from 'lucide-react';
import { colors, gradients } from '@/lib/colors';

interface Message {
  id: string;
  role: 'customer' | 'agent';
  content: string;
  timestamp: string;
}

export default function ConversationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const conversationId = params.id as string;

  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch messages for this conversation
    fetch(`/api/messages/${conversationId}`)
      .then((res) => res.json())
      .then((data) => {
        setMessages(Array.isArray(data) ? data : []);
      })
      .catch((error) => {
        console.error('Failed to fetch messages:', error);
        setMessages([]);
      })
      .finally(() => setLoading(false));
  }, [conversationId]);

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-8 flex items-center gap-4">
        <button
          onClick={() => router.back()}
          className="p-2 rounded-lg hover:bg-gray-lightest transition-colors"
        >
          <ArrowLeft className="w-6 h-6 text-gray-dark" />
        </button>
        <div>
          <h1 className="text-4xl font-bold text-gray-darkest mb-2">Conversation</h1>
          <p className="text-gray-medium font-mono text-sm">ID: {conversationId}</p>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-purple mx-auto"></div>
          <p className="text-gray-medium mt-4">Loading conversation...</p>
        </div>
      )}

      {/* Messages */}
      {!loading && (
        <div className="bg-white rounded-xl border-2 border-gray-light overflow-hidden">
          <div className="p-6 border-b-2 border-gray-light bg-gradient-to-r from-purple-50 to-white">
            <h2 className="text-xl font-bold text-gray-darkest">Message Thread</h2>
            <p className="text-sm text-gray-medium">{messages.length} messages</p>
          </div>

          {/* Messages List */}
          <div className="p-6 space-y-6 max-h-[600px] overflow-y-auto">
            {messages.length === 0 ? (
              <div className="text-center py-12 text-gray-medium">
                No messages in this conversation
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-4 ${
                    message.role === 'customer' ? 'flex-row' : 'flex-row-reverse'
                  }`}
                >
                  {/* Avatar */}
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
                    style={{
                      background:
                        message.role === 'customer'
                          ? 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)'
                          : gradients.primary,
                    }}
                  >
                    {message.role === 'customer' ? (
                      <User className="w-5 h-5 text-white" />
                    ) : (
                      <Bot className="w-5 h-5 text-white" />
                    )}
                  </div>

                  {/* Message Bubble */}
                  <div
                    className={`flex-1 ${
                      message.role === 'customer' ? 'pr-12' : 'pl-12'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-bold text-gray-darkest">
                        {message.role === 'customer' ? 'Customer' : 'AI Agent'}
                      </span>
                      <span className="text-xs text-gray-medium">
                        {formatTime(message.timestamp)}
                      </span>
                    </div>
                    <div
                      className={`p-4 rounded-xl ${
                        message.role === 'customer'
                          ? 'bg-blue-50 border-2 border-blue-200'
                          : 'bg-purple-50 border-2 border-purple-200'
                      }`}
                    >
                      <p className="text-gray-darkest leading-relaxed whitespace-pre-wrap">
                        {message.content}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="p-6 border-t-2 border-gray-light bg-gray-lightest">
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-medium">
                💬 This conversation is from your real submission
              </p>
              <button
                className="px-4 py-2 rounded-lg text-white font-semibold transition-all hover:scale-105"
                style={{ background: gradients.primary }}
              >
                Mark as Resolved
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
