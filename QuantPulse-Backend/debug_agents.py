"""
QuantPulse Agent Diagnostic Script
===================================
Run this to see exactly why CrewAI agents fail to load.

Usage:
    python debug_agents.py
"""

import os
import sys
import traceback

print("=" * 60)
print("🔍 QuantPulse Agent Diagnostic Tool")
print("=" * 60)

# ─────────────────────────────────────────────────────────────
# Step 0: Load .env so API keys are available
# ─────────────────────────────────────────────────────────────
print("\n[0/5] Loading .env file...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("  ✅ .env loaded")
except ImportError:
    print("  ❌ python-dotenv not installed! Run: pip install python-dotenv")
except Exception as e:
    print(f"  ⚠️ .env load failed: {e}")

# ─────────────────────────────────────────────────────────────
# Step 1: Check API Keys
# ─────────────────────────────────────────────────────────────
print("\n[1/5] Checking API Keys...")
groq_key = os.getenv("GROQ_API_KEY")
serper_key = os.getenv("SERPER_API_KEY")

if groq_key:
    print(f"  ✅ GROQ_API_KEY found ({groq_key[:8]}...{groq_key[-4:]})")
else:
    print("  ❌ GROQ_API_KEY is MISSING from .env!")

if serper_key:
    print(f"  ✅ SERPER_API_KEY found ({serper_key[:8]}...{serper_key[-4:]})")
else:
    print("  ❌ SERPER_API_KEY is MISSING from .env!")

# ─────────────────────────────────────────────────────────────
# Step 2: Test crewai import
# ─────────────────────────────────────────────────────────────
print("\n[2/5] Importing crewai...")
try:
    import crewai
    print(f"  ✅ crewai v{crewai.__version__} imported successfully")
except Exception:
    print("  ❌ CRITICAL ERROR importing crewai:")
    traceback.print_exc()
    print("\n  💡 Fix: pip install crewai")
    print("     Or if pydantic conflict: pip install 'crewai[tools]'")

# ─────────────────────────────────────────────────────────────
# Step 3: Test langchain-groq import
# ─────────────────────────────────────────────────────────────
print("\n[3/5] Importing langchain_groq...")
try:
    from langchain_groq import ChatGroq
    print("  ✅ langchain_groq imported successfully")
    
    # Try to instantiate it
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=groq_key,
            temperature=0.3,
        )
        print(f"  ✅ ChatGroq instantiated (model: llama-3.3-70b-versatile)")
    else:
        print("  ⚠️ Skipping instantiation — no GROQ_API_KEY")

except Exception:
    print("  ❌ CRITICAL ERROR importing langchain_groq:")
    traceback.print_exc()
    print("\n  💡 Fix: pip install langchain-groq")

# ─────────────────────────────────────────────────────────────
# Step 4: Test crewai_tools import
# ─────────────────────────────────────────────────────────────
print("\n[4/5] Importing crewai_tools...")
try:
    from crewai_tools import SerperDevTool
    print("  ✅ crewai_tools imported successfully")

    # Try instantiating the search tool
    if serper_key:
        tool = SerperDevTool()
        print(f"  ✅ SerperDevTool instantiated")
    else:
        print("  ⚠️ Skipping instantiation — no SERPER_API_KEY")

except Exception:
    print("  ❌ CRITICAL ERROR importing crewai_tools:")
    traceback.print_exc()
    print("\n  💡 Fix: pip install crewai-tools")
    print("     Or:  pip install 'crewai[tools]'")

# ─────────────────────────────────────────────────────────────
# Step 5: Test full Agent creation (the actual crash point)
# ─────────────────────────────────────────────────────────────
print("\n[5/5] Creating a test Agent...")
try:
    from crewai import Agent

    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        from langchain_groq import ChatGroq
        test_llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=groq_key,
            temperature=0.3,
        )
        test_agent = Agent(
            role="Test Agent",
            goal="Test that agent creation works",
            backstory="I am a diagnostic test agent.",
            llm=test_llm,
            verbose=False,
            allow_delegation=False,
        )
        print(f"  ✅ Test Agent created successfully: {test_agent.role}")
    else:
        print("  ⚠️ Skipping agent creation — no GROQ_API_KEY")

except Exception:
    print("  ❌ CRITICAL ERROR creating Agent:")
    traceback.print_exc()
    print("\n  💡 This is likely a pydantic or dependency version conflict.")
    print("     Try: pip install --upgrade crewai pydantic")

# ─────────────────────────────────────────────────────────────
# Final Verdict
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
all_ok = True
try:
    import crewai
    from langchain_groq import ChatGroq
    from crewai_tools import SerperDevTool
except Exception:
    all_ok = False

if all_ok and groq_key and serper_key:
    print("✅ Agents are Ready! All imports and API keys verified.")
else:
    issues = []
    if not groq_key:
        issues.append("GROQ_API_KEY missing")
    if not serper_key:
        issues.append("SERPER_API_KEY missing")
    if not all_ok:
        issues.append("Import errors (see above)")
    print(f"❌ CRITICAL ERROR: {' | '.join(issues)}")
    print("   Fix the errors above, then run this script again.")
print("=" * 60)
