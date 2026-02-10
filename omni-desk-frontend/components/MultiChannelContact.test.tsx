import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import MultiChannelContact from './MultiChannelContact';

describe('MultiChannelContact Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  describe('Channel Selection', () => {
    it('should render all three channel options', () => {
      render(<MultiChannelContact />);

      expect(screen.getByText('Email')).toBeInTheDocument();
      expect(screen.getByText('WhatsApp')).toBeInTheDocument();
      expect(screen.getByText('Web Form')).toBeInTheDocument();
    });

    it('should show email form when email channel is clicked', async () => {
      render(<MultiChannelContact />);

      const emailButton = screen.getByText('Email').closest('button');
      fireEvent.click(emailButton!);

      await waitFor(() => {
        expect(screen.getByText('Email Support')).toBeInTheDocument();
      });
    });

    it('should show whatsapp form when whatsapp channel is clicked', async () => {
      render(<MultiChannelContact />);

      const whatsappButton = screen.getByText('WhatsApp').closest('button');
      fireEvent.click(whatsappButton!);

      await waitFor(() => {
        expect(screen.getByText('WhatsApp Support')).toBeInTheDocument();
      });
    });

    it('should show web form when web form channel is clicked', async () => {
      render(<MultiChannelContact />);

      const webFormButton = screen.getByText('Web Form').closest('button');
      fireEvent.click(webFormButton!);

      await waitFor(() => {
        expect(screen.getByText(/Submit.*Support Request/)).toBeInTheDocument();
      });
    });
  });

  describe('Email Form', () => {
    beforeEach(async () => {
      render(<MultiChannelContact />);
      const emailButton = screen.getByText('Email').closest('button');
      fireEvent.click(emailButton!);
      await waitFor(() => screen.getByText('Email Support'));
    });

    it('should show validation errors for empty fields', async () => {
      const submitButton = screen.getByText('Send Email');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Please enter a valid email address/i)).toBeInTheDocument();
        expect(screen.getByText(/Subject must be at least 3 characters/i)).toBeInTheDocument();
        expect(screen.getByText(/Message must be at least 10 characters/i)).toBeInTheDocument();
      });
    });

    it('should submit email form successfully', async () => {
      const user = userEvent.setup();

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ conversation_id: 'conv-123' }),
      });

      const emailInput = screen.getByPlaceholderText('your.email@example.com');
      const subjectInput = screen.getByPlaceholderText('Brief description of your issue');
      const messageInput = screen.getByPlaceholderText(/Describe your issue/i);

      await user.type(emailInput, 'test@example.com');
      await user.type(subjectInput, 'Test Subject');
      await user.type(messageInput, 'This is a test message with enough characters');

      const submitButton = screen.getByText('Send Email');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/api/submit', expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: expect.stringContaining('test@example.com'),
        }));
      });
    });

    it('should go back to channel selection', async () => {
      const backButton = screen.getByText('Back to Channel Selection');
      fireEvent.click(backButton);

      await waitFor(() => {
        expect(screen.getByText('Contact Our')).toBeInTheDocument();
      });
    });
  });

  describe('WhatsApp Form', () => {
    beforeEach(async () => {
      render(<MultiChannelContact />);
      const whatsappButton = screen.getByText('WhatsApp').closest('button');
      fireEvent.click(whatsappButton!);
      await waitFor(() => screen.getByText('WhatsApp Support'));
    });

    it('should validate phone number format', async () => {
      const user = userEvent.setup();
      const phoneInput = screen.getByPlaceholderText('+1234567890');

      await user.type(phoneInput, 'invalid');

      const submitButton = screen.getByText('Send WhatsApp Message');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Please enter a valid phone number/i)).toBeInTheDocument();
      });
    });

    it('should enforce character limit', async () => {
      const user = userEvent.setup();
      const messageInput = screen.getByPlaceholderText('What can we help you with?');

      const longMessage = 'a'.repeat(1700);
      await user.type(messageInput, longMessage);

      await waitFor(() => {
        expect(screen.getByText(/1600 characters/i)).toBeInTheDocument();
      });
    });

    it('should submit whatsapp form successfully', async () => {
      const user = userEvent.setup();

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ conversation_id: 'conv-456' }),
      });

      const phoneInput = screen.getByPlaceholderText('+1234567890');
      const messageInput = screen.getByPlaceholderText('What can we help you with?');

      await user.type(phoneInput, '+923313494999');
      await user.type(messageInput, 'I need help with my account');

      const submitButton = screen.getByText('Send WhatsApp Message');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/api/submit', expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('whatsapp:+923313494999'),
        }));
      });
    });
  });

  describe('Web Form', () => {
    beforeEach(async () => {
      render(<MultiChannelContact />);
      const webFormButton = screen.getByText('Web Form').closest('button');
      fireEvent.click(webFormButton!);
      await waitFor(() => screen.getByText(/Submit.*Support Request/));
    });

    it('should have default category and priority selected', () => {
      const categorySelect = screen.getByLabelText(/Category/i) as HTMLSelectElement;
      const prioritySelect = screen.getByLabelText(/Priority/i) as HTMLSelectElement;

      expect(categorySelect.value).toBe('how-to');
      expect(prioritySelect.value).toBe('medium');
    });

    it('should submit web form successfully', async () => {
      const user = userEvent.setup();

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ conversation_id: 'conv-789' }),
      });

      const nameInput = screen.getByPlaceholderText('John Doe');
      const emailInput = screen.getByPlaceholderText('john@example.com');
      const messageInput = screen.getByPlaceholderText(/Describe your issue/i);

      await user.type(nameInput, 'Test User');
      await user.type(emailInput, 'test@example.com');
      await user.type(messageInput, 'This is my test message for support');

      const submitButton = screen.getByText('Send Message');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/api/submit', expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('Test User'),
        }));
      });
    });
  });

  describe('Error Handling', () => {
    it('should show error alert on submission failure', async () => {
      const user = userEvent.setup();
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});

      render(<MultiChannelContact />);
      const emailButton = screen.getByText('Email').closest('button');
      fireEvent.click(emailButton!);

      await waitFor(() => screen.getByText('Email Support'));

      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
      });

      const emailInput = screen.getByPlaceholderText('your.email@example.com');
      const subjectInput = screen.getByPlaceholderText('Brief description of your issue');
      const messageInput = screen.getByPlaceholderText(/Describe your issue/i);

      await user.type(emailInput, 'test@example.com');
      await user.type(subjectInput, 'Test Subject');
      await user.type(messageInput, 'Test message content');

      const submitButton = screen.getByText('Send Email');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(alertSpy).toHaveBeenCalledWith('Sorry, something went wrong. Please try again.');
      });

      alertSpy.mockRestore();
    });
  });
});
