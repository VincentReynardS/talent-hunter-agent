import streamlit as st
import requests
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="THA", page_icon="🤖")
st.title("Talent Hunter Agent")

# Initialize chat history (an AI greeting message without a corresponding human prompt)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "ai", "content": "Hi, how can I help you today?"}]

# Define a helper function to call your API
def call_api(prompt, temperature=0.7):
    payload = {
        "messages": [{"role": "human", "content": prompt}],
        "user_id": "user_123",
        "thread_id": "conversation_1",
        "temperature": temperature,
    }
    full_response = ""
    response = requests.post(f"{API_BASE_URL}/chat", json=payload, stream=True)
    response.raise_for_status()
    for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
        if chunk:
            full_response += chunk
    return full_response

# Display conversation history. For every AI message that is a response to a human prompt,
# add a Retry button that lets the user re‑fetch the answer with a different temperature.
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # # Only show the retry button on AI messages that follow a human message.
        # if msg["role"] == "ai" and idx > 0 and st.session_state.messages[idx - 1]["role"] == "human":
        #     if st.button("🔄 Try Again with More Creativity", key=f"retry_{idx}"):
        #         # Get the human prompt that produced this AI message
        #         prompt = st.session_state.messages[idx - 1]["content"]
        #         try:
        #             new_response = call_api(prompt, temperature=0.9)
        #         except requests.exceptions.RequestException as e:
        #             new_response = f"⚠️ API error: {e}"
        #         # Replace the old AI message with the new one
        #         st.session_state.messages[idx]["content"] = new_response
        #         st.rerun()  # Rerun to update the rendered chat

# Chat input block
if prompt := st.chat_input("Type your message here..."):
    # Append the user's message to the conversation history.
    st.session_state.messages.append({"role": "human", "content": prompt})
    with st.chat_message("human"):
        st.markdown(prompt)
    # Call your API with the user prompt (using the default temperature)
    try:
        ai_response = call_api(prompt)
    except requests.exceptions.RequestException as e:
        ai_response = f"⚠️ API error: {e}"
    # Append the AI response to the conversation history.
    st.session_state.messages.append({"role": "ai", "content": ai_response})
    st.rerun()  # Rerun to display the newly added messages