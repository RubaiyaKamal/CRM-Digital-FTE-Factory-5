'use client';

import { Zap, Mail, Linkedin, Twitter, Github } from 'lucide-react';
import { colors, gradients } from '@/lib/colors';

export default function Footer() {
  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <footer className="bg-gray-darkest text-white py-12 px-4">
      <div className="container mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Logo & Tagline */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-3 mb-4">
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center shadow-lg"
                style={{ background: gradients.primary }}
              >
                <Zap className="w-6 h-6 text-white" />
              </div>
              <span
                className="text-2xl font-bold bg-clip-text text-transparent"
                style={{ backgroundImage: gradients.primary }}
              >
                OmniDesk AI
              </span>
            </div>
            <p className="text-gray-light max-w-sm mb-6">
              24/7 Customer Success Agent powered by AI. Handle unlimited inquiries across all channels with instant, accurate responses.
            </p>
            {/* Contact */}
            <div className="flex items-center gap-2 text-gray-light hover:text-primary-purple transition-colors">
              <Mail className="w-5 h-5" />
              <a href="mailto:support@omnidesk.ai" className="hover:underline">
                support@omnidesk.ai
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-bold text-lg mb-4 text-white">Quick Links</h3>
            <ul className="space-y-2">
              {[
                { label: 'Home', id: 'home' },
                { label: 'Features', id: 'features' },
                { label: 'How It Works', id: 'how-it-works' },
                { label: 'Contact', id: 'contact' },
              ].map((link) => (
                <li key={link.id}>
                  <button
                    onClick={() => scrollToSection(link.id)}
                    className="text-gray-light hover:text-primary-purple transition-colors"
                  >
                    {link.label}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="font-bold text-lg mb-4 text-white">Legal</h3>
            <ul className="space-y-2">
              {['About', 'Privacy Policy', 'Terms of Service', 'Contact Us'].map((item) => (
                <li key={item}>
                  <a
                    href="#"
                    className="text-gray-light hover:text-primary-purple transition-colors"
                  >
                    {item}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-dark pt-8 mt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          {/* Copyright */}
          <p className="text-gray-medium text-sm">
            © {new Date().getFullYear()} OmniDesk AI. All rights reserved.
          </p>

          {/* Social Links */}
          <div className="flex gap-4">
            {[
              { icon: Linkedin, href: '#', label: 'LinkedIn' },
              { icon: Twitter, href: '#', label: 'Twitter' },
              { icon: Github, href: '#', label: 'GitHub' },
            ].map((social) => (
              <a
                key={social.label}
                href={social.href}
                aria-label={social.label}
                className="w-10 h-10 rounded-lg bg-gray-dark hover:bg-primary-purple transition-colors flex items-center justify-center group"
              >
                <social.icon className="w-5 h-5 text-gray-light group-hover:text-white transition-colors" />
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
