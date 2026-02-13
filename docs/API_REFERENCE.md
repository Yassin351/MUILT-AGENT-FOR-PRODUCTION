# 📚 API Reference

## Core Functions

### Procurement Workflow

#### `run_procurement(product_query: str, category: str) -> dict`

Main entry point for the procurement analysis workflow.

**Module:** `agents.supervisor`

**Parameters:**
- `product_query` (str): Product name or description to search for
- `category` (str): Product category. Options: `electronics`, `fashion`, `home`, `beauty`, `groceries`, `seeds`, `general`

**Returns:**
```python
{
    'final_recommendation': {
        'product_name': str,
        'best_option': {
            'price_kes': float,
            'platform': str,
            'seller': str,
            'rating': float,
            'url': str
        },
        'alternatives': [
            {
                'price_kes': float,
                'platform': str,
                'seller': str
            }
        ],
        'price_forecast': {
            'trend': str,  # 'rising', 'falling', 'stable'
            'recommendation': str,
            'savings_potential': float,
            'optimal_buy_date': str
        },
        'compliance_summary': {
            'seller_verified': bool,
            'risk_level': str,  # 'low', 'medium', 'high'
            'counterfeit_risk': str,
            'warnings': list
        },
        'confidence_score': float,  # 0.0 to 1.0
        'human_approval_required': bool,
        'approval_reason': str
    }
}
```

**Example:**
```python
from agents.supervisor import run_procurement

result = run_procurement(
    product_query="Samsung Galaxy A54 128GB",
    category="electronics"
)

print(f"Best price: KES {result['final_recommendation']['best_option']['price_kes']}")
print(f"Confidence: {result['final_recommendation']['confidence_score']:.0%}")
```

**Raises:**
- `ValueError`: Invalid category or empty product query
- `ConnectionError`: Network issues or API unavailable
- `TimeoutError`: Request exceeded timeout limit

---

## Tax Calculation

#### `calculate_tax(price: float, category: str) -> dict`

Calculate KRA taxes and import duties for a product.

**Module:** `tools.tax_tool`

**Parameters:**
- `price` (float): Product price in KES
- `category` (str): Product category for duty calculation

**Returns:**
```python
{
    'base_price': float,
    'vat': float,  # 16% VAT
    'import_duty': float,  # Category-specific
    'excise_duty': float,  # If applicable
    'total_tax': float,
    'final_price': float,
    'breakdown': {
        'vat_rate': float,
        'duty_rate': float,
        'excise_rate': float
    }
}
```

**Example:**
```python
from tools.tax_tool import calculate_tax

result = calculate_tax(100000, 'electronics')
print(f"Total tax: KES {result['total_tax']:,.2f}")
print(f"Final price: KES {result['final_price']:,.2f}")
```

---

## Safety & Security

### SafetyGuardrails

#### `SafetyGuardrails.sanitize_input(text: str) -> str`

Remove potentially dangerous content from user input.

**Module:** `core.safety`

**Parameters:**
- `text` (str): User input to sanitize

**Returns:**
- `str`: Sanitized text with dangerous patterns removed

**Example:**
```python
from core.safety import SafetyGuardrails

user_input = "<script>alert('xss')</script>Samsung Galaxy"
safe_input = SafetyGuardrails.sanitize_input(user_input)
# Returns: "[REDACTED]Samsung Galaxy"
```

#### `SafetyGuardrails.validate_price(price: float, max_price: float = 10000000) -> bool`

Validate that a price is within reasonable bounds.

**Parameters:**
- `price` (float): Price to validate
- `max_price` (float, optional): Maximum allowed price. Default: 10,000,000

**Returns:**
- `bool`: True if valid, False otherwise

**Example:**
```python
from core.safety import SafetyGuardrails

is_valid = SafetyGuardrails.validate_price(50000)  # True
is_valid = SafetyGuardrails.validate_price(-100)   # False
is_valid = SafetyGuardrails.validate_price(20000000)  # False
```

#### `SafetyGuardrails.redact_sensitive_data(text: str) -> str`

Redact sensitive information from text.

**Parameters:**
- `text` (str): Text containing potential sensitive data

**Returns:**
- `str`: Text with sensitive data redacted

**Example:**
```python
from core.safety import SafetyGuardrails

text = "Contact john@example.com or call 555-123-4567"
redacted = SafetyGuardrails.redact_sensitive_data(text)
# Returns: "Contact [EMAIL_REDACTED] or call [PHONE_NUMBER_REDACTED]"
```

### OutputFilter

#### `OutputFilter.filter_recommendation(recommendation: dict) -> dict`

Filter and validate agent outputs for safety.

**Module:** `core.safety`

**Parameters:**
- `recommendation` (dict): Raw recommendation from agents

**Returns:**
- `dict`: Filtered recommendation with only safe fields

**Example:**
```python
from core.safety import OutputFilter

raw_rec = {
    'product_name': 'Test Product',
    'best_option': {'price': 1000},
    'internal_debug': 'should be removed',
    'confidence_score': 0.45
}

safe_rec = OutputFilter.filter_recommendation(raw_rec)
# 'internal_debug' removed, 'human_approval_required' added
```

---

## Resilience

### Retry Decorator

#### `@with_retry(max_attempts: int = 3, backoff_seconds: int = 2)`

Decorator to add retry logic with exponential backoff.

**Module:** `core.resilience`

**Parameters:**
- `max_attempts` (int): Maximum retry attempts
- `backoff_seconds` (int): Initial backoff time in seconds

**Example:**
```python
from core.resilience import with_retry

@with_retry(max_attempts=5, backoff_seconds=2)
def fetch_data():
    # Your code that might fail
    return api_call()
```

### Timeout Decorator

#### `@with_timeout(seconds: int = 30)`

Decorator to enforce timeout on function execution.

**Module:** `core.resilience`

**Parameters:**
- `seconds` (int): Timeout in seconds

**Example:**
```python
from core.resilience import with_timeout

@with_timeout(seconds=60)
def long_running_task():
    # Your code
    pass
```

### Circuit Breaker

#### `CircuitBreaker(failure_threshold: int = 5, timeout: int = 60)`

Circuit breaker to prevent cascading failures.

**Module:** `core.resilience`

**Parameters:**
- `failure_threshold` (int): Number of failures before opening circuit
- `timeout` (int): Seconds before attempting to close circuit

**Methods:**
- `call(func, *args, **kwargs)`: Execute function through circuit breaker

**Example:**
```python
from core.resilience import CircuitBreaker

cb = CircuitBreaker(failure_threshold=3, timeout=60)

def risky_operation():
    # Your code
    return result

try:
    result = cb.call(risky_operation)
except Exception as e:
    print(f"Circuit breaker: {e}")
```

### Loop Guard

#### `LoopGuard(max_iterations: int = 10)`

Prevent infinite loops in agent workflows.

**Module:** `core.resilience`

**Parameters:**
- `max_iterations` (int): Maximum allowed iterations

**Methods:**
- `check() -> bool`: Returns True if loop should continue
- `reset()`: Reset iteration counter

**Example:**
```python
from core.resilience import LoopGuard

guard = LoopGuard(max_iterations=5)

while guard.check():
    # Your loop code
    process_item()
```

### Health Monitor

#### `health_monitor.check_health() -> dict`

Check health status of all system components.

**Module:** `core.resilience`

**Returns:**
```python
{
    'component_name': {
        'status': str,  # 'healthy', 'unhealthy', 'error'
        'timestamp': float,
        'error': str  # If status is 'error'
    }
}
```

**Example:**
```python
from core.resilience import health_monitor

status = health_monitor.check_health()
for component, info in status.items():
    print(f"{component}: {info['status']}")
```

---

## Logging

### AgentLogger

#### `get_logger(agent_name: str = "system") -> AgentLogger`

Get a context-aware logger for an agent.

**Module:** `core.logging`

**Parameters:**
- `agent_name` (str): Name of the agent or component

**Returns:**
- `AgentLogger`: Logger instance

**Methods:**
- `debug(message: str, **kwargs)`
- `info(message: str, **kwargs)`
- `warning(message: str, **kwargs)`
- `error(message: str, **kwargs)`
- `critical(message: str, **kwargs)`
- `bind(**kwargs)`: Add context to subsequent logs

**Example:**
```python
from core.logging import get_logger

logger = get_logger("market_agent")
logger.bind(product="Samsung Galaxy", platform="Jumia")
logger.info("Starting market analysis")
logger.error("Failed to fetch data", error="Connection timeout")
```

---

## Market Intelligence Tools

### Jumia API

#### `search_jumia(query: str, category: str = None) -> list`

Search for products on Jumia Kenya.

**Module:** `tools.jumia_api`

**Parameters:**
- `query` (str): Product search query
- `category` (str, optional): Product category filter

**Returns:**
```python
[
    {
        'name': str,
        'price': float,
        'seller': str,
        'rating': float,
        'url': str,
        'image_url': str,
        'in_stock': bool
    }
]
```

### Google Shopping

#### `search_google_shopping(query: str) -> list`

Search Google Shopping for products.

**Module:** `tools.google_shopping`

**Parameters:**
- `query` (str): Product search query

**Returns:**
- `list`: List of product dictionaries

### OCR Tool

#### `extract_text_from_image(image_path: str) -> str`

Extract text from image using Tesseract OCR.

**Module:** `tools.ocr_tool`

**Parameters:**
- `image_path` (str): Path to image file

**Returns:**
- `str`: Extracted text

**Example:**
```python
from tools.ocr_tool import extract_text_from_image

text = extract_text_from_image("catalog.png")
print(text)
```

---

## Data Models

### ProcurementRequest

```python
from pydantic import BaseModel

class ProcurementRequest(BaseModel):
    product_query: str
    category: str
    max_price: float = None
    preferred_platforms: list = []
```

### ProductData

```python
class ProductData(BaseModel):
    name: str
    price_kes: float
    platform: str
    seller: str
    rating: float = None
    url: str = None
```

### Recommendation

```python
class Recommendation(BaseModel):
    product_name: str
    best_option: ProductData
    alternatives: list[ProductData]
    confidence_score: float
    human_approval_required: bool
```

---

## Error Handling

### Custom Exceptions

```python
class ProcurementError(Exception):
    """Base exception for procurement system."""
    pass

class ValidationError(ProcurementError):
    """Input validation failed."""
    pass

class APIError(ProcurementError):
    """External API call failed."""
    pass

class TimeoutError(ProcurementError):
    """Operation exceeded timeout."""
    pass
```

**Example:**
```python
from agents.supervisor import run_procurement

try:
    result = run_procurement("laptop", "electronics")
except ValidationError as e:
    print(f"Invalid input: {e}")
except APIError as e:
    print(f"API error: {e}")
except TimeoutError as e:
    print(f"Timeout: {e}")
```

---

## Configuration

### Environment Variables

Access configuration through environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "30"))
```

---

## Testing Utilities

### Mock Fixtures

```python
import pytest

@pytest.fixture
def mock_gemini_client():
    from unittest.mock import MagicMock
    mock = MagicMock()
    mock.generate_content.return_value.text = "Test response"
    return mock

@pytest.fixture
def sample_product_data():
    return {
        'name': 'Test Product',
        'price': 50000,
        'seller': 'Test Seller'
    }
```

---

## Rate Limits

### API Rate Limits

- **Gemini API (Free)**: 60 requests/minute
- **Gemini API (Paid)**: 1000 requests/minute
- **Jumia API**: No official limit (respect robots.txt)
- **Google Shopping**: Depends on Custom Search API tier

### Handling Rate Limits

```python
from core.resilience import with_retry

@with_retry(max_attempts=5, backoff_seconds=10)
def api_call_with_retry():
    # Your API call
    pass
```

---

## Best Practices

1. **Always sanitize user input:**
   ```python
   from core.safety import SafetyGuardrails
   safe_input = SafetyGuardrails.sanitize_input(user_input)
   ```

2. **Use retry logic for external calls:**
   ```python
   from core.resilience import with_retry
   
   @with_retry(max_attempts=3)
   def fetch_data():
       pass
   ```

3. **Log important events:**
   ```python
   from core.logging import get_logger
   logger = get_logger("my_component")
   logger.info("Operation completed")
   ```

4. **Validate outputs:**
   ```python
   from core.safety import OutputFilter
   safe_output = OutputFilter.filter_recommendation(raw_output)
   ```

5. **Handle errors gracefully:**
   ```python
   try:
       result = run_procurement(query, category)
   except Exception as e:
       logger.error(f"Failed: {e}")
       # Fallback logic
   ```

---

**Version:** 1.0.0  
**Last Updated:** 2024
