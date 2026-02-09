'use client';

import { Bot, Mail, Target, BarChart3, Shield, Globe } from 'lucide-react';
import { colors, gradients } from '@/lib/colors';

interface Feature {
  icon: React.ReactNode;
  title: string;
  description: string;
}

const features: Feature[] = [
  {
    icon: <Bot className="w-8 h-8" />,
    title: 'AI-Powered Responses',
    description: 'Instant, accurate answers 24/7 powered by advanced AI that understands context and customer intent',
  },
  {
    icon: <Mail className="w-8 h-8" />,
    title: 'Multi-Channel Support',
    description: 'Seamlessly handle inquiries across Email, WhatsApp, and Web Form from one unified platform',
  },
  {
    icon: <Target className="w-8 h-8" />,
    title: 'Smart Escalation',
    description: 'Automatically escalate complex issues to human agents with full context and conversation history',
  },
  {
    icon: <BarChart3 className="w-8 h-8" />,
    title: 'Real-Time Analytics',
    description: 'Track performance metrics, customer satisfaction, and response times with detailed dashboards',
  },
  {
    icon: <Shield className="w-8 h-8" />,
    title: 'Enterprise Security',
    description: 'Bank-level encryption, GDPR compliance, and secure data handling for peace of mind',
  },
  {
    icon: <Globe className="w-8 h-8" />,
    title: 'Cross-Channel Memory',
    description: 'Maintain conversation context across all channels for a truly seamless customer experience',
  },
];

export default function Features() {
  return (
    <section id="features" className="py-20 px-4 bg-white">
      <div className="container mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-darkest mb-4">
            Everything You Need for
            <span
              className="bg-clip-text text-transparent ml-3"
              style={{ backgroundImage: gradients.primary }}
            >
              Customer Success
            </span>
          </h2>
          <p className="text-xl text-gray-medium max-w-2xl mx-auto">
            Powerful features designed to automate support and delight your customers
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group p-8 rounded-2xl bg-white border-2 border-gray-light hover:border-primary-purple transition-all duration-300 hover:shadow-xl hover:-translate-y-1"
            >
              {/* Icon */}
              <div
                className="w-16 h-16 rounded-xl flex items-center justify-center mb-6 transition-transform group-hover:scale-110"
                style={{ background: gradients.primary }}
              >
                <div className="text-white">{feature.icon}</div>
              </div>

              {/* Title */}
              <h3 className="text-2xl font-bold text-gray-darkest mb-3 group-hover:text-primary-purple transition-colors">
                {feature.title}
              </h3>

              {/* Description */}
              <p className="text-gray-dark leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-16">
          <button
            onClick={() => {
              const element = document.getElementById('contact');
              if (element) element.scrollIntoView({ behavior: 'smooth' });
            }}
            className="px-8 py-4 rounded-xl text-white font-semibold text-lg shadow-xl transition-all hover:scale-105 hover:shadow-2xl"
            style={{ background: gradients.primary }}
          >
            Get Started Free
          </button>
        </div>
      </div>
    </section>
  );
}
