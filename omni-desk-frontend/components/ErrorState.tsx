'use client';

import { AlertCircle, RefreshCw } from 'lucide-react';
import { gradients } from '@/lib/colors';

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  retrying?: boolean;
}

export default function ErrorState({
  title = 'Something went wrong',
  message,
  onRetry,
  retrying = false,
}: ErrorStateProps) {
  return (
    <div className="bg-white rounded-xl border-2 border-red-200 p-12 text-center">
      <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
        <AlertCircle className="w-8 h-8 text-red-600" />
      </div>
      <h3 className="text-xl font-bold text-gray-darkest mb-2">{title}</h3>
      <p className="text-gray-medium mb-6 max-w-md mx-auto">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          disabled={retrying}
          className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-white font-semibold shadow-lg transition-all hover:scale-105 hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          style={{ background: gradients.primary }}
        >
          {retrying ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              Retrying...
            </>
          ) : (
            <>
              <RefreshCw className="w-5 h-5" />
              Try Again
            </>
          )}
        </button>
      )}
    </div>
  );
}
