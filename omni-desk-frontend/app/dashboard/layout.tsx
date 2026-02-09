'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Ticket,
  Users,
  MessageSquare,
  Settings,
  Menu,
  X,
  Zap,
  Home
} from 'lucide-react';
import { colors, gradients } from '@/lib/colors';

const navItems = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/dashboard/tickets', icon: Ticket, label: 'Tickets' },
  { href: '/dashboard/customers', icon: Users, label: 'Customers' },
  { href: '/dashboard/conversations', icon: MessageSquare, label: 'Conversations' },
  { href: '/dashboard/settings', icon: Settings, label: 'Settings' },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-lightest flex">
      {/* Sidebar - Desktop */}
      <aside className="hidden md:flex md:flex-col md:w-64 bg-gray-darkest text-white fixed h-full">
        {/* Logo */}
        <div className="p-6 border-b border-gray-dark">
          <Link href="/" className="flex items-center gap-3 group">
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center shadow-lg"
              style={{ background: gradients.primary }}
            >
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div>
              <span
                className="text-xl font-bold bg-clip-text text-transparent"
                style={{ backgroundImage: gradients.primary }}
              >
                OmniDesk AI
              </span>
              <p className="text-xs text-gray-light">Admin Dashboard</p>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                  isActive
                    ? 'bg-primary-purple text-white'
                    : 'text-gray-light hover:bg-gray-dark hover:text-white'
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Back to Home */}
        <div className="p-4 border-t border-gray-dark">
          <Link
            href="/"
            className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-light hover:bg-gray-dark hover:text-white transition-all"
          >
            <Home className="w-5 h-5" />
            <span className="font-medium">Back to Home</span>
          </Link>
        </div>
      </aside>

      {/* Mobile Menu Button */}
      <button
        className="md:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-gray-darkest text-white"
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
      >
        {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
      </button>

      {/* Mobile Sidebar */}
      {isMobileMenuOpen && (
        <div className="md:hidden fixed inset-0 z-40 bg-black/50 backdrop-blur-sm">
          <aside className="w-64 h-full bg-gray-darkest text-white">
            <div className="p-6 border-b border-gray-dark">
              <Link href="/" className="flex items-center gap-3">
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center"
                  style={{ background: gradients.primary }}
                >
                  <Zap className="w-6 h-6 text-white" />
                </div>
                <div>
                  <span className="text-xl font-bold text-white">OmniDesk AI</span>
                  <p className="text-xs text-gray-light">Admin Dashboard</p>
                </div>
              </Link>
            </div>

            <nav className="p-4 space-y-2">
              {navItems.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                      isActive
                        ? 'bg-primary-purple text-white'
                        : 'text-gray-light hover:bg-gray-dark hover:text-white'
                    }`}
                  >
                    <item.icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                );
              })}
              <Link
                href="/"
                onClick={() => setIsMobileMenuOpen(false)}
                className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-light hover:bg-gray-dark hover:text-white transition-all"
              >
                <Home className="w-5 h-5" />
                <span className="font-medium">Back to Home</span>
              </Link>
            </nav>
          </aside>
        </div>
      )}

      {/* Main Content */}
      <main className="flex-1 md:ml-64">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
