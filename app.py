import streamlit as st
from rag import query_database, log_interaction
import os

st.set_page_config(page_title="Gene–GO RAG Chatbot", layout="wide")
st.title("Gene Ontology RAG Chatbot")

# --- Session State ---
if "history" not in st.session_state:
    st.session_state["history"] = []

# --- Input Box ---
user_query = st.text_input("Ask a question about a gene/GO term:", "")

if st.button("Ask") and user_query.strip():
    with st.spinner("Thinking..."):
        answer = query_database(user_query)

    st.session_state["history"].append((user_query, answer))
    log_interaction(user_query, answer)

# --- Display Chat History ---
if st.session_state["history"]:
    st.subheader("Chat History")
    for i, (q, a) in enumerate(st.session_state["history"], 1):
        st.markdown(f"**Q{i}:** {q}")
        st.markdown(f"**A{i}:** {a}")
        st.markdown("---")
