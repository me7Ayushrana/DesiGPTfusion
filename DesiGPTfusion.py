import streamlit as st
import openai
import os
import datetime
from fpdf import FPDF

client = openai.OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

MODEL = "meta-llama/llama-3-8b-instruct"

os.makedirs("chats", exist_ok=True)
os.makedirs("pdf_exports", exist_ok=True)

def get_timestamp():
    return datetime.datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")

def get_date_filename():
    return datetime.datetime.now().strftime("chat_%d-%m-%Y.txt")

def get_pdf_filename():
    return datetime.datetime.now().strftime("chat_%d-%m-%Y.pdf")

def save_chat(user_msg, bot_msg):
    with open(os.path.join("chats", get_date_filename()), "a", encoding="utf-8") as f:
        f.write(f"{get_timestamp()} You: {user_msg}\n")
        f.write(f"{get_timestamp()} DesiGPT: {bot_msg}\n\n")

def clear_chat():
    st.session_state.chat_history = []

def export_to_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for speaker, msg in st.session_state.chat_history:
        pdf.multi_cell(0, 10, f"{speaker}: {msg}")
    pdf_path = os.path.join("pdf_exports", get_pdf_filename())
    pdf.output(pdf_path)
    return pdf_path

st.set_page_config(page_title="DesiGPT", layout="centered")
st.title("DesiGPT")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system",
        "content": (
            "You are DesiGPT – a smart, humble Indian chatbot who speaks in Hinglish (Hindi + English mix). "
            "Be helpful and short. Avoid filmy or over-poetic responses. Keep it to-the-point and respectful."
        )
    }]

user_input = st.text_input("💬 Enter your message:")

if user_input:
    st.session_state.chat_history.append(("You", user_input))
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Thinking... 🤔"):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=st.session_state.messages
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = "⚠️ Error: " + str(e)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.chat_history.append(("DesiGPT", reply))
    save_chat(user_input, reply)

for speaker, msg in st.session_state.chat_history:
    if speaker == "You":
        st.write(f"👤 **{speaker}**: {msg}")
    else:
        st.success(f"🤖 **{speaker}**: {msg}")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🧹 Clear Chat"):
        clear_chat()
with col2:
    if st.button("📄 Export as PDF"):
        pdf_path = export_to_pdf()
        with open(pdf_path, "rb") as f:
            st.download_button("📥 Download PDF", f, file_name=os.path.basename(pdf_path), mime="application/pdf")
with col3:
    if st.button("🔁 Refresh"):
        st.rerun()
