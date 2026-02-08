import React, { useState } from 'react';
import SupportForm from './SupportForm';
import ConversationView from './ConversationView';

interface Message {
  role: 'customer' | 'agent';
  content: string;
  timestamp: Date;
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [status, setStatus] = useState<'idle' | 'waiting' | 'responded'>('idle');

  const handleSubmit = async (email: string, message: string, subject?: string) => {
    const sid = `${email}-${Date.now()}`;
    setSessionId(sid);
    setStatus('waiting');

    // Add customer message
    setMessages(prev => [...prev, {
      role: 'customer',
      content: message,
      timestamp: new Date(),
    }]);

    // Submit to API
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/webhooks/web_form`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, message, subject, session_id: sid }),
      });

      if (!response.ok) {
        throw new Error('Submission failed');
      }

      // Connect to SSE for response
      const eventSource = new EventSource(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/webhooks/web_form/stream/${sid}`
      );

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'response') {
            setMessages(prev => [...prev, {
              role: 'agent',
              content: data.content,
              timestamp: new Date(),
            }]);
            setStatus('responded');
            eventSource.close();
          }
        } catch {
          // ignore heartbeats
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        setStatus('responded');
      };

    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'agent',
        content: 'Sorry, something went wrong. Please try again.',
        timestamp: new Date(),
      }]);
      setStatus('responded');
    }
  };

  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <h1 style={styles.title}>CloudFlow Support</h1>
        <p style={styles.subtitle}>How can we help you today?</p>
      </header>

      <main style={styles.main}>
        {messages.length > 0 && (
          <ConversationView messages={messages} status={status} />
        )}
        <SupportForm onSubmit={handleSubmit} disabled={status === 'waiting'} />
      </main>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  app: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '24px 16px',
  },
  header: {
    textAlign: 'center',
    marginBottom: '24px',
  },
  title: {
    fontSize: '28px',
    fontWeight: '700',
    color: '#1a1a2e',
  },
  subtitle: {
    fontSize: '16px',
    color: '#666',
    marginTop: '8px',
  },
  main: {
    width: '100%',
    maxWidth: '680px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
};

export default App;
