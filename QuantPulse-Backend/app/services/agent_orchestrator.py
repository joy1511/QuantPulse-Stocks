# =============================================================================
# ENVIRONMENT SETUP — Must execute BEFORE any other imports
# =============================================================================
import os
import time
import logging
import traceback

# ---- Disable CrewAI / OpenTelemetry telemetry (prints "Menu", may hang) ----
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"

# ---- LiteLLM Optimization: Prevent slow remote fetch of cost map ----
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"

from dotenv import load_dotenv
load_dotenv()

# NOTE: crewai imports are DEFERRED to _execute_crew() to avoid blocking
# uvicorn port binding on Render. CrewAI pulls in chromadb, litellm,
# opentelemetry (300+ deps) which takes 30-60s to import.

logger = logging.getLogger(__name__)

# =============================================================================
# Validate API Keys at import time — warn if missing, don't crash
# =============================================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

if not GROQ_API_KEY:
    logger.error("❌ GROQ_API_KEY not found. War Room agents will fail.")
if not SERPER_API_KEY:
    logger.warning("⚠️ SERPER_API_KEY not found. Search tool and live price fallback disabled.")

logger.info("✅ API key check complete")
# ... (existing imports)

# =============================================================================
# THE WAR ROOM — Zero-Fail Entry Point
# =============================================================================

def run_war_room(
    ticker: str,
    lstm_result: dict,
    regime_result: dict,
    vix_level: float,
    features_summary: dict,
) -> dict:
    """
    Run the multi-agent War Room debate with timeout protection.

    ZERO-FAIL GUARANTEE:
    - If agents succeed → returns full AI Investment Memo
    - If agents timeout (25s) → returns fallback memo with timeout notice
    - If agents fail → returns fallback memo from real LSTM + HMM data
    - NEVER raises an exception. NEVER returns a 500.
    """

    # Phase A: Minimal buffer
    logger.info("⏳ Phase A: Initializing War Room...")
    time.sleep(1)

    # ---- PRODUCTION OPTIMIZATION ----
    # Only skip agents if FORCE_SIMULATION_MODE is explicitly set
    if os.getenv("FORCE_SIMULATION_MODE") == "true":
        logger.info("🚀 Simulation Mode: Skipping AI Agents (FORCE_SIMULATION_MODE=true)")
        return _build_fallback_memo(ticker, lstm_result, regime_result, vix_level, features_summary)

    try:
        # Phase B: Run the crew with timeout protection
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("War Room execution exceeded 25 seconds")
        
        # Set 25-second timeout (only on Unix systems)
        if hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(25)
        
        try:
            result = _execute_crew(ticker, lstm_result, regime_result, vix_level, features_summary)
            
            # Cancel alarm if successful
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
            
            return result
            
        except TimeoutError:
            logger.error("⏱️ War Room timeout (25s) - returning fallback memo")
            result = _build_fallback_memo(ticker, lstm_result, regime_result, vix_level, features_summary)
            result["error"] = "AI agents timed out (25s limit) - showing technical analysis"
            return result
            
    except Exception as e:
        # Phase C: Fail-safe — return fallback memo from REAL data
        error_msg = f"War Room failed: {type(e).__name__}: {e}"
        logger.error(f"❌ {error_msg}")
        logger.error(traceback.format_exc())
        logger.warning("⚠️ Falling back to rule-based Investment Memo...")
        result = _build_fallback_memo(ticker, lstm_result, regime_result, vix_level, features_summary)
        result["error"] = error_msg
        return result
    finally:
        # Always cancel alarm
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)


# =============================================================================
# CREW EXECUTION — Core logic (may raise, caught by run_war_room)
# =============================================================================

def _execute_crew(
    ticker: str,
    lstm_result: dict,
    regime_result: dict,
    vix_level: float,
    features_summary: dict,
) -> dict:

    # ---- Lazy import CrewAI (deferred from module level for fast startup) ----
    from crewai import Agent, Task, Crew, Process, LLM

    # Graceful import — crewai-tools may be incompatible
    try:
        from crewai_tools import SerperDevTool
        _serper_available = True
    except (ImportError, Exception) as e:
        SerperDevTool = None
        _serper_available = False
        logger.warning(f"⚠️ crewai_tools import failed: {e}")

    # ---- LLM Brain (Groq - Fast & Free) ----
    # llama-3.3-70b-versatile: Fast, high-quality, and generous free tier
    # Groq provides ultra-fast inference with excellent reasoning capabilities
    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
    )

    # ---- Tool (only for Fundamentalist, if available) ----
    search_tool = None
    if _serper_available and SerperDevTool and SERPER_API_KEY:
        try:
            search_tool = SerperDevTool(api_key=os.getenv("SERPER_API_KEY", ""))
        except Exception as e:
            logger.warning(f"⚠️ SerperDevTool init failed: {e}")
            search_tool = None

    # ---- Extract data for prompts ----
    lstm_prob = lstm_result.get("probability", 0.5)
    lstm_signal = lstm_result.get("signal", "Neutral")
    regime = regime_result.get("regime", "Sideways")
    regime_confidence = regime_result.get("confidence", 0.5)
    rsi = features_summary.get("rsi", 50)
    macd = features_summary.get("macd", 0)
    bollinger = features_summary.get("bollinger_pctb", 0.5)

    # =====================================================================
    # AGENT 1: The Fundamentalist
    # =====================================================================
    fundamentalist = Agent(
        role="Fundamentalist Analyst",
        goal=(
            f"Research the latest news and macro conditions for {ticker} on NSE India. "
            f"The current India VIX is {vix_level:.1f}. "
            f"Assess whether the macro environment supports or threatens this stock."
        ),
        backstory=(
            "You are a seasoned macro analyst at a top Indian hedge fund. "
            "You read The Economic Times, Moneycontrol, and Bloomberg every morning. "
            "You never ignore VIX — above 22 means the market is scared."
        ),
        tools=[search_tool] if search_tool else [],
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    # =====================================================================
    # AGENT 2: The Technician
    # =====================================================================
    technician = Agent(
        role="Technical Analyst (Chartist)",
        goal=(
            f"Analyze the technical signals for {ticker}. "
            f"LSTM neural network: Probability={lstm_prob:.1%}, Signal={lstm_signal}. "
            f"Indicators: RSI={rsi}, MACD={macd:.4f}, Bollinger %B={bollinger:.4f}. "
            f"Confirm or challenge the LSTM signal."
        ),
        backstory=(
            "You are an expert technical analyst with 15 years of experience. "
            "You trust the LSTM model but always cross-verify with RSI and Bollinger Bands. "
            "RSI > 70 = overbought, RSI < 30 = oversold."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    # =====================================================================
    # AGENT 3: The Risk Manager (THE BOSS)
    # =====================================================================
    veto_rules = []
    if "Bear" in regime or vix_level > 22:
        veto_rules.append(
            f"⚠️ VETO ACTIVE: Regime='{regime}' and/or VIX={vix_level:.1f}>22. "
            f"You MUST VETO any Buy unless exceptionally positive news justifies it."
        )
    if lstm_prob > 0.70 and "Bull" in regime:
        veto_rules.append(
            f"✅ STRONG SIGNAL: LSTM={lstm_prob:.1%} with Bull regime. "
            f"If no red flags, this is a STRONG BUY."
        )
    veto_text = "\n".join(veto_rules) if veto_rules else "No special veto rules. Use your judgment."

    risk_manager = Agent(
        role="Chief Risk Manager (Final Decision Maker)",
        goal=(
            f"You are the FINAL decision maker for {ticker}. "
            f"Regime: {regime} ({regime_confidence:.0%}). VIX: {vix_level:.1f}. "
            f"LSTM: {lstm_signal} ({lstm_prob:.1%}). "
            f"\n\nVETO RULES:\n{veto_text}\n\n"
            f"Issue FINAL VERDICT: STRONG BUY / BUY / HOLD / SELL / STRONG SELL."
        ),
        backstory=(
            "You are the Chief Risk Officer managing ₹5000 Cr in Indian equities. "
            "You have VETO power. You've seen the 2008 crash, COVID crash, and 2024 bubble. "
            "When VIX > 22, you become extremely cautious."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    # =====================================================================
    # TASKS — Each explicitly bound to its agent
    # =====================================================================
    fundamental_task = Task(
        description=(
            f"Search for \"{ticker} India stock latest news\". "
            f"India VIX is {vix_level:.1f}. "
            f"Report: bullish, bearish, or neutral? Any red flags?"
        ),
        agent=fundamentalist,
        expected_output="3-5 bullet news summary. End with: BULLISH, BEARISH, or NEUTRAL.",
    )

    technical_task = Task(
        description=(
            f"Analyze {ticker} technicals. "
            f"LSTM: {lstm_signal} ({lstm_prob:.1%}). "
            f"RSI={rsi}, MACD={macd:.4f}, Bollinger %B={bollinger:.4f}. "
            f"Confirm or contradict the AI signal."
        ),
        agent=technician,
        expected_output="Technical analysis. End with: CONFIRMS AI or CONTRADICTS AI.",
    )

    manager_task = Task(
        description=(
            f"Final Investment Decision for {ticker} (NSE)\n\n"
            f"Regime: {regime} ({regime_confidence:.0%}), VIX: {vix_level:.1f}\n"
            f"LSTM: {lstm_signal} ({lstm_prob:.1%})\n"
            f"Veto Rules: {veto_text}\n\n"
            f"Write an Investment Memo with sections:\n"
            f"1. Ticker & Date\n2. Market Regime\n3. LSTM Signal\n"
            f"4. News Analysis\n5. Technical Analysis\n"
            f"6. Risk Assessment\n7. FINAL VERDICT\n8. Justification"
        ),
        agent=risk_manager,
        expected_output="Structured Markdown Investment Memo with FINAL VERDICT.",
    )

    # =====================================================================
    # CREW — Sequential, Verbose
    # =====================================================================
    logger.info(f"🏛️ War Room convening for {ticker}...")

    # Disable memory to prevent ChromaDB/Embedding loading (heavy on Render)
    crew = Crew(
        agents=[fundamentalist, technician, risk_manager],
        tasks=[fundamental_task, technical_task, manager_task],
        process=Process.sequential,
        verbose=True,
        memory=False, 
    )

    result = crew.kickoff()

    memo_text = str(result)
    verdict = _extract_verdict(memo_text)
    logger.info(f"📋 War Room complete for {ticker}: {verdict}")

    return {
        "memo": memo_text,
        "verdict": verdict,
        "agents_used": ["Fundamentalist", "Technician", "Risk Manager"],
        "error": None,
    }


# =============================================================================
# FALLBACK MEMO — Built from REAL LSTM + HMM data (never crashes)
# =============================================================================

def _build_fallback_memo(
    ticker: str,
    lstm_result: dict,
    regime_result: dict,
    vix_level: float,
    features_summary: dict,
) -> dict:
    lstm_prob = lstm_result.get("probability", 0.5)
    lstm_signal = lstm_result.get("signal", "Neutral")
    regime = regime_result.get("regime", "Sideways")
    regime_confidence = regime_result.get("confidence", 0.5)
    rsi = features_summary.get("rsi", 50)
    macd = features_summary.get("macd", 0)
    bollinger = features_summary.get("bollinger_pctb", 0.5)

    # Apply veto logic
    if ("Bear" in regime or vix_level > 22) and lstm_signal == "Buy":
        verdict = "HOLD"
        justification = (
            f"LSTM suggests Buy ({lstm_prob:.0%}), but VETO: "
            f"Regime='{regime}', VIX={vix_level:.1f}. Capital preservation priority."
        )
    elif lstm_prob > 0.70 and "Bull" in regime:
        verdict = "STRONG BUY"
        justification = (
            f"Strong confluence: LSTM {lstm_prob:.0%} + Bull regime ({regime_confidence:.0%}). "
            f"VIX {vix_level:.1f} manageable."
        )
    elif lstm_signal == "Buy":
        verdict = "BUY"
        justification = f"LSTM Buy ({lstm_prob:.0%}) in {regime}. RSI {rsi:.1f} supports entry."
    elif lstm_signal == "Sell":
        verdict = "SELL"
        justification = f"LSTM Sell ({lstm_prob:.0%}). RSI {rsi:.1f} confirms bearish momentum."
    else:
        verdict = "HOLD"
        justification = f"Mixed signals — LSTM {lstm_prob:.0%}, regime {regime}, RSI {rsi:.1f}."

    rsi_status = "⚠️ Overbought" if rsi > 70 else ("📉 Oversold" if rsi < 30 else f"Normal ({rsi:.1f})")
    bb_status = "Extended" if bollinger > 1 else ("Compressed" if bollinger < 0 else f"Within bands ({bollinger:.2f})")

    memo = f"""## Investment Memo: {ticker} (NSE)

### 1. Market Regime
**{regime}** (confidence: {regime_confidence:.0%}) — HMM on Nifty 50

### 2. LSTM AI Signal
- Probability: **{lstm_prob:.1%}**
- Signal: **{lstm_signal}**

### 3. Technical Indicators
| Indicator | Value | Status |
|-----------|-------|--------|
| RSI (14) | {rsi:.1f} | {rsi_status} |
| MACD | {macd:.4f} | {'Bullish' if macd > 0 else 'Bearish'} |
| Bollinger %B | {bollinger:.4f} | {bb_status} |

### 4. India VIX
**{vix_level:.1f}** {'⚠️ Elevated fear' if vix_level > 22 else '✅ Calm market'}

### 5. Risk Assessment
{'🔴 VETO: Bear regime / elevated VIX. Defensive positioning.' if ('Bear' in regime or vix_level > 22) else '🟢 No veto conditions.'}

### 6. FINAL VERDICT: **{verdict}**
{justification}

---
*📊 Real LSTM + HMM data. AI agents temporarily offline.*
*⚠️ Not financial advice. Educational purposes only.*
"""

    return {
        "memo": memo,
        "verdict": verdict,
        "agents_used": ["Technical Analysis Fallback (LSTM + HMM)"],
        "error": None,
    }


# =============================================================================
# HELPERS
# =============================================================================

def _extract_verdict(memo: str) -> str:
    memo_upper = memo.upper()
    if "STRONG BUY" in memo_upper:
        return "STRONG BUY"
    if "STRONG SELL" in memo_upper:
        return "STRONG SELL"
    if "SELL" in memo_upper and "BUY" not in memo_upper:
        return "SELL"
    if "BUY" in memo_upper and "SELL" not in memo_upper:
        return "BUY"
    return "HOLD"
