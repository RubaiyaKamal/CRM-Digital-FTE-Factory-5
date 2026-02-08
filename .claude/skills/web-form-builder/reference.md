# Web Form Builder Reference

## Overview
This skill creates a complete, production-ready React/Next.js web support form with validation, submission handling, and ticket status tracking.

## Key Capabilities
- Form validation (client-side and server-side)
- Category and priority selection
- Real-time character counting
- Success/error state handling
- Ticket status retrieval
- Embeddable component design

## Prerequisites
- Next.js 14+ or React 18+ project
- FastAPI backend with form endpoint
- Tailwind CSS for styling (optional but recommended)

## Related Files
- `src/web-form/SupportForm.jsx` - Main component
- `src/api/channels/web_form_handler.py` - Backend handler
- `tests/test_web_form.py` - Component tests

## API References
- [React Hook Form](https://react-hook-form.com/) (alternative approach)
- [Tailwind CSS](https://tailwindcss.com/)

## Common Issues
1. **CORS errors**: Configure FastAPI CORS middleware
2. **Form validation**: Sync client and server validation rules
3. **Loading states**: Show spinner during submission

## Constitutional Alignment
- **Principle 1: Multi-Channel First** - Web form as equal channel
- **Principle 4: Channel-Appropriate Responses** - Semi-formal web responses
- **Principle 9: Test-Driven Reliability** - Component tests required
