'use client';

import { CheckCircle, X } from 'lucide-react';
import { colors, gradients } from '@/lib/colors';

interface SuccessModalProps {
  isOpen: boolean;
  onClose: () => void;
  ticketId?: string;
}

export default function SuccessModal({ isOpen, onClose, ticketId }: SuccessModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 relative animate-slideUp">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-lg hover:bg-gray-lightest transition-colors"
          aria-label="Close modal"
        >
          <X className="w-5 h-5 text-gray-medium" />
        </button>

        {/* Success Icon */}
        <div className="flex justify-center mb-6">
          <div
            className="w-20 h-20 rounded-full flex items-center justify-center shadow-lg"
            style={{ background: `${colors.success}20` }}
          >
            <CheckCircle className="w-12 h-12" style={{ color: colors.success }} />
          </div>
        </div>

        {/* Title */}
        <h3 className="text-3xl font-bold text-center mb-4 text-gray-darkest">
          Successfully Submitted!
        </h3>

        {/* Ticket ID */}
        {ticketId && (
          <div className="bg-purple-50 rounded-xl p-4 mb-6 border-2 border-primary-purple/20">
            <p className="text-sm text-gray-dark text-center mb-1">Your Ticket ID</p>
            <p className="text-2xl font-bold text-center text-primary-purple">
              #{ticketId}
            </p>
          </div>
        )}

        {/* Message */}
        <p className="text-center text-gray-dark mb-8 leading-relaxed">
          Thank you for reaching out! Our AI is processing your request and will respond within{' '}
          <span className="font-semibold text-primary-purple">5 minutes</span>.
        </p>

        {/* Close Button */}
        <button
          onClick={onClose}
          className="w-full px-6 py-4 rounded-xl text-white font-semibold text-lg shadow-lg transition-all hover:scale-105 hover:shadow-xl"
          style={{ background: gradients.primary }}
        >
          Close
        </button>
      </div>
    </div>
  );
}
