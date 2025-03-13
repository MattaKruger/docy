import streamlit as st

chat = st.Page("chat.py", title="Chat", default=True, icon="💬")

page = st.navigation([chat])
page.run()
