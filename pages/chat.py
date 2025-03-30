import asyncio

import streamlit as st
from chat_interface import StreamlitChatInterface
from config import AVAILABLE_AGENTS, AVAILABLE_MODELS
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.settings import ModelSettings

Agent.instrument_all()


deepseek_qwen = AVAILABLE_MODELS["deepseek_qwen"]
llama_model = AVAILABLE_MODELS["llama_model"]

groq_model = GroqModel(llama_model)
model_settings = ModelSettings(**AVAILABLE_AGENTS["Helpful Assistant"]["settings"])


def initialize_agents():
    available_agents = {}
    for agent_name, agent_config in AVAILABLE_AGENTS.items():
        available_agents[agent_name] = Agent(
            groq_model, system_prompt=agent_config["system_prompt"], model_settings=model_settings
        )
    return available_agents


available_agents = initialize_agents()

st.set_page_config(page_title="AI Chat Assistant", layout="wide")
st.title("AI Chat Assistant")

chat_interface = StreamlitChatInterface(available_agents)

if "messages" not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    st.title(f"Current model: {llama_model}")
    st.header("Agent selection")
    agents_name = list(available_agents.keys())
    selected_agent = st.selectbox("Choose which AI assistant to chat with:", agents_name, index=0)

    if chat_interface.set_agent(selected_agent):
        st.success(f"Start chatting with {selected_agent}!")

    st.header("Upload Files for Context")
    uploaded_files = st.file_uploader(
        "Upload files to provide context for the conversation",
        accept_multiple_files=True,
        type=["txt", "pdf", "py", "md", "csv"],
    )

    if uploaded_files:
        file_contexts = []
        for uploaded_file in uploaded_files:
            file_content = chat_interface.process_uploaded_file(uploaded_file)
            print(file_content)
            file_contexts.append(f"File: {uploaded_file.name}\nContent:\n{file_content}\n")

        chat_interface.uploaded_files_context = "\n\n".join(file_contexts)
        st.success(f"{len(uploaded_files)} file(s) uploaded successfully!")

        if st.button("Clear File Context"):
            chat_interface.uploaded_files_context = ""
            st.success("File context cleared!")

    st.header("Conversation")
    if st.button("Clear Conversation History"):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    conversation_history = (
        st.session_state.messages[-10:] if len(st.session_state.messages) > 10 else st.session_state.messages
    )

    with st.chat_message("assistant"):
        full_response = asyncio.run(chat_interface.generate_response(prompt, message_history=conversation_history[:-1]))

    st.session_state.messages.append({"role": "assistant", "content": full_response})
