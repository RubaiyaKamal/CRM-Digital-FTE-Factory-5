'use client';

import { Send, Brain, Zap, ArrowRight } from 'lucide-react';
import { colors, gradients } from '@/lib/colors';

interface Step {
  number: number;
  icon: React.ReactNode;
  title: string;
  description: string;
}

const steps: Step[] = [
  {
    number: 1,
    icon: <Send className="w-8 h-8" />,
    title: 'Customer Submits',
    description: 'Your customer sends an inquiry via email, WhatsApp, or web form with their question or issue',
  },
  {
    number: 2,
    icon: <Brain className="w-8 h-8" />,
    title: 'AI Processes',
    description: 'Our AI analyzes the request, searches your knowledge base, and generates an accurate, contextual response',
  },
  {
    number: 3,
    icon: <Zap className="w-8 h-8" />,
    title: 'Instant Response',
    description: 'Response is delivered perfectly formatted for the channel — email, WhatsApp, or web — in under 2 seconds',
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-20 px-4 bg-gradient-to-b from-purple-50 to-white">
      <div className="container mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-darkest mb-4">
            How It
            <span
              className="bg-clip-text text-transparent ml-3"
              style={{ backgroundImage: gradients.primary }}
            >
              Works
            </span>
          </h2>
          <p className="text-xl text-gray-medium max-w-2xl mx-auto">
            From inquiry to resolution in three simple steps
          </p>
        </div>

        {/* Steps - Desktop Timeline */}
        <div className="hidden md:block max-w-6xl mx-auto">
          <div className="relative">
            {/* Connecting Line */}
            <div
              className="absolute top-20 left-[16.66%] right-[16.66%] h-1 -z-10"
              style={{
                background: `linear-gradient(90deg, ${colors.primary.pink} 0%, ${colors.primary.purple} 100%)`,
              }}
            />

            <div className="grid grid-cols-3 gap-8">
              {steps.map((step, index) => (
                <div key={step.number} className="relative">
                  {/* Step Number Badge */}
                  <div className="flex justify-center mb-6">
                    <div
                      className="w-16 h-16 rounded-full flex items-center justify-center text-white text-2xl font-bold shadow-xl"
                      style={{ background: gradients.primary }}
                    >
                      {step.number}
                    </div>
                  </div>

                  {/* Card */}
                  <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-shadow border-2 border-gray-light hover:border-primary-purple">
                    {/* Icon */}
                    <div
                      className="w-16 h-16 rounded-xl flex items-center justify-center mb-4 mx-auto"
                      style={{ background: `${colors.primary.purple}15` }}
                    >
                      <div style={{ color: colors.primary.purple }}>
                        {step.icon}
                      </div>
                    </div>

                    {/* Title */}
                    <h3 className="text-2xl font-bold text-gray-darkest mb-3 text-center">
                      {step.title}
                    </h3>

                    {/* Description */}
                    <p className="text-gray-dark leading-relaxed text-center">
                      {step.description}
                    </p>
                  </div>

                  {/* Arrow (not on last step) */}
                  {index < steps.length - 1 && (
                    <div className="absolute top-20 -right-4 transform -translate-y-1/2 z-10">
                      <ArrowRight
                        className="w-8 h-8"
                        style={{ color: colors.primary.purple }}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Steps - Mobile Vertical */}
        <div className="md:hidden max-w-md mx-auto space-y-8">
          {steps.map((step, index) => (
            <div key={step.number} className="relative">
              {/* Step Number Badge */}
              <div className="flex items-start gap-4">
                <div
                  className="flex-shrink-0 w-14 h-14 rounded-full flex items-center justify-center text-white text-xl font-bold shadow-lg"
                  style={{ background: gradients.primary }}
                >
                  {step.number}
                </div>

                {/* Card */}
                <div className="flex-1 bg-white rounded-xl p-6 shadow-lg border-2 border-gray-light">
                  {/* Icon */}
                  <div
                    className="w-12 h-12 rounded-lg flex items-center justify-center mb-3"
                    style={{ background: `${colors.primary.purple}15` }}
                  >
                    <div style={{ color: colors.primary.purple }}>
                      {step.icon}
                    </div>
                  </div>

                  {/* Title */}
                  <h3 className="text-xl font-bold text-gray-darkest mb-2">
                    {step.title}
                  </h3>

                  {/* Description */}
                  <p className="text-gray-dark leading-relaxed text-sm">
                    {step.description}
                  </p>
                </div>
              </div>

              {/* Connecting Line */}
              {index < steps.length - 1 && (
                <div
                  className="w-1 h-8 ml-7 my-4"
                  style={{ background: gradients.primaryVertical }}
                />
              )}
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-16">
          <p className="text-lg text-gray-dark mb-6">
            Ready to automate your customer support?
          </p>
          <button
            onClick={() => {
              const element = document.getElementById('contact');
              if (element) element.scrollIntoView({ behavior: 'smooth' });
            }}
            className="px-8 py-4 rounded-xl text-white font-semibold text-lg shadow-xl transition-all hover:scale-105 hover:shadow-2xl"
            style={{ background: gradients.primary }}
          >
            Try It Free
          </button>
        </div>
      </div>
    </section>
  );
}
