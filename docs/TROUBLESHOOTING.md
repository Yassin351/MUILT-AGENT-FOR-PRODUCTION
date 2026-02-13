# 🔧 Troubleshooting Guide & FAQ

## Quick Diagnostics

### System Health Check
```bash
# Check Python version
python --version  # Should be 3.9+

# Check Tesseract installation
tesseract --version

# Check environment variables
python -c "import os; print('API Key:', 'SET' if os.getenv('GOOGLE_API_KEY') else 'NOT SET')"

# Run health check
python -c "from core.resilience import health_monitor; print(health_monitor.check_health())"
```

---

## Common Issues & Solutions

### 1. "GOOGLE_API_KEY not found"

**Symptoms:**
- Error on startup
- API calls failing
- "API key not configured" message

**Solutions:**

```bash
# Verify .env file exists
dir .env  # Windows
ls -la .env  # Linux/macOS

# Check API key is set
type .env | findstr GOOGLE_API_KEY  # Windows
grep GOOGLE_API_KEY .env  # Linux/macOS

# If missing, add to .env:
echo GOOGLE_API_KEY=your_key_here >> .env
```

**Get API Key:**
1. Visit https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy key to `.env` file

---

### 2. "Tesseract not found" or OCR Errors

**Symptoms:**
- OCR tool fails
- "tesseract is not recognized" error
- Image processing errors

**Solutions:**

**Windows:**
```bash
# Download installer
# https://github.com/UB-Mannheim/tesseract/wiki

# Add to PATH
setx PATH "%PATH%;C:\Program Files\Tesseract-OCR"

# Verify
tesseract --version
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
tesseract --version
```

**macOS:**
```bash
brew install tesseract
tesseract --version
```

---

### 3. "Module not found" Errors

**Symptoms:**
- ImportError or ModuleNotFoundError
- Missing dependencies

**Solutions:**

```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall

# If specific module missing
pip install <module-name>

# Clear pip cache if issues persist
pip cache purge
pip install -r requirements.txt
```

---

### 4. Connection Timeout / Network Errors

**Symptoms:**
- "Connection timeout" errors
- API calls hanging
- Slow response times

**Solutions:**

```bash
# Increase timeout in .env
TIMEOUT_SECONDS=60

# Check internet connection
ping google.com

# Check firewall settings
# Allow Python through firewall

# Use proxy if needed (add to .env)
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=http://proxy.example.com:8080
```

---

### 5. Low Confidence Scores

**Symptoms:**
- Confidence scores consistently < 60%
- "Human approval required" warnings
- Poor recommendations

**Causes & Solutions:**

**Vague Product Queries:**
```python
# ❌ Bad
"phone"
"laptop"

# ✅ Good
"Samsung Galaxy A54 128GB Black"
"Dell XPS 13 9310 i7 16GB"
```

**Limited Market Data:**
- Try alternative search terms
- Check if product is available in Kenya
- Use more common product names

**New/Uncommon Products:**
- System has less historical data
- Confidence naturally lower
- Human review recommended

---

### 6. Streamlit/Gradio Won't Start

**Symptoms:**
- Port already in use
- Application won't load
- Blank screen

**Solutions:**

```bash
# Check if port is in use
netstat -ano | findstr :8501  # Windows
lsof -i :8501  # Linux/macOS

# Kill process using port
taskkill /PID <PID> /F  # Windows
kill -9 <PID>  # Linux/macOS

# Use different port
streamlit run ui/app.py --server.port=8502

# Clear Streamlit cache
streamlit cache clear
```

---

### 7. High Memory Usage

**Symptoms:**
- System slowing down
- Out of memory errors
- Application crashes

**Solutions:**

```bash
# Monitor memory usage
# Windows: Task Manager
# Linux: htop or top

# Reduce concurrent requests
# Add to .env:
MAX_CONCURRENT_REQUESTS=5

# Increase system RAM
# Or deploy to cloud with more resources

# Clear logs periodically
cd logs
del *.log  # Windows
rm *.log  # Linux/macOS
```

---

### 8. Tests Failing

**Symptoms:**
- Pytest errors
- Coverage below 70%
- Import errors in tests

**Solutions:**

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_comprehensive.py -v

# Skip slow tests
pytest -m "not slow"

# Update test fixtures if needed
# Check tests/conftest.py
```

---

### 9. Logging Issues

**Symptoms:**
- No logs being written
- Permission denied errors
- Logs directory missing

**Solutions:**

```bash
# Create logs directory
mkdir logs

# Check permissions
# Windows: Right-click > Properties > Security
# Linux: chmod 755 logs

# Verify logging configuration
python -c "from core.logging import logger; logger.info('Test log')"

# Check log files
dir logs  # Windows
ls -lh logs  # Linux/macOS
```

---

### 10. API Rate Limits

**Symptoms:**
- "Rate limit exceeded" errors
- 429 HTTP errors
- Requests being throttled

**Solutions:**

```bash
# Increase retry delays in .env
MAX_RETRIES=5
RETRY_DELAY=5

# Implement caching
# Market data cached for 1 hour by default

# Upgrade API plan
# Gemini free tier: 60 requests/minute
# Paid tier: Higher limits

# Monitor API usage
# Check Google Cloud Console
```

---

## Debugging Tips

### Enable Debug Logging

```bash
# Set in .env
LOG_LEVEL=DEBUG

# Or temporarily
export LOG_LEVEL=DEBUG  # Linux/macOS
set LOG_LEVEL=DEBUG  # Windows

# Run application
streamlit run ui/app.py
```

### Check Logs

```bash
# View latest log
tail -f logs/procurement_*.log  # Linux/macOS
type logs\procurement_*.log  # Windows

# Search for errors
grep "ERROR" logs/*.log  # Linux/macOS
findstr "ERROR" logs\*.log  # Windows

# Analyze JSON logs
cat logs/events.json | jq '.[] | select(.level=="ERROR")'
```

### Test Individual Components

```python
# Test market agent
from agents.market_agent import MarketIntelligenceAgent
agent = MarketIntelligenceAgent()
print(agent)

# Test tax calculation
from tools.tax_tool import calculate_tax
result = calculate_tax(100000, 'electronics')
print(result)

# Test safety
from core.safety import SafetyGuardrails
result = SafetyGuardrails.sanitize_input("test input")
print(result)
```

---

## FAQ

### Q: How accurate are the price forecasts?

**A:** Accuracy depends on historical data availability. Typically:
- Common products: 70-85% accuracy
- New products: 50-60% accuracy
- Seasonal products: 60-75% accuracy

### Q: Can I add custom platforms?

**A:** Yes! Create a new scraper in `tools/` directory:

```python
# tools/custom_scraper.py
def scrape_custom_platform(query: str):
    # Your scraping logic
    return results
```

Then register in market agent.

### Q: What's the API rate limit?

**A:** 
- Gemini Free: 60 requests/minute
- Gemini Pro: 1000 requests/minute
- Upgrade at: https://cloud.google.com/

### Q: How do I deploy to production?

**A:** See [Deployment Guide](DEPLOYMENT.md) for:
- Local/On-premise deployment
- Docker deployment
- Cloud deployment (AWS, Render, etc.)

### Q: Is this suitable for enterprise use?

**A:** Yes, with proper infrastructure:
- Load balancing for multiple instances
- Redis for caching
- Database for persistence
- Monitoring and alerting

### Q: How do I backup data?

**A:**
```bash
# Backup configuration and logs
tar -czf backup.tar.gz .env logs/ data/

# Automated backup script in docs/DEPLOYMENT.md
```

### Q: Can I use a different LLM?

**A:** Yes, modify `core/gemini_client.py` to use:
- OpenAI GPT
- Anthropic Claude
- Local models (Ollama)

### Q: How do I contribute?

**A:**
1. Fork repository
2. Create feature branch
3. Add tests (maintain 70%+ coverage)
4. Submit pull request

### Q: What if I find a bug?

**A:**
1. Check existing GitHub issues
2. Create new issue with:
   - Steps to reproduce
   - Expected vs actual behavior
   - Logs and error messages
   - System information

### Q: How do I update dependencies?

**A:**
```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade <package-name>

# Check for outdated packages
pip list --outdated
```

---

## Performance Optimization

### Slow Response Times

**Check:**
1. Internet connection speed
2. API response times
3. System resources (CPU, RAM)

**Optimize:**
```bash
# Enable caching
CACHE_ENABLED=true
CACHE_TTL=3600

# Reduce concurrent scraping
MAX_CONCURRENT_SCRAPES=3

# Use faster LLM model
# In code: model="gemini-1.5-flash"
```

### High Resource Usage

**Monitor:**
```bash
# Windows
tasklist | findstr python

# Linux
ps aux | grep python
htop
```

**Optimize:**
```python
# Limit agent iterations
MAX_ITERATIONS=5

# Reduce batch sizes
BATCH_SIZE=10

# Clear caches periodically
```

---

## Getting Help

### Self-Help Resources
1. Read [Documentation](DOCUMENTATION.md)
2. Check this troubleshooting guide
3. Review logs: `logs/procurement_*.log`
4. Search GitHub issues

### Community Support
- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share ideas

### Professional Support
- Email: support@procurement.example.com
- Priority support available for enterprise users

---

## Emergency Procedures

### System Down

1. **Check logs:**
   ```bash
   tail -100 logs/procurement_*.log
   ```

2. **Restart service:**
   ```bash
   sudo systemctl restart procurement
   ```

3. **Verify health:**
   ```bash
   curl http://localhost:8501/_stcore/health
   ```

### Data Corruption

1. **Stop service**
2. **Restore from backup:**
   ```bash
   tar -xzf backup.tar.gz
   ```
3. **Restart service**

### Security Incident

1. **Rotate API keys immediately**
2. **Check logs for suspicious activity**
3. **Update `.env` with new keys**
4. **Restart application**

---

## Maintenance Checklist

### Daily
- [ ] Check error logs
- [ ] Monitor API usage
- [ ] Verify system health

### Weekly
- [ ] Review performance metrics
- [ ] Update dependencies (if needed)
- [ ] Backup configuration

### Monthly
- [ ] Rotate and archive logs
- [ ] Security audit
- [ ] Update documentation

---

**Last Updated:** 2024  
**Version:** 1.0.0
