import { z } from 'zod';

export const supportFormSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  subject: z.string().min(5, 'Subject must be at least 5 characters'),
  category: z.enum(
    [
      'technical',
      'billing',
      'how-to',
      'feature-request',
      'bug-report',
      'other',
    ],
    {
      message: 'Please select a category',
    }
  ),
  priority: z.enum(['low', 'medium', 'high', 'urgent'], {
    message: 'Please select a priority level',
  }),
  message: z
    .string()
    .min(10, 'Message must be at least 10 characters')
    .max(1000, 'Message must not exceed 1000 characters'),
});

export type SupportFormData = z.infer<typeof supportFormSchema>;
