"""
Channel-specific response formatting.
Each channel has different expectations for tone, length, and structure.
"""
import re
from typing import List
from models import Channel


class ChannelFormatter:
    """Formats responses appropriately for each channel"""

    def __init__(self):
        # Channel-specific length limits
        self.length_limits = {
            Channel.EMAIL: 2000,  # characters
            Channel.WHATSAPP: 1600,  # WhatsApp API limit
            Channel.WEB_FORM: 1200,  # characters
        }

        # WhatsApp preferred message length (will break into multiple if longer)
        self.whatsapp_preferred_length = 300

    def format(
        self,
        response: str,
        channel: Channel,
        customer_name: str = None,
        include_links: bool = True
    ) -> str:
        """Format response for specific channel"""

        if channel == Channel.EMAIL:
            return self._format_email(response, customer_name, include_links)
        elif channel == Channel.WHATSAPP:
            return self._format_whatsapp(response, customer_name)
        elif channel == Channel.WEB_FORM:
            return self._format_web_form(response, customer_name, include_links)
        else:
            return response

    def _format_email(self, response: str, customer_name: str, include_links: bool) -> str:
        """
        Email formatting:
        - Formal greeting with first name
        - Detailed content with formatting
        - Professional signature
        - Documentation links
        """
        # Extract first name if email provided
        first_name = self._extract_first_name(customer_name) if customer_name else "there"

        # Build formatted email
        parts = []

        # Greeting
        parts.append(f"Hi {first_name},\n")

        # Main content (keep markdown formatting)
        parts.append(response.strip())

        # Closing and signature
        parts.append("\n\nLet me know if you have any other questions - I'm here to help!")
        parts.append("\nBest regards,")
        parts.append("CloudFlow Support Team")

        formatted = "\n".join(parts)

        # Ensure within length limit
        if len(formatted) > self.length_limits[Channel.EMAIL]:
            formatted = formatted[:self.length_limits[Channel.EMAIL] - 50] + "...\n\n[continued in next message]"

        return formatted

    def _format_whatsapp(self, response: str, customer_name: str) -> str:
        """
        WhatsApp formatting:
        - Ultra-concise
        - No formal greeting/signature
        - Break into multiple messages if >300 chars
        - Casual tone
        - Emojis acceptable
        """
        first_name = self._extract_first_name(customer_name) if customer_name else None

        # Simplify response (remove markdown formatting for readability)
        simplified = self._simplify_for_whatsapp(response)

        # If short enough, add friendly greeting
        if len(simplified) < 250:
            if first_name:
                formatted = f"Hey {first_name}! 👋\n\n{simplified}"
            else:
                formatted = f"Hey! 👋\n\n{simplified}"
        else:
            formatted = simplified

        # Break into multiple messages if too long
        if len(formatted) > self.whatsapp_preferred_length:
            messages = self._break_into_messages(formatted, self.whatsapp_preferred_length)
            formatted = "\n\n---\n\n".join(messages)  # Separate with visual break

        # Ensure within WhatsApp API limit
        if len(formatted) > self.length_limits[Channel.WHATSAPP]:
            formatted = formatted[:self.length_limits[Channel.WHATSAPP] - 50] + "..."

        return formatted

    def _format_web_form(self, response: str, customer_name: str, include_links: bool) -> str:
        """
        Web form formatting:
        - Semi-formal
        - Concise greeting
        - Keep markdown formatting (will render in UI)
        - Simple signature
        """
        first_name = self._extract_first_name(customer_name) if customer_name else "there"

        # Build formatted response
        parts = []

        # Brief greeting
        parts.append(f"Hi {first_name},\n")

        # Main content (keep markdown)
        parts.append(response.strip())

        # Simple closing
        parts.append("\n\nLet me know if you need more help!")
        parts.append("\n- CloudFlow Support")

        formatted = "\n".join(parts)

        # Ensure within length limit
        if len(formatted) > self.length_limits[Channel.WEB_FORM]:
            formatted = formatted[:self.length_limits[Channel.WEB_FORM] - 50] + "..."

        return formatted

    def _extract_first_name(self, identifier: str) -> str:
        """Extract first name from email or full name"""
        if not identifier:
            return "there"

        # If it's an email, take part before @
        if '@' in identifier:
            username = identifier.split('@')[0]
            # Capitalize and return (handle john.doe@example.com -> John)
            name = username.split('.')[0].capitalize()
            return name

        # If it's a name, take first part
        if ' ' in identifier:
            return identifier.split()[0].capitalize()

        return identifier.capitalize()

    def _simplify_for_whatsapp(self, text: str) -> str:
        """Simplify text for WhatsApp (remove markdown, condense)"""
        # Remove markdown bold/italic
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)

        # Convert markdown headers to plain text
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)

        # Convert bullet points to simple dashes
        text = re.sub(r'^\*\s+', '• ', text, flags=re.MULTILINE)
        text = re.sub(r'^\-\s+', '• ', text, flags=re.MULTILINE)

        # Convert numbered lists to simple format
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)

        # Remove extra whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Replace "Go to Settings → Account" style with arrows for brevity
        text = text.replace(' → ', ' → ')

        return text.strip()

    def _break_into_messages(self, text: str, max_length: int) -> List[str]:
        """Break long text into multiple messages at natural boundaries"""
        messages = []
        current = ""

        # Split by paragraphs first
        paragraphs = text.split('\n\n')

        for para in paragraphs:
            # If adding this paragraph would exceed limit, start new message
            if len(current) + len(para) + 2 > max_length and current:
                messages.append(current.strip())
                current = para
            else:
                if current:
                    current += "\n\n" + para
                else:
                    current = para

        # Add remaining
        if current:
            messages.append(current.strip())

        return messages

    def add_documentation_links(self, text: str, links: List[str]) -> str:
        """Add documentation links at the end of response"""
        if not links:
            return text

        text += "\n\n📚 Related docs:"
        for link in links:
            text += f"\n- {link}"

        return text


# Test the formatter
if __name__ == "__main__":
    formatter = ChannelFormatter()

    sample_response = """To reset your password:

1. Go to the login page at app.techcorp-cloudflow.com
2. Click "Forgot Password"
3. Enter your email address
4. Check your inbox for the reset link (expires in 1 hour)
5. Create a new password

**IMPORTANT:** Check your spam folder if you don't see the email within 5 minutes."""

    print("=" * 60)
    print("EMAIL FORMAT:")
    print("=" * 60)
    email_formatted = formatter.format(sample_response, Channel.EMAIL, "sarah.johnson@example.com")
    print(email_formatted)

    print("\n" + "=" * 60)
    print("WHATSAPP FORMAT:")
    print("=" * 60)
    whatsapp_formatted = formatter.format(sample_response, Channel.WHATSAPP, "Sarah")
    print(whatsapp_formatted)

    print("\n" + "=" * 60)
    print("WEB FORM FORMAT:")
    print("=" * 60)
    web_formatted = formatter.format(sample_response, Channel.WEB_FORM, "Sarah Johnson")
    print(web_formatted)
