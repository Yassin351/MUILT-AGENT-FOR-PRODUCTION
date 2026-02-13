# 🇰🇪 Kenya Smart Procurement AI System

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Usage Guide](#usage-guide)
6. [API Reference](#api-reference)
7. [Testing](#testing)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)
10. [Security](#security)

---

## 🎯 System Overview

### Purpose
The Kenya Smart Procurement AI System is a production-ready multi-agent system designed to help Kenyan businesses make informed procurement decisions through intelligent market analysis, price forecasting, and compliance verification.

### Key Features
- **Multi-Agent Architecture**: Specialized agents for market intelligence, price strategy, and compliance
- **Real-time Market Data**: Scrapes Jumia, Copia, and other platforms
- **Price Forecasting**: ML-based predictions for optimal buying times
- **Tax Calculation**: Automatic KRA VAT, import duty, and levy calculations
- **OCR Integration**: Extract prices from supplier catalogs
- **Safety Guardrails**: Input validation, output filtering, and security measures
- **Resilience**: Retry logic, circuit breakers, and timeout handling
- **Comprehensive Testing**: 70%+ code coverage with unit, integration, and E2E tests

### Technology Stack
- **Framework**: LangGraph for agent orchestration
- **LLM**: Google Gemini API
- **UI**: Streamlit & Gradio
- **Testing**: Pytest with coverage
- **Logging**: Structured logging with Loguru
- **OCR**: Tesseract
- **Forecasting**: Prophet

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│              (Streamlit, Gradio, REST API)                   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Supervisor Agent                          │
│              (LangGraph Orchestration)                       │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐  ┌────────▼────────┐  ┌────────▼────────┐
│    Market      │  │     Price       │  │   Compliance    │
│ Intelligence   │  │   Strategist    │  │    Auditor      │
│     Agent      │  │     Agent       │  │     Agent       │
└───────┬────────┘  └────────┬────────┘  └────────┬────────┘
        │                    │                     │
┌───────▼────────────────────▼─────────────────────▼────────┐
│                        Tools Layer                         │
│  Jumia API │ Google Shopping │ OCR │ Tax Calc │ Sentiment │
└────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Core Infrastructure                        │
│  Safety │ Resilience │ Logging │ Monitoring │ Health Checks │
└─────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

1. **Market Intelligence Agent**
   - Scrapes product data from multiple platforms
   - Extracts prices from catalogs using OCR
   - Performs sentiment analysis on reviews
   - Aggregates market data

2. **Price Strategist Agent**
   - Forecasts price trends using Prophet
   - Calculates KRA taxes and import duties
   - Recommends optimal buying times
   - Identifies savings opportunities

3. **Compliance Auditor Agent**
   - Verifies seller legitimacy
   - Detects counterfeit risks
   - Checks regulatory compliance
   - Assesses transaction risks

4. **Supervisor Agent**
   - Orchestrates agent workflows
   - Manages state transitions
   - Handles errors and retries
   - Produces final recommendations

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9 or higher
- Tesseract OCR
- Google Gemini API Key
- 4GB RAM minimum
- Internet connection

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd "MUILT AGENT FOR PRODUCTION"
```

### Step 2: Install Tesseract OCR

**Windows:**
```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Install and add to PATH
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### Step 3: Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment
```bash
# Copy sample environment file
copy .env.sample .env  # Windows
cp .env.sample .env    # Linux/macOS

# Edit .env and add your API keys
```

### Step 6: Verify Installation
```bash
python -c "import google.generativeai; print('✅ Setup complete!')"
```

---

## ⚙️ Configuration

### Environment Variables

#### Required
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

#### Optional
```env
# Jumia Integration
JUMIA_AFFILIATE_ID=your_affiliate_id
JUMIA_API_KEY=your_api_key

# Google Custom Search
GOOGLE_CSE_ID=your_search_engine_id

# System Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT_SECONDS=30

# KRA Tax Rates
KRA_VAT_RATE=0.16
KRA_IMPORT_DUTY_ELECTRONICS=0.25
KRA_IMPORT_DUTY_GENERAL=0.35
```

### Getting API Keys

**Google Gemini API:**
1. Visit https://makersuite.google.com/app/apikey
2. Create new API key
3. Copy to `.env` file

**Jumia Affiliate (Optional):**
1. Visit https://www.jumia.co.ke/sp-affiliate/
2. Register as affiliate
3. Get API credentials

---

## 📖 Usage Guide

### Running the Application

#### Streamlit UI (Recommended)
```bash
streamlit run ui/app.py
```
Access at: http://localhost:8501

#### Gradio UI (Alternative)
```bash
python ui/gradio_app.py
```
Access at: http://localhost:7860

#### Command Line
```python
from agents.supervisor import run_procurement

result = run_procurement(
    product_query="Samsung Galaxy A54",
    category="electronics"
)

print(result['final_recommendation'])
```

### Example Workflow

1. **Enter Product Query**
   - Be specific: "Samsung Galaxy A54 128GB" vs "phone"
   - Include brand names when possible

2. **Select Category**
   - electronics, fashion, home, beauty, groceries, seeds, general

3. **Review Results**
   - Best price and platform
   - Price forecast and trend
   - Compliance status
   - Confidence score

4. **Make Decision**
   - High confidence (>70%): Proceed with purchase
   - Low confidence (<70%): Requires human review

---

## 🔌 API Reference

### Core Functions

#### `run_procurement(product_query: str, category: str) -> dict`
Main entry point for procurement analysis.

**Parameters:**
- `product_query` (str): Product name or description
- `category` (str): Product category

**Returns:**
```python
{
    'final_recommendation': {
        'product_name': str,
        'best_option': {
            'price_kes': float,
            'platform': str,
            'seller': str,
            'rating': float
        },
        'price_forecast': {
            'trend': str,  # 'rising', 'falling', 'stable'
            'recommendation': str,
            'savings_potential': float
        },
        'compliance_summary': {
            'seller_verified': bool,
            'risk_level': str,
            'counterfeit_risk': str
        },
        'confidence_score': float,
        'human_approval_required': bool
    }
}
```

#### `calculate_tax(price: float, category: str) -> dict`
Calculate KRA taxes and duties.

**Parameters:**
- `price` (float): Product price in KES
- `category` (str): Product category

**Returns:**
```python
{
    'vat': float,
    'import_duty': float,
    'excise_duty': float,
    'total_tax': float,
    'final_price': float
}
```

### Safety Functions

#### `SafetyGuardrails.sanitize_input(text: str) -> str`
Remove dangerous content from user input.

#### `SafetyGuardrails.validate_price(price: float) -> bool`
Validate price is within reasonable bounds.

#### `OutputFilter.filter_recommendation(rec: dict) -> dict`
Filter and validate agent outputs.

---

## 🧪 Testing

### Running Tests

#### All Tests
```bash
pytest
```

#### With Coverage Report
```bash
pytest --cov=. --cov-report=html
```

#### Specific Test Categories
```bash
# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# End-to-end tests
pytest -m e2e
```

### Test Coverage Requirements
- Minimum: 70% overall coverage
- Core modules: 80%+ coverage
- Critical paths: 90%+ coverage

### Coverage Report
After running tests with coverage:
```bash
# Open HTML report
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## 📊 Monitoring & Maintenance

### Logging

**Log Locations:**
- Console: Real-time output
- File: `logs/procurement_YYYY-MM-DD.log`
- JSON: `logs/events.json` (structured)

**Log Levels:**
- DEBUG: Detailed diagnostic information
- INFO: General system events
- WARNING: Warning messages
- ERROR: Error events
- CRITICAL: Critical failures

**Viewing Logs:**
```bash
# Tail latest log
tail -f logs/procurement_*.log

# Search for errors
grep "ERROR" logs/procurement_*.log

# Analyze JSON logs
cat logs/events.json | jq '.[] | select(.level=="ERROR")'
```

### Health Checks

**Manual Health Check:**
```python
from core.resilience import health_monitor

status = health_monitor.check_health()
print(status)
```

**Expected Output:**
```json
{
    "gemini_api": {"status": "healthy", "timestamp": 1234567890},
    "database": {"status": "healthy", "timestamp": 1234567890}
}
```

### Maintenance Tasks

**Daily:**
- Monitor error logs
- Check disk space for logs
- Verify API quotas

**Weekly:**
- Review performance metrics
- Update dependencies
- Backup configuration

**Monthly:**
- Rotate and archive logs
- Review security alerts
- Update documentation

---

## 🔧 Troubleshooting

### Common Issues

#### Issue: "GOOGLE_API_KEY not found"
**Solution:**
```bash
# Verify .env file exists
dir .env  # Windows
ls .env   # Linux/macOS

# Check API key is set
type .env | findstr GOOGLE_API_KEY  # Windows
grep GOOGLE_API_KEY .env            # Linux/macOS
```

#### Issue: "Tesseract not found"
**Solution:**
```bash
# Verify Tesseract installation
tesseract --version

# Add to PATH if needed (Windows)
setx PATH "%PATH%;C:\Program Files\Tesseract-OCR"
```

#### Issue: "Module not found"
**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Issue: "Connection timeout"
**Solution:**
- Check internet connection
- Verify firewall settings
- Increase timeout in `.env`: `TIMEOUT_SECONDS=60`

#### Issue: "Low confidence scores"
**Causes:**
- Vague product queries
- Limited market data
- New/uncommon products

**Solutions:**
- Be more specific with product names
- Include brand and model numbers
- Try alternative search terms

### Debug Mode

Enable detailed logging:
```bash
# Set in .env
LOG_LEVEL=DEBUG

# Or temporarily
export LOG_LEVEL=DEBUG  # Linux/macOS
set LOG_LEVEL=DEBUG     # Windows
```

### Getting Help

1. Check logs: `logs/procurement_*.log`
2. Review error messages
3. Search documentation
4. Check GitHub issues
5. Contact support

---

## 🔒 Security

### Input Validation
- All user inputs are sanitized
- SQL injection prevention
- XSS attack prevention
- Length limits enforced

### Output Filtering
- Sensitive data redaction
- Safe field whitelisting
- Confidence thresholds

### API Security
- API keys stored in `.env` (not in code)
- Rate limiting on external APIs
- Timeout enforcement

### Data Privacy
- No personal data stored
- Logs redact sensitive information
- Compliance with data protection regulations

### Best Practices
1. Never commit `.env` file
2. Rotate API keys regularly
3. Use HTTPS in production
4. Monitor for suspicious activity
5. Keep dependencies updated

---

## 📝 FAQ

**Q: How accurate are the price forecasts?**
A: Accuracy depends on historical data availability. Typically 70-85% for common products.

**Q: Can I add custom platforms?**
A: Yes, create a new scraper in `tools/` following existing patterns.

**Q: What's the API rate limit?**
A: Gemini API: 60 requests/minute (free tier). Upgrade for higher limits.

**Q: How do I deploy to production?**
A: See `render.yaml` for cloud deployment configuration.

**Q: Is this system suitable for enterprise use?**
A: Yes, with proper scaling and monitoring infrastructure.

---

## 📄 License
See LICENSE file for details.

## 🤝 Contributing
Contributions welcome! Please read CONTRIBUTING.md first.

## 📧 Support
For issues and questions, please open a GitHub issue.

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Maintained by:** Kenya Smart Procurement Team
