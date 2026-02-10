'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Loader2, Send, Mail, MessageCircle, Globe, ArrowLeft } from 'lucide-react';
import { colors, gradients } from '@/lib/colors';
import SuccessModal from './SuccessModal';

// Channel types
type Channel = 'email' | 'whatsapp' | 'web_form';

// Validation schemas
const emailFormSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  subject: z.string().min(3, 'Subject must be at least 3 characters'),
  body: z.string().min(10, 'Message must be at least 10 characters'),
});

const whatsappFormSchema = z.object({
  phone: z.string().regex(/^\+?[1-9]\d{1,14}$/, 'Please enter a valid phone number with country code'),
  message: z.string().min(10, 'Message must be at least 10 characters').max(1600, 'Message cannot exceed 1600 characters'),
});

const webFormSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  subject: z.string().optional(),
  category: z.string().min(1, 'Please select a category'),
  priority: z.string().min(1, 'Please select a priority'),
  message: z.string().min(10, 'Message must be at least 10 characters').max(1000, 'Message cannot exceed 1000 characters'),
});

type EmailFormData = z.infer<typeof emailFormSchema>;
type WhatsAppFormData = z.infer<typeof whatsappFormSchema>;
type WebFormData = z.infer<typeof webFormSchema>;

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

export default function MultiChannelContact() {
  const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [ticketId, setTicketId] = useState<string>('');

  const handleBack = () => {
    setSelectedChannel(null);
  };

  const handleChannelSubmit = async (channel: Channel, data: any) => {
    setIsSubmitting(true);

    try {
      let endpoint = '/api/submit';
      let payload: any = {};

      if (channel === 'email') {
        endpoint = '/api/submit';
        payload = {
          channel: 'email',
          from: data.email,
          subject: data.subject,
          body: data.body,
          message: data.body,
        };
      } else if (channel === 'whatsapp') {
        endpoint = '/api/submit';
        payload = {
          channel: 'whatsapp',
          From: `whatsapp:${data.phone}`,
          Body: data.message,
          MessageSid: `WEB${Date.now()}`,
        };
      } else {
        // web_form
        payload = {
          channel: 'web_form',
          name: data.name,
          email: data.email,
          subject: data.subject || undefined,
          message: data.message,
          category: data.category,
          priority: data.priority,
          session_id: `web-${Date.now()}`,
        };
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Submission failed');
      }

      const result = await response.json();
      setTicketId(result.conversation_id || 'ABC123');
      setShowSuccess(true);
      setSelectedChannel(null);
    } catch (error) {
      console.error('Form submission error:', error);
      alert('Sorry, something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Channel Selector
  if (!selectedChannel) {
    return (
      <section id="contact" className="py-20 px-4 bg-white">
        <div className="container mx-auto max-w-5xl">
          {/* Header */}
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-darkest mb-4">
              Contact Our
              <span
                className="bg-clip-text text-transparent ml-3"
                style={{ backgroundImage: gradients.primary }}
              >
                AI Assistant
              </span>
            </h2>
            <p className="text-xl text-gray-medium">
              Reach us through your preferred channel. Our AI agent is available 24/7 to assist you.
            </p>
          </div>

          {/* Channel Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            {/* Email Card */}
            <button
              onClick={() => setSelectedChannel('email')}
              className="bg-white border-2 border-gray-light rounded-2xl p-8 text-center hover:border-primary-purple hover:shadow-xl transition-all transform hover:scale-105"
            >
              <div className="flex justify-center mb-4">
                <div className="w-16 h-16 rounded-full bg-purple-100 flex items-center justify-center">
                  <Mail className="w-8 h-8 text-primary-purple" />
                </div>
              </div>
              <h3 className="text-xl font-bold text-gray-darkest mb-2">Email</h3>
              <p className="text-gray-medium">Send us an email and get a detailed response</p>
            </button>

            {/* WhatsApp Card */}
            <button
              onClick={() => setSelectedChannel('whatsapp')}
              className="bg-white border-2 border-gray-light rounded-2xl p-8 text-center hover:border-success hover:shadow-xl transition-all transform hover:scale-105"
            >
              <div className="flex justify-center mb-4">
                <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center">
                  <MessageCircle className="w-8 h-8 text-success" />
                </div>
              </div>
              <h3 className="text-xl font-bold text-gray-darkest mb-2">WhatsApp</h3>
              <p className="text-gray-medium">Chat with us instantly on WhatsApp</p>
            </button>

            {/* Web Form Card */}
            <button
              onClick={() => setSelectedChannel('web_form')}
              className="bg-white border-2 border-gray-light rounded-2xl p-8 text-center hover:border-primary-blue hover:shadow-xl transition-all transform hover:scale-105"
            >
              <div className="flex justify-center mb-4">
                <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center">
                  <Globe className="w-8 h-8 text-primary-blue" />
                </div>
              </div>
              <h3 className="text-xl font-bold text-gray-darkest mb-2">Web Form</h3>
              <p className="text-gray-medium">Fill out our form for structured support</p>
            </button>
          </div>
        </div>
      </section>
    );
  }

  // Email Form
  if (selectedChannel === 'email') {
    return <EmailForm onBack={handleBack} onSubmit={(data) => handleChannelSubmit('email', data)} isSubmitting={isSubmitting} />;
  }

  // WhatsApp Form
  if (selectedChannel === 'whatsapp') {
    return <WhatsAppForm onBack={handleBack} onSubmit={(data) => handleChannelSubmit('whatsapp', data)} isSubmitting={isSubmitting} />;
  }

  // Web Form
  return (
    <>
      <WebForm onBack={handleBack} onSubmit={(data) => handleChannelSubmit('web_form', data)} isSubmitting={isSubmitting} />
      <SuccessModal isOpen={showSuccess} onClose={() => setShowSuccess(false)} ticketId={ticketId} />
    </>
  );
}

// Email Form Component
function EmailForm({ onBack, onSubmit, isSubmitting }: { onBack: () => void; onSubmit: (data: EmailFormData) => void; isSubmitting: boolean }) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<EmailFormData>({
    resolver: zodResolver(emailFormSchema),
  });

  return (
    <section id="contact" className="py-20 px-4 bg-white">
      <div className="container mx-auto max-w-3xl">
        <button
          onClick={onBack}
          className="mb-6 flex items-center gap-2 text-primary-purple hover:text-primary-pink transition-colors font-semibold"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Channel Selection
        </button>

        <div className="text-center mb-8">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-darkest mb-4">
            <span className="bg-clip-text text-transparent" style={{ backgroundImage: gradients.primary }}>
              Email Support
            </span>
          </h2>
          <p className="text-xl text-gray-medium">Send us an email and we'll respond as soon as possible</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-2xl border-2 border-gray-light p-8 shadow-xl">
          {/* Email */}
          <div className="mb-6">
            <label htmlFor="email" className="block text-gray-darkest font-semibold mb-2">
              Email Address <span className="text-error">*</span>
            </label>
            <input
              {...register('email')}
              type="email"
              id="email"
              placeholder="your.email@example.com"
              className={`w-full px-4 py-3 rounded-lg border-2 bg-gray-lightest focus:bg-white focus:outline-none transition-colors ${
                errors.email ? 'border-error' : 'border-gray-light focus:border-primary-purple'
              }`}
            />
            {errors.email && <p className="text-error text-sm mt-1">{errors.email.message}</p>}
          </div>

          {/* Subject */}
          <div className="mb-6">
            <label htmlFor="subject" className="block text-gray-darkest font-semibold mb-2">
              Subject <span className="text-error">*</span>
            </label>
            <input
              {...register('subject')}
              type="text"
              id="subject"
              placeholder="Brief description of your issue"
              className={`w-full px-4 py-3 rounded-lg border-2 bg-gray-lightest focus:bg-white focus:outline-none transition-colors ${
                errors.subject ? 'border-error' : 'border-gray-light focus:border-primary-purple'
              }`}
            />
            {errors.subject && <p className="text-error text-sm mt-1">{errors.subject.message}</p>}
          </div>

          {/* Body */}
          <div className="mb-6">
            <label htmlFor="body" className="block text-gray-darkest font-semibold mb-2">
              Message <span className="text-error">*</span>
            </label>
            <textarea
              {...register('body')}
              id="body"
              rows={6}
              placeholder="Describe your issue or question in detail..."
              className={`w-full px-4 py-3 rounded-lg border-2 bg-gray-lightest focus:bg-white focus:outline-none transition-colors resize-none ${
                errors.body ? 'border-error' : 'border-gray-light focus:border-primary-purple'
              }`}
            />
            {errors.body && <p className="text-error text-sm mt-1">{errors.body.message}</p>}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full px-6 py-4 rounded-xl text-white font-semibold text-lg shadow-xl transition-all hover:scale-105 hover:shadow-2xl disabled:opacity-70 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-2"
            style={{ background: gradients.primary }}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Sending...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Send Email
              </>
            )}
          </button>
        </form>
      </div>
    </section>
  );
}

// WhatsApp Form Component
function WhatsAppForm({ onBack, onSubmit, isSubmitting }: { onBack: () => void; onSubmit: (data: WhatsAppFormData) => void; isSubmitting: boolean }) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<WhatsAppFormData>({
    resolver: zodResolver(whatsappFormSchema),
  });

  const messageValue = watch('message', '');
  const charCount = messageValue?.length || 0;

  return (
    <section id="contact" className="py-20 px-4 bg-white">
      <div className="container mx-auto max-w-3xl">
        <button
          onClick={onBack}
          className="mb-6 flex items-center gap-2 text-primary-purple hover:text-primary-pink transition-colors font-semibold"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Channel Selection
        </button>

        <div className="text-center mb-8">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-darkest mb-4">
            <span className="bg-clip-text text-transparent" style={{ backgroundImage: gradients.primary }}>
              WhatsApp Support
            </span>
          </h2>
          <p className="text-xl text-gray-medium">Chat with us instantly via WhatsApp</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-2xl border-2 border-gray-light p-8 shadow-xl">
          {/* Phone */}
          <div className="mb-6">
            <label htmlFor="phone" className="block text-gray-darkest font-semibold mb-2">
              Phone Number <span className="text-error">*</span>
            </label>
            <input
              {...register('phone')}
              type="tel"
              id="phone"
              placeholder="+1234567890"
              className={`w-full px-4 py-3 rounded-lg border-2 bg-gray-lightest focus:bg-white focus:outline-none transition-colors ${
                errors.phone ? 'border-error' : 'border-gray-light focus:border-success'
              }`}
            />
            <p className="text-gray-medium text-sm mt-1">Include country code (e.g., +1 for US)</p>
            {errors.phone && <p className="text-error text-sm mt-1">{errors.phone.message}</p>}
          </div>

          {/* Message */}
          <div className="mb-6">
            <label htmlFor="message" className="block text-gray-darkest font-semibold mb-2">
              Message <span className="text-error">*</span>
            </label>
            <textarea
              {...register('message')}
              id="message"
              rows={6}
              placeholder="What can we help you with?"
              maxLength={1600}
              className={`w-full px-4 py-3 rounded-lg border-2 bg-gray-lightest focus:bg-white focus:outline-none transition-colors resize-none ${
                errors.message ? 'border-error' : 'border-gray-light focus:border-success'
              }`}
            />
            <div className="flex justify-between items-center mt-1">
              <div>{errors.message && <p className="text-error text-sm">{errors.message.message}</p>}</div>
              <p className="text-sm text-gray-medium">{charCount} / 1600 characters</p>
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full px-6 py-4 rounded-xl text-white font-semibold text-lg shadow-xl transition-all hover:scale-105 hover:shadow-2xl disabled:opacity-70 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-2"
            style={{ background: gradients.primary }}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Sending...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Send WhatsApp Message
              </>
            )}
          </button>
        </form>
      </div>
    </section>
  );
}

// Web Form Component
function WebForm({ onBack, onSubmit, isSubmitting }: { onBack: () => void; onSubmit: (data: WebFormData) => void; isSubmitting: boolean }) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<WebFormData>({
    resolver: zodResolver(webFormSchema),
    defaultValues: {
      category: 'how-to',
      priority: 'medium',
    },
  });

  const messageValue = watch('message', '');
  const charCount = messageValue?.length || 0;

  return (
    <section id="contact" className="py-20 px-4 bg-white">
      <div className="container mx-auto max-w-3xl">
        <button
          onClick={onBack}
          className="mb-6 flex items-center gap-2 text-primary-purple hover:text-primary-pink transition-colors font-semibold"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Channel Selection
        </button>

        <div className="text-center mb-8">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-darkest mb-4">
            Submit
            <span className="bg-clip-text text-transparent ml-3" style={{ backgroundImage: gradients.primary }}>
              Support Request
            </span>
          </h2>
          <p className="text-xl text-gray-medium">Fill out the form below and our AI-powered support team will get back to you</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-2xl border-2 border-gray-light p-8 shadow-xl">
          {/* Name & Email */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label htmlFor="name" className="block text-gray-darkest font-semibold mb-2">
                Your Name <span className="text-error">*</span>
              </label>
              <input
                {...register('name')}
                type="text"
                id="name"
                placeholder="John Doe"
                className={`w-full px-4 py-3 rounded-lg border-2 bg-gray-lightest focus:bg-white focus:outline-none transition-colors ${
                  errors.name ? 'border-error' : 'border-gray-light focus:border-primary-purple'
                }`}
              />
              {errors.name && <p className="text-error text-sm mt-1">{errors.name.message}</p>}
            </div>

            <div>
              <label htmlFor="email" className="block text-gray-darkest font-semibold mb-2">
                Email Address <span className="text-error">*</span>
              </label>
              <input
                {...register('email')}
                type="email"
                id="email"
                placeholder="john@example.com"
                className={`w-full px-4 py-3 rounded-lg border-2 bg-gray-lightest focus:bg-white focus:outline-none transition-colors ${
                  errors.email ? 'border-error' : 'border-gray-light focus:border-primary-purple'
                }`}
              />
              {errors.email && <p className="text-error text-sm mt-1">{errors.email.message}</p>}
            </div>
          </div>

          {/* Subject */}
          <div className="mb-6">
            <label htmlFor="subject" className="block text-gray-darkest font-semibold mb-2">
              Subject
            </label>
            <input
              {...register('subject')}
              type="text"
              id="subject"
              placeholder="Brief description of your issue"
              className="w-full px-4 py-3 rounded-lg border-2 bg-gray-lightest focus:bg-white focus:outline-none transition-colors border-gray-light focus:border-primary-purple"
            />
          </div>

          {/* Category & Priority */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label htmlFor="category" className="block text-gray-darkest font-semibold mb-2">
                Category <span className="text-error">*</span>
              </label>
              <select
                {...register('category')}
                id="category"
                className={`w-full px-4 py-3 rounded-lg border-2 bg-gray-lightest focus:bg-white focus:outline-none transition-colors ${
                  errors.category ? 'border-error' : 'border-gray-light focus:border-primary-purple'
                }`}
              >
                {categories.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
              {errors.category && <p className="text-error text-sm mt-1">{errors.category.message}</p>}
            </div>

            <div>
              <label htmlFor="priority" className="block text-gray-darkest font-semibold mb-2">
                Priority <span className="text-error">*</span>
              </label>
              <select
                {...register('priority')}
                id="priority"
                className={`w-full px-4 py-3 rounded-lg border-2 bg-gray-lightest focus:bg-white focus:outline-none transition-colors ${
                  errors.priority ? 'border-error' : 'border-gray-light focus:border-primary-purple'
                }`}
              >
                {priorities.map((pri) => (
                  <option key={pri.value} value={pri.value}>
                    {pri.label}
                  </option>
                ))}
              </select>
              {errors.priority && <p className="text-error text-sm mt-1">{errors.priority.message}</p>}
            </div>
          </div>

          {/* Message */}
          <div className="mb-6">
            <label htmlFor="message" className="block text-gray-darkest font-semibold mb-2">
              Message <span className="text-error">*</span>
            </label>
            <textarea
              {...register('message')}
              id="message"
              rows={6}
              placeholder="Describe your issue or question in detail..."
              maxLength={1000}
              className={`w-full px-4 py-3 rounded-lg border-2 bg-gray-lightest focus:bg-white focus:outline-none transition-colors resize-none ${
                errors.message ? 'border-error' : 'border-gray-light focus:border-primary-purple'
              }`}
            />
            <div className="flex justify-between items-center mt-1">
              <div>{errors.message && <p className="text-error text-sm">{errors.message.message}</p>}</div>
              <p className={`text-sm ${charCount > 1000 ? 'text-error' : 'text-gray-medium'}`}>{charCount} / 1000 characters</p>
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full px-6 py-4 rounded-xl text-white font-semibold text-lg shadow-xl transition-all hover:scale-105 hover:shadow-2xl disabled:opacity-70 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-2"
            style={{ background: gradients.primary }}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Sending...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Send Message
              </>
            )}
          </button>
        </form>
      </div>
    </section>
  );
}
