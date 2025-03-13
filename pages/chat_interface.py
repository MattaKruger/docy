import tempfile
import os
import streamlit as st


class StreamlitChatInterface:
    def __init__(self, available_agents):
        self.conversation_history = []
        self.uploaded_files_context = ""
        self.available_agents = available_agents
        self.current_agent = next(iter(available_agents.values()))

    def set_agent(self, agent_name: str):
        if agent_name in self.available_agents:
            self.current_agent = self.available_agents[agent_name]
            return True
        return False

    def process_uploaded_file(self, uploaded_file):
        """Process uploaded file and extract its content."""
        file_content = ""

        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        try:
            if uploaded_file.type == "text/plain" or uploaded_file.name.endswith(('.txt', '.md', '.py', '.csv')):
                with open(tmp_path, "r") as f:
                    file_content = f.read()
            elif uploaded_file.name.endswith(('.pdf')):
                file_content = f"PDF file uploaded: {uploaded_file.name}"
            else:
                file_content = f"File uploaded: {uploaded_file.name} (content type: {uploaded_file.type})"
        finally:
            os.unlink(tmp_path)

        return file_content

    async def generate_response(self, user_input: str, message_history=None) -> str:
        """Generate streaming response from the agent with conversation history."""
        conversation_context = ""
        if message_history:
            for msg in message_history:
                role = "User" if msg["role"] == "user" else "Assistant"
                conversation_context += f"{role}: {msg['content']}\n\n"

        context_parts = []

        if self.uploaded_files_context:
            context_parts.append(f"Context from uploaded files:\n{self.uploaded_files_context}")

        if conversation_context:
            context_parts.append(f"Previous conversation:\n{conversation_context}")

        context_parts.append(f"User: {user_input}")

        full_context = "\n\n".join(context_parts)

        full_response = ""

        message_placeholder = st.empty()

        async with self.current_agent.run_stream(full_context) as response:
            async for chunk in response.stream_text(delta=True):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)

        return full_response
