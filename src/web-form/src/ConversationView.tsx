import React, { useEffect, useRef } from 'react';
import { colors, gradients } from './theme';

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
          <div style={styles.statusBadge}>
            <span style={styles.pulse}></span>
            <span>AI is thinking...</span>
          </div>
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
                {msg.role === 'customer' ? 'You' : '🤖 OmniDesk AI'}
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
    background: colors.white,
    borderRadius: '16px',
    boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
    overflow: 'hidden',
  },
  header: {
    padding: '20px 24px',
    borderBottom: `2px solid ${colors.gray.lightest}`,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    background: gradients.subtle,
  },
  headerTitle: {
    fontWeight: '700',
    fontSize: '18px',
    color: colors.gray.darkest,
  },
  statusBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '14px',
    color: colors.primary.purple,
    fontWeight: '600',
  },
  pulse: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    background: colors.primary.pink,
    animation: 'pulse 1.5s ease-in-out infinite',
  },
  messages: {
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
    maxHeight: '450px',
    overflowY: 'auto',
  },
  message: {
    padding: '14px 18px',
    borderRadius: '12px',
    maxWidth: '85%',
  },
  customerMessage: {
    background: `linear-gradient(135deg, ${colors.primary.pink}15 0%, ${colors.primary.purple}15 100%)`,
    border: `2px solid ${colors.primary.pink}30`,
    alignSelf: 'flex-end',
    borderBottomRightRadius: '4px',
  },
  agentMessage: {
    background: colors.gray.lightest,
    border: `2px solid ${colors.gray.light}`,
    alignSelf: 'flex-start',
    borderBottomLeftRadius: '4px',
  },
  messageMeta: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '8px',
    alignItems: 'center',
  },
  roleLabel: {
    fontSize: '13px',
    fontWeight: '700',
    color: colors.gray.dark,
  },
  timestamp: {
    fontSize: '12px',
    color: colors.gray.medium,
  },
  messageContent: {
    fontSize: '15px',
    lineHeight: '1.6',
    color: colors.gray.darkest,
    whiteSpace: 'pre-wrap' as const,
  },
};

export default ConversationView;
