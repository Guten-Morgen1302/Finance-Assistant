# MoneyMind: Smart Finance Companion

## Overview
MoneyMind is a Streamlit-based personal finance application designed for Gen Z. It combines financial planning tools with a modern, emoji-rich interface that makes money management feel less intimidating. Built for hackathons with judge-impressing features.

## Project Structure
```
.
├── streamlit_app.py     # Main Streamlit application (3800+ lines)
├── requirements.txt     # Python dependencies
├── data/
│   └── gdp_data.csv     # Sample data
├── finsphere.db         # SQLite database for user data
└── *.png                # Dashboard screenshots
```

## Technology Stack
- **Framework**: Streamlit
- **Language**: Python 3.11
- **Database**: SQLite (finsphere.db)
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Data Processing**: Pandas, NumPy
- **AI**: OpenAI, LangChain (optional integration)

## Running the Application
The app runs on port 5000 with:
```bash
streamlit run streamlit_app.py --server.port=5000 --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false
```

## Navigation Structure
Sidebar navigation with 8 main sections:
1. Dashboard - Main overview
2. Vibe Check - Mood-based financial tracking
3. Budget Planner - 50/30/20 budgeting
4. What-If Simulator - Life event impact analysis
5. Expense Forecasting - Hidden spending patterns
6. Income Analyzer - Loan eligibility & stability
7. Inflation Detector - Lifestyle creep detection
8. Stress Predictor - Financial stress forecasting

## Key Features

### Tier 1 Features
- Financial profile setup with customizable currency (USD, PKR, EUR)
- Spending tracking with emotional/vibe categorization
- Budget planning using 50/30/20 rule
- Investment suggestions based on risk tolerance
- AI-powered financial coaching (optional chatbot integration)
- Autonomous "Slay Planner" for goal setting
- Dynamic Aura System - Colors change based on mood

### Tier 2 Features (Hackathon Winners)
1. **What-If Financial Simulator** - Instagram-style life event selection, ripple effects, success rate dashboard, breaking point alerts
2. **Expense Archaeology** - Hidden pattern detector, Subscription Graveyard, anomaly alarms, leaky bucket visualization
3. **Income Stability Analyzer** - Bank Loan Eligibility Score, Gig Economy Readiness, Income Forecast, Salary Negotiation Power
4. **Lifestyle Inflation Detector** - 5-Year Broke Clock, Category Breakdown, Auto-Tightening Cap with behavioral economics
5. **Financial Stress Predictor** - Stress Heat Map Calendar, Prevention Mode, Emotional Intervention, Wellness Score

## Recent Changes
- December 17, 2025: Added Tier 2 features with sidebar navigation
- December 17, 2025: Implemented What-If Simulator, Expense Forecasting, Income Analyzer, Inflation Detector, Stress Predictor
- December 17, 2025: Initial import and Replit environment setup

## User Preferences
- Gen Z aesthetic with gradients and emojis
- No long scrolling - prefer sidebar navigation
- Judge-impressing features for hackathons
