"""
Setup script for Customer Success Agent prototype.
Installs dependencies and prepares knowledge base.
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"{description}...")
    print(f"{'='*60}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ SUCCESS")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"❌ FAILED")
        if result.stderr:
            print(result.stderr)
        return False

    return True


def main():
    print("=" * 60)
    print("Customer Success Agent - Prototype Setup")
    print("=" * 60)

    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        sys.exit(1)

    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

    if not in_venv:
        print("\n⚠️ WARNING: Not in a virtual environment")
        print("It's recommended to use a virtual environment:")
        print("  python -m venv venv")
        print("  source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)

    # Install dependencies
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing dependencies"
    ):
        print("\n❌ Failed to install dependencies")
        sys.exit(1)

    # Check if knowledge base exists
    kb_index = Path("kb_index.pkl")
    docs_file = Path("../context/product-docs.md")

    if kb_index.exists():
        print("\n✅ Knowledge base index already exists")
    elif docs_file.exists():
        print(f"\n📚 Building knowledge base from {docs_file}...")
        print("This may take a few minutes on first run...")

        if not run_command(
            f"{sys.executable} knowledge_base.py",
            "Building knowledge base"
        ):
            print("\n⚠️ Knowledge base build had issues, but continuing...")
    else:
        print(f"\n⚠️ WARNING: Product documentation not found at {docs_file}")
        print("Agent will run with limited capabilities")

    # Run tests
    print("\n" + "=" * 60)
    print("Setup complete! Ready to test.")
    print("=" * 60)

    print("\nTo test the agent:")
    print(f"  {sys.executable} test_agent.py")

    print("\nTo test individual components:")
    print(f"  {sys.executable} sentiment_analyzer.py")
    print(f"  {sys.executable} channel_formatter.py")
    print(f"  {sys.executable} escalation_engine.py")

    print("\nTo use the agent in your code:")
    print("  from agent import CustomerSuccessAgent")
    print("  agent = CustomerSuccessAgent()")
    print("  result = agent.process_message('How do I reset my password?', ...)")

    print()


if __name__ == "__main__":
    main()
