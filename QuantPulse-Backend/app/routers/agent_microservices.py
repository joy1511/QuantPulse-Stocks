"""
Agent Microservices Router

Splits the 3-agent CrewAI system into separate endpoints.
Each endpoint loads only 1 agent to fit Render free tier (512MB).
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, validator
from typing import Optional
import os
import logging
import re
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/agents", tags=["AI Agents"])
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Ticker validation regex (NSE symbols: 1-20 uppercase letters/numbers)
TICKER_PATTERN = re.compile(r'^[A-Z0-9]{1,20}$')

def validate_ticker(ticker: str) -> str:
    """Validate ticker symbol format"""
    if not TICKER_PATTERN.match(ticker):
        raise ValueError("Ticker must be 1-20 uppercase letters/numbers (e.g., TCS, RELIANCE)")
    return ticker

# Lazy import CrewAI to save memory
_crewai_imported = False
Agent = None
Task = None
Crew = None
LLM = None
SerperDevTool = None


def _import_crewai():
    """Lazy import CrewAI components"""
    global _crewai_imported, Agent, Task, Crew, LLM, SerperDevTool
    
    if not _crewai_imported:
        try:
            from crewai import Agent as _Agent, Task as _Task, Crew as _Crew, LLM as _LLM
            Agent = _Agent
            Task = _Task
            Crew = _Crew
            LLM = _LLM
            
            try:
                from crewai_tools import SerperDevTool as _SerperDevTool
                SerperDevTool = _SerperDevTool
            except ImportError:
                logger.warning("SerperDevTool not available")
                SerperDevTool = None
            
            _crewai_imported = True
            logger.info("CrewAI components imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import CrewAI: {e}")
            raise HTTPException(status_code=500, detail="CrewAI not available")


def _get_llm():
    """Get configured LLM instance"""
    _import_crewai()
    
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")
    
    return LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=groq_key,
        temperature=0.2,
    )


# =============================================================================
# Request/Response Models
# =============================================================================

class FundamentalistRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20, description="Stock ticker symbol")
    vix_level: float = Field(..., ge=0, le=100, description="VIX level (0-100)")
    
    @validator('ticker')
    def validate_ticker_format(cls, v):
        return validate_ticker(v.upper())


class FundamentalistResponse(BaseModel):
    analysis: str
    sentiment: str  # BULLISH, NEUTRAL, BEARISH


class TechnicianRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20)
    lstm_probability: float = Field(..., ge=0, le=1)
    lstm_outlook: str = Field(..., min_length=1, max_length=100)
    rsi: float = Field(..., ge=0, le=100)
    macd: float
    bollinger_pctb: float = Field(..., ge=0, le=1)
    
    @validator('ticker')
    def validate_ticker_format(cls, v):
        return validate_ticker(v.upper())


class TechnicianResponse(BaseModel):
    analysis: str
    confirmation: str  # CONFIRMS or CONTRADICTS


class RiskManagerRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20)
    regime: str = Field(..., min_length=1, max_length=50)
    regime_confidence: float = Field(..., ge=0, le=1)
    vix_level: float = Field(..., ge=0, le=100)
    lstm_probability: float = Field(..., ge=0, le=1)
    lstm_outlook: str = Field(..., min_length=1, max_length=100)
    fundamentalist_analysis: str = Field(..., min_length=1, max_length=10000)
    fundamentalist_sentiment: str = Field(..., min_length=1, max_length=20)
    technician_analysis: str = Field(..., min_length=1, max_length=10000)
    technician_confirmation: str = Field(..., min_length=1, max_length=20)
    
    @validator('ticker')
    def validate_ticker_format(cls, v):
        return validate_ticker(v.upper())


class RiskManagerResponse(BaseModel):
    report: str
    technical_summary: str


# =============================================================================
# ENDPOINT 1: Fundamentalist Agent
# =============================================================================

@router.post("/fundamentalist", response_model=FundamentalistResponse)
@limiter.limit("10/minute")  # Max 10 requests per minute per IP
async def run_fundamentalist(data: FundamentalistRequest, request: Request):
    """
    Runs only the Fundamentalist agent.
    Searches news and analyzes macro conditions.
    
    Memory: ~180MB (CrewAI + 1 Agent + SerperDevTool)
    Time: 5-8 seconds
    """
    try:
        llm = _get_llm()
        
        # Get search tool if available
        search_tool = None
        if SerperDevTool:
            serper_key = os.getenv("SERPER_API_KEY")
            if serper_key:
                search_tool = SerperDevTool(api_key=serper_key)
        
        # Create single agent
        fundamentalist = Agent(
            role="Fundamentalist Research Analyst",
            goal=f"Research latest news for {data.ticker}. VIX={data.vix_level}",
            backstory="Seasoned macro analyst at top Indian research firm specializing in NSE stocks.",
            tools=[search_tool] if search_tool else [],
            llm=llm,
            verbose=False,
            allow_delegation=False,
        )
        
        # Create task
        task = Task(
            description=f"""Search for '{data.ticker} India stock news' and analyze:
            - Recent news and developments
            - Market sentiment
            - VIX level: {data.vix_level}
            
            Report bullish/bearish factors and conclude with sentiment: BULLISH, NEUTRAL, or BEARISH""",
            agent=fundamentalist,
            expected_output="News summary with clear sentiment: BULLISH, NEUTRAL, or BEARISH",
        )
        
        # Run single-agent crew
        crew = Crew(
            agents=[fundamentalist],
            tasks=[task],
            verbose=False,
            memory=False,
        )
        
        result = crew.kickoff()
        analysis_text = str(result)
        
        # Extract sentiment
        sentiment = "NEUTRAL"
        analysis_upper = analysis_text.upper()
        if "BULLISH" in analysis_upper and "BEARISH" not in analysis_upper:
            sentiment = "BULLISH"
        elif "BEARISH" in analysis_upper:
            sentiment = "BEARISH"
        
        logger.info(f"Fundamentalist analysis complete for {data.ticker}: {sentiment}")
        
        return {
            "analysis": analysis_text,
            "sentiment": sentiment
        }
        
    except Exception as e:
        logger.error(f"Fundamentalist agent failed: {e}")
        raise HTTPException(status_code=500, detail=f"Fundamentalist agent failed: {str(e)}")


# =============================================================================
# ENDPOINT 2: Technician Agent
# =============================================================================

@router.post("/technician", response_model=TechnicianResponse)
@limiter.limit("10/minute")  # Max 10 requests per minute per IP
async def run_technician(data: TechnicianRequest, request: Request):
    """
    Runs only the Technician agent.
    Analyzes LSTM predictions and technical indicators.
    
    Memory: ~160MB (CrewAI + 1 Agent)
    Time: 3-5 seconds
    """
    try:
        llm = _get_llm()
        
        technician = Agent(
            role="Technical Research Analyst",
            goal=f"Analyze technicals for {data.ticker}. LSTM={data.lstm_probability:.1%}",
            backstory="Expert technical analyst with 15 years experience in Indian markets.",
            llm=llm,
            verbose=False,
            allow_delegation=False,
        )
        
        task = Task(
            description=f"""Analyze {data.ticker} technical indicators:
            
            LSTM Prediction:
            - Outlook: {data.lstm_outlook}
            - Probability: {data.lstm_probability:.1%}
            
            Technical Indicators:
            - RSI: {data.rsi}
            - MACD: {data.macd}
            - Bollinger %B: {data.bollinger_pctb}
            
            Determine if technical indicators CONFIRM or CONTRADICT the LSTM outlook.
            Provide detailed technical analysis and conclude with: CONFIRMS or CONTRADICTS""",
            agent=technician,
            expected_output="Technical analysis ending with clear statement: CONFIRMS or CONTRADICTS",
        )
        
        crew = Crew(
            agents=[technician],
            tasks=[task],
            verbose=False,
            memory=False,
        )
        
        result = crew.kickoff()
        analysis_text = str(result)
        
        # Extract confirmation
        confirmation = "CONFIRMS"
        if "CONTRADICT" in analysis_text.upper():
            confirmation = "CONTRADICTS"
        
        logger.info(f"Technician analysis complete for {data.ticker}: {confirmation}")
        
        return {
            "analysis": analysis_text,
            "confirmation": confirmation
        }
        
    except Exception as e:
        logger.error(f"Technician agent failed: {e}")
        raise HTTPException(status_code=500, detail=f"Technician agent failed: {str(e)}")


# =============================================================================
# ENDPOINT 3: Risk Manager Agent
# =============================================================================

@router.post("/risk-manager", response_model=RiskManagerResponse)
@limiter.limit("10/minute")  # Max 10 requests per minute per IP
async def run_risk_manager(data: RiskManagerRequest, request: Request):
    """
    Runs only the Risk Manager agent.
    Synthesizes fundamentalist and technician analyses into final report.
    
    Memory: ~160MB (CrewAI + 1 Agent)
    Time: 5-8 seconds
    """
    try:
        llm = _get_llm()
        
        # Build veto rules
        veto_rules = []
        if "Bear" in data.regime or data.vix_level > 22:
            veto_rules.append(f"CAUTION: Regime={data.regime}, VIX={data.vix_level}")
        if data.lstm_probability > 0.70 and "Bull" in data.regime:
            veto_rules.append(f"STRONG CONFLUENCE: LSTM={data.lstm_probability:.1%} + Bull regime")
        veto_text = "\n".join(veto_rules) if veto_rules else "No special risk conditions"
        
        risk_manager = Agent(
            role="Chief Research Analyst",
            goal=f"Final analysis for {data.ticker}. Regime={data.regime}, VIX={data.vix_level}",
            backstory="Chief Research Analyst for institutional clients with 20 years experience.",
            llm=llm,
            verbose=False,
            allow_delegation=False,
        )
        
        task = Task(
            description=f"""Create Final Research Analysis Report for {data.ticker}:

MARKET CONTEXT:
- Regime: {data.regime} ({data.regime_confidence:.0%} confidence)
- VIX: {data.vix_level}
- LSTM: {data.lstm_outlook} ({data.lstm_probability:.1%} probability)

FUNDAMENTALIST ANALYSIS:
{data.fundamentalist_analysis}
Sentiment: {data.fundamentalist_sentiment}

TECHNICIAN ANALYSIS:
{data.technician_analysis}
Confirmation: {data.technician_confirmation}

RISK CONDITIONS:
{veto_text}

Write a comprehensive Research Analysis Report with these sections:
1. **Ticker & Date**
2. **Market Regime Analysis**
3. **LSTM Prediction Analysis**
4. **News & Fundamental Analysis**
5. **Technical Analysis**
6. **Risk Assessment**
7. **TECHNICAL SUMMARY** (must be exactly one of: Strong Bullish Outlook / Bullish Outlook / Neutral Outlook / Bearish Outlook / Strong Bearish Outlook)
8. **Justification**

Format in clean Markdown.""",
            agent=risk_manager,
            expected_output="Structured Markdown report with clear TECHNICAL SUMMARY section",
        )
        
        crew = Crew(
            agents=[risk_manager],
            tasks=[task],
            verbose=False,
            memory=False,
        )
        
        result = crew.kickoff()
        report_text = str(result)
        
        # Extract technical summary
        technical_summary = "Neutral Outlook"
        report_upper = report_text.upper()
        
        if "STRONG BULLISH OUTLOOK" in report_upper:
            technical_summary = "Strong Bullish Outlook"
        elif "STRONG BEARISH OUTLOOK" in report_upper:
            technical_summary = "Strong Bearish Outlook"
        elif "BEARISH OUTLOOK" in report_upper:
            technical_summary = "Bearish Outlook"
        elif "BULLISH OUTLOOK" in report_upper:
            technical_summary = "Bullish Outlook"
        
        logger.info(f"Risk Manager report complete for {data.ticker}: {technical_summary}")
        
        return {
            "report": report_text,
            "technical_summary": technical_summary
        }
        
    except Exception as e:
        logger.error(f"Risk Manager agent failed: {e}")
        raise HTTPException(status_code=500, detail=f"Risk Manager agent failed: {str(e)}")
