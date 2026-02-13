"""Fast startup script for Render deployment"""
import os
os.environ['GRADIO_ANALYTICS_ENABLED'] = 'False'
os.environ['GRADIO_SERVER_NAME'] = '0.0.0.0'

# Preload modules
import gradio as gr
from chat_ui_pro import demo

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7866))
    demo.queue(max_size=20).launch(
        server_name="0.0.0.0",
        server_port=port,
        show_error=True,
        share=False,
        favicon_path=None,
        show_api=False,
        quiet=True
    )
