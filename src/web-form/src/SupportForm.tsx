import React, { useState } from 'react';

interface SupportFormProps {
  onSubmit: (email: string, message: string, subject?: string) => void;
  disabled?: boolean;
}

const SupportForm: React.FC<SupportFormProps> = ({ onSubmit, disabled }) => {
  const [email, setEmail] = useState('');
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = () => {
    const errs: Record<string, string> = {};
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errs.email = 'Please enter a valid email address';
    }
    if (!message.trim() || message.trim().length < 10) {
      errs.message = 'Please describe your issue (at least 10 characters)';
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onSubmit(email, message, subject || undefined);
      setMessage('');
      setSubject('');
    }
  };

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      <div style={styles.field}>
        <label style={styles.label}>Email *</label>
        <input
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder="your@email.com"
          style={{ ...styles.input, ...(errors.email ? styles.inputError : {}) }}
          disabled={disabled}
        />
        {errors.email && <span style={styles.error}>{errors.email}</span>}
      </div>

      <div style={styles.field}>
        <label style={styles.label}>Subject (optional)</label>
        <input
          type="text"
          value={subject}
          onChange={e => setSubject(e.target.value)}
          placeholder="What's this about?"
          style={styles.input}
          disabled={disabled}
        />
      </div>

      <div style={styles.field}>
        <label style={styles.label}>Message *</label>
        <textarea
          value={message}
          onChange={e => setMessage(e.target.value)}
          placeholder="Describe your issue or question..."
          rows={5}
          style={{ ...styles.input, ...styles.textarea, ...(errors.message ? styles.inputError : {}) }}
          disabled={disabled}
        />
        {errors.message && <span style={styles.error}>{errors.message}</span>}
      </div>

      <button type="submit" style={styles.button} disabled={disabled}>
        {disabled ? '⏳ Waiting for response...' : 'Send Message'}
      </button>
    </form>
  );
};

const styles: Record<string, React.CSSProperties> = {
  form: {
    background: '#fff',
    borderRadius: '12px',
    padding: '24px',
    boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  field: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  label: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#333',
  },
  input: {
    border: '1px solid #ddd',
    borderRadius: '8px',
    padding: '10px 12px',
    fontSize: '15px',
    outline: 'none',
    transition: 'border-color 0.2s',
  },
  inputError: {
    borderColor: '#e53e3e',
  },
  textarea: {
    resize: 'vertical' as const,
    minHeight: '100px',
  },
  error: {
    fontSize: '12px',
    color: '#e53e3e',
  },
  button: {
    background: '#4f46e5',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    padding: '12px 24px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'background 0.2s',
  },
};

export default SupportForm;
