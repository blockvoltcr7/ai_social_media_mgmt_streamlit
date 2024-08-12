import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

def main():
    st.set_page_config(page_title="Groq Chatbot", page_icon="🤖")

    st.title("Groq Chatbot")

    # Load environment variables
    load_dotenv()

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY environment variable not set")
        return

    client = Groq(api_key=GROQ_API_KEY)

    LLAMA3_70B = "llama3-70b-8192"

    # Sidebar for settings
    st.sidebar.header("Chat Settings")
    user_role = st.sidebar.selectbox("Select your role:", ["user", "system"])
    max_tokens = st.sidebar.number_input("Max Tokens", min_value=1, max_value=4096, value=1024, step=1)
    temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=2.0, value=1.0, step=0.1)

    # Main chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_content = st.chat_input("Enter your message:")

    if user_content:
        st.session_state.messages.append({"role": user_role, "content": user_content})
        with st.chat_message(user_role):
            st.markdown(user_content)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": user_role, "content": user_content}
            ]

            chat_completion = client.chat.completions.create(
                messages=messages,
                model=LLAMA3_70B,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=1,
                stream=True,
                stop=None
            )

            for chunk in chat_completion:
                full_response += (chunk.choices[0].delta.content or "")
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()