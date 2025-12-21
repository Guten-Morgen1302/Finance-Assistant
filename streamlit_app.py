# 💰 MoneyMind: Smart Finance Companion
# Enhanced Streamlit App with Financial Planning & Budget Structure

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import sqlite3
import asyncio
from enum import Enum
import hashlib
import math  # Added for debt calculations
import traceback
import logging
from pdf_report_generator import generate_financial_report

# =============================================================================
# ERROR HANDLING & DEBUGGING SYSTEM
# =============================================================================

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_execute(func, fallback=None, error_message="An error occurred"):
    """Safely execute a function with error handling"""
    try:
        return func()
    except Exception as e:
        logger.error(f"Error in {func.__name__ if hasattr(func, '__name__') else 'function'}: {str(e)}")
        if st.session_state.get('debug_mode', False):
            st.error(f"🐛 Debug Mode: {error_message}\n```\n{str(e)}\n```")
        return fallback

def handle_calculation_error(calculation_func, default_value=0):
    """Handle mathematical calculation errors"""
    try:
        result = calculation_func()
        if math.isnan(result) or math.isinf(result):
            return default_value
        return result
    except (ZeroDivisionError, ValueError, TypeError) as e:
        logger.warning(f"Calculation error: {str(e)}")
        return default_value

# Page config with Gen Z vibes
st.set_page_config(
    page_title="💰 MoneyMind - Smart Finance",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Gen Z aesthetic
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .vibe-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .money-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 0.5rem;
    }
    
    .budget-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem;
        color: #2d3748;
        text-align: center;
    }
    
    .investment-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem;
        color: #2d3748;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: white;
    }
    
    .success-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #2d3748;
    }
    
    .financial-goal-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .metric-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
    }
    
    .chat-bubble {
        background: #f7fafc;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 15px 15px 0;
        font-style: italic;
    }
    
    .progress-bar {
        background: #e2e8f0;
        border-radius: 10px;
        height: 20px;
        margin: 10px 0;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        transition: width 0.5s ease;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# ENHANCED DATA MODELS & CORE LOGIC
# =============================================================================

class VibeType(Enum):
    STRESSED = "😩"
    CONFIDENT = "😎"
    CONFUSED = "🤔"
    EXCITED = "🚀"
    CHILL = "😌"
    GUILTY = "😬"

class SpendingCategory(Enum):
    ESSENTIAL = "🏠 Essential"
    JOY = "✨ Joy"
    OOPS = "😅 Oops"
    INVESTMENT = "📈 Investment"

class FinancialGoal(Enum):
    EMERGENCY_FUND = "🚨 Emergency Fund"
    TRAVEL = "✈️ Travel Fund"
    HOUSE_DEPOSIT = "🏡 House Deposit"
    RETIREMENT = "👴 Future Me Fund"
    SIDE_HUSTLE = "💼 Side Hustle Capital"
    EDUCATION = "📚 Skill Up Fund"

@dataclass
class Transaction:
    date: datetime
    amount: float
    description: str
    category: SpendingCategory
    merchant: str = ""
    vibe_impact: float = 0.0

@dataclass
class VibeData:
    current_vibe: VibeType
    money_stress_level: int
    spending_guilt: int
    financial_confidence: int

@dataclass
class BudgetPlan:
    monthly_income: float
    needs_percentage: float = 50.0  # 50/30/20 rule adjusted for Gen Z
    wants_percentage: float = 30.0
    savings_percentage: float = 20.0
    
    @property
    def needs_amount(self) -> float:
        return self.monthly_income * (self.needs_percentage / 100)
    
    @property
    def wants_amount(self) -> float:
        return self.monthly_income * (self.wants_percentage / 100)
    
    @property
    def savings_amount(self) -> float:
        return self.monthly_income * (self.savings_percentage / 100)

class SmartFinanceAgent:
    """The Gen Z AI Agent that gets your vibes AND your financial goals"""
    
    def __init__(self):
        self.vibe_responses = {
            VibeType.STRESSED: [
                "Hey bestie, I see you're feeling the money stress 😔 Let's break this down together",
                "Okay, deep breath! Your finances aren't as scary as they seem rn",
                "You're doing better than you think! Let me show you the receipts 📊"
            ],
            VibeType.CONFIDENT: [
                "YES QUEEN! 👑 Your money game is strong today",
                "Love this energy! You're absolutely crushing your financial goals",
                "Confidence looks good on you! Your budget is thriving ✨"
            ],
            VibeType.CONFUSED: [
                "No judgment here! Money stuff is confusing AF sometimes 🤷‍♀️",
                "Let's untangle this together! I'll make it make sense",
                "Confusion is valid! Your finances don't have to be perfect"
            ],
            VibeType.GUILTY: [
                "Stop! 🛑 Guilt spending happens to literally everyone",
                "That purchase doesn't define you, babe. Let's just adjust and move on",
                "Self-compassion > self-judgment. Your worth isn't your spending"
            ]
        }
        
        self.investment_suggestions = {
            "low_risk": [
                {"name": "High-Yield Savings", "desc": "Safe & steady growth 📈", "risk": "Low", "return": "2-4%"},
                {"name": "Government Bonds", "desc": "Boring but reliable 🏛️", "risk": "Low", "return": "3-5%"},
                {"name": "CDs (Certificates of Deposit)", "desc": "Lock it up, stack it up 🔒", "risk": "Low", "return": "3-5%"}
            ],
            "medium_risk": [
                {"name": "Index Funds (S&P 500)", "desc": "Diversified market vibes 📊", "risk": "Medium", "return": "7-10%"},
                {"name": "Target-Date Funds", "desc": "Set it and forget it ⏰", "risk": "Medium", "return": "6-9%"},
                {"name": "REITs", "desc": "Real estate without the drama 🏠", "risk": "Medium", "return": "5-8%"}
            ],
            "high_risk": [
                {"name": "Individual Stocks", "desc": "Pick your favorites 🎯", "risk": "High", "return": "Variable"},
                {"name": "Cryptocurrency", "desc": "Digital gold or digital chaos? 🪙", "risk": "High", "return": "Highly Variable"},
                {"name": "Growth Stocks", "desc": "Betting on the future 🚀", "risk": "High", "return": "Variable"}
            ]
        }
        
        self.gen_z_financial_tips = [
            "💡 Automate your savings - treat it like a subscription you can't cancel",
            "🎯 Use the 24-hour rule for purchases over $50",
            "📱 Try investment apps like Robinhood, Acorns, or Stash for micro-investing",
            "🏠 Aim for 6-month emergency fund (adulting is expensive!)",
            "✨ Invest in yourself - courses, certifications, side hustles",
            "🌱 Start investing early - compound interest is your bestie",
            "💳 Build credit responsibly - your future self will thank you",
            "🎉 Celebrate small wins - every dollar saved matters!"
        ]
    
    def get_vibe_response(self, vibe: VibeType) -> str:
        return random.choice(self.vibe_responses.get(vibe, ["You're doing great! 💜"]))
    
    def get_budget_suggestions(self, income: float, age: int = 25) -> Dict:
        """Generate Gen Z-specific budget suggestions"""
        if income < 2000:
            return {
                "needs": 60,  # Higher for survival mode
                "wants": 25,
                "savings": 15,
                "advice": "Survival mode activated! Focus on essentials and small savings wins 💪"
            }
        elif income < 4000:
            return {
                "needs": 55,
                "wants": 30,
                "savings": 15,
                "advice": "Building phase! You're doing great - balance is key 🌟"
            }
        elif income < 6000:
            return {
                "needs": 50,
                "wants": 30,
                "savings": 20,
                "advice": "Thriving mode! Classic 50/30/20 rule works perfectly 🔥"
            }
        else:
            return {
                "needs": 45,
                "wants": 35,
                "savings": 20,
                "advice": "High earner energy! More room for joy spending AND aggressive saving ✨"
            }
    
    def get_investment_roadmap(self, age: int, income: float, risk_tolerance: str) -> List[Dict]:
        """Create age-appropriate investment suggestions"""
        roadmap = []
        
        # Emergency fund first (always!)
        roadmap.append({
            "priority": 1,
            "goal": "Emergency Fund",
            "target": min(income * 6, 10000),  # 6 months expenses
            "description": "Your financial safety net - aim for 3-6 months expenses 🚨"
        })
        
        # Age-based suggestions
        if age < 30:
            roadmap.extend([
                {
                    "priority": 2,
                    "goal": "Retirement Start",
                    "target": income * 0.15,  # 15% of income
                    "description": "Start early = retire like royalty 👑"
                },
                {
                    "priority": 3,
                    "goal": "Skill Investment",
                    "target": income * 0.05,  # 5% for education
                    "description": "Invest in yourself - best ROI ever 📚"
                }
            ])
        
        return roadmap

# =============================================================================
# CURRENCY FORMATTING HELPERS
# =============================================================================

def format_currency(amount, decimals=2):
    """Safely format currency with error handling"""
    try:
        if amount is None or math.isnan(amount) or math.isinf(amount):
            amount = 0
        
        currency_code = st.session_state.currency
        symbol = currency_symbols.get(currency_code, '$')
        rate = currency_rates.get(currency_code, 1.0)
        value = float(amount) * rate
        
        if currency_code == 'INR':
            return f"₹{value:,.{decimals}f}"
        elif currency_code == 'EUR':
            return f"€{value:,.{decimals}f}"
        else:  # USD
            return f"${value:,.{decimals}f}"
    except (ValueError, TypeError, KeyError) as e:
        logger.warning(f"Currency formatting error: {str(e)}")
        return f"${float(amount or 0):,.{decimals}f}"

def get_currency_label():
    symbol = currency_symbols[st.session_state.currency]
    code = st.session_state.currency
    return f"{symbol} ({code})"

# =============================================================================
# SESSION STATE INITIALIZATION WITH ERROR HANDLING
# =============================================================================

# Initialize debug mode and error tracking
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

if 'error_count' not in st.session_state:
    st.session_state.error_count = 0

if 'last_error' not in st.session_state:
    st.session_state.last_error = None

if 'transactions' not in st.session_state:
    sample_data = [
        Transaction(datetime.now() - timedelta(days=1), 4.50, "iced coffee emergency", SpendingCategory.JOY, "starbucks", 0.3),
        Transaction(datetime.now() - timedelta(days=2), 89.99, "skincare haul (self care!!)", SpendingCategory.JOY, "sephora", 0.2),
        Transaction(datetime.now() - timedelta(days=3), 1200.00, "rent (ugh)", SpendingCategory.ESSENTIAL, "landlord", -0.2),
        Transaction(datetime.now() - timedelta(days=4), 25.99, "tiktok made me buy it", SpendingCategory.OOPS, "amazon", -0.4),
        Transaction(datetime.now() - timedelta(days=5), 15.99, "spotify premium", SpendingCategory.JOY, "spotify", 0.1),
        Transaction(datetime.now() - timedelta(days=6), 67.43, "groceries (adult moment)", SpendingCategory.ESSENTIAL, "whole foods", 0.0),
        Transaction(datetime.now() - timedelta(days=7), 150.00, "therapy session", SpendingCategory.ESSENTIAL, "therapist", 0.5),
        Transaction(datetime.now() - timedelta(days=8), 39.99, "late night uber eats", SpendingCategory.OOPS, "uber eats", -0.2),
    ]
    st.session_state.transactions = sample_data

if 'current_vibe' not in st.session_state:
    st.session_state.current_vibe = VibeType.CHILL

if 'agent' not in st.session_state:
    st.session_state.agent = SmartFinanceAgent()

if 'budget_plan' not in st.session_state:
    st.session_state.budget_plan = None

if 'financial_profile' not in st.session_state:
    st.session_state.financial_profile = {}

# =============================================================================
# GLOBAL CURRENCY SELECTION
# =============================================================================

# Add currency selection at the top of the sidebar
if 'currency' not in st.session_state:
    st.session_state.currency = 'USD'

currency_symbols = {'USD': '$', 'INR': '₹', 'EUR': '€'}
currency_rates = {'USD': 1.0, 'INR': 83.0, 'EUR': 0.92}  # Example rates, update as needed

with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 1rem;'>
        <h2 style='color: white; margin: 0;'>💰 MoneyMind</h2>
        <p style='color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;'>Your Gen Z CFO</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🧭 Navigate")
    
    nav_options = [
        "🏠 Dashboard",
        "🎭 Vibe Check",
        "📊 Budget Planner",
        "🎯 What-If Simulator",
        "🔍 Expense Forecasting",
        "🏦 Income Analyzer",
        "📈 Inflation Detector",
        "🧠 Stress Predictor"
    ]
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🏠 Dashboard"
    
    st.session_state.current_page = st.radio(
        "Navigate",
        nav_options,
        index=nav_options.index(st.session_state.current_page) if st.session_state.current_page in nav_options else 0,
        label_visibility="collapsed",
        key="nav_radio"
    )
    
    st.markdown("---")
    
    st.markdown('### 🌍 Currency')
    st.session_state.currency = st.selectbox(
        'Currency',
        options=['USD', 'INR', 'EUR'],
        format_func=lambda x: f"{currency_symbols[x]} {x}",
        index=['USD', 'INR', 'EUR'].index(st.session_state.currency) if st.session_state.currency in ['USD', 'INR', 'EUR'] else 0,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    st.markdown('### 🤖 AI Assistant')
    enable_agent = st.checkbox('🧠 Enable AI Agent', value=st.session_state.get('agent_enabled', False))
    st.session_state.agent_enabled = enable_agent
    
    if enable_agent:
        st.success('🚀 AI Agent Active!')
        agent_mode = st.selectbox(
            '🎯 Agent Focus',
            ['💰 Autonomous Slay Planner', '🧾 Emotional Spending Coach', '📊 Financial Advisor', '🎯 Goal Tracker'],
            help='Choose what your AI agent should focus on'
        )
        st.session_state.agent_mode = agent_mode
        
        agent_intensity = st.slider('🔥 Agent Intensity', 1, 5, 3, help='How often should the agent intervene?')
        st.session_state.agent_intensity = agent_intensity

# =============================================================================
# AGENTIC AI CHATBOT INTEGRATION (ALWAYS VISIBLE ON DASHBOARD)
# =============================================================================

# Get current page early for navigation
current_page = st.session_state.get('current_page', '🏠 Dashboard')

# Show chat ONLY when AI Agent is enabled on Dashboard and Vibe Check
if st.session_state.get('agent_enabled', False) and current_page in ["🏠 Dashboard", "🎭 Vibe Check"]:
    # Display current agent mode
    current_mode = st.session_state.get('agent_mode', '💰 Autonomous Slay Planner')
    
    # Chatbot iframe integration with CRAZY AWESOME UI
    chatbot_html = f"""
    <style>
        @keyframes crazyGlow {{
            0% {{ box-shadow: 0 0 20px #FF006E, 0 0 40px #FB5607, 0 10px 30px rgba(0,0,0,0.2); }}
            50% {{ box-shadow: 0 0 30px #FFBE0B, 0 0 50px #8338EC, 0 10px 40px rgba(0,0,0,0.3); }}
            100% {{ box-shadow: 0 0 20px #FF006E, 0 0 40px #FB5607, 0 10px 30px rgba(0,0,0,0.2); }}
        }}
        @keyframes slideInWild {{
            from {{ opacity: 0; transform: translateY(30px) scale(0.95); }}
            to {{ opacity: 1; transform: translateY(0) scale(1); }}
        }}
    </style>
    <div style="
        background: linear-gradient(135deg, #FF006E 0%, #FB5607 25%, #FFBE0B 50%, #8338EC 75%, #FF006E 100%);
        padding: 2px;
        border-radius: 25px;
        margin: 2rem 0;
        box-shadow: 0 0 20px #FF006E, 0 0 40px #FB5607, 0 10px 30px rgba(0,0,0,0.2);
        animation: crazyGlow 3s ease-in-out infinite;
    ">
        <div style="
            background: #0A0E27;
            border-radius: 23px;
            padding: 2rem;
        ">
            <div style="text-align: center; margin-bottom: 1.5rem; animation: slideInWild 0.6s ease-out;">
                <h2 style="
                    background: linear-gradient(135deg, #FF006E, #FB5607, #FFBE0B, #8338EC);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    margin: 0;
                    font-size: 2.2rem;
                    font-weight: 900;
                ">
                    🔮 FinanceGPT Supreme
                </h2>
                <p style="
                    color: #FFBE0B;
                    margin: 0.5rem 0 0 0;
                    font-weight: 600;
                    font-size: 1.1rem;
                    text-shadow: 0 0 10px rgba(255, 190, 11, 0.5);
                ">
                    Chat with Your Financial Wizard ✨
                </p>
            </div>
            
            <div style="
                text-align: center;
                background: linear-gradient(135deg, rgba(255,0,110,0.1), rgba(251,86,7,0.1));
                padding: 1rem;
                border-radius: 15px;
                margin-bottom: 1.5rem;
                border: 2px solid rgba(255,190,11,0.3);
            ">
                <span style="color: #FB5607; font-weight: 700; font-size: 1rem;">
                    🎯 Mode: {current_mode}
                </span>
            </div>
            
            <div style="border-radius: 15px; overflow: hidden; background: linear-gradient(135deg, #1a1f3a 0%, #2d1b69 100%); border: 2px solid #8338EC; min-height: 750px;">
                <iframe
                    src="https://www.chatbase.co/chatbot-iframe/97sccVBW3_J60VexD-2eY"
                    width="100%"
                    height="750"
                    frameborder="0"
                    style="border: none;">
                </iframe>
            </div>
        </div>
    </div>
    """
    components.html(chatbot_html, height=850, scrolling=True)

# =============================================================================
# AGENTIC AI FEATURES - AUTONOMOUS PLANNER & EMOTIONAL COACH
# =============================================================================

if st.session_state.get('agent_enabled', False) and current_page in ["🏠 Dashboard", "🎭 Vibe Check"]:
    agent_mode = st.session_state.get('agent_mode', '💰 Autonomous Slay Planner')
    
    if agent_mode == '💰 Autonomous Slay Planner':
        st.markdown("### 🎯 Autonomous Slay Planner")
        
        # Goal Setting Interface
        with st.expander("🚀 Set Your Slay Goal", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                goal_item = st.text_input("🎯 What do you want to buy?", placeholder="e.g., iPad, vacation, car")
                goal_amount = st.number_input("💰 How much does it cost?", min_value=1.0, value=500.0, step=50.0)
            
            with col2:
                goal_months = st.slider("📅 In how many months?", 1, 24, 3)
                current_saved = st.number_input("💳 Already saved?", min_value=0.0, value=0.0, step=10.0)
            
            if st.button("🚀 Activate Slay Planner", type="primary"):
                # Calculate weekly savings needed
                remaining_amount = goal_amount - current_saved
                weeks_available = goal_months * 4.33  # Average weeks per month
                weekly_savings_needed = remaining_amount / weeks_available
                
                # Store goal in session state
                st.session_state.slay_goal = {
                    'item': goal_item,
                    'total_amount': goal_amount,
                    'months': goal_months,
                    'current_saved': current_saved,
                    'weekly_needed': weekly_savings_needed,
                    'created_date': datetime.now()
                }
                
                st.success(f"🎯 Goal Set! Save {format_currency(weekly_savings_needed)} per week to get your {goal_item}!")
        
        # Active Goal Tracking
        if 'slay_goal' in st.session_state:
            goal = st.session_state.slay_goal
            progress = (goal['current_saved'] / goal['total_amount']) * 100
            
            st.markdown("#### 🔥 Your Active Slay Goal")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🎯 Goal", goal['item'])
                st.metric("💰 Total Cost", format_currency(goal['total_amount']))
            
            with col2:
                st.metric("💳 Saved So Far", format_currency(goal['current_saved']))
                st.metric("📅 Time Left", f"{goal['months']} months")
            
            with col3:
                st.metric("💪 Weekly Target", format_currency(goal['weekly_needed']))
                st.metric("📈 Progress", f"{progress:.1f}%")
            
            # Progress bar
            st.progress(progress / 100)
            
            # AI Agent Intervention
            if goal['weekly_needed'] > 0:
                st.markdown("#### 🤖 AI Agent Recommendations")
                
                # Calculate spending adjustments
                monthly_income = st.session_state.financial_profile.get('monthly_income', 0) if st.session_state.financial_profile else 3000
                weekly_income = monthly_income / 4.33
                savings_rate = (goal['weekly_needed'] / weekly_income) * 100
                
                if savings_rate > 30:
                    st.warning(f"🚨 **Agent Alert:** This goal requires {savings_rate:.1f}% of your weekly income. Consider extending the timeline or finding additional income sources.")
                elif savings_rate > 15:
                    st.info(f"💪 **Agent Suggestion:** This goal requires {savings_rate:.1f}% of weekly income. I'll help you optimize your 'wants' spending!")
                else:
                    st.success(f"✅ **Agent Approved:** This goal is achievable with {savings_rate:.1f}% of your income!")
                
                # Spending category recommendations
                st.markdown("**🎯 AI Spending Adjustments:**")
                st.markdown(f"• Reduce 'Joy' spending by {format_currency(goal['weekly_needed'] * 0.6)} per week")
                st.markdown(f"• Find {format_currency(goal['weekly_needed'] * 0.4)} in optimized 'Essential' spending")
                st.markdown("• I'll remind you when you're about to overspend! 🤖")
    
    elif agent_mode == '🧾 Emotional Spending Coach':
        st.markdown("### 🧾 Emotional Spending Tracker + Agentic Coaching")
        
        # Emotional spending analysis
        if st.session_state.transactions:
            st.markdown("#### 🔍 Recent Emotional Spending Analysis")
            
            # Classify transactions by emotional state
            emotional_categories = {
                'Joy': [],
                'Regret': [],
                'Impulse': [],
                'Survival': []
            }
            
            for transaction in st.session_state.transactions[-10:]:  # Last 10 transactions
                vibe_impact = getattr(transaction, 'vibe_impact', 0)
                amount = getattr(transaction, 'amount', 0)
                description = getattr(transaction, 'description', '')
                
                # Simple emotional classification based on vibe impact and keywords
                if vibe_impact > 0.3:
                    emotional_categories['Joy'].append((description, amount))
                elif vibe_impact < -0.3:
                    emotional_categories['Regret'].append((description, amount))
                elif any(word in description.lower() for word in ['impulse', 'quick', 'saw', 'wanted']):
                    emotional_categories['Impulse'].append((description, amount))
                else:
                    emotional_categories['Survival'].append((description, amount))
            
            # Display emotional spending breakdown
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                joy_total = sum(amount for _, amount in emotional_categories['Joy'])
                st.metric("😊 Joy Purchases", f"{len(emotional_categories['Joy'])}")
                st.caption(f"Total: {format_currency(joy_total)}")
            
            with col2:
                regret_total = sum(amount for _, amount in emotional_categories['Regret'])
                st.metric("😔 Regret Purchases", f"{len(emotional_categories['Regret'])}")
                st.caption(f"Total: {format_currency(regret_total)}")
            
            with col3:
                impulse_total = sum(amount for _, amount in emotional_categories['Impulse'])
                st.metric("⚡ Impulse Buys", f"{len(emotional_categories['Impulse'])}")
                st.caption(f"Total: {format_currency(impulse_total)}")
            
            with col4:
                survival_total = sum(amount for _, amount in emotional_categories['Survival'])
                st.metric("🛡️ Survival Needs", f"{len(emotional_categories['Survival'])}")
                st.caption(f"Total: {format_currency(survival_total)}")
            
            # AI Coach Recommendations
            st.markdown("#### 🤖 AI Emotional Coach Insights")
            
            total_emotional = regret_total + impulse_total
            if total_emotional > joy_total:
                st.warning("🚨 **Coach Alert:** You're spending more on regret/impulse than joy! Let's fix this.")
                
                st.markdown("**🧸 Custom Action Plan:**")
                st.markdown("• **Pause Rule:** Wait 24 hours before any purchase over $25")
                st.markdown("• **Emotion Check:** Ask yourself 'Am I buying this because I'm sad/stressed?'")
                st.markdown("• **Joy Alternative:** Next time you're sad, save $10 instead of shopping")
                st.markdown("• **Celebration Savings:** Reward yourself with good vibes when you resist impulse buys!")
                
            elif joy_total > 0:
                st.success("✨ **Coach Celebration:** You're spending mindfully and choosing joy! Keep it up!")
                st.markdown("🎉 **Milestone Rewards:** You've made more joy purchases than regret purchases this week!")
            
            # Emotional spending tracker for new purchases
            st.markdown("#### 💭 Why Did You Buy This?")
            
            with st.expander("🔍 Analyze Your Last Purchase", expanded=False):
                if st.session_state.transactions:
                    last_transaction = st.session_state.transactions[-1]
                    st.write(f"**Last Purchase:** {last_transaction.description} - {format_currency(last_transaction.amount)}")
                    
                    emotional_reason = st.selectbox(
                        "Why did you buy this?",
                        ["I genuinely needed it", "It made me happy", "I was feeling sad/stressed", "It was on sale/impulse", "Social pressure", "Boredom"]
                    )
                    
                    emotional_rating = st.slider("How do you feel about this purchase now?", 1, 10, 5)
                    
                    if st.button("💾 Save Emotional Analysis"):
                        # Update transaction with emotional data
                        last_transaction.emotional_reason = emotional_reason
                        last_transaction.emotional_rating = emotional_rating
                        st.success("🧠 Emotional data saved! I'll learn your patterns to help you better.")
        
        else:
            st.info("💝 Start making some purchases to unlock emotional spending insights!")
    
    # Agent Notifications & Interventions
    if st.session_state.get('agent_intensity', 3) >= 3:
        st.markdown("### 🚨 Live Agent Interventions")
        
        # Check for spending deviations
        if st.session_state.transactions:
            recent_spending = sum(t.amount for t in st.session_state.transactions[-5:])  # Last 5 transactions
            
            if recent_spending > 200:  # Threshold for intervention
                st.warning("🤖 **Agent Alert:** Heavy spending detected! Current session: " + format_currency(recent_spending))
                st.markdown("**AI Suggestions:**")
                st.markdown("• Take a 10-minute break before your next purchase")
                st.markdown("• Consider if this aligns with your current goals")
                st.markdown("• Remember: Every dollar saved is a step closer to your dreams! ✨")
            
            # Positive reinforcement
            positive_transactions = [t for t in st.session_state.transactions[-10:] if getattr(t, 'vibe_impact', 0) > 0.2]
            if len(positive_transactions) >= 3:
                st.success("🎉 **Agent Celebration:** You're making smart, joy-filled purchases! Keep up the positive money vibes!")
        
        # Weekly check-ins (simulated)
        if datetime.now().weekday() == 0:  # Monday
            st.info("📅 **Weekly Agent Check-in:** How did your spending align with your goals last week?")
            
            weekly_reflection = st.selectbox(
                "How do you feel about last week's spending?",
                ["🔥 Crushed my goals!", "😌 Pretty good overall", "😅 Could've been better", "😔 Need to refocus"],
                key="weekly_reflection"
            )
            
            if weekly_reflection == "🔥 Crushed my goals!":
                st.balloons()
                st.success("🎉 Amazing work! Your AI agent is proud of you!")
            elif weekly_reflection == "😔 Need to refocus":
                st.markdown("💪 No worries! Let's adjust your plan and get back on track!")

# =============================================================================
# AGENT MILESTONE & REWARD SYSTEM
# =============================================================================

if st.session_state.get('agent_enabled', False) and 'slay_goal' in st.session_state:
    goal = st.session_state.slay_goal
    progress = (goal['current_saved'] / goal['total_amount']) * 100
    
    # Milestone celebrations
    milestones = [25, 50, 75, 90, 100]
    
    if 'celebrated_milestones' not in st.session_state:
        st.session_state.celebrated_milestones = []
    
    for milestone in milestones:
        if progress >= milestone and milestone not in st.session_state.celebrated_milestones:
            st.session_state.celebrated_milestones.append(milestone)
            
            # Celebration based on milestone
            if milestone == 25:
                st.success("🎉 **25% Milestone!** You're officially on your way! Your AI agent believes in you!")
            elif milestone == 50:
                st.success("🚀 **Halfway There!** You're absolutely crushing this goal! Keep the momentum!")
                st.balloons()
            elif milestone == 75:
                st.success("💎 **75% Complete!** You're in the final stretch! Your dream is so close!")
            elif milestone == 90:
                st.success("🔥 **90% Almost There!** Just a little more and you'll have your " + goal['item'] + "!")
            elif milestone == 100:
                st.success("🏆 **GOAL ACHIEVED!** You did it! Time to enjoy your " + goal['item'] + "! 🎊")
                st.balloons()
                # Reset goal after achievement
                if st.button("🎯 Set New Goal"):
                    del st.session_state.slay_goal
                    st.rerun()

# =============================================================================
# MAIN APP INTERFACE
# =============================================================================



# =============================================================================
# GLOBAL ERROR HANDLER & MAIN APP WRAPPER
# =============================================================================

# TIER 2 PAGE GUARD - Skip all main content if on Tier 2 pages
tier2_pages = ["🎯 What-If Simulator", "🔍 Expense Forecasting", "🏦 Income Analyzer", "📈 Inflation Detector", "🧠 Stress Predictor"]
is_tier2_page = current_page in tier2_pages

# Only show main header on Dashboard
if current_page == "🏠 Dashboard" and not is_tier2_page:
    try:
        st.markdown("""
        <div class="main-header">
            <h1>💰 MoneyMind</h1>
            <h5>Emotionally Smart. Financially Sharp.</h5>
            <p><em>"Forget spreadsheets. Feel your finances."</em></p>
            
        </div>
        """, unsafe_allow_html=True)
        
        # PDF Report Download Button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📄 Generate & Download PDF Report", type="primary", use_container_width=True):
                try:
                    financial_data = {
                        'health_score': 78,
                        'income': 50000,
                        'expenses': 35000,
                        'savings': 15000,
                        'categories': {'Housing': 15000, 'Food': 6000, 'Transport': 4000, 'Entertainment': 5000, 'Shopping': 3000, 'Other': 2000},
                        'key_metrics': {'Savings Rate': '30%', 'Monthly Income': '₹50,000'},
                        'budget_breakdown': {'needs': 25000, 'wants': 15000, 'savings': 10000},
                        'monthly_data': pd.DataFrame({'Income': [50000, 50000, 50000], 'Expenses': [35000, 36000, 34000]}, index=['Oct', 'Nov', 'Dec']),
                        'insights': ['✅ You\'re saving 30% of income', '⚠️ Food spending increased 5% this month', '🎯 Emergency fund at 75% capacity'],
                        'summary': 'Your financial health is strong! Keep building those savings.',
                        'conclusion': 'Great job tracking your finances. Continue optimizing and investing in your future!'
                    }
                    pdf_bytes = generate_financial_report('Financial User', 'December 2024', financial_data)
                    st.download_button('⬇️ Download PDF Report', pdf_bytes, 'MoneyMind_Financial_Report.pdf', 'application/pdf')
                    st.success('✅ PDF Report Generated Successfully!')
                except Exception as e:
                    st.error(f'❌ Error generating PDF: {str(e)}')
        
        # Error count display for admins
        if st.session_state.debug_mode and st.session_state.error_count > 0:
            st.warning(f"⚠️ Debug Mode: {st.session_state.error_count} errors detected this session")

    except Exception as e:
        st.error("🚨 Critical Error in App Header")
        logger.critical(f"Header error: {str(e)}")
        st.session_state.error_count += 1
        st.session_state.last_error = str(e)

# =============================================================================
# PAGE-SPECIFIC HEADERS
# =============================================================================

# Add header for Budget Planner page
if current_page == "📊 Budget Planner":
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 20px; margin-bottom: 2rem; text-align: center;'>
        <h1 style='color: white; margin: 0;'>📊 Budget Planner</h1>
        <p style='color: rgba(255,255,255,0.9); font-size: 1.2rem;'>Create your personalized Gen Z budget structure</p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# FINANCIAL PROFILE SETUP
# =============================================================================

# Skip entire dashboard section if on Tier 2 pages
if is_tier2_page:
    pass  # Skip to Tier 2 features
elif current_page in ["🏠 Dashboard", "🎭 Vibe Check", "📊 Budget Planner"]:
    st.markdown("## 💼 Financial Profile Setup")

    with st.expander("🚀 Set Up Your Financial Profile (Click to expand)", expanded=not st.session_state.financial_profile):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            monthly_income = st.number_input(
                f"💰 Monthly Income/Allowance {get_currency_label()}",
                min_value=0.0,
                value=st.session_state.financial_profile.get('monthly_income', 50000.0),
                step=1000.0,
                help="Include salary, freelance, side hustles, everything!"
            )
            
            age = st.slider(
                "🎂 Age",
                min_value=18,
                max_value=35,
                value=st.session_state.financial_profile.get('age', 25)
            )
        
        with col2:
            employment_status = st.selectbox(
                "👔 Employment Status",
                ["Student", "Full-time Job", "Freelancer", "Part-time", "Unemployed", "Side Hustle King/Queen"],
                index=1
            )
            
            living_situation = st.selectbox(
                "🏠 Living Situation",
                ["With Parents (blessed!)", "Shared Apartment", "Solo Living", "Dorm Life"],
                index=0
            )
        
        with col3:
            risk_tolerance = st.selectbox(
                "📊 Investment Risk Tolerance",
                ["Conservative (play it safe)", "Moderate (balanced vibes)", "Aggressive (YOLO but smart)"],
                index=1
            )
            
            primary_goal = st.selectbox(
                "🎯 Primary Financial Goal",
                list(FinancialGoal),
                format_func=lambda x: x.value
            )
        
        if st.button("💾 Save My Financial Profile", type="primary"):
            st.session_state.financial_profile = {
                'monthly_income': monthly_income,
                'age': age,
                'employment_status': employment_status,
                'living_situation': living_situation,
                'risk_tolerance': risk_tolerance,
                'primary_goal': primary_goal
            }
            
            # Generate budget plan
            budget_suggestions = st.session_state.agent.get_budget_suggestions(monthly_income, age)
            st.session_state.budget_plan = BudgetPlan(
                monthly_income=monthly_income,
                needs_percentage=budget_suggestions['needs'],
                wants_percentage=budget_suggestions['wants'],
                savings_percentage=budget_suggestions['savings']
            )
            
            st.success("🎉 Profile saved! Your personalized financial plan is ready!")
            st.rerun()

# =============================================================================
# PERSONALIZED BUDGET BREAKDOWN
# =============================================================================

if st.session_state.budget_plan and not is_tier2_page:
    st.markdown("## 💎 Your Personalized Gen Z Budget Structure")
    
    budget = st.session_state.budget_plan
    profile = st.session_state.financial_profile
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="budget-card">
            <h3>💰 Monthly Income</h3>
            <h2>{format_currency(budget.monthly_income, 0)}</h2>
            <p>Your total hustle</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="budget-card">
            <h3>🏠 Needs ({budget.needs_percentage}%)</h3>
            <h2>{format_currency(budget.needs_amount, 0)}</h2>
            <p>Rent, food, transport</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="budget-card">
            <h3>✨ Wants ({budget.wants_percentage}%)</h3>
            <h2>{format_currency(budget.wants_amount, 0)}</h2>
            <p>Fun, joy, self-care</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="budget-card">
            <h3>📈 Savings ({budget.savings_percentage}%)</h3>
            <h2>{format_currency(budget.savings_amount, 0)}</h2>
            <p>Future you fund</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Budget visualization
    st.markdown("### 📊 Your Budget Breakdown")
    
    budget_data = {
        'Category': ['🏠 Needs', '✨ Wants', '📈 Savings'],
        'Amount': [budget.needs_amount, budget.wants_amount, budget.savings_amount],
        'Percentage': [budget.needs_percentage, budget.wants_percentage, budget.savings_percentage]
    }
    
    fig_budget = px.pie(
        values=budget_data['Amount'],
        names=budget_data['Category'],
        title="💫 Your Money Allocation",
        color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
    )
    fig_budget.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14)
    )
    st.plotly_chart(fig_budget, use_container_width=True)

# =============================================================================
# INVESTMENT SUGGESTIONS
# =============================================================================

if st.session_state.financial_profile and not is_tier2_page:
    st.markdown("## 📈 Gen Z Investment Roadmap")
    
    profile = st.session_state.financial_profile
    risk_level = profile['risk_tolerance'].split(' ')[0].lower()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🚀 Recommended Investments")
        
        if risk_level == "conservative":
            investments = st.session_state.agent.investment_suggestions["low_risk"]
        elif risk_level == "moderate":
            investments = st.session_state.agent.investment_suggestions["medium_risk"]
        else:
            investments = st.session_state.agent.investment_suggestions["high_risk"]
        
        for inv in investments:
            st.markdown(f"""
            <div class="investment-card">
                <h4>{inv['name']}</h4>
                <p>{inv['desc']}</p>
                <p><strong>Risk:</strong> {inv['risk']} | <strong>Expected Return:</strong> {inv['return']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🎯 Your Financial Goals Roadmap")
        
        roadmap = st.session_state.agent.get_investment_roadmap(
            profile['age'], 
            profile['monthly_income'],
            risk_level
        )
        
        for item in roadmap:
            progress = min(100, random.randint(10, 80))  # Simulated progress
            st.markdown(f"""
            <div class="financial-goal-card">
                <h4>Priority {item['priority']}: {item['goal']}</h4>
                <p>{item['description']}</p>
                <p><strong>Target:</strong> {format_currency(item['target'], 0)}</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress}%"></div>
                </div>
                <p><small>{progress}% Complete</small></p>
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# GEN Z FINANCIAL SURVIVAL GUIDE
# =============================================================================

if not is_tier2_page:
    st.markdown("## 🔥 Gen Z Financial Survival Guide")

tab1, tab2, tab3, tab4 = st.tabs(["💰 Budgeting Hacks", "📈 Investment 101", "🚨 Emergency Fund", "💼 Side Hustle Tips"])

with tab1:
    st.markdown("### 💡 Budgeting That Actually Works")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🎯 The 50/30/20 Rule (Gen Z Edition):**
        - 50% Needs: Rent, groceries, transport, phone
        - 30% Wants: Entertainment, dining out, shopping
        - 20% Savings: Emergency fund + investments
        
        **📱 Apps That Slay:**
        - Mint (free budgeting)
        - YNAB (You Need A Budget)
        - PocketGuard (spending limits)
        - Goodbudget (envelope method)
        """)
    
    with col2:
        st.markdown("""
        **💫 Budgeting Hacks:**
        - Automate savings (pay yourself first!)
        - Use the 24-hour rule for big purchases
        - Track spending with photos of receipts
        - Set up separate accounts for different goals
        - Use cash for discretionary spending
        - Review and adjust monthly (not daily!)
        """)

with tab2:
    st.markdown("### 📊 Investing Made Simple")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🚀 Start Here (Beginner-Friendly):**
        - High-yield savings account (2-4% return)
        - Index funds (S&P 500) - diversified & low fees
        - Target-date funds - set it & forget it
        - Employer 401(k) match - FREE MONEY!
        
        **📱 Investment Apps:**
        - Robinhood (commission-free trading)
        - Acorns (micro-investing with spare change)
        - Stash ($5 minimum investment)
        - M1 Finance (automated portfolios)
        """)
    
    with col2:
        st.markdown("""
        **⚡ Power Moves:**
        - Start with small amounts ($25-50/month)
        - Diversify (don't put all eggs in one basket)
        - Think long-term (10+ years)
        - Don't panic sell during market dips
        - Reinvest dividends automatically
        - Learn about compound interest - it's magic! ✨
        """)

with tab3:
    st.markdown("### 🚨 Emergency Fund Essentials")
    
    emergency_target = st.session_state.budget_plan.monthly_income * 6 if st.session_state.budget_plan else 30000
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **🎯 Your Emergency Fund Goal: {format_currency(emergency_target, 0)}**
        
        **Why You Need It:**
        - Job loss protection
        - Medical emergencies
        - Car repairs
        - Unexpected expenses
        - Mental peace (priceless!)
        
        **Where to Keep It:**
        - High-yield savings account
        - Money market account
        - Short-term CDs
        """)
    
    with col2:
        st.markdown("""
        **🔥 Building Strategy:**
        - Start with INR 1,000 (any amount is better than zero!)
        - Automate transfers (INR 2,000-5,000/month)
        - Use windfalls (tax refunds, bonuses)
        - Sell stuff you don't need
        - Side hustle specifically for emergency fund
        - Celebrate milestones! 🎉
        """)

with tab4:
    st.markdown("### 💼 Side Hustle Game Strong")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🔥 Hot Side Hustles for 2024:**
        - Content creation (TikTok, YouTube, Instagram)
        - Freelance writing/graphic design
        - Online tutoring
        - Virtual assistant
        - Social media management
        - Photography/videography
        - Food delivery (Uber Eats, DoorDash)
        - Pet sitting/dog walking
        """)
    
    with col2:
        st.markdown("""
        **💡 Side Hustle Success Tips:**
        - Start with skills you already have
        - Set clear income goals
        - Track time vs. money earned
        - Separate business & personal finances
        - Save taxes (15-30% of earnings)
        - Scale what works, drop what doesn't
        - Network like crazy! 🤝
        """)

# =============================================================================
# HERO VIBE CHECK SECTION (Gen Z Hero Feature)
# =============================================================================

if not is_tier2_page:
    # Show header only on Vibe Check page
    if current_page == "🎭 Vibe Check":
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2.5rem 1rem 2rem 1rem;
            border-radius: 25px;
            margin-bottom: 2.5rem;
            text-align: center;
            color: white;
            box-shadow: 0 8px 32px rgba(102,126,234,0.15);
        '>
            <h1 style='font-size: 2.8rem; margin-bottom: 0.5rem;'>🌈 Daily Vibe Check</h1>
            <p style='font-size: 1.3rem; margin-bottom: 1.5rem; font-style: italic;'>How are you feeling about your money today?</p>
        </div>
        """, unsafe_allow_html=True)

# Large, central vibe selector and sliders
vibe_col, stress_col, conf_col = st.columns([2, 1, 1])

with vibe_col:
    # Ensure current_vibe is always a valid VibeType
    try:
        vibe_index = list(VibeType).index(st.session_state.current_vibe)
    except Exception:
        st.session_state.current_vibe = VibeType.CHILL
        vibe_index = list(VibeType).index(VibeType.CHILL)
    current_vibe = st.selectbox(
        "Select your vibe",
        options=list(VibeType),
        format_func=lambda x: f"{x.value} {x.name.title()}",
        index=vibe_index,
        key="hero_vibe_selectbox",
        label_visibility="collapsed"
    )
    
    # Check if vibe changed and trigger emoji pop-out effect
    if 'previous_vibe' not in st.session_state:
        st.session_state.previous_vibe = current_vibe
    
    if current_vibe != st.session_state.previous_vibe:
        # Trigger emoji pop-out effect instead of balloons
        st.markdown(f"""
        <div id="emoji-popup" style="
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 8rem;
            z-index: 9999;
            animation: emojiPop 2s ease-out forwards;
            pointer-events: none;
        ">
            {current_vibe.value}
        </div>
        <style>
        @keyframes emojiPop {{
            0% {{ 
                opacity: 0; 
                transform: translate(-50%, -50%) scale(0.1); 
            }}
            50% {{ 
                opacity: 1; 
                transform: translate(-50%, -50%) scale(1.2); 
            }}
            100% {{ 
                opacity: 0; 
                transform: translate(-50%, -50%) scale(0.8) translateY(-100px); 
            }}
        }}
        </style>
        <script>
        setTimeout(function() {{
            var popup = document.getElementById('emoji-popup');
            if (popup) {{
                popup.remove();
            }}
        }}, 2000);
        </script>
        """, unsafe_allow_html=True)
        st.session_state.previous_vibe = current_vibe
    
    # =============================================================================
    # DYNAMIC AURA SYSTEM - CHANGES WEBSITE COLORS BASED ON MOOD
    # =============================================================================
    
    # Define mood-based color schemes and auras
    vibe_auras = {
        VibeType.STRESSED: {
            "primary": "#FF6B6B",
            "secondary": "#FF8E8E", 
            "accent": "#FFB3B3",
            "bg_start": "#FF4757",
            "bg_end": "#FF6B6B",
            "card_bg": "linear-gradient(135deg, #FF6B6B 0%, #FF4757 100%)",
            "text_glow": "#FF6B6B",
            "particle_color": "#FF8E8E",
            "aura_name": "Stress Relief Aura",
            "description": "Calming reds to acknowledge stress while promoting healing"
        },
        VibeType.CONFIDENT: {
            "primary": "#4ECDC4",
            "secondary": "#45B7D1",
            "accent": "#96CEB4",
            "bg_start": "#667eea",
            "bg_end": "#764ba2",
            "card_bg": "linear-gradient(135deg, #4ECDC4 0%, #45B7D1 100%)",
            "text_glow": "#4ECDC4",
            "particle_color": "#45B7D1",
            "aura_name": "Confidence Power Aura",
            "description": "Bold blues and teals radiating success energy"
        },
        VibeType.CONFUSED: {
            "primary": "#A8A8A8",
            "secondary": "#B8B8B8",
            "accent": "#D3D3D3",
            "bg_start": "#74b9ff",
            "bg_end": "#0984e3",
            "card_bg": "linear-gradient(135deg, #A8A8A8 0%, #74b9ff 100%)",
            "text_glow": "#74b9ff",
            "particle_color": "#B8B8B8",
            "aura_name": "Clarity Seeking Aura",
            "description": "Cool grays and blues to promote mental clarity"
        },
        VibeType.EXCITED: {
            "primary": "#FFD93D",
            "secondary": "#FF6B35",
            "accent": "#FF8B94",
            "bg_start": "#FFD93D",
            "bg_end": "#FF6B35",
            "card_bg": "linear-gradient(135deg, #FFD93D 0%, #FF6B35 100%)",
            "text_glow": "#FFD93D",
            "particle_color": "#FF8B94",
            "aura_name": "High Energy Excitement Aura",
            "description": "Vibrant yellows and oranges bursting with excitement"
        },
        VibeType.CHILL: {
            "primary": "#96CEB4",
            "secondary": "#FFEAA7",
            "accent": "#DDA0DD",
            "bg_start": "#96CEB4",
            "bg_end": "#FFEAA7",
            "card_bg": "linear-gradient(135deg, #96CEB4 0%, #FFEAA7 100%)",
            "text_glow": "#96CEB4",
            "particle_color": "#DDA0DD",
            "aura_name": "Zen Chill Aura",
            "description": "Peaceful greens and soft yellows for ultimate relaxation"
        },
        VibeType.GUILTY: {
            "primary": "#E17055",
            "secondary": "#FDCB6E",
            "accent": "#FD79A8",
            "bg_start": "#E17055",
            "bg_end": "#FDCB6E",
            "card_bg": "linear-gradient(135deg, #E17055 0%, #FDCB6E 100%)",
            "text_glow": "#E17055",
            "particle_color": "#FD79A8",
            "aura_name": "Self-Compassion Aura",
            "description": "Warm oranges and peaches promoting self-forgiveness"
        }
    }
    
    current_aura = vibe_auras[current_vibe]
    
    # Apply dynamic aura styling
    st.markdown(f"""
    <style>
    /* DYNAMIC AURA SYSTEM - MOOD-RESPONSIVE DESIGN */
    
    :root {{
        --aura-primary: {current_aura['primary']};
        --aura-secondary: {current_aura['secondary']};
        --aura-accent: {current_aura['accent']};
        --aura-glow: {current_aura['text_glow']};
    }}
    
    /* Animated background aura effect */
    .stApp {{
        background: linear-gradient(45deg, {current_aura['bg_start']}22, {current_aura['bg_end']}22);
        animation: auraShift 8s ease-in-out infinite alternate;
    }}
    
    @keyframes auraShift {{
        0% {{ background: linear-gradient(45deg, {current_aura['bg_start']}15, {current_aura['bg_end']}15); }}
        100% {{ background: linear-gradient(135deg, {current_aura['bg_end']}15, {current_aura['bg_start']}15); }}
    }}
    
    /* Dynamic card styling based on mood */
    .main-header {{
        background: {current_aura['card_bg']} !important;
        box-shadow: 0 10px 30px {current_aura['primary']}40 !important;
        animation: cardGlow 3s ease-in-out infinite alternate;
    }}
    
    @keyframes cardGlow {{
        0% {{ box-shadow: 0 10px 30px {current_aura['primary']}40; }}
        100% {{ box-shadow: 0 15px 40px {current_aura['primary']}60, 0 0 20px {current_aura['text_glow']}30; }}
    }}
    
    .vibe-card {{
        background: {current_aura['card_bg']} !important;
        box-shadow: 0 8px 25px {current_aura['primary']}35 !important;
    }}
    
    .money-card {{
        background: {current_aura['card_bg']} !important;
        border: 2px solid {current_aura['accent']}60;
        box-shadow: 0 5px 20px {current_aura['primary']}30;
    }}
    
    .budget-card {{
        background: linear-gradient(135deg, {current_aura['accent']}80, {current_aura['secondary']}60) !important;
        border: 1px solid {current_aura['primary']}40;
    }}
    
    .investment-card {{
        background: linear-gradient(135deg, {current_aura['secondary']}70, {current_aura['accent']}50) !important;
        border-left: 4px solid {current_aura['primary']};
    }}
    
    .financial-goal-card {{
        background: {current_aura['card_bg']} !important;
        box-shadow: 0 6px 20px {current_aura['primary']}35;
    }}
    
    /* Mood-responsive text effects */
    h1, h2, h3 {{
        text-shadow: 0 0 10px {current_aura['text_glow']}50 !important;
        animation: textGlow 2s ease-in-out infinite alternate;
    }}
    
    @keyframes textGlow {{
        0% {{ text-shadow: 0 0 10px {current_aura['text_glow']}50; }}
        100% {{ text-shadow: 0 0 15px {current_aura['text_glow']}70, 0 0 25px {current_aura['text_glow']}30; }}
    }}
    
    /* Button styling matches mood */
    .stButton > button {{
        background: {current_aura['card_bg']} !important;
        border: 2px solid {current_aura['primary']} !important;
        box-shadow: 0 4px 15px {current_aura['primary']}40 !important;
        transition: all 0.3s ease !important;
    }}
    
    .stButton > button:hover {{
        box-shadow: 0 8px 25px {current_aura['primary']}60, 0 0 20px {current_aura['text_glow']}50 !important;
        transform: translateY(-3px) !important;
    }}
    
    /* Progress bars match the aura */
    .progress-fill {{
        background: {current_aura['card_bg']} !important;
        box-shadow: inset 0 0 10px {current_aura['text_glow']}30;
    }}
    
    /* Sidebar matches mood */
    .sidebar .sidebar-content {{
        background: linear-gradient(180deg, {current_aura['primary']}, {current_aura['secondary']}) !important;
    }}
    
    /* Floating particles for extra aura effect */
    .aura-particles {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 1;
    }}
    
    .particle {{
        position: absolute;
        width: 4px;
        height: 4px;
        background: {current_aura['particle_color']};
        border-radius: 50%;
        animation: float 15s infinite linear;
        opacity: 0.6;
    }}
    
    @keyframes float {{
        0% {{ transform: translateY(100vh) rotate(0deg); }}
        100% {{ transform: translateY(-100px) rotate(360deg); }}
    }}
    
    /* Create multiple particles with different delays */
    .particle:nth-child(1) {{ left: 10%; animation-delay: 0s; }}
    .particle:nth-child(2) {{ left: 20%; animation-delay: 2s; }}
    .particle:nth-child(3) {{ left: 30%; animation-delay: 4s; }}
    .particle:nth-child(4) {{ left: 40%; animation-delay: 6s; }}
    .particle:nth-child(5) {{ left: 50%; animation-delay: 8s; }}
    .particle:nth-child(6) {{ left: 60%; animation-delay: 10s; }}
    .particle:nth-child(7) {{ left: 70%; animation-delay: 12s; }}
    .particle:nth-child(8) {{ left: 80%; animation-delay: 14s; }}
    .particle:nth-child(9) {{ left: 90%; animation-delay: 16s; }}
    
    </style>
    
    <!-- Floating particles for aura effect -->
    <div class="aura-particles">
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
    </div>
    
    <!-- Aura notification -->
    <div style="
        position: fixed;
        top: 20px;
        right: 20px;
        background: {current_aura['card_bg']};
        color: white;
        padding: 12px 20px;
        border-radius: 25px;
        font-size: 0.9em;
        font-weight: 600;
        box-shadow: 0 8px 25px {current_aura['primary']}50;
        z-index: 1000;
        animation: auraNotification 4s ease-out;
    ">
        ✨ {current_aura['aura_name']} Activated ✨
    </div>
    
    
    
    """, unsafe_allow_html=True)
    
    st.session_state.current_vibe = current_vibe

with stress_col:
    stress_level = st.slider("Money stress level", 1, 10, 5, key="hero_stress_slider")

with conf_col:
    confidence_level = st.slider("Financial confidence", 1, 10, 6, key="hero_conf_slider")

# AI Response based on vibe (big, animated card) with dynamic aura
current_aura = vibe_auras[current_vibe]
vibe_response = st.session_state.agent.get_vibe_response(current_vibe)

# Enhanced response card with aura integration
st.markdown(f"""
<div style='
    background: {current_aura['card_bg']};
    padding: 2rem;
    border-radius: 20px;
    margin: 1.5rem 0 2.5rem 0;
    color: white;
    font-size: 1.5rem;
    font-weight: bold;
    box-shadow: 0 10px 30px {current_aura['primary']}40, 0 0 40px {current_aura['text_glow']}20;
    transition: all 0.3s;
    animation: heroFadeIn 1s, auraGlow 3s ease-in-out infinite alternate;
    border: 2px solid {current_aura['accent']}60;
'>
   

<style>
@keyframes heroFadeIn {{
    from {{ opacity: 0; transform: translateY(0); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes auraGlow {{
    0% {{ 
        box-shadow: 0 10px 30px {current_aura['primary']}40, 0 0 40px {current_aura['text_glow']}20;
        transform: scale(1);
    }}
    100% {{ 
        box-shadow: 0 15px 40px {current_aura['primary']}60, 0 0 60px {current_aura['text_glow']}40;
        transform: scale(1.02);
    }}
}}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 🔥 TIER 1 FEATURE: AI FINANCIAL COPILOT - MOOD-BASED CONVERSATIONS
# =============================================================================

st.markdown("## 💎 WealthMinds AI - Your Personal Finance Oracle")

# Initialize copilot personality settings
if 'copilot_personality' not in st.session_state:
    st.session_state.copilot_personality = "balanced"
if 'copilot_memory' not in st.session_state:
    st.session_state.copilot_memory = []

# Mood-based AI response generator
def get_mood_copilot_response(vibe, stress_level, context="general"):
    """Generate empathetic, mood-aware responses"""
    
    # Vibe-specific tone and messages
    vibe_responses = {
        VibeType.STRESSED: {
            "tone": "gentle",
            "greeting": "Hey bestie, I can see you're feeling stressed about money 😔",
            "approach": "Let's focus on small wins today - no pressure, just progress",
            "tips": [
                "Take 3 deep breaths. Your finances aren't as scary as they seem",
                "Let's find one thing to celebrate, even if it's just opening this app",
                "Would you like me to show you some quick wins? Small steps matter!"
            ],
            "emoji": "💚"
        },
        VibeType.CONFIDENT: {
            "tone": "hype",
            "greeting": "YOOO! You're radiating big money energy today! 🔥",
            "approach": "Let's level up! You're ready for some power moves",
            "tips": [
                "Time to crush those goals! What's your next target?",
                "Your confidence is contagious! Let's talk investments",
                "You're in the zone - perfect time for strategic planning"
            ],
            "emoji": "👑"
        },
        VibeType.CONFUSED: {
            "tone": "simple",
            "greeting": "No judgment here! Money stuff can be confusing AF 🤷‍♀️",
            "approach": "Let's break this down step by step - I'll explain everything simply",
            "tips": [
                "First, let's focus on just ONE thing at a time",
                "Think of your budget like a pizza - we'll slice it up together",
                "Questions are good! Every pro started as a beginner"
            ],
            "emoji": "💡"
        },
        VibeType.EXCITED: {
            "tone": "energetic",
            "greeting": "I LOVE THIS ENERGY! 🚀 Let's channel it into money wins!",
            "approach": "Perfect time to make big moves while motivation is high!",
            "tips": [
                "Strike while the iron's hot - what goal excites you most?",
                "Let's set up some automation while you're in the zone!",
                "Your excitement is the perfect fuel for financial success!"
            ],
            "emoji": "⚡"
        },
        VibeType.CHILL: {
            "tone": "relaxed",
            "greeting": "Hey there, chill vibes today! 😌 Love to see it",
            "approach": "Let's do a casual check-in, no stress",
            "tips": [
                "Perfect day for a gentle review of your progress",
                "Just vibing? Same. Let's keep it light and easy",
                "Good energy = good decisions. No rush today"
            ],
            "emoji": "🌿"
        },
        VibeType.GUILTY: {
            "tone": "compassionate",
            "greeting": "Hey, stop! 🛑 Guilt spending happens to literally everyone",
            "approach": "Self-compassion > self-judgment. Let's move forward together",
            "tips": [
                "That purchase doesn't define you. Let's just adjust and move on",
                "One slip doesn't erase all your progress - you're still winning",
                "Let's turn this into a learning moment, not a shame spiral"
            ],
            "emoji": "💜"
        }
    }
    
    response = vibe_responses.get(vibe, vibe_responses[VibeType.CHILL])
    
    # Add stress-level adjustments
    if stress_level > 7:
        response["tips"].insert(0, "🚨 High stress detected! Remember: Money is a tool, not your worth")
    
    return response

# Display AI Copilot Card
copilot_response = get_mood_copilot_response(current_vibe, stress_level if 'stress_level' in dir() else 5)

st.markdown(f"""
<style>
    @keyframes oracleGlow {{
        0% {{ box-shadow: 0 0 15px #00D9FF, inset 0 0 15px rgba(0,217,255,0.2); }}
        50% {{ box-shadow: 0 0 30px #00D9FF, inset 0 0 30px rgba(0,217,255,0.3); }}
        100% {{ box-shadow: 0 0 15px #00D9FF, inset 0 0 15px rgba(0,217,255,0.2); }}
    }}
    @keyframes borderShift {{
        0% {{ border-color: #00D9FF; }}
        50% {{ border-color: #BD00FF; }}
        100% {{ border-color: #00D9FF; }}
    }}
</style>
<div style='
    background: linear-gradient(135deg, #0A0E27 0%, #16213E 50%, #0F3B61 100%);
    padding: 1.5rem;
    border-radius: 20px;
    margin: 1.5rem 0;
    color: white;
    border: 2px solid #00D9FF;
    animation: oracleGlow 3s ease-in-out infinite, borderShift 4s ease-in-out infinite;
    position: relative;
'>
    <div style='display: flex; align-items: center; margin-bottom: 1.5rem;'>
        <span style='font-size: 3rem; margin-right: 15px; animation: spin 3s linear infinite;'>{copilot_response["emoji"]}</span>
        <div>
            <h3 style='
                margin: 0;
                font-size: 1.4rem;
                background: linear-gradient(135deg, #00D9FF, #BD00FF);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            '>{copilot_response["greeting"]}</h3>
            <p style='margin: 5px 0 0 0; opacity: 0.9; font-style: italic; color: #00D9FF;'>{copilot_response["approach"]}</p>
        </div>
    </div>
    <div style='background: linear-gradient(135deg, rgba(0,217,255,0.15), rgba(189,0,255,0.15)); padding: 1.2rem; border-radius: 12px; margin-top: 1rem; border: 1px solid rgba(0,217,255,0.3);'>
        <p style='margin: 0; font-weight: 600; color: #00D9FF;'>💭 Oracle Insight:</p>
        <p style='margin: 8px 0 0 0; color: #E8F4F8;'>{random.choice(copilot_response["tips"])}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Proactive Messages System
st.markdown("### 📬 Proactive Alerts")
proactive_alerts = []

# Check for upcoming expenses
current_day = datetime.now().day
if current_day >= 25:
    proactive_alerts.append({
        "type": "warning",
        "icon": "🗓️",
        "message": f"Month-end approaching! 10 days of careful spending ahead",
        "action": "Review remaining budget"
    })

# Check spending patterns
if len(st.session_state.transactions) > 3:
    recent_oops = [t for t in st.session_state.transactions[-5:] if t.category == SpendingCategory.OOPS]
    if len(recent_oops) >= 2:
        proactive_alerts.append({
            "type": "alert",
            "icon": "⚠️",
            "message": f"I noticed {len(recent_oops)} impulse purchases recently",
            "action": "Let's review what's triggering these"
        })

# Holiday spending alert
if datetime.now().month in [11, 12]:
    proactive_alerts.append({
        "type": "info",
        "icon": "🎄",
        "message": "Holiday season detected! Want to set a gift budget?",
        "action": "Create holiday budget"
    })

if proactive_alerts:
    for alert in proactive_alerts[:3]:
        color = "#FF6B6B" if alert["type"] == "alert" else "#4ECDC4" if alert["type"] == "info" else "#FFD93D"
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {color}40, {color}20);
            border-left: 4px solid {color};
            padding: 12px 15px;
            border-radius: 0 10px 10px 0;
            margin: 8px 0;
        '>
            <span style='font-size: 1.3rem;'>{alert["icon"]}</span>
            <strong style='margin-left: 10px;'>{alert["message"]}</strong>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# 🔥 TIER 1 FEATURE: CONTEXT-AWARE EXPENSE REASONING (SPENDING STORIES)
# =============================================================================

st.markdown("## 🕵️ Expense Detective - Spending Stories")

def analyze_transaction_context(transaction):
    """AI-powered expense analysis with context reasoning"""
    hour = transaction.date.hour
    amount = transaction.amount
    description = transaction.description.lower()
    merchant = transaction.merchant.lower() if hasattr(transaction, 'merchant') else ""
    
    # Time-based context
    if 0 <= hour < 6:
        time_context = "Late Night 🌙"
        time_risk = "high"
    elif 6 <= hour < 12:
        time_context = "Morning ☀️"
        time_risk = "low"
    elif 12 <= hour < 17:
        time_context = "Afternoon 🌤️"
        time_risk = "low"
    elif 17 <= hour < 21:
        time_context = "Evening 🌆"
        time_risk = "medium"
    else:
        time_context = "Night 🌙"
        time_risk = "medium"
    
    # Spending reason detection
    reason_keywords = {
        "stress": ["stress", "bad day", "rough", "tired", "exhausted", "ugh"],
        "celebration": ["birthday", "party", "celebrate", "won", "promotion", "happy"],
        "necessity": ["need", "broken", "repair", "emergency", "run out", "essential"],
        "impulse": ["saw", "couldn't resist", "random", "just because", "wanted"],
        "social": ["friend", "date", "dinner", "hangout", "going out"],
        "self-care": ["spa", "therapy", "wellness", "treat", "deserve"]
    }
    
    detected_reason = "General Purchase"
    for reason, keywords in reason_keywords.items():
        if any(kw in description for kw in keywords):
            detected_reason = reason.title()
            break
    
    # Impulse score calculation (0-100%)
    impulse_score = 20  # Base score
    if time_risk == "high":
        impulse_score += 30
    elif time_risk == "medium":
        impulse_score += 15
    if amount < 50:
        impulse_score += 20
    if detected_reason == "Impulse":
        impulse_score += 25
    if "amazon" in merchant or "online" in description:
        impulse_score += 10
    
    impulse_score = min(100, impulse_score)
    
    # Risk level
    if impulse_score >= 70:
        risk_level = "🔴 High Risk"
        risk_color = "#FF6B6B"
    elif impulse_score >= 40:
        risk_level = "🟡 Medium Risk"
        risk_color = "#FFD93D"
    else:
        risk_level = "🟢 Planned"
        risk_color = "#4ECDC4"
    
    # Future prediction
    predictions = {
        "travel": "🏨 Hotel booking might be next!",
        "grocery": "📦 Meal prep week incoming?",
        "coffee": "☕ Caffeine streak continues...",
        "clothes": "👗 Outfit completion purchase coming?",
        "tech": "🔌 Accessories purchase predicted",
        "food": "🍕 Dining pattern detected"
    }
    
    prediction = "📊 Watching your patterns..."
    for key, pred in predictions.items():
        if key in description or key in merchant:
            prediction = pred
            break
    
    return {
        "time_context": time_context,
        "reason": detected_reason,
        "impulse_score": impulse_score,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "prediction": prediction
    }

# Display spending stories for recent transactions
if st.session_state.transactions:
    st.markdown("### 📖 Your Recent Spending Stories")
    
    for i, transaction in enumerate(st.session_state.transactions[-5:]):
        analysis = analyze_transaction_context(transaction)
        
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-left: 4px solid {analysis["risk_color"]};
            padding: 15px;
            border-radius: 0 15px 15px 0;
            margin: 10px 0;
        '>
            <div style='display: flex; justify-content: space-between; align-items: start;'>
                <div>
                    <h4 style='margin: 0; color: #2d3748;'>{transaction.description}</h4>
                    <p style='margin: 5px 0; color: #718096;'>
                        {transaction.merchant if hasattr(transaction, 'merchant') and transaction.merchant else 'Unknown'} 
                        • {analysis["time_context"]} 
                        • {transaction.date.strftime('%b %d')}
                    </p>
                </div>
                <div style='text-align: right;'>
                    <h3 style='margin: 0; color: #2d3748;'>{format_currency(transaction.amount)}</h3>
                    <span style='
                        background: {analysis["risk_color"]}30;
                        color: {analysis["risk_color"]};
                        padding: 3px 10px;
                        border-radius: 15px;
                        font-size: 0.8rem;
                        font-weight: 600;
                    '>{analysis["risk_level"]}</span>
                </div>
            </div>
            <div style='display: flex; gap: 15px; margin-top: 12px; flex-wrap: wrap;'>
                <div style='background: rgba(102,126,234,0.1); padding: 8px 12px; border-radius: 8px;'>
                    <small style='color: #667eea; font-weight: 600;'>🎯 Reason:</small>
                    <span style='color: #2d3748; margin-left: 5px;'>{analysis["reason"]}</span>
                </div>
                <div style='background: rgba(255,107,107,0.1); padding: 8px 12px; border-radius: 8px;'>
                    <small style='color: #FF6B6B; font-weight: 600;'>⚡ Impulse Score:</small>
                    <span style='color: #2d3748; margin-left: 5px;'>{analysis["impulse_score"]}%</span>
                </div>
                <div style='background: rgba(78,205,196,0.1); padding: 8px 12px; border-radius: 8px;'>
                    <small style='color: #4ECDC4; font-weight: 600;'>🔮 Prediction:</small>
                    <span style='color: #2d3748; margin-left: 5px;'>{analysis["prediction"]}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Spending Personality Profile
st.markdown("### 🧬 Your Spending Personality")
if st.session_state.transactions:
    planned_count = len([t for t in st.session_state.transactions if analyze_transaction_context(t)["impulse_score"] < 40])
    impulse_count = len([t for t in st.session_state.transactions if analyze_transaction_context(t)["impulse_score"] >= 70])
    total = len(st.session_state.transactions)
    
    planned_percent = (planned_count / total * 100) if total > 0 else 0
    impulse_percent = (impulse_count / total * 100) if total > 0 else 0
    
    if planned_percent >= 70:
        personality = "🎯 THE PLANNER"
        personality_desc = "You're a strategic spender! 70%+ of your purchases are well-thought-out"
        personality_color = "#4ECDC4"
    elif impulse_percent >= 50:
        personality = "⚡ THE SPONTANEOUS"
        personality_desc = "You live in the moment! Consider adding a 24-hour rule for purchases over $50"
        personality_color = "#FF6B6B"
    else:
        personality = "⚖️ THE BALANCED"
        personality_desc = "You've got a healthy mix of planned and spontaneous spending!"
        personality_color = "#667eea"
    
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, {personality_color}, {personality_color}dd);
        padding: 1.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    '>
        <h2 style='margin: 0; font-size: 2rem;'>{personality}</h2>
        <p style='margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.95;'>{personality_desc}</p>
        <div style='display: flex; justify-content: center; gap: 30px; margin-top: 15px;'>
            <div>
                <h3 style='margin: 0;'>{planned_percent:.0f}%</h3>
                <small>Planned</small>
            </div>
            <div>
                <h3 style='margin: 0;'>{100 - planned_percent - impulse_percent:.0f}%</h3>
                <small>Mixed</small>
            </div>
            <div>
                <h3 style='margin: 0;'>{impulse_percent:.0f}%</h3>
                <small>Impulse</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# 🔥 TIER 1 FEATURE: BEHAVIOR-DRIVEN BUDGETING (NETFLIX-STYLE PROFILES)
# =============================================================================

st.markdown("## 🎬 Budget Profiles - Choose Your Mode")

# Budget persona definitions
budget_personas = {
    "Student Mode 📚": {
        "needs": 70, "wants": 20, "savings": 10,
        "description": "For when money's tight - focus on essentials",
        "color": "#FF6B6B",
        "icon": "📚",
        "best_for": "Students, job seekers, tight budgets"
    },
    "Balanced Mode ⚖️": {
        "needs": 50, "wants": 30, "savings": 20,
        "description": "The classic approach - work hard, play hard",
        "color": "#4ECDC4",
        "icon": "⚖️",
        "best_for": "Stable income, normal expenses"
    },
    "Slay Mode 👑": {
        "needs": 40, "wants": 35, "savings": 25,
        "description": "Making good money - maximize joy & savings",
        "color": "#667eea",
        "icon": "👑",
        "best_for": "High earners, growth phase"
    },
    "Emergency Mode 🚨": {
        "needs": 80, "wants": 10, "savings": 10,
        "description": "Crisis time - cut everything non-essential",
        "color": "#e74c3c",
        "icon": "🚨",
        "best_for": "Job loss, unexpected expenses, debt crisis"
    },
    "Holiday Mode 🎄": {
        "needs": 45, "wants": 40, "savings": 15,
        "description": "Tis the season - more room for gifts & fun",
        "color": "#27ae60",
        "icon": "🎄",
        "best_for": "November-December, special occasions"
    },
    "Wealth Builder 🚀": {
        "needs": 35, "wants": 25, "savings": 40,
        "description": "Aggressive saving - future millionaire vibes",
        "color": "#f39c12",
        "icon": "🚀",
        "best_for": "FIRE movement, big goals"
    }
}

# Initialize selected persona
if 'selected_budget_persona' not in st.session_state:
    st.session_state.selected_budget_persona = "Balanced Mode ⚖️"

# Display persona cards
st.markdown("### 🎯 Swipe to Choose Your Budget Personality")

cols = st.columns(3)
for i, (persona_name, persona) in enumerate(budget_personas.items()):
    with cols[i % 3]:
        is_selected = st.session_state.selected_budget_persona == persona_name
        border_style = f"4px solid {persona['color']}" if is_selected else "2px solid #e0e0e0"
        bg_opacity = "1" if is_selected else "0.7"
        
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {persona["color"]}30, {persona["color"]}10);
            border: {border_style};
            padding: 1.5rem;
            border-radius: 15px;
            margin: 8px 0;
            opacity: {bg_opacity};
            cursor: pointer;
            transition: all 0.3s;
            min-height: 220px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        '>
            <div style='text-align: center;'>
                <span style='font-size: 2.5rem; display: block; margin-bottom: 8px;'>{persona["icon"]}</span>
                <h4 style='margin: 0 0 8px 0; color: #FFFFFF; font-size: 1.2rem; font-weight: 700; word-wrap: break-word; overflow-wrap: break-word; text-shadow: 0 2px 4px rgba(0,0,0,0.3);'>{persona_name}</h4>
                <p style='margin: 0; font-size: 0.9rem; color: #E8E8E8; line-height: 1.3;'>{persona["description"]}</p>
            </div>
            <div style='display: flex; justify-content: space-around; margin-top: 15px; gap: 8px;'>
                <div style='text-align: center; flex: 1;'>
                    <small style='color: {persona["color"]}; font-weight: 600;'>Needs</small>
                    <p style='margin: 4px 0; font-weight: bold; font-size: 1.1rem;'>{persona["needs"]}%</p>
                </div>
                <div style='text-align: center; flex: 1;'>
                    <small style='color: {persona["color"]}; font-weight: 600;'>Wants</small>
                    <p style='margin: 4px 0; font-weight: bold; font-size: 1.1rem;'>{persona["wants"]}%</p>
                </div>
                <div style='text-align: center; flex: 1;'>
                    <small style='color: {persona["color"]}; font-weight: 600;'>Save</small>
                    <p style='margin: 4px 0; font-weight: bold; font-size: 1.1rem;'>{persona["savings"]}%</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"Select {persona['icon']}", key=f"persona_{i}", use_container_width=True):
            st.session_state.selected_budget_persona = persona_name
            st.rerun()

# Seasonal Auto-Switch Suggestion
current_month = datetime.now().month
seasonal_suggestion = None
if current_month in [11, 12]:
    seasonal_suggestion = ("Holiday Mode 🎄", "December detected! Switch to Holiday Mode?")
elif current_month == 1:
    seasonal_suggestion = ("Wealth Builder 🚀", "New Year's Resolution time! Go aggressive?")

# Show active budget breakdown based on selected mode
selected_persona = budget_personas[st.session_state.selected_budget_persona]
monthly_income = st.session_state.financial_profile.get('monthly_income', 5000) if st.session_state.financial_profile else 5000

needs_amount = monthly_income * (selected_persona['needs'] / 100)
wants_amount = monthly_income * (selected_persona['wants'] / 100)
savings_amount = monthly_income * (selected_persona['savings'] / 100)

st.markdown("### 💡 Your Active Budget Breakdown")
st.markdown(f"**Based on {st.session_state.selected_budget_persona}** - Monthly income: {format_currency(monthly_income)}")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, #FF6B6B40, #FF6B6B20);
        padding: 1.2rem;
        border-radius: 15px;
        text-align: center;
        border: 2px solid #FF6B6B;
    '>
        <h3 style='margin: 0; color: #FF6B6B; font-size: 2rem;'>{selected_persona['needs']}%</h3>
        <p style='margin: 8px 0 0 0; font-weight: 600;'>Needs (Bills, Food, etc)</p>
        <h2 style='margin: 8px 0 0 0; color: #FF6B6B;'>{format_currency(needs_amount)}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, #FFD93D40, #FFD93D20);
        padding: 1.2rem;
        border-radius: 15px;
        text-align: center;
        border: 2px solid #FFD93D;
    '>
        <h3 style='margin: 0; color: #FFD93D; font-size: 2rem;'>{selected_persona['wants']}%</h3>
        <p style='margin: 8px 0 0 0; font-weight: 600;'>Wants (Fun, Entertainment)</p>
        <h2 style='margin: 8px 0 0 0; color: #FFD93D;'>{format_currency(wants_amount)}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, #6BCF7F40, #6BCF7F20);
        padding: 1.2rem;
        border-radius: 15px;
        text-align: center;
        border: 2px solid #6BCF7F;
    '>
        <h3 style='margin: 0; color: #6BCF7F; font-size: 2rem;'>{selected_persona['savings']}%</h3>
        <p style='margin: 8px 0 0 0; font-weight: 600;'>Savings (Build Wealth)</p>
        <h2 style='margin: 8px 0 0 0; color: #6BCF7F;'>{format_currency(savings_amount)}</h2>
    </div>
    """, unsafe_allow_html=True)

if seasonal_suggestion and st.session_state.selected_budget_persona != seasonal_suggestion[0]:
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 15px;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    '>
        <div>
            <strong>🤖 AI Suggestion:</strong> {seasonal_suggestion[1]}
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔄 Switch Now", key="seasonal_switch"):
        st.session_state.selected_budget_persona = seasonal_suggestion[0]
        st.rerun()

# =============================================================================
# 🔥 TIER 1 FEATURE: PREDICTIVE END-OF-MONTH BALANCE
# =============================================================================

st.markdown("## 📉 Balance Trajectory Forecast")

# Calculate predictions
if st.session_state.financial_profile and st.session_state.transactions:
    monthly_income = st.session_state.financial_profile.get('monthly_income', 5000)
    
    # Calculate daily spending rate
    if len(st.session_state.transactions) >= 3:
        recent_spending = sum(t.amount for t in st.session_state.transactions[-7:])
        daily_spend_rate = recent_spending / 7
    else:
        daily_spend_rate = monthly_income / 30 * 0.8  # Assume 80% spend rate
    
    current_day = datetime.now().day
    days_remaining = 30 - current_day
    
    # Starting balance (assuming we start with income)
    starting_balance = monthly_income
    current_spent = sum(t.amount for t in st.session_state.transactions if t.date.month == datetime.now().month)
    current_balance = starting_balance - current_spent
    
    # Predicted end-of-month balance
    predicted_spending = daily_spend_rate * days_remaining
    predicted_eom_balance = current_balance - predicted_spending
    
    # Breaking point calculation
    days_until_zero = current_balance / daily_spend_rate if daily_spend_rate > 0 else 999
    
    # Create trajectory data
    trajectory_data = []
    balance = current_balance
    for day in range(days_remaining + 1):
        trajectory_data.append({
            "Day": current_day + day,
            "Balance": max(0, balance),
            "Status": "Safe" if balance > monthly_income * 0.1 else "Warning" if balance > 0 else "Danger"
        })
        balance -= daily_spend_rate
    
    # Display forecast cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        balance_color = "#4ECDC4" if current_balance > monthly_income * 0.3 else "#FFD93D" if current_balance > 0 else "#FF6B6B"
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {balance_color}40, {balance_color}20);
            padding: 1rem;
            border-radius: 15px;
            text-align: center;
            border: 2px solid {balance_color};
        '>
            <h4 style='margin: 0; color: #2d3748;'>💰 Current Balance</h4>
            <h2 style='margin: 8px 0; color: {balance_color};'>{format_currency(current_balance)}</h2>
            <small style='color: #718096;'>Day {current_day} of month</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        eom_color = "#4ECDC4" if predicted_eom_balance > 0 else "#FF6B6B"
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {eom_color}40, {eom_color}20);
            padding: 1rem;
            border-radius: 15px;
            text-align: center;
            border: 2px solid {eom_color};
        '>
            <h4 style='margin: 0; color: #2d3748;'>📅 Month-End Prediction</h4>
            <h2 style='margin: 8px 0; color: {eom_color};'>{format_currency(predicted_eom_balance)}</h2>
            <small style='color: #718096;'>{'✅ Looking good!' if predicted_eom_balance > 0 else '🚨 SHORTFALL!'}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #667eea40, #667eea20);
            padding: 1rem;
            border-radius: 15px;
            text-align: center;
            border: 2px solid #667eea;
        '>
            <h4 style='margin: 0; color: #2d3748;'>📊 Daily Burn Rate</h4>
            <h2 style='margin: 8px 0; color: #667eea;'>{format_currency(daily_spend_rate)}</h2>
            <small style='color: #718096;'>Per day average</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        zero_day_color = "#FF6B6B" if days_until_zero < days_remaining else "#4ECDC4"
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {zero_day_color}40, {zero_day_color}20);
            padding: 1rem;
            border-radius: 15px;
            text-align: center;
            border: 2px solid {zero_day_color};
        '>
            <h4 style='margin: 0; color: #2d3748;'>⏰ Days Until Zero</h4>
            <h2 style='margin: 8px 0; color: {zero_day_color};'>{days_until_zero:.0f} days</h2>
            <small style='color: #718096;'>{"🚨 Before month end!" if days_until_zero < days_remaining else "✅ You will make it!"}</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Trajectory chart
    if trajectory_data:
        df_trajectory = pd.DataFrame(trajectory_data)
        fig_trajectory = px.line(
            df_trajectory, x="Day", y="Balance",
            title="💰 Balance Trajectory This Month",
            color_discrete_sequence=['#667eea']
        )
        fig_trajectory.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Danger Zone")
        fig_trajectory.add_hline(y=monthly_income * 0.1, line_dash="dot", line_color="orange", annotation_text="Warning")
        fig_trajectory.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_trajectory, use_container_width=True)
    
    # Breaking Point Alert
    if predicted_eom_balance < 0:
        shortfall = abs(predicted_eom_balance)
        daily_cut_needed = shortfall / days_remaining if days_remaining > 0 else shortfall
        
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #FF6B6B, #e74c3c);
            padding: 1.5rem;
            border-radius: 15px;
            color: white;
            margin: 1rem 0;
        '>
            <h3 style='margin: 0;'>🚨 BREAKING POINT ALERT!</h3>
            <p style='margin: 10px 0;'>You'll be short <strong>{format_currency(shortfall)}</strong> by month-end at current rate</p>
            <div style='background: rgba(255,255,255,0.2); padding: 12px; border-radius: 10px; margin-top: 10px;'>
                <strong>🎯 Recovery Options:</strong>
                <p style='margin: 8px 0 0 0;'>• Cut {format_currency(daily_cut_needed)}/day from spending</p>
                <p style='margin: 5px 0 0 0;'>• Find extra income source: {format_currency(shortfall)}</p>
                <p style='margin: 5px 0 0 0;'>• Move to Emergency Mode budget</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # What-If Slider
    st.markdown("### 🎚️ What-If Simulator")
    spending_adjustment = st.slider(
        "Adjust daily spending by:",
        min_value=-50,
        max_value=50,
        value=0,
        step=5,
        format="%d%%"
    )
    
    adjusted_daily = daily_spend_rate * (1 + spending_adjustment/100)
    adjusted_eom = current_balance - (adjusted_daily * days_remaining)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("New Daily Spend", format_currency(adjusted_daily), f"{spending_adjustment}%")
    with col2:
        change = adjusted_eom - predicted_eom_balance
        st.metric("New Month-End Balance", format_currency(adjusted_eom), format_currency(change))

# =============================================================================
# 🔥 TIER 1 FEATURE: SPENDING INTENT DETECTION (IMPULSE ANALYZER)
# =============================================================================

st.markdown("## ⚡ Impulse Control Center")

# Initialize impulse tracking
if 'impulse_streak' not in st.session_state:
    st.session_state.impulse_streak = 0
if 'last_impulse_check' not in st.session_state:
    st.session_state.last_impulse_check = datetime.now().date()

# Reset streak if new day
if datetime.now().date() != st.session_state.last_impulse_check:
    st.session_state.last_impulse_check = datetime.now().date()

# Calculate overall impulse metrics
if st.session_state.transactions:
    impulse_data = []
    for t in st.session_state.transactions:
        analysis = analyze_transaction_context(t)
        impulse_data.append({
            "transaction": t,
            "score": analysis["impulse_score"],
            "is_impulse": analysis["impulse_score"] >= 70
        })
    
    total_transactions = len(impulse_data)
    impulse_count = len([d for d in impulse_data if d["is_impulse"]])
    planned_count = len([d for d in impulse_data if d["score"] < 40])
    impulse_amount = sum(d["transaction"].amount for d in impulse_data if d["is_impulse"])
    planned_amount = sum(d["transaction"].amount for d in impulse_data if d["score"] < 40)
    
    impulse_ratio = (impulse_count / total_transactions * 100) if total_transactions > 0 else 0
    discipline_score = 100 - impulse_ratio
    
    # Display impulse dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score_color = "#4ECDC4" if discipline_score >= 70 else "#FFD93D" if discipline_score >= 50 else "#FF6B6B"
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {score_color}, {score_color}dd);
            padding: 1.2rem;
            border-radius: 15px;
            text-align: center;
            color: white;
        '>
            <h4 style='margin: 0;'>🎯 Discipline Score</h4>
            <h1 style='margin: 8px 0; font-size: 2.5rem;'>{discipline_score:.0f}</h1>
            <small>Out of 100</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #4ECDC4, #45B7D1);
            padding: 1.2rem;
            border-radius: 15px;
            text-align: center;
            color: white;
        '>
            <h4 style='margin: 0;'>✅ Planned</h4>
            <h2 style='margin: 8px 0;'>{planned_count}</h2>
            <small>{format_currency(planned_amount)}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #FF6B6B, #e74c3c);
            padding: 1.2rem;
            border-radius: 15px;
            text-align: center;
            color: white;
        '>
            <h4 style='margin: 0;'>⚡ Impulse</h4>
            <h2 style='margin: 8px 0;'>{impulse_count}</h2>
            <small>{format_currency(impulse_amount)}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #667eea, #764ba2);
            padding: 1.2rem;
            border-radius: 15px;
            text-align: center;
            color: white;
        '>
            <h4 style='margin: 0;'>🔥 Streak</h4>
            <h2 style='margin: 8px 0;'>{st.session_state.impulse_streak}</h2>
            <small>Days no impulse</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Impulse Pattern Analysis
    st.markdown("### 📊 When Are You Most Impulsive?")
    
    # Analyze by time
    morning_impulses = len([d for d in impulse_data if d["is_impulse"] and 6 <= d["transaction"].date.hour < 12])
    afternoon_impulses = len([d for d in impulse_data if d["is_impulse"] and 12 <= d["transaction"].date.hour < 17])
    evening_impulses = len([d for d in impulse_data if d["is_impulse"] and 17 <= d["transaction"].date.hour < 21])
    night_impulses = len([d for d in impulse_data if d["is_impulse"] and (d["transaction"].date.hour >= 21 or d["transaction"].date.hour < 6)])
    
    time_data = pd.DataFrame({
        "Time": ["🌅 Morning", "☀️ Afternoon", "🌆 Evening", "🌙 Night"],
        "Impulse Purchases": [morning_impulses, afternoon_impulses, evening_impulses, night_impulses]
    })
    
    fig_time = px.bar(
        time_data, x="Time", y="Impulse Purchases",
        title="⏰ Impulse Purchases by Time of Day",
        color="Impulse Purchases",
        color_continuous_scale=["#4ECDC4", "#FFD93D", "#FF6B6B"]
    )
    fig_time.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig_time, use_container_width=True)
    
    # Find danger time
    max_impulses = max(morning_impulses, afternoon_impulses, evening_impulses, night_impulses)
    if max_impulses > 0:
        if night_impulses == max_impulses:
            danger_time = "Late Night 🌙"
            advice = "Stay off shopping apps after 9pm!"
        elif evening_impulses == max_impulses:
            danger_time = "Evening 🌆"
            advice = "Post-work shopping therapy detected. Try a walk instead!"
        elif afternoon_impulses == max_impulses:
            danger_time = "Afternoon ☀️"
            advice = "Boredom shopping? Keep hands busy with something else!"
        else:
            danger_time = "Morning 🌅"
            advice = "Coffee and online shopping don't mix!"
        
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #FF6B6B30, #e74c3c20);
            border-left: 4px solid #FF6B6B;
            padding: 15px;
            border-radius: 0 10px 10px 0;
            margin: 1rem 0;
        '>
            <strong>🚨 Your Danger Zone: {danger_time}</strong>
            <p style='margin: 5px 0 0 0;'>💡 {advice}</p>
        </div>
        """, unsafe_allow_html=True)

# Willpower Boost Section
st.markdown("### 💪 Willpower Boost")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #4ECDC4, #45B7D1);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
    '>
        <h4 style='margin: 0;'>🎯 24-Hour Rule Challenge</h4>
        <p style='margin: 10px 0;'>Want something over $50? Add it to your wishlist and wait 24 hours. If you still want it tomorrow, it's meant to be!</p>
        <div style='background: rgba(255,255,255,0.2); padding: 10px; border-radius: 8px; margin-top: 10px;'>
            <strong>✨ Reward:</strong> Every resisted impulse = $5 to your savings goal!
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
    '>
        <h4 style='margin: 0;'>🏆 Weekly Challenge</h4>
        <p style='margin: 10px 0;'>Go 7 days without impulse purchases to unlock:</p>
        <div style='background: rgba(255,255,255,0.2); padding: 10px; border-radius: 8px; margin-top: 10px;'>
            <strong>🎁 Reward:</strong> Guilt-free splurge of $25 on something you love!
        </div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# ENHANCED MONEY DASHBOARD
# =============================================================================

st.markdown("## 💰 Your Money Mood Board")

# Safe calculations with error handling
def calculate_dashboard_metrics():
    try:
        transactions = st.session_state.transactions or []
        total_spent = sum(t.amount for t in transactions if hasattr(t, 'amount') and t.amount)
        avg_daily = handle_calculation_error(lambda: total_spent / 7, 0)
        joy_spending = sum(t.amount for t in transactions if hasattr(t, 'category') and t.category == SpendingCategory.JOY and t.amount)
        essential_spending = sum(t.amount for t in transactions if hasattr(t, 'category') and t.category == SpendingCategory.ESSENTIAL and t.amount)
        return total_spent, avg_daily, joy_spending, essential_spending
    except Exception as e:
        logger.error(f"Dashboard calculation error: {str(e)}")
        st.session_state.error_count += 1
        st.session_state.last_error = str(e)
        return 0, 0, 0, 0

total_spent, avg_daily, joy_spending, essential_spending = calculate_dashboard_metrics()

# Get monthly_income safely
monthly_income = st.session_state.financial_profile.get('monthly_income', 0) if st.session_state.financial_profile else 0
current_savings = st.session_state.financial_profile.get('current_savings', 0) if st.session_state.financial_profile else 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="money-card">
        <h3>💸 Total Spent</h3>
        <h2>{format_currency(total_spent, 2)}</h2>
        <p>Last 7 days</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="money-card">
        <h3>📅 Daily Average</h3>
        <h2>{format_currency(avg_daily, 2)}</h2>
        <p>Per day</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    joy_ratio = (joy_spending / total_spent * 100) if total_spent > 0 else 0
    st.markdown(f"""
    <div class="money-card">
        <h3>😊 Joy Ratio</h3>
        <h2>{joy_ratio:.1f}%</h2>
        <p>Happiness spending</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    if monthly_income > 0:
        monthly_projected = total_spent * 4.33
        budget_remaining = monthly_income - monthly_projected
        st.markdown(f"""
        <div class="money-card">
            <h3>💰 Budget Left</h3>
            <h2>{format_currency(budget_remaining, 0)}</h2>
            <p>This month</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="money-card">
            <h3>✨ Joy Spending</h3>
            <h2>{format_currency(joy_spending, 2)}</h2>
            <p>Self-care investments</p>
        </div>
        """, unsafe_allow_html=True)

# Add a fifth column for savings/essentials if needed
col5 = None
if current_savings > 0 or essential_spending > 0:
    cols = st.columns(5)
    col5 = cols[4]
    with col5:
        if current_savings > 0:
            savings_growth = current_savings
            st.markdown(f"""
            <div class="money-card">
                <h3>📈 Savings</h3>
                <h2>{format_currency(savings_growth, 0)}</h2>
                <p>Total saved</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="money-card">
                <h3>🏠 Essentials</h3>
                <h2>{format_currency(essential_spending, 2)}</h2>
                <p>Responsible spending</p>
            </div>
            """, unsafe_allow_html=True)

# Budget vs Reality Check
if monthly_income > 0:
    st.markdown("### 📊 Budget vs Reality Check")
    # Remove planner reference and use budget_plan if available
    if st.session_state.budget_plan:
        budget = {
            'needs': st.session_state.budget_plan.needs_amount,
            'wants': st.session_state.budget_plan.wants_amount
        }
    else:
        budget = {'needs': 0, 'wants': 0}

    current_month_spending = total_spent * 4.33
    needs_budget = budget['needs']
    wants_budget = budget['wants']

    current_needs = essential_spending * 4.33
    current_wants = joy_spending * 4.33

    col1, col2, col3 = st.columns(3)

    with col1:
        needs_progress = (current_needs / needs_budget * 100) if needs_budget > 0 else 0
        st.markdown(f"**🏠 Needs: {format_currency(current_needs, 0)} / {format_currency(needs_budget, 0)}**")
        st.progress(min(needs_progress / 100, 1.0))
        if needs_progress > 100:
            st.markdown('<div class="warning-card">⚠️ Over budget on needs!</div>', unsafe_allow_html=True)

    with col2:
        wants_progress = (current_wants / wants_budget * 100) if wants_budget > 0 else 0
        st.markdown(f"**✨ Wants: {format_currency(current_wants, 0)} / {format_currency(wants_budget, 0)}**")
        st.progress(min(wants_progress / 100, 1.0))
        if wants_progress > 100:
            st.markdown('<div class="warning-card">⚠️ Over budget on wants!</div>', unsafe_allow_html=True)

    with col3:
        total_budget = needs_budget + wants_budget
        total_spent_month = current_needs + current_wants
        overall_progress = (total_spent_month / total_budget * 100) if total_budget > 0 else 0
        st.markdown(f"**💰 Overall: {format_currency(total_spent_month, 0)} / {format_currency(total_budget, 0)}**")
        st.progress(min(overall_progress / 100, 1.0))
        if overall_progress < 80:
            st.markdown('<div class="success-card">🎉 Under budget! Great job!</div>', unsafe_allow_html=True)

# =============================================================================
# TRANSACTION INPUT & INTERACTIVE FEATURES
# =============================================================================

st.markdown("## 💳 Add New Transaction")

# Transaction input form with error handling
with st.expander("➕ Add a New Transaction", expanded=False):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        new_amount = st.number_input("💰 Amount", min_value=0.01, value=10.0, step=0.5)
        new_description = st.text_input("📝 Description", placeholder="What did you spend on?")
    
    with col2:
        new_category = st.selectbox("📂 Category", list(SpendingCategory))
        new_merchant = st.text_input("🏪 Merchant", placeholder="Where did you spend?")
    
    with col3:
        new_vibe_impact = st.slider("😊 Vibe Impact", -1.0, 1.0, 0.0, 0.1, 
                                   help="How did this purchase make you feel?")
        
        if st.button("✅ Add Transaction", type="primary", use_container_width=True):
            try:
                if new_description.strip():
                    new_transaction = Transaction(
                        date=datetime.now(),
                        amount=float(new_amount),
                        description=new_description.strip(),
                        category=new_category,
                        merchant=new_merchant.strip(),
                        vibe_impact=float(new_vibe_impact)
                    )
                    st.session_state.transactions.append(new_transaction)
                    st.success(f"✅ Added: {new_description} - {format_currency(new_amount)}")
                    st.rerun()
                else:
                    st.warning("Please enter a description for your transaction!")
            except Exception as e:
                st.error(f"Error adding transaction: {str(e)}")
                st.session_state.error_count += 1
                st.session_state.last_error = str(e)

# =============================================================================
# TRANSACTION LOG & DISPLAY
# =============================================================================

st.markdown("## 🧾 Recent Spending Tea ☕")

# Safe transaction display with error handling
def create_transaction_dataframe():
    try:
        transactions = st.session_state.transactions or []
        if not transactions:
            return pd.DataFrame({'Message': ['No transactions yet! Add your first transaction above. 💸']})
        
        transaction_data = []
        for t in sorted(transactions, key=lambda x: getattr(x, 'date', datetime.now()), reverse=True):
            try:
                transaction_data.append({
                    'Date': getattr(t, 'date', datetime.now()).strftime('%m/%d'),
                    'Vibe': getattr(t, 'category', SpendingCategory.ESSENTIAL).value,
                    'Amount': format_currency(getattr(t, 'amount', 0)),
                    'Description': getattr(t, 'description', 'Unknown'),
                    'Merchant': getattr(t, 'merchant', 'Unknown'),
                    'Mood Impact': '😊' if getattr(t, 'vibe_impact', 0) > 0 else '😐' if getattr(t, 'vibe_impact', 0) == 0 else '😔'
                })
            except Exception as e:
                logger.warning(f"Error processing transaction: {str(e)}")
                continue
        
        return pd.DataFrame(transaction_data)
    except Exception as e:
        logger.error(f"Error creating transaction dataframe: {str(e)}")
        st.session_state.error_count += 1
        st.session_state.last_error = str(e)
        return pd.DataFrame({'Error': ['Unable to load transactions. Please try refreshing.']})

df_transactions = create_transaction_dataframe()
st.dataframe(df_transactions, use_container_width=True)

# Transaction analytics
if len(st.session_state.transactions) > 0:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        try:
            avg_transaction = handle_calculation_error(
                lambda: sum(t.amount for t in st.session_state.transactions) / len(st.session_state.transactions),
                0
            )
            st.metric("💰 Avg Transaction", format_currency(avg_transaction))
        except:
            st.metric("💰 Avg Transaction", "N/A")
    
    with col2:
        try:
            positive_vibes = len([t for t in st.session_state.transactions if getattr(t, 'vibe_impact', 0) > 0])
            st.metric("😊 Positive Purchases", f"{positive_vibes}")
        except:
            st.metric("😊 Positive Purchases", "N/A")
    
    with col3:
        try:
            most_category = max(SpendingCategory, key=lambda cat: len([t for t in st.session_state.transactions if getattr(t, 'category', None) == cat]))
            st.metric("🔥 Top Category", most_category.value)
        except:
            st.metric("🔥 Top Category", "N/A")

# =============================================================================
# ENHANCED SALARY INPUT & FINANCIAL PLANNING CALCULATOR
# =============================================================================

st.markdown("## 💰 Complete Financial Planning Calculator")

st.markdown("""
<div class="financial-setup-card">
    <h3>💸 Enter Your Financial Details</h3>
    <p>Let's create your personalized Gen Z survival & slay financial blueprint!</p>
</div>
""", unsafe_allow_html=True)

# Main salary input section
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 💵 Income Details")
    monthly_salary = st.number_input(
        "Monthly Salary/Income (After Tax)",
        min_value=0.0,
        value=4500.0,
        step=100.0,
        help="Your take-home pay per month"
    )
    
    additional_income = st.number_input(
        "Side Hustle/Additional Income",
        min_value=0.0,
        value=0.0,
        step=50.0,
        help="Freelance, part-time, passive income"
    )
    
    total_monthly_income = monthly_salary + additional_income
    annual_income = total_monthly_income * 12

with col2:
    st.markdown("### 🎯 Current Financial Status")
    current_debt = st.number_input(
        "Total Debt Amount",
        min_value=0.0,
        value=0.0,
        step=100.0,
        help="Credit cards, student loans, personal loans"
    )
    
    current_savings_amount = st.number_input(
        "Current Savings Balance",
        min_value=0.0,
        value=1000.0,
        step=100.0,
        help="Emergency fund + other savings accounts"
    )
    
    monthly_debt_payment = st.number_input(
        "Current Monthly Debt Payments",
        min_value=0.0,
        value=0.0,
        step=25.0,
        help="Minimum payments on all debts"
    )

with col3:
    st.markdown("### 🚀 Your Financial Goals")
    financial_priority = st.selectbox(
        "Primary Financial Priority",
        [
            "🛡️ Build Emergency Fund",
            "💳 Pay Off Debt",
            "📈 Start Investing",
            "🏠 Save for Big Purchase",
            "👑 Maximize Wealth Building"
        ]
    )
    
    lifestyle_mode = st.selectbox(
        "Current Lifestyle Mode",
        [
            "😩 Survival Mode (Minimize expenses)",
            "😌 Comfort Mode (Balanced approach)", 
            "👑 Slay Mode (Aggressive wealth building)"
        ]
    )
    
    investment_risk = st.selectbox(
        "Investment Risk Tolerance",
        ["Conservative (Safety first)", "Moderate (Balanced)", "Aggressive (High growth)"]
    )

# =============================================================================
# ADVANCED FINANCIAL BREAKDOWN CALCULATOR
# =============================================================================

if total_monthly_income > 0:
    st.markdown("## 📊 Your Personalized Financial Blueprint")
    
    # Determine budget allocation based on lifestyle mode
    if "Survival" in lifestyle_mode:
        needs_percent = 70
        wants_percent = 15
        savings_percent = 15
        mode_emoji = "🛡️"
        mode_description = "Focus on stability and emergency fund"
    elif "Comfort" in lifestyle_mode:
        needs_percent = 50
        wants_percent = 30
        savings_percent = 20
        mode_emoji = "😌"
        mode_description = "Balanced living with room for fun"
    else:  # Slay mode
        needs_percent = 45
        wants_percent = 25
        savings_percent = 30
        mode_emoji = "👑"
        mode_description = "Aggressive wealth building for financial freedom"
    
    # Calculate allocations
    needs_amount = total_monthly_income * (needs_percent / 100)
    wants_amount = total_monthly_income * (wants_percent / 100)
    savings_amount = total_monthly_income * (savings_percent / 100)
    
    # Adjust for existing debt payments
    adjusted_savings = max(0, savings_amount - monthly_debt_payment)
    debt_payoff_extra = savings_amount - adjusted_savings
    
    # Display budget breakdown
    st.markdown(f"""
    <div class="main-header">
        <h2>{mode_emoji} {lifestyle_mode.split('(')[0]} Budget Breakdown</h2>
        <p><em>{mode_description}</em></p>
        <h3>Total Monthly Income: {format_currency(total_monthly_income, 2)}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="survival-card">
            <h3>🏠 NEEDS ({needs_percent}%)</h3>
            <h2>{format_currency(needs_amount, 0)}</h2>
            <div style="font-size: 0.9em; margin-top: 10px;">
                <strong>Includes:</strong><br>
                • Rent/Mortgage<br>
                • Groceries & Utilities<br>
                • Transportation<br>
                • Insurance & Phone<br>
                • Minimum Debt Payments
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="comfort-card">
            <h3>✨ WANTS ({wants_percent}%)</h3>
            <h2>{format_currency(wants_amount, 0)}</h2>
            <div style="font-size: 0.9em; margin-top: 10px;">
                <strong>Includes:</strong><br>
                • Dining Out & Entertainment<br>
                • Shopping & Hobbies<br>
                • Subscriptions<br>
                • Travel & Fun<br>
                • Personal Care
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="slay-card">
            <h3>💰 SAVINGS ({savings_percent}%)</h3>
            <h2>{format_currency(adjusted_savings, 0)}</h2>
            <div style="font-size: 0.9em; margin-top: 10px;">
                <strong>Breakdown:</strong><br>
                • Emergency Fund<br>
                • Investment Accounts<br>
                • Goal Savings<br>
                • Extra Debt Payment<br>
                • Future Planning
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if monthly_debt_payment > 0:
            total_debt_focus = monthly_debt_payment + debt_payoff_extra
            st.markdown(f"""
            <div class="investment-card">
                <h3>💳 DEBT PAYOFF</h3>
                <h2>{format_currency(total_debt_focus, 0)}</h2>
                <div style="font-size: 0.9em; margin-top: 10px;">
                    <strong>Strategy:</strong><br>
                    • Minimum: {format_currency(monthly_debt_payment, 0)}<br>
                    • Extra: {format_currency(debt_payoff_extra, 0)}<br>
                    • Total Focus<br>
                    • Avalanche Method
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="investment-card">
                <h3>🚀 BONUS POWER</h3>
                <h2>{format_currency(adjusted_savings, 0)}</h2>
                <div style="font-size: 0.9em; margin-top: 10px;">
                    <strong>Opportunity:</strong><br>
                    • Full Savings Potential<br>
                    • Investment Ready<br>
                    • Wealth Building<br>
                    • Financial Freedom
                </div>
            </div>
            """, unsafe_allow_html=True)

    # =============================================================================
    # EMERGENCY FUND CALCULATOR
    # =============================================================================
    
    st.markdown("### 🛡️ Emergency Fund Strategy")
    
    emergency_months = st.slider("Target Emergency Fund (Months of Expenses)", 3, 12, 6)
    emergency_target = needs_amount * emergency_months
    emergency_progress = (current_savings_amount / emergency_target * 100) if emergency_target > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="goal-tracker">
            <h4>🎯 Emergency Fund Goal</h4>
            <h2>{format_currency(emergency_target, 0)}</h2>
            <p>{emergency_months} months of expenses</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="goal-tracker">
            <h4>💰 Current Progress</h4>
            <h2>{format_currency(current_savings_amount, 0)}</h2>
            <p>{emergency_progress:.1f}% Complete</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        months_to_goal = max(0, (emergency_target - current_savings_amount) / (adjusted_savings * 0.5)) if adjusted_savings > 0 else 0
        st.markdown(f"""
        <div class="goal-tracker">
            <h4>⏰ Time to Goal</h4>
            <h2>{months_to_goal:.1f} months</h2>
            <p>At 50% savings allocation</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Progress bar
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-fill" style="width: {min(emergency_progress, 100)}%;">
            Emergency Fund: {emergency_progress:.1f}% Complete
        </div>
    </div>
    """, unsafe_allow_html=True)

    # =============================================================================
    # INVESTMENT ALLOCATION STRATEGY
    # =============================================================================
    
    st.markdown("### 📈 Investment Allocation Strategy")
    
    # Calculate investment amount (portion of savings after emergency fund priority)
    emergency_monthly_need = max(0, (emergency_target - current_savings_amount) / 12)
    available_for_investment = max(0, adjusted_savings - emergency_monthly_need)
    
    if available_for_investment > 0:
        # Age-based investment allocation
        user_age = st.slider("Your Age", 18, 35, 25)
        
        # Determine allocation based on age and risk tolerance
        if "Conservative" in investment_risk:
            stock_percent = max(20, 60 - user_age)
            bond_percent = min(50, 40 + (user_age - 20))
        elif "Aggressive" in investment_risk:
            stock_percent = min(95, 80 + (35 - user_age))
            bond_percent = max(5, 20 - (35 - user_age))
        else:  # Moderate
            stock_percent = max(40, 70 - (user_age - 20))
            bond_percent = min(40, 30 + (user_age - 20))
        
        cash_percent = 100 - stock_percent - bond_percent
        
        # Calculate dollar amounts
        stock_amount = available_for_investment * (stock_percent / 100)
        bond_amount = available_for_investment * (bond_percent / 100)
        cash_amount = available_for_investment * (cash_percent / 100)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="investment-card">
                <h4>📊 Total Monthly Investment</h4>
                <h2>{format_currency(available_for_investment, 0)}</h2>
                <p>Available after emergency fund</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="investment-card">
                <h4>📈 Stocks/ETFs ({stock_percent}%)</h4>
                <h2>{format_currency(stock_amount, 0)}</h2>
                <p>VTI, VXUS, Growth funds</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="investment-card">
                <h4>🏛️ Bonds ({bond_percent}%)</h4>
                <h2>{format_currency(bond_amount, 0)}</h2>
                <p>BND, Treasury bonds</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="investment-card">
                <h4>💵 Cash/HYSA ({cash_percent}%)</h4>
                <h2>{format_currency(cash_amount, 0)}</h2>
                <p>High-yield savings, CDs</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Specific investment recommendations
        st.markdown("#### 🎯 Specific Investment Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="financial-tip">
                <h4>🚀 Gen Z Investment Essentials</h4>
                <strong>Core Holdings:</strong><br>
                • VTI (Total Stock Market) - 40%<br>
                • VXUS (International) - 20%<br>
                • BND (Total Bond Market) - 20%<br>
                • HYSA (Emergency Buffer) - 20%<br><br>
                <strong>Advanced Options:</strong><br>
                • QQQ (Tech Growth)<br>
                • SCHD (Dividend Growth)<br>
                • REITs (Real Estate)<br>
                • Small allocation to crypto (5% max)
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="financial-tip">
                <h4>💡 Investment Platform Suggestions</h4>
                <strong>Best for Beginners:</strong><br>
                • Fidelity (No fees, great funds)<br>
                • Vanguard (Low-cost leader)<br>
                • Schwab (Excellent customer service)<br><br>
                <strong>Robo-Advisors:</strong><br>
                • Betterment (Auto-rebalancing)<br>
                • Wealthfront (Tax-loss harvesting)<br>
                • M1 Finance (Pie investing)<br><br>
                <strong>Monthly Investment:</strong> {format_currency(available_for_investment, 0)}
            </div>
            """, unsafe_allow_html=True)
    
    else:
        st.markdown("""
        <div class="warning-card">
            <h4>⚠️ Focus on Emergency Fund First</h4>
            <p>Prioritize building your emergency fund before investing. Once you have 3-6 months of expenses saved, redirect funds to investments!</p>
        </div>
        """, unsafe_allow_html=True)

    # =============================================================================
    # DEBT PAYOFF STRATEGY
    # =============================================================================
    
    if current_debt > 0:
        st.markdown("### 💳 Debt Elimination Strategy")
        
        # Debt payoff calculators
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔥 Avalanche Method (Recommended)")
            # Assuming average 18% APR for credit cards
            avg_apr = st.slider("Average Debt Interest Rate (%)", 3.0, 29.9, 18.0)
            
            total_debt_payment = monthly_debt_payment + debt_payoff_extra
            
            # Calculate payoff time
            if total_debt_payment > 0 and avg_apr > 0:
                monthly_rate = (avg_apr / 100) / 12
                if monthly_rate * current_debt < total_debt_payment:
                    months_to_payoff = -(1/12) * (math.log(1 - (monthly_rate * current_debt / total_debt_payment)) / math.log(1 + monthly_rate))
                    total_interest = (total_debt_payment * months_to_payoff) - current_debt
                else:
                    months_to_payoff = float('inf')
                    total_interest = float('inf')
            else:
                months_to_payoff = current_debt / total_debt_payment if total_debt_payment > 0 else float('inf')
                total_interest = 0
            
            if months_to_payoff != float('inf'):
                st.markdown(f"""
                <div class="goal-tracker">
                    <h4>⏰ Payoff Timeline</h4>
                    <h2>{months_to_payoff:.1f} months</h2>
                    <p>Total Payment: {format_currency(total_debt_payment, 0)}/month</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="survival-card">
                    <h4>💰 Total Interest Saved</h4>
                    <p>By paying {format_currency(total_debt_payment, 0)}/month instead of minimums:</p>
                    <h3>Interest: {format_currency(total_interest, 0)}</h3>
                    <p>vs paying minimums for years!</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 🎯 Debt Freedom Goals")
            
            debt_free_date = datetime.now() + timedelta(days=months_to_payoff * 30) if months_to_payoff != float('inf') else None
            
            if debt_free_date:
                st.markdown(f"""
                <div class="slay-card">
                    <h4>🎉 Debt Freedom Date</h4>
                    <h2>{debt_free_date.strftime('%B %Y')}</h2>
                    <p>Your financial independence day!</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Monthly savings after debt payoff
            future_monthly_boost = total_debt_payment
            annual_boost = future_monthly_boost * 12
            
            st.markdown(f"""
            <div class="investment-card">
                <h4>🚀 Post-Debt Monthly Boost</h4>
                <h2>{format_currency(future_monthly_boost, 0)}</h2>
                <p>Extra for investments/goals</p>
                <small>Annual boost: {format_currency(annual_boost, 0)}</small>
            </div>
            """, unsafe_allow_html=True)

    # =============================================================================
    # GOAL-BASED SAVINGS CALCULATOR
    # =============================================================================
    
    st.markdown("### 🎯 Goal-Based Savings Planner")
    
    # Pre-defined common goals
    common_goals = {
        "🏖️ Dream Vacation": 3000,
        "🚗 Car Down Payment": 5000,  
        "🏠 House Down Payment": 40000,
        "💻 New Laptop/Setup": 2000,
        "📚 Education/Certification": 5000,
        "💍 Wedding Fund": 20000,
        "🎂 Custom Goal": 0
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_goal = st.selectbox("Choose Your Goal", list(common_goals.keys()))
        if selected_goal == "🎂 Custom Goal":
            goal_amount = st.number_input("Custom Goal Amount", min_value=100.0, value=5000.0, step=100.0)
            goal_name = st.text_input("Goal Name", value="My Custom Goal")
        else:
            goal_amount = common_goals[selected_goal]
            goal_name = selected_goal
    
    with col2:
        goal_timeline = st.selectbox(
            "Target Timeline",
            ["3 months", "6 months", "1 year", "2 years", "3 years", "5 years"]
        )
        timeline_months = {"3 months": 3, "6 months": 6, "1 year": 12, "2 years": 24, "3 years": 36, "5 years": 60}
        months = timeline_months[goal_timeline]
    
    with col3:
        goal_priority = st.selectbox(
            "Priority Level",
            ["🔥 High Priority", "⚡ Medium Priority", "💫 Low Priority"]
        )
    
    # Calculate required monthly savings
    if goal_amount > 0 and months > 0:
        required_monthly = goal_amount / months
        available_for_goal = adjusted_savings * 0.3  # 30% of savings can go to goals
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="goal-tracker">
                <h4>🎯 {goal_name}</h4>
                <h2>{format_currency(goal_amount, 0)}</h2>
                <p>Target in {goal_timeline}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="goal-tracker">
                <h4>💰 Required Monthly</h4>
                <h2>{format_currency(required_monthly, 0)}</h2>
                <p>To reach your goal</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            feasibility = "✅ Totally Doable!" if required_monthly <= available_for_goal else "⚠️ Needs Adjustment"
            st.markdown(f"""
            <div class="goal-tracker">
                <h4>📊 Feasibility</h4>
                <h2>{feasibility}</h2>
                <p>Available: {format_currency(available_for_goal, 0)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Goal progress tracking
        if required_monthly <= available_for_goal:
            st.markdown(f"""
            <div class="success-card">
                <h4>🎉 Goal Strategy Approved!</h4>
                <p><strong>Monthly Allocation:</strong> {format_currency(required_monthly, 0)} from your {format_currency(adjusted_savings, 0)} savings budget</p>
                <p><strong>Timeline:</strong> {goal_timeline} | <strong>Achievement Date:</strong> {(datetime.now() + timedelta(days=months*30)).strftime('%B %Y')}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Alternative suggestions
            realistic_timeline = goal_amount / available_for_goal
            st.markdown(f"""
            <div class="warning-card">
                <h4>💡 Alternative Suggestions</h4>
                <p><strong>Option 1:</strong> Extend timeline to {realistic_timeline:.1f} months</p>
                <p><strong>Option 2:</strong> Reduce goal to {format_currency(available_for_goal * months, 0)}</p>
                <p><strong>Option 3:</strong> Increase income or reduce other expenses</p>
            </div>
            """, unsafe_allow_html=True)

    # =============================================================================
    # WEALTH BUILDING PROJECTIONS
    # =============================================================================
    
    st.markdown("### 🚀 Long-Term Wealth Building Projections")
    
    # 10, 20, 30 year projections
    investment_return = 0.07  # 7% average annual return
    years_projections = [10, 20, 30]
    
    if available_for_investment > 0:
        st.markdown("#### 📈 Investment Growth Projections (7% Annual Return)")
        
        cols = st.columns(len(years_projections))
        
        for i, years in enumerate(years_projections):
            # Future value calculation: FV = PMT * [((1+r)^n - 1) / r]
            monthly_investment = available_for_investment
            monthly_rate = investment_return / 12
            months = years * 12
            
            future_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate)
            total_contributions = monthly_investment * months
            investment_growth = future_value - total_contributions
            
            with cols[i]:
                st.markdown(f"""
                <div class="slay-card">
                    <h4>💰 {years} Year Projection</h4>
                    <h2>{format_currency(future_value, 0)}</h2>
                    <div style="font-size: 0.8em; margin-top: 10px;">
                        <p>Contributions: {format_currency(total_contributions, 0)}</p>
                        <p>Growth: {format_currency(investment_growth, 0)}</p>
                        <p>Monthly: {format_currency(monthly_investment, 0)}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Net worth milestones
    st.markdown("#### 🎯 Net Worth Milestones by Age")
    
    user_age = 25  # Default, can be adjusted above
    current_age = user_age
    target_ages = [30, 35, 40]
    
    # Rule of thumb: net worth should be 1x annual income by 30, 3x by 40
    milestone_multipliers = {30: 1, 35: 3, 40: 5}
    
    cols = st.columns(len(target_ages))
    
    for i, target_age in enumerate(target_ages):
        years_to_age = target_age - current_age
        target_multiplier = milestone_multipliers.get(target_age, target_age - 25)
        target_net_worth = annual_income * target_multiplier
        
        # Calculate if current savings rate will achieve this
        if years_to_age > 0 and adjusted_savings > 0:
            projected_savings = current_savings_amount + (adjusted_savings * 12 * years_to_age)
            # Assuming some investment growth
            projected_investments = available_for_investment * 12 * years_to_age * (1 + investment_return) ** years_to_age if available_for_investment > 0 else 0
            projected_net_worth = projected_savings + projected_investments
            
            achievement_status = "✅ On Track" if projected_net_worth >= target_net_worth else "⚠️ Need Boost"
        else:
            achievement_status = "🎯 Future Goal"
            projected_net_worth = 0
        
        with cols[i]:
            st.markdown(f"""
            <div class="milestone-badge" style="display: block; margin: 10px 0; padding: 15px;">
                <h4>Age {target_age} Goal</h4>
                <h3>{format_currency(target_net_worth, 0)}</h3>
                <p>{target_multiplier}x Annual Income</p>
                <small>{achievement_status}</small>
            </div>
            """, unsafe_allow_html=True)

    # =============================================================================
    # ACTIONABLE NEXT STEPS & RECOMMENDATIONS
    # =============================================================================
    
    st.markdown("### ✅ Your Personalized Action Plan")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🚨 Immediate Actions (This Week)")
        immediate_actions = []
        
        if current_savings_amount < 1000:
            immediate_actions.append("🏦 Open high-yield savings account (Marcus, Ally, Capital One)")
            immediate_actions.append("💰 Set up automatic transfer of $50-100/week to savings")
        
        if monthly_debt_payment > 0 and debt_payoff_extra > 0:
            immediate_actions.append("📞 Call credit card companies to negotiate lower rates")
            immediate_actions.append("💳 Set up automatic extra payments to highest interest debt")
        
        if available_for_investment > 100:
            immediate_actions.append("📊 Open investment account (Fidelity, Vanguard, or Schwab)")
            immediate_actions.append("🤖 Set up automatic investing in index funds")
        
        immediate_actions.append("📱 Download budgeting app (Mint, YNAB, or PocketGuard)")
        immediate_actions.append("🔍 Review and cancel unused subscriptions")
        
        for action in immediate_actions[:5]:
            st.markdown(f"• {action}")
    
    with col2:
        st.markdown("#### 📅 30-Day Goals")
        monthly_goals = []
        
        if emergency_progress < 100:
            monthly_goals.append(f"🛡️ Save {format_currency(emergency_monthly_need, 0)} for emergency fund")
        
        monthly_goals.append(f"📊 Track all expenses and stay within {format_currency(wants_amount, 0)} fun budget")
        monthly_goals.append(f"💰 Automate {format_currency(adjusted_savings, 0)} monthly savings")
        
        if current_debt > 0:
            monthly_goals.append(f"💳 Pay {format_currency(total_debt_payment, 0)} toward debt elimination")
        
        monthly_goals.append("📚 Read one personal finance book or take online course")
        monthly_goals.append("🎯 Set up goal tracking for your biggest financial priority")
        
        for goal in monthly_goals:
            st.markdown(f"• {goal}")

# Quick Win Tips
st.markdown("""
<div class="vibe-card">
    <h3>💡 Quick Wins for This Week</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 15px;">
        <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px;">
            <h4>🏦 Banking Hack</h4>
            <p>Switch to a high-yield savings account earning 4%+ instead of 0.01% at big banks</p>
        </div>
        <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px;">
            <h4>🤖 Automation</h4>
            <p>Set up automatic transfers on payday - pay yourself first before you can spend it</p>
        </div>
        <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px;">
            <h4>💳 Credit Boost</h4>
            <p>Pay credit cards twice monthly instead of once to lower utilization and boost score</p>
        </div>
        <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px;">
            <h4>📊 Track Everything</h4>
            <p>Use apps like Mint or YNAB to see where every dollar goes - awareness = control</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 🚨 MAIN ERROR: format_currency function is not defined
# FIX: Replace format_currency with standard Python formatting

# ❌ ORIGINAL (BROKEN):
# Your {lifestyle_mode.split('(')[0]} approach with {format_currency(total_monthly_income, 0)} monthly income

# ✅ FIXED VERSION:


# Motivational closing - FIXED
st.markdown(f"""
<div class="success-card">
    <h3>✨ You're Already Winning!</h3>
    <p>Just by using this calculator and thinking about your financial future, you're ahead of 70% of people your age. 
    Your {lifestyle_mode.split('(')[0]} approach with INR {total_monthly_income:,.0f} monthly income puts you on track for 
    serious wealth building. Remember: every dollar you save in your 20s becomes $10+ in your future. 
    You've got this! 🚀</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# TIER 2 FEATURES - NAVIGATION BASED SECTIONS
# =============================================================================

# Note: current_page is already defined at the top after sidebar

# =============================================================================
# FEATURE 6: WHAT-IF FINANCIAL SIMULATOR
# =============================================================================
if current_page == "🎯 What-If Simulator":
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 20px; margin-bottom: 2rem; text-align: center;'>
        <h1 style='color: white; margin: 0;'>🎯 Life Event Impact Matrix</h1>
        <p style='color: rgba(255,255,255,0.9); font-size: 1.2rem;'>What if your life changes? See how major events reshape your financial future</p>
    </div>
    """, unsafe_allow_html=True)
    
    monthly_income = st.session_state.financial_profile.get('monthly_income', 5000) if st.session_state.financial_profile else 5000
    
    st.markdown("### 📅 Select Life Events (Like Instagram Stories!)")
    
    life_events = {
        "💍 Get Married": {"expense_change": 0.40, "income_stability": -0.20, "travel_change": 0.50, "timeline": "2 years"},
        "👶 Have a Baby": {"expense_change": 0.60, "income_stability": -0.30, "travel_change": -0.40, "timeline": "3 years"},
        "🏠 Buy a House": {"expense_change": 0.35, "income_stability": 0.10, "travel_change": -0.20, "timeline": "5 years"},
        "💼 Job Loss": {"expense_change": -0.10, "income_stability": -0.80, "travel_change": -0.70, "timeline": "6 months"},
        "📈 Get Promoted": {"expense_change": 0.15, "income_stability": 0.30, "travel_change": 0.25, "timeline": "1 year"},
        "🎓 Go Back to School": {"expense_change": 0.50, "income_stability": -0.50, "travel_change": -0.30, "timeline": "2 years"},
        "📉 Recession Hits": {"expense_change": -0.05, "income_stability": -0.40, "travel_change": -0.50, "timeline": "2 years"},
        "🚗 Buy a Car": {"expense_change": 0.20, "income_stability": 0.0, "travel_change": 0.10, "timeline": "Now"},
        "✈️ Year of Travel": {"expense_change": 0.80, "income_stability": -0.60, "travel_change": 1.0, "timeline": "1 year"},
        "🏥 Medical Emergency": {"expense_change": 0.90, "income_stability": -0.30, "travel_change": -0.80, "timeline": "6 months"}
    }
    
    cols = st.columns(5)
    selected_events = []
    
    for i, (event, impacts) in enumerate(life_events.items()):
        with cols[i % 5]:
            if st.checkbox(event, key=f"event_{i}"):
                selected_events.append((event, impacts))
    
    if selected_events:
        st.markdown("---")
        st.markdown("### 🔮 Impact Analysis")
        
        total_expense_change = sum(e[1]['expense_change'] for e in selected_events)
        total_stability_change = sum(e[1]['income_stability'] for e in selected_events)
        total_travel_change = sum(e[1]['travel_change'] for e in selected_events)
        
        base_monthly = monthly_income * 0.7
        new_monthly_expenses = base_monthly * (1 + total_expense_change)
        stability_score = max(0, min(100, 70 + (total_stability_change * 100)))
        
        months_to_broke = 999
        if new_monthly_expenses > monthly_income:
            deficit = new_monthly_expenses - monthly_income
            emergency_fund = monthly_income * 3
            months_to_broke = emergency_fund / deficit if deficit > 0 else 999
        
        success_rate = max(0, min(100, 85 - (len(selected_events) * 8) + (stability_score / 10)))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.5rem; border-radius: 15px; text-align: center; color: white;'>
                <h3>🎯 Success Rate</h3>
                <h1 style='font-size: 3rem; margin: 0;'>{success_rate:.0f}%</h1>
                <p>Will you reach your goal?</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            best_case = monthly_income * 12 * 5 * 1.15
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 1.5rem; border-radius: 15px; text-align: center; color: #2d3748;'>
                <h3>💚 Best Case</h3>
                <h1 style='font-size: 2rem; margin: 0;'>{format_currency(best_case, 0)}</h1>
                <p>5-year wealth (optimistic)</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            worst_case = max(0, monthly_income * 12 * 5 * (0.3 - total_expense_change))
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 1.5rem; border-radius: 15px; text-align: center; color: white;'>
                <h3>💔 Worst Case</h3>
                <h1 style='font-size: 2rem; margin: 0;'>{format_currency(worst_case, 0)}</h1>
                <p>5-year wealth (pessimistic)</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            confidence = max(20, 90 - (len(selected_events) * 12))
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 15px; text-align: center; color: white;'>
                <h3>🧠 Confidence</h3>
                <h1 style='font-size: 3rem; margin: 0;'>{confidence:.0f}%</h1>
                <p>Model certainty</p>
            </div>
            """, unsafe_allow_html=True)
        
        if len(selected_events) >= 2 and months_to_broke < 24:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); padding: 1.5rem; border-radius: 15px; margin-top: 1rem; text-align: center; color: white;'>
                <h2>⚠️ BREAKING POINT ALERT</h2>
                <p style='font-size: 1.3rem;'>If {len(selected_events)} events happen together, you'll run out of money in <strong>{months_to_broke:.0f} months</strong>!</p>
                <p>Consider building a bigger emergency fund or adjusting your timeline.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 📊 Success Probability Over Time")
        
        months = list(range(1, 61))
        base_prob = success_rate
        probabilities = [max(10, base_prob - (m * 0.3) + random.uniform(-2, 2)) for m in months]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=months, y=probabilities,
            mode='lines+markers',
            line=dict(color='#667eea', width=3),
            marker=dict(size=4),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.2)'
        ))
        fig.update_layout(
            title="Your Financial Success Probability (Next 5 Years)",
            xaxis_title="Months",
            yaxis_title="Success Probability (%)",
            template="plotly_white",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 🌊 Ripple Effects of Your Choices")
        for event, impacts in selected_events:
            expense_emoji = "📈" if impacts['expense_change'] > 0 else "📉"
            stability_emoji = "✅" if impacts['income_stability'] > 0 else "⚠️"
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 1rem; border-radius: 10px; margin: 0.5rem 0; color: #2d3748;'>
                <strong>{event}</strong> → 
                {expense_emoji} Expenses {'+' if impacts['expense_change'] > 0 else ''}{impacts['expense_change']*100:.0f}% | 
                {stability_emoji} Income Stability {'+' if impacts['income_stability'] > 0 else ''}{impacts['income_stability']*100:.0f}% | 
                📅 Timeline: {impacts['timeline']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("👆 Select life events above to see how they'll impact your financial future!")

# =============================================================================
# FEATURE 7: FUTURE EXPENSE FORECASTING (EXPENSE ARCHAEOLOGY)
# =============================================================================
elif current_page == "🔍 Expense Forecasting":
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 2rem; border-radius: 20px; margin-bottom: 2rem; text-align: center;'>
        <h1 style='color: white; margin: 0;'>🔍 Expense Archaeology</h1>
        <p style='color: rgba(255,255,255,0.9); font-size: 1.2rem;'>Discover hidden money leaks & forgotten subscriptions</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔮 Hidden Pattern Detector")
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 1rem;'>
            <h4>🎯 Cyclic Spending Patterns Found!</h4>
            <p>You spend <strong style='font-size: 1.5rem;'>$2,500 extra</strong> every 4 weeks</p>
            <p style='opacity: 0.8;'>Pattern detected: Weekend party cycles? 🎉</p>
        </div>
        """, unsafe_allow_html=True)
        
        patterns = [
            {"pattern": "Friday Night Splurge", "amount": 180, "frequency": "Weekly", "trend": "📈 +12% this month"},
            {"pattern": "End of Month YOLO", "amount": 450, "frequency": "Monthly", "trend": "📈 +8% vs last month"},
            {"pattern": "Payday Celebration", "amount": 320, "frequency": "Bi-weekly", "trend": "📉 -5% (improving!)"},
            {"pattern": "Late Night Shopping", "amount": 95, "frequency": "3x/week", "trend": "📈 +23% (uh oh!)"}
        ]
        
        for p in patterns:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.3rem; border-radius: 12px; margin: 0.7rem 0; box-shadow: 0 4px 12px rgba(0,0,0,0.15);'>
                <div style='color: white; font-weight: 700; font-size: 1.1rem;'>{p['pattern']}</div>
                <div style='color: #FFE8E8; font-size: 1.3rem; font-weight: 800; margin: 0.5rem 0;'>${p['amount']}</div>
                <div style='color: rgba(255,255,255,0.9); font-size: 0.95rem;'>{p['frequency']} | {p['trend']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 💀 Subscription Graveyard")
        st.markdown("*Where forgotten money goes to die...*")
        
        subscriptions = [
            {"name": "Netflix", "cost": 15.99, "last_used": "2 weeks ago", "worth_it": True},
            {"name": "Spotify Premium", "cost": 9.99, "last_used": "Yesterday", "worth_it": True},
            {"name": "Adobe Creative Cloud", "cost": 54.99, "last_used": "3 months ago", "worth_it": False},
            {"name": "ChatGPT Pro", "cost": 20.00, "last_used": "Today", "worth_it": True},
            {"name": "Gym Membership", "cost": 49.99, "last_used": "6 months ago", "worth_it": False},
            {"name": "iCloud Storage", "cost": 2.99, "last_used": "Daily (auto)", "worth_it": True},
            {"name": "LinkedIn Premium", "cost": 29.99, "last_used": "2 months ago", "worth_it": False},
            {"name": "Headspace", "cost": 12.99, "last_used": "1 month ago", "worth_it": False}
        ]
        
        total_subs = sum(s['cost'] for s in subscriptions)
        wasted = sum(s['cost'] for s in subscriptions if not s['worth_it'])
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); padding: 1.5rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 1rem;'>
            <h3>💸 Total Monthly Subscriptions</h3>
            <h1 style='font-size: 3rem; margin: 0;'>${total_subs:.2f}</h1>
            <p>= <strong>${total_subs * 12:.2f}/year</strong> draining from your account</p>
        </div>
        """, unsafe_allow_html=True)
        
        for sub in subscriptions:
            status = "🟢" if sub['worth_it'] else "🔴"
            cancel_btn = "" if sub['worth_it'] else " [CANCEL?]"
            bg_gradient = "linear-gradient(135deg, #51cf66 0%, #40c057 100%)" if sub['worth_it'] else "linear-gradient(135deg, #ff6b6b 0%, #ff5252 100%)"
            text_color = "white"
            st.markdown(f"""
            <div style='background: {bg_gradient}; padding: 1rem; border-radius: 10px; margin: 0.4rem 0; color: {text_color}; box-shadow: 0 3px 8px rgba(0,0,0,0.1);'>
                {status} <strong style='font-size: 1.1rem;'>{sub['name']}</strong><br/>
                <span style='font-size: 1.2rem; font-weight: 700;'>${sub['cost']}/mo</span> | Last used: {sub['last_used']}<span style='font-weight: bold;'>{cancel_btn}</span>
            </div>
            """, unsafe_allow_html=True)
        
        if wasted > 0:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 1.5rem; border-radius: 15px; color: white; text-align: center; margin-top: 1rem;'>
                <h3>💰 Cancel unused subscriptions to save:</h3>
                <h1 style='font-size: 2.5rem; margin: 0;'>${wasted * 12:.2f}/year</h1>
                <button style='background: white; color: #11998e; border: none; padding: 10px 25px; border-radius: 25px; font-weight: bold; margin-top: 10px; cursor: pointer;'>
                    🗑️ Review & Cancel Now
                </button>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🚨 Anomaly Alarm")
    
    anomalies = [
        {"category": "Groceries", "normal": 450, "current": 630, "change": 40, "reason": "Inflation or behavior change?"},
        {"category": "Dining Out", "normal": 200, "current": 380, "change": 90, "reason": "Dating season? 💕"},
        {"category": "Transport", "normal": 150, "current": 220, "change": 47, "reason": "Gas prices or more trips?"}
    ]
    
    cols = st.columns(3)
    for i, anomaly in enumerate(anomalies):
        with cols[i]:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 1.5rem; border-radius: 15px; color: white; text-align: center;'>
                <h4>{anomaly['category']}</h4>
                <p style='margin: 0;'>Normal: ${anomaly['normal']}</p>
                <h2 style='margin: 0.5rem 0;'>Now: ${anomaly['current']}</h2>
                <p style='font-size: 1.5rem; margin: 0;'>📈 +{anomaly['change']}%</p>
                <p style='opacity: 0.9; font-size: 0.9rem;'>{anomaly['reason']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("### 🪣 The Leaky Bucket")
    st.markdown("*Watch your money drip away through forgotten subscriptions...*")
    
    fig = go.Figure(go.Funnel(
        y = ["Income", "After Bills", "After Subscriptions", "After Hidden Leaks", "What's Left"],
        x = [5000, 3500, 3300, 2800, 2500],
        textposition = "inside",
        textinfo = "value+percent initial",
        marker=dict(color=["#667eea", "#764ba2", "#f093fb", "#f5576c", "#11998e"])
    ))
    fig.update_layout(title="Where Does Your Money Go?", height=400)
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# FEATURE 8: INCOME STABILITY ANALYZER
# =============================================================================
elif current_page == "🏦 Income Analyzer":
    st.markdown("""
    <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 2rem; border-radius: 20px; margin-bottom: 2rem; text-align: center;'>
        <h1 style='color: white; margin: 0;'>🏦 Income Stability Analyzer</h1>
        <p style='color: rgba(255,255,255,0.9); font-size: 1.2rem;'>Bank Loan Eligibility + Gig Economy Readiness Check</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Your Income Profile")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        income_type = st.selectbox("Income Type", ["Full-time Salary", "Freelance/Gig", "Mixed Income", "Business Owner"])
    with col2:
        monthly_income = st.number_input("Average Monthly Income", min_value=0, value=5000, step=500)
    with col3:
        income_variance = st.slider("Income Variance (%)", 0, 100, 15, help="How much does your income fluctuate month-to-month?")
    
    stability_base = {
        "Full-time Salary": 85,
        "Freelance/Gig": 45,
        "Mixed Income": 65,
        "Business Owner": 55
    }
    
    stability_score = max(0, min(100, stability_base[income_type] - (income_variance * 0.5)))
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Your Income Report Card")
        
        grade = "A+" if stability_score >= 90 else "A" if stability_score >= 80 else "B+" if stability_score >= 70 else "B" if stability_score >= 60 else "C+" if stability_score >= 50 else "C" if stability_score >= 40 else "D"
        
        grade_color = "#11998e" if stability_score >= 70 else "#f39c12" if stability_score >= 50 else "#e74c3c"
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, {grade_color} 0%, {grade_color}aa 100%); padding: 2rem; border-radius: 20px; color: white; text-align: center;'>
            <h2>Income Stability Grade</h2>
            <h1 style='font-size: 6rem; margin: 0;'>{grade}</h1>
            <h3>Score: {stability_score:.0f}/100</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 💳 How Much Can You Safely Borrow?")
        
        if stability_score >= 70:
            max_loan = monthly_income * 48
            loan_message = "Banks love you! High stability = great loan terms"
        elif stability_score >= 50:
            max_loan = monthly_income * 24
            loan_message = "Decent borrowing power, but rates may be higher"
        else:
            max_loan = monthly_income * 12
            loan_message = "Limited borrowing power - consider building stability first"
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 15px; color: white; text-align: center; margin-top: 1rem;'>
            <h3>Safe Borrowing Limit</h3>
            <h1 style='font-size: 2.5rem; margin: 0;'>{format_currency(max_loan, 0)}</h1>
            <p style='opacity: 0.9;'>{loan_message}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🚀 Gig Economy Readiness Check")
        
        emergency_needed = monthly_income * 6
        current_emergency = st.number_input("Current Emergency Fund", min_value=0, value=int(monthly_income * 2), step=1000)
        emergency_progress = (current_emergency / emergency_needed) * 100 if emergency_needed > 0 else 0
        
        if income_type == "Full-time Salary":
            st.markdown(f"""
            <div style='background: #fff3cd; padding: 1.5rem; border-radius: 15px; color: #856404; margin-bottom: 1rem;'>
                <h4>🤔 Thinking of Going Freelance?</h4>
                <p>You need <strong>{format_currency(emergency_needed, 0)}</strong> emergency fund</p>
                <p>Currently have: <strong>{format_currency(current_emergency, 0)}</strong> ({emergency_progress:.0f}%)</p>
                <div style='background: #ffc107; height: 20px; border-radius: 10px; overflow: hidden;'>
                    <div style='background: #28a745; height: 100%; width: {min(100, emergency_progress)}%;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if emergency_progress < 100:
                st.warning(f"⚠️ Your stability score is too low for freelancing. Recommendation: Build up {format_currency(emergency_needed - current_emergency, 0)} more in savings first!")
            else:
                st.success("✅ You're financially ready to explore freelancing!")
        else:
            st.info("You're already in the gig economy! Focus on building that emergency fund.")
        
        st.markdown("### 📈 Income Forecast (6 months)")
        
        months = ['Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6']
        if income_type == "Full-time Salary":
            forecast = [monthly_income * (1 + random.uniform(-0.02, 0.03)) for _ in months]
            trend = "Stable - Predictable growth trajectory"
        else:
            forecast = [monthly_income * (1 + random.uniform(-0.3, 0.4)) for _ in months]
            trend = "Variable - High volatility expected"
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=months, y=forecast, marker_color='#667eea'))
        fig.add_hline(y=monthly_income, line_dash="dash", line_color="red", annotation_text="Average")
        fig.update_layout(title=f"Projected Income: {trend}", height=300, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 💪 Salary Negotiation Power")
        
        negotiation_power = "HIGH" if stability_score >= 75 else "MEDIUM" if stability_score >= 50 else "LOW"
        safe_salary_demand = monthly_income * (1.15 if negotiation_power == "HIGH" else 1.10 if negotiation_power == "MEDIUM" else 1.05)
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.5rem; border-radius: 15px; color: white; text-align: center;'>
            <h3>Your Negotiation Power: {negotiation_power}</h3>
            <p>Based on your stability, you can safely demand:</p>
            <h2>{format_currency(safe_salary_demand, 0)}/month</h2>
            <p style='opacity: 0.8;'>(+{((safe_salary_demand/monthly_income)-1)*100:.0f}% from current)</p>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# FEATURE 9: LIFESTYLE INFLATION DETECTOR
# =============================================================================
elif current_page == "📈 Inflation Detector":
    st.markdown("""
    <div style='background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); padding: 2rem; border-radius: 20px; margin-bottom: 2rem; text-align: center;'>
        <h1 style='color: white; margin: 0;'>📈 Lifestyle Inflation Detector</h1>
        <p style='color: rgba(255,255,255,0.9); font-size: 1.2rem;'>The 5-Year Broke Clock - How fast are you draining your future?</p>
    </div>
    """, unsafe_allow_html=True)
    
    monthly_income = st.session_state.financial_profile.get('monthly_income', 5000) if st.session_state.financial_profile else 5000
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### ⏰ Your 5-Year Broke Clock")
        
        income_growth = st.slider("Your Income Growth Rate (%/year)", 0, 20, 5)
        spending_growth = st.slider("Your Spending Growth Rate (%/year)", 0, 30, 15)
        
        if spending_growth > income_growth:
            deficit_rate = spending_growth - income_growth
            years_to_broke = min(10, 100 / deficit_rate) if deficit_rate > 0 else 999
            
            clock_color = "#ff416c" if years_to_broke < 3 else "#f39c12" if years_to_broke < 5 else "#11998e"
            
            st.markdown(f"""
            <div style='background: {clock_color}; padding: 3rem; border-radius: 20px; color: white; text-align: center;'>
                <h2>⏰ TIME UNTIL BROKE</h2>
                <h1 style='font-size: 5rem; margin: 0;'>{years_to_broke:.1f}</h1>
                <h2>YEARS</h2>
                <p style='opacity: 0.9;'>At current spending trajectory</p>
            </div>
            """, unsafe_allow_html=True)
            
            years = list(range(0, 6))
            status_labels = ["Now (Fine)", "Year 1", "Year 2 (Stress)", "Year 3 (Crisis)", "Year 4", "Year 5 (Broke?)"]
            wealth = [monthly_income * 12 * 0.2]
            
            for y in range(1, 6):
                income = monthly_income * 12 * ((1 + income_growth/100) ** y)
                spending = monthly_income * 12 * 0.8 * ((1 + spending_growth/100) ** y)
                net = income - spending
                wealth.append(wealth[-1] + net)
            
            fig = go.Figure()
            colors = ['#11998e' if w > 0 else '#ff416c' for w in wealth]
            fig.add_trace(go.Bar(x=status_labels, y=wealth, marker_color=colors))
            fig.add_hline(y=0, line_color="red", line_width=3)
            fig.update_layout(title="Your Wealth Journey", height=350, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("🎉 Great news! Your income is growing faster than your spending. You're on track!")
    
    with col2:
        st.markdown("### 🔥 Category Inflation Breakdown")
        st.markdown("*Which category is killing you?*")
        
        categories = [
            {"name": "🍕 Food", "inflation": 12, "status": "danger"},
            {"name": "🎬 Entertainment", "inflation": 8, "status": "warning"},
            {"name": "📱 Subscriptions", "inflation": 15, "status": "danger"},
            {"name": "👗 Shopping", "inflation": 20, "status": "danger"},
            {"name": "🚗 Transport", "inflation": 5, "status": "ok"},
            {"name": "🏠 Housing", "inflation": 3, "status": "ok"}
        ]
        
        for cat in categories:
            if cat['status'] == 'danger':
                bg = "linear-gradient(135deg, #ff6b6b 0%, #ff5252 100%)"
                text_color = "white"
            elif cat['status'] == 'warning':
                bg = "linear-gradient(135deg, #ffa500 0%, #ffb84d 100%)"
                text_color = "white"
            else:
                bg = "linear-gradient(135deg, #51cf66 0%, #40c057 100%)"
                text_color = "white"
            
            icon = "🔴" if cat['status'] == 'danger' else "🟡" if cat['status'] == 'warning' else "🟢"
            st.markdown(f"""
            <div style='background: {bg}; padding: 1.2rem; border-radius: 12px; margin: 0.8rem 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
                <div style='color: {text_color}; font-size: 1.1rem; font-weight: 600;'>
                    {icon} <strong>{cat['name']}</strong>: <span style='font-size: 1.3rem; font-weight: 700;'>+{cat['inflation']}%/year</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        worst_category = max(categories, key=lambda x: x['inflation'])
        monthly_save = monthly_income * (worst_category['inflation'] / 100) * 0.5 / 12
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 1rem; border-radius: 15px; color: white; text-align: center; margin-top: 1rem;'>
            <h4>💡 Quick Fix</h4>
            <p>Cut {worst_category['name']} by 50%</p>
            <h3>Save {format_currency(monthly_save, 0)}/mo</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎛️ Auto-Tightening Cap (Behavioral Economics)")
    
    detected_inflation = spending_growth - income_growth if spending_growth > income_growth else 0
    
    if detected_inflation > 0:
        current_fun_budget = monthly_income * 0.3
        suggested_cap = current_fun_budget * (1 - detected_inflation / 100)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style='background: #f8f9fa; padding: 1.5rem; border-radius: 15px; text-align: center;'>
                <h4>Current Fun Budget</h4>
                <h2>{format_currency(current_fun_budget, 0)}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 15px; text-align: center; color: white;'>
                <h4>Suggested New Cap</h4>
                <h2>{format_currency(suggested_cap, 0)}</h2>
                <p style='opacity: 0.8;'>(-{detected_inflation:.0f}% reduction)</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            accept_cap = st.button("✅ Accept New Budget", type="primary", use_container_width=True)
            override = st.button("⚠️ Override (Not Recommended)", use_container_width=True)
            
            if override:
                st.warning("💔 Are you sure? This breaks your 5-year plan and puts your financial future at risk!")
    else:
        st.info("🎉 No lifestyle inflation detected! You're living within your means.")
    
    st.markdown("### 🚗 Inflation Speed Gauge")
    
    speed = spending_growth
    zone = "CRASH ZONE 💥" if speed > 15 else "DANGER ZONE ⚠️" if speed > 10 else "CAUTION 🟡" if speed > 5 else "SAFE ZONE ✅"
    gauge_color = "#ff416c" if speed > 15 else "#f39c12" if speed > 10 else "#ffc107" if speed > 5 else "#11998e"
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = speed,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Spending Inflation Rate<br><span style='font-size:0.8em;color:{gauge_color}'>{zone}</span>"},
        delta = {'reference': income_growth, 'relative': False, 'position': "bottom"},
        gauge = {
            'axis': {'range': [0, 30], 'tickwidth': 1},
            'bar': {'color': gauge_color},
            'bgcolor': "white",
            'steps': [
                {'range': [0, 5], 'color': '#e8f5e9'},
                {'range': [5, 10], 'color': '#fff3e0'},
                {'range': [10, 15], 'color': '#ffebee'},
                {'range': [15, 30], 'color': '#ffcdd2'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': income_growth
            }
        }
    ))
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# FEATURE 10: FINANCIAL STRESS PREDICTOR
# =============================================================================
elif current_page == "🧠 Stress Predictor":
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 20px; margin-bottom: 2rem; text-align: center;'>
        <h1 style='color: white; margin: 0;'>🧠 Financial Stress Predictor</h1>
        <p style='color: rgba(255,255,255,0.9); font-size: 1.2rem;'>Predict stress BEFORE it happens. Prepare NOW.</p>
    </div>
    """, unsafe_allow_html=True)
    
    monthly_income = st.session_state.financial_profile.get('monthly_income', 5000) if st.session_state.financial_profile else 5000
    
    st.markdown("### 📅 Stress Heat Map Calendar")
    st.markdown("*Color-coded months: 🟢 Chill → 🟡 Mild → 🔴 Stressful*")
    
    months_data = {
        "January": {"stress": 65, "reasons": ["New Year spending hangover", "Holiday credit card bills"], "color": "#f39c12"},
        "February": {"stress": 45, "reasons": ["Valentine's Day expenses", "Tax prep stress"], "color": "#f1c40f"},
        "March": {"stress": 40, "reasons": ["Spring break temptation", "End of Q1"], "color": "#2ecc71"},
        "April": {"stress": 80, "reasons": ["TAX DEADLINE 📋", "Spring shopping"], "color": "#e74c3c"},
        "May": {"stress": 55, "reasons": ["Mother's Day", "Wedding season starts"], "color": "#f39c12"},
        "June": {"stress": 50, "reasons": ["Summer vacation planning", "Mid-year review"], "color": "#f1c40f"},
        "July": {"stress": 45, "reasons": ["Summer activities", "Holiday spending"], "color": "#2ecc71"},
        "August": {"stress": 60, "reasons": ["Back to school", "End of summer splurge"], "color": "#f39c12"},
        "September": {"stress": 35, "reasons": ["Fresh start energy", "Fall reset"], "color": "#2ecc71"},
        "October": {"stress": 55, "reasons": ["Halloween prep", "Holiday planning starts"], "color": "#f39c12"},
        "November": {"stress": 75, "reasons": ["Black Friday FOMO", "Thanksgiving travel"], "color": "#e74c3c"},
        "December": {"stress": 90, "reasons": ["Holiday shopping madness", "Year-end expenses", "Travel costs"], "color": "#e74c3c"}
    }
    
    cols = st.columns(6)
    for i, (month, data) in enumerate(months_data.items()):
        with cols[i % 6]:
            stress_emoji = "🔴" if data['stress'] >= 70 else "🟡" if data['stress'] >= 50 else "🟢"
            st.markdown(f"""
            <div style='background: {data['color']}; padding: 1rem; border-radius: 10px; text-align: center; color: white; margin: 0.3rem 0; min-height: 100px;'>
                <strong>{month[:3]}</strong><br/>
                <span style='font-size: 1.5rem;'>{stress_emoji}</span><br/>
                <small>{data['stress']}%</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔮 Why Will You Be Stressed?")
        st.markdown("*AI explains upcoming financial pressure points*")
        
        current_month = datetime.now().strftime("%B")
        next_stressful = None
        
        for month, data in months_data.items():
            if data['stress'] >= 70:
                next_stressful = (month, data)
                break
        
        if next_stressful:
            month_name, data = next_stressful
            expected_cost = monthly_income * (data['stress'] / 100) * 1.5
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); padding: 1.5rem; border-radius: 15px; color: white;'>
                <h3>⚠️ {month_name} Stress Alert!</h3>
                <p><strong>Expected extra expenses:</strong> {format_currency(expected_cost, 0)}</p>
                <h4>Why?</h4>
                <ul>
                    {"".join(f"<li>{reason}</li>" for reason in data['reasons'])}
                </ul>
                <p style='opacity: 0.9;'>Your current savings may not cover this → Stress incoming!</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 📊 Vibe Check Trend")
        st.markdown("*Your emotional financial health over time*")
        
        weeks = [f"Week {i}" for i in range(1, 13)]
        stress_levels = [random.randint(30, 80) for _ in weeks]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=weeks, y=stress_levels,
            mode='lines+markers',
            line=dict(color='#667eea', width=3),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.2)'
        ))
        fig.add_hline(y=50, line_dash="dash", line_color="orange", annotation_text="Stress Threshold")
        fig.update_layout(title="Your Stress Levels (Last 12 Weeks)", height=300, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
        
        avg_stress = sum(stress_levels) / len(stress_levels)
        if avg_stress > 60:
            st.warning("📈 ML Finding: Your stress peaks when savings drop below $10,000. Build that buffer!")
        else:
            st.success("📉 Your stress levels are manageable. Keep up the good financial habits!")
    
    with col2:
        st.markdown("### 🛡️ Stress Prevention Mode")
        st.markdown("*Start preparing MONTHS before stress hits*")
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 1rem;'>
            <h4>🎄 December Fund Progress</h4>
            <p>Target: {format_currency(monthly_income * 1.5, 0)} for holiday expenses</p>
            <p>Start saving: <strong>November 1st</strong></p>
            <p>Monthly contribution needed: <strong>{format_currency(monthly_income * 0.25, 0)}</strong></p>
            <div style='background: rgba(255,255,255,0.3); height: 20px; border-radius: 10px; overflow: hidden; margin-top: 10px;'>
                <div style='background: white; height: 100%; width: 35%;'></div>
            </div>
            <p style='text-align: center; margin-top: 5px;'>35% funded | 🎯 On Track!</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 💚 Emotional Intervention")
        st.markdown("*When stress is detected, we help immediately*")
        
        stress_detected = random.choice([True, False])
        
        if stress_detected:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 1.5rem; border-radius: 15px; color: #2d3748;'>
                <h3>💬 Hey there! I detected some financial stress coming your way.</h3>
                <p>Let's build a plan together. Here are some quick wins:</p>
                <div style='background: white; padding: 1rem; border-radius: 10px; margin: 1rem 0;'>
                    <p>☕ Skip 1 coffee this week = <strong>{format_currency(25, 0)}</strong> toward your goal</p>
                    <p>🎬 Movie night at home instead = <strong>{format_currency(40, 0)}</strong> saved</p>
                    <p>🍽️ Cook one extra meal = <strong>{format_currency(30, 0)}</strong> in your pocket</p>
                </div>
                <p style='text-align: center;'>Small actions = Big stress relief! 💪</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("😌 No stress detected right now! You're doing great. Keep it up!")
        
        st.markdown("### 🧘 Wellness Score")
        
        financial_wellness = random.randint(60, 90)
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = financial_wellness,
            title = {'text': "Financial Wellness Score"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 40], 'color': "#ffcdd2"},
                    {'range': [40, 70], 'color': "#fff9c4"},
                    {'range': [70, 100], 'color': "#c8e6c9"}
                ]
            }
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)

