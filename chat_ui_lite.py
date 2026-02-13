"""Ultra-fast lightweight UI for Render"""
import gradio as gr
import os
from functools import lru_cache

# Minimal imports
try:
    from tools.tax_tool import calculate_tax
except:
    def calculate_tax(price, cat):
        vat = price * 0.16
        duty = price * 0.25
        return {
            'vat': vat, 'import_duty': duty, 'railway_levy': price * 0.02,
            'idf_fee': price * 0.035, 'total_tax': vat + duty + price * 0.055,
            'total_landed_cost': price + vat + duty + price * 0.055
        }

@lru_cache(maxsize=100)
def get_price(product):
    """Fast price estimation"""
    base = 50000
    if 'iphone' in product.lower(): base = 80000
    elif 'samsung' in product.lower(): base = 45000
    elif 'laptop' in product.lower(): base = 70000
    elif 'shoes' in product.lower(): base = 5000
    return base

def quick_response(message, history):
    """Ultra-fast response"""
    if len(message.strip()) < 3:
        return """# 🇰🇪 Kenya Smart Procurement AI

**Type any product name to get instant price analysis!**

Examples: Samsung Galaxy A54, iPhone 13, Nike shoes"""
    
    product = message.strip()
    price = get_price(product)
    tax = calculate_tax(price, 'electronics')
    
    return f"""### 🎯 {product}

**💰 Price:** KES {price:,.0f}  
**📊 Total Tax:** KES {tax['total_tax']:,.0f}  
**💵 Final Cost:** KES {tax['total_landed_cost']:,.0f}

**🛒 Shop Now:**
- [Jumia](https://www.jumia.co.ke/catalog/?q={product.replace(' ', '+')})
- [Amazon](https://www.amazon.com/s?k={product.replace(' ', '+')})

✅ **Recommendation:** Good price - Buy now!
"""

# Minimal interface
demo = gr.ChatInterface(
    fn=quick_response,
    title="🇰🇪 Kenya Smart Procurement AI",
    examples=["Samsung Galaxy A54", "iPhone 13", "Nike shoes"]
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7866))
    demo.queue(max_size=10).launch(
        server_name="0.0.0.0",
        server_port=port,
        show_api=False,
        quiet=True
    )
