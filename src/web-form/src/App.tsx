import React, { useState } from 'react';
import MultiChannelContact, { ChannelFormData } from './MultiChannelContact';
import ConversationView from './ConversationView';
import { colors, gradients } from './theme';

interface Message {
  role: 'customer' | 'agent';
  content: string;
  timestamp: Date;
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [status, setStatus] = useState<'idle' | 'waiting' | 'responded'>('idle');

  const handleSubmit = async (formData: ChannelFormData) => {
    setStatus('waiting');

    // Build session ID and customer message based on channel
    let sid: string;
    let customerMessage: string;
    let payload: any;
    let webhookUrl: string;

    const apiBaseUrl = process.env.REACT_APP_API_URL || 'http://localhost:3000';

    if (formData.channel === 'email') {
      sid = `${formData.email}-${Date.now()}`;
      customerMessage = `Subject: ${formData.subject}\n\n${formData.body}`;
      payload = {
        from: formData.email,
        subject: formData.subject,
        body: formData.body,
        message: formData.body,
      };
      webhookUrl = `${apiBaseUrl}/webhooks/gmail`;
    } else if (formData.channel === 'whatsapp') {
      sid = `${formData.phone}-${Date.now()}`;
      customerMessage = formData.message;
      payload = {
        From: `whatsapp:${formData.phone}`,
        Body: formData.message,
        MessageSid: `WEB${Date.now()}`,
      };
      webhookUrl = `${apiBaseUrl}/webhooks/whatsapp`;
    } else {
      // web_form
      sid = `${formData.email}-${Date.now()}`;
      customerMessage = formData.message;
      payload = {
        email: formData.email,
        message: formData.message,
        subject: formData.subject || undefined,
        session_id: sid,
        name: formData.name,
        category: formData.category,
        priority: formData.priority,
      };
      webhookUrl = `${apiBaseUrl}/webhooks/web_form`;
    }

    setSessionId(sid);

    // Add customer message to UI
    setMessages(prev => [...prev, {
      role: 'customer',
      content: customerMessage,
      timestamp: new Date(),
    }]);

    // Submit to API
    try {
      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Submission failed');
      }

      const data = await response.json();
      const conversationId = data.conversation_id;

      // Connect to SSE for response (polls DB via conversation_id)
      const eventSource = new EventSource(
        `${apiBaseUrl}/webhooks/web_form/stream/${conversationId}`
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
          // ignore heartbeats and other non-JSON events
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
        <div style={styles.logo}>
          <div style={styles.logoIcon}>⚡</div>
          <h1 style={styles.title}>OmniDesk AI</h1>
        </div>
        <p style={styles.subtitle}>24/7 Customer Success Agent</p>
        <p style={styles.tagline}>Get instant answers to your questions, anytime</p>
      </header>

      <main style={styles.main}>
        {messages.length > 0 && (
          <ConversationView messages={messages} status={status} />
        )}
        <MultiChannelContact onSubmit={handleSubmit} disabled={status === 'waiting'} />
      </main>

      <footer style={styles.footer}>
        <p style={styles.footerText}>
          Powered by OmniDesk AI • Your data is secure and private
        </p>
      </footer>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  app: {
    minHeight: '100vh',
    background: `linear-gradient(180deg, ${colors.purple100} 0%, ${colors.purple50} 100%)`,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '32px 16px',
  },
  header: {
    textAlign: 'center',
    marginBottom: '40px',
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '12px',
    marginBottom: '12px',
  },
  logoIcon: {
    fontSize: '36px',
    background: gradients.primary,
    borderRadius: '12px',
    width: '56px',
    height: '56px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: '0 4px 12px rgba(233, 30, 99, 0.3)',
  },
  title: {
    fontSize: '42px',
    fontWeight: '800',
    background: gradients.primary,
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    margin: 0,
  },
  subtitle: {
    fontSize: '18px',
    color: colors.gray.dark,
    fontWeight: '600',
    marginTop: '8px',
    marginBottom: '4px',
  },
  tagline: {
    fontSize: '15px',
    color: colors.gray.medium,
  },
  main: {
    width: '100%',
    maxWidth: '1000px',
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
  },
  footer: {
    marginTop: '48px',
    textAlign: 'center',
  },
  footerText: {
    fontSize: '13px',
    color: colors.gray.medium,
  },
};

export default App;
