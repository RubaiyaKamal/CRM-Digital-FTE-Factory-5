'use client';

import { Quote, Star } from 'lucide-react';
import { colors, gradients } from '@/lib/colors';

interface Testimonial {
  name: string;
  company: string;
  role: string;
  quote: string;
  avatar: string;
}

const testimonials: Testimonial[] = [
  {
    name: 'Sarah Chen',
    company: 'TechFlow Inc.',
    role: 'Head of Customer Success',
    quote: 'OmniDesk AI transformed our support operations. We went from 12-hour response times to under 2 seconds. Our customer satisfaction scores jumped 40% in the first month!',
    avatar: 'SC',
  },
  {
    name: 'Michael Rodriguez',
    company: 'CloudSync Solutions',
    role: 'CEO',
    quote: 'The best investment we\'ve made. The AI handles 80% of our tickets autonomously, and our team can focus on complex issues that truly need human touch. Game changer.',
    avatar: 'MR',
  },
  {
    name: 'Emily Watson',
    company: 'RetailHub Global',
    role: 'VP of Operations',
    quote: 'Cross-channel support made easy! Whether customers reach us via email, WhatsApp, or web, the AI maintains perfect context. It\'s like having a super-agent working 24/7.',
    avatar: 'EW',
  },
];

export default function Testimonials() {
  return (
    <section className="py-20 px-4 bg-gradient-to-b from-white to-purple-50">
      <div className="container mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-darkest mb-4">
            Loved by
            <span
              className="bg-clip-text text-transparent ml-3"
              style={{ backgroundImage: gradients.primary }}
            >
              Support Teams
            </span>
          </h2>
          <p className="text-xl text-gray-medium max-w-2xl mx-auto">
            See what our customers have to say about their experience
          </p>
        </div>

        {/* Testimonials Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {testimonials.map((testimonial, index) => (
            <div
              key={index}
              className="bg-white rounded-2xl p-8 shadow-lg border-2 border-gray-light hover:border-primary-purple hover:shadow-2xl transition-all duration-300"
            >
              {/* Quote Icon */}
              <div className="flex justify-center mb-6">
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center"
                  style={{ background: `${colors.primary.purple}15` }}
                >
                  <Quote className="w-6 h-6" style={{ color: colors.primary.purple }} />
                </div>
              </div>

              {/* Stars */}
              <div className="flex justify-center gap-1 mb-6">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star
                    key={star}
                    className="w-5 h-5 fill-current"
                    style={{ color: colors.warning }}
                  />
                ))}
              </div>

              {/* Quote */}
              <p className="text-gray-dark leading-relaxed mb-8 text-center">
                "{testimonial.quote}"
              </p>

              {/* Author */}
              <div className="flex items-center gap-4">
                {/* Avatar */}
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg flex-shrink-0"
                  style={{ background: gradients.primary }}
                >
                  {testimonial.avatar}
                </div>

                {/* Info */}
                <div>
                  <p className="font-bold text-gray-darkest">{testimonial.name}</p>
                  <p className="text-sm text-gray-medium">{testimonial.role}</p>
                  <p className="text-sm font-semibold text-primary-purple">
                    {testimonial.company}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-16">
          <p className="text-lg text-gray-dark mb-6">
            Join hundreds of satisfied customers
          </p>
          <button
            onClick={() => {
              const element = document.getElementById('contact');
              if (element) element.scrollIntoView({ behavior: 'smooth' });
            }}
            className="px-8 py-4 rounded-xl text-white font-semibold text-lg shadow-xl transition-all hover:scale-105 hover:shadow-2xl"
            style={{ background: gradients.primary }}
          >
            Start Your Free Trial
          </button>
        </div>
      </div>
    </section>
  );
}
