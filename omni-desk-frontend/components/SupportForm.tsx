'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2, Send } from 'lucide-react';
import { supportFormSchema, type SupportFormData } from '@/lib/validations';
import { colors, gradients } from '@/lib/colors';
import SuccessModal from './SuccessModal';

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

export default function SupportForm() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [ticketId, setTicketId] = useState<string>('');
  const [messageLength, setMessageLength] = useState(0);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm<SupportFormData>({
    resolver: zodResolver(supportFormSchema),
  });

  // Watch message field for character count
  const messageValue = watch('message', '');
  useState(() => {
    setMessageLength(messageValue?.length || 0);
  });

  const onSubmit = async (data: SupportFormData) => {
    setIsSubmitting(true);

    try {
      // API call via Next.js proxy (avoids CORS)
      const response = await fetch('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: data.name,
          email: data.email,
          subject: data.subject,
          message: data.message,
          category: data.category,
          priority: data.priority,
          session_id: `web-${Date.now()}`,
        }),
      });

      if (!response.ok) {
        throw new Error('Submission failed');
      }

      const result = await response.json();
      setTicketId(result.conversation_id || 'ABC123');
      setShowSuccess(true);
      reset();
      setMessageLength(0);
    } catch (error) {
      console.error('Form submission error:', error);
      alert('Sorry, something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <section id="contact" className="py-20 px-4 bg-white">
        <div className="container mx-auto max-w-3xl">
          {/* Section Header */}
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-darkest mb-4">
              Submit a
              <span
                className="bg-clip-text text-transparent ml-3"
                style={{ backgroundImage: gradients.primary }}
              >
                Support Request
              </span>
            </h2>
            <p className="text-xl text-gray-medium">
              We're here to help! Fill out the form below and we'll get back to you shortly.
            </p>
          </div>

          {/* Form */}
          <form
            onSubmit={handleSubmit(onSubmit)}
            className="bg-white rounded-2xl border-2 border-gray-light p-8 shadow-xl"
          >
            {/* Name */}
            <div className="mb-6">
              <label htmlFor="name" className="block text-gray-darkest font-semibold mb-2">
                Name <span className="text-error">*</span>
              </label>
              <input
                {...register('name')}
                type="text"
                id="name"
                placeholder="Your full name"
                className={`w-full px-4 py-3 rounded-lg border-2 bg-gray-lightest focus:bg-white focus:outline-none transition-colors ${
                  errors.name ? 'border-error' : 'border-gray-light focus:border-primary-purple'
                }`}
              />
              {errors.name && (
                <p className="text-error text-sm mt-1">{errors.name.message}</p>
              )}
            </div>

            {/* Email */}
            <div className="mb-6">
              <label htmlFor="email" className="block text-gray-darkest font-semibold mb-2">
                Email <span className="text-error">*</span>
              </label>
              <input
                {...register('email')}
                type="email"
                id="email"
                placeholder="your@email.com"
                className={`w-full px-4 py-3 rounded-lg border-2 bg-gray-lightest focus:bg-white focus:outline-none transition-colors ${
                  errors.email ? 'border-error' : 'border-gray-light focus:border-primary-purple'
                }`}
              />
              {errors.email && (
                <p className="text-error text-sm mt-1">{errors.email.message}</p>
              )}
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
              {errors.subject && (
                <p className="text-error text-sm mt-1">{errors.subject.message}</p>
              )}
            </div>

            {/* Category & Priority - Side by Side */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* Category */}
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
                  <option value="">Select a category</option>
                  {categories.map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
                {errors.category && (
                  <p className="text-error text-sm mt-1">{errors.category.message}</p>
                )}
              </div>

              {/* Priority */}
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
                  <option value="">Select priority</option>
                  {priorities.map((pri) => (
                    <option key={pri.value} value={pri.value}>
                      {pri.label}
                    </option>
                  ))}
                </select>
                {errors.priority && (
                  <p className="text-error text-sm mt-1">{errors.priority.message}</p>
                )}
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
                placeholder="Please describe your issue in detail..."
                onChange={(e) => setMessageLength(e.target.value.length)}
                className={`w-full px-4 py-3 rounded-lg border-2 bg-gray-lightest focus:bg-white focus:outline-none transition-colors resize-none ${
                  errors.message ? 'border-error' : 'border-gray-light focus:border-primary-purple'
                }`}
              />
              <div className="flex justify-between items-center mt-1">
                <div>
                  {errors.message && (
                    <p className="text-error text-sm">{errors.message.message}</p>
                  )}
                </div>
                <p
                  className={`text-sm ${
                    messageLength > 1000 ? 'text-error' : 'text-gray-medium'
                  }`}
                >
                  {messageLength} / 1000 characters
                </p>
              </div>
            </div>

            {/* Submit Button */}
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

      {/* Success Modal */}
      <SuccessModal
        isOpen={showSuccess}
        onClose={() => setShowSuccess(false)}
        ticketId={ticketId}
      />
    </>
  );
}
