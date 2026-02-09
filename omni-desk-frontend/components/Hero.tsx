'use client';

import { useEffect, useState } from 'react';
import { ArrowRight, PlayCircle } from 'lucide-react';
import { colors, gradients } from '@/lib/colors';

interface StatProps {
  end: number;
  label: string;
  suffix?: string;
  prefix?: string;
}

function AnimatedStat({ end, label, suffix = '', prefix = '' }: StatProps) {
  const [count, setCount] = useState(0);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  useEffect(() => {
    if (!isVisible) return;

    const duration = 2000; // 2 seconds
    const steps = 60;
    const increment = end / steps;
    const stepDuration = duration / steps;

    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, stepDuration);

    return () => clearInterval(timer);
  }, [isVisible, end]);

  return (
    <div className="text-center">
      <div className="text-4xl md:text-5xl font-bold text-white mb-2">
        {prefix}
        {count.toLocaleString()}
        {suffix}
      </div>
      <div className="text-white/90 text-sm md:text-base">{label}</div>
    </div>
  );
}

export default function Hero() {
  const scrollToContact = () => {
    const element = document.getElementById('contact');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <section
      id="home"
      className="relative pt-32 pb-20 px-4 min-h-screen flex flex-col justify-center overflow-hidden"
      style={{
        background: `linear-gradient(135deg, ${colors.purple100} 0%, ${colors.purple50} 50%, ${colors.white} 100%)`,
      }}
    >
      {/* Decorative background elements */}
      <div className="absolute top-20 right-10 w-72 h-72 rounded-full opacity-20 blur-3xl"
        style={{ background: gradients.primary }}
      />
      <div className="absolute bottom-20 left-10 w-96 h-96 rounded-full opacity-10 blur-3xl"
        style={{ background: gradients.primary }}
      />

      <div className="container mx-auto relative z-10">
        {/* Main Content */}
        <div className="max-w-4xl mx-auto text-center mb-16">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white shadow-md mb-8">
            <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
            <span className="text-sm font-medium text-gray-dark">
              AI-Powered • Available 24/7
            </span>
          </div>

          {/* Headline */}
          <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold mb-6 leading-tight">
            <span
              className="bg-clip-text text-transparent"
              style={{ backgroundImage: gradients.primary }}
            >
              24/7 AI-Powered
            </span>
            <br />
            <span className="text-gray-darkest">Customer Support</span>
          </h1>

          {/* Subheadline */}
          <p className="text-xl md:text-2xl text-gray-dark mb-10 max-w-3xl mx-auto leading-relaxed">
            Handle unlimited customer inquiries across{' '}
            <span className="font-semibold text-primary-purple">Email</span>,{' '}
            <span className="font-semibold text-primary-purple">WhatsApp</span>, and{' '}
            <span className="font-semibold text-primary-purple">Web</span> — all automated with AI
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-20">
            <button
              onClick={scrollToContact}
              className="group flex items-center gap-2 px-8 py-4 rounded-xl text-white font-semibold text-lg shadow-xl transition-all hover:scale-105 hover:shadow-2xl"
              style={{ background: gradients.primary }}
            >
              Start Free Trial
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
            <button
              className="flex items-center gap-2 px-8 py-4 rounded-xl bg-white text-primary-purple font-semibold text-lg border-2 border-primary-purple shadow-lg transition-all hover:scale-105 hover:bg-purple-50"
            >
              <PlayCircle className="w-5 h-5" />
              Watch Demo
            </button>
          </div>
        </div>

        {/* Animated Stats */}
        <div
          className="max-w-5xl mx-auto rounded-2xl p-8 md:p-12 shadow-2xl"
          style={{ background: gradients.primary }}
        >
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <AnimatedStat end={10000} suffix="+" label="Tickets Resolved" />
            <AnimatedStat end={99.8} suffix="%" label="Uptime" />
            <AnimatedStat end={2} suffix="s" prefix="<" label="Response Time" />
            <AnimatedStat end={500} suffix="+" label="Happy Customers" />
          </div>
        </div>
      </div>
    </section>
  );
}
