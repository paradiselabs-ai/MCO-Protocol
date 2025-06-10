#!/usr/bin/env python3

import gradio as gr

def hello(name):
    return f"Hello {name}!"

if __name__ == "__main__":
    print("🚀 Starting test Gradio app...")
    
    demo = gr.Interface(
        fn=hello,
        inputs="text",
        outputs="text"
    )
    
    demo.launch(share=True, debug=True)