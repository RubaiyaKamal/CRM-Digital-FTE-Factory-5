import React, { useState } from 'react';
import { colors, gradients } from './theme';

interface SupportFormProps {
  onSubmit: (data: FormData) => void;
  disabled?: boolean;
}

export interface FormData {
  name: string;
  email: string;
  subject: string;
  category: string;
  priority: string;
  message: string;
}

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

const SupportForm: React.FC<SupportFormProps> = ({ onSubmit, disabled = false }) => {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    subject: '',
    category: 'how-to',
    priority: 'medium',
    message: '',
  });

  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({});

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof FormData, string>> = {};

    if (formData.name.length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (formData.message.length < 10) {
      newErrors.message = 'Message must be at least 10 characters';
    }

    if (formData.message.length > 1000) {
      newErrors.message = 'Message cannot exceed 1000 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!disabled && validate()) {
      onSubmit(formData);
    }
  };

  const handleChange = (field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const charCount = formData.message.length;
  const charCountColor = charCount > 1000 ? colors.error : charCount > 900 ? colors.warning : colors.gray.medium;

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      <div style={styles.header}>
        <h2 style={styles.formTitle}>Submit a Support Request</h2>
        <p style={styles.formSubtitle}>We're here to help! Fill out the form below and we'll get back to you shortly.</p>
      </div>

      <div style={styles.row}>
        <div style={styles.field}>
          <label style={styles.label}>
            Name <span style={styles.required}>*</span>
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            placeholder="John Doe"
            disabled={disabled}
            style={{
              ...styles.input,
              ...(errors.name ? styles.inputError : {}),
            }}
          />
          {errors.name && <span style={styles.errorText}>{errors.name}</span>}
        </div>

        <div style={styles.field}>
          <label style={styles.label}>
            Email <span style={styles.required}>*</span>
          </label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => handleChange('email', e.target.value)}
            placeholder="john@example.com"
            disabled={disabled}
            style={{
              ...styles.input,
              ...(errors.email ? styles.inputError : {}),
            }}
          />
          {errors.email && <span style={styles.errorText}>{errors.email}</span>}
        </div>
      </div>

      <div style={styles.field}>
        <label style={styles.label}>Subject</label>
        <input
          type="text"
          value={formData.subject}
          onChange={(e) => handleChange('subject', e.target.value)}
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
            value={formData.category}
            onChange={(e) => handleChange('category', e.target.value)}
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
            value={formData.priority}
            onChange={(e) => handleChange('priority', e.target.value)}
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
          value={formData.message}
          onChange={(e) => handleChange('message', e.target.value)}
          placeholder="Describe your issue or question in detail..."
          disabled={disabled}
          rows={6}
          maxLength={1000}
          style={{
            ...styles.textarea,
            ...(errors.message ? styles.inputError : {}),
          }}
        />
        <div style={styles.charCount}>
          <span style={{ color: charCountColor }}>
            {charCount} / 1000 characters
          </span>
        </div>
        {errors.message && <span style={styles.errorText}>{errors.message}</span>}
      </div>

      <button
        type="submit"
        disabled={disabled}
        style={{
          ...styles.submitButton,
          ...(disabled ? styles.submitButtonDisabled : {}),
        }}
      >
        {disabled ? 'Sending...' : 'Send Message'}
      </button>
    </form>
  );
};

const styles: Record<string, React.CSSProperties> = {
  form: {
    background: colors.white,
    borderRadius: '16px',
    padding: '32px',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
  },
  header: {
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
  charCount: {
    marginTop: '4px',
    fontSize: '13px',
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

export default SupportForm;
