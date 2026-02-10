import React, { useState } from 'react';
import { colors, gradients } from './theme';

interface MultiChannelContactProps {
  onSubmit: (data: ChannelFormData) => void;
  disabled?: boolean;
}

type Channel = 'email' | 'whatsapp' | 'web_form';

interface BaseFormData {
  channel: Channel;
}

interface EmailFormData extends BaseFormData {
  channel: 'email';
  email: string;
  subject: string;
  body: string;
}

interface WhatsAppFormData extends BaseFormData {
  channel: 'whatsapp';
  phone: string;
  message: string;
}

interface WebFormData extends BaseFormData {
  channel: 'web_form';
  name: string;
  email: string;
  subject: string;
  category: string;
  priority: string;
  message: string;
}

export type ChannelFormData = EmailFormData | WhatsAppFormData | WebFormData;

const categories = [
  { value: 'technical', label: 'Technical Issue' },
  { value: 'billing', label: 'Billing & Payments' },
  { value: 'how-to', label: 'How-To Question' },
  { value: 'feature-request', label: 'Feature Request' },
  { value: 'bug-report', label: 'Bug Report' },
  { value: 'other', label: 'Other' },
];

const priorities = [
  { value: 'low', label: 'Low - Not urgent' },
  { value: 'medium', label: 'Medium - Normal priority' },
  { value: 'high', label: 'High - Important' },
  { value: 'urgent', label: 'Urgent - Critical issue' },
];

const MultiChannelContact: React.FC<MultiChannelContactProps> = ({ onSubmit, disabled = false }) => {
  const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null);
  const [emailForm, setEmailForm] = useState({ email: '', subject: '', body: '' });
  const [whatsappForm, setWhatsappForm] = useState({ phone: '', message: '' });
  const [webForm, setWebForm] = useState({
    name: '',
    email: '',
    subject: '',
    category: 'how-to',
    priority: 'medium',
    message: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateEmail = (email: string): boolean => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  };

  const validatePhone = (phone: string): boolean => {
    const regex = /^\+?[1-9]\d{1,14}$/;
    return regex.test(phone.replace(/[\s\-\(\)]/g, ''));
  };

  const validateEmailForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!validateEmail(emailForm.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    if (!emailForm.subject || emailForm.subject.length < 3) {
      newErrors.subject = 'Subject must be at least 3 characters';
    }
    if (!emailForm.body || emailForm.body.length < 10) {
      newErrors.body = 'Message must be at least 10 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateWhatsAppForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!validatePhone(whatsappForm.phone)) {
      newErrors.phone = 'Please enter a valid phone number with country code (e.g., +1234567890)';
    }
    if (!whatsappForm.message || whatsappForm.message.length < 10) {
      newErrors.message = 'Message must be at least 10 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateWebForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!webForm.name || webForm.name.length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }
    if (!validateEmail(webForm.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    if (!webForm.message || webForm.message.length < 10) {
      newErrors.message = 'Message must be at least 10 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (disabled) return;

    let isValid = false;
    let formData: ChannelFormData | null = null;

    if (selectedChannel === 'email') {
      isValid = validateEmailForm();
      if (isValid) {
        formData = { channel: 'email', ...emailForm };
      }
    } else if (selectedChannel === 'whatsapp') {
      isValid = validateWhatsAppForm();
      if (isValid) {
        formData = { channel: 'whatsapp', ...whatsappForm };
      }
    } else if (selectedChannel === 'web_form') {
      isValid = validateWebForm();
      if (isValid) {
        formData = { channel: 'web_form', ...webForm };
      }
    }

    if (isValid && formData) {
      onSubmit(formData);
    }
  };

  const renderChannelSelector = () => (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Contact Our AI Assistant</h1>
        <p style={styles.subtitle}>Reach us through your preferred channel. Our AI agent is available 24/7 to assist you.</p>
      </div>

      <h3 style={styles.sectionTitle}>Choose Your Preferred Channel</h3>

      <div style={styles.channelGrid}>
        <button
          type="button"
          onClick={() => setSelectedChannel('email')}
          style={styles.channelCard}
        >
          <div style={styles.channelIcon}>
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke={colors.primary.purple} strokeWidth="2">
              <rect x="3" y="5" width="18" height="14" rx="2" />
              <path d="M3 7l9 6 9-6" />
            </svg>
          </div>
          <h4 style={styles.channelTitle}>Email</h4>
          <p style={styles.channelDesc}>Send us an email and get a detailed response</p>
        </button>

        <button
          type="button"
          onClick={() => setSelectedChannel('whatsapp')}
          style={styles.channelCard}
        >
          <div style={styles.channelIcon}>
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke={colors.success} strokeWidth="2">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
            </svg>
          </div>
          <h4 style={styles.channelTitle}>WhatsApp</h4>
          <p style={styles.channelDesc}>Chat with us instantly on WhatsApp</p>
        </button>

        <button
          type="button"
          onClick={() => setSelectedChannel('web_form')}
          style={styles.channelCard}
        >
          <div style={styles.channelIcon}>
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke={colors.primary.blue} strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="2" y1="12" x2="22" y2="12" />
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
            </svg>
          </div>
          <h4 style={styles.channelTitle}>Web Form</h4>
          <p style={styles.channelDesc}>Fill out our form for structured support</p>
        </button>
      </div>
    </div>
  );

  const renderEmailForm = () => (
    <div style={styles.container}>
      <button
        type="button"
        onClick={() => setSelectedChannel(null)}
        style={styles.backButton}
      >
        \u2190 Back to Channel Selection
      </button>

      <div style={styles.formCard}>
        <div style={styles.formHeader}>
          <h2 style={styles.formTitle}>Email Support</h2>
          <p style={styles.formSubtitle}>Send us an email and we'll respond as soon as possible</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={styles.field}>
            <label style={styles.label}>
              Email Address <span style={styles.required}>*</span>
            </label>
            <input
              type="email"
              value={emailForm.email}
              onChange={(e) => {
                setEmailForm({ ...emailForm, email: e.target.value });
                setErrors({ ...errors, email: '' });
              }}
              placeholder="your.email@example.com"
              disabled={disabled}
              style={{ ...styles.input, ...(errors.email ? styles.inputError : {}) }}
            />
            {errors.email && <span style={styles.errorText}>{errors.email}</span>}
          </div>

          <div style={styles.field}>
            <label style={styles.label}>
              Subject <span style={styles.required}>*</span>
            </label>
            <input
              type="text"
              value={emailForm.subject}
              onChange={(e) => {
                setEmailForm({ ...emailForm, subject: e.target.value });
                setErrors({ ...errors, subject: '' });
              }}
              placeholder="Brief description of your issue"
              disabled={disabled}
              style={{ ...styles.input, ...(errors.subject ? styles.inputError : {}) }}
            />
            {errors.subject && <span style={styles.errorText}>{errors.subject}</span>}
          </div>

          <div style={styles.field}>
            <label style={styles.label}>
              Message <span style={styles.required}>*</span>
            </label>
            <textarea
              value={emailForm.body}
              onChange={(e) => {
                setEmailForm({ ...emailForm, body: e.target.value });
                setErrors({ ...errors, body: '' });
              }}
              placeholder="Describe your issue or question in detail..."
              disabled={disabled}
              rows={6}
              style={{ ...styles.textarea, ...(errors.body ? styles.inputError : {}) }}
            />
            {errors.body && <span style={styles.errorText}>{errors.body}</span>}
          </div>

          <button
            type="submit"
            disabled={disabled}
            style={{ ...styles.submitButton, ...(disabled ? styles.submitButtonDisabled : {}) }}
          >
            {disabled ? 'Sending...' : 'Send Email'}
          </button>
        </form>
      </div>
    </div>
  );

  const renderWhatsAppForm = () => (
    <div style={styles.container}>
      <button
        type="button"
        onClick={() => setSelectedChannel(null)}
        style={styles.backButton}
      >
        \u2190 Back to Channel Selection
      </button>

      <div style={styles.formCard}>
        <div style={styles.formHeader}>
          <h2 style={styles.formTitle}>WhatsApp Support</h2>
          <p style={styles.formSubtitle}>Chat with us instantly via WhatsApp</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={styles.field}>
            <label style={styles.label}>
              Phone Number <span style={styles.required}>*</span>
            </label>
            <input
              type="tel"
              value={whatsappForm.phone}
              onChange={(e) => {
                setWhatsappForm({ ...whatsappForm, phone: e.target.value });
                setErrors({ ...errors, phone: '' });
              }}
              placeholder="+1234567890"
              disabled={disabled}
              style={{ ...styles.input, ...(errors.phone ? styles.inputError : {}) }}
            />
            <span style={styles.helpText}>Include country code (e.g., +1 for US)</span>
            {errors.phone && <span style={styles.errorText}>{errors.phone}</span>}
          </div>

          <div style={styles.field}>
            <label style={styles.label}>
              Message <span style={styles.required}>*</span>
            </label>
            <textarea
              value={whatsappForm.message}
              onChange={(e) => {
                setWhatsappForm({ ...whatsappForm, message: e.target.value });
                setErrors({ ...errors, message: '' });
              }}
              placeholder="What can we help you with?"
              disabled={disabled}
              rows={6}
              maxLength={1600}
              style={{ ...styles.textarea, ...(errors.message ? styles.inputError : {}) }}
            />
            <div style={styles.charCount}>
              <span>{whatsappForm.message.length} / 1600 characters</span>
            </div>
            {errors.message && <span style={styles.errorText}>{errors.message}</span>}
          </div>

          <button
            type="submit"
            disabled={disabled}
            style={{ ...styles.submitButton, ...(disabled ? styles.submitButtonDisabled : {}) }}
          >
            {disabled ? 'Sending...' : 'Send WhatsApp Message'}
          </button>
        </form>
      </div>
    </div>
  );

  const renderWebForm = () => (
    <div style={styles.container}>
      <button
        type="button"
        onClick={() => setSelectedChannel(null)}
        style={styles.backButton}
      >
        \u2190 Back to Channel Selection
      </button>

      <div style={styles.formCard}>
        <div style={styles.formHeader}>
          <h2 style={styles.formTitle}>Submit Support Request</h2>
          <p style={styles.formSubtitle}>Fill out the form below and our AI-powered support team will get back to you</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={styles.row}>
            <div style={styles.field}>
              <label style={styles.label}>
                Your Name <span style={styles.required}>*</span>
              </label>
              <input
                type="text"
                value={webForm.name}
                onChange={(e) => {
                  setWebForm({ ...webForm, name: e.target.value });
                  setErrors({ ...errors, name: '' });
                }}
                placeholder="John Doe"
                disabled={disabled}
                style={{ ...styles.input, ...(errors.name ? styles.inputError : {}) }}
              />
              {errors.name && <span style={styles.errorText}>{errors.name}</span>}
            </div>

            <div style={styles.field}>
              <label style={styles.label}>
                Email Address <span style={styles.required}>*</span>
              </label>
              <input
                type="email"
                value={webForm.email}
                onChange={(e) => {
                  setWebForm({ ...webForm, email: e.target.value });
                  setErrors({ ...errors, email: '' });
                }}
                placeholder="john@example.com"
                disabled={disabled}
                style={{ ...styles.input, ...(errors.email ? styles.inputError : {}) }}
              />
              {errors.email && <span style={styles.errorText}>{errors.email}</span>}
            </div>
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Subject</label>
            <input
              type="text"
              value={webForm.subject}
              onChange={(e) => setWebForm({ ...webForm, subject: e.target.value })}
              placeholder="Brief description of your issue"
              disabled={disabled}
              style={styles.input}
            />
          </div>

          <div style={styles.row}>
            <div style={styles.field}>
              <label style={styles.label}>
                Category <span style={styles.required}>*</span>
              </label>
              <select
                value={webForm.category}
                onChange={(e) => setWebForm({ ...webForm, category: e.target.value })}
                disabled={disabled}
                style={styles.select}
              >
                {categories.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            <div style={styles.field}>
              <label style={styles.label}>
                Priority <span style={styles.required}>*</span>
              </label>
              <select
                value={webForm.priority}
                onChange={(e) => setWebForm({ ...webForm, priority: e.target.value })}
                disabled={disabled}
                style={styles.select}
              >
                {priorities.map((pri) => (
                  <option key={pri.value} value={pri.value}>
                    {pri.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div style={styles.field}>
            <label style={styles.label}>
              Message <span style={styles.required}>*</span>
            </label>
            <textarea
              value={webForm.message}
              onChange={(e) => {
                setWebForm({ ...webForm, message: e.target.value });
                setErrors({ ...errors, message: '' });
              }}
              placeholder="Describe your issue or question in detail..."
              disabled={disabled}
              rows={6}
              maxLength={1000}
              style={{ ...styles.textarea, ...(errors.message ? styles.inputError : {}) }}
            />
            <div style={styles.charCount}>
              <span>{webForm.message.length} / 1000 characters</span>
            </div>
            {errors.message && <span style={styles.errorText}>{errors.message}</span>}
          </div>

          <button
            type="submit"
            disabled={disabled}
            style={{ ...styles.submitButton, ...(disabled ? styles.submitButtonDisabled : {}) }}
          >
            {disabled ? 'Sending...' : 'Send Message'}
          </button>
        </form>
      </div>
    </div>
  );

  if (!selectedChannel) {
    return renderChannelSelector();
  }

  if (selectedChannel === 'email') {
    return renderEmailForm();
  }

  if (selectedChannel === 'whatsapp') {
    return renderWhatsAppForm();
  }

  return renderWebForm();
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: '900px',
    margin: '0 auto',
    padding: '40px 20px',
  },
  header: {
    textAlign: 'center',
    marginBottom: '48px',
  },
  title: {
    fontSize: '36px',
    fontWeight: '800',
    background: gradients.primary,
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    marginBottom: '16px',
  },
  subtitle: {
    fontSize: '16px',
    color: colors.gray.medium,
    lineHeight: '1.6',
  },
  sectionTitle: {
    fontSize: '20px',
    fontWeight: '700',
    color: colors.gray.dark,
    marginBottom: '24px',
    textAlign: 'center',
  },
  channelGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '24px',
    marginBottom: '40px',
  },
  channelCard: {
    background: colors.white,
    border: `2px solid ${colors.gray.light}`,
    borderRadius: '16px',
    padding: '32px 24px',
    textAlign: 'center',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)',
  },
  channelIcon: {
    marginBottom: '16px',
    display: 'flex',
    justifyContent: 'center',
  },
  channelTitle: {
    fontSize: '20px',
    fontWeight: '700',
    color: colors.gray.dark,
    marginBottom: '8px',
  },
  channelDesc: {
    fontSize: '14px',
    color: colors.gray.medium,
    lineHeight: '1.5',
  },
  backButton: {
    background: 'transparent',
    border: 'none',
    color: colors.primary.purple,
    fontSize: '15px',
    fontWeight: '600',
    cursor: 'pointer',
    marginBottom: '24px',
    padding: '8px 0',
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
  },
  formCard: {
    background: colors.white,
    borderRadius: '16px',
    padding: '32px',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
  },
  formHeader: {
    marginBottom: '32px',
    textAlign: 'center',
  },
  formTitle: {
    fontSize: '28px',
    fontWeight: '700',
    background: gradients.primary,
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    marginBottom: '8px',
  },
  formSubtitle: {
    fontSize: '15px',
    color: colors.gray.medium,
  },
  row: {
    display: 'flex',
    gap: '16px',
    marginBottom: '20px',
  },
  field: {
    flex: 1,
    marginBottom: '20px',
    display: 'flex',
    flexDirection: 'column',
  },
  label: {
    fontSize: '14px',
    fontWeight: '600',
    color: colors.gray.dark,
    marginBottom: '8px',
  },
  required: {
    color: colors.primary.pink,
  },
  input: {
    padding: '12px 16px',
    fontSize: '15px',
    border: `2px solid ${colors.gray.light}`,
    borderRadius: '10px',
    outline: 'none',
    transition: 'border-color 0.2s',
    fontFamily: 'inherit',
  },
  inputError: {
    borderColor: colors.error,
  },
  select: {
    padding: '12px 16px',
    fontSize: '15px',
    border: `2px solid ${colors.gray.light}`,
    borderRadius: '10px',
    outline: 'none',
    cursor: 'pointer',
    backgroundColor: colors.white,
    fontFamily: 'inherit',
  },
  textarea: {
    padding: '12px 16px',
    fontSize: '15px',
    border: `2px solid ${colors.gray.light}`,
    borderRadius: '10px',
    outline: 'none',
    resize: 'vertical',
    fontFamily: 'inherit',
    transition: 'border-color 0.2s',
  },
  helpText: {
    fontSize: '13px',
    color: colors.gray.medium,
    marginTop: '4px',
  },
  charCount: {
    marginTop: '4px',
    fontSize: '13px',
    color: colors.gray.medium,
    textAlign: 'right',
  },
  errorText: {
    color: colors.error,
    fontSize: '13px',
    marginTop: '4px',
  },
  submitButton: {
    width: '100%',
    padding: '16px',
    fontSize: '16px',
    fontWeight: '600',
    color: colors.white,
    background: gradients.primary,
    border: 'none',
    borderRadius: '12px',
    cursor: 'pointer',
    transition: 'transform 0.2s, box-shadow 0.2s',
    boxShadow: '0 4px 12px rgba(233, 30, 99, 0.3)',
  },
  submitButtonDisabled: {
    opacity: 0.6,
    cursor: 'not-allowed',
  },
};

export default MultiChannelContact;
