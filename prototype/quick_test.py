"""Quick test of agent with a few sample tickets"""
from agent import CustomerSuccessAgent
from models import Channel

print("="*60)
print("QUICK AGENT TEST")
print("="*60)

# Initialize agent (KB already built)
agent = CustomerSuccessAgent()

# Test cases
tests = [
    {
        "name": "Simple How-To",
        "message": "How do I reset my password?",
        "channel": Channel.EMAIL,
        "customer": "user@example.com",
        "expect_escalate": False
    },
    {
        "name": "Billing Dispute",
        "message": "I was charged twice this month! I need a refund immediately.",
        "channel": Channel.EMAIL,
        "customer": "billing@company.com",
        "expect_escalate": True
    },
    {
        "name": "WhatsApp Question",
        "message": "Can I export my tasks to Excel?",
        "channel": Channel.WHATSAPP,
        "customer": "+1-555-0123",
        "expect_escalate": False
    },
    {
        "name": "Angry Customer",
        "message": "This is UNACCEPTABLE!! I'm canceling my subscription!",
        "channel": Channel.EMAIL,
        "customer": "angry@customer.com",
        "expect_escalate": True
    }
]

results = []
for i, test in enumerate(tests, 1):
    print(f"\n{'='*60}")
    print(f"TEST {i}: {test['name']}")
    print(f"{'='*60}")
    print(f"Message: {test['message']}")
    print(f"Channel: {test['channel'].value}")
    print()

    result = agent.process_message(
        message=test['message'],
        channel=test['channel'],
        customer_id=test['customer']
    )

    correct = result.should_escalate == test['expect_escalate']
    results.append(correct)

    print(f"\nExpected escalation: {test['expect_escalate']}")
    print(f"Actual escalation: {result.should_escalate}")
    print(f"Result: {'PASS' if correct else 'FAIL'}")
    print(f"Sentiment: {result.sentiment.label.value} ({result.sentiment.score:.2f})")
    print(f"Processing time: {result.processing_time_ms:.0f}ms")

# Summary
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print(f"Tests passed: {sum(results)}/{len(results)}")
print(f"Accuracy: {sum(results)/len(results)*100:.0f}%")
print()
