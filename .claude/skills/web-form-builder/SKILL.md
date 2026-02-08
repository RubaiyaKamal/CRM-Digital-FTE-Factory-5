# Web Form Builder Skill

## Skill Definition

**Name:** web-form-builder
**Version:** 1.0.0
**Type:** Frontend Integration
**Complexity:** Beginner-Intermediate

## Description

Creates a complete, production-ready web support form component with validation, submission handling, success states, and ticket tracking. **REQUIRED deliverable for hackathon.**

## When to Use This Skill

- Building customer-facing support form
- Creating embeddable contact widgets
- Implementing form-to-ticket workflows
- Setting up web as a support channel

## Inputs

### Component Props
```typescript
interface SupportFormProps {
    apiEndpoint?: string;  // Default: '/api/support/submit'
    categories?: Category[];
    onSuccess?: (ticketId: string) => void;
    onError?: (error: string) => void;
}
```

### Form Data Structure
```typescript
interface FormData {
    name: string;
    email: string;
    subject: string;
    category: 'general' | 'technical' | 'billing' | 'feedback' | 'bug_report';
    priority: 'low' | 'medium' | 'high';
    message: string;
}
```

## Outputs

### API Request
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "API Authentication Issue",
    "category": "technical",
    "priority": "medium",
    "message": "I'm having trouble authenticating..."
}
```

### API Response
```json
{
    "ticket_id": "uuid-1234-5678",
    "message": "Thank you for contacting us!",
    "estimated_response_time": "Usually within 5 minutes"
}
```

## Implementation Steps

### Step 1: Create React Component
```jsx
import React, { useState } from 'react';

const CATEGORIES = [
    { value: 'general', label: 'General Question' },
    { value: 'technical', label: 'Technical Support' },
    { value: 'billing', label: 'Billing Inquiry' },
    { value: 'bug_report', label: 'Bug Report' },
    { value: 'feedback', label: 'Feedback' }
];

export default function SupportForm({ apiEndpoint = '/api/support/submit' }) {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        subject: '',
        category: 'general',
        priority: 'medium',
        message: ''
    });

    const [status, setStatus] = useState('idle');
    const [ticketId, setTicketId] = useState(null);
    const [error, setError] = useState(null);

    // Form handling implementation...
}
```

### Step 2: Implement Validation
```javascript
const validateForm = () => {
    if (formData.name.trim().length < 2) {
        setError('Please enter your name (at least 2 characters)');
        return false;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        setError('Please enter a valid email address');
        return false;
    }
    if (formData.subject.trim().length < 5) {
        setError('Please enter a subject (at least 5 characters)');
        return false;
    }
    if (formData.message.trim().length < 10) {
        setError('Please describe your issue in more detail');
        return false;
    }
    return true;
};
```

### Step 3: Handle Submission
```javascript
const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!validateForm()) return;

    setStatus('submitting');

    try {
        const response = await fetch(apiEndpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Submission failed');
        }

        const data = await response.json();
        setTicketId(data.ticket_id);
        setStatus('success');
    } catch (err) {
        setError(err.message);
        setStatus('error');
    }
};
```

### Step 4: Create Backend Handler
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, validator

router = APIRouter(prefix="/support")

class SupportFormSubmission(BaseModel):
    name: str
    email: EmailStr
    subject: str
    category: str
    priority: str = 'medium'
    message: str

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        return v.strip()

    @validator('message')
    def message_must_have_content(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Message must be at least 10 characters')
        return v.strip()

@router.post("/submit")
async def submit_support_form(submission: SupportFormSubmission):
    ticket_id = str(uuid.uuid4())

    message_data = {
        'channel': 'web_form',
        'channel_message_id': ticket_id,
        'customer_email': submission.email,
        'customer_name': submission.name,
        'subject': submission.subject,
        'content': submission.message,
        'category': submission.category,
        'priority': submission.priority,
        'received_at': datetime.utcnow().isoformat()
    }

    await publish_to_kafka('fte.tickets.incoming', message_data)
    await create_ticket_record(ticket_id, message_data)

    return {
        'ticket_id': ticket_id,
        'message': 'Thank you for contacting us!',
        'estimated_response_time': 'Usually within 5 minutes'
    }
```

## Testing Checklist

- [ ] Form validates required fields
- [ ] Email validation works correctly
- [ ] Character limits enforced
- [ ] Success state shows ticket ID
- [ ] Error state shows error message
- [ ] Loading state shows during submission
- [ ] Form resets after successful submission
- [ ] Backend validation matches frontend
- [ ] CORS configured correctly
- [ ] Ticket created in database

## Styling (Tailwind CSS)

```jsx
<div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
    <h2 className="text-2xl font-bold text-gray-900 mb-2">
        Contact Support
    </h2>

    <form onSubmit={handleSubmit} className="space-y-6">
        <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
                Your Name *
            </label>
            <input
                type="text"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
            />
        </div>

        {/* Additional fields... */}

        <button
            type="submit"
            disabled={status === 'submitting'}
            className={`w-full py-3 px-4 rounded-lg font-medium text-white ${
                status === 'submitting'
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700'
            }`}
        >
            {status === 'submitting' ? 'Submitting...' : 'Submit Support Request'}
        </button>
    </form>
</div>
```

## Error Handling

```javascript
// Network errors
try {
    const response = await fetch(apiEndpoint, {...});
} catch (err) {
    if (err.name === 'TypeError') {
        setError('Network error. Please check your connection.');
    } else {
        setError('An unexpected error occurred.');
    }
}

// Validation errors
if (!response.ok) {
    const errorData = await response.json();
    if (errorData.detail && Array.isArray(errorData.detail)) {
        // Pydantic validation errors
        const errors = errorData.detail.map(e => e.msg).join(', ');
        setError(errors);
    } else {
        setError(errorData.detail || 'Submission failed');
    }
}
```

## Accessibility

```jsx
// Add ARIA labels
<label htmlFor="name" className="...">Your Name *</label>
<input
    id="name"
    type="text"
    aria-required="true"
    aria-invalid={error && error.includes('name')}
    {...}
/>

// Error messages
{error && (
    <div role="alert" className="p-4 bg-red-50 text-red-700">
        {error}
    </div>
)}
```

## Example Complete Component

See `src/web-form/SupportForm.jsx` for full implementation with:
- Success screen with ticket ID
- Character counter for message field
- Priority selection
- Category dropdown
- Responsive design
- Loading spinner
- Error handling

## Dependencies

```json
{
    "react": "^18.2.0",
    "next": "^14.0.0",
    "tailwindcss": "^3.4.0"
}
```

## Related Skills

- **channel-response-formatter** - Format web responses
- **customer-identification** - Identify customers by email
- **e2e-testing** - Test form submission flow
