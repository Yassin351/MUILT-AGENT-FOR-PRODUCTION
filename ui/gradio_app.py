"""
Professional Gradio UI for Kenya Smart Procurement System.
Features: Interactive interface, error handling, progress tracking, and export capabilities.
"""
import gradio as gr
import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.supervisor import run_procurement
from core.safety import SafetyGuardrails
from core.logging import get_logger

logger = get_logger("ui")

def analyze_product(product_query: str, category: str, progress=gr.Progress()):
    """Main analysis function with progress tracking."""
    
    # Validate input
    if not product_query or len(product_query.strip()) < 3:
        return {
            "error": "⚠️ Please enter a valid product name (at least 3 characters)",
            "status": "error"
        }
    
    # Sanitize input
    sanitized_query = SafetyGuardrails.sanitize_input(product_query)
    
    if "[REDACTED]" in sanitized_query:
        return {
            "error": "⚠️ Input contains potentially unsafe content. Please revise your query.",
            "status": "error"
        }
    
    try:
        progress(0.1, desc="🔍 Initializing agents...")
        logger.info(f"Starting analysis for: {sanitized_query}")
        
        progress(0.3, desc="🌐 Collecting market data...")
        
        progress(0.6, desc="📊 Analyzing prices and forecasts...")
        
        # Run procurement workflow
        result = run_procurement(sanitized_query, category)
        
        progress(0.9, desc="✅ Finalizing recommendations...")
        
        rec = result.get('final_recommendation', {})
        
        # Format output
        output = format_results(rec, sanitized_query)
        
        progress(1.0, desc="✅ Complete!")
        
        logger.info(f"Analysis completed for: {sanitized_query}")
        
        return output
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return {
            "error": f"❌ Analysis failed: {str(e)}\n\n💡 Troubleshooting:\n- Check GOOGLE_API_KEY in .env\n- Verify internet connection\n- Try a simpler product query",
            "status": "error"
        }


def format_results(rec: dict, query: str) -> dict:
    """Format recommendation results for display."""
    
    if not rec or rec.get('warning'):
        return {
            "summary": f"⚠️ {rec.get('warning', 'No results found')}",
            "best_option": "N/A",
            "forecast": "N/A",
            "compliance": "N/A",
            "confidence": "0%",
            "approval_needed": "Yes",
            "export_data": json.dumps(rec, indent=2)
        }
    
    best = rec.get('best_option', {})
    forecast = rec.get('price_forecast', {})
    compliance = rec.get('compliance_summary', {})
    
    # Summary
    summary = f"""
### 🎯 Analysis Complete for: {query}

**Best Price Found:** KES {best.get('price_kes', 0):,.2f}  
**Platform:** {best.get('platform', 'Unknown')}  
**Seller:** {best.get('seller', 'Unknown')}  
**Confidence Score:** {rec.get('confidence_score', 0):.0%}
"""
    
    # Best Option
    best_option = f"""
**Product:** {best.get('product_name', 'N/A')}  
**Price:** KES {best.get('price_kes', 0):,.2f}  
**Platform:** {best.get('platform', 'N/A')}  
**Seller:** {best.get('seller', 'N/A')}  
**Rating:** {best.get('rating', 'N/A')}
"""
    
    # Forecast
    trend = forecast.get('trend', 'stable').upper()
    trend_emoji = "📈" if trend == "RISING" else "📉" if trend == "FALLING" else "➡️"
    
    forecast_text = f"""
**Trend:** {trend_emoji} {trend}  
**Recommendation:** {forecast.get('recommendation', 'Buy now')}  
**Savings Potential:** KES {forecast.get('savings_potential', 0):,.2f}
"""
    
    # Compliance
    compliance_text = f"""
**Seller Verified:** {'✅' if compliance.get('seller_verified') else '❌'}  
**Risk Level:** {compliance.get('risk_level', 'Unknown')}  
**Counterfeit Risk:** {compliance.get('counterfeit_risk', 'Unknown')}
"""
    
    # Confidence and approval
    confidence = f"{rec.get('confidence_score', 0):.0%}"
    approval_needed = "⚠️ Yes - Low confidence" if rec.get('human_approval_required') else "✅ No - High confidence"
    
    return {
        "summary": summary,
        "best_option": best_option,
        "forecast": forecast_text,
        "compliance": compliance_text,
        "confidence": confidence,
        "approval_needed": approval_needed,
        "export_data": json.dumps(rec, indent=2),
        "status": "success"
    }


def export_results(export_data: str):
    """Export results to JSON file."""
    if not export_data or export_data == "":
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"procurement_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        f.write(export_data)
    
    return filename


# Build Gradio Interface
with gr.Blocks(title="Kenya Smart Procurement AI") as app:
    
    gr.Markdown("""
    # 🇰🇪 Kenya Smart Procurement AI
    ### Intelligent sourcing powered by multi-agent AI system
    
    This system helps Kenyan businesses make informed procurement decisions by:
    - 🔍 Comparing prices across multiple platforms (Jumia, Copia, etc.)
    - 📈 Forecasting optimal buying times
    - 🛡️ Verifying seller legitimacy
    - 💰 Calculating import taxes (KRA VAT, duties, levies)
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📝 Input")
            
            product_input = gr.Textbox(
                label="Product Name",
                placeholder="e.g., Samsung Galaxy A54, Maize seeds, Office chairs",
                lines=2
            )
            
            category_input = gr.Dropdown(
                label="Category",
                choices=["electronics", "fashion", "home", "beauty", "groceries", "seeds", "general"],
                value="electronics"
            )
            
            analyze_btn = gr.Button("🔍 Analyze Market", variant="primary", size="lg")
            
            gr.Markdown("""
            ### 💡 Tips
            - Be specific with product names
            - Include brand names when possible
            - Check confidence score before purchasing
            """)
        
        with gr.Column(scale=2):
            gr.Markdown("### 📊 Results")
            
            summary_output = gr.Markdown(label="Summary")
            
            with gr.Tabs():
                with gr.Tab("💰 Best Option"):
                    best_option_output = gr.Markdown()
                
                with gr.Tab("📈 Price Forecast"):
                    forecast_output = gr.Markdown()
                
                with gr.Tab("🛡️ Compliance"):
                    compliance_output = gr.Markdown()
                
                with gr.Tab("📄 Raw Data"):
                    export_data_output = gr.Code(language="json", label="Export Data")
            
            with gr.Row():
                confidence_output = gr.Textbox(label="Confidence Score", interactive=False)
                approval_output = gr.Textbox(label="Human Approval Required", interactive=False)
            
            export_btn = gr.Button("💾 Export Results", size="sm")
            export_file = gr.File(label="Download")
    
    # Event handlers
    def handle_analysis(product, category):
        result = analyze_product(product, category)
        
        if result.get("status") == "error":
            return (
                result.get("error"),
                "N/A", "N/A", "N/A", "0%", "N/A", ""
            )
        
        return (
            result.get("summary"),
            result.get("best_option"),
            result.get("forecast"),
            result.get("compliance"),
            result.get("confidence"),
            result.get("approval_needed"),
            result.get("export_data")
        )
    
    analyze_btn.click(
        fn=handle_analysis,
        inputs=[product_input, category_input],
        outputs=[
            summary_output,
            best_option_output,
            forecast_output,
            compliance_output,
            confidence_output,
            approval_output,
            export_data_output
        ]
    )
    
    export_btn.click(
        fn=export_results,
        inputs=[export_data_output],
        outputs=[export_file]
    )
    
    gr.Markdown("""
    ---
    ### 🔒 Security & Privacy
    - All inputs are sanitized for security
    - Sensitive data is redacted from logs
    - No personal information is stored
    
    ### ⚙️ System Status
    - Agents: Market Intelligence, Price Strategist, Compliance Auditor
    - Orchestration: LangGraph Supervisor
    - Safety: Input validation, output filtering, circuit breakers
    """)


if __name__ == "__main__":
    app.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False,
        show_error=True
    )
