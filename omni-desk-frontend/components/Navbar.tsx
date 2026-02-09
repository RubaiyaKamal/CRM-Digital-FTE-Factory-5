'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Menu, X, Zap, LayoutDashboard } from 'lucide-react';
import { colors, gradients } from '@/lib/colors';

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setIsMobileMenuOpen(false);
    }
  };

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-white/90 backdrop-blur-md shadow-md'
          : 'bg-transparent'
      }`}
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <button
            onClick={() => scrollToSection('home')}
            className="flex items-center gap-3 group"
          >
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center shadow-lg transition-transform group-hover:scale-105"
              style={{ background: gradients.primary }}
            >
              <Zap className="w-6 h-6 text-white" />
            </div>
            <span
              className="text-2xl font-bold bg-clip-text text-transparent"
              style={{
                backgroundImage: gradients.primary,
              }}
            >
              OmniDesk AI
            </span>
          </button>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            {['home', 'features', 'how-it-works', 'contact'].map((item) => (
              <button
                key={item}
                onClick={() => scrollToSection(item)}
                className="text-gray-dark font-medium hover:text-primary-purple transition-colors"
              >
                {item
                  .split('-')
                  .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                  .join(' ')}
              </button>
            ))}
          </div>

          {/* CTA Buttons - Desktop */}
          <div className="hidden md:flex items-center gap-3">
            <Link
              href="/dashboard"
              className="flex items-center gap-2 px-5 py-3 rounded-lg bg-white text-primary-purple font-semibold border-2 border-primary-purple hover:bg-purple-50 transition-all"
            >
              <LayoutDashboard className="w-4 h-4" />
              Dashboard
            </Link>
            <button
              onClick={() => scrollToSection('contact')}
              className="px-6 py-3 rounded-lg text-white font-semibold shadow-lg transition-all hover:scale-105 hover:shadow-xl"
              style={{ background: gradients.primary }}
            >
              Get Started
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 rounded-lg hover:bg-gray-lightest transition-colors"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle mobile menu"
          >
            {isMobileMenuOpen ? (
              <X className="w-6 h-6" style={{ color: colors.primary.purple }} />
            ) : (
              <Menu className="w-6 h-6" style={{ color: colors.primary.purple }} />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-white border-t border-gray-light shadow-lg">
          <div className="container mx-auto px-4 py-6 space-y-4">
            {['home', 'features', 'how-it-works', 'contact'].map((item) => (
              <button
                key={item}
                onClick={() => scrollToSection(item)}
                className="block w-full text-left px-4 py-3 rounded-lg text-gray-dark font-medium hover:bg-purple-50 transition-colors"
              >
                {item
                  .split('-')
                  .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                  .join(' ')}
              </button>
            ))}
            <Link
              href="/dashboard"
              className="flex items-center justify-center gap-2 w-full px-6 py-3 rounded-lg bg-white text-primary-purple font-semibold border-2 border-primary-purple"
            >
              <LayoutDashboard className="w-4 h-4" />
              Dashboard
            </Link>
            <button
              onClick={() => scrollToSection('contact')}
              className="w-full px-6 py-3 rounded-lg text-white font-semibold shadow-lg"
              style={{ background: gradients.primary }}
            >
              Get Started
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}
