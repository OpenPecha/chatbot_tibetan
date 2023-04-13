import gradio as gr

def add_text(history, text):
    history = history + [(text, None)]
    return history, ""


def bot(history):
    response = "**That's cool!**"
    history[-1][1] = response
    return history

with gr.Blocks() as demo:
    chatbot = gr.Chatbot([], elem_id="chatbot").style(height=750)

    with gr.Column(scale=0.85):
        txt = gr.Textbox(
            show_label=False,
            placeholder="Enter text and press enter",
        ).style(container=False)

    txt.submit(add_text, [chatbot, txt], [chatbot, txt]).then(
        bot, chatbot, chatbot
    )

demo.launch()