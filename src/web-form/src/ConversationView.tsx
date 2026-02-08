import React, { useEffect, useRef } from 'react';

interface Message {
  role: 'customer' | 'agent';
  content: string;
  timestamp: Date;
}

interface ConversationViewProps {
  messages: Message[];
  status: 'idle' | 'waiting' | 'responded';
}

const ConversationView: React.FC<ConversationViewProps> = ({ messages, status }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <span style={styles.headerTitle}>Conversation</span>
        {status === 'waiting' && (
          <span style={styles.statusBadge}>Agent is typing...</span>
        )}
      </div>

      <div style={styles.messages}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              ...styles.message,
              ...(msg.role === 'customer' ? styles.customerMessage : styles.agentMessage),
            }}
          >
            <div style={styles.messageMeta}>
              <span style={styles.roleLabel}>
                {msg.role === 'customer' ? 'You' : 'CloudFlow Support'}
              </span>
              <span style={styles.timestamp}>
                {msg.timestamp.toLocaleTimeString()}
              </span>
            </div>
            <div style={styles.messageContent}>
              {msg.content.split('\n').map((line, i) => (
                <React.Fragment key={i}>
                  {line}
                  {i < msg.content.split('\n').length - 1 && <br />}
                </React.Fragment>
              ))}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    background: '#fff',
    borderRadius: '12px',
    boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
    overflow: 'hidden',
  },
  header: {
    padding: '16px 20px',
    borderBottom: '1px solid #eee',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerTitle: {
    fontWeight: '700',
    fontSize: '16px',
    color: '#1a1a2e',
  },
  statusBadge: {
    fontSize: '13px',
    color: '#4f46e5',
    fontStyle: 'italic',
  },
  messages: {
    padding: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    maxHeight: '400px',
    overflowY: 'auto',
  },
  message: {
    padding: '12px 16px',
    borderRadius: '10px',
    maxWidth: '85%',
  },
  customerMessage: {
    background: '#f0f4ff',
    alignSelf: 'flex-end',
    borderBottomRightRadius: '2px',
  },
  agentMessage: {
    background: '#f9fafb',
    border: '1px solid #e5e7eb',
    alignSelf: 'flex-start',
    borderBottomLeftRadius: '2px',
  },
  messageMeta: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '6px',
  },
  roleLabel: {
    fontSize: '12px',
    fontWeight: '600',
    color: '#555',
  },
  timestamp: {
    fontSize: '11px',
    color: '#999',
  },
  messageContent: {
    fontSize: '15px',
    lineHeight: '1.5',
    color: '#222',
    whiteSpace: 'pre-wrap' as const,
  },
};

export default ConversationView;
