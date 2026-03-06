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

def run_research_analysis(
    ticker: str,
    lstm_result: dict,
    regime_result: dict,
    vix_level: float,
    features_summary: dict,
) -> dict:
    """
    Run the multi-agent Research Analysis with timeout protection.

    ZERO-FAIL GUARANTEE:
    - If agents succeed → returns full Research Analysis Report
    - If agents timeout (25s) → returns fallback report with timeout notice
    - If agents fail → returns fallback report from real LSTM + HMM data
    - NEVER raises an exception. NEVER returns a 500.
    """

    # Phase A: Minimal buffer
    logger.info("⏳ Phase A: Initializing Research Analysis...")
    time.sleep(1)

    # ---- PRODUCTION OPTIMIZATION ----
    # Only skip agents if FORCE_SIMULATION_MODE is explicitly set
    if os.getenv("FORCE_SIMULATION_MODE") == "true":
        logger.info("🚀 Simulation Mode: Skipping AI Agents (FORCE_SIMULATION_MODE=true)")
        return _build_fallback_research_report(ticker, lstm_result, regime_result, vix_level, features_summary)

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
            logger.error("⏱️ Research Analysis timeout (25s) - returning fallback report")
            result = _build_fallback_research_report(ticker, lstm_result, regime_result, vix_level, features_summary)
            result["error"] = "AI agents timed out (25s limit) - showing technical analysis"
            return result
            
    except Exception as e:
        # Phase C: Fail-safe — return fallback report from REAL data
        error_msg = f"Research Analysis failed: {type(e).__name__}: {e}"
        logger.error(f"❌ {error_msg}")
        logger.error(traceback.format_exc())
        logger.warning("⚠️ Falling back to rule-based Research Report...")
        result = _build_fallback_research_report(ticker, lstm_result, regime_result, vix_level, features_summary)
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
    lstm_outlook = lstm_result.get("outlook", "Neutral Outlook")
    regime = regime_result.get("regime", "Sideways")
    regime_confidence = regime_result.get("confidence", 0.5)
    rsi = features_summary.get("rsi", 50)
    macd = features_summary.get("macd", 0)
    bollinger = features_summary.get("bollinger_pctb", 0.5)

    # =====================================================================
    # AGENT 1: The Fundamentalist
    # =====================================================================
    fundamentalist = Agent(
        role="Fundamentalist Research Analyst",
        goal=(
            f"Research the latest news and macro conditions for {ticker} on NSE India. "
            f"The current India VIX is {vix_level:.1f}. "
            f"Assess whether the macro environment supports or threatens this stock's outlook."
        ),
        backstory=(
            "You are a seasoned macro analyst at a top Indian research firm. "
            "You read The Economic Times, Moneycontrol, and Bloomberg every morning. "
            "You never ignore VIX — above 22 means the market is experiencing elevated volatility."
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
        role="Technical Research Analyst",
        goal=(
            f"Analyze the technical signals for {ticker}. "
            f"LSTM neural network: Probability={lstm_prob:.1%}, Outlook={lstm_outlook}. "
            f"Indicators: RSI={rsi}, MACD={macd:.4f}, Bollinger %B={bollinger:.4f}. "
            f"Confirm or challenge the LSTM outlook."
        ),
        backstory=(
            "You are an expert technical analyst with 15 years of experience in equity research. "
            "You trust the LSTM model but always cross-verify with RSI and Bollinger Bands. "
            "RSI > 70 = overbought territory, RSI < 30 = oversold territory."
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
            f"⚠️ CAUTION: Regime='{regime}' and/or VIX={vix_level:.1f}>22. "
            f"You MUST flag elevated risk unless exceptionally positive news justifies optimism."
        )
    if lstm_prob > 0.70 and "Bull" in regime:
        veto_rules.append(
            f"✅ STRONG CONFLUENCE: LSTM={lstm_prob:.1%} with Bull regime. "
            f"If no red flags, this shows strong bullish technical alignment."
        )
    veto_text = "\n".join(veto_rules) if veto_rules else "No special risk conditions. Use your judgment."

    risk_manager = Agent(
        role="Chief Research Analyst (Final Summary)",
        goal=(
            f"You are the FINAL analyst for {ticker}. "
            f"Regime: {regime} ({regime_confidence:.0%}). VIX: {vix_level:.1f}. "
            f"LSTM: {lstm_outlook} ({lstm_prob:.1%}). "
            f"\n\nRISK CONDITIONS:\n{veto_text}\n\n"
            f"Provide TECHNICAL SUMMARY: Strong Bullish / Bullish / Neutral / Bearish / Strong Bearish Outlook."
        ),
        backstory=(
            "You are the Chief Research Analyst managing equity research for institutional clients. "
            "You synthesize technical, fundamental, and risk factors into clear, objective assessments. "
            "When VIX > 22, you emphasize risk management and volatility considerations."
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
            f"Report: bullish factors, bearish factors, or neutral? Any red flags?"
        ),
        agent=fundamentalist,
        expected_output="3-5 bullet news summary. End with: BULLISH FACTORS, BEARISH FACTORS, or NEUTRAL.",
    )

    technical_task = Task(
        description=(
            f"Analyze {ticker} technicals. "
            f"LSTM: {lstm_outlook} ({lstm_prob:.1%}). "
            f"RSI={rsi}, MACD={macd:.4f}, Bollinger %B={bollinger:.4f}. "
            f"Confirm or contradict the AI outlook."
        ),
        agent=technician,
        expected_output="Technical analysis. End with: CONFIRMS AI OUTLOOK or CONTRADICTS AI OUTLOOK.",
    )

    manager_task = Task(
        description=(
            f"Final Research Analysis for {ticker} (NSE)\n\n"
            f"Regime: {regime} ({regime_confidence:.0%}), VIX: {vix_level:.1f}\n"
            f"LSTM: {lstm_outlook} ({lstm_prob:.1%})\n"
            f"Risk Conditions: {veto_text}\n\n"
            f"Write a Research Analysis Report with sections:\n"
            f"1. Ticker & Date\n2. Market Regime\n3. LSTM Analysis\n"
            f"4. News Analysis\n5. Technical Analysis\n"
            f"6. Risk Assessment\n7. TECHNICAL SUMMARY (detailed)\n8. Justification\n\n"
            f"TECHNICAL SUMMARY must be one of: Strong Bullish Outlook / Bullish Outlook / Neutral Outlook / Bearish Outlook / Strong Bearish Outlook"
        ),
        agent=risk_manager,
        expected_output="Structured Markdown Research Report with TECHNICAL SUMMARY.",
    )

    # =====================================================================
    # CREW — Sequential, Verbose
    # =====================================================================
    logger.info(f"🏛️ Research Analysis convening for {ticker}...")

    # Disable memory to prevent ChromaDB/Embedding loading (heavy on Render)
    crew = Crew(
        agents=[fundamentalist, technician, risk_manager],
        tasks=[fundamental_task, technical_task, manager_task],
        process=Process.sequential,
        verbose=True,
        memory=False, 
    )

    result = crew.kickoff()

    report_text = str(result)
    technical_summary = _extract_technical_summary(report_text)
    logger.info(f"📋 Research Analysis complete for {ticker}: {technical_summary}")

    return {
        "report": report_text,
        "technical_summary": technical_summary,
        "agents_used": ["Fundamentalist", "Technician", "Risk Manager"],
        "error": None,
    }


# =============================================================================
# FALLBACK REPORT — Built from REAL LSTM + HMM data (never crashes)
# =============================================================================

def _build_fallback_research_report(
    ticker: str,
    lstm_result: dict,
    regime_result: dict,
    vix_level: float,
    features_summary: dict,
) -> dict:
    lstm_prob = lstm_result.get("probability", 0.5)
    lstm_outlook = lstm_result.get("outlook", "Neutral Outlook")
    regime = regime_result.get("regime", "Sideways")
    regime_confidence = regime_result.get("confidence", 0.5)
    rsi = features_summary.get("rsi", 50)
    macd = features_summary.get("macd", 0)
    bollinger = features_summary.get("bollinger_pctb", 0.5)

    # Apply risk-aware logic
    if ("Bear" in regime or vix_level > 22) and "Bullish" in lstm_outlook:
        technical_summary = "Neutral Outlook"
        justification = (
            f"LSTM suggests {lstm_outlook} ({lstm_prob:.0%}), but elevated risk: "
            f"Regime='{regime}', VIX={vix_level:.1f}. Caution warranted given market conditions."
        )
    elif lstm_prob > 0.70 and "Bull" in regime:
        technical_summary = "Strong Bullish Outlook"
        justification = (
            f"Strong technical confluence: LSTM {lstm_prob:.0%} + Bull regime ({regime_confidence:.0%}). "
            f"VIX {vix_level:.1f} indicates manageable volatility."
        )
    elif "Bullish" in lstm_outlook:
        technical_summary = "Bullish Outlook"
        justification = f"LSTM {lstm_outlook} ({lstm_prob:.0%}) in {regime}. RSI {rsi:.1f} supports positive momentum."
    elif "Bearish" in lstm_outlook:
        technical_summary = "Bearish Outlook"
        justification = f"LSTM {lstm_outlook} ({lstm_prob:.0%}). RSI {rsi:.1f} confirms bearish momentum."
    else:
        technical_summary = "Neutral Outlook"
        justification = f"Mixed signals — LSTM {lstm_prob:.0%}, regime {regime}, RSI {rsi:.1f}."

    rsi_status = "⚠️ Overbought" if rsi > 70 else ("📉 Oversold" if rsi < 30 else f"Normal ({rsi:.1f})")
    bb_status = "Extended" if bollinger > 1 else ("Compressed" if bollinger < 0 else f"Within bands ({bollinger:.2f})")

    report = f"""## Research Analysis Report: {ticker} (NSE)

### 1. Market Regime
**{regime}** (confidence: {regime_confidence:.0%}) — HMM on Nifty 50

### 2. LSTM AI Analysis
- Probability: **{lstm_prob:.1%}**
- Outlook: **{lstm_outlook}**

### 3. Technical Indicators
| Indicator | Value | Status |
|-----------|-------|--------|
| RSI (14) | {rsi:.1f} | {rsi_status} |
| MACD | {macd:.4f} | {'Bullish' if macd > 0 else 'Bearish'} |
| Bollinger %B | {bollinger:.4f} | {bb_status} |

### 4. India VIX
**{vix_level:.1f}** {'⚠️ Elevated volatility' if vix_level > 22 else '✅ Calm market'}

### 5. Risk Assessment
{'🔴 CAUTION: Bear regime / elevated VIX. Risk management priority.' if ('Bear' in regime or vix_level > 22) else '🟢 No elevated risk conditions.'}

### 6. TECHNICAL SUMMARY: **{technical_summary}**
{justification}

---
*📊 Real LSTM + HMM data. AI agents temporarily offline.*
*⚠️ Research data for educational purposes. Stocks are inherently unpredictable.*
"""

    return {
        "report": report,
        "technical_summary": technical_summary,
        "agents_used": ["Technical Analysis Fallback (LSTM + HMM)"],
        "error": None,
    }


# =============================================================================
# HELPERS
# =============================================================================

def _extract_technical_summary(report: str) -> str:
    """Extract technical summary from AI-generated report."""
    report_upper = report.upper()
    if "STRONG BULLISH OUTLOOK" in report_upper or "STRONG BULLISH" in report_upper:
        return "Strong Bullish Outlook"
    if "STRONG BEARISH OUTLOOK" in report_upper or "STRONG BEARISH" in report_upper:
        return "Strong Bearish Outlook"
    if "BEARISH OUTLOOK" in report_upper or "BEARISH" in report_upper:
        return "Bearish Outlook"
    if "BULLISH OUTLOOK" in report_upper or "BULLISH" in report_upper:
        return "Bullish Outlook"
    return "Neutral Outlook"
