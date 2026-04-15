import gradio as gr
import sys
import os
import time

os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.pipeline import RAGPipeline

print("\n" + "="*50)
print(" NUSTra — Starting up...")
print(" Loading knowledge base and model...")
print("="*50 + "\n")

pipeline = RAGPipeline()

print("\n" + "="*50)
print(" NUSTra is ready!")
print(" Open your browser at: http://127.0.0.1:7860")
print("="*50 + "\n")


def chat(message, history):
    # 1. Start the timer when Enter is pressed
    start_time = time.time()

    yield "⏳ *Scanning NUST archives...*"

    chunks = pipeline.retriever.retrieve(message, top_k=3)
    chunks =[c for c in chunks if c["score"] >= 0.4]

    if not chunks:
        yield "*I don't have information about that in my NUST knowledge base. Try asking about admissions, programs, fees, hostels, or campus life.*"
        return

    yield "*Analyzing retrieved documents...*"
    yield "*Synthesizing response with Qwen 2.5...*"

    response = ""
    first_token_time = 0
    got_first_token = False

    # Actual generation
    for token in pipeline.ask(message):
        # 2. Stop the timer the millisecond the very first word arrives!
        if not got_first_token:
            first_token_time = time.time() - start_time
            got_first_token = True
            
        response += token
        yield response
        
    # 3. Append the "Time to First Token" subtly to the end of the response
    if got_first_token:
        response += f"\n\n<span style='font-size: 0.75rem; color: #6b7280;'>⏱️ *Response started in {first_token_time:.1f}s*</span>"
    
    yield response

#COMPACT UI STYLING
CSS = """
body, .gradio-container {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol" !important;
}
.nustra-header {
    text-align: center;
    padding: 0.5rem 1rem 0.5rem; 
    border-bottom: 1px solid var(--border-color-primary);
    margin-bottom: 0.5rem;
}
.nustra-logo {
    font-size: 2rem; 
    font-weight: 800;
    margin: 0;
    letter-spacing: -1px;
    color: var(--body-text-color);
}
.nustra-logo span { 
    color: #3b82f6;
}
.nustra-tagline {
    font-size: 0.9rem;
    color: var(--body-text-color-subdued);
    margin: 0.2rem 0 0;
}
.nustra-badges {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 0.5rem;
    flex-wrap: wrap;
}
.badge {
    background: var(--bg-color-secondary);
    color: var(--body-text-color);
    border: 1px solid var(--border-color-primary);
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.badge.green { color: #10b981; border-color: rgba(16, 185, 129, 0.3); background: rgba(16, 185, 129, 0.05); }
.badge.blue { color: #3b82f6; border-color: rgba(59, 130, 246, 0.3); background: rgba(59, 130, 246, 0.05); }
footer { display: none !important; }

.gr-examples { margin-top: 0.2rem !important; }
"""

HEADER_HTML = """
<div class="nustra-header">
    <h1 class="nustra-logo">NUST<span>ra</span></h1>
    <p class="nustra-tagline">Your local NUST knowledge assistant — powered by Qwen 2.5 & RAG</p>
    <div class="nustra-badges">
        <!-- FIXED: Updated Badge from Phi-3 to Qwen 2.5 3B -->
        <span class="badge blue">Qwen 2.5 3B</span>
        <span class="badge green">100% Offline</span>
        <span class="badge">No Internet Required</span>
        <span class="badge">CPU Optimized</span>
    </div>
</div>
"""

with gr.Blocks(title="NUSTra — Local Assistant", analytics_enabled=False) as demo:

    gr.HTML(HEADER_HTML)

    chatbot = gr.Chatbot(
        value=[],
        height=310, 
        show_label=False,
        elem_classes="chatbot-container"
    )

    with gr.Row():
        txt = gr.Textbox(
            placeholder="Ask anything about NUST (e.g., admissions, merit, hostels)...",
            show_label=False,
            scale=8,
            container=False,
            autofocus=False, 
        )
        btn = gr.Button("Send", scale=1, variant="primary")
        clear_btn = gr.ClearButton([txt, chatbot], value="Clear 🗑️", scale=1)

    gr.Examples(
        examples=[
            "Does NUST offer scholarship / financial assistance?",
            "Can i apply for rechecking NUST Entry Test Result?",
            "Can candidates of FSc Pre-Medical apply for BS Computer Science?",
            "What is the duration of test and the number of MCQs?",
            "Will there be hostel facility available?",
        ],
        inputs=txt,
        label="Quick Suggestions:",
    )

    def submit(message, history):
        if not message.strip():
            return "", history
            
        history = history or[]
        
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": "⏳ *Starting up...*"})
        yield "", history

        full_response = ""
        for token in chat(message, history):
            full_response = token
            history[-1]["content"] = full_response
            yield "", history

    txt.submit(submit,[txt, chatbot], [txt, chatbot])
    btn.click(submit, [txt, chatbot],[txt, chatbot])


if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        inbrowser=True,
        share=False,
        show_error=True,
        css=CSS,
        theme=gr.themes.Soft(primary_hue="blue", font=[gr.themes.GoogleFont(""), "Arial", "sans-serif"])
    )