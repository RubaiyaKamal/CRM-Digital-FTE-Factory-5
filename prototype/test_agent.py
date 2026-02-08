"""
Test runner for Customer Success Agent.
Tests agent with sample tickets from context/sample-tickets.json
"""
import json
import sys
from pathlib import Path
from typing import List, Dict
from agent import CustomerSuccessAgent
from models import Channel


class AgentTester:
    """Test agent with sample tickets"""

    def __init__(self):
        self.agent = CustomerSuccessAgent()
        self.test_results = []

    def load_sample_tickets(self, tickets_file: Path) -> List[Dict]:
        """Load sample tickets from JSON file"""
        print(f"Loading sample tickets from {tickets_file}...")
        with open(tickets_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        tickets = data['tickets']
        print(f"Loaded {len(tickets)} tickets\n")
        return tickets

    def run_tests(
        self,
        tickets: List[Dict],
        max_tests: int = 30,
        tickets_per_channel: int = 10
    ):
        """
        Run tests with sample tickets.

        Args:
            tickets: List of ticket dictionaries
            max_tests: Maximum number of tests to run
            tickets_per_channel: Number of tickets to test per channel
        """
        print("=" * 70)
        print("CUSTOMER SUCCESS AGENT - PROTOTYPE TESTING")
        print("=" * 70 + "\n")

        # Group tickets by channel
        by_channel = {
            "email": [t for t in tickets if t["channel"] == "email"],
            "whatsapp": [t for t in tickets if t["channel"] == "whatsapp"],
            "web_form": [t for t in tickets if t["channel"] == "web_form"],
        }

        # Test 10 per channel
        tests_to_run = []
        for channel, channel_tickets in by_channel.items():
            tests_to_run.extend(channel_tickets[:tickets_per_channel])

        print(f"Testing {len(tests_to_run)} tickets:")
        print(f"  - Email: {sum(1 for t in tests_to_run if t['channel'] == 'email')}")
        print(f"  - WhatsApp: {sum(1 for t in tests_to_run if t['channel'] == 'whatsapp')}")
        print(f"  - Web Form: {sum(1 for t in tests_to_run if t['channel'] == 'web_form')}\n")
        print("=" * 70 + "\n")

        # Run tests
        for i, ticket in enumerate(tests_to_run, 1):
            print(f"{'='*70}")
            print(f"TEST {i}/{len(tests_to_run)}: {ticket['id']}")
            print(f"{'='*70}\n")

            result = self._test_ticket(ticket)
            self.test_results.append(result)

            # Print summary
            self._print_test_result(ticket, result)
            print()

        # Print overall summary
        self._print_summary()

    def _test_ticket(self, ticket: Dict) -> Dict:
        """Test a single ticket and return results"""
        # Map channel string to enum
        channel_map = {
            "email": Channel.EMAIL,
            "whatsapp": Channel.WHATSAPP,
            "web_form": Channel.WEB_FORM
        }
        channel = channel_map[ticket["channel"]]

        # Process message
        response = self.agent.process_message(
            message=ticket["message"],
            channel=channel,
            customer_id=ticket["from"],
            subject=ticket.get("subject")
        )

        # Check if escalation decision matches expectation
        expected_escalation = "ESCALATE" in ticket.get("expected_resolution", "")
        escalation_correct = response.should_escalate == expected_escalation

        return {
            "ticket_id": ticket["id"],
            "channel": ticket["channel"],
            "category": ticket["category"],
            "expected_escalation": expected_escalation,
            "actual_escalation": response.should_escalate,
            "escalation_correct": escalation_correct,
            "sentiment_score": response.sentiment.score,
            "sentiment_label": response.sentiment.label.value,
            "kb_confidence": response.confidence,
            "processing_time_ms": response.processing_time_ms,
            "response_length": len(response.formatted_response),
            "priority": response.priority.value
        }

    def _print_test_result(self, ticket: Dict, result: Dict):
        """Print individual test result"""
        print(f"Ticket: {ticket['id']}")
        print(f"Channel: {ticket['channel']}")
        print(f"Category: {ticket['category']}")
        print(f"Message: {ticket['message'][:100]}{'...' if len(ticket['message']) > 100 else ''}\n")

        print(f"Expected escalation: {result['expected_escalation']}")
        print(f"Actual escalation: {result['actual_escalation']}")

        if result['escalation_correct']:
            print("✅ ESCALATION DECISION: CORRECT")
        else:
            print("❌ ESCALATION DECISION: INCORRECT")

        print(f"\nSentiment: {result['sentiment_label']} (score: {result['sentiment_score']:.2f})")
        print(f"KB Confidence: {result['kb_confidence']:.2f}")
        print(f"Priority: {result['priority']}")
        print(f"Response Length: {result['response_length']} chars")
        print(f"Processing Time: {result['processing_time_ms']:.0f}ms")

    def _print_summary(self):
        """Print overall test summary"""
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70 + "\n")

        total = len(self.test_results)
        correct_escalations = sum(1 for r in self.test_results if r['escalation_correct'])
        accuracy = (correct_escalations / total * 100) if total > 0 else 0

        print(f"Total Tests: {total}")
        print(f"Correct Escalation Decisions: {correct_escalations}/{total} ({accuracy:.1f}%)\n")

        # Escalation breakdown
        escalated = sum(1 for r in self.test_results if r['actual_escalation'])
        handled_by_ai = total - escalated
        print(f"Tickets Escalated: {escalated} ({escalated/total*100:.1f}%)")
        print(f"Tickets Handled by AI: {handled_by_ai} ({handled_by_ai/total*100:.1f}%)\n")

        # By channel
        print("By Channel:")
        for channel in ["email", "whatsapp", "web_form"]:
            channel_results = [r for r in self.test_results if r['channel'] == channel]
            if channel_results:
                channel_escalated = sum(1 for r in channel_results if r['actual_escalation'])
                print(f"  {channel.upper()}: {len(channel_results)} tests, "
                      f"{channel_escalated} escalated ({channel_escalated/len(channel_results)*100:.1f}%)")

        # Average metrics
        avg_sentiment = sum(r['sentiment_score'] for r in self.test_results) / total
        avg_confidence = sum(r['kb_confidence'] for r in self.test_results) / total
        avg_time = sum(r['processing_time_ms'] for r in self.test_results) / total

        print(f"\nAverage Metrics:")
        print(f"  Sentiment Score: {avg_sentiment:.2f}")
        print(f"  KB Confidence: {avg_confidence:.2f}")
        print(f"  Processing Time: {avg_time:.0f}ms")

        # Response length by channel
        print(f"\nAverage Response Length by Channel:")
        for channel in ["email", "whatsapp", "web_form"]:
            channel_results = [r for r in self.test_results if r['channel'] == channel]
            if channel_results:
                avg_length = sum(r['response_length'] for r in channel_results) / len(channel_results)
                print(f"  {channel.upper()}: {avg_length:.0f} chars")

        # Check WhatsApp length compliance
        whatsapp_results = [r for r in self.test_results if r['channel'] == 'whatsapp']
        if whatsapp_results:
            whatsapp_over_limit = sum(1 for r in whatsapp_results if r['response_length'] > 1600)
            whatsapp_over_preferred = sum(1 for r in whatsapp_results if r['response_length'] > 300)
            print(f"\nWhatsApp Length Compliance:")
            print(f"  Over API limit (1600): {whatsapp_over_limit}/{len(whatsapp_results)}")
            print(f"  Over preferred (300): {whatsapp_over_preferred}/{len(whatsapp_results)}")

        # Performance evaluation
        print(f"\n{'='*70}")
        print("PERFORMANCE EVALUATION")
        print(f"{'='*70}\n")

        if accuracy >= 90:
            print("✅ EXCELLENT: Escalation decision accuracy >=90%")
        elif accuracy >= 80:
            print("✅ GOOD: Escalation decision accuracy >=80%")
        elif accuracy >= 70:
            print("⚠️ FAIR: Escalation decision accuracy >=70% (needs improvement)")
        else:
            print("❌ POOR: Escalation decision accuracy <70% (significant issues)")

        target_resolution = 70  # 70% should be handled by AI
        if handled_by_ai/total >= 0.65 and handled_by_ai/total <= 0.75:
            print("✅ OPTIMAL: AI resolution rate within target range (65-75%)")
        elif handled_by_ai/total >= 0.60:
            print("✅ ACCEPTABLE: AI resolution rate acceptable (60%+)")
        else:
            print("⚠️ CONCERN: AI resolution rate outside target range")

        if avg_time < 2000:
            print(f"✅ FAST: Average response time <2 seconds")
        elif avg_time < 3000:
            print(f"✅ ACCEPTABLE: Average response time <3 seconds")
        else:
            print(f"⚠️ SLOW: Average response time >{avg_time/1000:.1f} seconds")

        print()


def main():
    """Main test runner"""
    # Load sample tickets
    tickets_file = Path(__file__).parent.parent / "context" / "sample-tickets.json"

    if not tickets_file.exists():
        print(f"Error: Sample tickets file not found at {tickets_file}")
        sys.exit(1)

    # Create tester and run tests
    tester = AgentTester()
    tickets = tester.load_sample_tickets(tickets_file)

    # Run tests (10 per channel = 30 total)
    tester.run_tests(tickets, tickets_per_channel=10)


if __name__ == "__main__":
    main()
